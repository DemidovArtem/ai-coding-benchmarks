# Beyond Vibe Coding: AI Prototypes That Last

**Artem Demidov · ProductTank Lausanne · English · visual revision, 22 November 2026**

## Presenting

Open `index.html` directly in a browser, keeping `assets/` beside it. No server, installation or network is needed. External links need a connection. `deck.pdf` contains all 26 main frames. Two appendices are available in HTML.

Right / Space / Page Down advances; Left / Page Up goes back. Home / End selects the first / final main frame. F toggles fullscreen. A / B opens an appendix; Escape returns. ? opens help; P prints the main frames. Direct links such as `index.html#slide-9` work.

Frames 14–17 and 18–19 develop the same visual in place. They are progressive reveals, not additional chapters. The schedule remains 23 minutes plus 7 minutes Q&A; the speaker can adjust pace. Rehearsal and venue equipment are **not delivery gates**, following Artem's feedback.

Employer material is never reproduced. Dashboard images are generated illustrations. Editable chat examples reconstruct the visual conventions of Codex; they are not observed sessions. Menu screenshots are real third-party images, with client/version scope. Documentation excerpts are browser captures of official pages. Red highlights are slide overlays. See `sources.md` and `assets/README.md`.

## 1. Beyond Vibe Coding — 0:00–0:27

Hello, I am Artem. This talk is about AI prototypes that remain easier to change after the exciting first version. I will share lessons from my own use, a small experiment, and guidance from the teams building coding agents.

## 2. The same change gets harder — 0:27–1:21

About a year ago, I started using AI-assisted coding. Early on, a useful result often took one attempt. Later, a similarly sized request could take three to five attempts, more quota and more checking.

The request on both sides is the same. The product underneath has changed. Rules were duplicated in three to five places, so a new feature needed more coordination. The buildings are metaphors for that experience, not application screenshots.

How do we keep the next feature from making later changes harder?

## 3. Leave less to maintain — 1:21–2:06

Some earlier features added about three thousand lines. A later feature might add three hundred and remove two hundred. These were different features, so this is not a controlled percentage saving.

The buildings show the distinction I care about: attaching more machinery, or reusing and simplifying what is already there. A feature can leave less redundant material behind. That gives us less to keep consistent on the next change.

## 4. Three habits for the next feature — 2:06–2:39

Three habits organize the talk. Keep changes small, using Ponytail as one tool. Explicitly use Planning Mode and agree on checks. Preserve progress when the conversation becomes long. I will add a short model-budget example, then leave you with a workflow you can try on your next feature.

## 5. Add Ponytail to your agent — 2:39–3:45

Ponytail is a third-party skill and plugin. It asks the agent to reuse existing functionality and prefer the smallest complete change. Necessary validation, error handling, security and checks remain part of the work.

This is a setup step. Install it for the agent you use and check that it is active. You can ask your agent to help install it from the official repository. The request and activation label here are illustrative; exact commands are in the notes.

It gives us useful defaults. We still have to define the feature and check the result. A plugin does not know what our product should do.

## 6. Ponytail: publisher and my pilot — 3:45–4:30

Ponytail's author reports around fifty-three percent less code and forty-five percent fewer output tokens. My six-edit pilot found around twenty-seven percent less net code growth and seven percent fewer output tokens.

I put them together to show the direction and the difference in scale. They use different tasks, models, code measures and statistics. These are separate findings, not a replication or a forecast for your application.

## 7. What my small pilot found — 4:30–5:15

Here is my pilot as a chart. Baseline is one hundred on each measure. There are two independent six-edit trajectories per displayed method, on the same model and setup. Each change continues the previous one.

Quality measurements did not establish a winner. Less code is not proof of correctness. The appendix retains exact values, variation and grading limitations. These are output tokens, not dollars or subscription quota.

## 8. An independent check: JetBrains — 5:15–5:57

JetBrains independently tested these skills. For Ponytail, eighty paired tasks showed about fifteen percent less code written and ten percent lower API cost. The code result was less statistically certain than the cost result.

Their separate Caveman evaluation found around nine percent fewer output tokens. Neither evaluation detected a task-score difference; that does not prove unchanged quality. Effects depend on the workload, model and activation.

## 9. Keep your setup simple — 5:57–7:21

My recommendation is to keep the initial setup simple. I would start with Ponytail, verify activation, and add tools for a specific need.

