"""Stage audited local skill dependencies inside a dedicated protected profile."""

import hashlib
import json
from pathlib import Path
import subprocess

from experiment.profiles import ROOT, activate_profile


def install_native_skill(setup, output, config, variant, repository_mount=None):
    if variant not in ("ponytail", "caveman"):
        raise ValueError("Unsupported native skill profile")
    proof = activate_profile(setup,output,config,variant,repository_mount=repository_mount)
    profile = ROOT/'profiles'/variant
    manifest = json.loads((profile/'manifest.json').read_text())
    node = Path(manifest['node']['local_source'])
    if hashlib.sha256(node.read_bytes()).hexdigest() != manifest['node']['sha256']:
        raise ValueError('Reviewed Node runtime changed')
    for name, expected in manifest['files_sha256'].items():
        if hashlib.sha256((profile/'assets'/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Reviewed native skill source changed')
    name = setup.container_name
    def execute(*args):
        subprocess.run(['docker','exec',name,*args],check=True,capture_output=True)
    def copy(source,target):
        subprocess.run(['docker','cp',str(source),name+':'+target],check=True,capture_output=True)
    execute('mkdir','-p','/opt/experiment-node','/opt/experiment-skills/'+variant,'/opt/experiment-hooks')
    copy(node,'/opt/experiment-node/node')
    copy(str(profile/'assets')+'/.','/opt/experiment-skills/'+variant)
    copy(profile/'manifest.json','/opt/experiment-hooks/manifest.json')
    copy(ROOT/'profiles/hooks/dispatch.py','/opt/experiment-hooks/dispatch.py')
    if variant == 'caveman':
        copy(ROOT/'profiles/hooks/caveman_dispatch.py','/opt/experiment-hooks/caveman_dispatch.py')
    execute('chmod','-R','a-w','/opt/experiment-node','/opt/experiment-skills','/opt/experiment-hooks')
    execute('chmod','a+rx','/opt/experiment-node/node')
    copy(profile/'native_hooks.json','/home/fakeroot/.codex/hooks.json')
    execute('chown','root:root','/home/fakeroot/.codex/hooks.json')
    execute('chmod','0444','/home/fakeroot/.codex/hooks.json')
    proof.update(skill=variant,skill_version=manifest['version'],mode=manifest['mode'],
        manifest_sha256=hashlib.sha256((profile/'manifest.json').read_bytes()).hexdigest(),
        hooks_sha256=hashlib.sha256((profile/'native_hooks.json').read_bytes()).hexdigest(),
        node=manifest['node'],hook_trust='one invocation bypass after external source/hash review',
        remote_plugins_enabled=False,native_hook_activation_verified=False)
    (output/'effective_profile.json').write_text(json.dumps(proof,indent=2)+'\n')
    return proof
