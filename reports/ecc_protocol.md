# ECC for Codex: six-edit activation-gated pilot

This is a new experiment, not an extension of the historical skill cohorts.
One cold ECC trajectory implements the first six milestones selected in the
retained ripgrep Phase 6 protocol, in their existing dependency order. There is
one repetition. Each step continues its predecessor's source and Codex session.

## Fixed conditions

- Codex CLI 0.163.0, gpt-6.1-sol, high reasoning effort, ChatGPT OAuth only.
- ECC 2.2.3, source commit `c05b2d6614f62f6db0047669aa4eefb223d478f9`.
- Official native Codex plugin, SessionStart hook, and three official Codex roles.
  Role instructions are retained; model and effort are overridden consistently.
- The existing protected ripgrep quarantine remains mandatory. Web search,
  browser tools, connected apps, remote plugins, and the bundled external MCP
  server are disabled. This evaluates **ECC for Codex, offline**, not Claude Code
  feature parity or every skill's external integration.
- The locally rebuilt runtime uses the original pinned ripgrep base and retained
  Codex binary. Node is 24.22.1. The old Serena runtime was removed during host
  cleanup; this runtime difference prevents matched historical A/B claims.

## Activation gate

Before any measured task, a separate neutral fixture must establish native plugin
registration, available skills, actual SessionStart execution, and a real
configured subagent with the pinned model and effort. Registration alone is not
activation. Preserve failed setup attempts and activation evidence separately
from measured results. If a required capability fails on the fixed CLI, record
the reason and withhold all measured tasks; do not upgrade CLI or replace ECC
with custom prompts.

Inspect parent and child rollouts to determine whether parent token counters
include child consumption. Count each stream once; leave unverified totals
missing. Activation calls are setup overhead, not benchmark observations.

## Continuation and measurement

Start from the retained common source tree. Use `codex exec resume` for subsequent
task dispatches, preserving prior submission tags and exact ancestry. Retain ECC
notes under `/home/fakeroot/.ecc`, outside source. Preserve source bundles,
incremental and cumulative patches, exact snapshots, native parent/child session
stores, plugin/configuration hashes, activation logs, and memory at each boundary.
Never feed grader or SonarQube output back to the agent.

At 2% or less remaining in the 300-minute quota window, the calling process waits,
retaining its container and sessions. Observe quota at most once per minute and
resume only after a fresh successful observation. Do not kill an active model
turn at that threshold. Other failures preserve evidence and stop the sequence;
no automatic trial replay or context replacement is allowed.

Report tokens, elapsed model time, production LOC/churn, unchanged upstream
grading, and Rust SonarQube deltas using the retained measurement policies.
Plots use edit count as the horizontal axis. With one trajectory there are no
uncertainty bands or statistical significance claims. Historical curves may be
shown only as explicitly separate descriptive references.

## Reproduction boundary

Profile configuration and protocol are public. Private OAuth, raw sessions,
checkpoint bundles and local runtime files remain ignored. Public analysis
reproduction, fresh inference, and native continuation are distinct checks;
success of any one does not certify the others. Current progress is recorded in
`EXPERIMENT_STATUS.md` and the activation report.

## Six-step evaluation policy

Steps 1–3 retain the original grader pruning setting (disabled). Steps 4–6 use
the previously validated upstream residue-pruning switch. The fifth task has a
known undeclared `max_matches` dependency in its grader: preserve its raw failure
and mark correctness unknown while retaining source, usage and quality metrics.
Only that exact known error may continue; other infrastructure failures stop.
No grader details are sent to the model. Task order and SRS remain unchanged.

The restored Sonar server, scanner, Rust analyzer and active rules retain their
original pins. Clippy was rebuilt after cleanup with the exact same 1.88.0
versions. Its new image ID is recorded in `ecc_sonar_setup.json`, with a separate
`ecc_sonar_protocol.json` and freshly measured common base. Historical analysis
protocols and baseline measurements are not replaced.
