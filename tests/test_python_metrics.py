import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor/SWE-Milestone'))
from experiment.python_metrics import footprint, verify_snapshot


class PythonMetricsTests(unittest.TestCase):
    def test_cython_tests_binary_and_cross_boundary_rename(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.check_output(['git', '-C', temp, *args], stderr=subprocess.DEVNULL).decode().strip()
            def write(path, content):
                p = root / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content)
            git('init', '-q'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.invalid')
            write('sklearn/a.py', 'value = 1\n')
            write('sklearn/tests/test_moved.py', 'def moved():\n    return 3\n')
            write('sklearn/old.pxd', 'cdef int value\n')
            git('add', '.'); git('commit', '-qm', 'base'); base = git('rev-parse', 'HEAD')
            write('sklearn/a.py', 'value = 2\n# physical line\n')
            write('sklearn/new.pyx', 'cdef int added\n')
            write('sklearn/tests/test_new.py', 'assert True\n')
            write('sklearn/generated/a.py', 'generated = True\n')
            git('mv', 'sklearn/tests/test_moved.py', 'sklearn/moved.py')
            git('rm', 'sklearn/old.pxd')
            (root / 'sklearn/binary.py').write_bytes(b'\0binary')
            git('add', '.'); git('commit', '-qm', 'solution'); end = git('rev-parse', 'HEAD')
            metadata = {'repo_src_dirs': ['sklearn/'], 'test_dirs': ['**/tests/**']}
            result = footprint(root, base, end, metadata)
            self.assertEqual((result['added_prod_loc'], result['deleted_prod_loc']), (5, 2))
            self.assertEqual(result['cumulative_prod_loc'], 5)
            self.assertEqual(result['new_prod_files'], 2)
            self.assertEqual(result['binary_changes'], ['sklearn/binary.py'])
            self.assertEqual(result['changed_prod_files'], 4)

    def test_snapshot_verifies_python_bytes_and_rejects_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.check_output(['git', '-C', temp, *args], stderr=subprocess.DEVNULL)
            git('init', '-q'); git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.invalid')
            (root / 'a.py').write_text('value = 1\n')
            git('add', '.'); git('commit', '-qm', 'source'); git('tag', 'agent-impl-M06')
            archive = root / 'snapshot.tar'
            archive.write_bytes(git('archive', 'HEAD', '--', 'a.py'))
            side = {'ok': True, 'snapshot_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                    'tag': 'agent-impl-M06', 'agent_tag_commit': git('rev-parse', 'HEAD').decode().strip()}
            self.assertIn('a.py', verify_snapshot(archive, side, root))
            with tarfile.open(archive, 'w') as output:
                (root / 'a.py').write_text('wrong = True\n'); output.add(root / 'a.py', arcname='a.py')
            side['snapshot_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, 'differs'):
                verify_snapshot(archive, side, root)
