import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiment.runner import host_smoke, validate


class RunnerTests(unittest.TestCase):
    def test_paid_key_rejected_before_any_cli_call(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret"}, clear=True), \
                patch("experiment.runner.command") as command:
            with self.assertRaisesRegex(RuntimeError, "Paid API"):
                validate({})
            command.assert_not_called()

    def test_host_smoke_has_clean_home_and_preserves_original_auth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "original"
            (home / ".codex").mkdir(parents=True)
            auth = home / ".codex/auth.json"
            auth.write_text('{"tokens":{"access_token":"secret"}}')
            output = root / "output"
            output.mkdir()

            def invoke(args, **kwargs):
                self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)
                env = kwargs["env"]
                self.assertNotIn("OPENAI_API_KEY", env)
                self.assertNotIn("UNRELATED_PRIVATE", env)
                self.assertNotEqual(Path(env["HOME"]), home)
                self.assertEqual(Path(env["CODEX_HOME"]).parent, Path(env["HOME"]))
                self.assertIn('forced_login_method = "chatgpt"', (Path(env["CODEX_HOME"]) / "config.toml").read_text())
                (Path(env["CODEX_HOME"]) / "auth.json").write_text('{"tokens":{"access_token":"refreshed"}}')
                events = [{"type":"item.completed","item":{"type":"agent_message","text":"OAUTH_SMOKE_OK"}},
                          {"type":"turn.completed","usage":{"input_tokens":10,"output_tokens":2}}]
                return subprocess.CompletedProcess(args, 0, "\n".join(map(json.dumps, events)), "secret refreshed")

            with patch("experiment.runner.Path.home", return_value=home), \
                    patch.dict(os.environ, {"UNRELATED_PRIVATE":"private"}), \
                    patch("experiment.runner.subprocess.run", side_effect=invoke):
                self.assertEqual(host_smoke({}, output), 0)
            self.assertEqual(auth.read_text(), '{"tokens":{"access_token":"secret"}}')
            self.assertNotIn("secret", (output / "stderr.txt").read_text())
            self.assertNotIn("refreshed", (output / "stderr.txt").read_text())
            self.assertFalse(list(output.glob("oauth-host-*")))
