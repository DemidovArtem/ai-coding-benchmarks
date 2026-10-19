"""Run the pinned upstream Caveman Codex hook without installing its broader workflow suite."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from dispatch import verify_assets


def main():
    if os.geteuid() == 0:
        raise RuntimeError('Hooks must not run as root')
    root = Path('/opt/experiment-skills/caveman')
    manifest = json.loads(Path('/opt/experiment-hooks/manifest.json').read_text())
    node = Path('/opt/experiment-node/node')
    entry = sys.argv[1]
    verify_assets(root,node,manifest,entry)
    payload = sys.stdin.buffer.read(1_000_001)
    if len(payload)>1_000_000:
        raise ValueError('Hook input exceeds the pilot budget')
    env = {**os.environ,'CAVEMAN_DEFAULT_MODE':'full','CLAUDE_PLUGIN_ROOT':str(root)}
    result = subprocess.run([str(node),str(root/'.codex'/entry)],input=payload,capture_output=True,env=env,timeout=4)
    if result.returncode:
        raise RuntimeError('Reviewed Caveman hook failed; stdout/stderr suppressed')
    context = result.stdout.decode()
    header = 'CAVEMAN MODE ACTIVE — mode: caveman'
    if not context.startswith(header) or 'Clarity beats compression.' not in context:
        raise ValueError('The full pinned communication ruleset was not emitted')
    proof = {'entrypoint':entry,'event':json.loads(payload or b'{}').get('hook_event_name'),
        'exit_code':0,'mode':'caveman','configured_legacy_mode':'full','context_chars':len(context),
        'context_sha256':hashlib.sha256(result.stdout).hexdigest(),'caveman_mode_context':True,'unprivileged_uid':os.geteuid()}
    with (Path.home()/'.codex/skill_hook_audit.jsonl').open('a') as audit:
        audit.write(json.dumps(proof)+'\n')
    sys.stdout.buffer.write(result.stdout)


if __name__=='__main__':
    main()
