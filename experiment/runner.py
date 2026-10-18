"""One OAuth host smoke or one actual, protected SWE-Milestone baseline smoke."""

import argparse
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from experiment.audit import PAID_KEYS, check_pins, command
from experiment.security import credential_values, redact, redact_artifacts


ROOT = Path(__file__).resolve().parents[1]


def validate(config):
    if any(os.environ.get(key) for key in PAID_KEYS):
        raise RuntimeError("Paid API environment is forbidden")
    if any(os.environ.get(key) for key in ("OPENAI_BASE_URL", "UNIFIED_BASE_URL")):
        raise RuntimeError("Custom model endpoints are forbidden")
    if command("codex", "login", "status") != "Logged in using ChatGPT":
        raise RuntimeError("ChatGPT OAuth login is unverified")
    if command("codex", "--version") != "codex-cli " + config["codex"]["version"]:
        raise RuntimeError("Codex CLI version differs from experiment pin")
    failures = check_pins(ROOT, config["pins"])
    if failures:
        raise RuntimeError("Setup pins failed: " + ", ".join(failures))


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def check_quota(snapshot, limit):
    if snapshot.get("status") != "observed" or not snapshot.get("rate_limits"):
        raise RuntimeError("Current quota unavailable; a verified snapshot is required")
    for quota in snapshot["rate_limits"].values():
        if quota.get("rateLimitReachedType") or quota.get("spendControlReached"):
            raise RuntimeError("Quota pressure: stop before a model request")
        for window in ("primary", "secondary"):
            value = quota.get(window)
            if value is not None and value["usedPercent"] >= limit:
                raise RuntimeError("Quota pressure: configured stop threshold reached")


def trial_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    handle = (directory / ".trial.lock").open("a")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("Another experiment model trial is active") from None
    return handle


def setup_fingerprint(config):
    conditions = {key: config[key] for key in ("codex", "benchmark", "pins")}
    conditions["planning"] = config.get("planning")
    return hashlib.sha256(json.dumps(conditions, sort_keys=True).encode()).hexdigest(), conditions


def session_isolation(planner, executor):
    if not planner or not executor or planner == executor:
        raise RuntimeError("Planner and executor sessions are not isolated")
    return {"planner_session_id": planner, "executor_session_id": executor,
            "separate_containers": True, "separate_sessions": True}


def host_smoke(config, output):
    """No tools requested; user/project profiles are absent in the temporary home."""
    auth = Path.home() / ".codex/auth.json"
    secrets = credential_values(auth)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="oauth-host-", dir=output) as tmp:
        home = Path(tmp)
        codex_home = home / ".codex"
        codex_home.mkdir(mode=0o700)
        shutil.copyfile(auth, codex_home / "auth.json")
        (codex_home / "auth.json").chmod(0o600)
        shutil.copyfile(ROOT / "profiles/baseline/config.toml", codex_home / "config.toml")
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "LANG", "TERM", "SSL_CERT_FILE", "SSL_CERT_DIR")}
        env.update(HOME=str(home), CODEX_HOME=str(codex_home))
        result = subprocess.run(
            [shutil.which("codex"), "exec", "--skip-git-repo-check", "--ephemeral", "--json",
             "--sandbox", "read-only", "Reply exactly OAUTH_SMOKE_OK. Do not invoke tools."],
            cwd=home, env=env, capture_output=True, text=True, timeout=120,
        )
        secrets.update(credential_values(codex_home / "auth.json"))
        stdout = redact(result.stdout, secrets)
        (output / "events.jsonl").write_text(stdout)
        (output / "stderr.txt").write_text(redact(result.stderr, secrets))
        events = [json.loads(line) for line in stdout.splitlines() if line.startswith("{")]
        messages = [e.get("item", {}).get("text") for e in events if e.get("type") == "item.completed"]
        success = result.returncode == 0 and "OAUTH_SMOKE_OK" in messages
        save(output / "result.json", {"auth": "chatgpt_oauth_only", "success": success,
             "returncode": result.returncode, "duration_seconds": time.monotonic() - started,
             "usage_events": [e for e in events if e.get("type") == "turn.completed"],
             "tool_calls": sum(e.get("item", {}).get("type") in ("command_execution", "mcp_tool_call")
                               for e in events if e.get("type") == "item.completed")})
        return 0 if success else 2


