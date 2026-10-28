import unittest
from experiment.phase6f_serena_resume import validate_failure


class SerenaSixthRecoveryTests(unittest.TestCase):
    def test_completed_unsubmitted_semantic_stop_requires_recorded_error(self):
        failed={'trial_state':'failed','ending_commit':None,'variant':'serena','repetition':1,
                'continuous':{'step':6},'failure_category':'continuation_failure'}
        events=[{'type':'item.completed','item':{'type':'agent_message','text':
                 "No symbol matching the requested symbol found; no commit or submission tag."}},
                {'type':'turn.completed','usage':{'output_tokens':5}}]
        validate_failure(failed,events)
        with self.assertRaises(ValueError):validate_failure(failed,events[:-1])
        failed['ending_commit']='already-submitted'
        with self.assertRaises(ValueError):validate_failure(failed,events)

    def test_other_method_or_unverified_stop_cannot_use_this_recovery(self):
        failed={'trial_state':'failed','ending_commit':None,'variant':'serena','repetition':1,
                'continuous':{'step':6},'failure_category':'continuation_failure'}
        with self.assertRaises(ValueError):validate_failure(failed,[{'type':'turn.completed'}])
        failed['variant']='baseline'
        with self.assertRaises(ValueError):validate_failure(failed,[])
