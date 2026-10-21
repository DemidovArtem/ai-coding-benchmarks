"""Recover a withheld executor step without replacing its recorded quota stop."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import tomllib

from experiment.collect import load
from experiment.continuous import (assert_boundary, check_resources, events_from, preserve_and_collect,
                                   resume_step, update_progress, verify_dispatch, verify_images)
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact


def verify_retained_config(actual, expected):
    actual = tomllib.loads(actual)
    projects = actual.pop('projects', None)
    if projects not in (None, {'/testbed': {'trust_level': 'trusted'}}) or actual != tomllib.loads(expected):
        raise ValueError('Retained profile changed beyond the Codex project trust entry')


def recovery_input(blocked, previous, config):
    metadata = load(blocked / 'run_metadata.json', {})
    if (metadata.get('state') != 'failed' or metadata.get('failure_category') != 'quota_pressure'
            or metadata.get('step') != 2 or metadata.get('variant') not in ('baseline', 'caveman', 'ponytail')):
        raise ValueError('Only a withheld second baseline or native-skill step can use this recovery')
    for name in ('log/session_history.jsonl', 'log/agent_stdout.txt', 'log/resume_message.txt', 'dispatched_task.txt'):
        if (blocked / name).exists():
            raise ValueError('Blocked step may already have invoked the executor')
    if (previous.get('resolved') is not True or previous.get('collection_errors')
            or previous.get('setup_fingerprint') != metadata.get('setup_fingerprint')
            or metadata.get('setup_fingerprint') != setup_fingerprint(config)[0]
            or previous.get('continuous', {}).get('trajectory_id') != metadata.get('trajectory_id')
            or previous['continuous'].get('step') != 1
            or previous['continuous'].get('executor_session_id') != metadata.get('executor_session_id')):
        raise ValueError('Previous immutable submission and executor session are unverified')
    return metadata


def recover(config, blocked, output):
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.skill_trial import assert_no_profile_artifacts

    old = load(blocked / 'run_metadata.json')
    variant = old['variant']
    native = variant in ('caveman', 'ponytail')
    chain = old['trajectory_id']
    previous = load(ROOT / 'reports' / (chain + '_s01.json'))
    recovery_input(blocked, previous, config)
    if output.exists() or (ROOT / 'results/trials' / output.name).exists():
        raise ValueError('Recovery output must be fresh; previous failures cannot be overwritten')
    benchmark = config['benchmark']
    workspace = ROOT / benchmark['dataset_root'] / benchmark['repo']
    milestone = benchmark['continuous_pilot']['milestones'][1]
    name = benchmark['continuous_pilot']['milestones'][0] + '-' + chain + '-runner'
    info = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
    if info['Image'] != benchmark['skill_runtime_image_id']:
        raise ValueError('Retained container image differs from the frozen cohort')
    if {item['Destination'] for item in info['Mounts']} != {'/tmp/host-codex/auth.json'} or any(item['RW'] for item in info['Mounts']):
        raise ValueError('Retained container mounts differ from the protected runtime')
    if not info['State']['Running']:
        subprocess.run(['docker', 'start', name], check=True, capture_output=True)
    session = old['executor_session_id']
    task_path = '/home/fakeroot/continuous-step-2.txt'
    task = None

    class NativeHooks(CodexFramework):
        def build_resume_command(self, *args, **kwargs):
            return super().build_resume_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

    class RecoveryRunner(MilestoneRunner):
        def _load_prompt(self):
            nonlocal task
            original = super()._load_prompt()
            (output / 'original_task.txt').write_text(original)
            task = original + ('\n\nThis is one step of a sequential pilot. Preserve prior work and submission tags. '
                'Implement only this task. After committing and tagging this step, stop and await the next user turn.\n')
            local = output / 'dispatched_task.txt'
            local.write_text(task)
            self.container_setup.verify_network_lockdown()
            quota = read_quota()
            save(output / 'quota_before_executor.json', quota)
            check_quota(quota, config['resources']['quota_stop_percent'])
            subprocess.run(['docker', 'cp', str(local), name + ':' + task_path], check=True, capture_output=True)
            self.container_setup.docker_exec(['chown', 'root:root', task_path], user='root')
            self.container_setup.docker_exec(['chmod', '0444', task_path], user='root')
            return ('Continue in this repository and session. Your first shell command must be `cat ' + task_path
                    + '`. Read the complete task and any supplied plan, then follow it. Do not work on other tasks.')

        def _run_evaluation(self, snapshot):
            audit = verify_dispatch(events_from(output / 'log/agent_stdout.txt'), session, task_path, task)
            audit.update(input_commit=previous['ending_commit'], milestone_id=milestone)
            save(output / 'dispatch.json', audit)
            assert_no_profile_artifacts(snapshot)
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot)
            finally:
                save(output / 'durations.json', {'evaluation': time.monotonic() - started})

    runner = RecoveryRunner(workspace_root=workspace, milestone_id=milestone,
        srs_path=workspace / 'srs' / milestone / 'SRS.md', output_dir=output,
        image_name=benchmark['skill_runtime_image_id'], agent_name='codex', agent_version=config['codex']['version'],
        model=config['codex']['model'], reasoning_effort=config['codex']['reasoning_effort'],
        timeout_ms=benchmark['timeout_seconds'] * 1000, main_branch=benchmark['main_branch'], keep_container=True)
    runner.container_name = runner.container_setup.container_name = runner.agent_runner.container_name = name
    framework = NativeHooks if native else CodexFramework
    runner.agent_runner._framework = framework(reasoning_effort=config['codex']['reasoning_effort'])
    runner.agent_runner.session_id = session
    runner._snapshot_baseline_commit = previous['starting_commit']
    assert_boundary(runner, previous['ending_commit'])
    if runner._get_tag_hash('agent-impl-' + benchmark['continuous_pilot']['milestones'][0]) != previous['ending_commit']:
        raise ValueError('Previous submission tag changed')
    if runner._verify_tag_exists():
        raise ValueError('Second task has already been submitted')
    processes = runner.container_setup.docker_exec(['ps', '-eo', 'comm']).stdout.splitlines()
    if any(item.strip() in ('codex', 'codex-linux-x64') for item in processes):
        raise ValueError('An executor process is already running')
    if runner.agent_runner._framework.extract_session_id_from_container(name) != session:
        raise ValueError('Retained Codex thread differs from the withheld step')
    verify_retained_config(runner.container_setup.docker_exec(['cat', '/home/fakeroot/.codex/config.toml']).stdout,
                           (ROOT / 'profiles' / variant / 'config.toml').read_text())
    hook_path = '/home/fakeroot/.codex/skill_hook_audit.jsonl'
    if native:
        actual = runner.container_setup.docker_exec(['sha256sum', '/home/fakeroot/.codex/hooks.json']).stdout.split()[0]
        if actual != hashlib.sha256((ROOT / 'profiles' / variant / 'native_hooks.json').read_bytes()).hexdigest():
            raise ValueError('Retained native hooks changed')
        old_audit = runner.container_setup.docker_exec(['cat', hook_path]).stdout.splitlines()
    else:
        for path in ('/AGENTS.md', '/home/AGENTS.md', '/home/fakeroot/AGENTS.md', '/testbed/AGENTS.md',
                     '/testbed/.codex', '/testbed/.agents', '/testbed/.serena', '/home/fakeroot/.agents',
                     '/home/fakeroot/.codex/AGENTS.md', '/home/fakeroot/.codex/hooks.json'):
            if runner.container_setup.docker_exec(['test', '!', '-e', path]).returncode:
                raise ValueError('Unexpected retained baseline instructions or hooks: ' + path)
    # A stopped container loses its network namespace; restore the same pinned protective rules before inference.
    runner.container_setup.lock_network()
    if not runner.agent_runner.refresh_container_credentials():
        raise RuntimeError('OAuth refresh failed before recovery')
    output.chmod(0o700)
    (output / 'log').mkdir(exist_ok=True)
    save(output / 'effective_profile.json', previous['effective_profile'])
    step_config = json.loads(json.dumps(config))
    step_config['benchmark']['smoke_milestone'] = milestone
    save(output / 'experiment.json', step_config)
    metadata = {**old, 'state': 'running', 'failure_category': None, 'error': None,
        'started_at': datetime.now(timezone.utc).isoformat(), 'duration_seconds': None,
        'resume': {'attempt_of': blocked.name, 'same_session_required': session,
                   'original_failure_preserved': str(blocked), 'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'execution_override': config['execution_override'],
        'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    save(output / 'run_metadata.json', metadata)
    save(output / 'quota_before.json', read_quota())
    update_progress(chain, state='running', completed_steps=1, active_step=2, failure_category=None, resumed_attempt=output.name)
    started = time.monotonic()
    try:
        # resume_step also validates the clean boundary, same session and exact immutable snapshot.
        original_resume = runner.agent_runner.resume_session
        def timed_resume(*args, **kwargs):
            execute_started = time.monotonic()
            try:
                return original_resume(*args, **kwargs)
            finally:
                save(output / 'execution.json', {'duration_seconds': time.monotonic() - execute_started})
        runner.agent_runner.resume_session = timed_resume
        result = resume_step(runner, session, previous['ending_commit'])
        commit = runner._get_tag_hash('agent-impl-' + milestone)
        assert_boundary(runner, commit)
        if runner.container_setup.docker_exec_git('merge-base', '--is-ancestor', previous['ending_commit'], commit).returncode:
            raise ValueError('Recovered submission does not descend from the preceding step')
        if runner._get_tag_hash('agent-impl-' + benchmark['continuous_pilot']['milestones'][0]) != previous['ending_commit']:
            raise ValueError('Previous submission tag moved during recovery')
        if native:
            subprocess.run(['docker', 'cp', name + ':' + hook_path, str(output / 'hook_audit.jsonl')], check=True, capture_output=True)
            audit = [json.loads(line) for line in (output / 'hook_audit.jsonl').read_text().splitlines()]
            field = 'caveman_mode_context' if variant == 'caveman' else 'full_mode_context'
            active = any(row.get(field) for row in audit[len(old_audit):])
            save(output / 'skill_activation.json', {'variant': variant, 'native_hook_activation_verified': active, 'audit': audit})
            if not active:
                raise RuntimeError('Recovered native activation is unverified')
        if load(output / 'evaluation/evaluation_result.json').get('error_message'):
            raise RuntimeError('Recovered grader infrastructure is unverified')
        metadata.update(state='finished', returncode=0 if result.resolved else 1)
    except Exception as error:
        category = 'quota_pressure' if runner.agent_runner._last_rate_limit or str(error).startswith('Quota pressure') else 'continuous_recovery_failure'
        metadata.update(state='failed', failure_category=category, error=redact(str(error), credential_values(Path.home() / '.codex/auth.json')))
    finally:
        metadata['duration_seconds'] = time.monotonic() - started
        save(output / 'quota_after.json', read_quota())
        record, _ = preserve_and_collect(runner, output, step_config, metadata,
            previous['usage']['executor_cumulative'], previous['ending_commit'])
        update_progress(chain, state='finished' if metadata['state'] == 'finished' else 'failed',
            completed_steps=2 if metadata['state'] == 'finished' else 1, active_step=None,
            failure_category=metadata.get('failure_category'), last_step=output.name)
        if metadata['state'] == 'finished' and not record['collection_errors']:
            runner.container_setup.cleanup()
    return 0 if metadata['state'] == 'finished' else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('blocked', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT / 'reports/phase5_authorized_execution.json')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = load(args.config)
    validate(config)
    verify_images()
    check_resources(config)
    check_quota(read_quota(), config['resources']['quota_stop_percent'])
    lock = trial_lock(Path(config['resources']['runtime_root']))
    try:
        return recover(config, args.blocked.resolve(), args.output.resolve())
    finally:
        lock.close()


if __name__ == '__main__':
    raise SystemExit(main())
