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

## Slide-by-slide map

| Slide | Claim or content | Evidence |
| --- | --- | --- |
| 1 | More duplication and three to five attempts as an application grew | Personal experience supplied by Artem; five-copy dashboard is illustrative |
| 2 | Define observable conditions and give the agent checks | A1, O1; all dashboard data and error copy are illustrative |
| 3 | Interview and plan before ambiguous work; save the agreement | A1, O1; dialogue is illustrative; earlier planning pilot in B1 does not show token savings |
| 4 | Reuse, small complete changes, no speculative features | P1, A2; own recommended prompt is a paraphrase, not a quoted vendor instruction |
| 5 | Six-step baseline/Ponytail means and descriptive differences | B1–B3; only the two methods in the same step-6 setup fingerprint |
| 6 | Preserve progress artifacts; plan and goal have different roles | A3, O2, A4; file contents and passed checks are illustrative |
| 7 | Selective model delegation can be worth trying | S1 for the narrower reported case; the three-stage workflow is a suggested practice, not an evaluated result |
| 8 | Standing project guidance versus reusable skills | A5, O1; examples are illustrative; instructions are not enforcement |
| 9 | Reusable prompt | Original synthesis for this talk; no guaranteed outcome claimed |
| 10 | Takeaways and reading | Original synthesis; reading links A1 and A5 |
| Appendix A | Ranges, other metrics and limitations | B1–B3 |
| Appendix B | Configuration-specific performance and API cost | X1, X2; dated public-page data snapshot |

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

Main charts start at zero. They display means, without uncertainty bands. Appendix ranges are observed minima and maxima, not confidence intervals.

Appendix A also retains descriptive context for the other methods. Caveman has n=2, mean net production LOC +396.5, cumulative output 85,989.5 and cognitive delta 150.5. Serena has n=1, net production LOC +497, output 84,165 and cognitive delta 156. Serena's setup fingerprint is `f1140b0cc89bade585633a3ad4c88603ee82faaf3a77a9b4bc8bb5b583c24805`; it is a separate cohort and is explicitly not presented as a paired comparison. These extra values do not enter the main charts or percentages.

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

Supports giving the agent a check, clarifying unspecified work, keeping instruction files focused, and reviewing against a specification. Its current context guidance does not make aggressive manual compaction a required ritual. These are recommendations, not a measured effect size for this talk. Used on slides 2–3 and as the first reading link.

## O1. OpenAI: Codex best practices

[Practical guide](https://learn.chatgpt.com/guides/best-practices).

Supports goal/context/constraints/done-when prompts, planning and interviews for difficult work, reusable project guidance, skills, and verification. Used as a supplementary source, with Anthropic the main teaching reference. It does not prove that a specific planning workflow reduces total usage.

## A2. Anthropic: Prompting best practices, overeagerness

[Overeagerness section](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#overeagerness).

Guidance against unnecessary code, abstractions and flexibility supports the small-change principle. The section discusses particular model behaviour; do not generalize it into a claim that all current models behave identically. It does not mention or endorse Ponytail.

## P1. Ponytail upstream

[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail).

Third-party skill/project focused on minimal complete changes and reuse. Its publisher's benchmark claims are not used as evidence here. This talk uses Artem's independent pilot instead. Current installed version and historical measured version need not be the same; consult the frozen profile manifest when reproducing the study.

## A3. Anthropic: Effective harnesses for long-running agents

[Article](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), published **26 November 2025**.

Reports incomplete undocumented work and premature completion in its agent setting. Uses progress artifacts, Git history and incremental work to bridge sessions. This is a particular historical system, not a claim that every current agent forgets in the same way. Used on slide 6.

## O2 / A4. Goals

- [O2: Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).
- [A4: Keep Claude working toward a goal](https://code.claude.com/docs/en/goal).

Both describe persistent completion conditions within their supported thread/session workflows. Implementations and stopping behaviour differ. Neither is complete cross-project memory or proof that the resulting application is correct. Use a supporting build/client version; no universal command syntax is taught in this talk.

## S1. Spotify Portal: token delegation case

[Portal by Spotify cut my Claude Code token usage by 90%](https://portal.spotify.com/blog/portal-by-spotify-cut-my-claude-code-token-usage-by-90), Dimitri Mazmanov, **3 September 2026**, updated **8 September 2026**.

Reports roughly 90% mean bulk-read token savings in testing across four Java-monorepo scenarios. Uses Gemini 2.5 Flash workers for large reads and predictable generation. The author describes a subtle bug the worker missed and additional latency. Do not represent this as 90% off total development cost, a company-wide result, or validation of the talk's strong-plan/cheaper-implementation/review suggestion. Used on slide 7.

## A5. Anthropic: Extend Claude Code

[Extension overview](https://code.claude.com/docs/en/features-overview).

Explains project instructions, skills, hooks, subagents, MCP and plugins. Standing guidance loads into context; skills provide reusable knowledge/procedures loaded or invoked for relevant work. Instructions remain probabilistic; enforcement and verification require other mechanisms. Used on slide 8 and as the second reading link.

## X1 / X2. Artificial Analysis

- [X1: Coding agents benchmark](https://artificialanalysis.ai/agents/coding-agents).
- [X2: Coding Agent Index v2.1 methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking).

Read the public page and its embedded variant records on **22 November 2026**. Store only the selected public measurements in the HTML's `evidence-data`, not a copy of the page. Index = `indexScore × 100`; API cost = `mean.costUsd`.

| Public variant ID | Configuration | Exact index | Exact mean API cost/task, USD |
| --- | --- | ---: | ---: |
| `4d278d53a18fbdcb5138d11466ea0b1b` | Claude Code + Claude Sonnet 5.5, Max, Default Fallback | 56.3314945150429 | 11.39857189877927 |
| `2b66aa9f8afa482977259846d9b207ba` | Codex + GPT-6.2 Sol, Xhigh | 49.7854108287173 | 0.8980194131553201 |

Appendix display rounds to 56.33 / $11.40 and 49.79 / $0.90. Index v2.1 equally weights FrontierCode-AA 2.0, Terminal-Bench 4.1 and SWE-Atlas-QnA-AA. Costs include applicable cache pricing; they exclude subscription pricing and full operational/human costs. Results describe configurations and do not isolate model quality from the agent. No ranking or universal Codex-efficiency claim is made.

## Organizer requirements and remaining human checks

The privately supplied **ProductTank Lausanne speaker guidelines 2026** were read in full. They request practical takeaways, lessons from experience, no sales pitches, a draft/outline 72 hours in advance, speaker name/photo and a 55–60-word bio. They describe a varied audience, organizer-assisted Q&A and arrival 30–45 minutes early. The private PDF is not redistributed.

For this particular talk Artem confirmed **30 minutes total**; the schedule therefore uses 23 + 7, rather than assuming the generic guideline's Q&A is additional. English slides and speech, browser presentation, and synthetic work examples were confirmed during preparation.

Event date, meetup registration, organizer delivery, photo selection, actual timed human rehearsal and venue-equipment checks remain human actions. They must not be marked complete by an automated HTML or PDF check.