Caveman shortens explanations. In my matched pilot it used around twenty-eight percent more output tokens, despite slightly lower net code growth. That differs from JetBrains; a small pilot is not a universal result.

Serena provides semantic code navigation and editing, plus project memories. Tools and retained memories worked, but one separate trajectory does not establish a quality benefit or harm.

ECC bundles agents, hooks and skills. Its author reports winning an Anthropic hackathon. My offline Codex pilot completed six edits after integration and recovery. It is a separate runtime and one interrupted trajectory, so I cannot rank its effectiveness against the earlier arms. Installation is only the start: verify what actually runs.

## 10. Use Planning Mode — 7:21–8:27

The second habit is to turn on Planning Mode explicitly. Asking a question in an implementation session is not the same action.

These are real cropped headings from official OpenAI and Anthropic documentation. They support reviewing a plan before making changes. This is a practical workflow recommendation, not a trick I discovered alone.

Planning helps when the feature is complex or I am still deciding what I want. It gives the agent room to inspect the project, identify ambiguity and ask questions before implementation. It is not a promise of lower token use. A tiny clear edit does not need a long planning ceremony.

## 11. Turn it on before prompting — 8:27–9:42

[Point to the red rectangles and distinguish the clients.]

In the current Codex desktop command set, type slash-plan to toggle Planning Mode. The screenshot shows an earlier desktop interface, where the command menu labels it Plan mode.

In Claude Code, use the mode menu and select Plan mode. This image is the VS Code interface. In the terminal, the official workflow says to press Shift-Tab until the status bar shows plan mode on, or start with the documented plan permission mode.

Desktop, terminal and editor controls differ. See that Planning Mode is active before sending the feature request. Once the agent has explored and you have agreed on the plan, review it. Then switch into implementation with that plan. We are deliberately separating deciding the work from changing the product.

## 12. Use Planning Mode to clarify the task — 9:42–10:21

With Planning Mode active, ask the agent to resolve ambiguity: I want an expenses dashboard. Ask the questions needed before we agree on a plan.

This reconstructed Codex-style example shows one decision: export only the selected month. That affects the interface, calculation and exported rows. Review the resulting plan and save it, so another model can implement the same agreement.

## 13. Give the agent a way to check — 10:21–11:09

There is another part of the agreement: how will the agent check the result? Anthropic's documentation makes this explicit.

If the agent has no way to check what you wanted, that review work comes back to you. You inspect the result, spot a missing requirement, and ask again. The next frames illustrate that loop. They are teaching examples, not measurements of how often agents fail or how much time this saves.

## 14. “Build me an expenses dashboard.” — 11:09–11:54

[Pause before revealing the corrections.]

Suppose I only ask for an expenses dashboard. The agent produces a plausible screen with a table and total. It looks finished. There is no month filter and no Export CSV button.

The model could not infer every product decision I had in mind. Now I discover the gaps while using the result. A polished appearance can delay that discovery because the screen initially looks convincing.

## 15. Your review becomes the test — 11:54–12:42

I ask where the export button is. Then I ask for a month filter. Then I clarify that the export should contain only that month.

Each correction may require another change and another review. We moved the requirements conversation into implementation. That is the avoidable part of this back-and-forth.

Clear requirements will not eliminate debugging. They give the agent information it could not otherwise know and make the remaining review more focused.

## 16. Define the result and the check — 12:42–13:39

Here we agree on a January filter, exporting the selected rows, and a known calculation: one hundred plus two hundred is three hundred.

Ask the agent to verify the interface in the browser and the calculation using known inputs. A screenshot demonstrates appearance. A test or inspection of exported rows demonstrates behaviour. Include a failure case, such as preserving saved data when a source is unavailable.

For a communication prototype, choose checks for the intended scenario. A recurring personal tool also needs safe reruns and data preservation.

## 17. Move the checks into the task — 13:39–14:42

The contrast is the workflow. On the left, I build from a vague request and become the person discovering missing requirements. On the right, the task includes a concrete result and checks the agent can perform.

The right image is a desired illustrative result, not a promise of one-shot success. The agent can still misunderstand, fail a test or need another attempt. We gave it a way to detect more gaps before asking us to review.

For a product manager, this is a useful change: make the intended result observable and ask for evidence that it happened.

## 18. Your conversation has a limit — 14:42–15:18

Long coding sessions accumulate requirements, decisions, code and tool output. Active context has a limit. The red diagram shows that working space getting crowded.

