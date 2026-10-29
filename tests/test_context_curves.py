import unittest
from reports.plots.context_curves import NOTE, annotated_footer

class ContextFooterTests(unittest.TestCase):
    def test_only_current_sixth_step_footer_is_annotated(self):
        current = 'Churn/Net values\nПравка 6: retained prefix'
        self.assertEqual(annotated_footer(current, True), current+'\n'+NOTE)
        for text, enabled in ((current, False), ('Chart title', True), ('Churn/Net historical cohort', True)):
            self.assertEqual(annotated_footer(text, enabled), text)
