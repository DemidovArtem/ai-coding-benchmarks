import hashlib
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from experiment.phase6f_resume import validate_failure, work_state, resume_retained_step


class SixthRecoveryTests(unittest.TestCase):
    def test_only_failed_unsubmitted_quota_turn_may_resume(self):
        failed={'trial_state':'failed','ending_commit':None,'variant':'caveman','repetition':1,
                'continuous':{'step':6},'failure_category':'quota_pressure'}
        events=[{'type':'turn.failed','error':{'message':'You have hit your usage limit'}}]
        validate_failure(failed,events)
        with self.assertRaises(ValueError):validate_failure(failed,events+[{'type':'turn.completed'}])
        failed['ending_commit']='already-submitted'
        with self.assertRaises(ValueError):validate_failure(failed,events)

    def test_partial_tracked_work_is_hashed_and_untracked_files_rejected(self):
        setup=Mock();setup.docker_exec_git.side_effect=[SimpleNamespace(stdout=s) for s in ('c5\n','partial diff\n','','')]
        state=work_state(setup)
        self.assertEqual(state['unstaged_sha256'],hashlib.sha256(b'partial diff\n').hexdigest())
        setup.docker_exec_git.side_effect=[SimpleNamespace(stdout=s) for s in ('c5\n','partial diff\n','','unexpected.rs\n')]
        with self.assertRaises(ValueError):work_state(setup)

    def test_changed_retained_work_stops_before_prompt_or_model(self):
        runner=Mock()
        with patch('experiment.phase6f_resume.work_state',return_value={'head':'changed'}):
            with self.assertRaises(ValueError):resume_retained_step(runner,'same-session',{'head':'c5'})
        runner._load_prompt.assert_not_called()
        runner.agent_runner.resume_session.assert_not_called()
