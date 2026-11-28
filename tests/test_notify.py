import json
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from experiment.notify import send


class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.config = Path(self.temporary.name) / 'config.json'
        self.config.write_text(json.dumps({'ssh_host': 'user@example.invalid',
                                          'identity_file': '/tmp/test-key',
                                          'telegram_target': '12345'}))

    @patch('experiment.notify.subprocess.run')
    def test_confirmed_delivery_is_deduplicated_and_shell_text_stays_literal(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, json.dumps({
            'payload': {'ok': True, 'messageId': '42'}}), '')
        message = 'Apostrophe: \' and $(do-not-run) `not-code`\nsecond line'
        self.assertEqual(send(self.config, 'blocked-1', message)['status'], 'sent')
        self.assertEqual(send(self.config, 'blocked-1', message)['message_id'], '42')
        run.assert_called_once()
        command = shlex.split(run.call_args.args[0][-1])
        self.assertEqual(command[command.index('--message') + 1], message)
        with self.assertRaisesRegex(ValueError, 'different content'):
            send(self.config, 'blocked-1', 'changed')

    @patch('experiment.notify.subprocess.run')
    def test_unknown_delivery_is_retained_and_never_blindly_retried(self, run):
        run.side_effect = subprocess.TimeoutExpired('ssh', 60)
        self.assertEqual(send(self.config, 'blocked-2', 'review needed')['status'], 'uncertain')
        send(self.config, 'blocked-2', 'review needed')
        run.assert_called_once()
        records = list((self.config.parent / 'events').glob('*.json'))
        self.assertEqual(json.loads(records[0].read_text())['message'], 'review needed')

    @patch('experiment.notify.subprocess.run')
    def test_dry_run_does_not_mark_an_event_as_delivered(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, '{"dryRun":true}', '')
        self.assertEqual(send(self.config, 'test', 'hello', dry_run=True)['status'], 'dry_run_verified')
        self.assertEqual(list((self.config.parent / 'events').glob('*.json')), [])
        run.return_value.stdout = '{"payload":{"ok":true,"messageId":43}}'
        self.assertEqual(send(self.config, 'test', 'hello')['status'], 'sent')
        self.assertEqual(run.call_count, 2)

    @patch('experiment.notify.subprocess.run')
    def test_process_start_failure_can_retry_but_a_pending_send_cannot(self, run):
        run.side_effect = FileNotFoundError('ssh')
        self.assertEqual(send(self.config, 'test', 'hello')['status'], 'failed')
        run.side_effect = None
        run.return_value = subprocess.CompletedProcess([], 0, '{"payload":{"ok":true,"messageId":44}}', '')
        self.assertEqual(send(self.config, 'test', 'hello')['status'], 'sent')
        record = next((self.config.parent / 'events').glob('*.json'))
        value = json.loads(record.read_text()); value['status'] = 'pending'
        record.write_text(json.dumps(value))
        run.reset_mock()
        self.assertEqual(send(self.config, 'test', 'hello')['status'], 'pending')
        run.assert_not_called()

    @patch('experiment.notify.subprocess.run')
    def test_invalid_host_or_nonprivate_chat_never_sends(self, run):
        for change in ({'ssh_host': '-oProxyCommand=bad'}, {'telegram_target': '-12345'}):
            config = {'ssh_host': 'user@example.invalid', 'identity_file': '/tmp/key',
                      'telegram_target': '12345', **change}
            self.config.write_text(json.dumps(config))
            with self.assertRaises(ValueError):
                send(self.config, 'test', 'hello')
        run.assert_not_called()
