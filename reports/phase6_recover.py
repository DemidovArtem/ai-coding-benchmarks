"""Resume the submitted Serena trajectory after a host restart, without replaying inference.

Operational adapter: frozen experiment modules and model conditions remain unchanged.
Only the already-submitted grader is retried; subsequent turns retain the same thread.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'vendor/SWE-Milestone')]

from experiment.collect import load
from experiment.continuous import (assert_boundary, check_resources, events_from, preserve_and_collect,
                                   resume_step, runtime_binding, update_progress, verify_dispatch, verify_images)
from experiment.continuous_resume import verify_retained_config
from experiment.phase6 import analyze
from experiment.quota import read_quota
from experiment.runner import check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact
from experiment.serena_continuous import memory_state, preserve_memory, verify_memory_boundary, verify_usage
from experiment.skill_trial import assert_no_profile_artifacts
from harness.e2e.run_milestone import MilestoneRunner


def task_text(original):
    return original + ('\n\nThis is one step of a sequential pilot. Preserve prior work and submission tags. '
        'Implement only this task. After committing and tagging this step, stop and await the next user turn.\n'
        '\nSerena memory mode: warm; read and reuse a memory retained from the previous task. Do not repeat onboarding.'
        '\nAfter the required first task-file read, follow the Serena continuous startup policy.\n')


def verify_checkpoint(metadata, previous, config, sidecar, snapshot):
    if (metadata['state'] != 'running' or metadata['variant'] != 'serena' or metadata['step'] != 2
            or metadata['trajectory_id'] != 'phase6_serena_r01'
            or metadata['setup_fingerprint'] != setup_fingerprint(config)[0]
            or previous['collection_errors'] or previous['trial_state'] != 'finished'
            or previous['continuous']['executor_session_id'] != metadata['executor_session_id']):
        raise ValueError('Recovery requires the exact interrupted Serena checkpoint')
    if not sidecar.get('ok') or hashlib.sha256(snapshot.read_bytes()).hexdigest() != sidecar['snapshot_sha256']:
        raise ValueError('Submitted snapshot integrity changed')


def withheld_output(runtime, name):
    """Retain each quota-observation failure; never retry a turn that reached inference."""
    output = runtime / name
    attempt = 0
    while output.exists():
        metadata = load(output / 'run_metadata.json', {})
        quota = load(output / 'quota_before_executor.json', {})
        if (metadata.get('state') != 'failed' or quota.get('status') != 'timeout'
                or any((output / p).exists() for p in ('execution.json', 'log/agent_stdout.txt',
                                                      'log/session_history.jsonl', 'log/resume_message.txt'))):
            raise ValueError('Existing step may have reached inference; automatic replay forbidden')
        attempt += 1
        output = runtime / (name + '_retry' + str(attempt).zfill(2))
    return output


def main():
    config = load(ROOT / 'reports/phase6_experiment.json')
    validate(config)
    verify_images(config)
    check_resources(config)
    check_quota(read_quota(), config['resources']['quota_stop_percent'])
    runtime = Path(config['resources']['runtime_root'])
    lock = trial_lock(runtime)
    chain = 'phase6_serena_r01'
    output = runtime / (chain + '_s02')
    interrupted = output / 'host_restart.json'
    collected = (ROOT / 'results/trials' / output.name).exists()
    old = load(interrupted)['original_metadata'] if collected else load(output / 'run_metadata.json')
    previous = load(ROOT / 'reports' / (chain + '_s01.json'))
    snapshot = output / 'evaluation/source_snapshot.tar'
    sidecar = load(snapshot.with_name('source_snapshot.integrity.json'))
    verify_checkpoint(old, previous, config, sidecar, snapshot)
    if not collected and (output / 'evaluation/evaluation_result.json').exists():
        raise ValueError('Recovery cannot overwrite a terminal result')
    if collected:
        recovered = load(ROOT / 'reports' / (output.name + '.json'))
        if (recovered['trial_state'] != 'finished' or recovered['collection_errors']
                or recovered['ending_commit'] != sidecar['agent_tag_commit']
                or recovered['setup_fingerprint'] != old['setup_fingerprint']):
            raise ValueError('Collected checkpoint is not a valid submitted step')
    benchmark = config['benchmark']
    workspace = ROOT / benchmark['dataset_root'] / benchmark['repo']
    milestones = benchmark['continuous_pilot']['milestones']
    name = milestones[0] + '-' + chain + '-runner'
    info = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
    if (info['Image'] != benchmark['skill_runtime_image_id']
            or {m['Destination'] for m in info['Mounts']} != {'/tmp/host-codex/auth.json'}
            or any(m['RW'] for m in info['Mounts'])):
        raise ValueError('Retained image or mounts changed')
    if not info['State']['Running']:
        subprocess.run(['docker', 'start', name], check=True, capture_output=True)
    session = old['executor_session_id']
    previous_memory = load(output / 'serena_state.json')['after']
    memory_before = load(output / 'serena_memory_before.json')
    verify_memory_boundary(memory_before, load(runtime / (chain + '_s01') / 'serena_state.json')['after'])
    task = (output / 'dispatched_task.txt').read_text()
    dispatch_path = '/home/fakeroot/continuous-step-2.txt'
    index = 2

    class RetainedRunner(MilestoneRunner):
        def _load_prompt(self):
            nonlocal task, dispatch_path, memory_before
            original = super()._load_prompt()
            self.container_setup.verify_network_lockdown()
            save(output / 'effective_profile.json', load(runtime / (chain + '_s01') / 'effective_profile.json'))
            memory_before = memory_state(self.container_setup)
            verify_memory_boundary(memory_before, previous_memory)
            save(output / 'serena_memory_before.json', memory_before)
            (output / 'original_task.txt').write_text(original)
            task = task_text(original)
            path = output / 'dispatched_task.txt'
            path.write_text(task)
            dispatch_path = '/home/fakeroot/continuous-step-' + str(index) + '.txt'
            subprocess.run(['docker', 'cp', str(path), name + ':' + dispatch_path], check=True, capture_output=True)
            self.container_setup.docker_exec(['chown', 'root:root', dispatch_path], user='root')
            self.container_setup.docker_exec(['chmod', '0444', dispatch_path], user='root')
            check_resources(config)
            quota = read_quota()
            save(output / 'quota_before_executor.json', quota)
            check_quota(quota, config['resources']['quota_stop_percent'])
            return ('Continue in this repository and session. Your first shell command must be `cat ' + dispatch_path
                    + '`. Read the complete task and any supplied plan, then follow it. Do not work on other tasks.')

        def _run_evaluation(self, submitted):
            nonlocal previous_memory
            audit = verify_dispatch(events_from(output / 'log/agent_stdout.txt'), session, dispatch_path, task)
            audit.update(input_commit=previous['ending_commit'], milestone_id=self.milestone_id)
            save(output / 'dispatch.json', audit)
            usage = verify_usage(events_from(output / 'log/agent_stdout.txt'), audit['read_item_id'], memory_before)
            if index == 2:
                state = load(output / 'serena_state.json')
                if any(state.get(k) != v for k, v in usage.items()):
                    raise ValueError('Previously verified Serena usage changed')
                verify_memory_boundary(memory_state(self.container_setup), state['after'])
            else:
                previous_memory = preserve_memory(self.container_setup, output, memory_before, usage)
            assert_no_profile_artifacts(submitted)
            started = time.monotonic()
            try:
                return super()._run_evaluation(submitted)
            finally:
                save(output / 'durations.json', {'evaluation': time.monotonic() - started})

    runner = RetainedRunner(workspace_root=workspace, milestone_id=milestones[1],
        srs_path=workspace / 'srs' / milestones[1] / 'SRS.md', output_dir=output,
        image_name=benchmark['skill_runtime_image_id'], agent_name='codex', agent_version=config['codex']['version'],
        model=config['codex']['model'], reasoning_effort=config['codex']['reasoning_effort'],
        timeout_ms=benchmark['timeout_seconds'] * 1000, main_branch=benchmark['main_branch'], keep_container=True,
        runtime_policy_binding=runtime_binding(config, runtime / (chain + '_s01')))
    runner.container_name = runner.container_setup.container_name = runner.agent_runner.container_name = name
    runner.agent_runner.session_id = session
    runner._snapshot_baseline_commit = previous['starting_commit']
    assert_boundary(runner, sidecar['agent_tag_commit'])
    verify_retained_config(runner.container_setup.docker_exec(['cat', '/home/fakeroot/.codex/config.toml']).stdout,
                           (ROOT / 'profiles/serena/config.toml').read_text())
    policy = runner.container_setup.docker_exec(['sha256sum', '/home/fakeroot/.codex/AGENTS.md']).stdout.split()[0]
    if policy != hashlib.sha256((ROOT / 'profiles/serena_continuous/AGENTS.md').read_bytes()).hexdigest():
        raise ValueError('Retained Serena policy changed')
    if runner.agent_runner._framework.extract_session_id_from_container(name) != session:
        raise ValueError('Retained Codex thread changed')
    if task_text((output / 'original_task.txt').read_text()) != task:
        raise ValueError('Recovery prompt differs from frozen continuous delivery')
    runner.container_setup.lock_network()
    if not runner.agent_runner.refresh_container_credentials():
        raise RuntimeError('OAuth refresh failed before recovery')
    if interrupted.exists() and not collected:
        raise ValueError('Repeated recovery needs a new explicit audit')
    if not interrupted.exists():
        save(interrupted, {'observed_at': datetime.now(timezone.utc).isoformat(), 'original_metadata': old,
            'interrupted_stage': 'grader', 'inference_replayed': False,
            'snapshot_sha256': sidecar['snapshot_sha256'],
            'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    original_resume = runner.agent_runner.resume_session
    def timed_resume(*args, **kwargs):
        started = time.monotonic()
        try:
            return original_resume(*args, **kwargs)
        finally:
            save(output / 'execution.json', {'duration_seconds': time.monotonic() - started})
    runner.agent_runner.resume_session = timed_resume
    submissions = {milestones[0]: previous['ending_commit'], milestones[1]: sidecar['agent_tag_commit']}
    if collected:
        verify_memory_boundary(memory_state(runner.container_setup), previous_memory)
        if recovered['sonar'].get('analysis_ok') is not True:
            analyze(recovered)
        previous = recovered
    for index in range(3 if collected else 2, 6):
        output = withheld_output(runtime, chain + '_s' + str(index).zfill(2)) if index > 2 else output
        if index > 2:
            output.mkdir(mode=0o700, exist_ok=False)
        runner.milestone_id = milestones[index - 1]
        runner.srs_path = workspace / 'srs' / runner.milestone_id / 'SRS.md'
        runner.output_dir, runner.log_dir = output, output / 'log'
        runner.log_dir.mkdir(exist_ok=True)
        runner.agent_runner.log_dir = runner.log_dir
        step_config = json.loads(json.dumps(config))
        step_config['benchmark']['smoke_milestone'] = runner.milestone_id
        save(output / 'experiment.json', step_config)
        metadata = old.copy() if index == 2 else {**old, 'step': index, 'started_at': datetime.now(timezone.utc).isoformat()}
        metadata['operational_recovery'] = {**load(interrupted),
            'continuation_adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        save(output / 'run_metadata.json', metadata)
        update_progress(chain, state='running', completed_steps=index - 1, active_step=index,
                        operational_recovery='host restart after step 2 submission; no inference replay')
        started = time.monotonic()
        try:
            save(output / 'quota_before.json' if index > 2 else output / 'quota_recovery.json', read_quota())
            if index == 2:
                result = runner._run_evaluation(snapshot)
            else:
                result = resume_step(runner, session, previous['ending_commit'])
            commit = runner._get_tag_hash('agent-impl-' + runner.milestone_id)
            assert_boundary(runner, commit)
            if runner.container_setup.docker_exec_git('merge-base', '--is-ancestor', previous['ending_commit'], commit).returncode:
                raise ValueError('Submission no longer descends from preceding step')
            if any(runner._get_tag_hash('agent-impl-' + m) != c for m, c in submissions.items()):
                raise ValueError('Previous submission tag moved')
            submissions[runner.milestone_id] = commit
            if load(output / 'evaluation/evaluation_result.json').get('error_message'):
                raise RuntimeError('Grader infrastructure failed')
            metadata.update(state='finished', returncode=0 if result.resolved else 1,
                            duration_seconds=time.monotonic() - started +
                            (load(output / 'execution.json')['duration_seconds'] if index == 2 else 0))
            save(output / 'quota_after.json', read_quota())
            record, _ = preserve_and_collect(runner, output, step_config, metadata,
                previous['usage']['executor_cumulative'], previous['ending_commit'])
            update_progress(chain, state='running', completed_steps=index, active_step=None, last_step=output.name)
            if record['collection_errors']:
                raise RuntimeError('Step collection failed')
            analyze(record)
            previous = record
        except Exception as error:
            if not (ROOT / 'results/trials' / output.name).exists():
                metadata.update(state='failed', failure_category='operational_recovery_failure',
                    error=redact(str(error), credential_values(Path.home() / '.codex/auth.json')),
                    duration_seconds=time.monotonic() - started)
                preserve_and_collect(runner, output, step_config, metadata,
                    previous['usage']['executor_cumulative'], previous['ending_commit'])
            update_progress(chain, state='failed', active_step=None, failure_category='operational_recovery_failure')
            raise
    update_progress(chain, state='finished', completed_steps=5)
    runner.container_setup.cleanup()
    lock.close()


if __name__ == '__main__':
    main()
