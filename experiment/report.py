"""Export every collected trial, with conservative paired baseline comparisons."""

import argparse
import csv
import json
from pathlib import Path


FIELDS = ("trial_id", "repo", "milestone_id", "variant", "repetition", "starting_commit", "ending_commit",
          "resolved", "added_prod_loc", "deleted_prod_loc", "net_prod_loc", "churn_prod_loc", "changed_prod_files",
          "cumulative_prod_loc", "failure_category", "duration_seconds", "planner_input_tokens", "planner_output_tokens",
          "executor_input_tokens", "executor_output_tokens", "executor_cached_input_tokens", "sonar_analysis_ok")


def paired_key(row):
    return tuple(row.get(key) for key in ("repo", "milestone_id", "repetition", "starting_tree",
                                          "dataset_version", "model", "reasoning_effort", "setup_fingerprint"))


def export(rows, directory):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
    with (directory / "results.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            flat = dict(row)
            for phase in ("planner", "executor"):
                usage = row.get("usage", {}).get(phase, {})
                flat.update({phase + "_" + key: usage.get(key) for key in ("input_tokens", "output_tokens", "cached_input_tokens")})
            flat["sonar_analysis_ok"] = row.get("sonar", {}).get("analysis_ok")
            writer.writerow({field: flat[field] if isinstance(flat.get(field), str) else json.dumps(flat.get(field))
                             for field in FIELDS})
    baselines = {}
    for row in rows:
        if row.get("variant") == "baseline":
            baselines.setdefault(paired_key(row), []).append(row)
    text = ["# Experiment results", "", "All collected trials are retained, including failures. Missing values are `null`.",
            "Dependent milestones form trajectories; they are not independent statistical samples.", "",
            "| Trial | Variant | Resolved | Production + / - | Churn delta vs baseline | Failure |",
            "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        candidates = baselines.get(paired_key(row), [])
        complete_key = all(value is not None for value in paired_key(row))
        baseline = candidates[0] if len(candidates) == 1 and complete_key else None
        delta = None
        if baseline and row.get("churn_prod_loc") is not None and baseline.get("churn_prod_loc") is not None:
            delta = row["churn_prod_loc"] - baseline["churn_prod_loc"]

        def cell(value):
            return str(value).replace("|", "\\|").replace("\n", " ") if value is not None else "null"

        values = (row.get("trial_id"), row.get("variant"), row.get("resolved"),
                  f'{cell(row.get("added_prod_loc"))} / {cell(row.get("deleted_prod_loc"))}', delta,
                  row.get("failure_category"))
        text.append("| " + " | ".join(map(cell, values)) + " |")
    text += ["", "Paired deltas require one baseline with identical task, repetition, starting tree, model, effort, dataset and setup fingerprint.",
             "A delta does not imply correctness. Inspect correctness and footprint together; no failed rows are dropped.",
             "Sonar data and raw grader/usage/profile details remain in JSONL. Missing Sonar is not a zero score.",
             "Token counts are not ChatGPT subscription prices or precise quota costs. Small pilots do not support broad generalizations.", ""]
    (directory / "summary.md").write_text("\n".join(text))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    export([json.loads(line) for line in args.input.read_text().splitlines() if line.strip()], args.output)
