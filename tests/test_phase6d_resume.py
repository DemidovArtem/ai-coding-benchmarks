import json
from pathlib import Path
import tempfile
import unittest

from experiment.phase6d_resume import validate_failure


class FourthRecoveryTests(unittest.TestCase):
    def test_only_unsubmitted_quota_failure_can_resume(self):
        row = {'trial_state':'failed', 'ending_commit':None, 'variant':'ponytail', 'repetition':2,
               'continuous':{'step':4, 'executor_session_id':'01a16e63-039b-7653-aff4-bfd3ae7116af'}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'log').mkdir()
            log = root/'log/agent_stdout.txt'
            log.write_text(json.dumps({'type':'turn.failed', 'error':'usage limit'})+'\n')
            validate_failure(row,root)
            row['ending_commit']='submitted'
            with self.assertRaises(ValueError):validate_failure(row,root)
            row['ending_commit']=None
            log.write_text(json.dumps({'type':'turn.failed', 'error':'other error'})+'\n')
            with self.assertRaises(ValueError):validate_failure(row,root)
            log.write_text(json.dumps({'type':'turn.failed', 'error':'usage limit'})+'\n'+
                           json.dumps({'type':'turn.completed'})+'\n')
            with self.assertRaises(ValueError):validate_failure(row,root)
