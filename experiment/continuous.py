"""Bounded sequential pilot: one protected repository and Codex thread per trajectory."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

from experiment.collect import collect, load
from experiment.metrics import codex_usage, footprint
from experiment.report import export
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.quota import read_quota
from experiment.security import credential_values, redact, redact_artifacts

VARIANTS = ('baseline', 'caveman', 'ponytail', 'plan')
TOKEN_FIELDS = ('input_tokens', 'output_tokens', 'cached_input_tokens', 'reasoning_output_tokens')


def verify_selection(milestones, edges):
    if len(milestones) < 2 or len(set(milestones)) != len(milestones):
        raise ValueError('A trajectory needs at least two distinct milestones')
    positions = {name: index for index, name in enumerate(milestones)}
    for edge in edges:
        if edge['target_id'] not in positions or edge['strength'].lower() != 'strong':
            continue
        if edge['source_id'] not in positions or positions[edge['source_id']] >= positions[edge['target_id']]:
            raise ValueError('Selected trajectory has a missing or unordered prerequisite')


def verify_dispatch(events, session, path, task):
    threads = {event['thread_id'] for event in events if event.get('type') == 'thread.started'}
    if threads != {session}:
        raise ValueError('Executor did not preserve the authoritative Codex thread')
    commands = [event['item'] for event in events if event.get('type') == 'item.completed'
                and event.get('item', {}).get('type') == 'command_execution']
    if not commands or path not in commands[0].get('command', '') or commands[0].get('exit_code') != 0:
        raise ValueError('Executor must read the dispatched task before other shell work')
    if commands[0].get('aggregated_output', '').strip() != task.strip():
        raise ValueError('Executor did not read the complete validated task/handoff')
    return {'session_id': session, 'read_item_id': commands[0].get('id'),
            'task_sha256': hashlib.sha256(task.encode()).hexdigest(), 'read_verified': True}


def usage_delta(current, previous):
    if not current.get('session_ids'):
        return {**current, **{key: None for key in TOKEN_FIELDS}, 'counter_semantics': 'no completed step counters'}
    if current.get('anomalies') or (previous and current['session_ids'] != previous['session_ids']):
        raise ValueError('Continuous token counters have an invalid thread boundary')
    result = dict(current)
    for key in TOKEN_FIELDS:
        value, before = current.get(key), previous.get(key) if previous else 0
        if value is not None and before is not None and value < before:
            raise ValueError('Continuous token counter decreased')
        result[key] = value - before if value is not None and before is not None else None
    result['counter_semantics'] = 'difference of cumulative thread totals at consecutive step boundaries'
    return result


def verify_images():
    for image in load(ROOT / 'reports/continuous_image_budget.json'):
        actual = json.loads(subprocess.check_output(['docker', 'image', 'inspect', image['local']], text=True))[0]
        if image['digest_ref'] not in actual.get('RepoDigests', []):
            raise ValueError('Required grader image is not pinned to its approved digest')


def check_resources(config):
    if shutil.disk_usage(ROOT).free < config['resources']['min_workspace_free_bytes']:
        raise RuntimeError('Workspace free-space reserve is insufficient')
    docker_root = subprocess.check_output(['docker', 'info', '--format', '{{.DockerRootDir}}'], text=True).strip()
    # Docker storage can be readable only to the daemon; its nearest readable parent shares the filesystem.
    while not Path(docker_root).exists():
        docker_root = str(Path(docker_root).parent)
    if shutil.disk_usage(docker_root).free < config['resources']['docker_free_reserve_bytes']:
        raise RuntimeError('Docker free-space reserve is insufficient')


def events_from(path):
    events = []
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def freeze(output, repetitions):
    if repetitions < 1:
        raise ValueError('At least one repetition is required')
    base = load(ROOT / 'reports/phase3_experiment.json')
    validate(base)
    plan = load(ROOT / 'reports/continuous_feasibility.json')
    workspace = ROOT / base['benchmark']['dataset_root'] / base['benchmark']['repo']
    edges = []
    for name, expected in plan['csv_sha256'].items():
        path = workspace / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Continuous selection CSV changed: ' + name)
        if 'dependencies' in name:
            edges.extend(csv.DictReader(path.open()))
    verify_selection(plan['selected_milestones'], edges)
    base.update(experiment_id='ripgrep-continuous-v1-pilot', stage='phase5_frozen', variants=list(VARIANTS))
    base['benchmark']['continuous_pilot'] = {
        'label': 'pilot/non-official subset', 'milestones': plan['selected_milestones'],
        'repetitions': repetitions, 'same_executor_session_required': True,
        'dispatch': 'host-gated turns using codex exec resume; no background watcher',
        'stop_after': len(plan['selected_milestones']), 'grader_feedback_to_agent': False}
    base['benchmark']['timeout_seconds'] = 1800
    base['resources']['min_workspace_free_bytes'] = 1_000_000_000
    paths = [ROOT / 'experiment/continuous.py', ROOT / 'reports/phase5_protocol.md',
             ROOT / 'reports/continuous_image_budget.json']
    paths += [workspace / 'srs' / name / 'SRS.md' for name in plan['selected_milestones']]
    paths += [workspace / 'test_results' / name / (name + '_classification.json') for name in plan['selected_milestones']]
    for path in paths:
        base['pins']['file_sha256'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    with output.open('x') as handle:
        json.dump(base, handle, indent=2)
        handle.write('\n')
    output.chmod(0o444)


def update_progress(chain, **values):
    path = ROOT / 'reports/continuous_feasibility.json'
    plan = load(path)
    run = next(row for row in plan['pilot_runs'] if row['trial_id'] == chain)
    run.update(values)
    cohort = run.get('cohort')
    runs = [row for row in plan['pilot_runs'] if row.get('cohort') == cohort]
    target = plan['cohorts'][cohort] if cohort else plan
    finished = sum(row['state'] == 'finished' for row in runs)
    failed = sum(row['state'] == 'failed' for row in runs)
    active = any(row['state'] == 'running' for row in runs)
    target.update(status='running' if active else 'completed' if finished == len(runs) else 'partial',
                label='Trials выполняются' if active else 'Пилот завершён' if finished == len(runs) else 'Пилот выполнен частично',
                summary=f"Траекторий завершено {finished}/{len(runs)}; ошибок {failed}. Метрики по шагам и протокол ниже.",
                same_executor_session_verified=finished > 0, continuous_result_claimed=finished > 0)
    save(path, plan)
    from experiment.status import main
    main()


def runtime_binding(config, output):
    """Use an explicitly pinned policy for a new cohort without editing upstream policy."""
    policy_root = config['benchmark'].get('runtime_policy_root')
    if policy_root is None:
        return None
    from harness.e2e.runtime_policy_binding import (freeze_runtime_policy, resolve_runtime_policy,
                                                   runtime_policy_coverage_errors)
    policy = resolve_runtime_policy(config['benchmark']['repo'], ROOT / policy_root)
    if policy.mode != 'protected' or runtime_policy_coverage_errors(policy):
        raise ValueError('Explicit cohort policy must pass protected quarantine coverage')
    return freeze_runtime_policy(output, policy)


def preserve_and_collect(runner, output, config, metadata, previous_usage, input_commit):
    """Preserve every terminal step and merge it into the existing result register."""
    try:
        runner.agent_runner.extract_trace(output / 'log')
        bundle = '/tmp/continuous-submission.bundle'
        result = runner.container_setup.docker_exec_git('bundle', 'create', bundle, '--all')
        if result.returncode:
            raise RuntimeError('Git bundle capture failed')
        subprocess.run(['docker', 'cp', runner.container_name + ':' + bundle, str(output / 'repository.bundle')],
                       check=True, capture_output=True)
    except (OSError, subprocess.SubprocessError, RuntimeError) as error:
        metadata.setdefault('artifact_error', str(error))
    save(output / 'run_metadata.json', metadata)
    secrets = credential_values(Path.home() / '.codex/auth.json')
    redact_artifacts(output, secrets)
    durable = ROOT / 'results/trials' / output.name
    shutil.copytree(output, durable)
    record = collect(durable, config)
    record['repetition'] = metadata['repetition']
    cumulative = codex_usage(events_from(durable / 'log/agent_stdout.txt'))
    try:
        executor = usage_delta(cumulative, previous_usage)
    except ValueError as error:
        record['collection_errors'].append(str(error))
        record['failure_category'] = record['failure_category'] or 'continuous_usage_failure'
        executor = {**cumulative, **{key: None for key in TOKEN_FIELDS}}
    record['usage']['executor_cumulative'] = cumulative
    record['usage']['executor'] = executor
    record['usage']['total'] = {key: sum(record['usage'][phase][key] for phase in ('planner', 'executor'))
        if all(record['usage'][phase].get(key) is not None for phase in ('planner', 'executor')) else None
        for key in TOKEN_FIELDS}
    record['durations_seconds']['executor'] = load(durable / 'execution.json', {}).get('duration_seconds')
    record['continuous'] = {key: metadata[key] for key in ('trajectory_id', 'step', 'repetition', 'executor_session_id')}
    record['continuous'].update(input_commit=input_commit, dispatch=load(durable / 'dispatch.json'),
                                initial_starting_commit=record['starting_commit'])
    if record.get('ending_commit') and not record['collection_errors']:
        filters = load(ROOT / config['benchmark']['dataset_root'] / config['benchmark']['repo'] / 'metadata.json')
        record['continuous']['incremental_footprint'] = footprint(durable / 'metrics_repository', input_commit,
                                                                  record['ending_commit'], filters)
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    if any(row['trial_id'] == record['trial_id'] for row in rows):
        raise ValueError('A step ID cannot overwrite a previous result')
    export(rows + [record], ROOT / 'results')
    save(ROOT / 'reports' / (output.name + '.json'), record)
    return record, cumulative


def run(config, variant, repetition, chain):
    from harness.e2e.agent_runner import AgentRunner
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.planning import prepare
    from experiment.profiles import activate_profile
    from experiment.skill_profiles import install_native_skill
    from experiment.skill_trial import assert_no_profile_artifacts

    benchmark = config['benchmark']
    workspace = ROOT / benchmark['dataset_root'] / benchmark['repo']
    milestones = benchmark['continuous_pilot']['milestones']
    runtime = Path(config['resources']['runtime_root'])
    for index in range(1, len(milestones) + 1):
        name = chain + '_s' + str(index).zfill(2)
        if (runtime / name).exists() or (ROOT / 'results/trials' / name).exists():
            raise ValueError('Continuous trial outputs must be fresh')
    fingerprint = setup_fingerprint(config)[0]
    initialized = False
    proof = None
    task = dispatch_path = input_commit = None
    output = None

    class Hooks(CodexFramework):
        def build_run_command(self, *args, **kwargs):
            return super().build_run_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

        def build_resume_command(self, *args, **kwargs):
            return super().build_resume_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

    class TimedAgent(AgentRunner):
        def run(self, *args, **kwargs):
            started = time.monotonic()
            try:
                return super().run(*args, **kwargs)
            finally:
                save(output / 'execution.json', {'duration_seconds': time.monotonic() - started})

        def resume_session(self, *args, **kwargs):
            started = time.monotonic()
            try:
                return super().resume_session(*args, **kwargs)
            finally:
                elapsed = load(output / 'execution.json', {}).get('duration_seconds', 0)
                save(output / 'execution.json', {'duration_seconds': elapsed + time.monotonic() - started})

    class ContinuousRunner(MilestoneRunner):
        def _load_prompt(self):
            nonlocal initialized, proof, task, dispatch_path, input_commit
            original = super()._load_prompt()
            if not initialized:
                if variant in ('caveman', 'ponytail'):
                    proof = install_native_skill(self.container_setup, output, config, variant)
                    self.agent_runner._framework = Hooks(reasoning_effort=config['codex']['reasoning_effort'])
                else:
                    proof = activate_profile(self.container_setup, output, config)
                tree = self.container_setup.docker_exec_git('rev-parse', 'HEAD^{tree}').stdout.strip()
                if tree != benchmark['common_starting_tree']:
                    raise ValueError('Continuous starting tree differs from the frozen cohort')
                initialized = True
            else:
                save(output / 'effective_profile.json', proof)
                self.container_setup.verify_network_lockdown()
            input_commit = self.container_setup.docker_exec_git('rev-parse', 'HEAD').stdout.strip()
            task = original
            if variant == 'plan':
                quota = read_quota()
                save(output / 'quota_before_planner.json', quota)
                check_quota(quota, config['resources']['quota_stop_percent'])
                planner_input = SimpleNamespace(container_name=self.container_name, image_name=self.image_name,
                    repo_name=self.repo_name, runtime_policy_binding=self.runtime_policy_binding,
                    container_setup=self.container_setup, _snapshot_baseline_commit=input_commit)
                task = prepare(planner_input, original, config, output, 'plan')
                planner_commit = subprocess.check_output(['git', '-C', str(output / 'planner/repository'), 'rev-parse', 'HEAD'], text=True).strip()
                if planner_commit != input_commit:
                    raise ValueError('Planner did not receive the exact previous submitted source commit')
            (output / 'original_task.txt').write_text(original)
            task += ('\n\nThis is one step of a sequential pilot. Preserve prior work and submission tags. '
                     'Implement only this task. After committing and tagging this step, stop and await the next user turn.\n')
            path = output / 'dispatched_task.txt'
            path.write_text(task)
            dispatch_path = '/home/fakeroot/continuous-step-' + str(index) + '.txt'
            subprocess.run(['docker', 'cp', str(path), self.container_name + ':' + dispatch_path], check=True, capture_output=True)
            self.container_setup.docker_exec(['chown', 'root:root', dispatch_path], user='root')
            self.container_setup.docker_exec(['chmod', '0444', dispatch_path], user='root')
            quota = read_quota()
            save(output / 'quota_before_executor.json', quota)
            check_quota(quota, config['resources']['quota_stop_percent'])
            return ('Continue in this repository and session. Your first shell command must be `cat ' + dispatch_path
                    + '`. Read the complete task and any supplied plan, then follow it. Do not work on other tasks.')

        def _extract_snapshot_from_workdir(self):
            raise RuntimeError('Continuous step lacks a completed immutable submission; next step is withheld')

        def _run_evaluation(self, snapshot):
            audit = verify_dispatch(events_from(output / 'log/agent_stdout.txt'), self.agent_runner.session_id, dispatch_path, task)
            audit.update(input_commit=input_commit, milestone_id=self.milestone_id)
            planner = load(output / 'planner/audit.json', {})
            if planner:
                if planner.get('session_id') == self.agent_runner.session_id or planner.get('state') != 'validated':
                    raise ValueError('Planner isolation or handoff validation failed')
                audit['handoff_sha256'] = planner['handoff_sha256']
                save(output / 'session_isolation.json', {'planner_session_id': planner['session_id'],
                    'executor_session_id': self.agent_runner.session_id, 'separate_containers': True, 'separate_sessions': True})
            save(output / 'dispatch.json', audit)
            assert_no_profile_artifacts(snapshot)
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot)
            finally:
                save(output / 'durations.json', {'evaluation': time.monotonic() - started})

    first_output = runtime / (chain + '_s01')
    binding = runtime_binding(config, first_output)
    runner = ContinuousRunner(workspace_root=workspace, milestone_id=milestones[0],
        srs_path=workspace / 'srs' / milestones[0] / 'SRS.md', output_dir=first_output,
        image_name=benchmark['skill_runtime_image_id'], agent_name='codex', agent_version=config['codex']['version'],
        model=config['codex']['model'], reasoning_effort=config['codex']['reasoning_effort'],
        timeout_ms=benchmark['timeout_seconds'] * 1000, main_branch=benchmark['main_branch'],
        keep_container=True, trial_name=chain, max_retries=1, runtime_policy_binding=binding)
    runner.agent_runner = TimedAgent(container_name=runner.container_name, workdir='/testbed',
        model=config['codex']['model'], timeout_ms=benchmark['timeout_seconds'] * 1000,
        log_dir=first_output / 'log', agent_name='codex', reasoning_effort=config['codex']['reasoning_effort'])
    session = previous_commit = None
    previous_usage = {}
    submissions = {}
    finished = 0
    try:
        for index, milestone in enumerate(milestones, 1):
            output = runtime / (chain + '_s' + str(index).zfill(2))
            if index == 1:
                # Constructor freezes bindings in this directory, before any model request.
                if (output / 'run_metadata.json').exists():
                    raise ValueError('Trial output already exists')
            else:
                output.mkdir(exist_ok=False)
            output.chmod(0o700)
            runner.milestone_id, runner.srs_path = milestone, workspace / 'srs' / milestone / 'SRS.md'
            runner.output_dir, runner.log_dir = output, output / 'log'
            runner.log_dir.mkdir(exist_ok=True)
            runner.agent_runner.log_dir = runner.log_dir
            step_config = json.loads(json.dumps(config))
            step_config['benchmark']['smoke_milestone'] = milestone
            save(output / 'experiment.json', step_config)
            metadata = {'phase': 'trial', 'trial_kind': 'continuous_step', 'measured_comparison': True,
                'state': 'running', 'variant': variant, 'trajectory_id': chain, 'step': index,
                'repetition': repetition, 'model': config['codex']['model'], 'reasoning_effort': config['codex']['reasoning_effort'],
                'started_at': datetime.now(timezone.utc).isoformat(), 'executor_session_id': session,
                'setup_fingerprint': fingerprint, 'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
            save(output / 'run_metadata.json', metadata)
            update_progress(chain, state='running', completed_steps=finished, active_step=index)
            started = time.monotonic()
            error = None
            try:
                quota = read_quota()
                save(output / 'quota_before.json', quota)
                check_quota(quota, config['resources']['quota_stop_percent'])
                if index == 1:
                    result = runner.run()
                    session = runner.agent_runner.session_id
                else:
                    result = resume_step(runner, session, previous_commit)
                commit = runner._get_tag_hash('agent-impl-' + milestone)
                assert_boundary(runner, commit)
                if previous_commit:
                    if runner.container_setup.docker_exec_git('merge-base', '--is-ancestor', previous_commit, commit).returncode:
                        raise ValueError('New submission does not descend from the previous step')
                for prior_milestone, prior_commit in submissions.items():
                    if runner._get_tag_hash('agent-impl-' + prior_milestone) != prior_commit:
                        raise ValueError('A previous submission tag changed')
                submissions[milestone] = commit
                if variant in ('caveman', 'ponytail'):
                    subprocess.run(['docker', 'cp', runner.container_name + ':/home/fakeroot/.codex/skill_hook_audit.jsonl', str(output / 'hook_audit.jsonl')], check=True, capture_output=True)
                    audit = [json.loads(line) for line in (output / 'hook_audit.jsonl').read_text().splitlines()]
                    active = any(row.get('full_mode_context') if variant == 'ponytail' else row.get('caveman_mode_context') for row in audit)
                    save(output / 'skill_activation.json', {'variant': variant, 'native_hook_activation_verified': active, 'audit': audit})
                    if not active:
                        raise RuntimeError('Native skill activation was not observed')
                if load(output / 'evaluation/evaluation_result.json').get('error_message'):
                    raise RuntimeError('Grader infrastructure failed; next step is withheld')
                previous_commit = commit
                finished += 1
                metadata.update(state='finished', returncode=0 if result.resolved else 1)
            except Exception as caught:
                error = caught
                category = 'quota_pressure' if str(caught).startswith('Quota pressure') or runner.agent_runner._last_rate_limit else 'continuous_step_failure'
                metadata.update(state='failed', failure_category=category,
                                error=redact(str(caught), credential_values(Path.home() / '.codex/auth.json')))
            finally:
                metadata.update(duration_seconds=time.monotonic() - started,
                                executor_session_id=runner.agent_runner.session_id if initialized else session)
                save(output / 'quota_after.json', read_quota())
                record, previous_usage = preserve_and_collect(runner, output, step_config, metadata, previous_usage, input_commit)
                update_progress(chain, state='failed' if error else 'running', completed_steps=finished,
                                active_step=None, last_step=output.name, failure_category=metadata.get('failure_category'))
            if error:
                raise error
            if record['collection_errors']:
                raise RuntimeError('Step collection failed; next step is withheld')
        update_progress(chain, state='finished', completed_steps=finished)
        runner.container_setup.cleanup()
    except Exception:
        update_progress(chain, state='failed', completed_steps=finished)
        raise


def assert_boundary(runner, commit):
    actual = runner.container_setup.docker_exec_git('rev-parse', 'HEAD')
    dirty = runner.container_setup.docker_exec_git('status', '--porcelain')
    if not commit or actual.returncode or dirty.returncode or actual.stdout.strip() != commit or dirty.stdout.strip():
        raise ValueError('Step boundary is not the clean immutable submitted commit')


def resume_step(runner, session, previous_commit):
    assert_boundary(runner, previous_commit)
    prompt = runner._load_prompt()
    runner.container_setup.prepare_agent_invocation()
    if not runner.agent_runner.resume_session(session, prompt):
        raise RuntimeError('Continuous executor resume failed; next step is withheld')
    if runner.agent_runner.session_id != session:
        raise RuntimeError('Executor switched sessions during resume')
    if not runner._verify_tag_exists():
        raise RuntimeError('Continuous executor did not submit this step')
    submission = runner._get_tag_hash('agent-impl-' + runner.milestone_id)
    snapshot = runner._extract_snapshot(expected_tag_hash=submission)
    runner._extract_and_parse_logs()
    return runner._run_evaluation(snapshot)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('freeze', 'trial'))
    parser.add_argument('--config', type=Path, default=ROOT / 'reports/phase5_experiment.json')
    parser.add_argument('--variant', choices=VARIANTS)
    parser.add_argument('--repetition', type=int, default=1)
    parser.add_argument('--repetitions', type=int, default=2)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    if args.action == 'freeze':
        freeze(args.config, args.repetitions)
        return
    config = load(args.config)
    if config.get('stage') != 'phase5_frozen' or not args.variant or not 1 <= args.repetition <= config['benchmark']['continuous_pilot']['repetitions']:
        parser.error('A frozen continuous cohort, variant and valid repetition are required')
    validate(config)
    verify_images()
    check_resources(config)
    lock = trial_lock(Path(config['resources']['runtime_root']))
    try:
        run(config, args.variant, args.repetition, 'phase5_' + args.variant + '_r' + str(args.repetition).zfill(2))
    finally:
        lock.close()


if __name__ == '__main__':
    main()
