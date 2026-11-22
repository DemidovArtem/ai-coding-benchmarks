# Beyond Vibe Coding: AI Prototypes That Last

**Artem Demidov · ProductTank Lausanne · English · visual revision, 22 November 2026**

## Presenting

Open `index.html` directly in a browser, keeping `assets/` beside it. No server, installation or network is needed. External links need a connection. `deck.pdf` contains 24 main frames followed by both appendices: 26 pages in total. HTML links labelled Appendix A/B, the Appendix button, or A/B keys open the same material.

Right / Space / Page Down advances; Left / Page Up goes back. Home / End selects the first / final main frame. F toggles fullscreen. A / B opens an appendix; Escape returns. ? opens help; P prints the main frames. Direct links such as `index.html#slide-9` work.

Frames 12–15 and 16–17 develop the same visual in place. They are progressive reveals, not additional chapters. The schedule remains 23 minutes plus 7 minutes Q&A; the speaker can adjust pace. Rehearsal and venue equipment are **not delivery gates**, following Artem's feedback.

Employer material is never reproduced. Dashboard images are generated illustrations. Editable chat examples reconstruct the visual conventions of Codex; they are not observed sessions. Menu screenshots are real third-party images, with client/version scope. Documentation excerpts are browser captures of official pages. Red highlights are slide overlays. See `sources.md` and `assets/README.md`.

## 1. Beyond Vibe Coding — 0:00–0:30

Hello, I am Artem. This talk is about AI prototypes that remain easier to change after the exciting first version. I will share lessons from my own use, a small experiment, and guidance from the teams building coding agents.

## 2. The same change gets harder — 0:30–1:27

About a year ago, I started using AI-assisted coding. Early on, a useful result often took one attempt. Later, a similarly sized request could take three to five attempts, more quota and more checking.

The request on both sides is the same. The product underneath has changed. Rules were duplicated in three to five places, so a new feature needed more coordination. The buildings are metaphors for that experience, not application screenshots.

How do we keep the next feature from making later changes harder?

## 3. Leave less to maintain — 1:27–2:15

Some earlier features added about three thousand lines. A later feature might add three hundred and remove two hundred. These were different features, so this is not a controlled percentage saving.

The buildings show the distinction I care about: attaching more machinery, or reusing and simplifying what is already there. A feature can leave less redundant material behind. That gives us less to keep consistent on the next change.

## 4. Three habits for the next feature — 2:15–2:51

Three habits organize the talk. Keep changes small, using Ponytail as one tool. Explicitly use Planning Mode and agree on checks. Preserve progress when the conversation becomes long. I will add a short model-budget example, then leave you with a workflow you can try on your next feature.

## 5. Add Ponytail to your agent — 2:51–4:00

Ponytail is a third-party skill and plugin. It asks the agent to reuse existing functionality and prefer the smallest complete change. Necessary validation, error handling, security and checks remain part of the work.

This is a setup step. Install it for the agent you use and check that it is active. You can ask your agent to help install it from the official repository. The request and activation label here are illustrative; exact commands are in the notes.

It gives us useful defaults. We still have to define the feature and check the result. A plugin does not know what our product should do.

## 6. Ponytail: three separate checks — 4:00–5:03

Here are three separate checks of Ponytail. Its author reports around fifty-three percent less code and forty-five percent fewer output tokens. JetBrains independently measured around fifteen percent less code written and ten percent lower API cost. My pilot found around twenty-seven percent less net code growth and seven percent fewer output tokens.

These use different models, tasks and metrics. Read them as separate observations, not interchangeable percentages or a pooled result. JetBrains found clearer statistical evidence for cost than for code reduction; my pilot is too small for significance claims. None establishes a guarantee of higher quality.

## 7. Keep your setup simple — 5:03–6:48

These are examples of installable skills, tools and plugins. Caveman compresses explanations. Serena provides code navigation and project memories. ECC bundles agents, hooks and skills.

The configuration matters. Caveman was always on. Serena had a required workflow: navigation and memory steps before other work. These results include those activation rules, not just installing the tools. The pinned Caveman plugin also defaults to caveman mode, so I cannot call always-on use a departure from that plugin's default. This does not show either tool is inherently harmful, or isolate enforcement as the cause.

Caveman used around twenty-eight percent more output tokens. Serena used around forty-eight percent more input tokens than the displayed baseline, including cache reads, in a separate setup. ECC used around one hundred and twenty-four thousand output tokens across six edits and introduced a regression at edit three. Different runtimes and recoveries prevent a clean quality ranking.

