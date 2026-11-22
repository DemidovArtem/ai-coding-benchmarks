# Sources and evidence register

**Talk:** Beyond Vibe Coding: AI Prototypes That Last · Artem Demidov · ProductTank Lausanne.

**Source check:** 22 November 2026, Europe/Zurich. Model rankings and product features can change; recheck them before the event. The talk uses existing public analysis, not a fresh benchmark run or native-session continuation.

## Evidence types

- **Personal experience:** supplied by Artem in preparation conversations. Not independently audited.
- **Illustrative example:** synthetic dashboard, dialogue, duplication diagram and handover. No employer material or observed application results.
- **Own measurement:** the frozen six-step ripgrep comparison below.
- **Documentation guidance:** vendor recommendations and descriptions, not controlled evidence of effectiveness.
- **Industry case:** a published report with a particular method and measurement scope.
- **External benchmark:** measured agent/model/settings configurations; not universal product comparisons.

## Visual revision and slide map

Revised after Artem's review: a coherent house on the cover; two-sided story and feature-diff metaphors; explicit agenda; publisher/own results side by side; independent JetBrains evidence; a simple-setup recommendation; clickable official documentation; real Planning Mode controls; editable Codex-style teaching conversations; qualitative context fullness; a dedicated goal example; model delegation and cost comparison in the main sequence. There are **26 main frames plus 2 appendices**, scheduled for 23 minutes and 7 minutes Q&A. Rehearsal and venue arrangements are not delivery gates.

| Frames | Content | Evidence |
| --- | --- | --- |
| 1–3 | Coherent cover, growing difficulty, +3000 vs +300 / −200 | Artem's account; generated house metaphors; different features, no causal saving claim |
| 4 | Three-chapter agenda | Editorial structure |
| 5 | Add Ponytail and verify activation | P1; activation label is illustrative |
| 6 | Publisher and own reductions side by side | P2/B1–B3; different methods/workloads, not a replication |
| 7 | Own pilot with rounded percentages | B1–B3; normalized chart baseline = 100%; no quality superiority |
| 8 | Independent Ponytail and Caveman results | J1/J2; separate studies/settings, no pooled estimate |
| 9 | Keep the setup simple | B1–B3/E1; recommendation, not a universal quality ranking |
| 10 | Explicit Planning Mode recommendation | O1/A6; official heading captures and clickable source names |
| 11 | Where to enable Planning Mode | O3/A6/A7; real screenshots I1/I2, client/version scope stated |
| 12 | Questions in Planning Mode | A1/O1; editable reconstructed chat |
| 13 | Give the agent checks | A1; official heading capture, clickable source and red underline |
| 14–17 | Vague prompt, corrections, requirements, comparison | Generated dashboard teaching example; no measured duration or first-attempt success claim |
| 18–19 | Context fills and compacts | A8/A9; qualitative native diagram, no numerical trigger or retention claim |
| 20–21 | Save state; set /goal with criteria | A3/O2/A4; reconstructed chat and example command |
| 22 | Example prompts for rules and skills | A5/O1; editable native file diagram |
| 23 | Strong plan, cheaper implementation, optional strong review | Artem's practice; S1 supports only the narrower delegation case |
| 24 | Specific model/agent/settings cost–index tradeoff | X1/X2; subscription experience separately attributed to Artem |
| 25–26 | Actions, takeaways and reading | Editorial synthesis; A1/A5 reading links |
| Appendix A | Exact values, ranges, other methods and limits | B1–B3; Serena separate cohort |
| Appendix B | Specific model/agent/settings comparison | X1/X2; checked 22 November 2026 |

## B1–B3. Own benchmark: frozen six-step ripgrep comparison

- [B1: Published results](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/docs/RESULTS.md).
- [B2: Numeric plot data](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/reports/plots/current_comparison.json).
- [B3: Methodology](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/docs/METHODOLOGY.md), with [run parameters](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/reports/plots/run_parameters.md).

