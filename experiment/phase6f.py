"""Continue the exact original SWE sixth task, preserving all five measured edits."""

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
from experiment.phase6e import restore_history
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



def grading_state(raw):
    error = raw.get('error_message')
    if (error or raw.get('infra_invalid') or not raw.get('test_summary', {}).get('total')
            or raw.get('residue_prune', {}).get('enabled') is not True):
        raise RuntimeError('Sixth grader infrastructure failure: ' + str(error or 'missing valid test reports')[:400])
    return {'valid': True, 'raw_score_preserved': True}


def prefix_rows(parent, checkpoint):
    priors = [load(ROOT / 'reports' / (name + '.json')) for name in parent['extension']['prefix_trials']] + [parent]
    if [r['continuous']['step'] for r in priors] != [1, 2, 3, 4, 5]:
        raise ValueError('Exactly five measured prefix steps are required')
    if (parent['trial_state'] != 'finished' or parent['collection_errors']
            or parent['sonar'].get('analysis_ok') is not True
            or parent['ending_commit'] != checkpoint['ending_commit']):
        raise ValueError('Parent source checkpoint is incomplete or changed')
    for row in priors:
        if (row['variant'] != checkpoint['variant'] or row['repetition'] != checkpoint['repetition']
                or row['continuous']['executor_session_id'] != checkpoint['session_id']):
            raise ValueError('Prefix source/session belongs to another trajectory')
    return priors


