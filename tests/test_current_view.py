import copy
import unittest

from experiment.runner import setup_fingerprint
from reports.plots.current_view import comparison_view


def config(image, tasks):
    return {'codex': {'model': 'model', 'reasoning_effort': 'high', 'version': 'version'},
            'benchmark': {'continuous_pilot': {'milestones': tasks},
                          'common_starting_tree': 'tree', 'skill_runtime_image_id': image},
            'pins': {}}


class CurrentComparisonTests(unittest.TestCase):
    def test_overlay_preserves_source_means_and_does_not_invent_missing_workflows(self):
        current = config('offline', ['one', 'two', 'three'])
        serena = config('original', ['one', 'two', 'three', 'four'])
        def point(variant, source, step, mean, n):
            return {'variant': variant, 'setup_fingerprint': setup_fingerprint(source)[0],
                    'step': step, 'milestone_id': source['benchmark']['continuous_pilot']['milestones'][step-1],
                    'metrics': {'output_tokens': {'mean': mean, 'n': n}}}
        data = {'points': [point('baseline', current, 1, 10, 2),
                           point('serena', serena, 1, 17, 1),
                           point('serena', serena, 4, 999, 1),
                           point('baseline', serena, 1, 999, 3)]}
        original = copy.deepcopy(data)
        view = comparison_view(data, current, serena)
        self.assertEqual([(p['variant'], p['metrics']['output_tokens']) for p in view['points']],
                         [('baseline', {'mean': 10, 'n': 2}), ('serena', {'mean': 17, 'n': 1})])
        self.assertEqual(data, original)
        self.assertEqual(len(view['sources']), 4)

    def test_different_tasks_or_models_are_rejected(self):
        current = config('offline', ['one', 'two', 'three'])
        for different in (config('original', ['one', 'other', 'three']),
                          config('original', ['one', 'two', 'three'])):
            if different['benchmark']['continuous_pilot']['milestones'][1] == 'two':
                different['codex']['model'] = 'other'
            with self.assertRaises(ValueError):
                comparison_view({'points': []}, current, different)

    def test_wrong_milestone_in_a_selected_source_is_rejected(self):
        current = config('offline', ['one'])
        with self.assertRaises(ValueError):
            comparison_view({'points': [{'variant': 'baseline', 'setup_fingerprint': setup_fingerprint(current)[0],
                                         'step': 1, 'milestone_id': 'other'}]}, current, config('original', ['one']))