The results page is dated **5 November 2026**. Checked locally on 22 November 2026 against repository commit `7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c`.

SHA-256 at preparation:

```text
reports/plots/current_comparison.json
ae5a1ff7569813b279175f989147f6508792de13122b643c44274a3ce98c4531
docs/RESULTS.md
606ab3d877e4e5eac5fd83e8a658f9df3ada6a30b51d03778d8b59390474208e
```

Use `points` where `step == 6`, `variant` is `baseline` or `ponytail`, and the setup fingerprint is:

```text
b8edbc5be2bb39fb867bc59cc73f7f6188ffa5fe1b7d46d2da35f6918b2841ac
```

Each displayed method has two trajectories. Fixed model/effort: `gpt-6.1-sol` / `high`. Historical measured CLI: Codex 0.163.0. The skill profile is version-pinned; these results are not a comparison of current model brands.

| Metric | Baseline mean [min–max] | Ponytail mean [min–max] | Definition |
| --- | --- | --- | --- |
| `net_prod_loc` | 413.5 [322–505] | 301 [286–316] | Added minus deleted physical production-source lines between initial and final trees |
| `output_tokens` | 67,311.5 [65,442–69,181] | 62,766 [59,521–66,011] | Cumulative model output over the six steps of each trajectory, then mean across trajectories |
| `churn_prod_loc` | 578.5 [522–635] | 449 [420–478] | Added plus deleted physical production-source lines between initial and final trees |
| `sonar_delta_cognitive_complexity` | 142 [125–159] | 150.5 [149–152] | Snapshot cognitive-complexity delta under the study's Sonar scope |

Production-source filtering uses upstream source metadata and a pinned Rust AST filter for inline tests. It excludes tests, generated and vendor files according to the study's policy. Physical LOC includes comments and blank lines. Sonar scope differs: it includes inline tests and benchmark masking. Net growth, churn and cognitive complexity must not be treated as interchangeable measures.

Derived, relative to baseline mean:

```text
Net growth reduction = (413.5 - 301) / 413.5 × 100 = 27.2067…% → 27.2%
Output reduction = (67311.5 - 62766) / 67311.5 × 100 = 6.7529…% → 6.8%
Production churn reduction = (578.5 - 449) / 578.5 × 100 = 22.3854…%
```

Main charts start at zero and normalize each baseline mean to 100%. Ponytail displays rounded ratios, 73% for net code growth and 93% for output; headlines round the reductions to approximately 27% and 7%. Exact inputs and 27.2% / 6.8% calculations remain here. No uncertainty bands are drawn. Appendix ranges are observed minima and maxima, not confidence intervals.

Appendix A retains descriptive context for other methods. Caveman has n=2, mean net production LOC +396.5, cumulative output 85,989.5 and cognitive delta 150.5. Its main-slide output increase is `(85989.5 / 67311.5 - 1) × 100 = 27.7…%`, rounded to approximately 28%. Net growth is approximately 4% lower, so this study does not support saying Caveman increased code size. Serena has n=1, net production LOC +497, output 84,165 and cognitive delta 156. Its setup fingerprint is `f1140b0cc89bade585633a3ad4c88603ee82faaf3a77a9b4bc8bb5b583c24805`: a separate cohort, not a paired comparison. Functioning semantic tools and memories are verified; a quality benefit or harm is not established. These methods do not enter the main Ponytail charts.

Interpretation limits retained in slides and notes:

