import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from experiment.continuous import resume_step, update_progress, usage_delta, verify_dispatch, verify_selection


class ContinuousTests(unittest.TestCase):
    def test_selection_rejects_missing_reversed_and_duplicate_prerequisites(self):
        edges = [{'source_id': 'a', 'target_id': 'b', 'strength': 'Strong'}]
        verify_selection(['a', 'b'], edges)
        for selected in (['b', 'a'], ['b', 'c'], ['a', 'a']):
            with self.subTest(selected=selected), self.assertRaises(ValueError):
                verify_selection(selected, edges)

    def test_dispatch_requires_same_thread_and_complete_first_read(self):
        events = [{'type': 'thread.started', 'thread_id': 'same'}, {'type': 'item.completed', 'item': {
            'type': 'command_execution', 'command': 'cat /task', 'exit_code': 0, 'aggregated_output': 'SRS and validated plan\n'}}]
        self.assertTrue(verify_dispatch(events, 'same', '/task', 'SRS and validated plan')['read_verified'])
        for session, path, task in (('new', '/task', 'SRS and validated plan'),
                                    ('same', '/other', 'SRS and validated plan'), ('same', '/task', 'truncated')):
            with self.subTest(session=session, path=path, task=task), self.assertRaises(ValueError):
                verify_dispatch(events, session, path, task)
        events.insert(1, {'type': 'item.completed', 'item': {'type': 'command_execution', 'command': 'touch source.rs'}})
        with self.assertRaises(ValueError):
            verify_dispatch(events, 'same', '/task', 'SRS and validated plan')

    def test_cumulative_usage_is_subtracted_missing_stays_null(self):
        before = {'session_ids': ['thread'], 'anomalies': [], 'input_tokens': 100, 'output_tokens': 20}
        after = {**before, 'input_tokens': 160, 'output_tokens': 37}
        delta = usage_delta(after, before)
        self.assertEqual((delta['input_tokens'], delta['output_tokens']), (60, 17))
        self.assertIsNone(delta['cached_input_tokens'])
        self.assertIsNone(usage_delta({'session_ids': []}, before)['output_tokens'])
        for invalid in ({**after, 'session_ids': ['new']}, {**after, 'output_tokens': 19}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                usage_delta(invalid, before)

    def runner(self):
        runner = Mock(milestone_id='step2')
        runner.container_setup.docker_exec_git.side_effect = [
            SimpleNamespace(returncode=0, stdout='previous\n'), SimpleNamespace(returncode=0, stdout='')]
        runner.agent_runner.session_id = 'same'
        runner.agent_runner.resume_session.return_value = True
        runner._load_prompt.return_value = 'validated dispatch'
        runner._verify_tag_exists.return_value = True
        runner._get_tag_hash.return_value = 'submission'
        runner._extract_snapshot.return_value = 'immutable snapshot'
        return runner

    def test_resume_uses_same_session_and_grades_only_immutable_submission(self):
        runner = self.runner()
        resume_step(runner, 'same', 'previous')
        runner.agent_runner.resume_session.assert_called_once_with('same', 'validated dispatch')
        runner._extract_snapshot.assert_called_once_with(expected_tag_hash='submission')
        runner._run_evaluation.assert_called_once_with('immutable snapshot')

    def test_preparation_resume_and_submission_failures_withhold_next_work(self):
        for failure in ('prep', 'resume', 'session', 'tag'):
            with self.subTest(failure=failure):
                runner = self.runner()
                if failure == 'prep':
                    runner._load_prompt.side_effect = RuntimeError('planner failed')
                elif failure == 'resume':
                    runner.agent_runner.resume_session.return_value = False
                elif failure == 'session':
                    runner.agent_runner.session_id = 'new'
                else:
                    runner._verify_tag_exists.return_value = False
                with self.assertRaises(RuntimeError):
                    resume_step(runner, 'same', 'previous')
                runner._run_evaluation.assert_not_called()
                if failure == 'prep':
                    runner.agent_runner.resume_session.assert_not_called()

    def test_dirty_boundary_prevents_task_publication(self):
        runner = self.runner()
        runner.container_setup.docker_exec_git.side_effect = [
            SimpleNamespace(returncode=0, stdout='previous'), SimpleNamespace(returncode=0, stdout=' M source.rs')]
        with self.assertRaises(ValueError):
            resume_step(runner, 'same', 'previous')
        runner._load_prompt.assert_not_called()

    def test_progress_only_claims_session_proof_after_finished_trajectory(self):
        with TemporaryDirectory() as tmp, patch('experiment.continuous.ROOT', Path(tmp)), patch('experiment.status.main'):
            path = Path(tmp) / 'reports/continuous_feasibility.json'
            path.parent.mkdir()
            path.write_text(json.dumps({'pilot_runs':[{'trial_id':'chain','state':'planned'}]}))
            update_progress('chain', state='running')
            self.assertFalse(json.loads(path.read_text())['same_executor_session_verified'])
            update_progress('chain', state='finished')
            result = json.loads(path.read_text())
            self.assertTrue(result['same_executor_session_verified'])
            self.assertEqual(result['status'], 'completed')
