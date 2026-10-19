# Experiment results

All collected trials are retained, including failures. Missing values are `null`.
Dependent milestones form trajectories; they are not independent statistical samples.

| Trial | Variant | Resolved | Production + / - | Churn delta vs baseline | Failure |
| --- | --- | --- | --- | --- | --- |
| baseline_smoke_001 | baseline | True | 74 / 24 | null | null |
| phase2_baseline_001 | baseline | True | 79 / 29 | 0 | null |
| phase2_plan_001 | plan | True | 83 / 28 | 3 | null |
| phase2_goal_plan_001 | goal_plan | True | 93 / 24 | 9 | null |
| phase3_baseline_001 | baseline | True | 78 / 24 | 0 | null |
| phase3_ponytail_001 | ponytail | True | 70 / 22 | -10 | null |
| phase3_caveman_001 | caveman | True | 77 / 21 | -4 | null |

Paired deltas require one baseline with identical task, repetition, starting tree, model, effort, dataset and setup fingerprint.
A delta does not imply correctness. Inspect correctness and footprint together; no failed rows are dropped.
Sonar data and raw grader/usage/profile details remain in JSONL. Missing Sonar is not a zero score.
Raw Sonar snapshots include different inline test code. Aggregate Sonar deltas are not production-only quality effects; remediation effort is not measured human review time.
Token counts are not ChatGPT subscription prices or precise quota costs. Small pilots do not support broad generalizations.
