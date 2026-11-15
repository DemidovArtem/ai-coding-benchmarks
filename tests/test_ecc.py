import json
from pathlib import Path
from tempfile import TemporaryDirectory
import tomllib
import unittest

from experiment.quota import wait_for_quota
from experiment.ecc import native_evidence, require_activation
from unittest.mock import patch
from unittest.mock import Mock
from types import SimpleNamespace


class ECCTests(unittest.TestCase):
    def test_quota_recovery_keeps_root_waits_for_children_and_never_retries_other_errors(self):
        from experiment.ecc import resume_after_quota
        agent = SimpleNamespace(_last_rate_limit=True, _last_fatal_error=None, session_id='parent', quota_wait_seconds=0)
        setup = Mock(); setup.docker_exec.side_effect = [SimpleNamespace(returncode=0), SimpleNamespace(returncode=1)]
        sleeps, states = [], []
        resume = Mock(return_value=True)
        with patch('experiment.quota.wait_for_quota') as wait:
            self.assertTrue(resume_after_quota(agent, setup, Path('unused'), resume, states.append, sleep=sleeps.append))
        wait.assert_called_once()
        self.assertEqual(sleeps, [60]);self.assertEqual(states, ['waiting_quota', 'running'])
        self.assertEqual(resume.call_args.args[0], 'parent')
        agent._last_rate_limit = False
        resume.reset_mock()
        self.assertFalse(resume_after_quota(agent, setup, Path('unused'), resume, states.append))
        resume.assert_not_called()
        agent._last_rate_limit = True; agent._last_fatal_error = 'invocation may be alive'
        with self.assertRaises(RuntimeError):resume_after_quota(agent, setup, Path('unused'), resume, states.append)

    def test_native_usage_deduplicates_forked_responses_and_keeps_missing_unknown(self):
        def meta(name, parent=None):
            return {'type': 'session_meta', 'payload': {'id': name, 'parent_thread_id': parent}}
        def response(name, thread, amount):
            return {'type': 'token_usage_record', 'payload': {'response_id': name, 'thread_id': thread,
                'usage': {'input_tokens': amount}, 'thread_token_usage': {'input_tokens': amount}}}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            parent = response('response1', 'parent', 100)
            (root / 'parent.jsonl').write_text('\n'.join(map(json.dumps, [meta('parent'), parent])))
            (root / 'child.jsonl').write_text('\n'.join(map(json.dumps, [meta('child', 'parent'), parent, response('response2', 'child', 30)])))
            evidence, _ = native_evidence(root)
            self.assertEqual(evidence['root_session_id'], 'parent')
            self.assertEqual(evidence['response_count'], 2)
            self.assertEqual(evidence['total']['input_tokens'], 130)
            self.assertIsNone(evidence['total']['output_tokens'])
            # Missing older native records must not be reported as a complete total.
            damaged = response('response2', 'child', 30)
            damaged['payload']['thread_token_usage']['input_tokens'] = 50
            (root / 'child.jsonl').write_text('\n'.join(map(json.dumps, [meta('child', 'parent'), damaged])))
            self.assertIsNone(native_evidence(root)[0]['total']['input_tokens'])
            (root / 'unrelated.jsonl').write_text(json.dumps(meta('other')))
            with self.assertRaises(ValueError):
                native_evidence(root)

    def test_activation_gate_rejects_failed_or_different_profile(self):
        with TemporaryDirectory() as tmp, patch('experiment.ecc.ROOT', Path(tmp)):
            config = {'ecc': {'smoke_result': 'smoke.json', 'source_commit': 'commit'},
                      'benchmark': {'skill_runtime_image_id': 'image'},
                      'codex': {'version': '0.163.0', 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high'}}
            proof = {'success': True, 'source_commit': 'commit', 'image_id': 'image', 'codex': '0.163.0',
                     'model': 'gpt-6.1-sol', 'reasoning_effort': 'high', 'native_hook_activation_verified': True,
                     'skill_activation_verified': True, 'subagent_activation_verified': True, 'runtime_verified': True}
            path = Path(tmp) / 'smoke.json';path.write_text(json.dumps(proof));require_activation(config)
            for change in ({'success': False}, {'model': 'other'}, {'subagent_activation_verified': False}):
                path.write_text(json.dumps({**proof, **change}))
                with self.assertRaises(ValueError):require_activation(config)

    def test_config_schedules_one_trajectory_and_six_ordered_dataset_tasks(self):
        from experiment.continuous import verify_selection
        from experiment.phase6 import schedule
        import csv
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / 'reports/ecc_experiment.json').read_text())
        pilot = config['benchmark']['continuous_pilot']
        self.assertEqual(schedule(config), [('ecc', 1, 'ecc_ecc_r01')])
        self.assertEqual(len(pilot['milestones']), 6)
        self.assertEqual(pilot['stop_after'], 6)
        self.assertEqual(config['benchmark']['evaluation_policy']['residue_prune_from_step'], 4)
        self.assertEqual(config['benchmark']['evaluation_policy']['known_dependency_task'], pilot['milestones'][4])
        with (root / config['benchmark']['dataset_root'] / config['benchmark']['repo'] / 'dependencies.csv').open() as f:
            verify_selection(pilot['milestones'], list(csv.DictReader(f)))

    def test_native_wrapper_enables_only_local_plugins_and_sets_memory_home(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor/SWE-Milestone'))
        from experiment.ecc import framework
        agent = framework()
        command = agent.build_run_command(model='gpt-6.1-sol', session_id='unused', prompt_path='/task')
        self.assertNotIn('features.plugins=false', command)
        self.assertIn('features.remote_plugin=false', command)
        self.assertIn('web_search="disabled"', command)
        self.assertIn('--dangerously-bypass-hook-trust', command)
        self.assertIn('ECC_AGENT_DATA_HOME=/home/fakeroot/.ecc', agent.get_effective_container_env_vars())

    def test_profile_is_offline_and_all_official_roles_use_the_same_model(self):
        profile = Path(__file__).resolve().parents[1] / 'profiles/ecc'
        config = tomllib.loads((profile / 'config.toml').read_text())
        self.assertEqual(config['forced_login_method'], 'chatgpt')
        self.assertEqual(config['web_search'], 'disabled')
        self.assertTrue(config['features']['plugins'])
        self.assertTrue(config['features']['multi_agent'])
        self.assertFalse(config['features']['remote_plugin'])
        self.assertEqual(set(config['plugins']), {'ecc@ecc'})
        self.assertTrue(all(server['enabled'] is False for server in config['mcp_servers'].values()))
        self.assertEqual(set(config['agents']) - {'max_threads', 'max_depth'}, {'explorer', 'reviewer', 'docs_researcher'})
        for path in (profile / 'agents').glob('*.toml'):
            role = tomllib.loads(path.read_text())
            self.assertEqual(role['model'], config['model'])
            self.assertEqual(role['model_reasoning_effort'], config['model_reasoning_effort'])
            self.assertEqual(role['sandbox_mode'], 'read-only')

    def test_quota_wait_keeps_process_and_waits_at_exactly_two_percent(self):
        def report(used, minutes=300):
            return {'status': 'observed', 'rate_limits': {'codex': {'primary': {
                'usedPercent': used, 'windowDurationMins': minutes, 'resetsAt': 123}}}}
        snapshots = iter([report(98), {'status': 'timeout'}, report(97)])
        sleeps, states = [], []
        with TemporaryDirectory() as tmp:
            ready = wait_for_quota(tmp, read=lambda: next(snapshots), sleep=sleeps.append, on_wait=states.append)
            saved = json.loads((Path(tmp) / 'quota_wait.json').read_text())
        self.assertEqual(ready, report(97))
        self.assertEqual(sleeps, [60, 60])
        self.assertEqual(states, ['waiting_quota', 'waiting_observation'])
        self.assertEqual(saved['state'], 'ready')

    def test_long_window_exhaustion_does_not_silently_start_inference(self):
        snapshot = {'status': 'observed', 'rate_limits': {'codex': {
            'primary': {'usedPercent': 1, 'windowDurationMins': 300},
            'secondary': {'usedPercent': 100, 'windowDurationMins': 10080}}}}
        with TemporaryDirectory() as tmp, self.assertRaises(RuntimeError):
            wait_for_quota(tmp, read=lambda: snapshot, sleep=lambda _: self.fail('must not sleep'))


if __name__ == '__main__':
    unittest.main()
