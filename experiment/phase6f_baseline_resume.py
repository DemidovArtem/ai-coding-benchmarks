"""Resume the exact retained baseline sixth task after its recorded quota refusal."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from experiment.checkpoint_restore import copy_to
from experiment.checkpoint_restore import read_turns
from experiment.continuous_resume import verify_retained_config
from experiment.phase6f import prefix_rows, grading_state
from experiment.session_store import backup_stores
from experiment.serena_continuous import install_policy, memory_state, preserve_memory, verify_memory_boundary, verify_usage
from experiment.phase6d import analyze, publish
from experiment.collect import collect, load, sonar_result
from experiment.continuous import (assert_boundary, check_resources, events_from, preserve_and_collect,
                                   resume_step, runtime_binding, update_progress, verify_dispatch, verify_images)
from experiment.quota import read_quota
from experiment.report import export
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact
from experiment.status import main as refresh_status

MILESTONE = 'milestone_seed_a6e0be3_1_sub-01'
CONFIG = ROOT / 'reports/phase6f_experiment.json'



def validate_failure(failed, events):
    if (failed['trial_state'] != 'failed' or failed.get('ending_commit')
            or failed['variant'] != 'baseline' or failed['repetition'] != 2
            or failed['continuous']['step'] != 6 or failed['failure_category'] != 'quota_pressure'):
        raise ValueError('Recovery requires the retained baseline sixth quota stop')
    if (not any(e.get('type') == 'turn.failed' and 'usage limit' in str(e).lower() for e in events)
            or any(e.get('type') == 'turn.completed' for e in events)):
        raise ValueError('A quota failure without a completed sixth turn is required')


def work_state(setup):
    head = setup.docker_exec_git('rev-parse', 'HEAD').stdout.strip()
    unstaged = setup.docker_exec_git('diff', '--binary', '--full-index').stdout
    staged = setup.docker_exec_git('diff', '--cached', '--binary', '--full-index').stdout
    untracked = setup.docker_exec_git('ls-files', '--others', '--exclude-standard').stdout
    if untracked:
        raise ValueError('Recovery is limited to the verified tracked baseline changes')
    return {'head': head, 'unstaged_sha256': hashlib.sha256(unstaged.encode()).hexdigest(),
            'staged_sha256': hashlib.sha256(staged.encode()).hexdigest(), 'untracked_files': []}


def resume_retained_step(runner, session, expected_work):
    if work_state(runner.container_setup) != expected_work:
        raise ValueError('Retained work changed before recovery dispatch')
    prompt = runner._load_prompt()
    runner.container_setup.prepare_agent_invocation()
    if not runner.agent_runner.resume_session(session, prompt):
        raise RuntimeError('Continuous executor resume failed; next step is withheld')
    if runner.agent_runner.session_id != session or not runner._verify_tag_exists():
        raise RuntimeError('Recovered executor must preserve session and submit this step')
    commit = runner._get_tag_hash('agent-impl-' + runner.milestone_id)
    snapshot = runner._extract_snapshot(expected_tag_hash=commit)
    runner._extract_and_parse_logs()
    return runner._run_evaluation(snapshot)


def recover(config):
    chain = 'phase6f_baseline_r02'
    blocked = ROOT / 'results/trials/phase6f_baseline_r02_s06'
    failed = load(ROOT / 'reports/phase6f_baseline_r02_s06.json')
    validate_failure(failed, events_from(blocked / 'log/agent_stdout.txt'))
    checkpoint = next(r for r in load(ROOT / 'reports/phase6f_checkpoints.json')['entries']
                      if r['variant'] == 'baseline' and r['repetition'] == 2)
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.profiles import activate_profile
    from experiment.skill_profiles import install_native_skill, install_serena
    from experiment.skill_trial import assert_no_profile_artifacts

    parent = load(ROOT / 'reports' / (checkpoint['parent_trial'] + '.json'))
    priors = prefix_rows(parent, checkpoint)
    rollout = Path(checkpoint['rollout_path'])
    if hashlib.sha256(rollout.read_bytes()).hexdigest() != checkpoint['rollout_sha256']:
        raise ValueError('Parent native history changed')
    config = json.loads(json.dumps(config))
    config['benchmark']['skill_runtime_image_id'] = checkpoint['image_id']
    output = Path(config['resources']['runtime_root']) / (chain + '_s06_resume01')
    if output.exists():
        raise ValueError('Existing extension attempt requires explicit recovery')
    output.mkdir(mode=0o700, parents=True)
    step_config = json.loads(json.dumps(config))
    step_config['benchmark']['smoke_milestone'] = MILESTONE
    save(output / 'experiment.json', step_config)
    session = checkpoint['session_id']
    metadata = {'phase': 'trial', 'trial_kind': 'continuous_step', 'measured_comparison': True,
                'state': 'running', 'variant': parent['variant'], 'trajectory_id': chain, 'step': 6,
                'repetition': parent['repetition'], 'model': config['codex']['model'],
                'reasoning_effort': config['codex']['reasoning_effort'],
                'started_at': datetime.now(timezone.utc).isoformat(), 'executor_session_id': session,
                'setup_fingerprint': setup_fingerprint(config)[0],
                'resume': {'attempt_of': failed['trial_id'], 'same_session_required': session,
                           'original_failure_preserved': str(blocked),
                           'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    save(output / 'run_metadata.json', metadata)
    save(output / 'quota_before.json', read_quota())
    check_quota(load(output / 'quota_before.json'), config['resources']['quota_stop_percent'])
    binding = runtime_binding(config, output)
    workspace = ROOT / config['benchmark']['dataset_root'] / config['benchmark']['repo']
    task_path = '/home/fakeroot/continuous-step-6.txt'
    task = None
    memory_before = None

    class ExtensionRunner(MilestoneRunner):
        def _load_prompt(self):
            nonlocal task
            original = super()._load_prompt()
            (output / 'original_task.txt').write_text(original)
            task = original + ('\n\nThis is one step of a sequential pilot. Preserve prior work and submission tags. '
                              'Implement only this task. After committing and tagging this step, stop and await the next user turn.\n')
            if parent['variant'] == 'serena':
                task += ('\nSerena memory mode: warm; read and reuse a memory retained from the previous task. Do not repeat onboarding.'
                         '\nAfter the required first task-file read, follow the Serena continuous startup policy.\n')
            local = output / 'dispatched_task.txt'
            local.write_text(task)
            self.container_setup.verify_network_lockdown()
            quota = read_quota()
            save(output / 'quota_before_executor.json', quota)
            check_quota(quota, config['resources']['quota_stop_percent'])
            copy_to(self.container_name, local, task_path)
            self.container_setup.docker_exec(['chown', 'root:root', task_path], user='root')
            self.container_setup.docker_exec(['chmod', '0444', task_path], user='root')
            return ('Continue in this repository and session. Your first shell command must be `cat ' + task_path
                    + '`. Read the complete task and any supplied plan, then follow it. Do not work on other tasks.')

        def _run_evaluation(self, snapshot):
            audit = verify_dispatch(events_from(output / 'log/agent_stdout.txt'), session, task_path, task)
            audit.update(input_commit=parent['ending_commit'], milestone_id=MILESTONE)
            save(output / 'dispatch.json', audit)
            if parent['variant'] == 'serena':
                usage = verify_usage(events_from(output / 'log/agent_stdout.txt'), audit['read_item_id'], memory_before)
                preserve_memory(self.container_setup, output, memory_before, usage)
            assert_no_profile_artifacts(snapshot)
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot)
            finally:
                save(output / 'durations.json', {'evaluation': time.monotonic() - started})

        def _extract_snapshot_from_workdir(self):
            raise RuntimeError('Continuation requires an immutable sixth submission tag')

    runner = ExtensionRunner(workspace_root=workspace, milestone_id=MILESTONE,
        srs_path=workspace / 'srs' / MILESTONE / 'SRS.md', output_dir=output,
        image_name=config['benchmark']['skill_runtime_image_id'], agent_name='codex',
        agent_version=config['codex']['version'], model=config['codex']['model'],
        reasoning_effort=config['codex']['reasoning_effort'],
        timeout_ms=config['benchmark']['timeout_seconds'] * 1000,
        main_branch=config['benchmark']['main_branch'], keep_container=True,
        trial_name=chain, runtime_policy_binding=binding)
    setup = runner.container_setup
    name = MILESTONE + '-' + chain + '-runner'
    runner.container_name = setup.container_name = runner.agent_runner.container_name = name
    info = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
    if info['Image'] != checkpoint['image_id']:
        raise ValueError('Retained runtime image differs')
    if {m['Destination'] for m in info['Mounts']} != {'/tmp/host-codex/auth.json'} or any(m['RW'] for m in info['Mounts']):
        raise ValueError('Retained mounts differ')
    if not info['State']['Running']:
        subprocess.run(['docker', 'start', name], check=True, capture_output=True)
    if any(p.strip() in ('codex', 'codex-linux-x64') for p in setup.docker_exec(['ps', '-eo', 'comm']).stdout.splitlines()):
        raise ValueError('An executor is already running')
    expected = load(ROOT / 'reports/phase6f_baseline_resume_preflight.json')['retained_work']
    if work_state(setup) != expected or expected['head'] != parent['ending_commit']:
        raise ValueError('Retained partial sixth source changed')
    runner._snapshot_baseline_commit = parent['starting_commit']
    runner.agent_runner.session_id = session
    for previous in priors:
        if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
            raise ValueError('A prior submission tag moved')
    if runner._verify_tag_exists():
        raise ValueError('Sixth submission already exists; inference replay forbidden')
    verify_retained_config(setup.docker_exec(['cat', '/home/fakeroot/.codex/config.toml']).stdout,
                           (ROOT / 'profiles/baseline/config.toml').read_text())
    proof = load(blocked / 'effective_profile.json')
    history = read_turns(name, session)
    turns = history.get('result', {}).get('data', [])
    old = failed['extension']['history_restore']['native_turns']
    if (history.get('error') or history.get('result', {}).get('nextCursor')
            or [{'id':t['id'], 'status':t['status']} for t in turns[:-1]] != old
            or len(turns) != len(old) + 1 or turns[-1]['status'] not in ('failed', 'interrupted')):
        raise ValueError('Retained history must contain the retained measured turns and quota failure')
    save(output / 'native_history_before.json', history)
    setup.verify_network_lockdown()
    if not runner.agent_runner.refresh_container_credentials():
        raise RuntimeError('OAuth refresh failed before recovery')
    extension = {**failed['extension'], 'recovery_of': failed['trial_id'], 'failed_turn_preserved': turns[-1]['id'],
                 'history_reimported': False, 'partial_work_preserved': expected,
                 'recovery_adapter_sha256': metadata['resume']['adapter_sha256']}
    proof['extension'] = extension
    save(output / 'effective_profile.json', proof)
    update_progress(chain, state='running', completed_steps=0, active_step=6, failure_category=None, resumed_attempt=output.name)
    started = time.monotonic()
    original_resume = runner.agent_runner.resume_session
    def timed_resume(*args, **kwargs):
        before = time.monotonic()
        try:
            return original_resume(*args, **kwargs)
        finally:
            save(output / 'execution.json', {'duration_seconds': time.monotonic() - before})
    runner.agent_runner.resume_session = timed_resume
    error = None
    try:
        result = resume_retained_step(runner, session, expected)
        commit = runner._get_tag_hash('agent-impl-' + MILESTONE)
        assert_boundary(runner, commit)
        if setup.docker_exec_git('merge-base', '--is-ancestor', parent['ending_commit'], commit).returncode:
            raise ValueError('Sixth submission does not descend from the fifth')
        for previous in priors:
            if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
                raise ValueError('Previous submission tag moved during extension')
        raw = load(output / 'evaluation/evaluation_result.json')
        grading = grading_state(raw)
        save(output / 'grading_state.json', grading)
        metadata.update(state='finished', returncode=0 if result.resolved else 1)
    except Exception as caught:
        error = caught
        metadata.update(state='failed', failure_category='quota_pressure' if runner.agent_runner._last_rate_limit else 'continuation_failure',
                        error=redact(str(caught), credential_values(Path.home() / '.codex/auth.json')))
    finally:
        metadata['duration_seconds'] = time.monotonic() - started
        save(output / 'quota_after.json', read_quota())
        # Hash only closed backup files; never reuse a prior attempt's destination.
        copy_to(setup.container_name, ROOT / 'experiment/session_store.py', '/tmp/phase6f_session_store.py')
        setup.docker_exec(['python3', '/tmp/phase6f_session_store.py', '/home/fakeroot/.codex',
                           '/tmp/phase6f-baseline-resume01-native-store'], user='root')
        subprocess.run(['docker', 'cp', setup.container_name + ':/tmp/phase6f-baseline-resume01-native-store',
                        str(output / 'native_session_store')], check=True, capture_output=True)
        stores = load(output / 'native_session_store/manifest.json')
        if any(hashlib.sha256((output / 'native_session_store' / name).read_bytes()).hexdigest() != digest
               for name, digest in stores.items()):
            raise ValueError('Native database backup hash mismatch')
        record, _ = preserve_and_collect(runner, output, step_config, metadata,
                                        parent['usage']['executor_cumulative'], parent['ending_commit'])
        record['extension'] = extension
        record['grading_state'] = load(output / 'grading_state.json', {'valid':False,'reason':'execution_failure'})
        publish(record)
        update_progress(chain, state='failed' if error else 'running', completed_steps=0,
                        active_step=None, last_step=output.name, failure_category=metadata.get('failure_category'))
    if error:
        raise error
    if record['collection_errors']:
        raise RuntimeError('Continuation collection failed; further inference withheld')
    analyze(record)
    update_progress(chain, state='finished', completed_steps=1)
    durable = ROOT / 'results/trials' / record['trial_id']
    if any(hashlib.sha256((durable / 'native_session_store' / name).read_bytes()).hexdigest() != digest
           for name, digest in stores.items()):
        raise ValueError('Durable native database backup hash mismatch; retain container')
    setup.cleanup()
    print('STEP_COLLECTED', record['trial_id'], 'resolved=', record['resolved'], 'sonar=', True, flush=True)



def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = load(CONFIG)
    validate(config)
    adapter = load(ROOT / 'reports/phase6f_baseline_resume_preflight.json')['adapter_sha256']
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != adapter:
        raise ValueError('Recovery adapter changed after preflight')
    verify_images(config)
    check_resources(config)
    check_quota(read_quota(), config['resources']['quota_stop_percent'])
    os.environ['SWE_MILESTONE_RESIDUE_PRUNE'] = '1'
    lock = trial_lock(Path(config['resources']['runtime_root']))
    try:
        recover(config)
        from experiment.phase6f_report import main as report
        report()
        subprocess.run([sys.executable, str(ROOT / 'reports/plots/export_patches.py')], check=True)
        subprocess.run(['/tmp/ai-coding-charts/bin/python', str(ROOT / 'reports/plots/mean_curves.py'), '--refresh-data'],
                       check=True, env={**os.environ, 'MPLCONFIGDIR':'/tmp/ai-coding-charts/mpl'})
    finally:
        lock.close()
    from experiment.phase6f import main as remaining
    remaining()


if __name__ == '__main__':
    main()
