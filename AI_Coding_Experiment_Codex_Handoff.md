# AI-Assisted Coding Experiment — Implementation Handoff

**Owner:** Artem Demidov  
**Prepared:** 2026-10-18  
**Target executor:** local Codex CLI, operating on the user's Linux machine  
**Status:** implementation specification; **nothing has been deployed or executed** by the author of this handoff.

## 0. Mission and operating rules

Build the **smallest reproducible experiment** comparing how coding-agent workflows and skills affect **correctness, maintainability, and production-code footprint** when developing existing repositories over multiple iterations. Use [SWE-Milestone](https://github.com/DeepCommit-ai/SWE-Milestone) as the benchmark harness, Codex CLI as the agent, local SonarQube Community Build for static analysis, and Git for patch metrics.

**Absolutely avoid paid model API usage.** Use the user's existing Codex/ChatGPT login if supported. Do not set or solicit `OPENAI_API_KEY`, `CODEX_API_KEY`, or `UNIFIED_API_KEY` as a paid workaround. If OAuth fails inside the harness, diagnose and report the blocker before taking any paid route. The ChatGPT subscription has usage/quota limits, which must be respected.

Implement in **phases with real smoke tests**. Do not download the entire image collection or run a large matrix first. Do not quietly change the benchmark's evaluator, tests, quarantine, network policy, or scoring logic to make a run work. Ask before any substantial downloads, privileged/network-control modifications, or changes to the user's global Codex configuration. Prefer a separate working directory, a fork/branch, and narrowly scoped overrides.

**Security:** Never commit or print `.codex/auth.json`, refresh tokens, Sonar tokens, credentials, raw private settings, or environment dumps. Mount credentials read-only wherever feasible; benchmark agents must not get GitHub/web lookup or connected-account tools. Avoid changing firewall/quarantine behavior to enable plugins; prepare offline dependencies before agent execution. Never run unreviewed downloaded hooks with elevated privileges. Respect local system limits.

## 1. Scientific question and scope

**Priority:** (1) functional correctness and regression avoidance; (2) production-code footprint and maintainability; (3) quota/token efficiency; (4) elapsed runtime. Small, understandable, maintainable patches matter because human reviewers must preserve ownership of the product.

**Research questions:**

1. Does explicit **plan** improve correctness or patch quality over an ordinary Codex run?
2. Does explicit **goal + plan** help more than a plan alone? A `goal` is a concise, comprehensive restatement of acceptance criteria, constraints, invariants, and non-goals; it must not be a solution or a hidden-test hint.
3. How do **Ponytail**, **Caveman**, and **Serena** separately affect correctness, patch size, maintainability, and resource usage?
4. On sequential changes, does an early patch create more rework, code growth, or failures downstream?

**Not in v1:** Sol → Tera multi-model planner/executor; model-vs-model leaderboards; combinations of skills; human-review time study; public SaaS dashboard; paid API; all 7 SWE-Milestone repositories.

## 2. Decisions already made — do not block on them

| Area | v1 default | Later option |
| --- | --- | --- |
| Model | **One** model accessible to local Codex OAuth, same exact ID everywhere; discover using CLI, do not invent an ID | Compare other models later |
| Reasoning effort | `high`, if supported by chosen model; otherwise consistent supported value | Sensitivity to effort |
| Variants | 6: `baseline`, `plan`, `goal_plan`, `ponytail`, `caveman`, `serena` | interactions after screening |
| Skills | One skill at a time on baseline, no hidden other skills | Best combinations |
| Repository | `ripgrep` for initial smoke; add a larger repository (prefer `scikit-learn`) after pipeline works | Multiple repos |
| Tasks | 1 isolated milestone first; 2–3 **dependent** milestones next; then longer/full chain | More projects/repetitions |
| Serena memory | Start with **cold** onboarding, counting its cost; isolate memories between trials, preserve only within a continuous trial | Warm-start as separate ablation |
| SonarQube | Local Community Build, after-run snapshots; not part of agent feedback | More static metrics |
| Review | Git diff = review surface; SonarQube = static maintainability proxy, **not** measured human review effort | Blinded human review |
| Cost control | Single trial at a time; save usage; stop on quota pressure or auth failures | Automated quotas when available |

**Only ask owner if one of these defaults is impossible, destructive, or materially changes fairness.** Expose blockers explicitly rather than silently substituting an API key.

## 3. Important verified upstream behavior / caveats

At time of writing (2026-10-18), upstream sources indicate:

- SWE-Milestone has persistent Docker workspaces, a **milestone dependency DAG**, Git completion tags, snapshot evaluation, and a Codex agent adapter. A continuous trial is **not** just a list of independent prompts. Source: [README](https://github.com/DeepCommit-ai/SWE-Milestone), [running trials](https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/docs/running-trials.md).
- The Codex adapter supports two auth modes: API and OAuth via host `~/.codex/auth.json` (mounts credential read-only before copying it into the agent container). **Code support is not proof of successful OAuth on this computer.** Source: [`harness/e2e/agents/codex.py`](https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/harness/e2e/agents/codex.py).
- **Critical blocker for skill comparisons:** that adapter generates a clean container `config.toml` and disables `features.plugins` plus other product tools in its CLI arguments. It does **not** automatically honor the host's `CODEX_HOME` plugin and MCP profiles. A local-global Ponytail/Serena/Caveman installation alone will not establish the desired variant inside benchmark containers. Modify only the agent-environment integration needed for each variant; keep forbidden capabilities disabled.
- `run_all.py` is a detached **full-trial launcher**; `--repos` scopes repos. Do **not** assume an undocumented `--milestones 2` argument exists. Single-milestone debugging is available through `python -m harness.e2e.run_milestone` (confirm exact flags with `--help`). For 2–3 *continuous* milestones, inspect the DAG and implement a **deterministic early-stop/subset mechanism** if none exists; preserve test/evaluation semantics. See [advanced usage](https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/docs/advanced.md).
- `agent: codex` uses `codex exec --json` and can resume via `codex exec resume`. The upstream implementation uses `--dangerously-bypass-approvals-and-sandbox` **inside its isolated benchmark container**; never copy that argument into a host-side run by habit. Its safety depends on the container and quarantine being correctly configured.
- This benchmark's README still documents API credentials as the normal setup even though the Codex adapter contains an OAuth code path. Verify against the actual pinned source, not just README examples.
- SonarQube Community Build can measure maintainability issues, remediation effort, complexity, duplication and LOC, but **cannot infer human review time or architecture quality directly**. It is mostly single-main-branch analysis; isolate experimental snapshots under distinct project keys or carefully reset reference state. For `ripgrep` (Rust), pin a Rust-capable Community Build image (e.g., inspect the 26.9 release) and install **Cargo + Clippy** for the scanner; verify the rules/metrics actually appear. Sonar announced that Rust will no longer be bundled by default in Community Build **26.11**, so **do not float to `latest`** and accidentally change analyzer coverage mid-experiment. Sources: [metrics](https://docs.sonarsource.com/sonarqube-community-build/user-guide/code-metrics/metrics-definition), [Rust analyzer](https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/languages/rust), [October 2026 analyzer change announcement](https://community.sonarsource.com/t/changes-in-community-build-regarding-rust-ruby-scala-and-advanced-bugs-in-java-python/189759).

Pin and record exact versions/commits of SWE-Milestone, dataset/images, Codex, SonarQube, Serena, Ponytail, Caveman, plus scanner and rule profiles. Upstream behavior may change.

## 4. Experiment matrix (minimum, not full factorial)

| ID | Pre-task preparation | Implementation agent | Extra behavior |
| --- | --- | --- | --- |
| `baseline` | None | Normal Codex | No experiment skills or MCP |
| `plan` | Separate **read-only** Codex session creates a plan | New/isolated execution context receives original task + plan | No experiment skills |
| `goal_plan` | Separate **read-only** Codex session creates structured goal + plan | New/isolated execution context receives original task + goal + plan | No experiment skills |
| `ponytail` | None | Baseline Codex | Ponytail enabled in pinned mode `full` |
| `caveman` | None | Baseline Codex | Caveman enabled via trusted session-start hook / equivalent validated injection |
| `serena` | None | Baseline Codex | Serena MCP and memories enabled |

Keep the underlying **task/SRS, baseline code, model, effort, benchmark config, runtime policy, timeout, and test suite identical** for matched comparisons. Use the same milestones in all variants. Do not give any variant hidden verification feedback. Record any difference in effective prompt or tools.

**Fairness nuances:**

- An ordinary `baseline` agent may plan internally; the comparison tests **explicit advance planning/handoff**, not whether the model is capable of thinking.
- The `plan` and `goal_plan` variants must pay for **both** preparation and implementation tokens/quota. Preparation must not write source files, read hidden tests, or mutate any repository. Its output should be bounded/structured and validated.
- Plan-only vs goal+plan should differ **only** by the extra goal content and any inevitable formatting changes. Keep planner instructions and budgets aligned. Report input sizes.
- For a single milestone, the executor starts in a clean context. For continuous mode, keep executor context continuity **consistent across all variants** between milestones; use a separate read-only planning phase at each newly unlocked milestone, then send results to the ongoing executor. A newly forked executor on every milestone changes another variable and must be labeled separately.
- No use of past benchmark attempts or test results to tune prompts during a measured run. Freeze prompts before benchmark collection.

Suggested planner outputs, validated as JSON or Markdown with strict headings:

`plan`: objective; steps with files/dependencies as warranted; verification checklist; risks. No implementation.

`goal_plan`: goal (acceptance criteria, constraints, non-goals, regression invariants) plus the same plan schema. No implementation.

Avoid hand-editing generated plans. Persist each as an artifact with a hash.

## 5. Architecture: reuse evaluator, customize agent/profile layer

```text
SWE-Milestone dataset + DAG + grader (unchanged)
                     |
              variant-aware adapter
                     |
      [optional read-only planner]
                     |
        [Codex executor/session]
                     |
        source commit / milestone tag
                     |
            SWE-Milestone grading
                     |
    snapshot ─ Git diff ─ SonarQube ─ metrics
                     |
             JSONL/CSV report
```

### Required implementation components

1. `experiment.yaml`: chosen model, CLI version, repo/milestone selection, reasoning effort, timeout, variants, resource budget, setup hashes, deterministic analysis paths.
2. `experiment/runner.py` or a narrowly scoped harness adapter: isolate profiles, launch phases, preserve benchmark lifecycle, record run IDs and usage, implement safe early stop when needed. Favor patching the existing Codex adapter over writing a new benchmark evaluator.
3. `experiment/profiles/`: explicitly constructed **per-variant** Codex settings + pinned plugin/hook/MCP assets, not symlinks to the user's global configuration. Verify the active settings **inside each container**.
4. `experiment/metrics.py`: parse upstream grader JSON, `git diff`/`--numstat`, Codex JSON events, SonarQube API results into normalized per-milestone records.
5. `experiment/report.py`: paired comparisons and a compact Markdown/CSV report; no invented values.
6. `tests/`: dry-run tests for prompt formatting, isolation, output collection, non-leakage and reproducibility.

**Do not** assume `CODEX_HOME` automatically reaches the agent container. The upstream adapter currently reads `~/.codex/auth.json` from the **host** and writes `/home/fakeroot/.codex/config.toml` **inside** the container. A custom profile must be safely staged in that environment after/beside the generated settings and all relevant CLI overrides audited. Capture sanitized effective config and hook/MCP activation proof.

### Skills and MCP profiles

- **Caveman:** upstream [installation and Codex hook behavior](https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md). Normally a trusted `SessionStart` hook injects concise communication rules. This skill may **not** reduce production code; test rather than assume. If native hooks are unavailable in that version/container, use a clearly labeled prompt-injection fallback, not a silent substitute.
- **Ponytail:** upstream [repository](https://github.com/DietrichGebert/ponytail). Pin version; install hooks/plugin into a dedicated profile. `PONYTAIL_DEFAULT_MODE=full` is an option. Verify active mode, lifecycle hook injection, and conflicts with Caveman (the variants are **separate**). If plugin support must be enabled, enable only what is necessary for the local pinned package; **do not enable remote plugins or connected app tooling**.
- **Serena:** upstream [Codex MCP setup](https://github.com/oraios/serena/blob/main/docs/02-usage/030_clients.md), [memories](https://github.com/oraios/serena/blob/main/docs/02-usage/045_memories.md). MCP typically uses `serena start-mcp-server --project-from-cwd --context=codex`, but install the server and language tooling **inside the effective agent environment**, with no external-data access in agent runtime. `.serena/memories/` is experiment state: cold start per independent trial, retain within same trial, never transfer to a different variant/repetition. Exclude setup/memory artifacts from **production-code footprint**; log their bytes/count separately. Ensure no memories enter the benchmark grader snapshot unless explicitly part of the desired design.
- **Baseline must truly be clean.** Any global `AGENTS.md`, hooks, memory files, user plugins, proxy environment or project-level settings can contaminate it. Print a sanitized profile-diff/activation audit, not the secrets.

Require activation assertions before measured runs:

- `baseline`: no Caveman/Ponytail hooks, Serena tools or stored memories.
- `ponytail`: hook fired, expected mode seen.
- `caveman`: session-start hook or documented fallback observed.
- `serena`: MCP process connected, Serena tool call observed; memory policy respected.

A tool being installed does **not** mean it was used; record actual tool-call counts. Do not artificially force Serena tool use if that is not the tested workflow; merely require at least one verified use in a smoke test and report natural usage in measured trials.

## 6. Measurements and reporting

**Unit of analysis:** per `(repo, milestone, variant, repetition)` with immutable starting and ending Git refs; then aggregate per continuous trajectory. Do not treat dependent milestones as independent statistical samples.

### Correctness (primary gate)

- Raw and normalized SWE-Milestone grading outputs; strict resolved indicator where defined.
- F2P / P2P / N2P (when provided), regressions, missing submission tags, timeouts, infrastructure failures **separately**.
- Preserve upstream scoring unchanged; do not reduce a nuanced grade to success/failure only.
- Report cumulative outcomes across a chain and number of downstream milestones reached.

### Production code footprint (independent axis)

Use *incremental diff against previous accepted/submitted milestone* (first against common base):

- Added, deleted, net `+/-`, and churn `(added + deleted)` lines.
- Changed source files (and optionally tests/docs/config separately).
- New production files, deleted files, file rename counts; gross additions in **production code**, not tests/autogenerated/vendor files.
- Cumulative production LOC and per-stage diff, with consistent language-appropriate inclusion/exclusion rules.
- Detect formatting-only mass edits, generated code, vendored dependencies and binary changes; report or exclude under documented consistent rules.
- Publish footprint comparisons **alongside correctness**. Optionally compare footprint among fully correct paired milestones, but never quietly drop failures.

Useful Git primitives: `git diff --numstat BASE END -- <production-paths>` and `git diff --name-status -M BASE END`; derive path filters from benchmark `metadata.json`, review exclusions. Avoid using staged/uncommitted workspace diff when authoritative milestone snapshots/tags exist.

### Maintainability (SonarQube Community Build)

For the **same immutable snapshot** scored by the grader, run a SonarScanner against local SonarQube, preferably per unique experiment/milestone project key. Record:

- LOC / ncloc, complexity, cognitive complexity (as available), duplicated lines/density, maintainability issues, estimated remediation effort, new-code issues when comparison semantics are valid.
- Initial repository baseline under the same scanner, rules, and exclusion settings; compare **deltas from matched baseline or previous stage**, not raw scores alone across different repos.
- Quality profile, analyzer versions, scanner version, source exclusions, language support, and missing metrics (`null`, never zero).
- Scanner/evaluator failures distinguish from perfect code. Wait for SonarQube background computation to finish before querying its API.

**Warning:** Community Build's branch/PR support is limited. Do not reuse one project key across concurrent competing variant scans; use stable independent keys or explicit snapshot reinitialization. Sonar's “technical debt minutes” estimate is **not actual human review time**. Where useful, note code smells and design trade-offs that Sonar cannot capture (e.g., misleading abstractions, architectural fit). Human review remains outside v1.

### Efficiency

- Codex JSONL usage events: input, output, cached tokens, turns, session IDs; sum **planner and executor**.
- Record elapsed times separately for prep, executor, evaluation, Sonar; runtime is descriptive rather than optimization target.
- Quota snapshots before/after each batch via Codex `/status` where available. Treat rounded/rolling usage limits as **approximate** and do not infer precise per-task quota from them. If inaccessible programmatically, manual fields are acceptable; save reset window/time.
- Do not label API token-price estimates as ChatGPT subscription quota costs.

### Minimal results schema

```json
{
  "trial_id": "ripgrep_plan_001",
  "variant": "plan",
  "repo": "ripgrep",
  "milestone_id": "milestone_001",
  "repetition": 1,
  "starting_commit": "<sha>",
  "ending_commit": "<sha>",
  "resolved": null,
  "grader_metrics": {},
  "added_prod_loc": null,
  "deleted_prod_loc": null,
  "changed_prod_files": null,
  "sonar": {"analysis_ok": null, "new_maintainability_issues": null},
  "usage": {"planner": {}, "executor": {}},
  "quota": {"before": null, "after": null},
  "duration_seconds": null,
  "effective_profile": {},
  "failure_category": null
}
```

In the real files, use **actual** values or `null`; placeholder strings above are just schema illustrations. Include `experiment_id`, dataset/manifests version and all relevant hashes in experiment metadata.

## 7. Implementation phases and acceptance criteria

### Phase 0 — environment audit, **zero benchmark quota**

- Check Linux prerequisites: Codex CLI + version + `codex login status`, Docker, Python/`uv`, Git LFS, CPU/RAM/disk, connectivity for downloading dataset/images, available model and reasoning levels.
- Inspect upstream README, `docs/setup.md`, `docs/advanced.md`, `docs/running-trials.md`, `harness/e2e/agents/codex.py`, `harness/e2e/run_e2e.py`, config and dataset DAG.
- Pin SWE-Milestone commit, dataset version, image digests and local CLI version. Estimate download/storage budget before initiating large pulls; **fetch only prerequisites for the first repo where feasible**.
- Confirm OAuth only. Document current quota and whether `codex exec` consumes ChatGPT subscription usage.
- Inspect existing user Codex config but do not modify it; mask secrets.
- Deliver `environment_report.md`, setup instructions and `experiment.yaml`.

**Gate:** user gets a clear list of setup blockers and commands; no hidden use of paid API.

### Phase 1 — baseline end-to-end smoke, **one milestone**

- Clone/install SWE-Milestone, pin dataset and necessary Docker image(s).
- Confirm a trivial **host** `codex exec` works with ChatGPT auth; then confirm the **containerized** harness Codex OAuth path, restricted network and grader all work on exactly one milestone.
- Official doc shows `python -m harness.e2e.run_milestone`; derive exact required arguments using current `--help`. Do not invent flags.
- Collect one actual authoritative milestone output, snapshot/commit, Codex trace, and Git diff. Record whether results are valid, even if unresolved.

**Gate:** grader runs unchanged, no API charges, trace and diff are linked to the same code snapshot; failures are diagnosable.

### Phase 2 — planning A/B, **same milestone**

- Build minimal variant adapter: `baseline`, `plan`, `goal_plan` with strict read-only planner and fresh task implementation context.
- Add unit tests for prompt templates, repo immutability after planning, session separation, usage aggregation, profile isolation, and identical setup.
- Execute each variant on **fresh identical starting state**. Persist plans (hashed) and traces.
- Generate first comparison report with correctness, production diff, usage and missing-data markers.

**Gate:** all three variants run with identical conditions; differences are auditable and not inflated by uncounted prep work.

### Phase 3 — isolated skill A/B, **same milestone**

- Build dedicated pinned container profiles for `ponytail`, `caveman`, `serena`; audited activation tests first. Clean baseline remains free of them.
- For Serena perform cold onboarding in its own trial and account for its tokens/time. Never reuse test-specific knowledge from a previous attempt.
- Run one matched task per variant; log tool calls and per-profile effective features. Keep benchmark network/quarantine intact.

**Gate:** no “enabled in settings” claim without activation evidence; no cross-contamination or credentials in trace outputs.

### Phase 4 — SonarQube + robust measurements

- Start local Community Build, pin image and scanner (**pin a pre-26.11 Rust-enabled release for ripgrep**, checking actual support), secure admin password/token, do not expose instance publicly. Ensure Cargo and Clippy are present for Rust analysis.
- Analyze initial common base and all solution snapshots with same profile/exclusions. Build collection via local Web API and check asynchronous task completion. Store raw response + normalized metrics.
- Validate Git calculations against independent `git diff` commands on sample snapshots.
- Export `results.jsonl`, `results.csv`, `summary.md` with paired per-task comparisons and limitations.

**Gate:** real, verifiable data; no fabricated scores; scanner errors shown as errors, not zeros.

### Phase 5 — continuous SWE-Milestone pilot, **2–3 linked milestones**

- Examine DAG and how task unlocks/prompts reach the long-running agent. Add an **explicit** variant-aware hook around task dispatch **if necessary** to invoke a separate read-only planner before the executor gets each milestone. This is the actual nontrivial integration: simply wrapping the first `codex exec` is not sufficient for per-milestone planning.
- Maintain executor context across milestones for all variants consistently, unless tested in a clearly separate design. Preserve milestone tags and isolated grading. Stop after a predetermined dependency-consistent subset or bounded number of completions without changing the scoring behavior. Label such a run **pilot/non-official subset**, not official full-benchmark score.
- Run baseline first, then plan and goal_plan, then select one or two skills based on Phase 3, measuring growth and regression across milestones.

**Gate:** score/diff/Sonar each milestone; same dependency-consistent trajectory; no data leakage across trial variants; explicit stop rule.

### Phase 6 — larger evaluation (not automatically authorized)

- After user sees pilot report and quota/storage forecast, add a **larger repo** (e.g. scikit-learn) for a realistic Serena test, then expand tasks/repetitions and optionally full benchmark.
- Use matched tasks, deterministic configuration ordering or randomized order to limit quota/time-window effects, and account for dependence between milestones. Report uncertainty; do not generalize from 1–3 milestones.

## 8. Suggested on-disk layout

```text
ai-coding-experiment/
  README.md
  experiment.yaml
  prompts/
    planner_plan.md
    planner_goal_plan.md
    executor.md
  experiment/
    runner.py
    profiles.py
    metrics.py
    sonar.py
    report.py
  profiles/
    baseline/
    caveman/
    ponytail/
    serena/
  tests/
  results/                # gitignored: runs, source snapshots, tool logs
  reports/
  vendor/SWE-Milestone/   # pinned upstream submodule/clone; local patch tracked
  .gitignore
```

Keep upstream modifications a small patch set in a separate branch and summarize exactly which safety and agent-integration code changed. Avoid rewriting the grader. For experimental artifacts, record revision hashes and redact secrets automatically.

## 9. Open questions to resolve locally (default-first)

1. **Which exact Codex model is available to this subscription?** Discover locally and choose one ID; do not assume `Sol`/`Tera` are valid CLI identifiers. Default reasoning `high` if supported.
2. **Is OAuth container execution functioning under the benchmark network quarantine?** Test one milestone; if blocked, report and investigate the authentication/whitelist mechanism without opening general internet or adding a paid API credential.
3. **What is a valid 2–3-node dependency-consistent subset of `ripgrep`?** Inspect `dependencies.csv`, `milestones.csv` and available task subsets; choose and pin IDs *before* measuring. If partial continuous mode requires code changes, implement and label them.
4. **How much disk/RAM and remaining Codex quota are available?** Check before downloading/building or running more than one pilot.
5. **Which Serena setup should be used?** Default cold start (includes onboarding cost) and trial-isolated project memories, with actual MCP usage logged. Later compare warm-start separately, without borrowing memories from another evaluated run.
6. **Do hooks/plugins survive the container setup?** Verify per-profile. The current upstream clean config actively disables plugins; the experimental adapter must explicitly and safely address this.
7. **How to hold continuous executor state while injecting a prep stage?** First inspect the benchmark task-dispatch lifecycle. If architectural change would be extensive, implement the truthful single-milestone A/B first and report a separate engineering estimate for the continuous stage.
8. **Which source-path classifications work for Rust and Python?** Derive from dataset metadata and freeze exclusions. Never mistake generated/test code growth for new production code.

If there is a consequential conflict with these defaults, present **a small decision table with recommendation** and ask only the essential question. Otherwise proceed.

## 10. Definition of done for v1

A v1 result is accepted only if:

- [ ] A baseline Codex OAuth task is executed through the **actual** SWE-Milestone grader and artifacts are saved.
- [ ] All 6 variants have isolated, testable settings; any variant that cannot activate is marked **blocked**, not silently run as baseline.
- [ ] `baseline`, `plan`, `goal_plan` compare the same task with accounted prep+execution usage.
- [ ] Git diff production-code footprint works and is tested against Git directly.
- [ ] SonarQube Community Build produces before/after results or reports a transparent blocker.
- [ ] A compact report exists with per-task results, versions, environment, activation checks and explicit limitations.
- [ ] No paid API use, credential leak, public service, or unauthorized relaxation of the benchmark quarantine.
- [ ] Continuous 2–3-milestone flow is either demonstrably implemented and tested or explicitly deferred with an exact blocker and next step (do **not** mark done by claiming a sequence of independent `codex exec` calls is equivalent).

**First action for local Codex:** inspect environment and upstream source, write a concise `environment_report.md`, create the repo scaffolding, and execute **only Phase 0**, then one tiny OAuth/grader smoke test in Phase 1 if dependencies and quota permit. Keep implementation minimal; prefer one working vertical slice to a framework full of unused abstractions.

## References to read before coding

- SWE-Milestone repository: https://github.com/DeepCommit-ai/SWE-Milestone
- SWE-Milestone setup: https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/docs/setup.md
- SWE-Milestone trial runbook: https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/docs/running-trials.md
- SWE-Milestone advanced/single milestone: https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/docs/advanced.md
- Codex SWE-Milestone adapter: https://github.com/DeepCommit-ai/SWE-Milestone/blob/main/harness/e2e/agents/codex.py
- Codex authentication: https://learn.chatgpt.com/docs/auth
- Caveman: https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md
- Ponytail: https://github.com/DietrichGebert/ponytail
- Serena + Codex: https://github.com/oraios/serena/blob/main/docs/02-usage/030_clients.md
- Serena memories: https://github.com/oraios/serena/blob/main/docs/02-usage/045_memories.md
- SonarQube Community Build metrics: https://docs.sonarsource.com/sonarqube-community-build/user-guide/code-metrics/metrics-definition
- SonarQube Community Build Web API: https://docs.sonarsource.com/sonarqube-community-build/extension-guide/web-api
