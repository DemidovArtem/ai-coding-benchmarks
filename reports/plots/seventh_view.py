"""Append seventh observations after the frozen fourth-through-sixth view."""

from experiment.curves import QUALITY, TOKENS, summarize
from reports.plots.extension_view import append_fourth


def append_seventh(view, rows):
    result = append_fourth(view, [r for r in rows if (r.get('continuous') or {}).get('step') != 7])
    by_id = {row['trial_id']: row for row in rows}
    groups = {}
    seen = set()
    sources = []
    for row in rows:
        if (row.get('continuous') or {}).get('step') != 7:
            continue
        link = row.get('extension')
        if (not link or row.get('trial_state') != 'finished' or row.get('collection_errors')
                or row.get('failure_category')
                or row.get('sonar', {}).get('analysis_ok') is not True):
            continue
        step = row['continuous']['step']
        expected_task = {7:'milestone_seed_292bc54_1'}.get(step)
        parent = by_id[link['parent_trial']]
        prefix = [by_id[name] for name in link['prefix_trials']]
        if ([r['continuous']['step'] for r in prefix] != list(range(1,step))
                or prefix[-1]['trial_id'] != parent['trial_id']
                or expected_task is None or row['milestone_id'] != expected_task
                or row['continuous']['input_commit'] != parent['ending_commit']):
            raise ValueError('Seventh observation has an invalid source prefix')
        for previous in prefix:
            if (previous['variant'] != row['variant'] or previous['repetition'] != row['repetition']
                    or previous['starting_tree'] != row['starting_tree']
                    or previous['continuous']['executor_session_id'] != row['continuous']['executor_session_id']):
                raise ValueError('Seventh observation differs from its parent trajectory')
        key = (row['variant'], row['repetition'],step)
        if key in seen:
            raise ValueError('Duplicate seventh observation for one independent repetition')
        seen.add(key)
        values = {name: row.get(name) for name in ('churn_prod_loc', 'net_prod_loc', 'added_prod_loc', 'deleted_prod_loc')}
        for name in TOKENS:
            counts = [previous['usage']['total'].get(name) for previous in prefix + [row]]
            values[name] = sum(counts) if all(value is not None for value in counts) else None
            reported = row['usage'].get('executor_cumulative', {}).get(name)
            if reported is not None and values[name] is not None and reported != values[name]:
                raise ValueError('Seventh native cumulative counter differs from linked steps')
        values['uncached_input_tokens'] = (values['input_tokens'] - values['cached_input_tokens']
            if values['input_tokens'] is not None and values['cached_input_tokens'] is not None else None)
        values['model_seconds'] = None
        for name in QUALITY:
            values['sonar_delta_' + name] = ((row['sonar'].get('delta_vs_common_base') or {}).get(name)
                if row['sonar'].get('common_base_comparison_verified') is True else None)
        values['grader_acceptance'] = int(row['resolved']) if type(row.get('resolved')) is bool else None
        groups.setdefault((row['variant'],step), []).append((row, values))
        sources.append({'trial_id': row['trial_id'], 'parent_trial': parent['trial_id'],
                        'setup_fingerprint': row['setup_fingerprint'],
                        'new_inference_executed': link['new_inference_executed'],
                        'step':step, 'grading_state':row.get('grading_state'),
                        'prefix_recounted_as_new_repetitions': False,
                        'inherited_context_deviations':link.get('inherited_context_deviations',[])})
    for (variant,step), observations in groups.items():
        fingerprints = {row['setup_fingerprint'] for row, _ in observations}
        if len(fingerprints) != 1:
            raise ValueError('Seventh-step conditions differ within one approach')
        fields = observations[0][1]
        result['points'].append({'setup_fingerprint': next(iter(fingerprints)), 'variant': variant,
            'step':step, 'milestone_id':observations[0][0]['milestone_id'], 'n_trajectories': len(observations),
            'trial_ids': [row['trial_id'] for row, _ in observations],
            'metrics': {field: summarize([values[field] for _, values in observations]) for field in fields},
            'paired_delta': {field: summarize([]) for field in fields}})
    result['extension_sources'] = result.get('extension_sources', []) + sources
    for step,task in ((7,'milestone_seed_292bc54_1'),):
        if any(p['step']==step for p in sources) and task not in result.get('milestones', []):
            result.setdefault('milestones', []).append(task)
    result['extension_interpretation'] = ('Steps four through seven continue their linked source/session prefixes. '
        'Previous scores remain frozen; seventh grading uses the original JSON replacement task. '
        'Ponytail repetition two retains its explicitly documented sixth-step context amendment.')
    return result
