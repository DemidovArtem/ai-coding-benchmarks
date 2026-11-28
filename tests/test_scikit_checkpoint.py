from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiment.scikit_collect import metrics_repository
from experiment.scikit_run import schedule, trial_id
from experiment.scikit import artifact


class ScikitCheckpointTests(unittest.TestCase):
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
