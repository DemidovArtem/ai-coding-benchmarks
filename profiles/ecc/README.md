# ECC for Codex, offline

This profile evaluates the official native Codex plugin from ECC 2.2.3. Its
source commit, annotated tag, Node hash, dependency lock, runtime image and
overrides are recorded in `manifest.json`. The repository contains the profile
and upstream MIT license; fetched source, dependencies, runtime files and raw
sessions remain under ignored directories.

The three official Codex role instructions are retained. Their model settings
are overridden to `gpt-6.1-sol` with `high` reasoning effort. The runtime uses
Codex 0.163.0 and the original ripgrep base. This is a separate cohort: its
rebuilt Node runtime differs from the historical Serena runtime.

## Preparation

Fetch `affaan-m/ECC` at the manifest's commit into `vendor/ECC`. A sparse checkout
needs the manifest's `source_paths` and `.codex/agents` for source review. Install
runtime dependencies with `npm ci --omit=dev --ignore-scripts --no-audit
--no-fund --no-bin-links`; preserve the upstream tracked files and verify the
lock hash. No package lifecycle scripts are required. Build `Dockerfile` from
a local context containing the retained `codex-release` and the hash-verified
Node executable. No build network or replacement CLI is needed.

`experiment.ecc.install` first verifies the clean baseline, then registers the
native marketplace/plugin inside the container. It copies this profile and
roles, disables the bundled external MCP server, and hashes every installed
source/dependency file. Global host Codex settings are never changed.

For the standalone activation check:

```sh
python -m experiment.ecc --smoke --config reports/ecc_experiment.json \
  --output results/ecc_preflight/native_smoke_NEW
```

The host command must use the pinned Codex 0.163.0 executable on `PATH` and the
project's prepared Python environment. Existing output directories are refused.
This command performs real OAuth inference on a neutral read-only fixture.
It does not run a benchmark task. Failed attempts are retained, not overwritten.

## Verified behavior and limitations

The native activation audit verifies a supplied ECC skill, an actual skill read,
the SessionStart-injected Rust project context, and one real configured explorer.
Native records prove the model and effort. A separate continuation smoke proves
the same root thread, retained memory and closed SQLite checkpoint capture.

Parent CLI token counters exclude the explorer's consumption. The profile sums
unique native response IDs across the root and children and checks the sums
against native thread counters. Missing or inconsistent counters stay missing.
Forked copies are deduplicated. The upstream newest-rollout identity heuristic
selects a child after delegation, so this profile explicitly selects the single
root thread from native metadata.

Hook commands run unprivileged after source review, using the existing
invocation-scoped hook trust flag. The benchmark's sandbox bypass is confined
to its protected container; child runtime permissions inherit that bypass even
though the official role files request read-only access. Native hook support
does not imply Claude Code hook parity. External MCPs, web search, connected
apps and remote plugin discovery remain disabled.

The measured interface remains:

```sh
python -m experiment.continuous trial --config reports/ecc_experiment.json \
  --variant ecc --repetition 1
```

It requires frozen inputs and successful activation, and implements one
six-task trajectory. The source, session tree and ECC memory continue between
tasks. At 2% or less of the five-hour quota, the host process waits. A service quota
interruption resumes the same root after quota recovery and after all previous
agent processes exit. Other errors stop the sequence and retain evidence.

See `reports/ecc_protocol.md` and `reports/ecc_smoke.json`. Public analysis,
fresh inference, and native continuation are separate reproduction boundaries.
