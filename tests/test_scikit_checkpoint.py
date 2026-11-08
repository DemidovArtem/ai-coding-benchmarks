from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiment.scikit_collect import metrics_repository
from experiment.scikit_run import schedule


class ScikitCheckpointTests(unittest.TestCase):
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
                with patch('experiment.scikit_collect.ROOT', root):
                    repo = metrics_repository(run)
                actual = subprocess.check_output(['git', '-C', str(repo), 'show', 'agent-impl-M06:value.py']).decode()
                self.assertEqual(actual, f'value = {repetition}\n')
                if repetition == 2:
                    self.assertNotEqual(commit, commits[0])
                    missing = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', commits[0]], capture_output=True)
                    self.assertNotEqual(missing.returncode, 0)
                git('tag', '-d', 'agent-impl-M06')
