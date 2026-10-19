import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiment.sonar_bootstrap import bootstrap, private_save, VERSION


class BootstrapTests(unittest.TestCase):
    def test_private_save_refuses_public_file_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"secret"
            private_save(path, {"token":"secret"})
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            link = Path(tmp)/"link"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                private_save(link,{})
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                private_save(path,{})

    def test_password_is_saved_before_change_and_token_is_never_in_report(self):
        password = "admin"
        def call(value, endpoint, **params):
            nonlocal password
            if endpoint == "/api/authentication/validate":
                return {"valid":value == password}
            self.assertEqual(value,password)
            if endpoint == "/api/users/change_password":
                self.assertEqual(json.loads(path.read_text())["password"],params["password"])
                password = params["password"]
            elif endpoint == "/api/user_tokens/generate":
                return {"token":"private-token"}
            else:
                self.assertEqual(endpoint,"/api/user_tokens/revoke")
            return {}
        with tempfile.TemporaryDirectory() as tmp, patch("experiment.sonar_bootstrap.request",side_effect=call), patch("experiment.sonar_bootstrap.SonarClient") as client:
            path = Path(tmp)/"private"/"credentials.json"
            client.return_value.get.side_effect = lambda endpoint, **params: VERSION if endpoint == "/api/server/version" else {"valid":True}
            report = bootstrap(path)
            self.assertNotIn("private-token",json.dumps(report))
            self.assertEqual(json.loads(path.read_text())["token"],"private-token")
            self.assertNotEqual(password,"admin")
            self.assertEqual(path.parent.stat().st_mode & 0o777,0o700)
