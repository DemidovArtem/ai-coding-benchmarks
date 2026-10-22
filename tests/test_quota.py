import io
import json
import unittest
from unittest.mock import MagicMock, patch

from experiment.quota import read_quota


class QuotaTests(unittest.TestCase):
    def test_timeout_retries_only_the_observation_and_preserves_first_failure(self):
        timeout = {'status': 'timeout', 'rate_limits': None}
        fresh = {'status': 'observed', 'rate_limits': {'codex': {'primary': {'usedPercent': 33}}}}
        with patch('experiment.quota._read_quota_once', side_effect=[timeout, fresh]) as read:
            report = read_quota()
        self.assertEqual(read.call_count, 2)
        self.assertEqual(report['status'], 'observed')
        self.assertEqual(report['previous_observation'], timeout)

    def test_actual_service_limit_is_not_retried(self):
        limit = {'status': 'observed', 'rate_limits': {'codex': {'rateLimitReachedType': 'usage_limit'}}}
        with patch('experiment.quota._read_quota_once', return_value=limit) as read:
            self.assertEqual(read_quota(), limit)
        read.assert_called_once()

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
