# Phase 5: bounded sequential pilot

This is a new cohort, separate from frozen Phase 2 and Phase 3. The selected non-official trajectory contains `milestone_seed_5f5da48_1_sub-01`, followed by `milestone_seed_5f5da48_1_sub-02`. Both modify the glob parser, with a Strong FUNC dependency and no external incoming Strong prerequisites. The selection CSVs, both SRS documents, both classifications, implementation and profiles are pinned before inference.

The requested variants are baseline, Caveman, Ponytail and plan + implementation. The default schedule runs these four variants once, then repeats the same order for repetition 2: eight independent trajectories, sixteen task executions. Every trajectory starts a fresh protected container and Codex thread. Both steps within a trajectory retain the same repository, working tree and Codex thread through `codex exec resume`. There is no state transfer between independent trajectories.

All variants use the verified common runtime image `sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269`, Codex CLI 0.163.0, model `gpt-6.1-sol`, reasoning effort high, ChatGPT OAuth and the unchanged protected benchmark quarantine. Serena is not registered. Baseline has no skills; Caveman and Ponytail use their existing reviewed native hooks. Hook trust is granted only for those pinned hooks inside the container, including resumed invocations. No host configuration changes are required.

## Sequential delivery contract

The host drives a bounded sequence of completed turns, without the upstream background watcher. Only the current task exists in the executor container. Every turn begins by reading a root-owned read-only task file outside the repository; the exact tool output and task hash are checked. Subsequent task files are created only after the previous turn has stopped and its immutable submission has been captured. This mode retains conversation context but includes host pauses between turns; it is not an unattended full benchmark queue.

The plan variant runs one fresh read-only planner before each executor turn. The planner receives the current task and the exact source state at the previous submitted commit, without grader outputs or feedback. The existing bounded JSON validation, kernel read-only mount and separate-container/session checks apply. Only a validated handoff is included in the current task file. The executor's first shell read proves delivery. A preparation failure withholds the task from execution.

The upstream initial-history truncation, test masking, source filtering, immutable-tag snapshot capture, evaluator and scoring are reused. The host requires clean HEAD at each submission and verifies that the next submission descends from the previous one and preserves earlier tags. Missing tags, changed sessions, preparation failure, timeout or infrastructure failure stop that trajectory. A normal graded `resolved=false` remains an observed result and does not by itself prevent the next dependent step. The grader's decisions and files never enter the executor or planner prompt.

## Metrics and limits

Each step has its own metadata, original SRS prompt, delivered task/handoff proof, stdout, raw trace, immutable snapshot, Git bundle, grader result, hook audit and result record. Existing records and failures are preserved. Main production LOC metrics compare each step with the trajectory's initial source state; `continuous.incremental_footprint` compares it with the preceding submitted step. Later steps are dependent observations, not independent samples.

Codex counters are cumulative within a thread. Per-step token usage is the difference between consecutive completed-step totals; raw cumulative totals are retained. Missing counters stay null, and decreasing counters or changed thread IDs invalidate token collection. Planner usage is added separately for that step. Executor duration measures its invocation; setup, grading and Sonar durations remain separate. Sonar uses the existing frozen protocol on each graded snapshot. Its inline-test limitations still apply.

Trials run serially under the existing OS lock. A fresh quota read precedes every planner and executor invocation; stop at 85% in either account window. Required grader-image digests are checked before model use. `reports/continuous_image_budget.json` records their registry manifests and compressed sizes; their download needs the separate approval requested in chat. No image collection is downloaded.

Raw runtime output uses `/tmp/ai-coding-experiment`; terminal steps are copied to ignored durable `results/trials` before collection. Completed trajectory containers are removed after preserving their source and traces; failed trajectory containers remain for diagnosis. Existing finished-trial Cargo `target` caches may be discarded without changing source or recorded evidence. The new cohort reserves 1 GB on the workspace filesystem for small bundles and result files and 12 GB on Docker storage; the old frozen cohorts retain their original resource settings.

## Commands

Run from the repository root after tests, image approval/download and disk/quota preflight:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.continuous freeze
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.continuous trial --variant baseline --repetition 1
```

Repeat the trial command with `caveman`, `ponytail`, `plan`, then repetition 2, requiring terminal state and a fresh quota gate each time. A previously used step ID cannot overwrite a result. Do not silently start a fresh thread to recover a broken trajectory. Sonar runs separately through `experiment.sonar_scan` on each saved step, followed by collection refresh. The status register is regenerated after each launch, terminal step, analysis and plan change.
