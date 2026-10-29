import unittest
from experiment.phase6f_ponytail_resume import validate_failure

class EncryptedHistoryRetryTests(unittest.TestCase):
    def test_retry_only_before_model_work_and_without_submission(self):
        row = {'trial_state': 'failed', 'ending_commit': None, 'variant': 'ponytail',
               'repetition': 2, 'continuous': {'step': 6}, 'failure_category': 'continuation_failure'}
        events = [{'type': 'turn.failed', 'error': {'message': 'invalid_encrypted_content'}}]
        validate_failure(row, events + [{'type': 'item.completed', 'item': {'type': 'error'}}])
        for extra in ('item.started', 'item.completed', 'turn.completed'):
            with self.assertRaises(ValueError):
                validate_failure(row, events + [{'type': extra}])
        row['ending_commit'] = 'submitted'
        with self.assertRaises(ValueError):
            validate_failure(row, events)
        row['ending_commit'] = None
        with self.assertRaises(ValueError):
            validate_failure(row, [{'type': 'turn.failed', 'error': {'message': 'usage limit'}}])
