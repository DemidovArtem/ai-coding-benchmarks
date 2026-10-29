import copy
import unittest
from unittest.mock import patch

from experiment.phase6g import grading_state, prefix_rows, require_ready


class SeventhContinuationTests(unittest.TestCase):
    def test_seventh_grader_requires_actual_reports_and_never_excuses_sixth_error(self):
        self.assertTrue(grading_state({'test_summary':{'total':3},'residue_prune':{'enabled':True}})['valid'])
        for raw in ({'error_message':'error[E0599]: no method named max_matches'},
                    {'test_summary':{'total':0},'residue_prune':{'enabled':True}},
                    {'test_summary':{'total':3},'residue_prune':{'enabled':False}},
                    {'test_summary':{'total':3},'residue_prune':{'enabled':True},'infra_invalid':True}):
            with self.assertRaises(RuntimeError):grading_state(raw)

    def test_exact_six_step_same_session_prefix_required(self):
        rows=[{'trial_id':f't{s}','variant':'serena','repetition':1,'trial_state':'finished',
               'collection_errors':[],'sonar':{'analysis_ok':True},'ending_commit':f'c{s}',
               'continuous':{'step':s,'executor_session_id':'retained'}} for s in range(1,7)]
        rows[-1]['extension']={'prefix_trials':['t1','t2','t3','t4','t5']}
        checkpoint={'ending_commit':'c6','variant':'serena','repetition':1,'session_id':'retained'}
        def read(path):return next(r for r in rows if r['trial_id']==path.stem)
        with patch('experiment.phase6g.load',side_effect=read):
            self.assertEqual(len(prefix_rows(rows[-1],checkpoint)),6)
            rows[1]['continuous']['executor_session_id']='another-repeat'
            with self.assertRaises(ValueError):prefix_rows(rows[-1],checkpoint)
            rows[1]['continuous']['executor_session_id']='retained'
            parent=copy.deepcopy(rows[-1]);parent['extension']['prefix_trials']=['t1','t2','t4']
            with self.assertRaises(ValueError):prefix_rows(parent,checkpoint)


class SeventhAuthorizationTests(unittest.TestCase):
    def test_preparation_or_missing_either_approval_stops_before_inference(self):
        config={'stage':'phase6g_frozen','measurement_started':True}
        budget={'download_authorized':True,'task_choice_authorized':True}
        require_ready(config,budget)
        for field in budget:
            with self.assertRaises(RuntimeError): require_ready(config,{**budget,field:False})
        with self.assertRaises(RuntimeError): require_ready({**config,'stage':'phase6g_preparing'},budget)
        with self.assertRaises(RuntimeError): require_ready({**config,'measurement_started':False},budget)
