import hashlib
from pathlib import Path
import tempfile
import unittest

from experiment.collect import collect, verify_snapshot


class CollectTests(unittest.TestCase):
    def test_tampered_snapshot_fails_before_reading_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.tar"
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                verify_snapshot(path, {"snapshot_sha256": hashlib.sha256(b"original").hexdigest()}, Path(tmp))

    def test_live_or_missing_trial_is_not_treated_as_finished(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "not terminal"):
                collect(Path(tmp), {})
