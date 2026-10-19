"""Continue a quota-interrupted planning trial only when its executor never started."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from experiment.audit import command
from experiment.planning import repository_fingerprint, validate_handoff
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, save, session_isolation, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact, redact_artifacts


def prepared_input(output, config):
    metadata = json.loads((output / "run_metadata.json").read_text())
    if metadata.get("state") != "failed" or metadata.get("failure_category") != "quota_pressure":
        raise ValueError("Only a quota-interrupted terminal trial may continue")
    if metadata.get("variant") not in ("plan", "goal_plan"):
        raise ValueError("A planning trial is required")
    if (output / "log/agent_stdout.txt").exists() or (output / "session_isolation.json").exists():
        raise ValueError("Executor already started; refusing another attempt")
    if metadata.get("setup_fingerprint") != setup_fingerprint(config)[0]:
        raise ValueError("Frozen setup differs from the interrupted trial")
    if metadata.get("experiment_sha256") != hashlib.sha256((ROOT / "experiment.yaml").read_bytes()).hexdigest():
        raise ValueError("Frozen experiment file changed")
    if json.loads((output / "experiment.json").read_text()) != config:
        raise ValueError("Saved experiment differs from the frozen setup")
    audit = json.loads((output / "planner/audit.json").read_text())
    if (audit.get("state") != "validated" or audit.get("repository_unchanged") is not True or
            audit.get("repository_before_sha256") != audit.get("repository_after_sha256") or
            not audit.get("session_id") or audit.get("variant") != metadata["variant"]):
        raise ValueError("Preparation integrity is unverified")
    if repository_fingerprint(output / "planner/repository") != audit["repository_after_sha256"]:
        raise ValueError("Saved planner repository changed")
    raw = (output / "planner/handoff.json").read_text()
    if hashlib.sha256(raw.encode()).hexdigest() != audit.get("handoff_sha256"):
        raise ValueError("Prepared handoff changed")
    validate_handoff(raw,metadata["variant"])
    return metadata, audit, raw


def executor_state(name, config):
    def call(*args):
        return subprocess.check_output(["docker","exec","--user","fakeroot","-e","HOME=/home/fakeroot",
            "-w","/testbed",name,*args],stderr=subprocess.DEVNULL)
    info = json.loads(subprocess.check_output(["docker","inspect",name]))[0]
    expected_image = json.loads(subprocess.check_output(["docker","image","inspect",config["images"][0]["digest_ref"]]))[0]["Id"]
    if info["Image"] != expected_image:
        raise ValueError("Retained executor image differs from the frozen image")
    if not info["State"]["Running"]:
        raise ValueError("Retained executor container is not running; do not replace it")
    if b"codex" in call("ps","-eo","comm").splitlines():
        raise ValueError("A Codex process is already running")
    sessions = call("python3","-c","from pathlib import Path; print(sum(p.is_file() for p in Path('/home/fakeroot/.codex/sessions').rglob('*')))")
    if sessions.strip() != b"0":
        raise ValueError("Executor already has a session")
    git = lambda *args: call("git","-c","safe.directory=/testbed",*args)
    tree = git("rev-parse","HEAD^{tree}").decode().strip()
    if tree != config["benchmark"]["common_starting_tree"]:
        raise ValueError("Executor starting tree changed")
    status = git("status","--porcelain=v1","-z","--untracked-files=all")
    files = {}
    from experiment.metrics import production_content
    for entry in status.split(b"\0"):
        if not entry:
            continue
        path = entry[3:].decode()
        if entry[:3] != b" M " or not path.endswith(".rs"):
            raise ValueError("Executor has changes beyond the upstream test masking")
        content = call("cat","--","/testbed/"+path)
        base = git("show","HEAD:"+path)
        if production_content(base,path) != production_content(content,path):
            raise ValueError("Executor production source changed")
        files[path] = hashlib.sha256(content).hexdigest()
    # Upstream masking can leave test-only edits uncommitted when there are zero commits to squash.
    return {"container_id":info["Id"],"image_id":info["Image"],"starting_tree":tree,
            "starting_commit":git("rev-parse","HEAD").decode().strip(),"test_only_worktree_edits":files,
            "executor_session_files":0,"executor_processes":0}


def execute(config, output, metadata, audit, raw, before):
    sys.path.insert(0,str(ROOT / "vendor/SWE-Milestone"))
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.profiles import activate_profile

    class PreparedRunner(MilestoneRunner):
        def _load_prompt(self):
            task = super()._load_prompt()
            if task != (output / "original_task.txt").read_text():
                raise ValueError("Original task changed")
            if executor_state(self.container_name,config) != before:
                raise ValueError("Executor state changed during preprocessing")
            activate_profile(self.container_setup,output,config,metadata["variant"])
            if not self.agent_runner.refresh_container_credentials():
                raise RuntimeError("OAuth refresh failed before executor start")
            quota = read_quota()
            save(output / "resume_quota_before_executor.json",quota)
            check_quota(quota,config["resources"]["quota_stop_percent"])
            return task + "\n\n" + (ROOT / "prompts/executor.md").read_text().format(handoff=raw)

        def _run_evaluation(self, snapshot_path):
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot_path)
            finally:
                save(output / "durations.json",{"evaluation":time.monotonic()-started})

    benchmark = config["benchmark"]
    workspace = (ROOT / benchmark["dataset_root"] / benchmark["repo"]).resolve()
    milestone = benchmark["smoke_milestone"]
    runner = PreparedRunner(workspace_root=workspace,milestone_id=milestone,srs_path=workspace / "srs" / milestone / "SRS.md",
        output_dir=output,agent_name="codex",agent_version=config["codex"]["version"],model=config["codex"]["model"],
        reasoning_effort=config["codex"]["reasoning_effort"],timeout_ms=benchmark["timeout_seconds"]*1000,
        main_branch=benchmark["main_branch"],keep_container=True,trial_name=output.name,max_retries=1)
    if runner.container_name != metadata["resume"]["container_name"]:
        raise ValueError("Executor identity changed")
    result = runner.run()
    save(output / "session_isolation.json",session_isolation(audit["session_id"],runner.agent_runner.session_id))
    bundle = "/tmp/experiment-submission.bundle"
    subprocess.run(["docker","exec","-w","/testbed",runner.container_name,"git","-c","safe.directory=/testbed","bundle","create",bundle,"--all"],check=True,capture_output=True)
    subprocess.run(["docker","cp",runner.container_name+":"+bundle,str(output / "repository.bundle")],check=True,capture_output=True)
    return 0 if result.resolved else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--check-only",action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "experiment.yaml").read_text())
    sys.path.insert(0,str(ROOT / "vendor/SWE-Milestone"))
    validate(config)
    lock = trial_lock(Path(config["resources"]["runtime_root"]))
    output = args.output.resolve()
    metadata, audit, raw = prepared_input(output,config)
    name = config["benchmark"]["smoke_milestone"]+"-"+output.name+"-runner"
    before = executor_state(name,config)
    quota = read_quota()
    check_quota(quota,config["resources"]["quota_stop_percent"])
    if args.check_only:
        print(json.dumps({"preflight_ok":True,"executor_state":before,"handoff_sha256":audit["handoff_sha256"]}))
        lock.close()
        return 0
    secrets = credential_values(Path.home() / ".codex/auth.json")
    history = output / "interruptions" / "001"
    history.mkdir(parents=True,exist_ok=False)
    for filename in ("run_metadata.json","quota_before.json","quota_after.json","effective_profile.json"):
        shutil.copy2(output / filename,history / filename)
    previous_duration = metadata["duration_seconds"]
    started = time.monotonic()
    metadata["resume"] = {"started_at":datetime.now(timezone.utc).isoformat(),"container_name":name,"preflight":before,
        "preparation_reused":True,"prior_duration_seconds":previous_duration,"prior_outcome":"quota_pressure_before_executor",
        "history_path":str(history),"implementation_commit":command("git","rev-parse","HEAD",cwd=ROOT),
        "adapter_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    metadata.update(state="running",failure_category=None)
    metadata.pop("error",None)
    save(output / "run_metadata.json",metadata)
    save(output / "resume_quota_before.json",quota)
    code = 2
    try:
        code = execute(config,output,metadata,audit,raw,before)
        metadata.update(state="finished",returncode=code)
    except Exception as error:
        category = "quota_pressure" if str(error).startswith("Quota pressure") else "resume_failure"
        metadata.update(state="failed",failure_category=category,error=redact(str(error),secrets))
    finally:
        metadata["resume"]["duration_seconds"] = time.monotonic()-started
        metadata["duration_seconds"] = previous_duration+metadata["resume"]["duration_seconds"]
        metadata["wall_duration_seconds"] = (datetime.now(timezone.utc)-datetime.fromisoformat(metadata["started_at"])).total_seconds()
        try:
            save(output / "quota_after.json",read_quota())
        except Exception:
            save(output / "quota_after.json",{"status":"unavailable_after_resume"})
        save(output / "run_metadata.json",metadata)
        redact_artifacts(output,secrets)
        lock.close()
    print(json.dumps(metadata))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
