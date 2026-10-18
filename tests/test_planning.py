import json
from pathlib import Path
import tempfile
import unittest

from experiment.planning import GOAL_FIELDS, planner_prompt, repository_fingerprint, schema, validate_handoff


class PlanningTests(unittest.TestCase):
    def plan(self):
        return {"objective":"Meet the requirements", "steps":["Inspect source"],
                "verification":["Run existing checks"], "risks":[], "goal":None}

    def test_shared_prompt_and_schema_differ_only_in_goal_instruction(self):
        from experiment.planning import GOAL_INSTRUCTIONS
        for variant in ("plan", "goal_plan"):
            prompt = planner_prompt("ORIGINAL_TASK", variant)
            common = prompt.replace(GOAL_INSTRUCTIONS[variant], "GOAL_INSTRUCTION")
            if variant == "plan":
                expected = common
            self.assertEqual(common, expected)
        self.assertEqual(set(schema()["required"]), set(self.plan()))

    def test_plan_goal_validation_and_output_bounds(self):
        value = self.plan()
        self.assertEqual(validate_handoff(json.dumps(value), "plan"), value)
        with self.assertRaises(ValueError):
            validate_handoff(json.dumps(value), "goal_plan")
        value["goal"] = {key:["Requirement from the task"] for key in GOAL_FIELDS}
        validate_handoff(json.dumps(value), "goal_plan")
        with self.assertRaises(ValueError):
            validate_handoff(json.dumps(value), "plan")
        value["steps"] = ["```implementation```"]
        with self.assertRaises(ValueError):
            validate_handoff(json.dumps(value), "goal_plan")
        with self.assertRaises(ValueError):
            validate_handoff('{"goal":null,"goal":null}', "plan")
        with self.assertRaises(ValueError):
            validate_handoff(" " * 12001, "plan")

    def test_repository_fingerprint_detects_untracked_and_symlink_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source.rs").write_text("original")
            before = repository_fingerprint(root)
            (root / "new.rs").write_text("added")
            self.assertNotEqual(repository_fingerprint(root), before)
            (root / "new.rs").unlink()
            (root / "link").symlink_to("source.rs")
            with_link = repository_fingerprint(root)
            (root / "link").unlink()
            (root / "link").symlink_to("another.rs")
            self.assertNotEqual(repository_fingerprint(root), with_link)

    def test_executor_profiles_are_equal_but_independent_files(self):
        root = Path(__file__).resolve().parents[1]
        base = root / "profiles/baseline/config.toml"
        for variant in ("plan", "goal_plan"):
            path = root / "profiles" / variant / "config.toml"
            self.assertFalse(path.is_symlink())
            self.assertEqual(path.read_bytes(), base.read_bytes())
            self.assertNotEqual(path.stat().st_ino, base.stat().st_ino)
