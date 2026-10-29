import unittest
from experiment.phase6f_baseline_resume import validate_failure


class BaselineSixthRecoveryTests(unittest.TestCase):
    def test_only_unsubmitted_second_baseline_quota_failure_may_resume(self):
        failed={'trial_state':'failed','ending_commit':None,'variant':'baseline','repetition':2,
                'continuous':{'step':6},'failure_category':'quota_pressure'}
        events=[{'type':'turn.failed','error':{'message':'You have hit your usage limit'}}]
        validate_failure(failed,events)
        with self.assertRaises(ValueError):validate_failure(failed,events+[{'type':'turn.completed'}])
        failed['repetition']=1
        with self.assertRaises(ValueError):validate_failure(failed,events)
