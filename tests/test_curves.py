import unittest

from experiment.curves import aggregate


def row(variant, repetition, step, tokens, churn, cohort='a'):
    return {'trial_id':f'{cohort}-{variant}-{repetition}-{step}', 'variant':variant,
            'trial_state':'finished','resolved':True,'collection_errors':[], 'setup_fingerprint':cohort,
            'repo':'repo','starting_tree':'tree','model':'model','reasoning_effort':'high',
            'dataset_version':'version','repetition':repetition,'milestone_id':f'task{step}',
            'continuous':{'trajectory_id':f'{cohort}-{variant}-{repetition}','step':step},
            'usage':{'total':{'input_tokens':tokens*10,'output_tokens':tokens,'cached_input_tokens':tokens*5}},
            'churn_prod_loc':churn,'sonar':{'analysis_ok':True,'common_base_comparison_verified':True,
                'delta_vs_common_base':{'cognitive_complexity':churn}},
            'durations_seconds':{'planner':0,'executor':2}}


class CurvesTests(unittest.TestCase):
    def test_repeat_mean_uses_cumulative_tokens_but_not_sum_of_cumulative_churn(self):
        result=aggregate([row('baseline',1,1,10,5),row('baseline',1,2,20,9),
                          row('baseline',2,1,20,7),row('baseline',2,2,30,13)])
        point=next(p for p in result['points'] if p['step']==2)
        self.assertEqual(point['metrics']['output_tokens']['mean'],40)
        self.assertEqual(point['metrics']['churn_prod_loc']['mean'],11)
        self.assertEqual(point['metrics']['churn_prod_loc']['n'],2)
        self.assertEqual(point['metrics']['output_tokens']['min'],30)
        self.assertIsNone(point['metrics']['net_prod_loc']['mean'])

    def test_missing_repeat_is_not_zero_and_different_cohort_is_not_pooled(self):
        rows=[row('baseline',1,1,10,5),row('baseline',2,1,20,7),row('ponytail',1,1,8,3),
              row('ponytail',2,1,100,100,'other')]
        failed=row('ponytail',2,1,0,0);failed['trial_state']='failed';rows.append(failed)
        result=aggregate(rows)
        pony=next(p for p in result['points'] if p['variant']=='ponytail' and p['setup_fingerprint']=='a')
        self.assertEqual(pony['metrics']['output_tokens']['mean'],8)
        self.assertEqual(pony['metrics']['output_tokens']['n'],1)
        self.assertIsNone(pony['metrics']['output_tokens']['sd'])
        self.assertEqual(pony['paired_delta']['output_tokens']['mean'],-2)
        self.assertEqual(len(result['excluded_trials']),1)

    def test_duplicate_or_nonconsecutive_steps_are_rejected(self):
        for rows in ([row('baseline',1,2,10,5)], [row('baseline',1,1,10,5)]*2):
            with self.assertRaises(ValueError):aggregate(rows)
