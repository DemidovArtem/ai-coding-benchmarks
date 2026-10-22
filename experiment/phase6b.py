"""Run a separately frozen matrix with upstream source-residue pruning enabled."""

import argparse
import json
import os
from pathlib import Path

from experiment.continuous import check_resources, run, verify_images
from experiment.phase6 import analyze
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, trial_lock, validate

ORDER = ('baseline', 'caveman', 'ponytail', 'serena')


def schedule():
    return [(variant, repetition, f'phase6b_{variant}_r{repetition:02d}')
            for repetition in (1, 2) for variant in ORDER]


def verify_grading_policy(record):
    policy = record.get('grader_metrics', {}).get('residue_prune', {})
    if policy.get('enabled') is not True or policy.get('enablement_source') != 'environment-override':
        raise RuntimeError('The explicit upstream pruning policy was not observed in the grader result')


def analyze_step(record):
    verify_grading_policy(record)
    analyze(record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'reports/phase6b_experiment.json')
    args = parser.parse_args()
    import sys
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = json.loads(args.config.read_text())
    if (config.get('stage') != 'phase6b_frozen' or config['variants'] != list(ORDER)
            or config['benchmark'].get('grading_policy', {}).get('residue_prune') is not True):
        raise ValueError('The separately frozen pruning-enabled matrix is required')
    preflight = json.loads((ROOT / config['benchmark']['grading_policy']['compatibility_preflight']).read_text())
    if preflight.get('ready') is not True:
        raise ValueError('Zero-model grading compatibility preflight has not passed')
    os.environ['SWE_MILESTONE_RESIDUE_PRUNE'] = '1'
    for variant, repetition, chain in schedule():
        plan = json.loads((ROOT / 'reports/continuous_feasibility.json').read_text())
        progress = next(row for row in plan['pilot_runs'] if row['trial_id'] == chain)
        if progress['state'] == 'finished':
            continue
        if progress['state'] != 'planned':
            raise RuntimeError('Interrupted trajectories require explicit recovery: ' + chain)
        validate(config)
        verify_images(config)
        check_resources(config)
        check_quota(read_quota(), config['resources']['quota_stop_percent'])
        print('START', chain, flush=True)
        lock = trial_lock(Path(config['resources']['runtime_root']))
        try:
            run(config, variant, repetition, chain, on_step=analyze_step)
        finally:
            lock.close()
        print('DONE', chain, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
