"""Apply retained skills to the new Python runtime without changing historical pins."""

import hashlib
import json
from pathlib import Path
import subprocess

from experiment.profiles import activate_profile
from experiment.runner import ROOT, save
from experiment.serena_continuous import memory_state


def copy(setup, source, target):
    subprocess.run(['docker', 'cp', str(source), setup.container_name + ':' + target], check=True, capture_output=True)


def install(setup, output, config, variant):
    proof = activate_profile(setup, output, config, variant if variant != 'serena' else 'baseline')
    actual = subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', setup.container_name], text=True).strip()
    if actual != config['benchmark']['skill_runtime_image_id']:
        raise ValueError('Profile runtime differs from the common Python image')
    proof.update(variant=variant, image_id=actual)
    if variant in ('caveman', 'ponytail'):
        profile = ROOT / 'profiles' / variant
        manifest = json.loads((profile / 'manifest.json').read_text())
        if setup.docker_exec(['sha256sum', '/opt/experiment-node/node']).stdout.split()[0] != manifest['node']['sha256']:
            raise ValueError('Baked Node differs from the retained hook pin')
        for name, expected in manifest['files_sha256'].items():
            if hashlib.sha256((profile / 'assets' / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Retained skill asset changed: ' + name)
        setup.docker_exec(['mkdir', '-p', '/opt/experiment-skills/' + variant, '/opt/experiment-hooks'], user='root')
        copy(setup, str(profile / 'assets') + '/.', '/opt/experiment-skills/' + variant)
        copy(setup, profile / 'manifest.json', '/opt/experiment-hooks/manifest.json')
        for name in ('dispatch.py', 'caveman_dispatch.py'):
            copy(setup, ROOT / 'profiles/hooks' / name, '/opt/experiment-hooks/' + name)
        setup.docker_exec(['chmod', '-R', 'a-w', '/opt/experiment-skills', '/opt/experiment-hooks'], user='root')
        copy(setup, profile / 'native_hooks.json', '/home/fakeroot/.codex/hooks.json')
        setup.docker_exec(['chown', 'root:root', '/home/fakeroot/.codex/hooks.json'], user='root')
        setup.docker_exec(['chmod', '0444', '/home/fakeroot/.codex/hooks.json'], user='root')
        proof.update(skill=variant, skill_version=manifest['version'], mode=manifest['mode'],
                     native_hook_activation_verified=False, node_source='verified immutable common runtime',
                     manifest_sha256=hashlib.sha256((profile / 'manifest.json').read_bytes()).hexdigest())
    elif variant == 'serena':
        profile = ROOT / 'profiles/scikit_serena'
        runtime = json.loads((ROOT / 'profiles/scikit_runtime/manifest.json').read_text())
        if runtime.get('image_id') != actual or runtime.get('python_lsp_verified') is not True:
            raise ValueError('Verified Python MCP runtime is required')
        setup.docker_exec(['mkdir', '-p', '/home/fakeroot/.serena-profile'], user='root')
        copy(setup, profile / 'config.toml', '/home/fakeroot/.codex/config.toml')
        copy(setup, profile / 'server_config.yml', '/home/fakeroot/.serena-profile/serena_config.yml')
        copy(setup, profile / 'AGENTS.md', '/home/fakeroot/.codex/AGENTS.md')
        setup.docker_exec(['chown', '-R', 'fakeroot:fakeroot', '/home/fakeroot/.serena-profile'], user='root')
        setup.docker_exec(['chown', 'root:root', '/home/fakeroot/.codex/config.toml', '/home/fakeroot/.codex/AGENTS.md'], user='root')
        setup.docker_exec(['chmod', '0444', '/home/fakeroot/.codex/config.toml', '/home/fakeroot/.codex/AGENTS.md'], user='root')
        setup.docker_exec(['python3', '-c', "from pathlib import Path;p=Path('/testbed/.git/info/exclude');p.write_text(p.read_text()+'\\n/.serena/\\n')"], user='root')
        if memory_state(setup)['count']:
            raise ValueError('Profile installation requires cold memory before exact parent restore')
        proof.update(skill='serena', serena_version=runtime['serena_version'], python_lsp_verified=True,
                     memory_policy='cold repetition; exact trajectory memories restored between steps',
                     config_sha256=hashlib.sha256((profile / 'config.toml').read_bytes()).hexdigest(),
                     continuous_policy_sha256=hashlib.sha256((profile / 'AGENTS.md').read_bytes()).hexdigest())
    elif variant != 'baseline':
        raise ValueError('Unsupported scikit configuration')
    save(output / 'effective_profile.json', proof)
    return proof
