import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiment.continuous_resume import recovery_input, verify_retained_config
from experiment.runner import check_quota, setup_fingerprint


class RecoveryTests(unittest.TestCase):
    def test_only_expected_project_trust_entry_may_be_added_by_codex(self):
        expected='model="frozen"\n'
        verify_retained_config(expected,expected)
        verify_retained_config(expected+'[projects."/testbed"]\ntrust_level="trusted"\n',expected)
        for changed in ('model="other"\n',expected+'[projects."/other"]\ntrust_level="trusted"\n',
                        expected+'[mcp_servers.extra]\ncommand="other"\n'):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                verify_retained_config(changed,expected)
    def test_authorized_percentage_override_still_rejects_real_rate_limit(self):
        quota={'status':'observed','rate_limits':{'codex':{'primary':{'usedPercent':99}}}}
        with self.assertRaises(RuntimeError):
            check_quota(quota,85)
        check_quota(quota,101)
        quota['rate_limits']['codex']['rateLimitReachedType']='hard'
        with self.assertRaises(RuntimeError):
            check_quota(quota,101)

    def test_only_uninvoked_quota_stop_with_matching_previous_thread_can_recover(self):
        config={'codex':{},'benchmark':{},'pins':{}}
        fingerprint=setup_fingerprint(config)[0]
        metadata={'state':'failed','failure_category':'quota_pressure','step':2,'variant':'caveman',
                  'setup_fingerprint':fingerprint,'trajectory_id':'chain','executor_session_id':'thread'}
        previous={'resolved':True,'setup_fingerprint':fingerprint,'continuous':{
            'trajectory_id':'chain','step':1,'executor_session_id':'thread'}}
        with TemporaryDirectory() as tmp:
            blocked=Path(tmp)
            (blocked/'run_metadata.json').write_text(json.dumps(metadata))
            self.assertEqual(recovery_input(blocked,previous,config),metadata)
            previous['continuous']['executor_session_id']='different'
            with self.assertRaises(ValueError):
                recovery_input(blocked,previous,config)
            previous['continuous']['executor_session_id']='thread'
            (blocked/'log').mkdir()
            (blocked/'log/resume_message.txt').write_text('already invoked')
            with self.assertRaises(ValueError):
                recovery_input(blocked,previous,config)
