import hashlib
from pathlib import Path
import tempfile
import subprocess
import tarfile
import io
import unittest

from experiment.collect import collect, verify_snapshot


class CollectTests(unittest.TestCase):
    def test_uncommitted_workspace_does_not_invalidate_verified_submission_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repository"
            repo.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL).decode().strip()
            git("init", "-q")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            content = b"pub fn submitted() {}\n"
            (repo / "source.rs").write_bytes(content)
            git("add", ".")
            git("commit", "-qm", "submitted")
            git("tag", "submission")
            commit = git("rev-parse", "HEAD")
            (repo / "source.rs").write_text("uncommitted workspace change")
            snapshot = Path(tmp) / "snapshot.tar"
            with tarfile.open(snapshot, "w") as archive:
                member = tarfile.TarInfo("source.rs")
                member.size = len(content)
                archive.addfile(member, io.BytesIO(content))
            sidecar = {"ok":True, "uncommitted_lost_count":1, "agent_tag_commit":commit, "tag":"submission",
                       "snapshot_sha256":hashlib.sha256(snapshot.read_bytes()).hexdigest()}
            self.assertEqual(verify_snapshot(snapshot, sidecar, repo), 1)
            sidecar["ok"] = False
            with self.assertRaisesRegex(ValueError, "integrity"):
                verify_snapshot(snapshot, sidecar, repo)

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
