import json
from pathlib import Path
import tempfile
import unittest

from experiment.security import credential_values, redact, redact_artifacts


class SecurityTests(unittest.TestCase):
    def test_artifact_redaction_preserves_binary_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "trace.jsonl").write_text('{"message":"private-secret"}\n')
            (root / "snapshot.tar").write_bytes(b"\xff\x00binary")
            redact_artifacts(root, {"private-secret"})
            self.assertEqual(json.loads((root / "trace.jsonl").read_text())["message"], "[REDACTED]")
            self.assertEqual((root / "snapshot.tar").read_bytes(), b"\xff\x00binary")

    def test_redacts_known_values_and_credential_formats(self):
        text = 'nested-secret Bearer opaque-secret refresh_token="other-secret" sk-abcdefgh123456'
        clean = redact(text, {"nested-secret"})
        for value in ("nested-secret", "opaque-secret", "other-secret", "sk-abcdefgh123456"):
            self.assertNotIn(value, clean)
        self.assertEqual(redact('"input_tokens": 123'), '"input_tokens": 123')

    def test_collects_nested_credentials_without_account_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "auth.json"
            path.write_text(json.dumps({"tokens": {"access_token": "secret", "account_id": "account"}}))
            self.assertEqual(credential_values(path), {"secret"})
