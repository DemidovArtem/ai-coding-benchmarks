"""Average independent repetitions at each edit count without merging cohorts."""

import statistics

VARIANTS = ('baseline', 'caveman', 'ponytail')
TOKENS = ('input_tokens', 'cached_input_tokens', 'output_tokens')
QUALITY = ('ncloc', 'complexity', 'cognitive_complexity', 'duplicated_lines',
           'software_quality_maintainability_issues',
           'software_quality_maintainability_remediation_effort')


def summarize(values):
    values = [value for value in values if value is not None]
    return {'n': len(values), 'mean': statistics.mean(values) if values else None,
            'min': min(values) if values else None, 'max': max(values) if values else None,
            'sd': statistics.stdev(values) if len(values) > 1 else None}


def aggregate(rows):
    """Keep missing metrics missing and each trajectory's cumulative counters separate."""
    trajectories = {}
    excluded = []
    for row in rows:
        continuous = row.get('continuous') or {}
        if row.get('variant') not in VARIANTS or not continuous.get('trajectory_id'):
            continue
        if row.get('trial_state') != 'finished' or row.get('collection_errors') or row.get('failure_category'):
            excluded.append(row['trial_id'])
            continue
        key = (row['setup_fingerprint'], row['variant'], continuous['trajectory_id'])
        trajectories.setdefault(key, []).append(row)
    groups, observations = {}, []
    for (fingerprint, variant, trajectory), steps in trajectories.items():
        steps.sort(key=lambda row: row['continuous']['step'])
        if [row['continuous']['step'] for row in steps] != list(range(1, len(steps) + 1)):
            raise ValueError('Trajectory has a duplicate or missing step: ' + trajectory)
        identities = {(row['repo'], row['starting_tree'], row['model'], row['reasoning_effort'],
                       row['dataset_version'], row['repetition']) for row in steps}
        if len(identities) != 1:
            raise ValueError('Trajectory measurement conditions changed: ' + trajectory)
        for index, row in enumerate(steps, 1):
            values = {key: row.get(key) for key in ('churn_prod_loc', 'net_prod_loc', 'added_prod_loc', 'deleted_prod_loc')}
            for field in TOKENS:
                counts = [step['usage']['total'].get(field) for step in steps[:index]]
                values[field] = sum(counts) if all(value is not None for value in counts) else None
            values['uncached_input_tokens'] = (values['input_tokens'] - values['cached_input_tokens']
                if values['input_tokens'] is not None and values['cached_input_tokens'] is not None else None)
            durations = [step.get('durations_seconds', {}).get(phase) for step in steps[:index]
                         for phase in ('planner', 'executor')]
            values['model_seconds'] = sum(durations) if all(value is not None for value in durations) else None
            sonar = row.get('sonar') or {}
            for field in QUALITY:
                values['sonar_delta_' + field] = ((sonar.get('delta_vs_common_base') or {}).get(field)
                    if sonar.get('analysis_ok') is True and sonar.get('common_base_comparison_verified') is True else None)
            values['grader_acceptance'] = int(row['resolved']) if type(row.get('resolved')) is bool else None
            observation = {'setup_fingerprint': fingerprint, 'variant': variant, 'trajectory': trajectory,
                           'repetition': row['repetition'], 'step': index, 'trial_id': row['trial_id'],
                           'milestone_id': row['milestone_id'], 'values': values}
            observations.append(observation)
            groups.setdefault((fingerprint, variant, index, row['milestone_id']), []).append(observation)
    points = []
    baselines = {(r['setup_fingerprint'], r['repetition'], r['step'], r['milestone_id']): r
                 for r in observations if r['variant'] == 'baseline'}
    if len(baselines) != sum(r['variant'] == 'baseline' for r in observations):
        raise ValueError('Ambiguous baseline repetition; assign a distinct repetition before averaging')
    for (fingerprint, variant, step, milestone), records in sorted(groups.items()):
        paired = []
        for record in records:
            base = baselines.get((fingerprint, record['repetition'], step, milestone))
            if base is not None:
                paired.append({key: record['values'][key] - base['values'][key]
                    if record['values'][key] is not None and base['values'][key] is not None else None
                    for key in record['values']})
        points.append({'setup_fingerprint': fingerprint, 'variant': variant, 'step': step,
                       'milestone_id': milestone, 'n_trajectories': len(records),
                       'trial_ids': [r['trial_id'] for r in records],
                       'metrics': {key: summarize([r['values'][key] for r in records]) for key in records[0]['values']},
                       'paired_delta': {key: summarize([r[key] for r in paired]) for key in records[0]['values']}})
    return {'points': points, 'observations': observations, 'excluded_trials': excluded,
            'aggregation': 'Arithmetic mean at each edit count within one frozen cohort; range is min–max, not a confidence interval.'}
