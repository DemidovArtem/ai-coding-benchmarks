# Scikit-learn five-method v2 protocol

Status: implementation and preflight; **not frozen for measured dispatch yet**.
Execution is authorized by the maintainer's 28 November 2026 decision, subject
to the [readiness gates](../docs/SCIKIT_NEW_COHORT_PLAN.md). The first image pair
is approved; later substantial grader acquisitions require separate approval.

## Separate cohort and inputs

Cohort `scikit-five-method-v2` starts at zero. Its 60 submissions comprise five
methods, two independent cold repetitions and six sequential edits. The three
historical scikit-learn submissions and failed attempts remain a separate pilot.
They supply neither native context nor source changes to v2 and are not pooled
with its results. Both cohorts use the same starting source commit/tree; the
common runtime has a new identity and therefore creates a new cohort boundary.

Repository: `scikit-learn_scikit-learn_1.5.2_1.6.0`, SWE-Milestone v1.0.2.
Dataset commit: `3500478e740d42583277c2658aa7729eb36e10f4`.

| Edit | Milestone | Task |
| --- | --- | --- |
| 1 | M06 | Array API Support for Metrics and Preprocessing |
| 2 | M11 | Missing value support for ExtraTree estimators |
| 3 | M12.1 | Infrastructure Foundation Phase 1 |
| 4 | M12.2 | Infrastructure Foundation Phase 2 |
| 5 | M01 | Metadata routing for RFE and RFECV |
| 6 | M03 | Move Estimator Type to Tags |

For each edit run baseline, Caveman, Ponytail, Serena and ECC serially, then
advance to the next edit. Start repetition two only after repetition one.
A blocked method permits its peers on the current task; it holds the next task.
Each method/repetition owns its source, root/child sessions and memories.

## Conditions and continuation

All methods share Codex 0.163.0, gpt-6.1-sol/high, ChatGPT OAuth and the
[common runtime](../profiles/scikit_runtime_v2/manifest.json). No paid endpoint,
model/account fallback, connected app, web lookup or remote plugin is enabled.
Profiles preserve reviewed versions: Caveman v4.0.1/full, Ponytail 5.3.2/full,
Serena 1.6.1 with Python/Pyright, and ECC 2.2.3 with the existing offline roles.
ECC's configured subagents use the same model and effort. Both Node binaries
are in the common image; activating a profile does not select another image.

Start every repetition cold. Subsequent tasks restore the exact previous
source bundle, tags, closed SQLite and native history. Single-root transport
uses the existing verified native-history restoration, preserving message and
reasoning bytes. ECC restores its entire root/child tree, closed databases and
`.ecc` state and compares native API turn boundaries for every session. Serena
restores only its own trajectory's memories; onboarding is cold-only. Never
supply grader or Sonar feedback to the model. Reject a changed parent cohort,
setup fingerprint, source ancestry or previous submission tag.

Keep source snapshots, full binary diffs, incremental bundles and the required
common bundle. Verify before deleting a container. Retain unfinished attempts;
never turn missing measurements into zeros. Automatically recover connectivity,
quota waits or collection/evaluation of the same snapshot only. Context edits,
task/model changes, evaluator changes and quarantine changes require a decision
in the benchmark's Codex chat.

## Evaluation and analysis

Keep the original evaluator, classifications, tests and quarantine. The new
zero-model preflight reproduces the known M06 baseline limitation: 78 missing
P2P tests. Its baseline is unresolved; this is infrastructure evidence, not an
agent failure. Retain all raw upstream decisions and counts.

Git metrics use the benchmark production-source filter. Python Sonar scans are
bound to captured snapshots and the frozen Python analyzer/rules; Cython is
outside Sonar coverage. Compare changes against v2's own common-base scan.
CLI token counters are cumulative per root. ECC totals instead sum deduplicated
native responses across the complete tree; the root counter excludes children.
Subtract the exact previous cumulative counter for step usage; absent fields
remain unknown. Retain parent-only counters alongside full-tree evidence.

Plot all five methods together per metric against edit count. Average only
independent repetitions within v2, with actual n and observed ranges. Separate
smoke activation from measured task usage, and separate Rust/Python cohorts.
Two repetitions are exploratory evidence, not a powered significance test.

## Gates and operational evidence

Before measured dispatch: verify the durable image archive, zero-model source,
quarantine, MCP, hooks, unchanged-source grader and fresh Sonar baseline; pass
all five neutral cold/disposable-resume checks; freeze configuration, protocol,
profile assets, implementation files, dataset inputs and all milestone SRS/test
classifications. Only then set `measurement_started` and the frozen stage.

Pause new model turns at <=2% remaining five-hour quota, exhausted weekly quota
or unknown quota. Keep an already active turn and its process/checkpoints.
The existing heartbeat resumes retained work, never a parallel copy. Maintain
12 GB Docker and 1 GB workspace reserves. Cleanup is limited to verified,
reconstructible benchmark resources; retain the common archive, checkpoints,
Sonar volumes and other projects' resources.

[Configuration](scikit_v2_experiment.json) ·
[Zero-model evidence](scikit_v2_preflight.json) ·
[Neutral activation evidence](scikit_v2_activation_preflight.json) ·
[Live register](../EXPERIMENT_STATUS.md)