Coding agents compact earlier context so work can continue. The trigger depends on the agent, model and configuration. This drawing does not claim a particular percentage.

## 19. Compaction keeps a summary — 15:18–16:03

Compaction keeps a summary of earlier material. A summary can leave out a detail that later matters.

In this illustration, the instruction to export only the selected month is dropped. A later turn asks whether to export all rows. This is an example of a possible omission, not a measured retention rate.

Keep a short, current record of decisions that the next turn needs to recover.

## 20. Save the work. Keep the goal — 16:03–16:48

Ask the agent to save the plan, decisions, checks and next step. Keep that file current at useful milestones.

At the next session, ask it to read the handover, inspect the project and continue. Files can become stale; code and checks still matter. This example uses the visual conventions of Codex, with an invented conversation.

Files preserve details. A goal preserves what we are trying to finish. Use both.

## 21. Set the finish line with /goal — 16:48–17:51

Use slash-goal with a completion condition. Here it points to PLAN.md, names the required checks and protects existing data.

Codex documents a durable objective scoped to the thread. Claude Code documents a session goal and an evaluator that decides whether the condition is met. Their continuation and stopping rules differ.

Neither is global long-term memory. The point is to keep working toward an observable finish line instead of ending after a plausible partial answer. Save the detailed plan and results in files, and ask the agent to show verification evidence. A goal cannot guarantee completion or correctness.

## 22. Turn repeated instructions into guidance — 17:51–18:33

If you repeat a rule, ask the agent to save it in AGENTS.md or CLAUDE.md. For example: reuse existing UI before adding another component.

If you repeat a procedure, ask for a skill. The prompt here names the steps: check an import fixture, simulate failure, and verify saved data survives. Keep guidance focused. Instructions guide behaviour; checks show whether it happened.

## 23. Use cheaper models for the long middle — 18:33–19:54

This is a workflow I use: plan with a stronger model, give the saved plan and goal to a cheaper model for implementation, then use a stronger model for final corrections when needed.

Implementation can be the long middle: writing code, running checks and fixing it. Keeping that loop off the premium model helps my budget. This is my practical observation, not a measured saving from my pilot. It need not reduce total tokens; the benefit depends on model prices, quotas and rework.

Spotify Portal offers a related, narrower example: around ninety percent average bulk-read token savings across four Java scenarios. It delegates large reads and predictable generation to a cheaper worker. That is not ninety percent off the total bill, and it does not validate this full three-stage workflow.

## 24. Codex + Sol: a lower-cost option — 19:54–21:09

Artificial Analysis compares specific agent, model and effort configurations. In the checked snapshot, Codex with GPT-6.2 Sol costs about ninety cents per task; Claude Code with Sonnet 5.5 costs about eleven dollars forty.

That is roughly thirteen times lower mean API cost. Index values are about fifty and fifty-six: around six and a half points, or twelve percent, lower. The index is not percentage accuracy. This is a cost-performance tradeoff, not equal quality.

Separately, my subscription experience is that Codex lets me get more coding done, and its quality is enough for many of my tasks. This benchmark does not measure subscription limits or establish that experience for everyone. Try the cheaper configuration on your own acceptance checks.

## 25. A workflow, not one magic prompt — 21:09–21:51

These are separate actions. Start with Ponytail if its defaults help. Use Planning Mode to describe the outcome, resolve ambiguity and agree on checks. Save the plan and set a goal. Implement, verify and preserve a handover.

A communication prototype and a recurring personal tool need different checks. The common habit is to make the intended result observable and keep evidence of progress.

## 26. Make the next change easier — 21:51–23:00

Define what done looks like. Ask for a small, complete implementation. Keep checks and a handover so the next change starts from useful evidence.

The first reading is Anthropic's practical best-practice guide. The second explains instruction files, skills, hooks and the other extension components. The linked materials include OpenAI guidance, Spotify, and my experiment's sources and limitations.

Pick one habit for your next feature. If you discover missing details late, start with Planning Mode and checks. If changes keep introducing machinery, try Ponytail and inspect the result. If long sessions lose decisions, save a current handover. Thank you. Which part of changing your prototypes is becoming difficult?

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
google-chrome --headless --print-to-pdf="$PWD/deck.pdf" --no-pdf-header-footer "file://$PWD/index.html"
```

Browser Print → Save as PDF also works. Container sandbox flags vary. Print CSS includes 26 main frames and excludes both appendices.
