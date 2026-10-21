# Phase 6: four isolated workflows, two rounds of five edits

The user authorized baseline, Caveman, Ponytail and Serena, five sequential edits per workflow and then a second independent round. Plan remains excluded. This is eight independent trajectories and forty task executions in one newly frozen cohort. Prior two-edit results and failures remain historical observations; they are not pooled with this cohort.

## Selected tasks and round order

Each trajectory receives exactly this sequence, one task at a time:

1. `milestone_seed_5f5da48_1_sub-01`: nested glob alternates.
2. `milestone_seed_5f5da48_1_sub-02`: unclosed character-class toggle.
3. `milestone_seed_2924d0c_1`: WalkBuilder min_depth.
4. `milestone_seed_b610d1c_1`: global gitignore with absolute paths.
5. `milestone_seed_8c6595c_1`: after-context performance fixes.

Strong prerequisites are ordered within the subset: task 1 before task 2, task 3 before task 4. Selection validation checks both dependency CSVs for all incoming Strong edges. These are mixed glob/ignore/search changes, not five artificially repeated copies of the same task. Dataset SRS, classifications, images and dependencies are pinned. The additional three grader images were explicitly approved by the user, with a recorded 618,480,384-byte incremental compressed-layer budget.

Round 1 completes Serena, baseline, Caveman and Ponytail, each through five edits, before round 2 starts the same sequence. Serena runs first to test real memory continuity early. The order is fixed and not randomized. A service limit or infrastructure failure stops scheduling; no paid fallback or silent fresh-session restart is permitted. Each model call receives a fresh quota check. The previously authorized percentage override remains; actual service rate-limit flags still stop inference.

## Isolation and memory

Every trajectory uses a new protected Docker workspace and Codex thread, starting at the same pinned source tree. No host instructions, host skills or external-data tools are inherited. Each turn exposes only its current task. Source commits and executor context accumulate only within that trajectory. The second round starts with a fresh repository/session and cold memories. Submission tags must remain immutable; later commits descend from earlier ones.

Serena uses its pinned local MCP profile plus `profiles/serena_continuous/AGENTS.md`. Its first shell operation is the exact verified task-file read, then Serena instructions, cold onboarding, nonempty semantic navigation and memory write precede other source/shell operations. Subsequent turns read an existing memory, navigate real symbols and write memory without repeating onboarding. The full filename/content SHA/byte inventory must match the preceding checkpoint before each warm turn. Mere MCP registration or server startup is insufficient.

`.serena/` is trial-local ignored state, excluded through `.git/info/exclude`, never committed or included in source snapshots. The runner saves a separate text-memory checkpoint after every completed turn, with before/after inventories, measured successful tool calls and continuity proof. Codex/MCP processes may restart between turns; the same executor thread and persistent container files preserve context and memories. No memory is transferred to another variant or round.

## Metrics and lifecycle

The unchanged upstream source masking, snapshot capture, evaluator and scoring remain in use. Grading and Sonar run after every edit; results never enter model prompts or memories. Production churn/net compare each submitted tree with its trajectory's original tree. Per-step counters are differences of cumulative thread totals; plots sum those step counters and average independent rounds at each edit count. Min/max and n remain visible. Failed or absent measurements stay explicit. Same-cohort paired deltas use the matching baseline round, and await its result if it has not run yet.

Raw Git bundles, session traces, snapshots and memory checkpoints remain in durable ignored results directories. Textual incremental/cumulative patches and replay hashes are refreshed from immutable submissions. Register updates happen after each state transition and analysis. Host-wide quota and disk limits can require pauses; this forty-task matrix is expected to take several hours, not a short smoke test.

The strengthened immutable Phase 5b registry policy remains unchanged. Model, CLI, runtime, hooks, Serena policy and Sonar rules are frozen before inference. Any required implementation repair after inference creates a new cohort rather than silently combining unlike conditions.
