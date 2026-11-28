"""Prepare the separate scikit-learn cohort without replaying the ripgrep pilot."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from experiment.runner import ROOT, save, trial_lock

REPOSITORY = 'scikit-learn_scikit-learn_1.5.2_1.6.0'
WORKSPACE = ROOT / 'results/setup/dataset' / REPOSITORY
CONFIG = ROOT / 'reports/scikit_experiment.json'


def artifact(config, name, default):
    return ROOT / config.get('artifacts', {}).get(name, default)


def initial_config(runtime_manifest='profiles/scikit_runtime/manifest.json'):
    budget = json.loads((ROOT / 'reports/second_repository_preflight.json').read_text())
    runtime = json.loads((ROOT / runtime_manifest).read_text())
    config = {
        'experiment_id': 'scikit-configuration-v1-pilot', 'stage': 'preflight', 'measurement_started': False,
        'codex': {'version': '0.163.0', 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'auth': 'chatgpt_oauth_only'},
        'variants': ['baseline', 'caveman', 'ponytail', 'serena'],
        'benchmark': {'repo': REPOSITORY, 'version': 'v1.0.2', 'dataset_root': 'results/setup/dataset',
                      'smoke_milestone': 'M06', 'milestones': budget['selected_tasks'], 'main_branch': 'main',
                      'timeout_seconds': 1800, 'skill_runtime_image_id': runtime['image_id']},
        'resources': {'parallel_trials': 1, 'min_workspace_free_bytes': 1_000_000_000,
                      'docker_free_reserve_bytes': 12_000_000_000, 'quota_stop_percent': 85,
                      'runtime_root': str(ROOT / 'results/scikit_runtime')},
        'pins': {'git_commits': {'results/setup/dataset': budget['dataset_commit']}, 'file_sha256': {}},
    }
    for name, expected in budget['csv_sha256'].items():
        path = WORKSPACE / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Pinned dataset input changed: ' + name)
        config['pins']['file_sha256'][str(path.relative_to(ROOT))] = expected
    return config


class PreparedBoundary(Exception):
    pass


def prepare_base(config=None, config_path=CONFIG):
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.profiles import activate_profile
    from experiment.python_metrics import verify_snapshot

    config = config if config is not None else initial_config()
    prepared = artifact(config, 'common_base', 'results/scikit_preflight/common_base')
    if prepared.exists():
        raise ValueError('Preflight output already exists; do not overwrite an attempt')
    save(config_path, config)

    class PrepareRunner(MilestoneRunner):
        def _load_prompt(self):
            proof = activate_profile(self.container_setup, prepared, config)
            tree = self.container_setup.docker_exec_git('rev-parse', 'HEAD^{tree}').stdout.strip()
            proof['starting_tree'] = tree
            save(prepared / 'effective_profile.json', proof)
            self.container_setup.docker_exec_git('tag', 'agent-impl-M06')
            snapshot = self._extract_snapshot(proof['starting_commit'])
            self.container_setup.docker_exec_git('bundle', 'create', '/tmp/scikit-preflight.bundle', '--all')
            subprocess.run(['docker', 'cp', self.container_name + ':/tmp/scikit-preflight.bundle',
                            str(prepared / 'repository.bundle')], check=True, capture_output=True)
            subprocess.run(['git', 'clone', '--bare', '--quiet', str(prepared / 'repository.bundle'),
                            str(prepared / 'metrics_repository')], check=True, capture_output=True)
            sidecar = json.loads((prepared / 'evaluation/source_snapshot.integrity.json').read_text())
            manifest = verify_snapshot(snapshot, sidecar, prepared / 'metrics_repository')
            save(prepared / 'source_manifest.json', manifest)
            config['benchmark'].update(common_starting_tree=tree, common_starting_commit=proof['starting_commit'])
            save(config_path, config)
            save(prepared / 'preparation.json', {'state': 'prepared', 'model_calls': 0,
                 'container': self.container_name, 'runtime_image_id': config['benchmark']['skill_runtime_image_id'],
                 'source_manifest_files': len(manifest), 'starting_tree': tree,
                 'quarantine_verified': True, 'baseline_profile_verified': True,
                 'snapshot_sha256': sidecar['snapshot_sha256'],
                 'note': 'Host tagged unchanged common base for infrastructure evaluation; not an agent submission.'})
            raise PreparedBoundary()

    runner = PrepareRunner(workspace_root=WORKSPACE, milestone_id='M06', srs_path=WORKSPACE / 'srs/M06/SRS.md',
        output_dir=prepared, image_name=config['benchmark']['skill_runtime_image_id'], agent_name='codex',
        agent_version='0.163.0', model=config['codex']['model'], reasoning_effort='high', main_branch='main',
        keep_container=True, trial_name=config.get('trial_prefix', 'scikit') + '_preflight_common_base', max_retries=1)
    try:
        runner.run()
    except PreparedBoundary:
        print('Common source prepared and quarantined; zero model calls.')
    else:
        raise RuntimeError('Preflight must stop before inference')


def grade_base(config=None):
    from harness.e2e.evaluator import PatchEvaluator
    config = config or {}
    prepared = artifact(config, 'common_base', 'results/scikit_preflight/common_base')
    output = artifact(config, 'base_grader', 'results/scikit_preflight/base_grader')
    output.mkdir(parents=True, exist_ok=False)
    evaluator = PatchEvaluator(workspace_root=WORKSPACE, milestone_id='M06',
        patch_file=prepared / 'evaluation/source_snapshot.tar',
        baseline_classification=WORKSPACE / 'test_results/M06/M06_classification.json', output_dir=output,
        repo_config_path=prepared / 'repo_config.yaml',
        repo_config_sha256=hashlib.sha256((prepared / 'repo_config.yaml').read_bytes()).hexdigest(),
        runtime_policy_path=prepared / 'runtime_policy.yaml',
        runtime_policy_sha256=hashlib.sha256((prepared / 'runtime_policy.yaml').read_bytes()).hexdigest(),
        runtime_policy_mode='protected')
    result = evaluator.evaluate().to_dict()
    save(output / 'evaluation_result.json', result)
    valid = not result.get('infra_invalid') and bool(result.get('test_summary', {}).get('total'))
    save(artifact(config, 'grader_preflight', 'reports/scikit_grader_preflight.json'), {'valid': valid, 'model_calls': 0,
         'kind': 'unchanged_common_base_infrastructure_probe', 'raw_resolved': result.get('resolved'),
         'test_summary': result.get('test_summary'), 'error_message': result.get('error_message'),
         'raw_artifacts': str(output.relative_to(ROOT))})
    if not valid:
        raise RuntimeError('Common-base grader infrastructure is invalid; inference withheld')
    print('Original grader infrastructure verified on unchanged common base; not a model result.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--prepare-base', action='store_true')
    actions.add_argument('--grade-base', action='store_true')
    parser.add_argument('--config', type=Path, default=CONFIG)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = json.loads(args.config.read_text()) if args.config.exists() else None
    with trial_lock(ROOT / 'results/scikit_runtime'):
        prepare_base(config, args.config) if args.prepare_base else grade_base(config)


if __name__ == '__main__':
    main()
