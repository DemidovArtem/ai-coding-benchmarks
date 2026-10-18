"""One OAuth host smoke or one actual, protected SWE-Milestone baseline smoke."""

import argparse
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


def milestone_smoke(config, output):
    sys.path.insert(0, str(ROOT / "vendor/SWE-Milestone"))
    from harness.e2e.run_milestone import MilestoneRunner

    profile = ROOT / "profiles/baseline/config.toml"
    expected_hash = hashlib.sha256(profile.read_bytes()).hexdigest()

    class BaselineRunner(MilestoneRunner):
        def _load_prompt(self):
            prompt = super()._load_prompt()
            subprocess.run(["docker", "cp", str(profile), self.container_name + ":/home/fakeroot/.codex/config.toml"], check=True, capture_output=True)
            subprocess.run(["docker", "exec", self.container_name, "chown", "fakeroot:fakeroot", "/home/fakeroot/.codex/config.toml"], check=True, capture_output=True)
            script = '''
import hashlib,json,pathlib,shutil,subprocess,sys,tomllib
p=pathlib.Path('/home/fakeroot/.codex/config.toml')
assert hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[1], 'profile hash mismatch'
c=tomllib.loads(p.read_text())
assert c['forced_login_method']=='chatgpt'
assert not c.get('mcp_servers') and not c.get('hooks') and not c.get('plugins')
assert c['web_search']=='disabled' and all(v is False for v in c['features'].values())
for path in ('/AGENTS.md','/home/AGENTS.md','/home/fakeroot/AGENTS.md','/testbed/AGENTS.md','/testbed/.codex','/testbed/.agents','/testbed/.serena','/home/fakeroot/.agents','/home/fakeroot/.codex/AGENTS.md','/home/fakeroot/.codex/hooks.json'):
 assert not pathlib.Path(path).exists(), 'unexpected instruction or memory artifact: '+path
if shutil.which('sudo'):
 assert subprocess.run(['sudo','-n','true'],capture_output=True).returncode != 0, 'sudo privileges remain available'
print(json.dumps({'config_sha256':sys.argv[1],'effective_config':c,'instruction_audit':'clean','serena_memories':0}))
'''
            proof = subprocess.run(["docker", "exec", "--user", "fakeroot", "-e", "HOME=/home/fakeroot", self.container_name,
                                    "python3", "-c", script, expected_hash], check=True, capture_output=True, text=True)
            mounts = json.loads(subprocess.check_output(["docker", "inspect", "--format", "{{json .Mounts}}", self.container_name], text=True))
            allowed = {"/tmp/host-codex/auth.json"}
            if any(m["Destination"] not in allowed or m["RW"] for m in mounts):
                raise RuntimeError("Unexpected host mount in baseline container")
            if self.runtime_policy_binding.mode != "protected":
                raise RuntimeError("Protected quarantine is required")
            self.container_setup.verify_network_lockdown()
            audit = json.loads(proof.stdout)
            audit["profile_config"] = audit["effective_config"].copy()
            audit["effective_config"]["sandbox_mode"] = "danger-full-access"
            audit["cli_overrides"] = {"sandbox_bypass_inside_isolated_container": True,
                                      "web_search": "disabled"}
            audit.update(quarantine="protected", requested_cli_version=config["codex"]["version"],
                         actual_cli_version=self.container_setup.get_agent_version(verify_requested=True),
                         starting_commit=self._snapshot_baseline_commit,
                         host_mounts=[{"destination": m["Destination"], "read_only": not m["RW"]} for m in mounts])
            save(output / "effective_profile.json", audit)
            return prompt

    benchmark = config["benchmark"]
    workspace = (ROOT / benchmark["dataset_root"] / benchmark["repo"]).resolve()
    milestone = benchmark["smoke_milestone"]
    runner = BaselineRunner(workspace_root=workspace, milestone_id=milestone,
        srs_path=workspace / "srs" / milestone / "SRS.md", output_dir=output,
        agent_name="codex", agent_version=config["codex"]["version"], model=config["codex"]["model"],
        reasoning_effort=config["codex"]["reasoning_effort"], timeout_ms=benchmark["timeout_seconds"] * 1000,
        main_branch=benchmark["main_branch"], keep_container=True, trial_name=output.name, max_retries=1)
    result = runner.run()
    # Preserve authoritative refs for Git metrics, including unresolved submissions.
    bundle = "/tmp/experiment-submission.bundle"
    subprocess.run(["docker", "exec", "-w", "/testbed", runner.container_name, "git", "-c", "safe.directory=/testbed", "bundle", "create", bundle, "--all"], check=True, capture_output=True)
    subprocess.run(["docker", "cp", runner.container_name + ":" + bundle, str(output / "repository.bundle")], check=True, capture_output=True)
    return 0 if result.resolved else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("host-smoke", "milestone-smoke"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "experiment.yaml").read_text())
    validate(config)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    output.chmod(0o700)
    logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(output / "orchestrator.log")])
    started = time.monotonic()
    metadata = {"phase": args.phase, "state": "running", "started_at": datetime.now(timezone.utc).isoformat(),
                "model": config["codex"]["model"], "reasoning_effort": config["codex"]["reasoning_effort"],
                "implementation_commit": command("git", "rev-parse", "HEAD", cwd=ROOT),
                "experiment_sha256": hashlib.sha256((ROOT / "experiment.yaml").read_bytes()).hexdigest()}
    save(output / "run_metadata.json", metadata)
    secrets = credential_values(Path.home() / ".codex/auth.json")
    try:
        code = host_smoke(config, output) if args.phase == "host-smoke" else milestone_smoke(config, output)
        metadata.update(state="finished", returncode=code)
    except Exception as error:
        metadata.update(state="failed", failure_category="infrastructure_failure", error=redact(str(error), secrets))
        code = 2
    finally:
        metadata["duration_seconds"] = time.monotonic() - started
        save(output / "run_metadata.json", metadata)
        redact_artifacts(output, secrets)
    print(json.dumps(metadata))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
