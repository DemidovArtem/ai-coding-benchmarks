import unittest

from experiment.status import render, trial_status, phase_status


class StatusTests(unittest.TestCase):
    def test_pending_and_failed_results_are_explicit_and_missing_metrics_are_not_zero(self):
        rows=[{'trial_id':'phase3_baseline_001','variant':'baseline','resolved':True,'sonar':{'analysis_ok':True},'added_prod_loc':10}]
        pending=[{'trial_id':'phase3_serena_001','variant':'serena','trial_state':'running'}]
        text=render(rows,pending,{'status':'explicitly_deferred_engineering_integration_not_implemented'},'fixed time')
        self.assertIn('| phase3_serena_001 | serena | Выполняется | — | — | — | — | — |',text)
        self.assertIn('Отложен; не реализован',text)
        self.assertIn('Несобранных trials: **1**, из них выполняется: **1**',text)
        self.assertEqual(trial_status({'resolved':True,'failure_category':'activation_failure'}),'Ошибка; результат сохранён')
        self.assertEqual(phase_status(rows+pending,{'baseline','serena'}),'Выполняется')
        self.assertEqual(phase_status([],{'baseline'}),'Ещё не запускался')

    def test_actual_zero_serena_usage_stays_zero_and_scanner_failure_hides_metrics(self):
        row={'trial_id':'serena','variant':'serena','resolved':False,'sonar':{'analysis_ok':False,'metrics':{'ncloc':99}},'skill_state':{'natural_mcp_tool_calls':0,'memory_files_after':0}}
        text=render([row],[],{},'fixed time')
        self.assertIn('| serena | Ошибка | — | — | — | — | 0 | 0 |',text)
        self.assertIn('Завершён; grader не принят',text)