- One repository/task chain, two trajectories per displayed method; six dependent steps per trajectory.
- No statistical-significance claim and no direct measurement of dollar cost or human review time.
- All seven step-6 evaluations in the wider comparison are valid but unresolved, each passing 7/8 new tests. This includes the four displayed baseline/Ponytail trajectories.
- Step-5 grading is invalid because of a documented undeclared dependency. Protocol/runtime differences and earlier failures limit a simple accumulated-error interpretation.
- Second Ponytail trajectory at step 6 includes an authorized removal of one API-rejected encrypted reasoning record from a checkpoint copy. It remains in the descriptive mean. Other source/session history was preserved.
- Sonar does not establish a consistent quality winner. No causal or universal Ponytail benefit is claimed.
- The separate earlier planning pilot has n=1 per condition; planning increased output there. Do not pool its baseline with this cohort.

## A1. Anthropic: Best practices for Claude Code

[Current documentation](https://code.claude.com/docs/en/best-practices).

Supports giving the agent a check, clarifying unspecified work, keeping instruction files focused, and reviewing against a specification. Its current context guidance does not make aggressive manual compaction a required ritual. These are recommendations, not a measured effect size for this talk. Used in the planning/checks section and as the first reading link.

## O1. OpenAI: Codex best practices

[Practical guide](https://learn.chatgpt.com/guides/best-practices).

Supports goal/context/constraints/done-when prompts, planning and interviews for difficult work, reusable project guidance, skills, and verification. Used as a supplementary source, with Anthropic the main teaching reference. It does not prove that a specific planning workflow reduces total usage.

## A2. Anthropic: Prompting best practices, overeagerness

[Overeagerness section](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#overeagerness).

Guidance against unnecessary code, abstractions and flexibility supports the small-change principle. The section discusses particular model behaviour; do not generalize it into a claim that all current models behave identically. It does not mention or endorse Ponytail.

## P1. Ponytail upstream

[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail).

Third-party skill/plugin focused on minimal complete changes and reuse. Frame 5 illustrates asking the agent to install it; exact current commands are in the speaker notes. No installation is executed by this talk. Current installed and historical measured versions need not match; consult the frozen profile manifest for reproduction. Publisher and independent evidence are separated on consecutive frames.

## A3. Anthropic: Effective harnesses for long-running agents

[Article](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), published **26 November 2025**.

Reports incomplete undocumented work and premature completion in its agent setting. Uses progress artifacts, Git history and incremental work to bridge sessions. This is a particular historical system, not a claim that every current agent forgets in the same way. Used in the saved-state section.

## O2 / A4. Goals

- [O2: Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
- [A4: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal).

Both describe persistent completion conditions within their supported thread/session workflows. Implementations and stopping behaviour differ. Neither is complete cross-project memory or proof that the resulting application is correct. Use a supporting build/client version; no universal command syntax is taught in this talk.

## S1. Spotify Portal: token delegation case

[Portal by Spotify cut my Claude Code token usage by 90%](https://portal.spotify.com/blog/portal-by-spotify-cut-my-claude-code-token-usage-by-90), Dimitri Mazmanov, **3 September 2026**, updated **8 September 2026**.

Reports roughly 90% mean bulk-read token savings in testing across four Java-monorepo scenarios. Uses Gemini 2.5 Flash workers for large reads and predictable generation. The author describes a subtle bug the worker missed and additional latency. Do not represent this as 90% off total development cost, a company-wide result, or validation of the talk's strong-plan/cheaper-implementation/review suggestion. Used in the model-budget section.

## A5. Anthropic: Extend Claude Code

[Extension overview](https://code.claude.com/docs/en/features-overview).

Explains project instructions, skills, hooks, subagents, MCP and plugins. Standing guidance loads into context; skills provide reusable knowledge/procedures loaded or invoked for relevant work. Instructions remain probabilistic; enforcement and verification require other mechanisms. Used in the rules/skills section and as the second reading link.

## X1 / X2. Artificial Analysis

- [X1: Coding agents benchmark](https://artificialanalysis.ai/agents/coding-agents).
- [X2: Coding Agent Index v2.1 methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking).

Read the public page and its embedded variant records on **22 November 2026**. Store only the selected public measurements in the HTML's `evidence-data`, not a copy of the page. Index = `indexScore × 100`; API cost = `mean.costUsd`.

| Public variant ID | Configuration | Exact index | Exact mean API cost/task, USD |
| --- | --- | ---: | ---: |
| `4d278d53a18fbdcb5138d11466ea0b1b` | Claude Code + Claude Sonnet 5.5, Max, Default Fallback | 56.3314945150429 | 11.39857189877927 |
| `2b66aa9f8afa482977259846d9b207ba` | Codex + GPT-6.2 Sol, Xhigh | 49.7854108287173 | 0.8980194131553201 |

The public embedded records were fetched again during this revision; both selected values match the earlier same-day capture. Appendix values round to 56.33 / $11.40 and 49.79 / $0.90. Main display uses index 56 / 50 and zero-based native charts. Cost ratio is `11.39857189877927 / 0.8980194131553201 = 12.69…`, displayed as approximately 13× lower cost. Relative index reduction is approximately 11.62%, displayed as 12%; absolute gap is approximately 6.5 index points. The index is not percentage accuracy.

Index v2.1 equally weights FrontierCode-AA 2.0, Terminal-Bench 4.1 and SWE-Atlas-QnA-AA. Costs include applicable cache pricing; they exclude subscription pricing and full operational/human costs. Results describe configurations and do not isolate model quality from the agent. Artem's observation that Codex lets him do more coding within subscription limits is personal experience, not an outcome measured by Artificial Analysis. No universal efficiency or model-ranking claim is made.

## J1 / J2. Independent JetBrains evaluations

- [J1: Ponytail evaluation](https://blog.jetbrains.com/ai/2026/07/ponytail-skill-claude-tested/): 80 paired SkillsBench tasks, Claude Sonnet 5 at medium effort, injected Ponytail v4.8.4 rules. Median code-written reduction 15.4% (p=0.088); median API cost reduction 10.3% (paired test p=0.004, bootstrap median interval touches zero). No detectable task-score difference, not proof of equivalence. Code counts cumulative emitted lines, not final net growth. Skill self-activation failed in 10/10 setup sessions; verify injected activation. This evaluates an older version than P2.
- [J2: Caveman evaluation](https://blog.jetbrains.com/ai/2026/07/speak-to-ai-agents-like-cavemen-tosave-tokens/): full run 82 paired tasks, forced Caveman, Claude Sonnet 5 at low effort; output saving 8.5%, rounded to 9%. No detectable task-score difference (sign test p=0.82). Pricing outliers affected raw cost totals. Do not convert this output result into a guaranteed cost saving.

These are primary reports by an organization independent of the skill publishers. Different settings and endpoints prevent pooling them with each other or the own pilot. Do not interpret disagreement with the small own Caveman result as evidence of universal quality degradation.

## E1. ECC integration and six-edit pilot

[Frozen results](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/reports/ecc_results.md), [protocol](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/reports/ecc_protocol.md), and [activation record](https://github.com/DemidovArtem/ai-coding-benchmarks/blob/7cb5b3ee215287717edbb2cdf0ecb34f232a1c4c/reports/ecc_smoke.json).

ECC for Codex, offline, version 2.2.3 at `c05b2d6614f62f6db0047669aa4eefb223d478f9`: one recovered trajectory, six edits and Sonar scans; 2 accepted, 3 rejected, 1 correctness score unavailable. Native plugin, SessionStart and configured roles were verified separately before measurement. Runtime changes, disabled external integrations and interruption recovery prevent a matched historical A/B efficiency claim. No general quality ranking follows. Configuration and activation must be tested; registration alone is insufficient.

[ECC upstream](https://github.com/affaan-m/ECC) describes agents, hooks, skills and other integrations. Its author states in the Background section that he won the Anthropic × Forum Ventures hackathon in September 2025. Attribute this to the author; it is not Anthropic endorsement of ECC. This background is optional speech context, not evidence of benchmark performance.

## Personal model allocation

Artem reports using a stronger model for planning, a cheaper model for the longer implementation loop, and stronger review/correction when necessary. No controlled saving was measured for this three-stage workflow. The intended benefit is reduced premium-model usage or budget pressure. Total tokens can increase; rework, cache, prices, subscription limits and task difficulty matter. Pass the saved plan and checks, preserve the goal in the active session, and compare the verified result. The earlier isolated planning pilot did not show token savings; it tests a different question.

## Organizer requirements and remaining human checks

The privately supplied **ProductTank Lausanne speaker guidelines 2026** were read in full. They request practical takeaways, lessons from experience, no sales pitches, a draft/outline 72 hours in advance, speaker name/photo and a 55–60-word bio. They describe a varied audience, organizer-assisted Q&A and arrival 30–45 minutes early. The private PDF is not redistributed.

For this particular talk Artem confirmed **30 minutes total**; the schedule therefore uses 23 + 7, rather than assuming the generic guideline's Q&A is additional. English slides and speech, browser presentation, and synthetic work examples were confirmed during preparation.

Event date, registration, organizer delivery, photo and equipment remain speaker/organizer actions. Artem explicitly removed equipment and timed rehearsal as gates for this presentation revision. They are not claimed completed and do not block delivery of the verified materials.


## P2. Current publisher benchmark

[Ponytail 5 agentic report, 7 October 2026](https://github.com/DietrichGebert/ponytail/blob/main/benchmarks/results/2026-10-07-agentic.md), checked 22 November 2026. The headline reports 53% less source code, 45% fewer output tokens, 41% less agent time and 26% lower API cost. Opus 5.5, default effort, Claude Code CLI 2.1.288; 39 tasks, 5 runs per task/arm. Headline statistics use geometric means of per-task median ratios. Bash is disabled; the harness evaluates written code afterwards. Hidden correctness checks apply to 18 surgical tasks. These are publisher-reported, task-specific results, not a universal effect or a replication of Artem's study. The older single-shot 80–94% claim is not used as the current main-slide result. No safety guarantee or assertion that less code always improves quality is made.

## A6 / A7 / O3. Planning Mode controls

- [A6: Claude Code common workflows, Plan before editing](https://code.claude.com/docs/en/common-workflows#plan-before-editing): terminal Shift+Tab until plan mode, or the plan permission-mode flag.
- [A7: Claude desktop permission modes](https://code.claude.com/docs/en/desktop#choose-a-permission-mode): mode selector below the prompt; desktop and terminal shortcuts differ.
- [O3: OpenAI current desktop slash commands](https://learn.chatgpt.com/docs/reference/slash-commands): `/plan` toggles Plan mode. Fetched using official OpenAI documentation tools.

## A8 / A9. Context and compaction

- [A8: Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents), 29 September 2025: context is finite; compaction and structured notes support longer tasks.
- [A9: How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works): context management in the agent harness.

The diagram now uses “Nearly full” and “Room to continue” instead of percentages. Its cells are qualitative, not an exact compaction trigger or a compression/retention measurement. The dropped export detail is a synthetic possible failure, not an observed benchmark event. Goals preserve the completion condition; saved files preserve explicit details. Neither guarantees recall or correctness. O2 documents Codex thread-scoped durable objective state; A4 documents Claude Code's session goal and evaluator. The example `/goal` contains a saved plan, observable acceptance criteria and a data-preservation constraint; it does not promise perpetual execution or global memory.

## Images, screenshots and annotations

See `assets/README.md` for every local asset, original URL, provenance and image-generation prompts. I1/I2 illustrate where a control appears; primary vendor docs establish the behaviour. Screenshots are older client versions and are labelled accordingly. Official documentation headings are actual browser captures. Red boxes/underlines are editable slide annotations, not changes to the source text. Chats are editable Codex-style reconstructions; dashboards are generated illustrations. Neither is evidence of a real session or successful test.
