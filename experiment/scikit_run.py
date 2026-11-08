"""Run one new-cohort step, then preserve a restorable source/session checkpoint."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

from experiment.audit import PAID_KEYS
from experiment.checkpoint_restore import copy_to
from experiment.collect import load
from experiment.continuous import assert_boundary, check_resources, events_from, verify_dispatch
from experiment.phase6e import restore_history
from experiment.python_sonar import scan
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock
from experiment.scikit import CONFIG, PREPARED, WORKSPACE
from experiment.scikit_collect import collect, metrics_repository, publish
from experiment.scikit_profiles import install
from experiment.security import credential_values, redact, redact_artifacts
from experiment.serena_continuous import memory_state, preserve_memory, verify_memory_boundary, verify_usage
from experiment.session_store import backup_stores
from experiment.skill_trial import assert_no_profile_artifacts
from experiment.status import main as refresh_status


def schedule():
    return [(repetition, step, variant) for repetition in (1, 2) for step in range(1, 7)
            for variant in ('baseline', 'caveman', 'ponytail', 'serena')]


def trial_id(variant, repetition, step):
    return f'scikit_{variant}_r{repetition:02d}_s{step:02d}'


def require_ready(config, milestone):
    if config.get('stage') != 'scikit_frozen' or config.get('measurement_started') is not True:
        raise ValueError('Freeze the new cohort before model execution')
    if any(os.environ.get(k) for k in (*PAID_KEYS, 'OPENAI_BASE_URL', 'UNIFIED_BASE_URL')):
        raise ValueError('Only the retained ChatGPT OAuth route is authorized')
    for name, expected in config['pins']['file_sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen cohort input changed: ' + name)
    for name, expected in config['pins'].get('git_commits', {}).items():
        if subprocess.check_output(['git', '-C', str(ROOT / name), 'rev-parse', 'HEAD'], text=True).strip() != expected:
            raise ValueError('Frozen source checkout changed: ' + name)
    image = config['benchmark']['skill_runtime_image_id']
    runtime = load(ROOT / 'profiles/scikit_runtime/manifest.json')
    if runtime.get('image_id') != image or runtime.get('python_lsp_verified') is not True:
        raise ValueError('Python semantic runtime is unverified')
    if not load(ROOT / 'reports/scikit_grader_preflight.json').get('valid'):
        raise ValueError('Original grader preflight is missing')
    if not load(ROOT / 'results/scikit_preflight/python_sonar_base_attempt02/sonar.json').get('analysis_ok'):
        raise ValueError('Python common-base Sonar is missing')
    hooks = load(ROOT / 'reports/scikit_hook_preflight.json')
    if any(not hooks[v].get('hook_command_activation_verified') or hooks[v]['image_id'] != image
           for v in ('caveman', 'ponytail')):
        raise ValueError('Hook-command preflight is missing')
    budget = load(ROOT / 'reports/second_repository_preflight.json')
    grader = next(r for r in budget['images'] if r['milestone'] == milestone)
    inspected = json.loads(subprocess.check_output(['docker', 'image', 'inspect', grader['local']], text=True))[0]
    if grader['digest_ref'] not in inspected.get('RepoDigests', []):
        raise ValueError('Current-task grader digest is not verified; acquire it before inference')
    check_resources(config)


def progress(chain, **changes):
    path = ROOT / 'reports/continuous_feasibility.json'
    plan = load(path)
    row = next(r for r in plan['pilot_runs'] if r['trial_id'] == chain)
    row.update(changes)
    cohort = plan['cohorts']['scikit_replication']
    complete = sum(r['completed_steps'] for r in plan['pilot_runs'] if r['trial_id'].startswith('scikit_'))
    stopped = changes.get('state') == 'failed'
    cohort.update(status='stopped' if stopped else 'running' if changes.get('state') == 'running' else 'ready',
                  label=('Stopped; ' if stopped else '') + f'{complete}/48 measured steps collected',
                  summary=f'{complete}/48 steps; serial step-first order, four configurations, two cold repetitions. '
                          'Python Sonar excludes Cython; common-base M06 grading has 78 missing P2P tests. '
                          'Source, native session and Serena memories checkpointed per trajectory.')
    save(path, plan)
    refresh_status()


def restore_source(setup, config, parent):
    copy_to(setup.container_name, PREPARED / 'repository.bundle', '/tmp/scikit-common.bundle')
    # This is a new disposable container. Remove its original future-bearing Git history.
    setup.docker_exec(['rm', '-rf', '/testbed/.git'], user='root')
    setup.docker_exec_git('init', '-q')
    setup.docker_exec_git('fetch', '-q', '/tmp/scikit-common.bundle', '+refs/*:refs/*')
    setup.docker_exec_git('tag', '-d', 'agent-impl-M06')
    commit = config['benchmark']['common_starting_commit']
    if parent:
        copy_to(setup.container_name, Path(parent['artifacts_path']) / 'repository.bundle', '/tmp/scikit-parent.bundle')
        setup.docker_exec_git('fetch', '-q', '/tmp/scikit-parent.bundle', '+refs/*:refs/*')
        commit = parent['ending_commit']
    setup.docker_exec_git('checkout', '-B', 'main', commit)
    setup.docker_exec_git('reset', '--hard', commit)
    setup.docker_exec_git('clean', '-ffd')
    return commit


def checkpoint(runner, output, config):
    runner.agent_runner.extract_trace(output / 'log')
    base = config['benchmark']['common_starting_commit']
    current = runner.container_setup.docker_exec_git('rev-parse', 'HEAD').stdout.strip()
    previous = load(output / 'run_metadata.json')['input_commit']
    for name, start in (('cumulative.patch', base), ('incremental.patch', previous)):
        patch = subprocess.check_output(['docker', 'exec', '-w', '/testbed', runner.container_name,
                    'git', '-c', 'safe.directory=/testbed', 'diff', '--binary', '--full-index', start, current, '--'])
        (output / name).write_bytes(patch)
    runner.container_setup.docker_exec_git('bundle', 'create', '/tmp/scikit-step.bundle', '--all', 'HEAD', '^' + base)
    copy_source = runner.container_name + ':/tmp/scikit-step.bundle'
    subprocess.run(['docker', 'cp', copy_source, str(output / 'repository.bundle')], check=True, capture_output=True)
    raw = output / 'native_store_raw'
    raw.mkdir()
    for db in ('state_5.sqlite', 'thread_history_1.sqlite'):
        for suffix in ('', '-wal', '-shm'):
            name = db + suffix
            source = '/home/fakeroot/.codex/' + name
            if runner.container_setup.docker_exec(['test', '-f', source], check=False).returncode == 0:
                subprocess.run(['docker', 'cp', runner.container_name + ':' + source, str(raw / name)],
                               check=True, capture_output=True)
    backup_stores(raw, output / 'native_session_store')
    repo = metrics_repository(output)
    subprocess.run(['git', '-C', str(repo), 'fsck', '--full'], check=True, capture_output=True)
    save(output / 'checkpoint.json', {'common_base_bundle_required': str((PREPARED / 'repository.bundle').relative_to(ROOT)),
         'common_base_bundle_sha256': hashlib.sha256((PREPARED / 'repository.bundle').read_bytes()).hexdigest(),
         'step_bundle_sha256': hashlib.sha256((output / 'repository.bundle').read_bytes()).hexdigest(),
         'native_session_store_verified': True, 'source_bundle_fsck_verified': True})
    shutil.rmtree(raw)


def compact(run):
    """Discard only verified copies created by this step; retain grader evidence compressed."""
    artifacts = run / 'evaluation/artifacts'
    if artifacts.exists():
        expected = {str(p.relative_to(artifacts)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in artifacts.rglob('*') if p.is_file()}
        target = run / 'evaluation/grader_artifacts.tar.gz'
        with tarfile.open(target, 'w:gz', compresslevel=1) as archive:
            archive.add(artifacts, arcname='artifacts')
        with tarfile.open(target) as archive:
            actual = {str(Path(m.name).relative_to('artifacts')): hashlib.sha256(archive.extractfile(m).read()).hexdigest()
                      for m in archive if m.isfile()}
        if actual != expected:
            raise ValueError('Grader archive differs from original evidence')
        save(run / 'evaluation/grader_artifacts_manifest.json', expected)
        shutil.rmtree(artifacts)
    for temporary in (run / 'metrics_repository', run / 'sonar/source', run / 'sonar/scanner_work'):
        if temporary.exists():
            shutil.rmtree(temporary)


def run_one(config, variant, repetition, step):
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.run_milestone import MilestoneRunner

    milestone = config['benchmark']['milestones'][step - 1]
    require_ready(config, milestone)
    name = trial_id(variant, repetition, step)
    output = ROOT / 'results/trials' / name
    if output.exists() or (ROOT / 'reports' / (name + '.json')).exists():
        raise ValueError('Existing attempt needs explicit recovery; never replay it')
    parent = load(ROOT / 'reports' / (trial_id(variant, repetition, step - 1) + '.json')) if step > 1 else None
    if step > 1 and (not parent or parent['trial_state'] != 'finished' or parent['collection_errors']):
        raise ValueError('Exact previous step is not complete')
    if parent and (parent['variant'] != variant or parent['repetition'] != repetition
                   or parent['repo'] != config['benchmark']['repo']):
        raise ValueError('Parent belongs to a different trajectory')
    output.mkdir(parents=True, mode=0o700)
    task_path = f'/home/fakeroot/scikit-task-{step:02d}.txt'
    task = None
    session = parent['continuous']['executor_session_id'] if parent else None
    memory_before = None
    chain = f'scikit_{variant}_r{repetition:02d}'
    metadata = {'phase': 'trial', 'trial_kind': 'continuous_step', 'measured_comparison': True,
        'state': 'running', 'variant': variant, 'repetition': repetition, 'step': step, 'trajectory_id': chain,
        'executor_session_id': session, 'model': config['codex']['model'], 'reasoning_effort': 'high',
        'setup_fingerprint': setup_fingerprint(config)[0], 'started_at': datetime.now(timezone.utc).isoformat(),
        'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    save(output / 'run_metadata.json', metadata); save(output / 'experiment.json', config)

    class Hooks(CodexFramework):
        def build_run_command(self, *args, **kwargs):
            return super().build_run_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'
        def build_resume_command(self, *args, **kwargs):
            return super().build_resume_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

    class StepRunner(MilestoneRunner):
        def _load_prompt(self):
            nonlocal task
            task = super()._load_prompt() + ('\n\nImplement only this sequential task. Preserve all previous work and submission tags. '
                                             'Commit and tag the supplied milestone, then stop.\n')
            if variant == 'serena':
                task += ('\nSerena memory mode: warm; reuse retained memories, without onboarding.\n' if parent
                         else '\nSerena memory mode: cold; perform onboarding and save task orientation.\n')
            (output / 'dispatched_task.txt').write_text(task)
            copy_to(self.container_name, output / 'dispatched_task.txt', task_path)
            self.container_setup.docker_exec(['chown', 'root:root', task_path], user='root')
            self.container_setup.docker_exec(['chmod', '0444', task_path], user='root')
            self.container_setup.verify_network_lockdown()
            return f'Your first shell command must be `cat {task_path}`. Read the complete task, then follow it. Implement only this task.'

    runner = StepRunner(workspace_root=WORKSPACE, milestone_id=milestone, srs_path=WORKSPACE / 'srs' / milestone / 'SRS.md',
        output_dir=output, image_name=config['benchmark']['skill_runtime_image_id'], model=config['codex']['model'],
        reasoning_effort='high', agent_name='codex', agent_version='0.163.0', main_branch='main', keep_container=True,
        trial_name=chain, max_retries=1, timeout_ms=config['benchmark']['timeout_seconds'] * 1000)
    error = None
    started = time.monotonic()
    try:
        save(output / 'quota_before.json', read_quota())
        check_quota(load(output / 'quota_before.json'), config['resources']['quota_stop_percent'])
        runner.container_setup.start_container()
        runner.container_setup.lock_network()
        metadata['input_commit'] = restore_source(runner.container_setup, config, parent)
        prior_tags = {}
        for index in range(1, step):
            previous = load(ROOT / 'reports' / (trial_id(variant, repetition, index) + '.json'))
            tag = 'agent-impl-' + previous['milestone_id']
            if runner._get_tag_hash(tag) != previous['ending_commit']:
                raise ValueError('Restored previous submission tag differs')
            prior_tags[tag] = previous['ending_commit']
        install(runner.container_setup, output, config, variant)
        runner._snapshot_baseline_commit = config['benchmark']['common_starting_commit']
        assert_boundary(runner, metadata['input_commit'])
        if variant in ('caveman', 'ponytail'):
            runner.agent_runner._framework = Hooks(reasoning_effort='high', agent_version='0.163.0')
        if variant == 'serena':
            if parent:
                runner.container_setup.docker_exec(['mkdir', '-p', '/testbed/.serena'], user='root')
                copy_to(runner.container_name, Path(parent['artifacts_path']) / 'serena_memories', '/testbed/.serena/memories')
                runner.container_setup.docker_exec(['chown', '-R', 'fakeroot:fakeroot', '/testbed/.serena'], user='root')
            memory_before = memory_state(runner.container_setup)
            verify_memory_boundary(memory_before, parent['skill_state']['after'] if parent else None)
            save(output / 'serena_memory_before.json', memory_before)
        if parent:
            restore_history(runner.container_setup, parent, output)
        prompt = runner._load_prompt()
        check_resources(config)
        runner.container_setup.prepare_agent_invocation()
        save(output / 'run_metadata.json', metadata)
        progress(chain, state='running', active_step=step, completed_steps=step - 1)
        execution_started = time.monotonic()
        ok = (runner.agent_runner.resume_session(session, prompt) if parent else runner.agent_runner.run(prompt)[0])
        save(output / 'execution.json', {'duration_seconds': time.monotonic() - execution_started})
        session = runner.agent_runner.session_id
        metadata['executor_session_id'] = session
        save(output / 'run_metadata.json', metadata)
        if not ok or not session or (parent and session != parent['continuous']['executor_session_id']):
            raise RuntimeError('Model turn stopped or changed sessions; recovery requires a distinct attempt')
        events = events_from(output / 'log/agent_stdout.txt')
        dispatch = verify_dispatch(events, session, task_path, task)
        save(output / 'dispatch.json', dispatch)
        if variant == 'serena':
            preserve_memory(runner.container_setup, output, memory_before, verify_usage(events, dispatch['read_item_id'], memory_before))
        if variant in ('caveman', 'ponytail'):
            subprocess.run(['docker', 'cp', runner.container_name + ':/home/fakeroot/.codex/skill_hook_audit.jsonl',
                            str(output / 'hook_audit.jsonl')], check=True, capture_output=True)
            audit = [json.loads(l) for l in (output / 'hook_audit.jsonl').read_text().splitlines()]
            flag = 'full_mode_context' if variant == 'ponytail' else 'caveman_mode_context'
            if not any(r.get(flag) for r in audit):
                raise ValueError('Actual native hook activation missing from model turn')
            save(output / 'skill_activation.json', {'native_hook_activation_verified': True, 'audit': audit})
        submission = runner._get_tag_hash('agent-impl-' + milestone)
        assert_boundary(runner, submission)
        if runner.container_setup.docker_exec_git('merge-base', '--is-ancestor', metadata['input_commit'], submission).returncode:
            raise ValueError('Submission does not descend from the previous checkpoint')
        if any(runner._get_tag_hash(tag) != commit for tag, commit in prior_tags.items()):
            raise ValueError('Model changed a previous submission tag')
        snapshot = runner._extract_snapshot(expected_tag_hash=submission)
        assert_no_profile_artifacts(snapshot)
        runner._extract_and_parse_logs()
        checkpoint(runner, output, config)
        evaluation_started = time.monotonic()
        runner._run_evaluation(snapshot)
        save(output / 'durations.json', {'evaluation': time.monotonic() - evaluation_started})
        raw = load(output / 'evaluation/evaluation_result.json')
        if raw.get('error_message') or raw.get('infra_invalid') or not raw.get('test_summary', {}).get('total'):
            raise ValueError('Original grader infrastructure failed; do not start the next task')
        scan(output, output / 'sonar')
        metadata['state'] = 'finished'
    except Exception as caught:
        error = caught
        category = ('quota_pressure' if runner.agent_runner._last_rate_limit else 'scikit_step_failure')
        metadata.update(state='failed', failure_category=category,
                        error=redact(str(caught), credential_values(Path.home() / '.codex/auth.json')))
        # A failed or unfinished model turn keeps its container for explicit recovery.
    finally:
        metadata.update(duration_seconds=time.monotonic() - started,
                        executor_session_id=runner.agent_runner.session_id or session)
        metadata.setdefault('input_commit', parent['ending_commit'] if parent else config['benchmark']['common_starting_commit'])
        save(output / 'run_metadata.json', metadata)
        save(output / 'quota_after.json', read_quota())
        redact_artifacts(output, credential_values(Path.home() / '.codex/auth.json'))
        record = collect(output, config, parent)
        publish(record)
        progress(chain, state='failed' if error or record['collection_errors'] else 'ready_next_step',
                 completed_steps=step - 1 if error else step, active_step=None, last_step=name,
                 failure_category=metadata.get('failure_category'))
    if error:
        raise error
    if record['collection_errors']:
        raise RuntimeError('Source/session collection failed; retained container requires review')
    compact(output)
    runner.container_setup.cleanup()
    if step == 6:
        progress(chain, state='finished', completed_steps=6)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--next', action='store_true', required=True)
    parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = load(CONFIG)
    lock = trial_lock(ROOT / 'results/scikit_runtime')
    existing = {r['trial_id']: r for r in (json.loads(l) for l in (ROOT / 'results/results.jsonl').read_text().splitlines() if l.strip())}
    for repetition, step, variant in schedule():
        name = trial_id(variant, repetition, step)
        if name in existing:
            if existing[name]['trial_state'] != 'finished' or existing[name]['collection_errors']:
                raise RuntimeError('An earlier attempt needs explicit recovery; scheduler is stopped')
            continue
        run_one(config, variant, repetition, step)
        break
    else:
        print('All 48 planned steps are already collected.')


if __name__ == '__main__':
    main()
