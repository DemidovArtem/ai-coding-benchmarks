import json
import unittest
from experiment.phase6f_ponytail_context_resume import REJECTED_ITEM, remove_rejected_reasoning

class OneReasoningAmendmentTests(unittest.TestCase):
    def test_only_exact_reasoning_record_is_removed_without_reencoding_survivors(self):
        first = b'{"type": "session_meta", "payload": {}}\n'
        last = b'{ "type":"event_msg", "payload":{"type":"task_complete"}}\n'
        target = (json.dumps({'type':'response_item','payload':{'type':'reasoning','id':REJECTED_ITEM,'encrypted_content':'opaque'}})+'\n').encode()
        self.assertEqual(remove_rejected_reasoning(first+target+last)[0], first+last)
        for raw in (first+last, first+target+target+last, first+target.replace(b'"reasoning"',b'"message"')+last):
            with self.assertRaises(ValueError): remove_rejected_reasoning(raw)
