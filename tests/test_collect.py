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

    def test_sonar_must_bind_to_the_same_graded_submission_and_keeps_missing_deltas_null(self):
        import json
        from experiment.collect import sonar_result
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/"trial"
            (run/"sonar").mkdir(parents=True)
            base = Path(tmp)/"base"; base.mkdir()
            record = {"sonar":{"analysis_ok":None},"snapshot_sha256":"snapshot","ending_commit":"commit","starting_tree":"tree"}
            result = {"analysis_ok":True,"snapshot_binding_verified":True,"rust_coverage_verified":True,
                "snapshot_sha256":"snapshot","project_key":"project","protocol_sha256":"protocol","source_exclusions":[],
                "metrics":{"ncloc":12,"complexity":None}}
            binding = {"snapshot_sha256":"snapshot","submission_commit":"commit","kind":"solution","trial_id":"trial",
                "project_key":"project","protocol_sha256":"protocol","source_files":{"file.rs":"sha"}}
            (run/"sonar/sonar.json").write_text(json.dumps(result))
            (run/"sonar/binding.json").write_text(json.dumps(binding))
            (run/"sonar/components.json").write_text(json.dumps([{"path":"file.rs","language":"rust"}]))
            (base/"sonar.json").write_text(json.dumps({**result,"metrics":{"ncloc":10,"complexity":4}}))
            (base/"binding.json").write_text(json.dumps({"kind":"base","starting_tree":"tree"}))
            attached = sonar_result(run,record,base)
            self.assertTrue(attached["analysis_ok"])
            self.assertEqual(attached["delta_vs_common_base"],{"ncloc":2,"complexity":None})
            binding["submission_commit"] = "another trial"
            (run/"sonar/binding.json").write_text(json.dumps(binding))
            rejected = sonar_result(run,record,base)
            self.assertFalse(rejected["analysis_ok"])
            self.assertIsNone(rejected["metrics"])

    def test_grader_success_does_not_hide_failed_profile_activation(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)
            (run/'evaluation').mkdir()
            (run/'run_metadata.json').write_text(json.dumps({'state':'failed','variant':'ponytail','failure_category':'skill_trial_failure'}))
            (run/'evaluation/evaluation_result.json').write_text(json.dumps({'resolved':True}))
            config={'experiment_id':'test','benchmark':{'repo':'repo','smoke_milestone':'task','version':'v'},
                'pins':{'git_commits':{'results/setup/dataset':'commit'}},'codex':{}}
            record=collect(run,config)
            self.assertTrue(record['resolved'])
            self.assertEqual(record['failure_category'],'skill_trial_failure')
            self.assertEqual(record['trial_state'],'failed')
