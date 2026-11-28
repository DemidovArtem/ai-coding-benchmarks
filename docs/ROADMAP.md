# Benchmark completion and framework roadmap

Authorized on 28 November 2026. This roadmap records the current objective;
historical frozen protocols, input hashes and failed attempts remain unchanged.
The [live register](../EXPERIMENT_STATUS.md) is generated from retained records.

Latest decision: implement the approved [fresh-cohort plan](SCIKIT_NEW_COHORT_PLAN.md).
The new 0/60 matrix excludes the three historical submissions. Builds, activation
and measured inference are authorized subject to readiness and quota gates.
The pinned base + M06 pair is verified (4,005,763,625 unique compressed bytes).
After all five M06 results completed, the maintainer separately approved one
pinned M11 grader: 1,421,510,719 new compressed bytes, as recorded in the
[M11 budget](../reports/scikit_v2_m11_image_budget.json). Later graders still
need separate approval.

## Deliverables and order

| Stage | State | Acceptance condition |
| --- | --- | --- |
| Durable coordination and Telegram | Schedule and delivery verified | [Preflight evidence](../reports/coordination_preflight.json): persisted roadmap heartbeat, verified private recipient, dry-run, delivered test and sender tests. Reboot/quota recovery remains untested. |
| Ripgrep ECC audit | Verified without new inference | [Retained evidence audit](../reports/ecc_activation_audit.md) verifies measured activation, native agent tree, memory, usage, source ancestry and checkpoint hashes for all six submissions. |
| Scikit-learn environment | Fresh-cohort implementation authorized | [Recovery audit](../reports/scikit_recovery_audit.json): original image absent, three historical checkpoints verified. [New proposal](SCIKIT_NEW_COHORT_PLAN.md) uses one independent common runtime; base + M06 verified; new common runtime built and durably archived, offline Python MCP verified. |
| Scikit-learn ECC preflight | All five cold/disposable-resume checks verified | Reuse the pinned ECC profile; verify Python activation, child-session accounting, complete native-tree restore and trajectory-local memory. |
| Scikit-learn matrix | Fresh cohort frozen; see live register for measured progress | Five methods, two cold repetitions, six sequential tasks; collect every source/session checkpoint, usage, grading and Sonar result. |
| Results publication | Pending matrix completion | Publish five-method curves, observed sample counts, deviations and missing scores; verify public analysis reproduction. |
| Framework simplification | Deferred until results are published | Shared CLI and orchestration; configuration-driven tasks/models and profile registry; Rust/Python adapters; fixture-proven extension with less duplicated execution code. |

Verified preservation work has also removed three completed ECC smoke containers,
recovering approximately 2.17 GB after archive verification. See the
[cleanup receipt](../reports/storage_cleanup_20261128.md). Checkpoints and other
projects' resources remain intact.

### Experiment scope

Ripgrep's ECC trajectory has already completed six edits. Audit it; do not rerun
it, add its second repetition, or execute the prepared seventh task. Smoke
activation and measured task usage must remain distinct. Existing false
activation fields are not proof of absence: report what native evidence actually
establishes without replacing the original records.

Scikit-learn uses baseline, Caveman, Ponytail, Serena and ECC, in that order.
The task sequence remains M06, M11, M12.1, M12.2, M01, M03. Finish every method on
a task before advancing; finish repetition one before starting repetition two
from the identical clean base. The original three first-step submissions remain
a separate historical pilot. The proposed fresh cohort starts all 60 steps from
zero, without restoring historical source, sessions or memories. Serena's old
quota failure remains in history; it is neither a new-cohort result nor an
independent repetition. The fresh cohort is authorized, subject to the recorded readiness gates.

Preserve the existing offline ECC 2.2.3 source, official instructions and roles,
model and reasoning overrides. External MCP, web lookup, remote plugins and
connected apps remain disabled. Do not upgrade the historical Codex 0.163.0,
gpt-6.1-sol/high or dataset pins. Freeze a separate five-method protocol and input
manifest before inference, preserving the original protocol and hashes. Never
join old and new trajectory segments or pool different cohort fingerprints.

## Operational rules

- Use the existing ten-minute heartbeat in this chat. Before dispatch, inspect
  the active goal, a shared trial lock, actual processes and containers. A stale
  PID, lock file or progress record is not proof that a process is alive.
