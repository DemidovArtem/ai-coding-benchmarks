import copy
import unittest

from reports.plots.extension_view import append_fourth


def fixtures():
    rows=[]
    for step in range(1,5):
        tokens={'output_tokens':10*step,'input_tokens':20*step,'cached_input_tokens':10*step}
        rows.append({'trial_id':f't{step}','variant':'baseline','repetition':1,'starting_tree':'same-tree',
            'ending_commit':f'c{step}','setup_fingerprint':'old' if step<4 else 'new',
            'trial_state':'finished','collection_errors':[], 'resolved':False,
            'milestone_id':'milestone_seed_b610d1c_1' if step==4 else f'task{step}',
            'continuous':{'step':step,'executor_session_id':'same-session','input_commit':f'c{step-1}'},
            'usage':{'total':tokens,'executor_cumulative':{'output_tokens':100,'input_tokens':200,'cached_input_tokens':100}},
            'churn_prod_loc':100+step,'net_prod_loc':step,
            'sonar':{'analysis_ok':True,'common_base_comparison_verified':True,
                     'delta_vs_common_base':{'cognitive_complexity':2}}})
    rows[-1]['extension']={'parent_trial':'t3','prefix_trials':['t1','t2','t3'],'new_inference_executed':True}
    return {'points':[{'variant':'baseline','step':3,'n_trajectories':2}],'milestones':['task1','task2','task3']},rows


class ExtensionViewTests(unittest.TestCase):
    def test_prefix_is_not_recounted_and_tokens_accumulate(self):
        view,rows=fixtures();saved=copy.deepcopy(view)
        result=append_fourth(view,rows)
        self.assertEqual(view,saved)
        self.assertEqual(result['points'][0],saved['points'][0])
        fourth=result['points'][1]
        self.assertEqual(fourth['n_trajectories'],1)
        self.assertEqual(fourth['metrics']['output_tokens']['mean'],100)
        self.assertEqual(fourth['metrics']['churn_prod_loc']['mean'],104)
        self.assertEqual(fourth['metrics']['grader_acceptance']['mean'],0)

    def test_duplicate_independent_repetition_rejected(self):
        view,rows=fixtures();duplicate=copy.deepcopy(rows[-1]);duplicate['trial_id']='duplicate'
        with self.assertRaises(ValueError):append_fourth(view,rows+[duplicate])

    def test_changed_context_and_reset_counters_rejected(self):
        view,rows=fixtures();rows[-1]['continuous']['executor_session_id']='new-session'
        with self.assertRaises(ValueError):append_fourth(view,rows)
        view,rows=fixtures();rows[-1]['usage']['executor_cumulative']['output_tokens']=40
        with self.assertRaises(ValueError):append_fourth(view,rows)

    def test_pending_quality_does_not_invent_fourth_point(self):
        view,rows=fixtures();rows[-1]['sonar']['analysis_ok']=None
        self.assertEqual(append_fourth(view,rows)['points'],view['points'])

    def test_unverified_common_base_delta_stays_missing(self):
        view,rows=fixtures();rows[-1]['sonar']['common_base_comparison_verified']=False
        metric=append_fourth(view,rows)['points'][-1]['metrics']['sonar_delta_cognitive_complexity']
        self.assertIsNone(metric['mean'])
        self.assertEqual(metric['n'],0)

    def test_fifth_source_metrics_survive_known_invalid_grader(self):
        view,rows=fixtures()
        fifth=copy.deepcopy(rows[-1])
        fifth.update(trial_id='t5',ending_commit='c5',milestone_id='milestone_seed_8c6595c_1',
                     setup_fingerprint='fifth',failure_category='grader_infrastructure',
                     grading_state={'valid':False,'reason':'known_undeclared_max_matches_dependency'})
        fifth['continuous'].update(step=5,input_commit='c4')
        fifth['extension'].update(parent_trial='t4',prefix_trials=['t1','t2','t3','t4'])
        fifth['usage']['executor_cumulative'].update(output_tokens=140,input_tokens=280,cached_input_tokens=140)
        result=append_fourth(view,rows+[fifth])
        fourth=next(p for p in result['points'] if p['step']==4)
        fifth_point=next(p for p in result['points'] if p['step']==5)
        self.assertEqual(fourth['metrics']['output_tokens']['mean'],100)
        self.assertEqual(fifth_point['metrics']['output_tokens']['mean'],140)
        self.assertIsNone(fifth_point['metrics']['grader_acceptance']['mean'])
        self.assertEqual(fifth_point['n_trajectories'],1)
