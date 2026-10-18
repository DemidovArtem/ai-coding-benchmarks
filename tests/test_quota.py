import io
import json
import unittest
from unittest.mock import MagicMock, patch

from experiment.quota import read_quota


class QuotaTests(unittest.TestCase):
    def test_buffered_messages_do_not_hide_rate_limit_response(self):
        process = MagicMock()
        process.stdin = io.BytesIO()
        process.stdout.fileno.return_value = 123
        chunks = [b'{"id":1,"result":{}}\n{"method":"notice"}\n',
                  b'{"id":2,"result":{"rateLimits":{"primary":{"usedPercent":33},"accountSecret":"private"}}}\n']
        selector = MagicMock()
        selector.select.return_value = [True]
        with patch("experiment.quota.subprocess.Popen", return_value=process), \
                patch("experiment.quota.selectors.DefaultSelector", return_value=selector), \
                patch("experiment.quota.os.read", side_effect=chunks), \
                patch.object(process.stdin, "close"):
            report = read_quota()
            requests = [json.loads(line) for line in process.stdin.getvalue().splitlines()]
        self.assertEqual(report["status"], "observed")
        self.assertEqual(report["rate_limits"]["default"]["primary"]["usedPercent"], 33)
        self.assertNotIn("private", json.dumps(report))
        self.assertEqual([r["method"] for r in requests], ["initialize", "initialized", "account/rateLimits/read"])
        process.terminate.assert_called_once()
