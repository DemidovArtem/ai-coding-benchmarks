# Phase 6b: matched 2×5 matrix with upstream source-residue pruning

This is a new frozen cohort, separate from the interrupted Phase 6 pilot. It retains the user-authorized four workflows, five tasks per trajectory, two independent rounds, persistent Serena memories within a trajectory and cold memories between rounds. Plan remains excluded.

## Reason for a new cohort

Phase 6 reached four Serena submissions. Its fourth unchanged grader combined the submitted `crates/printer/src/hyperlink.rs` with historical `hyperlink/mod.rs` and `hyperlink/aliases.rs` from the grader image. Both END and START builds failed before valid test reports were produced. A zero-model replay of the identical snapshot with the existing upstream `SWE_MILESTONE_RESIDUE_PRUNE=1` switch removed those two residue source files and produced test reports. Original results, failures, source patches, thread and memories remain preserved. The replay is diagnostic, not another independent model observation.

Phase 6b enables that existing switch uniformly from the first grader of every trajectory. The upstream evaluator, scoring functions, classifiers, SRS, approved images, network quarantine, model, CLI, runtime and Sonar rules are unchanged. Every successful collection must show `residue_prune.enabled=true` and `enablement_source=environment-override` in the actual grader result. Test/fixture/generated/asset protections remain enforced by upstream pruning. No individual file is manually deleted to obtain a score.

The new grading setting is encoded in the benchmark configuration, giving a distinct setup fingerprint. No Phase 6 execution is counted as an independent Phase 6b observation. Every Phase 6b trajectory starts with a fresh container, repository, executor thread and cold Serena state. This costs additional model work, but avoids silently combining different grading conditions or claiming reused traces as independent repeats.

## Fixed schedule and isolation

Round 1 runs baseline, Caveman, Ponytail, then Serena, each through five sequential edits. Round 2 repeats that order with independent containers and sessions. Baseline runs first to establish the new comparison early. The five SRS tasks and their order are pinned in `phase6b_selection.json`: nested alternates, unclosed classes, min_depth, maintenance fixes, global gitignore. The after-context task is excluded: its injected tests require `SearcherBuilder::max_matches`, absent from the common source and its SRS. A synthetic zero-model probe exposed that undeclared API dependency. Maintenance fixes use an already approved local grader image; no additional images are downloaded. Global gitignore remains last, after min_depth. Existing dependency validation and task-by-task host dispatch remain in force. One model trajectory runs at a time.

Within a trajectory, source commits, immutable submission tags and executor context accumulate. Serena warm boundaries require exact filename/content SHA/byte agreement with the preceding memory checkpoint, followed by retained-memory reads, semantic navigation and memory writes. No host memories are imported and no grader feedback reaches the executor. Native Caveman/Ponytail activation and protected network verification remain mandatory.

Before the first model turn, source/config/image pins, quota, resource reserves and the zero-model grading compatibility evidence are checked. A timed-out quota observation is retried once, with the first timeout retained in the saved observation; this never retries a model invocation or an actual service-limit response. Actual quota refusal, grader infrastructure failure or invalid Sonar analysis stops further inference. A negative graded task result remains a measured outcome and does not trigger a manual source repair.

The compatibility preflight uses no new model calls. A conservative pruning dry-run on the first three already measured snapshots removes zero source files, preserving their grader input trees. For the replacement maintenance task and final global-gitignore task, separately labelled diagnostic clones compose existing measured implementations and verify that the unmodified graders compile and produce test reports. Reference controls are not independent observations and need not have positive raw scores; historical baseline/test-version differences remain visible. A task that introduces a named API may legitimately fail test compilation before implementation. Unlike after-context's undeclared `max_matches` dependency, maintenance's `SummaryKind::QuietWithMatch` requirement is explicitly present in its SRS.

## Reporting and interpretation

Every terminal step appends to the existing result register. Missing measurements remain missing; source patches are exported whenever an immutable submission and snapshot have been verified, including submissions whose grader failed. Means and paired deltas remain within this new setup fingerprint; independent rounds contribute to the same edit-count curves with n and min/max.

Raw and task-local filtered grader outputs are both retained. Raw scores remain canonical. Historical task graders can disagree about implementation details: the Phase 6 `re35` test expected opposite serialization orders for the equivalent `{a,b}` alternation in successive graders. Raw P2P failures/missing tests therefore require attribution before they can be called behavioral degradation. No post-hoc filtered-score substitution is made. Sonar still includes inline tests and benchmark masking; its aggregate deltas are not production-only quality effects.

The forty-step matrix is not complete when its runner starts. `EXPERIMENT_STATUS.md` records actual progress and failures; a stopped trajectory is never silently restarted under the same trial ID.