Choose when a tool should run and check the result. Ponytail is designed to inject its rules continuously in full mode by default; the smaller code-growth result was measured with that activation. That is why it is my starting point, rather than a reason to force every other tool into every turn.

## 8. Use Planning Mode — 6:48–7:57

The second habit is to turn on Planning Mode explicitly. Asking a question in an implementation session is not the same action.

These are real cropped headings from official OpenAI and Anthropic documentation. They support reviewing a plan before making changes. This is a practical workflow recommendation, not a trick I discovered alone.

Planning helps when the feature is complex or I am still deciding what I want. It gives the agent room to inspect the project, identify ambiguity and ask questions before implementation. It is not a promise of lower token use. A tiny clear edit does not need a long planning ceremony.

## 9. Turn it on before prompting — 7:57–9:15

[Point to the red rectangles and distinguish the clients.]

In the current Codex desktop command set, type slash-plan to toggle Planning Mode. The screenshot shows an earlier desktop interface, where the command menu labels it Plan mode.

In Claude Code, use the mode menu and select Plan mode. This image is the VS Code interface. In the terminal, the official workflow says to press Shift-Tab until the status bar shows plan mode on, or start with the documented plan permission mode.

Desktop, terminal and editor controls differ. See that Planning Mode is active before sending the feature request. Once the agent has explored and you have agreed on the plan, review it. Then switch into implementation with that plan. We are deliberately separating deciding the work from changing the product.

## 10. Use Planning Mode to clarify the task — 9:15–9:57

With Planning Mode active, ask the agent to resolve ambiguity: I want an expenses dashboard. Ask the questions needed before we agree on a plan.

This reconstructed example shows one decision: export only the selected month. That affects the interface, calculation and exported rows. Review the resulting plan and save it, so another model can implement the same agreement.

## 11. Give the agent a way to check — 9:57–10:45

There is another part of the agreement: how will the agent check the result? Anthropic's documentation makes this explicit.

If the agent has no way to check what you wanted, that review work comes back to you. You inspect the result, spot a missing requirement, and ask again. The next frames illustrate that loop. They are teaching examples, not measurements of how often agents fail or how much time this saves.

## 12. “Build me an expenses dashboard.” — 10:45–11:30

[Pause before revealing the corrections.]

Suppose I only ask for an expenses dashboard. The agent produces a plausible screen with a table and total. It looks finished. There is no month filter and no Export CSV button.

The model could not infer every product decision I had in mind. Now I discover the gaps while using the result. A polished appearance can delay that discovery because the screen initially looks convincing.

## 13. Your review becomes the test — 11:30–12:18

I ask where the export button is. Then I ask for a month filter. Then I clarify that the export should contain only that month.

Each correction may require another change and another review. We moved the requirements conversation into implementation. That is the avoidable part of this back-and-forth.

Clear requirements will not eliminate debugging. They give the agent information it could not otherwise know and make the remaining review more focused.

## 14. Define the result and the check — 12:18–13:15

Here we agree on a January filter, exporting the selected rows, and a known calculation: one hundred plus two hundred is three hundred.

Ask the agent to verify the interface in the browser and the calculation using known inputs. A screenshot demonstrates appearance. A test or inspection of exported rows demonstrates behaviour. Include a failure case, such as preserving saved data when a source is unavailable.

For a communication prototype, choose checks for the intended scenario. A recurring personal tool also needs safe reruns and data preservation.

## 15. Move the checks into the task — 13:15–14:18

The contrast is the workflow. On the left, I build from a vague request and become the person discovering missing requirements. On the right, the task includes a concrete result and checks the agent can perform.

The right image is a desired illustrative result, not a promise of one-shot success. The agent can still misunderstand, fail a test or need another attempt. We gave it a way to detect more gaps before asking us to review.

For a product manager, this is a useful change: make the intended result observable and ask for evidence that it happened.

## 16. Your conversation has a limit — 14:18–14:54

Long coding sessions accumulate requirements, decisions, code and tool output. Active context has a limit. The red diagram shows that working space getting crowded.

Coding agents compact earlier context so work can continue. The trigger depends on the agent, model and configuration. This drawing does not claim a particular percentage.

## 17. Compaction keeps a summary — 14:54–15:39

Compaction keeps a summary of earlier material. A summary can leave out a detail that later matters.

