import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiment.planning import repository_fingerprint
from experiment.resume_prepared import executor_state, prepared_input
from experiment.runner import setup_fingerprint


class ResumeTests(unittest.TestCase):
    def test_preparation_tampering_existing_executor_and_setup_changes_are_rejected(self):
        for mutation in (None,"handoff","repository","executor","setup","state"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                run = root/"trial"
                (run/"planner/repository").mkdir(parents=True)
                config = {"codex":{},"benchmark":{},"pins":{}}
                (root/"experiment.yaml").write_text(json.dumps(config))
                (run/"experiment.json").write_text(json.dumps(config))
                raw = json.dumps({"objective":"Task","steps":["Inspect"],"verification":["Check"],"risks":[],
                    "goal":{key:["Keep behavior"] for key in ("acceptance_criteria","constraints","non_goals","regression_invariants")}})
                (run/"planner/handoff.json").write_text(raw)
                sha = repository_fingerprint(run/"planner/repository")
                metadata = {"state":"failed","failure_category":"quota_pressure","variant":"goal_plan",
                    "setup_fingerprint":setup_fingerprint(config)[0],
                    "experiment_sha256":hashlib.sha256((root/"experiment.yaml").read_bytes()).hexdigest()}
                audit = {"state":"validated","variant":"goal_plan","repository_unchanged":True,
                    "repository_before_sha256":sha,"repository_after_sha256":sha,"session_id":"planner",
                    "handoff_sha256":hashlib.sha256(raw.encode()).hexdigest()}
                if mutation == "handoff":
                    (run/"planner/handoff.json").write_text(raw+" ")
                elif mutation == "repository":
                    (run/"planner/repository/new.rs").write_text("changed")
                elif mutation == "executor":
                    (run/"log").mkdir(); (run/"log/agent_stdout.txt").touch()
                elif mutation == "setup":
                    config["codex"]["model"] = "changed"
                elif mutation == "state":
                    metadata["state"] = "running"
                (run/"run_metadata.json").write_text(json.dumps(metadata))
                (run/"planner/audit.json").write_text(json.dumps(audit))
                with patch("experiment.resume_prepared.ROOT",root):
                    if mutation:
                        with self.assertRaises(ValueError):
                            prepared_input(run,config)
                    else:
                        self.assertEqual(prepared_input(run,config)[2],raw)

    def test_only_unstarted_pinned_executor_with_test_only_edits_is_accepted(self):
        config = {"images":[{"digest_ref":"pinned"}],"benchmark":{"common_starting_tree":"tree"}}
        for mutation in (None,"image","process","session","source","untracked"):
            with self.subTest(mutation=mutation):
                def call(args,**kwargs):
                    if args[1] == "inspect":
                        return json.dumps([{"Id":"container","Image":"other" if mutation == "image" else "image","State":{"Running":True}}]).encode()
                    if args[1:3] == ["image","inspect"]:
                        return b'[{"Id":"image"}]'
                    if "ps" in args:
                        return b"codex\n" if mutation == "process" else b"tail\n"
                    if "python3" in args:
                        return b"1\n" if mutation == "session" else b"0\n"
                    if "status" in args:
                        return b"?? file.rs\0" if mutation == "untracked" else b" M file.rs\0"
                    if "rev-parse" in args:
                        return b"tree\n" if "HEAD^{tree}" in args else b"commit\n"
                    if "show" in args:
                        return b"pub fn same() {}\n#[cfg(test)]\nmod tests {\n    #[test]\n    fn check() {}\n}\n"
                    if "cat" in args:
                        return b"pub fn changed() {}\n" if mutation == "source" else b"pub fn same() {}\n"
                    raise AssertionError(args)
                with patch("experiment.resume_prepared.subprocess.check_output",side_effect=call):
                    if mutation:
                        with self.assertRaises(ValueError):
                            executor_state("container",config)
                    else:
                        state = executor_state("container",config)
                        self.assertEqual(state["executor_session_files"],0)
                        self.assertIn("file.rs",state["test_only_worktree_edits"])
