import unittest

from experiment.phase6 import schedule


class Phase6Tests(unittest.TestCase):
    def test_second_round_starts_only_after_all_four_first_round_trajectories(self):
        runs=schedule()
        self.assertEqual(len(runs),8)
        self.assertEqual([repetition for _,repetition,_ in runs],[1]*4+[2]*4)
        self.assertEqual({variant for variant,_,_ in runs},{'baseline','serena','caveman','ponytail'})
        self.assertEqual(len({chain for _,_,chain in runs}),8)

    def test_three_edit_scope_excludes_serena_and_keeps_independent_rounds(self):
        config = {'variants': ['baseline', 'caveman', 'ponytail'], 'benchmark': {
            'continuous_pilot': {'cohort': 'phase6c', 'repetitions': 2}}}
        runs = schedule(config)
        self.assertEqual(runs[:3], [('baseline', 1, 'phase6c_baseline_r01'),
                                   ('caveman', 1, 'phase6c_caveman_r01'),
                                   ('ponytail', 1, 'phase6c_ponytail_r01')])
        self.assertEqual([repeat for _, repeat, _ in runs], [1, 1, 1, 2, 2, 2])
        self.assertEqual(len({chain for _, _, chain in runs}), 6)
