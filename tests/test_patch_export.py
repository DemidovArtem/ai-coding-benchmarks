import unittest

from reports.plots.export_patches import has_submission


class PatchExportTests(unittest.TestCase):
    def test_failed_grader_does_not_discard_a_verified_submission(self):
        row = {'trial_state': 'failed', 'continuous': {'trajectory_id': 'one'},
               'ending_commit': 'abc', 'snapshot_sha256': 'sha',
               'verified_snapshot_rust_files': 119, 'collection_errors': []}
        self.assertTrue(has_submission(row))
        self.assertFalse(has_submission({**row, 'snapshot_sha256': None}))
        self.assertFalse(has_submission({**row, 'collection_errors': ['snapshot mismatch']}))
        self.assertFalse(has_submission({**row, 'verified_snapshot_rust_files': 0}))
