import unittest

from experiment.phase6e import grading_state, verify_restored


class FifthContinuationTests(unittest.TestCase):
    def test_only_known_grader_compile_failure_is_nonfatal(self):
        raw={'error_message':'error[E0599]: no method named `max_matches` found'}
        self.assertFalse(grading_state(raw)['valid'])
        with self.assertRaises(RuntimeError):grading_state({'error_message':'different compiler error'})
        with self.assertRaises(RuntimeError):grading_state({'test_summary':{'total':0}})
        self.assertTrue(grading_state({'test_summary':{'total':10},'residue_prune':{'enabled':True}})['valid'])

    def test_history_keeps_failed_prior_turn_but_rejects_live_or_missing_turn(self):
        response={'result':{'data':[{'id':'first','status':'completed'},
                                    {'id':'quota','status':'failed'},
                                    {'id':'fourth','status':'completed'}]}}
        self.assertEqual(len(verify_restored(response,['first','quota','fourth'])),3)
        with self.assertRaises(ValueError):verify_restored(response,['first','fourth'])
        response['result']['data'][-1]['status']='inProgress'
        with self.assertRaises(ValueError):verify_restored(response,['first','quota','fourth'])
