"""Continue existing three-edit trajectories through their fourth task only."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from experiment.checkpoint_restore import copy_to, restore_history
from experiment.collect import collect, load, sonar_result
from experiment.continuous import (assert_boundary, check_resources, events_from, preserve_and_collect,
                                   resume_step, runtime_binding, update_progress, verify_dispatch, verify_images)
from experiment.quota import read_quota
from experiment.report import export
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact
from experiment.status import main as refresh_status

MILESTONE = 'milestone_seed_b610d1c_1'
CONFIG = ROOT / 'reports/phase6d_experiment.json'


def publish(record):
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    rows = [record if row['trial_id'] == record['trial_id'] else row for row in rows]
    export(rows, ROOT / 'results')
    save(ROOT / 'reports' / (record['trial_id'] + '.json'), record)


def analyze(record):
    from experiment.sonar_scan import scan
    directory = ROOT / 'results/trials' / record['trial_id']
    output = directory / 'sonar'
    scan(directory, output, ROOT / 'results/sonar/private/credentials.json', 'solution')
    record['sonar'] = sonar_result(directory, record, ROOT / 'results/sonar/common_base')
    record['durations_seconds']['sonar'] = record['sonar'].get('duration_seconds')
    publish(record)
    refresh_status()
    if record['sonar']['analysis_ok'] is not True:
        raise RuntimeError('Fourth-step Sonar failed; further inference withheld')


def prior_rows(parent):
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    result = sorted((row for row in rows if row.get('continuous', {}).get('trajectory_id') ==
                     parent['continuous']['trajectory_id'] and row['trial_state'] == 'finished'
                     and row['continuous']['step'] <= 3), key=lambda row: row['continuous']['step'])
    if [row['continuous']['step'] for row in result] != [1, 2, 3]:
        raise ValueError('Continuation requires exactly three collected parent steps')
    return result


def continue_one(config, checkpoint, chain):
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.profiles import activate_profile
    from experiment.skill_profiles import install_native_skill
    from experiment.skill_trial import assert_no_profile_artifacts

    parent = load(ROOT / 'reports' / (checkpoint['parent_trial'] + '.json'))
    priors = prior_rows(parent)
    if parent['collection_errors'] or parent['ending_commit'] != checkpoint['ending_commit']:
        raise ValueError('Parent source checkpoint changed')
    rollout = Path(checkpoint['rollout_path'])
    if hashlib.sha256(rollout.read_bytes()).hexdigest() != checkpoint['rollout_sha256']:
        raise ValueError('Parent native history changed')
    output = Path(config['resources']['runtime_root']) / (chain + '_s04')
    if output.exists():
        raise ValueError('Existing extension attempt requires explicit recovery')
    output.mkdir(mode=0o700, parents=True)
    step_config = json.loads(json.dumps(config))
    step_config['benchmark']['smoke_milestone'] = MILESTONE
    save(output / 'experiment.json', step_config)
    session = checkpoint['session_id']
    metadata = {'phase': 'trial', 'trial_kind': 'continuous_step', 'measured_comparison': True,
                'state': 'running', 'variant': parent['variant'], 'trajectory_id': chain, 'step': 4,
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
    task_path = '/home/fakeroot/continuous-step-4.txt'
    task = None

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
            assert_no_profile_artifacts(snapshot)
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot)
            finally:
                save(output / 'durations.json', {'evaluation': time.monotonic() - started})

        def _extract_snapshot_from_workdir(self):
            raise RuntimeError('Continuation requires an immutable fourth submission tag')

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
    if parent['variant'] == 'baseline':
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
    runner._snapshot_baseline_commit = parent['starting_commit']
    assert_boundary(runner, parent['ending_commit'])
    for previous in priors:
        if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
            raise ValueError('Restored submission tags differ from parent records')
    if runner._verify_tag_exists():
        raise ValueError('Fourth submission already exists; inference replay forbidden')
    history = restore_history(setup, parent, output)
    if not runner.agent_runner.refresh_container_credentials():
        raise RuntimeError('OAuth refresh failed before continuation')
    runner.agent_runner.session_id = session
    extension = {'parent_trial': parent['trial_id'], 'prefix_trials': [r['trial_id'] for r in priors],
                 'parent_setup_fingerprint': parent['setup_fingerprint'], 'history_restore': history,
                 'new_inference_executed': True, 'replayed_prefix_model_calls': 0}
    proof['extension'] = extension
    save(output / 'effective_profile.json', proof)
    update_progress(chain, state='running', completed_steps=0, active_step=4)
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
            raise ValueError('Fourth submission does not descend from the third')
        for previous in priors:
            if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
                raise ValueError('Previous submission tag moved during extension')
        if parent['variant'] != 'baseline':
            copy_to_path = output / 'hook_audit.jsonl'
            subprocess.run(['docker', 'cp', setup.container_name + ':/home/fakeroot/.codex/skill_hook_audit.jsonl', str(copy_to_path)], check=True, capture_output=True)
            audit = [json.loads(line) for line in copy_to_path.read_text().splitlines()]
            field = 'caveman_mode_context' if parent['variant'] == 'caveman' else 'full_mode_context'
            active = any(row.get(field) for row in audit)
            save(output / 'skill_activation.json', {'variant': parent['variant'], 'native_hook_activation_verified': active, 'audit': audit})
            if not active:
                raise RuntimeError('Restored native profile was not activated')
        raw = load(output / 'evaluation/evaluation_result.json')
        if (raw.get('error_message') or raw.get('infra_invalid')
                or not raw.get('test_summary', {}).get('total')
                or raw.get('residue_prune', {}).get('enabled') is not True):
            raise RuntimeError('Fourth grader infrastructure or pruning policy invalid')
        metadata.update(state='finished', returncode=0 if result.resolved else 1)
    except Exception as caught:
        error = caught
        metadata.update(state='failed', failure_category='continuation_failure',
                        error=redact(str(caught), credential_values(Path.home() / '.codex/auth.json')))
    finally:
        metadata['duration_seconds'] = time.monotonic() - started
        save(output / 'quota_after.json', read_quota())
        # A rollout alone is insufficient for paginated native history: retain its databases too.
        setup.docker_exec(['python3', '-c', '''from pathlib import Path
import sqlite3,hashlib,json
source=Path('/home/fakeroot/.codex'); target=Path('/tmp/phase6d-native-store'); target.mkdir(exist_ok=True)
manifest={}
for name in ('state_5.sqlite','thread_history_1.sqlite'):
 p=source/name
 if not p.exists(): continue
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as before, sqlite3.connect(target/name) as after:
  before.backup(after)
 manifest[name]=hashlib.sha256((target/name).read_bytes()).hexdigest()
assert 'state_5.sqlite' in manifest
(target/'manifest.json').write_text(json.dumps(manifest,indent=2))
'''], user='root')
        subprocess.run(['docker', 'cp', setup.container_name + ':/tmp/phase6d-native-store',
                        str(output / 'native_session_store')], check=True, capture_output=True)
        stores = load(output / 'native_session_store/manifest.json')
        if any(hashlib.sha256((output / 'native_session_store' / name).read_bytes()).hexdigest() != digest
               for name, digest in stores.items()):
            raise ValueError('Native database backup hash mismatch')
        record, _ = preserve_and_collect(runner, output, step_config, metadata,
                                        parent['usage']['executor_cumulative'], parent['ending_commit'])
        record['extension'] = extension
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


def regrade_serena(config, checkpoint, chain):
    old = load(ROOT / 'reports/phase6_serena_r01_s04.json')
    preflight = load(ROOT / 'reports/phase6d_grader_preflight.json')
    if not preflight['ready'] or preflight['snapshot_sha256'] != old['snapshot_sha256']:
        raise ValueError('Exact fourth Serena submission has no valid grader replay')
    output = Path(config['resources']['runtime_root']) / (chain + '_s04')
    if output.exists():
        raise ValueError('Serena regrade output already exists')
    shutil.copytree(Path(old['artifacts_path']), output)
    # Copy diagnostics into a fresh result; never replace the original failed evaluation.
    retained = output / 'original_failed_evaluation'
    (output / 'evaluation').rename(retained)
    shutil.copytree(Path(preflight['result_path']).parent, output / 'evaluation')
    step_config = json.loads(json.dumps(config))
    step_config['benchmark']['smoke_milestone'] = MILESTONE
    step_config['benchmark']['skill_runtime_image_id'] = load(ROOT / 'reports/phase6_experiment.json')['benchmark']['skill_runtime_image_id']
    save(output / 'experiment.json', step_config)
    metadata = load(output / 'run_metadata.json')
    metadata.update(state='finished', failure_category=None, error=None, trajectory_id=chain, step=4,
                    setup_fingerprint=setup_fingerprint(step_config)[0], new_inference_executed=False,
                    duration_seconds=preflight['duration_seconds'],
                    source_implementation_commit=old['implementation_commit'],
                    implementation_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    save(output / 'run_metadata.json', metadata)
    durable = ROOT / 'results/trials' / output.name
    shutil.copytree(output, durable)
    record = collect(durable, step_config)
    record['usage'] = old['usage']
    record['continuous'] = {**old['continuous'], 'trajectory_id': chain}
    record['extension'] = {'parent_trial': checkpoint['parent_trial'],
                           'prefix_trials': [r['trial_id'] for r in prior_rows(load(ROOT / 'reports' / (checkpoint['parent_trial'] + '.json')))],
                           'new_inference_executed': False, 'reused_submission': old['trial_id'],
                           'usage_origin_trial': old['trial_id'], 'replayed_prefix_model_calls': 0}
    record['sonar'] = {**old['sonar'], 'analysis_reused_from': old['trial_id'], 'new_analysis_executed': False}
    record['durations_seconds'].update(executor=None, sonar=None, evaluation=preflight['duration_seconds'])
    if record['snapshot_sha256'] != old['snapshot_sha256'] or record['collection_errors']:
        raise ValueError('Regraded Serena source binding failed')
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    if any(row['trial_id'] == record['trial_id'] for row in rows):
        raise ValueError('Duplicate Serena regrade result')
    export(rows + [record], ROOT / 'results')
    save(ROOT / 'reports' / (record['trial_id'] + '.json'), record)
    update_progress(chain, state='finished', completed_steps=1, active_step=None, last_step=record['trial_id'])
    print('REGRADED', record['trial_id'], 'new_model_calls=0', flush=True)


def main():
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = load(CONFIG)
    validate(config)
    verify_images(config)
    if not load(ROOT / 'reports/phase6d_grader_preflight.json')['ready']:
        raise ValueError('Fourth grader preflight is not ready')
    os.environ['SWE_MILESTONE_RESIDUE_PRUNE'] = '1'
    checkpoints = load(ROOT / 'reports/phase6d_checkpoints.json')['entries']
    checkpoints.sort(key=lambda row: (row['variant'] != 'serena', row['repetition'], ['baseline', 'caveman', 'ponytail', 'serena'].index(row['variant'])))
    lock = trial_lock(Path(config['resources']['runtime_root']))
    try:
        for checkpoint in checkpoints:
            chain = f"phase6d_{checkpoint['variant']}_r{checkpoint['repetition']:02d}"
            plan = load(ROOT / 'reports/continuous_feasibility.json')
            progress = next(row for row in plan['pilot_runs'] if row['trial_id'] == chain)
            if progress['state'] == 'finished':
                continue
            if progress['state'] != 'planned':
                raise ValueError('Interrupted continuation requires explicit recovery')
            check_resources(config)
            if checkpoint['variant'] != 'serena':
                check_quota(read_quota(), config['resources']['quota_stop_percent'])
            print('START', chain, flush=True)
            try:
                if checkpoint['variant'] == 'serena':
                    regrade_serena(config, checkpoint, chain)
                else:
                    continue_one(config, checkpoint, chain)
            except Exception as error:
                output = Path(config['resources']['runtime_root']) / (chain + '_s04')
                metadata = load(output / 'run_metadata.json', {})
                if metadata.get('state') == 'running':
                    metadata.update(state='failed', failure_category='continuation_failure',
                                    error=redact(str(error), credential_values(Path.home() / '.codex/auth.json')))
                    save(output / 'run_metadata.json', metadata)
                update_progress(chain, state='failed', active_step=None, failure_category='continuation_failure')
                raise
            print('DONE', chain, flush=True)
    finally:
        lock.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