In this illustration, the instruction to export only the selected month is dropped. A later turn asks whether to export all rows. This is an example of a possible omission, not a measured retention rate.

Keep a short, current record of decisions that the next turn needs to recover.

## 18. Save the work. Keep the goal — 15:39–16:27

Ask the agent to save the plan, decisions, checks and next step. Keep that file current at useful milestones.

At the next session, ask it to read the handover, inspect the project and continue. Files can become stale; code and checks still matter. This example uses the visual conventions of Codex, with an invented conversation.

Files preserve details. A goal preserves what we are trying to finish. Use both.

## 19. Set the finish line with /goal — 16:27–17:30

Use slash-goal with a completion condition. Here it points to PLAN.md, names the required checks and protects existing data.

Codex documents a durable objective scoped to the thread. Claude Code documents a session goal and an evaluator that decides whether the condition is met. Their continuation and stopping rules differ.

Neither is global long-term memory. The point is to keep working toward an observable finish line instead of ending after a plausible partial answer. Save the detailed plan and results in files, and ask the agent to show verification evidence. A goal cannot guarantee completion or correctness.

## 20. Turn repeated instructions into guidance — 17:30–18:15

If you repeat a rule, ask the agent to save it in AGENTS.md or CLAUDE.md. For example: reuse existing UI before adding another component.

If you repeat a procedure, ask for a skill. The prompt here names the steps: check an import fixture, simulate failure, and verify saved data survives. Keep guidance focused. Instructions guide behaviour; checks show whether it happened.

## 21. Use cheaper models for the long middle — 18:15–19:39

This is a workflow I use: plan with a stronger model, give the saved plan and goal to a cheaper model for implementation, then use a stronger model for final corrections when needed.

Implementation can be the long middle: writing code, running checks and fixing it. Keeping that loop off the premium model helps my budget. This is my practical observation, not a measured saving from my pilot. It need not reduce total tokens; the benefit depends on model prices, quotas and rework.

Spotify Portal offers a related, narrower example: around ninety percent average bulk-read token savings across four Java scenarios. It delegates large reads and predictable generation to a cheaper worker. That is not ninety percent off the total bill, and it does not validate this full three-stage workflow.

## 22. Codex + Sol: a lower-cost option — 19:39–20:54

Both numbers describe Codex with GPT-6.2 Sol relative to Claude Code with Sonnet 5.5 in the stated Artificial Analysis configurations. The model being compared is now one shared heading, with the reference configuration immediately below it.

Codex has roughly thirteen times lower mean API cost and a twelve percent lower Coding Agent Index. That is a cost-performance tradeoff. API cost reflects token use, model prices and caching; it is not a direct measure of subscription quota. Exact values remain in appendix B.

My separate experience is that Codex lets me get more coding done within my limits and its quality is enough for many of my tasks. Try the configuration on your own acceptance checks.

## 23. A workflow, not one magic prompt — 20:54–21:36

These are separate actions. Start with Ponytail if its defaults help. Use Planning Mode to describe the outcome, resolve ambiguity and agree on checks. Save the plan and set a goal. Implement, verify and preserve a handover.

A communication prototype and a recurring personal tool need different checks. The common habit is to make the intended result observable and keep evidence of progress.

## 24. Make the next change easier — 21:36–23:00

Here are five actions for your next feature. Install Ponytail using the direct link. Use Planning Mode and define requirements. Use a goal and save a handover.

When you repeat a rule, ask the agent to save it in AGENTS.md or CLAUDE.md. When you repeat a procedure, ask the agent to make a skill.

If quota is tight, first try a strong model for planning and a cheaper model for implementation, with stronger review when needed. If you still hit the limits, try Codex. These are budget options based on my experience, not a promise about every subscription.

The readings explain practical checks and how instructions, skills, hooks and other components fit together. The repository contains my experiment sources and limitations. Thank you. What makes changing your prototypes difficult?

## Appendix reference and setup

### Ponytail installation

Reference commands, not executed for this presentation. Checked against upstream on 22 November 2026. Installation and trust decisions belong to the user's environment.

Claude Code, two separate prompts:

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

Codex CLI:

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

Upstream then instructs Codex users to open `/hooks`, review/trust its two lifecycle hooks, and start a new thread. Use the official repository. The slide's activation label is illustrative.

### Planning Mode controls

