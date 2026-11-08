# Second repository: scikit-learn replication plan

**Authorized scope: 5 November 2026; continuation authorized 8 November. Status: initial-task preflight complete; protocol frozen before measured inference.**

Publication of the ripgrep pilot is the first priority. The second experiment uses `scikit-learn_scikit-learn_1.5.2_1.6.0` from the same pinned SWE-Milestone dataset (`3500478e740d42583277c2658aa7729eb36e10f4`). It is a new cohort, never a continuation of ripgrep source or model sessions. The previously approved seventh ripgrep task remains prepared and unexecuted while this work takes priority.

## Matrix and order

Configurations: **baseline, Caveman, Ponytail, Serena**. Each gets **six successive source tasks and two independent repetitions**: eight independent trajectories, 48 planned step submissions. Plan/goal-plan and combinations remain excluded.

For repetition 1, run task 1 for baseline, Caveman, Ponytail, and Serena; then task 2 in the same method order; continue through task 6. Finish that repetition before starting repetition 2 from the identical clean base. Each invocation is serial, with a host checkpoint barrier before the next. Task order is a source-dependency constraint; method order is fixed and its potential time/order confounding must be disclosed.

The frozen dataset's first six topologically ordered nodes form a Strong-dependency-closed prefix:

| Step | Milestone | Change |
| --- | --- | --- |
| 1 | M06 | Array API Support for Metrics and Preprocessing |
| 2 | M11 | Missing value support for ExtraTree estimators |
| 3 | M12.1 | Infrastructure Foundation Phase 1 |
| 4 | M12.2 | Infrastructure Foundation Phase 2 |
| 5 | M01 | Metadata routing for RFE and RFECV |
| 6 | M03 | Move Estimator Type to Tags |

This is a deterministic prefix selection before inference, not a selection based on model outcomes. Actual source/task and grader compatibility still require preflight. The tasks include infrastructure changes; this is a realistic sequence, not six interchangeable independent tasks. Source manifests, CSV hashes, image digests and compressed layer sizes appear in [the preflight record](../reports/second_repository_preflight.json).

## Isolation, continuity and measurements

All four methods must share one newly validated base runtime, model ID, reasoning effort, CLI version, source base, task sequence, evaluator, and resource limits. Retain the already pinned skill assets if compatible; freeze the final setup before any measured run. Do not silently reuse a Rust/ripgrep image for scikit-learn. Do not update an old cohort's pins to accommodate the new environment.

Each method/repetition has its own workspace, native session and checkpoints. Preserve source commits, tags, binary/text patches, closed native database backups and usage counters after each task. Serena starts with cold onboarding in both repetitions and retains only its own memories between steps. Confirm actual semantic calls, retained-memory reads and memory writes. Baseline receives no experiment hooks, MCP or inherited memory. No grader or Sonar feedback is sent to agents.

Correctness is primary: retain valid task acceptance and regression-test counts at each step, and report per-trajectory resolved counts over six tasks. Invalid infrastructure evaluations remain missing scores; failures and recoveries remain distinct attempts. Secondary measures are cumulative production churn/net, input/cache/output tokens, runtime, and within-repository Sonar deltas. The Python source/test filter and Python analyzer profile must be validated; the current Rust-only helpers are not proof of Python measurement support. Cython files need an explicit supported/excluded scope before freeze. Analyze scikit-learn separately from ripgrep; absolute Sonar metrics across languages are not a matched comparison.

With only two trajectories per method this remains a replication pilot, not a powered confirmatory study. Predefine the primary endpoint and practical effect before additional repetitions. Do not count six sequential steps as six independent samples or stop because a p-value becomes favorable.

## Resource and execution gates

Registry manifests were read without downloading image layers. Seven images (base-offline plus six graders) have **14,464,358,957 unique compressed layer bytes**, approximately 14.46 GB, compared with prior experiment manifests. This estimate is not an expanded disk requirement or proof of daemon cache residency. The first base/first-grader pair alone has about 4.01 GB of unique compressed layers.

Observed free space during preflight: approximately **18.53 GB on the Docker filesystem** and **2.67 GB in the workspace**. The full image set cannot be treated as safely fitting after expansion, build layers, results and reserves. No image layers have been downloaded. Do not delete unrelated images, move the Docker data root, or acquire the full collection without an approved storage plan and the handoff's separate download authorization.

A lower-peak alternative is to keep the shared base and only the grader for the active task, because each task runs across all four methods before the next task starts. The base plus first grader has 4,005,763,625 unique compressed bytes. Expanded peak occupancy remains unmeasured. Evicting old graders may require downloading their task-specific layers again in repetition two. This changes storage scheduling, not the task order or evaluation; it does not authorize deleting checkpoint/session state or unrelated Docker assets.

Before inference, complete: expanded disk budget or alternate approved storage; exact image acquisition approval; isolated runtime and semantic-server validation; unchanged offline grader smoke; Python footprint checks; common-base Sonar analysis; current model access/quota; and a frozen execution protocol with the step-first scheduler. An actual service refusal stops inference without paid fallback. No seventh scikit-learn task or additional repetition is authorized by this plan.

## Storage follow-up — 8 November 2026

Six old benchmark containers were removed after verified private source/session/memory backups and separate verification of all seven latest ripgrep checkpoints. This recovered approximately 13.99 GB; Docker free space reached 29.76 GB. No images, volumes, or unrelated projects were removed. The workspace partition still has only approximately 2.4 GiB available. See the [preservation audit](../reports/storage_cleanup_20261108.md).

The maintainer authorized proceeding after this cleanup. Start with the shared base and current-task grader, subject to free-space checks; do not acquire the full image collection at once. Runtime, grader, Python metrics, Sonar and semantic-tool preflight remain mandatory before measured inference. No new-repository result is claimed.

## Initial-task readiness — 8 November 2026

The base and M06 grader are acquired and digest-verified. A separate common runtime reuses pinned local Codex, Serena, Node and Pyright assets. Real offline Python MCP navigation, both unprivileged hook commands, the original unchanged-source grader and a snapshot-bound Python Sonar baseline have passed preflight. The harness suite passes 131 tests. These are setup checks, not measured method results. The unchanged M06 base already has 78 missing P2P tests; this limitation is retained. The [frozen execution protocol](../reports/scikit_protocol.md) defines Python/Cython scope, storage limits and per-trajectory source/session/memory continuation. Later-task images remain unacquired.
