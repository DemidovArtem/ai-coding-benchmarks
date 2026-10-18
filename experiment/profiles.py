"""Construct and verify isolated Codex profiles inside protected containers."""

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def activate_profile(setup, output, config, variant="baseline", repository_mount=None):
    profile = ROOT / "profiles" / variant / "config.toml"
    expected_hash = hashlib.sha256(profile.read_bytes()).hexdigest()
    subprocess.run(["docker", "cp", str(profile), setup.container_name + ":/home/fakeroot/.codex/config.toml"], check=True, capture_output=True)
    subprocess.run(["docker", "exec", setup.container_name, "chown", "fakeroot:fakeroot", "/home/fakeroot/.codex/config.toml"], check=True, capture_output=True)
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
    proof = subprocess.run(["docker", "exec", "--user", "fakeroot", "-e", "HOME=/home/fakeroot", setup.container_name,
                            "python3", "-c", script, expected_hash], check=True, capture_output=True, text=True)
    mounts = json.loads(subprocess.check_output(["docker", "inspect", "--format", "{{json .Mounts}}", setup.container_name], text=True))
    allowed = {"/tmp/host-codex/auth.json"}
    if repository_mount is not None:
        allowed.add("/testbed")
    if {m["Destination"] for m in mounts} != allowed or any(m["RW"] for m in mounts):
        raise RuntimeError("Unexpected host mount in baseline container")
    if repository_mount is not None and not any(
        m["Destination"] == "/testbed" and Path(m["Source"]).resolve() == repository_mount.resolve() for m in mounts
    ):
        raise RuntimeError("Planner repository mount differs from the frozen input")
    if setup.runtime_policy_binding.mode != "protected":
        raise RuntimeError("Protected quarantine is required")
    setup.verify_network_lockdown()
    audit = json.loads(proof.stdout)
    audit["profile_config"] = audit["effective_config"].copy()
    audit["effective_config"]["sandbox_mode"] = "danger-full-access"
    audit["cli_overrides"] = {"sandbox_bypass_inside_isolated_container": True,
                              "web_search": "disabled"}
    audit.update(quarantine="protected", requested_cli_version=config["codex"]["version"],
                 actual_cli_version=setup.get_agent_version(verify_requested=True),
                 starting_commit=setup.docker_exec_git("rev-parse", "HEAD").stdout.strip(),
                 host_mounts=[{"destination": m["Destination"], "read_only": not m["RW"]} for m in mounts])
    audit["variant"] = variant
    (output / "effective_profile.json").write_text(json.dumps(audit, indent=2) + "\n")
    return audit
