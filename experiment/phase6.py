"""Run the authorized two-round, five-edit matrix with isolated trajectories."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from experiment.collect import sonar_result
from experiment.continuous import check_resources, run, verify_images
from experiment.curves import aggregate
from experiment.quota import read_quota
from experiment.report import export
from experiment.runner import ROOT, check_quota, save, trial_lock, validate
from experiment.sonar_scan import scan
from experiment.status import main as refresh_status

ORDER = ('serena', 'baseline', 'caveman', 'ponytail')


def schedule():
    return [(variant, repetition, f'phase6_{variant}_r{repetition:02d}')
            for repetition in (1, 2) for variant in ORDER]


def analyze(record):
    directory = ROOT / 'results/trials' / record['trial_id']
    output = directory / 'sonar'
    if not output.exists():
        scan(directory, output, ROOT / 'results/sonar/private/credentials.json', 'solution')
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    row = next(row for row in rows if row['trial_id'] == record['trial_id'])
    row['sonar'] = sonar_result(directory, row, ROOT / 'results/sonar/common_base')
    row['durations_seconds']['sonar'] = row['sonar'].get('duration_seconds')
    export(rows, ROOT / 'results')
    save(ROOT / 'reports' / (record['trial_id'] + '.json'), row)
    save(ROOT / 'reports/plots/mean_data.json', aggregate(rows))
    refresh_status()
    subprocess.run([sys.executable, str(ROOT / 'reports/plots/export_patches.py')], cwd=ROOT, check=True)
    # Plotting uses an existing host-only environment, never the measured container runtime.
    plotting = Path('/tmp/ai-coding-charts/bin/python')
    if plotting.exists():
        subprocess.run([str(plotting), str(ROOT / 'reports/plots/mean_curves.py')], cwd=ROOT, check=True,
                       env={**os.environ, 'MPLCONFIGDIR': '/tmp/ai-coding-charts/mpl'})
    print('STEP_COLLECTED', record['trial_id'], 'resolved=', row['resolved'], 'sonar=', row['sonar']['analysis_ok'], flush=True)
    if row['sonar']['analysis_ok'] is not True:
        raise RuntimeError('Sonar analysis failed; subsequent inference is withheld')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'reports/phase6_experiment.json')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = json.loads(args.config.read_text())
    if config.get('stage') != 'phase6_frozen' or config['variants'] != list(ORDER):
        raise ValueError('The frozen four-workflow matrix is required')
    for variant, repetition, chain in schedule():
        plan = json.loads((ROOT / 'reports/continuous_feasibility.json').read_text())
        progress = next(row for row in plan['pilot_runs'] if row['trial_id'] == chain)
        if progress['state'] == 'finished':
            continue
        if progress['state'] != 'planned':
            raise RuntimeError('An interrupted trajectory requires explicit recovery; no silent rerun: ' + chain)
        validate(config)
        verify_images(config)
        check_resources(config)
        check_quota(read_quota(), config['resources']['quota_stop_percent'])
        print('START', chain, flush=True)
        lock = trial_lock(Path(config['resources']['runtime_root']))
        try:
            run(config, variant, repetition, chain, on_step=analyze)
        finally:
            lock.close()
        print('DONE', chain, flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
