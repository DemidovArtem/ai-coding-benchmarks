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

    def test_required_serena_extension_remains_separate_from_measured_results(self):
        text=render([],[],{},'fixed time',{'label':'Профиль реализован; smoke тестируется'})
        self.assertIn('Дополнение: serena_required | Профиль реализован; smoke тестируется',text)
        self.assertIn('отдельный measured trial ещё не выполнен',text)
        self.assertLess(text.index('Дополнение: serena_required'),text.index('Phase 4: Sonar'))

    def test_continuous_priority_label_comes_from_plan(self):
        text=render([],[],{'status':'planned_not_implemented','label':'Следующий приоритет; не реализован'},'fixed time')
        self.assertIn('Phase 5: continuous, 2 связанных milestone | Следующий приоритет; не реализован',text)
        self.assertNotIn('planned_not_implemented',text)

    def test_continuous_schedule_shows_unfinished_steps_without_metrics(self):
        plan={'pilot_runs':[{'trial_id':'phase5_baseline_r01','variant':'baseline','repetition':1,
                            'completed_steps':1,'total_steps':2,'state':'running'}]}
        text=render([],[],plan,'fixed time')
        self.assertIn('| phase5_baseline_r01 | baseline | 1 | 1/2 | Выполняется |',text)
        plan['pilot_runs'][0]['state']='waiting_quota'
        self.assertIn('| phase5_baseline_r01 | baseline | 1 | 1/2 | Ожидает квоты |',render([],[],plan,'fixed time'))

    def test_quota_stop_without_snapshot_does_not_require_impossible_sonar_scan(self):
        rows=[{'trial_id':'graded','snapshot_sha256':'snapshot','sonar':{'analysis_ok':True}},
              {'trial_id':'quota_stop','trial_state':'failed','failure_category':'quota_pressure'}]
        text=render(rows,[],{},'fixed time')
        self.assertIn('Завершён для собранных snapshots',text)
        self.assertIn('| quota_stop | — | Ошибка; результат сохранён |',text)
        rows[0]['sonar']['analysis_ok']=False
        self.assertIn('Частично выполнен / ожидает анализов',render(rows,[],{},'fixed time'))

    def test_authorized_quota_override_is_explicit_in_register(self):
        text=render([],[],{'quota_override':{'percentage_gate_disabled':True}},'fixed time')
        self.assertIn('пользователь разрешил продолжение выше 85%',text)
        self.assertNotIn('Новые model trials требуют fresh quota check ниже 85%',text)

    def test_quarantine_blocked_queue_has_no_invented_results(self):
        plan={'label':'Пилот остановлен: quarantine preflight','pilot_runs':[
            {'trial_id':'phase5_plan_r02','variant':'plan','repetition':2,
             'completed_steps':0,'total_steps':2,'state':'blocked_quarantine'}]}
        text=render([],[],plan,'fixed time')
        self.assertIn('| phase5_plan_r02 | plan | 2 | 0/2 | Заблокирован: quarantine |',text)
        self.assertIn('Пилот остановлен: quarantine preflight',text)
        self.assertNotIn('grader принят',text)
