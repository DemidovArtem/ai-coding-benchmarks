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


def install_serena(setup, output, config):
    """Register one cold local MCP profile only after its common runtime is verified."""
    expected = config['benchmark'].get('skill_runtime_image_id')
    runtime = json.loads((ROOT/'profiles/runtime/manifest.json').read_text())
    if not expected or runtime.get('image_id') != expected or runtime.get('rust_lsp_verified') is not True:
        raise ValueError('Verified shared Rust/MCP runtime is required')
    proof = activate_profile(setup,output,config,'baseline')
    name = setup.container_name
    def execute(*args):
        return subprocess.run(['docker','exec',name,*args],check=True,capture_output=True,text=True)
    actual = subprocess.check_output(['docker','inspect','--format','{{.Image}}',name],text=True).strip()
    if actual != expected:
        raise ValueError('Serena container differs from the common runtime pin')
    execute('python3','-c',"from pathlib import Path; assert not Path('/testbed/.serena').exists(); assert not Path('/home/fakeroot/.serena-profile').exists()")
    execute('mkdir','-p','/home/fakeroot/.serena-profile')
    for source,target in ((ROOT/'profiles/serena/config.toml','/home/fakeroot/.codex/config.toml'),
                          (ROOT/'profiles/serena/server_config.yml','/home/fakeroot/.serena-profile/serena_config.yml')):
        subprocess.run(['docker','cp',str(source),name+':'+target],check=True,capture_output=True)
    execute('chown','-R','fakeroot:fakeroot','/home/fakeroot/.serena-profile','/home/fakeroot/.codex/config.toml')
    execute('chmod','0700','/home/fakeroot/.serena-profile')
    check = execute('python3','-c',"import hashlib,json,pathlib,tomllib; p=pathlib.Path('/home/fakeroot/.codex/config.toml'); c=tomllib.loads(p.read_text()); assert set(c['mcp_servers'])=={'serena'}; assert not c.get('hooks') and not c.get('plugins'); assert all(v is False for v in c['features'].values()); assert c['mcp_servers']['serena']['env']['SERENA_USAGE_REPORTING']=='false'; print(json.dumps({'config_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'profile_config':c}))")
    staged = json.loads(check.stdout)
    expected_hash = hashlib.sha256((ROOT/'profiles/serena/config.toml').read_bytes()).hexdigest()
    if staged['config_sha256'] != expected_hash:
        raise ValueError('Serena profile hash differs from the frozen source')
    proof.update(staged,variant='serena',skill='serena',skill_version=runtime['serena_version'],
                 image_id=actual,memory_files_before=0,memory_bytes_before=0,memory_policy='cold independent trial',
                 mcp_activation_verified=False)
    (output/'effective_profile.json').write_text(json.dumps(proof,indent=2)+'\n')
    return proof
