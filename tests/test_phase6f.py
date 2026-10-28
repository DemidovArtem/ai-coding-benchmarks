import copy
import unittest
from unittest.mock import patch

from experiment.phase6f import grading_state, prefix_rows


class SixthContinuationTests(unittest.TestCase):
    def test_sixth_grader_requires_actual_reports_and_never_excuses_fifth_error(self):
        self.assertTrue(grading_state({'test_summary':{'total':3},'residue_prune':{'enabled':True}})['valid'])
        for raw in ({'error_message':'error[E0599]: no method named max_matches'},
                    {'test_summary':{'total':0},'residue_prune':{'enabled':True}},
                    {'test_summary':{'total':3},'residue_prune':{'enabled':False}},
                    {'test_summary':{'total':3},'residue_prune':{'enabled':True},'infra_invalid':True}):
            with self.assertRaises(RuntimeError):grading_state(raw)

    def test_exact_five_step_same_session_prefix_required(self):
        rows=[{'trial_id':f't{s}','variant':'serena','repetition':1,'trial_state':'finished',
               'collection_errors':[],'sonar':{'analysis_ok':True},'ending_commit':f'c{s}',
               'continuous':{'step':s,'executor_session_id':'retained'}} for s in range(1,6)]
        rows[-1]['extension']={'prefix_trials':['t1','t2','t3','t4']}
        checkpoint={'ending_commit':'c5','variant':'serena','repetition':1,'session_id':'retained'}
        def read(path):return next(r for r in rows if r['trial_id']==path.stem)
        with patch('experiment.phase6f.load',side_effect=read):
            self.assertEqual(len(prefix_rows(rows[-1],checkpoint)),5)
            rows[1]['continuous']['executor_session_id']='another-repeat'
            with self.assertRaises(ValueError):prefix_rows(rows[-1],checkpoint)
            rows[1]['continuous']['executor_session_id']='retained'
            parent=copy.deepcopy(rows[-1]);parent['extension']['prefix_trials']=['t1','t2','t4']
            with self.assertRaises(ValueError):prefix_rows(parent,checkpoint)
