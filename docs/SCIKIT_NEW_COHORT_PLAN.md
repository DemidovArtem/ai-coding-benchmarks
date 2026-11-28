# Proposed fresh scikit-learn cohort

Prepared on 28 November 2026 following the maintainer's request to plan a new
environment and a separate cohort. **Planning only:** image acquisition, builds,
activation inference and measured trials have not been authorized by this plan.

## Cohort boundary

Use `scikit-five-method-v2` as a new cohort, with a distinct results prefix,
prepared-source directory, common source bundle, native sessions, memory and
Sonar baseline. The target is **60 new submissions: five methods × two cold
repetitions × six sequential tasks**. Progress starts at 0/60. Keep the three
original first-step results and failed Serena attempt as a historical pilot;
never count them toward, restore their sessions into, or average them with v2.

Keep the dataset commit, source preparation, tasks and evaluator unchanged:
M06, M11, M12.1, M12.2, M01, M03. Keep Codex 0.163.0, gpt-6.1-sol/high and
ChatGPT OAuth. Retain Ponytail 5.3.2/full, Caveman v4.0.1/full, Serena 1.6.1 and
offline ECC 2.2.3. Unavailable model access stops the preflight; it does not
authorize an upgrade or paid fallback.

## One independently reproducible runtime

Create one new recipe based directly on the pinned scikit-learn `base-offline`
image. It must not use the deleted historical Rust/semantic runtime image IDs as
build stages. Reuse the retained local Codex distribution, Python 3.13.14,
Serena and its installed dependency closure, Pyright 1.1.403 and reviewed Node
binaries. The available Serena environment still matches all 72 recorded
distribution versions; all 4,764 retained Pyright inventory entries match.
Freeze a new complete file inventory rather than claiming old image identity.

Include both Node binaries in the **same image for every method**:

- `/opt/experiment-node/node`: retained 24.19.0 for the existing Ponytail/Caveman
  dispatchers and Python language-server wrapper.
- `/usr/local/bin/node`: retained 24.22.1 required by the existing ECC installer.

This preserves the reviewed hook manifests without silently replacing their Node
pin. Freeze exact `sudo`/`iptables` package versions, dependency files and hashes
before the build; stage any missing packages through a separately budgeted
download. Build from the prepared context with network disabled. Do not copy
host settings, projects, credentials, memories or unrelated caches into it.

Before measured inference, save the final image, build context/inventories and
package closure in a durable ignored archive on the workspace filesystem.
Verify archive hashes and image configuration/layer identity. The image archive
must remain protected from cleanup until the cohort and publication are done.
This prevents another Docker-cache cleanup from removing the only runtime copy.

## Resources and acquisition gates

Retained digest-verified manifests give these **compressed** layer estimates;
revalidate metadata and actual cache residency before requesting each download:

| Acquisition | Estimated unique compressed bytes |
| --- | ---: |
| Base plus first-task M06 grader | 4,005,763,625 |
| All seven upstream images together | 14,464,358,957 |
| Conservative extra task layers for repetition two after grader eviction | 13,629,355,227 |

With task-by-task eviction, total image traffic may approach 28.1 GB across two
repetitions, before package downloads or failed transfers. These values are not
expanded disk or peak-usage guarantees. Do not acquire the complete set at once.

First request only the pinned base/M06 pair and any missing small package closure,
with exact digests, sizes and local-cache deductions. Keep the common runtime and
current-task grader. Before later tasks, budget the next grader, expansion,
active agent/evaluator writable layers, analysis staging and archive space.
Preserve at least 12 GB on the Docker filesystem and 1 GB in the workspace.
If the next peak cannot fit, stop for a storage decision rather than pruning
checkpoints, the runtime archive, Sonar volumes or other projects.

## Preflight, execution and collection

Reuse the existing scikit runner and collectors. Add only the configuration/path
parameters needed for a distinct cohort, data-driven method/task/repetition
schedule and ECC's existing installer/native-tree accounting. Do not copy a new
phase-specific runner. Preserve the old protocols/configs; freeze new inputs and
implementation provenance only after v2 preflight passes.

First run zero-model checks: runtime inventory, clean baseline, quarantine,
unprivileged hook commands, offline Python semantic call, unchanged-source grader,
source filter and fresh Python Sonar base. Recheck the known historical M06
missing-P2P limitation and disclose the actual new baseline counts. A broken
grader is a blocker, not permission to alter tests or scoring.

Then, subject to explicit execution authorization and available quota, use short
neutral cold/resume activation checks for all five methods. Verify real hook
context and skill reads, Serena semantic calls and warm memory, and ECC skill
use, one configured explorer, deduplicated parent/child usage and complete native
tree/memory restore. These setup turns are excluded from measured task metrics.

Measured order is baseline, Caveman, Ponytail, Serena, ECC for task one; repeat
that order for each task through task six. Only then start repetition two cold.
Every method/repetition gets isolated source, root/child sessions and memories.
Reuse its exact previous checkpoint between tasks; do not deliver grader/Sonar
feedback. Preserve all attempts and recover only technical failures under the
existing roadmap rules. Hold the next task until current-task blockers resolve.

After every step, retain source bundles/patches/snapshots, closed native stores,
complete native agent trees, memory, original grader evidence, usage and Sonar.
Validate before removing the disposable container. Update the live register and
five-method curves at each edit count, averaging only independent v2 repetitions.
Missing values remain missing; n=2 is exploratory, not a significance claim.

## Acceptance and next decision

Implementation is ready for measured dispatch only when the common image and
durable archive are verified, all five activation/continuation checks pass,
the unmodified grader is infrastructure-valid, the fresh Sonar baseline is
verified, and the new protocol/config are frozen. The unchanged-source grader
need not return `resolved=true`; retain its actual baseline failure/missing
counts. Each substantial download still needs separate approval in Codex;
Telegram carries notifications only.

After the 60 submissions and result publication, continue the already agreed
framework simplification. This proposal does not start that refactor early.

[Machine-readable proposal](../reports/scikit_new_cohort_plan.json) ·
[Historical recovery audit](../reports/scikit_recovery_audit.json) ·
[Main roadmap](ROADMAP.md) · [Live register](../EXPERIMENT_STATUS.md)
