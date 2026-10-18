import csv
import json
from pathlib import Path
import tempfile
import unittest

from experiment.metrics import codex_usage, normalize_grader
from experiment.report import export


class ResultTests(unittest.TestCase):
    def test_usage_counts_each_threads_cumulative_totals_once(self):
        def usage(amount):
            return {"type":"turn.completed", "usage":{"input_tokens":amount,"output_tokens":2,"cached_input_tokens":1}}
        result = codex_usage([{"type":"thread.started","thread_id":"executor"}, usage(10),
                              {"type":"thread.started","thread_id":"executor"}, usage(25),
                              {"type":"thread.started","thread_id":"planner"}, usage(5)])
        self.assertEqual(result["input_tokens"], 30)
        self.assertEqual(result["output_tokens"], 4)
        self.assertIsNone(result["reasoning_output_tokens"])
        self.assertEqual(result["session_ids"], ["executor", "planner"])

    def test_reset_or_missing_usage_is_unknown(self):
        self.assertIsNone(codex_usage([])["input_tokens"])
        result = codex_usage([{"type":"thread.started","thread_id":"same"},
            {"type":"turn.completed","usage":{"input_tokens":10}},
            {"type":"turn.completed","usage":{"input_tokens":2}}])
        self.assertIsNone(result["input_tokens"])
        self.assertTrue(result["anomalies"])

    def test_normalizer_preserves_upstream_failure_and_missing_values(self):
        raw = {"resolved":False,"error_message":"scanner failed","partial_custom_grade":0.5}
        result = normalize_grader(raw)
        self.assertEqual(result["grader_metrics"], raw)
        self.assertFalse(result["resolved"])
        self.assertIsNone(result["p2p"])
        self.assertEqual(result["failure_category"], "evaluation_failure")
        self.assertIsNone(normalize_grader({})["resolved"])

    def test_report_keeps_failures_and_refuses_unmatched_pairing(self):
        base = dict(repo="ripgrep", milestone_id="M1", repetition=1, starting_tree="tree", dataset_version="v1",
                    model="model", reasoning_effort="high", setup_fingerprint="same", churn_prod_loc=10,
                    usage={"planner":{"input_tokens":0},"executor":{"input_tokens":100}})
        rows = [dict(base,trial_id="base",variant="baseline",resolved=True),
                dict(base,trial_id="failed",variant="plan",resolved=False,churn_prod_loc=4),
                dict(base,trial_id="unmatched",variant="goal_plan",starting_tree="other",churn_prod_loc=1)]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            export(rows, directory)
            self.assertEqual(len((directory / "results.jsonl").read_text().splitlines()), 3)
            saved = list(csv.DictReader((directory / "results.csv").open()))
            self.assertEqual(saved[0]["trial_id"], "base")
            self.assertEqual(saved[0]["executor_input_tokens"], "100")
            self.assertEqual(saved[0]["planner_input_tokens"], "0")
            self.assertEqual(saved[0]["sonar_analysis_ok"], "null")
            self.assertEqual(json.loads(saved[1]["resolved"]), False)
            summary = (directory / "summary.md").read_text()
            self.assertIn("| failed | plan | False | null / null | -6 |", summary)
            self.assertIn("| unmatched | goal_plan | null | null / null | null |", summary)
