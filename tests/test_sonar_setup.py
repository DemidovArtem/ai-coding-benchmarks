import json
from pathlib import Path
import unittest

import yaml


class SonarSetupTests(unittest.TestCase):
    def test_recipe_is_pinned_private_and_cannot_pull_implicitly(self):
        root = Path(__file__).resolve().parents[1] / "sonar"
        config = yaml.safe_load((root / "compose.yaml").read_text())
        candidates = {row["role"]:row["digest_ref"] for row in json.loads((root / "setup_candidates.json").read_text())["images"]}
        services = config["services"]
        for role in ("server", "scanner"):
            self.assertEqual(services[role]["image"], candidates[role])
            self.assertEqual(services[role]["pull_policy"], "never")
            self.assertFalse(services[role].get("privileged", False))
        self.assertEqual(services["server"]["ports"], ["127.0.0.1:9000:9000"])
        self.assertNotIn("ports", services["scanner"])
        self.assertTrue(config["networks"]["analysis"]["internal"])
        self.assertEqual(services["scanner"]["environment"], ["SONAR_HOST_URL=http://server:9000", "SONAR_TOKEN"])
        self.assertIn("scan", services["scanner"]["profiles"])
