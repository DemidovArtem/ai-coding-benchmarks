# Phase 3: isolated skill pilot on one common runtime

This cohort compares `baseline`, `ponytail`, `caveman`, then `serena`, in that deterministic order, once each on `maintenance_fixes_1_sub-01` in ripgrep. Every executor starts from the Phase 2 common starting tree in a fresh protected container. The model remains `gpt-6.1-sol`, reasoning effort `high`, Codex CLI `0.163.0`, with ChatGPT OAuth. There is no planner in this cohort and no cross-trial memory transfer.

All four variants use image `sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269`. This adds the same public Python/Node/Rust LSP prerequisites to every container. Baseline registers no hooks, MCP or experiment instructions; tools merely being present does not activate a profile. A new measured baseline is necessary: the older Phase 2 baseline has a different runtime and setup fingerprint.

Ponytail 5.3.2 uses its reviewed native SessionStart/UserPromptSubmit/SubagentStart hooks in full mode. Caveman v4.0.1 uses its pinned upstream Codex SessionStart hook in canonical caveman mode (the upstream alias for full). Both use a per-invocation hook-trust bypass only inside the protected container after source and runtime hash validation. Plugin and remote-plugin capabilities stay disabled.

Serena 1.6.1 registers exactly one required local stdio MCP server with `--context codex`, cold project state and a dedicated empty home. No host configuration or memories are copied. Telemetry, dashboards and paid token estimators are disabled. Onboarding time, tokens and any generated memories belong to the measured trial. The measured task does not request or force Serena usage; actual tool calls, onboarding observation and final memory count/bytes are collected separately.

Before freezing, all three profiles must pass actual OAuth activation smokes on this exact image ID. An additional offline, unprivileged MCP probe returns a Rust symbol with network disabled and no credentials. Activation-smoke usage is setup overhead, excluded from measured task comparisons. `experiment.skill_trial freeze` refuses incomplete or mismatched activation evidence, then pins runner/profile/proof files in a separate immutable configuration. It never overwrites the Phase 2 configuration.

Run one trial at a time, from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_trial freeze --config experiment.yaml --output reports/phase3_experiment.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_trial trial --config reports/phase3_experiment.json --variant baseline --output /tmp/ai-coding-experiment/phase3_baseline_001
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_trial trial --config reports/phase3_experiment.json --variant ponytail --output /tmp/ai-coding-experiment/phase3_ponytail_001
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_trial trial --config reports/phase3_experiment.json --variant caveman --output /tmp/ai-coding-experiment/phase3_caveman_001
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.skill_trial trial --config reports/phase3_experiment.json --variant serena --output /tmp/ai-coding-experiment/phase3_serena_001
```

Do not execute the list blindly: require the previous trial to be terminal, preserve all failures, and re-read quota before each model invocation. Stop at 85% in either quota window. The common OS lock prevents concurrent model trials; a fresh output directory is mandatory. The benchmark grader, scoring, source filters and quarantine remain unchanged. Profile/memory paths are explicitly rejected if they enter the grader snapshot.

Collect authoritative Git tag/snapshot metrics, actual grader decisions and raw usage using the existing collector. Sonar uses the same pinned analyzer, rules, exclusions, Clippy import and snapshot binding as Phase 2. Raw Sonar includes inline tests, so its aggregate deltas cannot establish production-only quality effects. A single task without repetitions supports pilot observations only. Phase 6 remains outside this run.
