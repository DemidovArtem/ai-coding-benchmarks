"""Install and prove the pinned native ECC profile in a protected container."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from experiment.profiles import activate_profile
from experiment.runner import ROOT, save


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def observe_runtime(setup, output):
    observation = {
        'image_id': subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', setup.container_name], text=True).strip(),
        'codex': setup.docker_exec(['codex', '--version']).stdout.strip().removeprefix('codex-cli '),
        'config_sha256': setup.docker_exec(['sha256sum', '/home/fakeroot/.codex/config.toml']).stdout.split()[0],
        'node_sha256': setup.docker_exec(['sha256sum', '/usr/local/bin/node']).stdout.split()[0]}
    save(output / 'runtime_observation.json', observation)
    return observation


def resume_after_quota(agent, setup, output, resume, on_state, sleep=time.sleep):
    """Wait in the existing host process and resume only a verified idle agent tree."""
    from experiment.quota import wait_for_quota
    while agent._last_rate_limit:
        if agent._last_fatal_error or not agent.session_id:
            raise RuntimeError('Cannot safely resume the rate-limited ECC invocation')
        started = time.monotonic(); on_state('waiting_quota')
        wait_for_quota(output)
        while True:
            status = setup.docker_exec(['pgrep', '-x', 'codex'], check=False).returncode
            if status == 1:
                break
            if status != 0:
                raise RuntimeError('Cannot verify that the ECC agent tree is idle')
            sleep(60)
        agent.quota_wait_seconds += time.monotonic() - started
        on_state('running')
        if resume(agent.session_id, 'Quota is available again. Continue the same dispatched task from the retained code and history. '
                  'Preserve all prior work and tags; do not start another task.'):
            return True
    return False


def require_activation(config):
    proof = json.loads((ROOT / config['ecc']['smoke_result']).read_text())
    expected = {'source_commit': config['ecc']['source_commit'],
                'image_id': config['benchmark']['skill_runtime_image_id'],
                'codex': config['codex']['version'], 'model': config['codex']['model'],
                'reasoning_effort': config['codex']['reasoning_effort']}
    if not proof.get('success') or any(proof.get(key) != value for key, value in expected.items()):
        raise ValueError('ECC activation is missing or belongs to different frozen inputs')
    for key in ('native_hook_activation_verified', 'skill_activation_verified', 'subagent_activation_verified', 'runtime_verified'):
        if proof.get(key) is not True:
            raise ValueError('ECC capability was not proven: ' + key)


def freeze(path):
    """Freeze this new cohort without modifying any historical input hashes."""
    import csv
    from experiment.continuous import verify_selection, verify_images
    from experiment.runner import validate
    config = json.loads(path.read_text())
    if config.get('measurement_started') or config.get('stage') not in ('ecc_preflight', 'ecc_frozen'):
        raise ValueError('Only an unstarted ECC cohort may be frozen')
    require_activation(config)
    continuation = json.loads((ROOT / 'reports/ecc_continuation_smoke.json').read_text())
    if not continuation.get('success') or not continuation.get('native_resume_verified') or not continuation.get('native_checkpoint_verified'):
        raise ValueError('ECC native continuation checkpoint must be verified')
    workspace = ROOT / config['benchmark']['dataset_root'] / config['benchmark']['repo']
    with (workspace / 'dependencies.csv').open() as handle:
        verify_selection(config['benchmark']['continuous_pilot']['milestones'], list(csv.DictReader(handle)))
    verify_images(config)
    files = [*sorted((ROOT / 'experiment').glob('*.py')), *sorted((ROOT / 'profiles/ecc').rglob('*')),
             *sorted((ROOT / config['benchmark']['runtime_policy_root']).rglob('*')),
             ROOT / 'reports/ecc_protocol.md', ROOT / 'reports/ecc_smoke.json',
             ROOT / 'reports/ecc_continuation_smoke.json', ROOT / 'reports/ecc_grader_images.json',
             ROOT / config['sonar']['setup_candidates'], ROOT / config['sonar']['analysis_protocol'],
             workspace / 'metadata.json', workspace / 'dependencies.csv', workspace / 'milestones.csv']
    for task in config['benchmark']['continuous_pilot']['milestones']:
        files.extend((workspace / 'srs' / task).rglob('*'))
        files.extend((workspace / 'test_results' / task).rglob('*'))
    config['pins']['file_sha256'] = {str(p.relative_to(ROOT)): digest(p) for p in files if p.is_file()}
    config['pins']['git_commits']['vendor/ECC'] = config['ecc']['source_commit']
    config['stage'] = 'ecc_frozen'
    validate(config)
    save(path, config)


def framework(effort='high'):
    from harness.e2e.agents.codex import CodexFramework

    class ECCFramework(CodexFramework):
        # Only the reviewed local plugin is enabled; other product tools stay off.
        BENCHMARK_DISABLED_FEATURES = tuple(
            name for name in CodexFramework.BENCHMARK_DISABLED_FEATURES if name != 'plugins')

        def get_container_env_vars(self):
            return [*super().get_container_env_vars(), '-e', 'ECC_AGENT_DATA_HOME=/home/fakeroot/.ecc']

        def extract_session_id_from_container(self, container_name):
            # The upstream newest-rollout heuristic selects the last child instead of the executor.
            script = '''
import json,pathlib
roots=[]
for p in pathlib.Path('/home/fakeroot/.codex/sessions').rglob('*.jsonl'):
 with p.open() as f: m=json.loads(next(f))['payload']
 if not m.get('parent_thread_id'): roots.append(m['id'])
assert len(set(roots))==1, 'ECC requires exactly one authoritative root thread'
print(roots[0])
'''
            return subprocess.check_output(['docker', 'exec', container_name, 'python3', '-c', script], text=True).strip()

        def build_run_command(self, *args, **kwargs):
            return super().build_run_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

        def build_resume_command(self, *args, **kwargs):
            return super().build_resume_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

    return ECCFramework(reasoning_effort=effort)


def native_evidence(directory):
    """Deduplicate response IDs, including copies inherited by forked rollouts."""
    sessions, responses, events, declared = {}, {}, {}, {}
    for path in sorted(Path(directory).rglob('*.jsonl')):
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        meta = rows[0]['payload']; owner = meta['id']
        sessions[owner] = {key: meta.get(key) for key in ('id', 'parent_thread_id', 'agent_role', 'cli_version')}
        events[owner] = rows
        for row in rows:
            if row.get('type') != 'token_usage_record':
                continue
            payload = row['payload']; key = payload['response_id']
            value = {'thread_id': payload['thread_id'], 'usage': payload['usage']}
            if key in responses and responses[key] != value:
                raise ValueError('Conflicting usage for the same native response')
            responses[key] = value
            declared.setdefault(payload['thread_id'], []).append(payload.get('thread_token_usage', {}))
    roots = [key for key, value in sessions.items() if not value['parent_thread_id']]
    if len(roots) != 1:
        raise ValueError('Expected one root and only its descendant sessions')
    root = roots[0]
    for session, meta in sessions.items():
        if session != root and meta['parent_thread_id'] != root:
            raise ValueError('Unexpected session outside the frozen one-level agent tree')
    if any(row['thread_id'] not in sessions for row in responses.values()):
        raise ValueError('Usage references a missing native session')
    fields = ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')
    usage = {}
    for session in sessions:
        own = [r['usage'] for r in responses.values() if r['thread_id'] == session]
        usage[session] = {key: sum(r[key] for r in own) if own and all(type(r.get(key)) is int and r[key] >= 0 for r in own) else None for key in fields}
        for key in fields:
            counters = [row[key] for row in declared.get(session, []) if type(row.get(key)) is int and row[key] >= 0]
            if not counters or usage[session][key] != max(counters):
                usage[session][key] = None
    totals = {key: sum(u[key] for u in usage.values()) if usage and all(u[key] is not None for u in usage.values()) else None for key in fields}
    return {'root_session_id': root, 'sessions': sessions, 'per_thread': usage, 'total': totals,
            'response_count': len(responses), 'counter_semantics': 'sum unique native response usage per thread; parent excludes children'}, events


def audit_smoke(output, config):
    usage, events = native_evidence(output / 'sessions')
    root = usage['root_session_id']; parent = events[root]
    children = [key for key in events if key != root]
    contexts = [row['payload'] for key in events for row in events[key] if row['type'] == 'turn_context']
    messages = [row['payload'] for row in parent if row['type'] == 'response_item' and row['payload'].get('role') == 'developer']
    texts = [' '.join(part.get('text', '') for part in msg.get('content', [])) for msg in messages]
    calls = [row['payload'] for row in parent if row['type'] == 'response_item' and row['payload'].get('type') in ('custom_tool_call', 'function_call')]
    cli = [json.loads(line) for line in (output / 'log/agent_stdout.txt').read_text().splitlines() if line.startswith('{')]
    completions = [row['usage'] for row in cli if row.get('type') == 'turn.completed']
    native_hook = any(text.startswith('Project type: ') and '"primary":"rust"' in text for text in texts)
    skill = any('plugins/cache/ecc/ecc/2.2.3/skills' in text and 'verification-loop' in text for text in texts)
    skill_read = any('verification-loop/SKILL.md' in row.get('input', '') for row in calls)
    settings = bool(contexts) and all(row.get('model') == config['codex']['model'] and row.get('effort') == config['codex']['reasoning_effort'] for row in contexts)
    parent_only = bool(completions) and all(completions[-1].get(key) == value for key, value in usage['per_thread'][root].items())
    child_used = len(children) == 1 and usage['sessions'][children[0]]['agent_role'] == 'explorer' and usage['per_thread'][children[0]]['input_tokens'] is not None
    observed = json.loads((output / 'runtime_observation.json').read_text())
    runtime_ok = (observed['image_id'] == config['benchmark']['skill_runtime_image_id']
                  and observed['codex'] == config['codex']['version']
                  and all(meta['cli_version'] == observed['codex'] for meta in usage['sessions'].values())
                  and observed['config_sha256'] == digest(ROOT / 'profiles/ecc/config.toml')
                  and observed['node_sha256'] == json.loads((ROOT / 'profiles/ecc/manifest.json').read_text())['node']['sha256'])
    result = {'kind': 'activation_smoke_not_measured', 'variant': 'ecc',
              'success': native_hook and skill and skill_read and settings and parent_only and child_used and runtime_ok,
              'source_commit': config['ecc']['source_commit'], 'image_id': observed['image_id'],
              'codex': observed['codex'], 'model': contexts[-1].get('model'), 'reasoning_effort': contexts[-1].get('effort'),
              'runtime_verified': runtime_ok, 'effective_config_sha256': observed['config_sha256'],
              'native_hook_activation_verified': native_hook, 'skill_activation_verified': skill and skill_read,
              'subagent_activation_verified': child_used and settings, 'parent_excludes_child_usage_verified': parent_only,
              'usage': usage, 'limitations': ['Native subagent sandbox inherits the isolated invocation bypass; role instructions remain read-only.',
                  'Model self-report did not identify SessionStart; native developer context proves execution.',
                  'Upstream newest-rollout session selection returned the child; ECC overrides it using root metadata.']}
    save(output / 'audit.json', result)
    return result


def require_idle_sessions(setup, events):
    if setup.docker_exec(['pgrep', '-x', 'codex'], check=False).returncode != 1:
        raise ValueError('An ECC process is still active; preserve the container')
    for rows in events.values():
        turns = [row['payload'].get('type') for row in rows if row['type'] == 'event_msg'
                 and row['payload'].get('type') in ('task_started', 'task_complete', 'turn_aborted')]
        if not turns or turns[-1] not in ('task_complete', 'turn_aborted'):
            raise ValueError('An ECC agent is unfinished; preserve the container before continuing')


def checkpoint(runner, output, metadata):
    """Retain the entire native agent tree and memory, excluding authentication."""
    from experiment.session_store import backup_stores
    setup = runner.container_setup
    for remote, target in (('/home/fakeroot/.codex/sessions', 'native_sessions'),
                           ('/home/fakeroot/.ecc', 'ecc_state')):
        subprocess.run(['docker', 'cp', runner.container_name + ':' + remote, str(output / target)], check=True, capture_output=True)
    usage, events = native_evidence(output / 'native_sessions')
    if usage['root_session_id'] != metadata['executor_session_id']:
        raise ValueError('ECC executor identity changed to a child or unrelated thread')
    require_idle_sessions(setup, events)
    for rows in events.values():
        contexts = [r['payload'] for r in rows if r['type'] == 'turn_context']
        if not contexts or any(c.get('model') != metadata['model'] or c.get('effort') != metadata['reasoning_effort'] for c in contexts):
            raise ValueError('ECC native model or effort differs from the frozen profile')
    if setup.docker_exec(['sha256sum', '/home/fakeroot/.codex/config.toml']).stdout.split()[0] != digest(ROOT / 'profiles/ecc/config.toml'):
        raise ValueError('ECC configuration changed during the trajectory')
    raw = output / 'native_store_raw'; raw.mkdir()
    for name in ('state_5.sqlite', 'thread_history_1.sqlite'):
        for suffix in ('', '-wal', '-shm'):
            source = '/home/fakeroot/.codex/' + name + suffix
            if setup.docker_exec(['test', '-f', source], check=False).returncode == 0:
                subprocess.run(['docker', 'cp', runner.container_name + ':' + source, str(raw / (name + suffix))], check=True, capture_output=True)
    backup_stores(raw, output / 'native_session_store'); shutil.rmtree(raw)
    proof = json.loads((output / 'effective_profile.json').read_text())
    for filename, base in (('cumulative.patch', proof['starting_commit']), ('incremental.patch', metadata['input_commit'])):
        patch = subprocess.check_output(['docker', 'exec', '-w', '/testbed', runner.container_name, 'git', '-c', 'safe.directory=/testbed',
                                         'diff', '--binary', '--full-index', base, 'HEAD', '--'])
        (output / filename).write_bytes(patch)
    manifest = {str(path.relative_to(output)): digest(path) for directory in ('ecc_state', 'native_sessions', 'native_session_store')
                for path in (output / directory).rglob('*') if path.is_file()}
    save(output / 'ecc_checkpoint.json', {'root_session_id': usage['root_session_id'], 'files_sha256': manifest,
                                        'memory_files': sum(name.startswith('ecc_state/') for name in manifest)})
    save(output / 'ecc_usage.json', usage)
    return usage


def verify_live_checkpoint(runner, directory, record):
    """Resume only an idle, byte-identical native checkpoint in the retained container."""
    from experiment.continuous import assert_boundary
    setup = runner.container_setup
    assert_boundary(runner, record['ending_commit'])
    if setup.docker_exec(['pgrep', '-x', 'codex'], check=False).returncode != 1:
        raise ValueError('The retained ECC agent tree is not verified idle')
    image = subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', setup.container_name], text=True).strip()
    config_hash = setup.docker_exec(['sha256sum', '/home/fakeroot/.codex/config.toml']).stdout.split()[0]
    if image != record['effective_profile']['image_id'] or config_hash != digest(ROOT / 'profiles/ecc/config.toml'):
        raise ValueError('The retained ECC runtime or profile changed')
    proof = json.loads((directory / 'ecc_checkpoint.json').read_text())
    if proof['root_session_id'] != runner.agent_runner.session_id:
        raise ValueError('The retained ECC root differs from the checkpoint')
    for name, expected in proof['files_sha256'].items():
        if digest(directory / name) != expected:
            raise ValueError('Retained ECC checkpoint bytes changed: ' + name)
        if name.startswith(('native_sessions/', 'ecc_state/')):
            group, suffix = name.split('/', 1)
            remote = ('/home/fakeroot/.codex/sessions/' if group == 'native_sessions' else '/home/fakeroot/.ecc/') + suffix
            if setup.docker_exec(['sha256sum', remote]).stdout.split()[0] != expected:
                raise ValueError('Live ECC history or memory differs from the checkpoint')


def install(setup, output, config, repository_mount=None):
    source, profile = ROOT / 'vendor/ECC', ROOT / 'profiles/ecc'
    manifest = json.loads((profile / 'manifest.json').read_text())
    if subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != manifest['source_commit']:
        raise ValueError('ECC source commit differs from its reviewed pin')
    if subprocess.check_output(['git', '-C', str(source), 'status', '--porcelain', '--untracked-files=no'], text=True).strip():
        raise ValueError('Tracked ECC source has changed')
    if digest(source / 'package-lock.json') != manifest['dependency_lock_sha256']:
        raise ValueError('ECC dependency lock changed')
    if not (source / 'node_modules').is_dir():
        raise ValueError('Prepare ECC lockfile dependencies before entering quarantine')
    proof = activate_profile(setup, output, config, 'baseline', repository_mount=repository_mount)
    name = setup.container_name
    actual_image = subprocess.check_output(['docker', 'inspect', '--format', '{{.Image}}', name], text=True).strip()
    if actual_image != config['benchmark']['skill_runtime_image_id']:
        raise ValueError('ECC runtime differs from the frozen image')

    def copy(src, target):
        subprocess.run(['docker', 'cp', str(src), name + ':' + target], check=True, capture_output=True)

    setup.docker_exec(['mkdir', '-p', '/opt/ecc', '/home/fakeroot/.codex/agents'], user='root')
    for part in manifest['source_paths'] + ['node_modules']:
        copy(source / part, '/opt/ecc/' + part)
    result = setup.docker_exec(['sha256sum', '/usr/local/bin/node'])
    if result.stdout.split()[0] != manifest['node']['sha256']:
        raise ValueError('ECC Node runtime differs from the reviewed pin')
    for args in (['plugin', 'marketplace', 'add', '/opt/ecc', '--json'], ['plugin', 'add', 'ecc@ecc', '--json']):
        setup.docker_exec(['codex', '--enable', 'plugins', *args], user='fakeroot')
    copy(profile / 'config.toml', '/home/fakeroot/.codex/config.toml')
    copy(str(profile / 'agents') + '/.', '/home/fakeroot/.codex/agents')
    copy(profile / 'AGENTS.md', '/home/fakeroot/.codex/AGENTS.md')
    setup.docker_exec(['chown', '-R', 'root:root', '/opt/ecc', '/home/fakeroot/.codex/agents',
                      '/home/fakeroot/.codex/plugins', '/home/fakeroot/.codex/config.toml',
                      '/home/fakeroot/.codex/AGENTS.md'], user='root')
    setup.docker_exec(['chmod', '-R', 'a-w', '/opt/ecc', '/home/fakeroot/.codex/agents',
                      '/home/fakeroot/.codex/plugins', '/home/fakeroot/.codex/config.toml',
                      '/home/fakeroot/.codex/AGENTS.md'], user='root')
    installed = json.loads(setup.docker_exec(['codex', 'plugin', 'list', '--json'], user='fakeroot').stdout)['installed']
    if len(installed) != 1 or installed[0]['pluginId'] != 'ecc@ecc' or not installed[0]['enabled']:
        raise ValueError('Only the reviewed ECC plugin may be enabled')
    audit = setup.docker_exec(['python3', '-c', '''
import hashlib,json,pathlib,tomllib
p=pathlib.Path('/home/fakeroot/.codex/config.toml'); c=tomllib.loads(p.read_text())
assert c['forced_login_method']=='chatgpt' and c['web_search']=='disabled'
assert set(c['mcp_servers'])=={'chrome-devtools'} and c['mcp_servers']['chrome-devtools']['enabled'] is False
assert c['features']['plugins'] and c['features']['multi_agent'] and not c['features']['remote_plugin']
for p in pathlib.Path('/home/fakeroot/.codex/agents').glob('*.toml'):
 r=tomllib.loads(p.read_text()); assert r['model']==c['model'] and r['model_reasoning_effort']==c['model_reasoning_effort']
files={str(p.relative_to('/opt/ecc')):hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('/opt/ecc').rglob('*') if p.is_file()}
print(json.dumps({'effective_config':c,'installed_files_sha256':files}))
'''], user='fakeroot')
    details = json.loads(audit.stdout)
    save(output / 'ecc_installed_files.json', details.pop('installed_files_sha256'))
    details['profile_config'] = details['effective_config'].copy()
    details['effective_config']['sandbox_mode'] = 'danger-full-access'
    proof.update(details, variant='ecc', skill='ecc', skill_version=manifest['version'], image_id=actual_image,
                 source_commit=manifest['source_commit'], label=manifest['label'],
                 config_sha256=digest(profile / 'config.toml'), plugin_registration=installed,
                 native_hook_activation_verified=False, subagent_activation_verified=False,
                 remote_plugins_enabled=False, memory_policy='cold trajectory; retained across sequential tasks')
    save(output / 'effective_profile.json', proof)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--smoke', action='store_true')
    mode.add_argument('--audit', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    from harness.e2e.container_setup import ContainerSetup
    from harness.e2e.agent_runner import AgentRunner
    from experiment.continuous import runtime_binding
    from experiment.quota import wait_for_quota
    from experiment.security import credential_values, redact_artifacts

    config = json.loads(args.config.read_text())
    if args.smoke:
        from experiment.runner import validate
        validate(config)
    output = args.output.resolve()
    if args.audit:
        result = audit_smoke(output, config)
        print(json.dumps(result))
        return 0 if result['success'] else 1
    output.mkdir(parents=True, exist_ok=False); output.chmod(0o700)
    fixture = output / 'fixture'; fixture.mkdir()
    (fixture / 'lib.rs').write_text('pub fn ecc_activation_fixture() -> bool { true }\n')
    for command in (['init', '-q'], ['add', '.'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Neutral fixture']):
        subprocess.run(['git', '-C', str(fixture), *command], check=True, capture_output=True)
    binding = runtime_binding(config, output / 'bindings')
    os.environ.update(binding.env)
    setup = ContainerSetup(container_name='ecc-' + output.name, image_name=config['benchmark']['skill_runtime_image_id'],
        agent_name='codex', agent_framework_name='codex', agent_version=config['codex']['version'],
        repo_name=config['benchmark']['repo'], runtime_policy_binding=binding)
    result = {'kind': 'activation_smoke_not_measured', 'success': False, 'variant': 'ecc'}
    try:
        wait_for_quota(output)
        setup.start_container(extra_mounts=['--mount', f'type=bind,src={fixture},dst=/testbed,readonly'])
        setup.lock_network()
        install(setup, output, config, repository_mount=fixture)
        setup.prepare_agent_invocation()
        agent = AgentRunner(container_name=setup.container_name, agent_name='codex', model=config['codex']['model'],
            reasoning_effort=config['codex']['reasoning_effort'], timeout_ms=240000, log_dir=output / 'log')
        agent._framework = framework(config['codex']['reasoning_effort'])
        prompt = ('Activation check on a neutral read-only fixture. Read the installed ECC verification-loop skill '
                  'and name it. Spawn exactly one configured explorer subagent to read lib.rs and report the function name. '
                  'Wait for it. Report its answer and whether ECC SessionStart context was supplied. '
                  'Do not edit files, use web/MCP, change settings, or run another model CLI.')
        ok, session = agent.run(prompt)
        agent.extract_trace(output / 'log')
        result.update(session_id=session, model_turn_completed=ok)
        # Native rollouts are authoritative for hooks and parent/child accounting.
        subprocess.run(['docker', 'cp', setup.container_name + ':/home/fakeroot/.codex/sessions', str(output / 'sessions')], check=True, capture_output=True)
        subprocess.run(['docker', 'cp', setup.container_name + ':/home/fakeroot/.ecc', str(output / 'ecc_state')], check=True, capture_output=True)
        observe_runtime(setup, output)
        result.update(audit_smoke(output, config))
    except Exception as error:
        result['error'] = str(error)
        if isinstance(error, subprocess.CalledProcessError):
            result['diagnostic'] = (error.stderr or '')[-3000:]
    finally:
        save(output / 'result.json', result)
        redact_artifacts(output, credential_values(Path.home() / '.codex/auth.json'))
    print(json.dumps(result))
    return 0 if result['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
