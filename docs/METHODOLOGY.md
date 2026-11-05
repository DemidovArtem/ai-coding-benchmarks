# Methodology

Status: **5 November 2026**. This is an exploratory research prototype using SWE-Milestone tasks from the Rust repository ripgrep. It is not a full benchmark or a leaderboard.

## Experimental units and approaches

An isolated trial starts from the same pinned source tree and receives one task. A continuous trajectory receives successive tasks in the same executor session, retaining its own code and context. Independent repetitions start with separate repositories, sessions, and memories; no state moves between approaches or repetitions.

The active approaches are baseline, Caveman, Ponytail, and Serena. Baseline has no experimental skill hooks or MCP. Caveman and Ponytail use pinned native skill hooks. Serena uses semantic MCP tools and trajectory-local memories. Historical plan and goal_plan trials remain separate; they are excluded from the active continuous comparison.

The initial isolated pilot contains two frozen cohorts: Phase 2 planning and Phase 3 skills, each with its own matched baseline. The current continuous comparison has two six-step trajectories each for baseline, Caveman, and Ponytail, and one for Serena. These are seven independent trajectories, not 42 independent samples. See [results](RESULTS.md).

## Tasks and execution

All current trajectories follow the same measured task prefix:

| Step | SWE-Milestone task | Change |
| --- | --- | --- |
| 1 | `milestone_seed_5f5da48_1_sub-01` | Nested glob alternates |
| 2 | `milestone_seed_5f5da48_1_sub-02` | Unclosed character-class toggle |
| 3 | `milestone_seed_2924d0c_1` | WalkBuilder min_depth |
| 4 | `milestone_seed_b610d1c_1` | Global gitignore with absolute paths |
| 5 | `milestone_seed_8c6595c_1` | After-context performance fixes |
| 6 | `milestone_seed_a6e0be3_1_sub-01` | Max matches searcher migration |

The seventh task, JSON output replacement (`milestone_seed_292bc54_1`), is approved and preparing; **0/7** continuations are collected. It precedes Printer Cleanup because of a Strong dependency. Earlier tasks will not be replayed. See the [seventh-step protocol](../reports/phase6g_protocol.md).

Execution uses pinned Codex CLI 0.163.0, gpt-6.1-sol, high reasoning effort, and ChatGPT OAuth. Paid API fallback is forbidden. A host gate exposes one task at a time and checks quota, source/runtime pins, isolation, and disk reserves. Grader feedback and Sonar findings are withheld from the executor. Task order is fixed, not randomized.

The continuous overlay preserves Serena's original runtime cohort and the other methods' offline runtime cohort. The offline image stages the same retained Codex binary to avoid an unavailable installer. The overlay retains each cohort's means and does not create cross-cohort matched baseline pairs. Exact inputs appear in [run parameters](../reports/plots/run_parameters.md), [Phase 6c](../reports/phase6c_protocol.md), and [Phase 6f](../reports/phase6f_experiment.json).

## Measurements

| Measurement | Definition and boundary |
| --- | --- |
| Input, cached input, output tokens | Native executor counters; step usage is the difference from the preceding cumulative checkpoint. Input includes cached input. Curves accumulate step usage. |
| Production churn | Added plus deleted physical Rust lines relative to the trajectory's original commit. Intermediate churn values are not summed. |
| Production net growth | Added minus deleted production lines relative to the same original commit. |
| Production filtering | Upstream source metadata excludes tests, generated files, and vendor code; a pinned Rust AST filter removes inline tests. Physical LOC includes comments and blank lines. |
| Sonar static metrics | Snapshot-level ncloc, cyclomatic/cognitive complexity, duplication, maintainability issues, and remediation estimates; curves show deltas from a verified common base. |
| Correctness | Original grader decisions and test counts, with infrastructure-invalid evaluations distinguished from valid negative outcomes. |
| Serena usage | Successful measured MCP/semantic calls and memory inventories; activation smoke is not task usage. |

Sonar scans the exact submitted Rust snapshot, **including inline test differences and benchmark test masking**. Its deltas are not production-only quality effects. Remediation minutes are Sonar estimates, not measured human review time. New-code issue counts remain unavailable where reference semantics are unverified. See [Sonar protocol and limitations](../sonar/README.md).

## Grading and continuation exceptions

Original task evaluators and raw decisions are preserved. Step 3 has a documented exact-string regex branch-order mismatch; matching behavior may be equivalent, and this observation does not excuse other failures. Step 4 introduces explicitly recorded source-residue pruning and is not the same grading protocol as steps 1–3. Its remaining failures are not automatically classified as agent regressions. Step 5 evaluations are invalid because the grader requires an undeclared max_matches API. Step 6 evaluations are valid and all remain unresolved. Details: [step 3](../reports/phase6_grader_compatibility.json), [step 4](../reports/phase6d_progress.md), [step 5](../reports/phase6e_progress.md), [step 6](../reports/phase6f_findings.md).

Failures and recoveries remain separate records; a recovery does not add an independent repetition. Ponytail repetition 2, step 6, required removal of exactly one API-rejected encrypted reasoning item from a checkpoint copy, with explicit user authorization. Other retained records were verified unchanged. This observation remains in descriptive means with a visible context-deviation annotation; it is not a strict unchanged-history continuation. See the [amendment protocol](../reports/phase6f_ponytail_context_protocol.md).

## Aggregation, uncertainty, and artifacts

At each edit count, the plot reports the arithmetic mean of available independent repetitions, with n and min–max. Missing values stay missing. Bands are **not confidence intervals**. Paired deltas require a baseline from the same frozen cohort and repetition. Sequential points within a trajectory are dependent.

One repository, two repetitions for three methods, one for Serena, fixed ordering, runtime differences, and recovery exceptions limit inference. No p-values or statistical superiority claims are reported. New model runs are not assumed deterministic. More independent full trajectories and additional task chains/repositories are needed before generalizing; repetition counts should follow variance and a predefined primary effect size.

Tracked [plot data](../reports/plots/current_comparison.json), [parameters](../reports/plots/run_parameters.json), and [textual patches](../reports/patches/README.md) support inspection. Private ignored artifacts additionally retain source bundles, snapshots, native histories, closed database backups, and Serena memories. Patches restore code, not model context. The [live register](../EXPERIMENT_STATUS.md) preserves trials and failures; historical frozen cohorts are not rewritten.
