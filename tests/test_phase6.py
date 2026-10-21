import unittest

from experiment.phase6 import schedule


class Phase6Tests(unittest.TestCase):
    def test_second_round_starts_only_after_all_four_first_round_trajectories(self):
        runs=schedule()
        self.assertEqual(len(runs),8)
        self.assertEqual([repetition for _,repetition,_ in runs],[1]*4+[2]*4)
        self.assertEqual({variant for variant,_,_ in runs},{'baseline','serena','caveman','ponytail'})
        self.assertEqual(len({chain for _,_,chain in runs}),8)
