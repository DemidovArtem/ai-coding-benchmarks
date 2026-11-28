from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiment.scikit_collect import metrics_repository, collect
from experiment.scikit_run import schedule, trial_id, next_trial
from experiment.scikit import artifact


class ScikitCheckpointTests(unittest.TestCase):
    def test_blocked_method_allows_current_task_peers_but_holds_next_task(self):
        config = {'variants': ['baseline', 'ecc'], 'benchmark': {'milestones': ['M06', 'M11']},
                  'trial_prefix': 'v2', 'repetitions': 2}
        rows = {trial_id('baseline', 1, 1, config): {'trial_state': 'failed', 'collection_errors': []}}
        self.assertEqual(next_trial(config, rows), (1, 1, 'ecc'))
        rows[trial_id('ecc', 1, 1, config)] = {'trial_state': 'finished', 'collection_errors': []}
        with self.assertRaisesRegex(RuntimeError, 'before advancing'):
            next_trial(config, rows)

    def test_ecc_collection_uses_deduplicated_tree_totals_instead_of_parent_only(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            metadata = {'state': 'failed', 'variant': 'ecc', 'step': 1, 'repetition': 1,
                        'setup_fingerprint': 'setup', 'implementation_commit': 'implementation',
                        'trajectory_id': 'v2_ecc_r01', 'executor_session_id': 'root', 'input_commit': 'base'}
            (run / 'run_metadata.json').write_text(json.dumps(metadata))
            (run / 'log').mkdir()
            (run / 'log/agent_stdout.txt').write_text('\n'.join(map(json.dumps, [
                {'type': 'thread.started', 'thread_id': 'root'},
                {'type': 'turn.completed', 'usage': {'input_tokens': 100, 'cached_input_tokens': 50, 'output_tokens': 10}}])))
            native = {'total': {'input_tokens': 130, 'cached_input_tokens': 60, 'output_tokens': 15, 'reasoning_output_tokens': None}}
            (run / 'ecc_usage.json').write_text(json.dumps(native))
            config = {'experiment_id': 'v2', 'benchmark': {'common_starting_commit': 'base', 'common_starting_tree': 'tree',
                      'repo': 'repo', 'milestones': ['M06'], 'version': 'v1.0.2'},
                      'codex': {'model': 'gpt-6.1-sol', 'reasoning_effort': 'high'},
                      'pins': {'git_commits': {'results/setup/dataset': 'dataset'}}}
            result = collect(run, config)
            self.assertEqual(result['cohort'], 'v2')
            self.assertEqual(result['usage']['executor']['input_tokens'], 130)
            self.assertEqual(result['usage']['parent_cumulative']['input_tokens'], 100)
            self.assertIsNone(result['usage']['executor']['reasoning_output_tokens'])

    def test_v2_schedule_and_ids_do_not_reuse_historical_attempts(self):
        config = {'variants': ['baseline', 'caveman', 'ponytail', 'serena', 'ecc'],
                  'repetitions': 2, 'benchmark': {'milestones': ['M06', 'M11', 'M12.1', 'M12.2', 'M01', 'M03']},
                  'trial_prefix': 'scikit_v2'}
        rows = schedule(config)
        self.assertEqual(len(rows), 60)
        self.assertEqual(len(set(rows)), 60)
        self.assertEqual(rows[4], (1, 1, 'ecc'))
        self.assertEqual(rows[29:31], [(1, 6, 'ecc'), (2, 1, 'baseline')])
        old = {trial_id(v, r, s) for r, s, v in schedule()}
        self.assertFalse(old & {trial_id(v, r, s, config) for r, s, v in rows})

    def test_new_cohort_uses_its_own_base_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = {'artifacts': {'common_base': 'results/scikit_v2_preflight/common_base'}}
            with patch('experiment.scikit.ROOT', root):
                self.assertEqual(artifact(config, 'common_base', 'old'), root / config['artifacts']['common_base'])
                with patch('experiment.scikit_collect.ROOT', root), patch('experiment.scikit_collect.subprocess.run') as run:
                    metrics_repository(root / 'trial', config)
                self.assertEqual(run.call_args.args[0][4], str(root / config['artifacts']['common_base'] / 'repository.bundle'))

    def test_step_first_order_and_cold_second_repetition(self):
        rows = schedule()
        self.assertEqual(len(rows), 48)
        self.assertEqual(rows[:4], [(1, 1, v) for v in ('baseline', 'caveman', 'ponytail', 'serena')])
        self.assertEqual(rows[23], (1, 6, 'serena'))
        self.assertEqual(rows[24], (2, 1, 'baseline'))
        self.assertEqual(len(set(rows)), 48)

    def test_incremental_bundles_restore_without_cross_trajectory_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source'; source.mkdir()
            def git(*args):
                return subprocess.check_output(['git', '-C', str(source), *args], stderr=subprocess.DEVNULL).decode().strip()
            git('init', '-q'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.invalid')
            (source / 'value.py').write_text('value = 0\n')
            git('add', '.'); git('commit', '-qm', 'base'); base = git('rev-parse', 'HEAD')
            common = root / 'results/scikit_preflight/common_base'; common.mkdir(parents=True)
            git('bundle', 'create', str(common / 'repository.bundle'), '--all')
            commits = []
            for repetition in (1, 2):
                git('checkout', '--detach', base)
                (source / 'value.py').write_text(f'value = {repetition}\n')
                git('add', '.'); git('commit', '-qm', f'run {repetition}')
                commit = git('rev-parse', 'HEAD'); commits.append(commit)
                git('tag', 'agent-impl-M06')
                run = root / f'r{repetition}'; run.mkdir()
                git('bundle', 'create', str(run / 'repository.bundle'), '--all', 'HEAD', '^' + base)
                with patch('experiment.scikit_collect.ROOT', root), patch('experiment.scikit.ROOT', root):
                    repo = metrics_repository(run)
                actual = subprocess.check_output(['git', '-C', str(repo), 'show', 'agent-impl-M06:value.py']).decode()
                self.assertEqual(actual, f'value = {repetition}\n')
                if repetition == 2:
                    self.assertNotEqual(commit, commits[0])
                    missing = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', commits[0]], capture_output=True)
                    self.assertNotEqual(missing.returncode, 0)
                git('tag', '-d', 'agent-impl-M06')