- Codex desktop: `/plan`, per [official slash commands](https://learn.chatgpt.com/docs/reference/slash-commands). Image: earlier desktop UI via Codecademy.
- Claude Code: choose Plan mode in the mode picker. Image: VS Code interface via Paweł Huryn / Product Compass.
- Claude Code terminal: `Shift+Tab` until `plan mode on`, or `claude --permission-mode plan`, per [official common workflows](https://code.claude.com/docs/en/common-workflows#plan-before-editing).
- Claude desktop: permission-mode selector below the prompt. Terminal shortcuts do not apply universally. See [desktop docs](https://code.claude.com/docs/en/desktop#choose-a-permission-mode).

### Own benchmark limitations

Frozen six-step ripgrep cohort, fixed model/effort `gpt-6.1-sol` / `high`, historical Codex 0.163.0. Baseline/Ponytail n=2 each; steps dependent. Net production LOC: 413.5 [322–505] versus 301 [286–316]. Cumulative output: 67,311.5 [65,442–69,181] versus 62,766 [59,521–66,011]. Ranges are observed min–max, not confidence intervals. Main displays round reductions to approximately 27% and 7%.

All seven step-6 trajectories in the wider study have valid grading but are unresolved, each passing 7/8 new tests. Step-5 grading is invalid because of an undeclared dependency. Runtime/protocol limitations and earlier failures prevent attributing every rejection to accumulated agent error. One Ponytail continuation includes authorized removal of one API-rejected encrypted reasoning item from a checkpoint copy; source and other history were preserved. No significance, dollar-saving or quality-superiority claim is established.

Physical production LOC includes comments/blank lines under the pinned filtering. Net growth is added minus deleted lines between initial/final filtered trees. Churn is added plus deleted lines between those trees, not a sum of intermediate changes. Output is cumulative per trajectory, then averaged. Sonar includes inline tests and benchmark masking. Cognitive deltas: baseline 142; Ponytail 150.5; no consistent quality winner.

Caveman n=2: net production LOC +396.5, output 85,989.5, cognitive delta 150.5. Serena n=1: +497, 84,165 and 156; a separate setup cohort, not a paired baseline comparison. Appendix A retains them as descriptive context. The separate earlier planning pilot had n=1 per condition and higher output with planning; do not pool its baseline with this cohort.

### Publisher benchmark limitations

The 7 October 2026 report uses Opus 5.5, Claude Code CLI 2.1.288, 39 tasks, 5 runs per task/arm. Reductions are geometric means of per-task median ratios. Bash is disabled: agents write code and tests; the harness runs checks afterwards. Only 18 surgical tasks have hidden correctness checks; other tasks have different completeness checks. Do not pool these results with old single-shot comparisons or Artem's sequential experiment. No universal safety guarantee is claimed.

### Model comparison

Artificial Analysis, checked 22 November 2026: Claude Code + Sonnet 5.5, Max / Default Fallback: index 56.33, mean API cost $11.40/task. Codex + GPT-6.2 Sol, Xhigh: index 49.79, $0.90/task. Costs are benchmark API costs with applicable cache pricing, not subscriptions, quota, review time or total operating costs. Index is not a percentage of code correctness. See appendix B and `sources.md`.

## Organizer information

Title: **Beyond Vibe Coding: AI Prototypes That Last**. Speaker: **Artem Demidov**.

Proposed bio, **56 words**:

> Artem Demidov experiments with AI-assisted coding and studies how agent configurations affect code growth, quality metrics, and token use. His open-source benchmark compares workflows across successive changes to an existing repository. In this talk, he shares lessons from practical use, preliminary experiment results, and documented techniques for building prototypes that remain easier to change over time.

The organizer asks for a draft/outline 72 hours before the event. Date, photo, registration and equipment are outside this visual revision. No organizer message or registration has been sent. The speaker handles rehearsal and venue arrangements; these do not keep presentation delivery blocked.

## Maintenance

Run `python3 verify.py` for the public-analysis/asset checks. No model calls or Docker. This verifies pinned data, rounded displays, local assets and frame structure; browser/PDF review is separate. Edit the HTML directly. Data are in `evidence-data`. Preserve frozen cohort boundaries. Red annotations are CSS overlays on unmodified screenshots.

Regenerate the PDF with an installed Chrome:

```bash
google-chrome --headless --force-color-profile=srgb --print-to-pdf="$PWD/deck.pdf" --no-pdf-header-footer "file://$PWD/index.html"
```

Browser Print → Save as PDF also works. Container sandbox flags vary. Print CSS includes 24 main frames followed by both appendices. The main talk still has 24 frames; appendices are optional Q&A material.
