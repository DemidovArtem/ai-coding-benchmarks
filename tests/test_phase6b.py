import unittest

from experiment.phase6b import schedule, verify_grading_policy


class RepairedMatrixTests(unittest.TestCase):
    def test_two_independent_rounds_put_baseline_first(self):
        runs = schedule()
        self.assertEqual(len({chain for _, _, chain in runs}), 8)
        self.assertEqual([round for _, round, _ in runs], [1] * 4 + [2] * 4)
        self.assertEqual([variant for variant, _, _ in runs[:4]], ['baseline', 'caveman', 'ponytail', 'serena'])

    def test_grader_must_record_the_actual_pruning_policy(self):
        with self.assertRaises(RuntimeError):
            verify_grading_policy({'grader_metrics': {'residue_prune': {'enabled': False}}})
        with self.assertRaises(RuntimeError):
            verify_grading_policy({'grader_metrics': {'residue_prune': {'enabled': True}}})
        verify_grading_policy({'grader_metrics': {'residue_prune': {
            'enabled': True, 'enablement_source': 'environment-override'}}})
