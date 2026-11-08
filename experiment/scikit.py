"""Prepare the separate scikit-learn cohort without replaying the ripgrep pilot."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from experiment.runner import ROOT, save

REPOSITORY = 'scikit-learn_scikit-learn_1.5.2_1.6.0'
WORKSPACE = ROOT / 'results/setup/dataset' / REPOSITORY
CONFIG = ROOT / 'reports/scikit_experiment.json'
PREPARED = ROOT / 'results/scikit_preflight/common_base'


def initial_config():
    budget = json.loads((ROOT / 'reports/second_repository_preflight.json').read_text())
    runtime = json.loads((ROOT / 'profiles/scikit_runtime/manifest.json').read_text())
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


def prepare_base():
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.profiles import activate_profile
    from experiment.python_metrics import verify_snapshot

    if PREPARED.exists():
        raise ValueError('Preflight output already exists; do not overwrite an attempt')
    config = initial_config()
    save(CONFIG, config)

    class PrepareRunner(MilestoneRunner):
        def _load_prompt(self):
            proof = activate_profile(self.container_setup, PREPARED, config)
            tree = self.container_setup.docker_exec_git('rev-parse', 'HEAD^{tree}').stdout.strip()
            proof['starting_tree'] = tree
            save(PREPARED / 'effective_profile.json', proof)
            self.container_setup.docker_exec_git('tag', 'agent-impl-M06')
            snapshot = self._extract_snapshot(proof['starting_commit'])
            self.container_setup.docker_exec_git('bundle', 'create', '/tmp/scikit-preflight.bundle', '--all')
            subprocess.run(['docker', 'cp', self.container_name + ':/tmp/scikit-preflight.bundle',
                            str(PREPARED / 'repository.bundle')], check=True, capture_output=True)
            subprocess.run(['git', 'clone', '--bare', '--quiet', str(PREPARED / 'repository.bundle'),
                            str(PREPARED / 'metrics_repository')], check=True, capture_output=True)
            sidecar = json.loads((PREPARED / 'evaluation/source_snapshot.integrity.json').read_text())
            manifest = verify_snapshot(snapshot, sidecar, PREPARED / 'metrics_repository')
            save(PREPARED / 'source_manifest.json', manifest)
            config['benchmark'].update(common_starting_tree=tree, common_starting_commit=proof['starting_commit'])
            save(CONFIG, config)
            save(PREPARED / 'preparation.json', {'state': 'prepared', 'model_calls': 0,
                 'container': self.container_name, 'runtime_image_id': config['benchmark']['skill_runtime_image_id'],
                 'source_manifest_files': len(manifest), 'starting_tree': tree,
                 'quarantine_verified': True, 'baseline_profile_verified': True,
                 'snapshot_sha256': sidecar['snapshot_sha256'],
                 'note': 'Host tagged unchanged common base for infrastructure evaluation; not an agent submission.'})
            raise PreparedBoundary()

    runner = PrepareRunner(workspace_root=WORKSPACE, milestone_id='M06', srs_path=WORKSPACE / 'srs/M06/SRS.md',
        output_dir=PREPARED, image_name=config['benchmark']['skill_runtime_image_id'], agent_name='codex',
        agent_version='0.163.0', model=config['codex']['model'], reasoning_effort='high', main_branch='main',
        keep_container=True, trial_name='scikit_preflight_common_base', max_retries=1)
    try:
        runner.run()
    except PreparedBoundary:
        print('Common source prepared and quarantined; zero model calls.')
    else:
        raise RuntimeError('Preflight must stop before inference')


def grade_base():
    from harness.e2e.evaluator import PatchEvaluator
    output = ROOT / 'results/scikit_preflight/base_grader'
    output.mkdir(parents=True, exist_ok=False)
    evaluator = PatchEvaluator(workspace_root=WORKSPACE, milestone_id='M06',
        patch_file=PREPARED / 'evaluation/source_snapshot.tar',
        baseline_classification=WORKSPACE / 'test_results/M06/M06_classification.json', output_dir=output,
        repo_config_path=PREPARED / 'repo_config.yaml',
        repo_config_sha256=hashlib.sha256((PREPARED / 'repo_config.yaml').read_bytes()).hexdigest(),
        runtime_policy_path=PREPARED / 'runtime_policy.yaml',
        runtime_policy_sha256=hashlib.sha256((PREPARED / 'runtime_policy.yaml').read_bytes()).hexdigest(),
        runtime_policy_mode='protected')
    result = evaluator.evaluate().to_dict()
    save(output / 'evaluation_result.json', result)
    valid = not result.get('infra_invalid') and bool(result.get('test_summary', {}).get('total'))
    save(ROOT / 'reports/scikit_grader_preflight.json', {'valid': valid, 'model_calls': 0,
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
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    prepare_base() if args.prepare_base else grade_base()


if __name__ == '__main__':
    main()
