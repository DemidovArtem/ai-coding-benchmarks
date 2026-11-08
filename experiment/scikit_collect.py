"""Collect Python trajectories while retaining all historical attempts."""

import hashlib
import json
from pathlib import Path
import subprocess

from experiment.collect import load
from experiment.continuous import events_from, usage_delta
from experiment.metrics import codex_usage, normalize_grader
from experiment.python_metrics import footprint, verify_snapshot
from experiment.report import export
from experiment.runner import ROOT, save


def metrics_repository(run):
    repo = run / 'metrics_repository'
    if not repo.exists():
        subprocess.run(['git', 'clone', '--bare', '--quiet',
                        str(ROOT / 'results/scikit_preflight/common_base/repository.bundle'), str(repo)],
                       check=True, capture_output=True)
        if (run / 'repository.bundle').exists():
            subprocess.run(['git', '-C', str(repo), 'fetch', '--quiet', '--update-head-ok',
                            str(run / 'repository.bundle'), '+refs/*:refs/*'], check=True, capture_output=True)
    return repo


def publish(record):
    path = ROOT / 'results/results.jsonl'
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if any(r['trial_id'] == record['trial_id'] for r in rows):
        raise ValueError('Refuse to replace an existing attempt; use a distinct recovery ID')
    export([*rows, record], ROOT / 'results')
    save(ROOT / 'reports' / (record['trial_id'] + '.json'), record)


def collect(run, config, parent=None):
    metadata = load(run / 'run_metadata.json')
    if metadata['state'] not in ('finished', 'failed'):
        raise ValueError('Do not collect a live model turn')
    raw = load(run / 'evaluation/evaluation_result.json', {})
    sidecar = load(run / 'evaluation/source_snapshot.integrity.json', {})
    profile = load(run / 'effective_profile.json', {})
    cumulative = codex_usage(events_from(run / 'log/agent_stdout.txt'))
    previous = parent['usage']['executor_cumulative'] if parent else None
    errors = []
    try:
        usage = usage_delta(cumulative, previous)
    except ValueError as error:
        errors.append(str(error))
        usage = {k: None for k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')}
    valid = bool(raw.get('test_summary', {}).get('total')) and not raw.get('infra_invalid') and not raw.get('error_message')
    initial = config['benchmark']['common_starting_commit']
    record = {'experiment_id': config['experiment_id'], 'cohort': 'scikit-configuration-v1-pilot',
        'trial_id': run.name, 'trial_kind': 'continuous_step', 'measured_comparison': True,
        'repo': config['benchmark']['repo'], 'milestone_id': config['benchmark']['milestones'][metadata['step'] - 1],
        'variant': metadata['variant'], 'repetition': metadata['repetition'], 'trial_state': metadata['state'],
        'trial_failure_category': metadata.get('failure_category'), 'model': config['codex']['model'],
        'reasoning_effort': config['codex']['reasoning_effort'], 'dataset_version': config['benchmark']['version'],
        'dataset_commit': config['pins']['git_commits']['results/setup/dataset'],
        'starting_commit': initial, 'starting_tree': config['benchmark']['common_starting_tree'],
        'ending_commit': sidecar.get('agent_tag_commit'), 'snapshot_sha256': sidecar.get('snapshot_sha256'),
        'artifacts_path': str(run), 'effective_profile': profile, 'setup_fingerprint': metadata['setup_fingerprint'],
        'implementation_commit': metadata['implementation_commit'], 'duration_seconds': metadata.get('duration_seconds'),
        'durations_seconds': {'executor': load(run / 'execution.json', {}).get('duration_seconds'),
                              'evaluation': load(run / 'durations.json', {}).get('evaluation'),
                              'sonar': load(run / 'sonar/sonar.json', {}).get('duration_seconds')},
        'usage': {'planner': {'used': False, 'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0},
                  'executor': usage, 'executor_cumulative': cumulative,
                  'total': {k: usage.get(k) for k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')}},
        'quota': {'before': load(run / 'quota_before.json'), 'after': load(run / 'quota_after.json')},
        'continuous': {k: metadata[k] for k in ('trajectory_id', 'step', 'repetition', 'executor_session_id', 'input_commit')},
        'collection_errors': errors, 'skill_state': load(run / 'serena_state.json'),
        'hook_activation_audit': load(run / 'skill_activation.json'),
        'grading_validity': {'valid': valid, 'raw_score_preserved': True,
                             'common_base_limitation': 'M06 unchanged-base preflight has 78 missing P2P tests; inspect raw counts.'},
        'sonar': load(run / 'sonar/sonar.json', {'analysis_ok': None, 'metrics': None, 'status': 'not_run'}),
        **normalize_grader(raw)}
    record.update({k: None for k in ('added_prod_loc', 'deleted_prod_loc', 'net_prod_loc', 'churn_prod_loc',
                                    'changed_prod_files', 'cumulative_prod_loc')})
    if not valid:
        record.update(resolved=None, failure_category=metadata.get('failure_category') or 'grader_infrastructure_failure')
    record['failure_category'] = record.get('failure_category') or metadata.get('failure_category')
    if sidecar and (run / 'repository.bundle').exists():
        try:
            repo = metrics_repository(run)
            captured = verify_snapshot(run / 'evaluation/source_snapshot.tar', sidecar, repo)
            filters = load(ROOT / config['benchmark']['dataset_root'] / config['benchmark']['repo'] / 'metadata.json')
            record.update(footprint(repo, initial, sidecar['agent_tag_commit'], filters))
            record['verified_snapshot_files'] = len(captured)
            record['continuous']['incremental_footprint'] = footprint(repo, metadata['input_commit'], sidecar['agent_tag_commit'], filters)
            sonar = record['sonar']
            if sonar.get('analysis_ok'):
                binding = load(run / 'sonar/binding.json')
                if (not sonar.get('python_coverage_verified') or not sonar.get('snapshot_binding_verified')
                        or sonar['snapshot_sha256'] != record['snapshot_sha256']
                        or binding['submission_commit'] != record['ending_commit']):
                    raise ValueError('Python Sonar source binding failed')
                base = load(ROOT / 'results/scikit_preflight/python_sonar_base_attempt02/sonar.json')
                if base['protocol_sha256'] != sonar['protocol_sha256']:
                    raise ValueError('Python Sonar common-base protocol differs')
                sonar['delta_vs_common_base'] = {k: v - base['metrics'][k] if v is not None and base['metrics'].get(k) is not None
                                                else None for k, v in sonar['metrics'].items()}
                sonar['common_base_comparison_verified'] = True
        except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as error:
            errors.append(str(error)); record['failure_category'] = record['failure_category'] or 'collection_failure'
    else:
        errors.append('Source checkpoint or snapshot missing')
    return record
