import json
import unittest

from experiment.checkpoint_restore import legacy_rollout, verify_turns


class CheckpointRestoreTests(unittest.TestCase):
    def raw(self):
        return b'\n'.join(json.dumps(event).encode() for event in [
            {'type': 'session_meta', 'payload': {'id': 'same-thread', 'history_mode': 'paginated', 'cwd': '/testbed'}},
            {'type': 'response_item', 'payload': {'type': 'message', 'content': 'retained context'}},
            {'type': 'event_msg', 'payload': {'type': 'task_complete', 'turn_id': 'turn-3'}},
        ]) + b'\n'

    def test_only_storage_header_changes(self):
        raw = self.raw()
        restored, proof = legacy_rollout(raw, 'same-thread')
        self.assertEqual(raw.splitlines()[1:], restored.splitlines()[1:])
        self.assertEqual(json.loads(restored.splitlines()[0])['payload']['cwd'], '/testbed')
        self.assertEqual(json.loads(restored.splitlines()[0])['payload']['history_mode'], 'legacy')
        self.assertEqual(proof['turn_ids'], ['turn-3'])
        self.assertFalse(proof['messages_changed'])

    def test_wrong_session_and_unfinished_boundary_rejected(self):
        with self.assertRaises(ValueError):
            legacy_rollout(self.raw(), 'different-thread')
        with self.assertRaises(ValueError):
            legacy_rollout(self.raw() + b'{"type":"response_item","payload":{}}\n', 'same-thread')

    def test_missing_reordered_and_incomplete_native_turns_rejected(self):
        response = {'result': {'data': [{'id': 'one', 'status': 'completed'}, {'id': 'two', 'status': 'completed'}], 'nextCursor': None}}
        self.assertEqual(verify_turns(response, ['one', 'two']), 2)
        with self.assertRaises(ValueError):
            verify_turns(response, ['two', 'one'])
        with self.assertRaises(ValueError):
            verify_turns(response, ['one', 'two', 'three'])
        response['result']['data'][1]['status'] = 'inProgress'
        with self.assertRaises(ValueError):
            verify_turns(response, ['one', 'two'])
