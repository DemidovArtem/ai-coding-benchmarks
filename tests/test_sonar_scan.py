import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

from experiment.sonar_scan import extract, prepare, rust_manifest, verify_protocol


class ScanTests(unittest.TestCase):
    def test_archive_rejects_traversal_links_and_duplicate_paths_before_writing(self):
        for kind in ("traversal","link","duplicate"):
            buffer = io.BytesIO()
            with tarfile.open(fileobj=buffer,mode="w") as archive:
                member = tarfile.TarInfo("../escape" if kind == "traversal" else "source.rs")
                if kind == "link":
                    member.type = tarfile.SYMTYPE
                    member.linkname = "outside"
                archive.addfile(member)
                if kind == "duplicate":
                    archive.addfile(member)
            buffer.seek(0)
            with tempfile.TemporaryDirectory() as tmp, tarfile.open(fileobj=buffer) as archive:
                root = Path(tmp)
                with self.assertRaises(ValueError):
                    extract(archive,root)
                self.assertEqual(list(root.iterdir()),[])

    def test_profile_rule_parameters_and_analyzer_are_enforced(self):
        plugin = {"key":"rust","version":"pinned","hash":"digest"}
        rule = {"qProfile":"profile","inherit":"NONE","severity":"MAJOR","params":[],"impacts":[]}
        active = {"rust:rule":[dict(rule)]}
        protocol = {"rust_plugin":dict(plugin),"profile":{"key":"profile"},
            "active_rules_sha256":hashlib.sha256(json.dumps(active,sort_keys=True).encode()).hexdigest()}
        class Client:
            def get(self,path,**params):
                return {"plugins":[plugin]} if path == "/api/plugins/installed" else {"actives":{"rust:rule":[rule]}}
        client = Client()
        verify_protocol(client,protocol)
        rule["params"] = [{"key":"threshold","value":"changed"}]
        with self.assertRaisesRegex(ValueError,"rules"):
            verify_protocol(client,protocol)
        plugin["version"] = "changed"
        with self.assertRaisesRegex(ValueError,"analyzer"):
            verify_protocol(client,protocol)

    def test_solution_uses_exact_snapshot_bytes_and_common_base_build_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)/"trial"
            repo = run/"metrics_repository"
            (repo/"crates").mkdir(parents=True)
            (run/"evaluation").mkdir()
            def git(*args):
                return subprocess.check_output(["git","-C",str(repo),*args],stderr=subprocess.DEVNULL).decode().strip()
            git("init","-q")
            git("config","user.name","Test")
            git("config","user.email","test@example.invalid")
            (repo/"crates/data.help").write_text("immutable embedded resource")
            (repo/"Cargo.toml").write_text('base build support\n')
            (repo/"crates/lib.rs").write_text('pub fn before() {}\n')
            git("add","."); git("commit","-qm","base")
            base = git("rev-parse","HEAD")
            (repo/"crates/lib.rs").write_text('pub fn after() {}\n')
            git("add","."); git("commit","-qm","solution"); git("tag","submission")
            end = git("rev-parse","HEAD")
            snapshot = run/"evaluation/source_snapshot.tar"
            with tarfile.open(snapshot,"w") as archive:
                archive.add(repo/"crates/lib.rs",arcname="crates/lib.rs")
            sidecar = {"ok":True,"snapshot_sha256":hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                "agent_tag_commit":end,"tag":"submission","manifest_overlay":{"baseline_commit":base,"deletes":[]},
                "capture_filter":{"src_dirs":["crates"],"test_dirs":[],"exclude_patterns":["crates/*.help"],"generated_patterns":[]}}
            for path,data in (("evaluation/source_snapshot.integrity.json",sidecar),("experiment.json",{}),("effective_profile.json",{"starting_commit":base})):
                (run/path).write_text(json.dumps(data))
            output = Path(tmp)/"solution"; output.mkdir()
            stage,proof = prepare(run,output,"solution")
            self.assertEqual((stage/"crates/lib.rs").read_text(),'pub fn after() {}\n')
            self.assertEqual((stage/"Cargo.toml").read_text(),'base build support\n')
            self.assertEqual(proof["source_files"],rust_manifest(stage))
            self.assertEqual((stage/"crates/data.help").read_text(),"immutable embedded resource")
            self.assertEqual(proof["snapshot_sha256"],sidecar["snapshot_sha256"])
            output = Path(tmp)/"base"; output.mkdir()
            stage,proof = prepare(run,output,"base")
            self.assertEqual((stage/"crates/lib.rs").read_text(),'pub fn before() {}\n')
            self.assertEqual(proof["submission_commit"],base)
            (run/"evaluation/source_snapshot.tar").write_bytes(b"tampered")
            output = Path(tmp)/"tampered"; output.mkdir()
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                prepare(run,output,"solution")