def continue_one(config, checkpoint, chain):
    from harness.e2e.agents.codex import CodexFramework
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
    output = Path(config['resources']['runtime_root']) / (chain + '_s06')
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
                'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    save(output / 'run_metadata.json', metadata)
    save(output / 'quota_before.json', read_quota())
    check_quota(load(output / 'quota_before.json'), config['resources']['quota_stop_percent'])
    binding = runtime_binding(config, output)
    workspace = ROOT / config['benchmark']['dataset_root'] / config['benchmark']['repo']
    task_path = '/home/fakeroot/continuous-step-6.txt'
    task = None
    memory_before = None

    class Hooks(CodexFramework):
        def build_resume_command(self, *args, **kwargs):
            return super().build_resume_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

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
    setup.start_container()
    setup.lock_network()
    if parent['variant'] == 'serena':
        proof = install_serena(setup, output, config)
        proof['continuous_policy_sha256'] = install_policy(setup)
    elif parent['variant'] == 'baseline':
        proof = activate_profile(setup, output, config)
    else:
        proof = install_native_skill(setup, output, config, parent['variant'])
        runner.agent_runner._framework = Hooks(reasoning_effort=config['codex']['reasoning_effort'])
    copy_to(setup.container_name, Path(parent['artifacts_path']) / 'repository.bundle', '/tmp/continuation-parent.bundle')
    setup.docker_exec(['chmod', '0444', '/tmp/continuation-parent.bundle'], user='root')
    setup.docker_exec_git('fetch', '--update-head-ok', '/tmp/continuation-parent.bundle', '+refs/*:refs/*')
    setup.docker_exec_git('checkout', '--detach', parent['ending_commit'])
    setup.docker_exec_git('reset', '--hard', parent['ending_commit'])
    setup.docker_exec_git('clean', '-ffd')
    if parent['variant'] == 'serena':
        # Restore only this trajectory's verified textual memories, never another repeat's state.
        setup.docker_exec(['mkdir', '-p', '/testbed/.serena'], user='root')
        copy_to(setup.container_name, Path(parent['artifacts_path']) / 'serena_memories', '/testbed/.serena/memories')
        setup.docker_exec(['chown', '-R', 'fakeroot:fakeroot', '/testbed/.serena'], user='root')
        memory_before = memory_state(setup)
        verify_memory_boundary(memory_before, parent['skill_state']['after'])
        save(output / 'serena_memory_before.json', memory_before)
        proof.update(memory_files_before=memory_before['count'], memory_bytes_before=memory_before['bytes'],
                     memory_policy='warm memories restored from exact fifth checkpoint')
    runner._snapshot_baseline_commit = parent['starting_commit']
    assert_boundary(runner, parent['ending_commit'])
    for previous in priors:
        if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
            raise ValueError('Restored submission tags differ from parent records')
    if runner._verify_tag_exists():
        raise ValueError('Sixth submission already exists; inference replay forbidden')
    history = restore_history(setup, parent, output)
    save(output / 'effective_profile.json', proof)
    if not runner.agent_runner.refresh_container_credentials():
        raise RuntimeError('OAuth refresh failed before continuation')
    runner.agent_runner.session_id = session
    extension = {'parent_trial': parent['trial_id'], 'prefix_trials': [r['trial_id'] for r in priors],
                 'parent_setup_fingerprint': parent['setup_fingerprint'], 'history_restore': history,
                 'new_inference_executed': True, 'replayed_prefix_model_calls': 0}
    proof['extension'] = extension
    save(output / 'effective_profile.json', proof)
    update_progress(chain, state='running', completed_steps=0, active_step=6)
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
        result = resume_step(runner, session, parent['ending_commit'])
        commit = runner._get_tag_hash('agent-impl-' + MILESTONE)
        assert_boundary(runner, commit)
        if setup.docker_exec_git('merge-base', '--is-ancestor', parent['ending_commit'], commit).returncode:
            raise ValueError('Sixth submission does not descend from the fifth')
        for previous in priors:
            if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
                raise ValueError('Previous submission tag moved during extension')
        if parent['variant'] in ('caveman', 'ponytail'):
            copy_to_path = output / 'hook_audit.jsonl'
            subprocess.run(['docker', 'cp', setup.container_name + ':/home/fakeroot/.codex/skill_hook_audit.jsonl', str(copy_to_path)], check=True, capture_output=True)
            audit = [json.loads(line) for line in copy_to_path.read_text().splitlines()]
            field = 'caveman_mode_context' if parent['variant'] == 'caveman' else 'full_mode_context'
            active = any(row.get(field) for row in audit)
            save(output / 'skill_activation.json', {'variant': parent['variant'], 'native_hook_activation_verified': active, 'audit': audit})
            if not active:
                raise RuntimeError('Restored native profile was not activated')
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
                           '/tmp/phase6f-native-store'], user='root')
        subprocess.run(['docker', 'cp', setup.container_name + ':/tmp/phase6f-native-store',
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
    sys.path.insert(0,str(ROOT/'vendor/SWE-Milestone'))
    config=load(CONFIG)
    validate(config)
    if load(ROOT/'reports/phase6f_image_budget.json').get('download_authorized') is not True:
        raise RuntimeError('Sixth grader image download approval is required')
    verify_images(config)
    os.environ['SWE_MILESTONE_RESIDUE_PRUNE']='1'
    checkpoints=load(ROOT/'reports/phase6f_checkpoints.json')['entries']
    lock=trial_lock(Path(config['resources']['runtime_root']))
    try:
        for checkpoint in checkpoints:
            chain=f"phase6f_{checkpoint['variant']}_r{checkpoint['repetition']:02d}"
            plan=load(ROOT/'reports/continuous_feasibility.json')
            progress=next(r for r in plan['pilot_runs'] if r['trial_id']==chain)
            if progress['state']=='finished':continue
            if progress['state']!='planned':raise ValueError('Interrupted sixth step requires explicit recovery')
            check_resources(config)
            check_quota(read_quota(),config['resources']['quota_stop_percent'])
            print('START',chain,flush=True)
            update_progress(chain,state='running',active_step=6,completed_steps=0)
            try:continue_one(config,checkpoint,chain)
            except Exception as error:
                output=Path(config['resources']['runtime_root'])/(chain+'_s06')
                metadata=load(output/'run_metadata.json',{})
                if metadata.get('state')=='running':
                    metadata.update(state='failed',failure_category='continuation_failure',
                                    error=redact(str(error),credential_values(Path.home()/'.codex/auth.json')))
                    save(output/'run_metadata.json',metadata)
                update_progress(chain,state='failed',active_step=None,failure_category='continuation_failure')
                raise
            print('DONE',chain,flush=True)
            from experiment.phase6f_report import main as report
            report()
            subprocess.run([sys.executable,str(ROOT/'reports/plots/export_patches.py')],check=True)
            plotting=Path('/tmp/ai-coding-charts/bin/python')
            if plotting.exists():
                subprocess.run([str(plotting),str(ROOT/'reports/plots/mean_curves.py'),'--refresh-data'],
                               check=True,env={**os.environ,'MPLCONFIGDIR':'/tmp/ai-coding-charts/mpl'})
    finally:lock.close()


if __name__=='__main__':main()