def milestone_smoke(config, output, variant="baseline"):
    sys.path.insert(0, str(ROOT / "vendor/SWE-Milestone"))
    from harness.e2e.run_milestone import MilestoneRunner

    class BaselineRunner(MilestoneRunner):
        def _load_prompt(self):
            prompt = super()._load_prompt()
            from experiment.profiles import activate_profile
            activate_profile(self.container_setup, output, config, variant)
            tree = self.container_setup.docker_exec_git("rev-parse", "HEAD^{tree}").stdout.strip()
            if benchmark.get("common_starting_tree") and tree != benchmark["common_starting_tree"]:
                raise RuntimeError("Starting tree differs from the frozen matched baseline")
            if variant in ("plan", "goal_plan"):
                from experiment.planning import prepare
                prepared = prepare(self, prompt, config, output, variant)
                from experiment.quota import read_quota
                quota = read_quota()
                save(output / "planner/quota_after.json", quota)
                check_quota(quota, config["resources"]["quota_stop_percent"])
                return prepared
            (output / "original_task.txt").write_text(prompt)
            return prompt

        def _run_evaluation(self, snapshot_path):
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot_path)
            finally:
                save(output / "durations.json", {"evaluation": time.monotonic() - started})

    benchmark = config["benchmark"]
    workspace = (ROOT / benchmark["dataset_root"] / benchmark["repo"]).resolve()
    milestone = benchmark["smoke_milestone"]
    runner = BaselineRunner(workspace_root=workspace, milestone_id=milestone,
        srs_path=workspace / "srs" / milestone / "SRS.md", output_dir=output,
        agent_name="codex", agent_version=config["codex"]["version"], model=config["codex"]["model"],
        reasoning_effort=config["codex"]["reasoning_effort"], timeout_ms=benchmark["timeout_seconds"] * 1000,
        main_branch=benchmark["main_branch"], keep_container=True, trial_name=output.name, max_retries=1)
    result = runner.run()
    planner_audit = output / "planner/audit.json"
    if planner_audit.exists():
        planner_session = json.loads(planner_audit.read_text()).get("session_id")
        save(output / "session_isolation.json", session_isolation(planner_session, runner.agent_runner.session_id))
    # Preserve authoritative refs for Git metrics, including unresolved submissions.
    bundle = "/tmp/experiment-submission.bundle"
    subprocess.run(["docker", "exec", "-w", "/testbed", runner.container_name, "git", "-c", "safe.directory=/testbed", "bundle", "create", bundle, "--all"], check=True, capture_output=True)
    subprocess.run(["docker", "cp", runner.container_name + ":" + bundle, str(output / "repository.bundle")], check=True, capture_output=True)
    return 0 if result.resolved else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("host-smoke", "milestone-smoke", "trial"))
    parser.add_argument("--variant", choices=("baseline", "plan", "goal_plan"), default="baseline")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "experiment.yaml").read_text())
    validate(config)
    if args.phase == "host-smoke" and args.variant != "baseline":
        parser.error("Host auth smoke only supports baseline")
    lock = trial_lock(Path(config["resources"]["runtime_root"]))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(output / "orchestrator.log")])
    started = time.monotonic()
    metadata = {"phase": args.phase, "state": "running", "started_at": datetime.now(timezone.utc).isoformat(),
                "variant": args.variant, "trial_kind": "measured" if args.phase == "trial" else "smoke",
                "measured_comparison": args.phase == "trial",
                "model": config["codex"]["model"], "reasoning_effort": config["codex"]["reasoning_effort"],
                "implementation_commit": command("git", "rev-parse", "HEAD", cwd=ROOT),
                "experiment_sha256": hashlib.sha256((ROOT / "experiment.yaml").read_bytes()).hexdigest()}
    metadata["setup_fingerprint"], conditions = setup_fingerprint(config)
    save(output / "experiment.json", config)
    save(output / "comparison_conditions.json", conditions)
    save(output / "run_metadata.json", metadata)
    secrets = set()
    try:
        secrets = credential_values(Path.home() / ".codex/auth.json")
        if args.phase == "trial":
            from experiment.quota import read_quota
            before = read_quota()
            save(output / "quota_before.json", before)
            check_quota(before, config["resources"]["quota_stop_percent"])
        code = host_smoke(config, output) if args.phase == "host-smoke" else milestone_smoke(config, output, args.variant)
        metadata.update(state="finished", returncode=code)
    except Exception as error:
        category = "quota_pressure" if str(error).startswith("Quota pressure") else "infrastructure_failure"
        preparation = output / "planner/audit.json"
        if preparation.exists() and category != "quota_pressure":
            category = json.loads(preparation.read_text()).get("failure_category", "preparation_failure")
        metadata.update(state="failed", failure_category=category, error=redact(str(error), secrets))
        code = 2
    finally:
        metadata["duration_seconds"] = time.monotonic() - started
        if args.phase == "trial":
            from experiment.quota import read_quota
            save(output / "quota_after.json", read_quota())
        save(output / "run_metadata.json", metadata)
        redact_artifacts(output, secrets)
        lock.close()
    print(json.dumps(metadata))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
