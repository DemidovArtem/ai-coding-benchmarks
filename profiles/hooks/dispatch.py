"""Run the reviewed Ponytail native hook as the unprivileged container user."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_assets(root, node, manifest, entry):
    if entry not in manifest['entrypoints']:
        raise ValueError("Unreviewed hook entrypoint")
    if digest(node) != manifest['node']['sha256']:
        raise ValueError("Node runtime differs from the pin")
    for name, expected in manifest['files_sha256'].items():
        target = (root / name).resolve()
        if not target.is_relative_to(root.resolve()):
            raise ValueError('Hook dependency escapes the reviewed package')
        if digest(target) != expected:
            raise ValueError("Hook dependency differs from the reviewed source")


def main():
    if os.geteuid() == 0:
        raise RuntimeError("Hooks must not run as root")
    root = Path('/opt/experiment-skills/ponytail')
    manifest = json.loads(Path('/opt/experiment-hooks/manifest.json').read_text())
    entry = sys.argv[1]
    node = Path('/opt/experiment-node/node')
    verify_assets(root, node, manifest, entry)
    payload = sys.stdin.buffer.read(1_000_001)
    if len(payload) > 1_000_000:
        raise ValueError("Hook input exceeds the pilot budget")
    state = Path.home()/'.codex/ponytail-state'
    env = {**os.environ,'PLUGIN_DATA':str(state),'PLUGIN_ROOT':str(root),
           'CLAUDE_PLUGIN_ROOT':str(root),'PONYTAIL_DEFAULT_MODE':'full'}
    result = subprocess.run([str(node),str(root/'hooks'/entry)],input=payload,capture_output=True,env=env,timeout=10)
    if result.returncode:
        raise RuntimeError("Reviewed hook failed; stdout/stderr suppressed")
    output = json.loads(result.stdout) if result.stdout.strip() else {}
    context = output.get('hookSpecificOutput',{}).get('additionalContext','')
    event = json.loads(payload or b'{}').get('hook_event_name')
    proof = {'entrypoint':entry,'event':event,'exit_code':result.returncode,
             'mode':(state/'.ponytail-active').read_text().strip() if (state/'.ponytail-active').exists() else None,
             'context_chars':len(context),'context_sha256':hashlib.sha256(context.encode()).hexdigest(),
             'full_mode_context':'PONYTAIL MODE ACTIVE — level: full' in context,
             'unprivileged_uid':os.geteuid()}
    with (Path.home()/'.codex/skill_hook_audit.jsonl').open('a') as audit:
        audit.write(json.dumps(proof)+'\n')
    sys.stdout.buffer.write(result.stdout)


if __name__ == '__main__':
    main()
