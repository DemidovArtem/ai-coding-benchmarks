import hashlib
import tempfile
import unittest
from pathlib import Path

from experiment.runner import setup_fingerprint
from reports.phase6_recover import task_text, verify_checkpoint


class RecoveryTests(unittest.TestCase):
    def test_snapshot_and_executor_must_match_before_any_recovery(self):
        config = {'codex': {}, 'benchmark': {}, 'pins': {}}
        metadata = {'state': 'running', 'variant': 'serena', 'step': 2,
                    'trajectory_id': 'phase6_serena_r01', 'executor_session_id': 'original',
                    'setup_fingerprint': setup_fingerprint(config)[0]}
        previous = {'collection_errors': [], 'trial_state': 'finished',
                    'continuous': {'executor_session_id': 'original'}}
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / 'snapshot'
            snapshot.write_bytes(b'original submitted archive')
            sidecar = {'ok': True, 'snapshot_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest()}
            verify_checkpoint(metadata, previous, config, sidecar, snapshot)
            previous['continuous']['executor_session_id'] = 'fresh'
            with self.assertRaises(ValueError):
                verify_checkpoint(metadata, previous, config, sidecar, snapshot)
            previous['continuous']['executor_session_id'] = 'original'
            snapshot.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                verify_checkpoint(metadata, previous, config, sidecar, snapshot)

    def test_warm_delivery_preserves_original_task_and_memory_instruction(self):
        task = task_text('Original task\nwith exact whitespace.\n')
        self.assertTrue(task.startswith('Original task\nwith exact whitespace.\n'))
        self.assertIn('Preserve prior work and submission tags.', task)
        self.assertIn('warm; read and reuse a memory retained from the previous task. Do not repeat onboarding.', task)