- At 2% or less remaining in the five-hour window, exhausted weekly quota or
  unavailable quota evidence, preserve state and wait. Do not kill a running
  model turn merely because the boundary threshold was reached. No paid API,
  alternate account or model fallback is authorized.
- Recover only technical failures automatically: connectivity, quota waits and
  collection/evaluation of the same captured source. Preserve attempts and
  context. Changes to tasks, reasoning history, model, evaluator, quarantine or
  experimental conditions require the maintainer's decision in Codex.
- A blocked method does not prevent collecting the other methods on the same
  task. Do not advance to the next task until the blocker is resolved.
- Send Telegram notifications through the existing OpenClaw server CLI. Keep
  bot credentials on that server. Resolve a unique existing private recipient;
  ask in Codex if ambiguous. Telegram is outbound only: decisions belong here.
- Notify only on actionable blockers, required decisions, recovery after a long
  interruption or a completed stage. Include the trial/checkpoint, reason,
  decision options and chat link. Retain unsuccessful deliveries and suppress
  duplicates; reconcile uncertain sends before retrying.
- Local scheduling requires the computer and Codex app to be running. It does
  not execute work while the laptop is powered off.

### Notification command

The prepared host keeps the private SSH destination, identity-file path and
verified positive private-chat ID in ignored `results/notifications/config.json`:
`ssh_host`, `identity_file`, `telegram_target`. No bot token is copied locally.
Use a curated operational summary, not raw logs or credentials, as the message.

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.notify \
  --config results/notifications/config.json \
  --event UNIQUE_STABLE_EVENT_ID --message-file /path/to/private-summary.txt
```

Add `--dry-run` to verify routing without delivery. The private `events/`
directory next to the configuration retains receipts and unsuccessful sends.
A confirmed event is not sent again. A timeout, interrupted send or missing
receipt has an uncertain outcome and is not automatically repeated: inspect the
OpenClaw/Telegram delivery record before retrying. A failed SSH process start is
safe to retry. Local deduplication cannot provide a distributed exactly-once
guarantee when the server sends but the connection loses its acknowledgement.

## Preservation and storage

Keep only the common runtime and current-task grader when feasible. Before each
substantial acquisition, disclose pinned digests, new compressed layer bytes and
expanded peak/reserve estimates in Telegram; obtain the decision in Codex. Keep
at least 1 GB free in the workspace and 12 GB on the Docker filesystem. Do not
download the complete image collection at once.

Remove only identified benchmark-owned, reconstructible resources after
verification: finished containers, temporary analysis copies, obsolete graders
and associated build cache. Never use a global prune. Keep source bundles,
snapshots, closed native SQLite, histories, memories, records, Sonar volumes and
other projects' assets. Checkpoint verification precedes container deletion;
retaining public patches alone is insufficient for native-session recovery.

## Reporting and framework completion

After each launch, collection, failure or plan change, update authoritative
records and regenerate `EXPERIMENT_STATUS.md`. Preserve all historical attempts.
Average independent repetitions at each edit count; display all five methods
together per metric, actual n, missing values and observed ranges. Keep languages
and frozen cohorts separate. Two repetitions remain exploratory, not a powered
significance test. Commit and push verified stages without private raw artifacts.

Only after the benchmark results are published, replace phase-specific execution
with one `python -m experiment` CLI for validation, the next step, resume, analysis
and cleanup (dry-run by default). Reuse the existing evaluator and checkpoint
logic. Configuration selects repository/tasks, profiles, model/effort, repetitions,
runtime and resources. A small profile registry owns installation, activation,
memory and usage differences. SWE-Milestone owns task preparation and evaluation;
Rust and Python adapters retain language-specific footprint/Sonar behavior.

Prove with fixtures that adding a supported task, profile or Codex model does not
require editing the common runner. Test recovery, exact parent selection,
isolation, append-only attempts, token deduplication and unchanged public analysis.
Record executable LOC/duplication before and after consolidation. Preserve old
execution via recorded Git commits and reproduction instructions, without
rewriting frozen protocols or hashes. Do not add plugin discovery, a new service,
UI or second AI client; no additional large inference run is required for this
framework acceptance check.
