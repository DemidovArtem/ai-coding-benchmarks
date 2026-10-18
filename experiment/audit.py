"""Read-only Phase 0 audit; never invoke a model or read credential contents."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tomllib


PAID_KEYS = ("OPENAI_API_KEY", "CODEX_API_KEY", "UNIFIED_API_KEY")


def command(*args, cwd=None):
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=15)
        return (result.stdout or result.stderr).strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def host_summary(home, environ):
    """Only export booleans/counts; raw configuration and environment stay private."""
    config = {}
    status = "missing"
    path = home / ".codex/config.toml"
    if path.exists():
        try:
            config = tomllib.loads(path.read_text())
            status = "parsed"
        except (OSError, ValueError):
            status = "unreadable"
    return {
        "config_status": status,
        "mcp_server_count": len(config.get("mcp_servers", {})),
        "plugins_configured": bool(config.get("plugins")),
        "hooks_configured": bool(config.get("hooks")),
        "global_agents_present": (home / ".codex/AGENTS.md").exists(),
        "global_skills_present": (home / ".agents/skills").exists(),
        "auth_file_present": (home / ".codex/auth.json").exists(),
        "paid_key_env_present": {key: bool(environ.get(key)) for key in PAID_KEYS},
        "proxy_env_present": any(environ.get(k) for k in (
            "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy",
            "OPENAI_BASE_URL", "UNIFIED_BASE_URL",
        )),
    }


def check_pins(root, pins):
    failures = []
    for name, expected in pins["file_sha256"].items():
        path = root / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != expected:
            failures.append(f"file_pin_mismatch:{name}")
    for name, expected in pins["git_commits"].items():
        if command("git", "rev-parse", "HEAD", cwd=root / name) != expected:
            failures.append(f"git_pin_mismatch:{name}")
        elif command("git", "status", "--porcelain", "--untracked-files=normal", cwd=root / name) != "":
            failures.append(f"checkout_dirty:{name}")
    return failures


def collect(root, config):
    versions = {name: command(*args) for name, args in {
        "codex": ("codex", "--version"), "docker": ("docker", "--version"),
        "git": ("git", "--version"), "git_lfs": ("git", "lfs", "version"),
        "uv": ("uv", "--version"),
    }.items()}
    host = host_summary(Path.home(), os.environ)
    failures = check_pins(root, config["pins"])
    if versions["codex"] != "codex-cli " + config["codex"]["version"]:
        failures.append("codex_version_mismatch")
    oauth = command("codex", "login", "status") == "Logged in using ChatGPT"
    if not oauth:
        failures.append("chatgpt_login_unverified")
    if any(host["paid_key_env_present"].values()):
        failures.append("paid_api_environment_present")
    if command("docker", "info", "--format", "{{.ServerVersion}}") is None:
        failures.append("docker_daemon_unavailable")
    runtime_root = Path(config["resources"].get("runtime_root", str(root)))
    storage = runtime_root
    while not storage.exists():
        storage = storage.parent
    free = shutil.disk_usage(storage).free
    if free < config["resources"]["min_workspace_free_bytes"]:
        failures.append("insufficient_runtime_disk")
    return {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "versions": versions, "chatgpt_login_verified": oauth, "host_summary": host,
        "cpu_count": os.cpu_count(), "workspace_free_bytes": shutil.disk_usage(root).free,
        "runtime_root": str(runtime_root), "runtime_free_bytes": free,
        "root_free_bytes": shutil.disk_usage("/").free,
        "pin_and_environment_failures": failures,
        "phase1_blockers": config["phase1_blockers"],
        "ready_for_smoke": not failures and not config["phase1_blockers"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "experiment.yaml").read_text())
    report = collect(root, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"ready_for_smoke": report["ready_for_smoke"],
                      "failures": report["pin_and_environment_failures"]}))
    return 0 if report["ready_for_smoke"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
