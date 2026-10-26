"""Append linked fourth observations without re-counting their measured prefixes."""

import copy

from experiment.curves import QUALITY, TOKENS, summarize


def append_fourth(view, rows):
    result = copy.deepcopy(view)
    by_id = {row['trial_id']: row for row in rows}
    groups = {}
    seen = set()
    sources = []
    for row in rows:
        link = row.get('extension')
        if (not link or row.get('trial_state') != 'finished' or row.get('collection_errors')
                or row.get('failure_category') or row.get('sonar', {}).get('analysis_ok') is not True):
            continue
        parent = by_id[link['parent_trial']]
        prefix = [by_id[name] for name in link['prefix_trials']]
        if ([r['continuous']['step'] for r in prefix] != [1, 2, 3]
                or prefix[-1]['trial_id'] != parent['trial_id']
                or row['continuous']['step'] != 4
                or row['milestone_id'] != 'milestone_seed_b610d1c_1'
                or row['continuous']['input_commit'] != parent['ending_commit']):
            raise ValueError('Fourth observation has an invalid source prefix')
        for previous in prefix:
            if (previous['variant'] != row['variant'] or previous['repetition'] != row['repetition']
                    or previous['starting_tree'] != row['starting_tree']
                    or previous['continuous']['executor_session_id'] != row['continuous']['executor_session_id']):
                raise ValueError('Fourth observation differs from its parent trajectory')
        key = (row['variant'], row['repetition'])
        if key in seen:
            raise ValueError('Duplicate fourth observation for one independent repetition')
        seen.add(key)
        values = {name: row.get(name) for name in ('churn_prod_loc', 'net_prod_loc', 'added_prod_loc', 'deleted_prod_loc')}
        for name in TOKENS:
            counts = [previous['usage']['total'].get(name) for previous in prefix + [row]]
            values[name] = sum(counts) if all(value is not None for value in counts) else None
            reported = row['usage'].get('executor_cumulative', {}).get(name)
            if reported is not None and values[name] is not None and reported != values[name]:
                raise ValueError('Fourth native cumulative counter differs from linked steps')
        values['uncached_input_tokens'] = (values['input_tokens'] - values['cached_input_tokens']
            if values['input_tokens'] is not None and values['cached_input_tokens'] is not None else None)
        values['model_seconds'] = None
        for name in QUALITY:
            values['sonar_delta_' + name] = ((row['sonar'].get('delta_vs_common_base') or {}).get(name)
                if row['sonar'].get('common_base_comparison_verified') is True else None)
        values['grader_acceptance'] = int(row['resolved']) if type(row.get('resolved')) is bool else None
        groups.setdefault(row['variant'], []).append((row, values))
        sources.append({'trial_id': row['trial_id'], 'parent_trial': parent['trial_id'],
                        'setup_fingerprint': row['setup_fingerprint'],
                        'new_inference_executed': link['new_inference_executed'],
                        'prefix_recounted_as_new_repetitions': False})
    for variant, observations in groups.items():
        fingerprints = {row['setup_fingerprint'] for row, _ in observations}
        if len(fingerprints) != 1:
            raise ValueError('Fourth-step conditions differ within one approach')
        fields = observations[0][1]
        result['points'].append({'setup_fingerprint': next(iter(fingerprints)), 'variant': variant,
            'step': 4, 'milestone_id': 'milestone_seed_b610d1c_1', 'n_trajectories': len(observations),
            'trial_ids': [row['trial_id'] for row, _ in observations],
            'metrics': {field: summarize([values[field] for _, values in observations]) for field in fields},
            'paired_delta': {field: summarize([]) for field in fields}})
    result['extension_sources'] = sources
    if sources and 'milestone_seed_b610d1c_1' not in result.get('milestones', []):
        result.setdefault('milestones', []).append('milestone_seed_b610d1c_1')
    result['extension_interpretation'] = ('Fourth points continue their explicitly linked source/session prefixes. '
        'The fourth grader enables source-residue pruning; old scores remain frozen. '
        'Serena reuses its previously submitted fourth source, not another independent model run.')
    return result
