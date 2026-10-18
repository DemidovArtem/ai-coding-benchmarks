import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
from unittest.mock import patch

from experiment.audit import check_pins, collect, command, host_summary


class AuditTests(unittest.TestCase):
    def test_codex_login_status_on_stderr_is_recognized(self):
        result = subprocess.CompletedProcess([], 0, "", "Logged in using ChatGPT\n")
        with patch("experiment.audit.subprocess.run", return_value=result):
            self.assertEqual(command("codex", "login", "status"), "Logged in using ChatGPT")

    def test_credentials_and_private_settings_never_enter_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".codex").mkdir()
            (home / ".codex/config.toml").write_text(
                'private_setting = "DO_NOT_PRINT"\n'
                '[mcp_servers.private]\nenv = {TOKEN = "DO_NOT_PRINT"}\n'
            )
            (home / ".codex/auth.json").write_text("invalid-json-DO_NOT_PRINT")
            summary = host_summary(home, {"OPENAI_API_KEY": "DO_NOT_PRINT"})
            self.assertNotIn("DO_NOT_PRINT", json.dumps(summary))
            self.assertNotIn("private", json.dumps(summary))
            self.assertTrue(summary["auth_file_present"])
            self.assertTrue(summary["paid_key_env_present"]["OPENAI_API_KEY"])
            self.assertEqual(summary["mcp_server_count"], 1)

    def test_broken_config_does_not_dump_parser_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".codex").mkdir()
            (home / ".codex/config.toml").write_text('secret = "DO_NOT_PRINT')
            summary = host_summary(home, {})
            self.assertEqual(summary["config_status"], "unreadable")
            self.assertNotIn("DO_NOT_PRINT", json.dumps(summary))

    def test_missing_or_modified_asset_fails_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pins = {"file_sha256": {"asset": hashlib.sha256(b"frozen").hexdigest()}, "git_commits": {}}
            self.assertEqual(check_pins(root, pins), ["file_pin_mismatch:asset"])
            (root / "asset").write_bytes(b"frozen")
            self.assertEqual(check_pins(root, pins), [])
            (root / "asset").write_bytes(b"changed")
            self.assertEqual(check_pins(root, pins), ["file_pin_mismatch:asset"])

    def test_dirty_pinned_checkout_fails(self):
        with patch("experiment.audit.command", side_effect=["commit", " M evaluator.py"]):
            failures = check_pins(Path("."), {"file_sha256": {}, "git_commits": {"vendor": "commit"}})
        self.assertEqual(failures, ["checkout_dirty:vendor"])

    def test_patched_source_can_be_recommitted_with_exact_tree_and_base(self):
        pins = {"file_sha256": {}, "git_commits": {"vendor": "upstream-base"}, "git_trees": {"vendor": "patched-tree"}}
        with patch("experiment.audit.command", side_effect=["patched-tree", "", ""]):
            self.assertEqual(check_pins(Path("."), pins), [])
        with patch("experiment.audit.command", side_effect=["different-tree"]):
            self.assertEqual(check_pins(Path("."), pins), ["git_tree_mismatch:vendor"])
        with patch("experiment.audit.command", side_effect=["patched-tree", None]):
            self.assertEqual(check_pins(Path("."), pins), ["git_base_mismatch:vendor"])

    def test_paid_environment_blocks_smoke(self):
        config = {"pins": {"file_sha256": {}, "git_commits": {}},
                  "codex": {"version": "0.163.0"},
                  "resources": {"min_workspace_free_bytes": 0}, "phase1_blockers": []}

        def fake_command(*args, **kwargs):
            if args == ("codex", "--version"):
                return "codex-cli 0.163.0"
            if args == ("codex", "login", "status"):
                return "Logged in using ChatGPT"
            return "available"

        with tempfile.TemporaryDirectory() as tmp, patch("experiment.audit.command", side_effect=fake_command), \
                patch.dict("os.environ", {"CODEX_API_KEY": "DO_NOT_PRINT"}, clear=True):
            report = collect(Path(tmp), config)
        self.assertFalse(report["ready_for_smoke"])
        self.assertIn("paid_api_environment_present", report["pin_and_environment_failures"])
        self.assertNotIn("DO_NOT_PRINT", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
