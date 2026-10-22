"""Display the matched task prefix together while preserving each source mean."""

from experiment.runner import setup_fingerprint


def comparison_view(data, current, serena):
    tasks = current['benchmark']['continuous_pilot']['milestones']
    if tasks != serena['benchmark']['continuous_pilot']['milestones'][:len(tasks)]:
        raise ValueError('The displayed workflows must have the same task prefix')
    for field in ('model', 'reasoning_effort', 'version'):
        if current['codex'][field] != serena['codex'][field]:
            raise ValueError('Comparison model/effort/CLI differ: ' + field)
    for field in ('common_starting_tree', 'runtime_policy_root', 'grading_policy'):
        if current['benchmark'].get(field) != serena['benchmark'].get(field):
            raise ValueError('Comparison source/grading/quarantine differ: ' + field)
    configs = {variant: current for variant in ('baseline', 'caveman', 'ponytail')}
    configs['serena'] = serena
    sources = {variant: {'setup_fingerprint': setup_fingerprint(config)[0],
                        'image_id': config['benchmark']['skill_runtime_image_id']}
               for variant, config in configs.items()}
    points = []
    for point in data['points']:
        source = sources.get(point['variant'])
        if not source or point['setup_fingerprint'] != source['setup_fingerprint']:
            continue
        if not 1 <= point['step'] <= len(tasks):
            continue
        if point['milestone_id'] != tasks[point['step'] - 1]:
            raise ValueError('Displayed step has a different milestone')
        points.append(point)
    return {'points': points, 'sources': sources, 'milestones': tasks,
            'interpretation': 'Descriptive overlay of the same task prefix. Each line retains its original within-cohort repeat mean and range. Runtime image IDs differ; this view does not pool cohorts or create cross-cohort paired baseline deltas.'}
