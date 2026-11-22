# Beyond Vibe Coding: AI Prototypes That Last

**Artem Demidov · ProductTank Lausanne · English · visual revision, 22 November 2026**

## Presenting

Open `index.html` directly in a browser, keeping `assets/` beside it. No server, installation or network is needed. External links need a connection. `deck.pdf` contains all 22 main frames. Two appendices are available in HTML.

Right / Space / Page Down advances; Left / Page Up goes back. Home / End selects the first / final main frame. F toggles fullscreen. A / B opens an appendix; Escape returns. ? opens help; P prints the main frames. Direct links such as `index.html#slide-9` work.

Frames 12–15 and 16–17 develop the same visual in place. They are progressive reveals, not additional chapters. The schedule remains 23 minutes plus 7 minutes Q&A; the speaker can adjust pace. Rehearsal and venue equipment are **not delivery gates**, following Artem's feedback.

Employer material is never reproduced. Dashboard images and chats are illustrative. Menu screenshots are real third-party images, with client/version scope. Documentation excerpts are browser captures of official pages. Red highlights are slide overlays. See `sources.md` and `assets/README.md`.

## 1. Cover — 0:00–0:18

Hello, I am Artem. This talk is about AI prototypes that remain easier to change after the exciting first version. I will share lessons from my own use, a small experiment, and guidance from the teams building coding agents.

## 2. The next change got harder — 0:18–1:30

[Let the building illustration carry the story.]

About a year ago, I started using AI-assisted coding. Early on, I could describe a feature and often get something useful in one attempt. As the application grew, I started needing three to five attempts, more quota, and more checking.

The same idea could live in three to five places. A new change had to find all of them and keep them consistent. The illustration is a metaphor: a simple building has acquired many additions, each reasonable on its own, until the whole structure becomes difficult to work on.

I cannot show material from my previous work. The experience is mine; the building and examples are invented. The question is how to keep the next feature from making every later feature harder.

## 3. Different feature diffs — 1:30–2:30

Some earlier features added about three thousand lines. A later change might add three hundred and remove two hundred. These were different features. This is a personal observation, not a controlled comparison or a percentage saving.

I am showing the amount of material a change can leave us to maintain. Deleting redundant code can be part of implementing a feature. The practical question is what the feature actually needs and what already exists. That is the thinking I want to make easier to ask of an agent.

## 4. Agenda — 2:30–3:00

Three habits organize the talk. Keep changes small, using Ponytail as one tool. Explicitly use Planning Mode and agree on checks. Preserve progress when the conversation becomes long. I will add a short model-budget example, then leave you with a workflow you can try on your next feature.

## 5. Add Ponytail — 3:00–4:00

Ponytail is a third-party skill and plugin. It asks the agent to reuse existing functionality and prefer the smallest complete change. Necessary validation, error handling, security and checks remain part of the work.

This is a setup step. Install it for the agent you use and check that it is active. You can ask your agent to help install it from the official repository. The request and activation label here are illustrative; exact commands are in the notes.

It gives us useful defaults. We still have to define the feature and check the result. A plugin does not know what our product should do.

## 6. Publisher results — 4:00–5:00

Here is what Ponytail's author currently reports: roughly fifty-three percent less code and forty-five percent fewer output tokens, with lower time and cost in that benchmark.

These are publisher-reported agentic results on thirty-nine tasks, with five runs per task and arm. They use a particular model and setup. This is not a forecast for your application.

The older eighty-to-ninety-four-percent headline came from a single-shot comparison with important limitations. I use the newer report here. The next slide is my independent, much smaller experiment, with a different workload and measurement method.

## 7. My pilot — 5:00–6:30

My pilot compares the same model with and without Ponytail across six sequential changes to an existing repository. There are two independent trajectories per displayed method. Successive changes depend on the previous ones.

Baseline is one hundred percent on both charts. Ponytail's mean net code growth is around twenty-seven percent lower. Cumulative output tokens are around seven percent lower. I rounded the display because decimal places would suggest more certainty than this small sample supports.

These measures differ from the publisher's benchmark, so the percentages are not directly comparable. My quality measurements did not establish a winner. Less code is a useful observation, not proof of correctness.

The appendix has exact values, ranges and grading limitations. Output tokens do not equal total usage, subscription quota or dollars. Compare a configuration against checks and measurements rather than accept a universal saving claim.

## 8. Use Planning Mode — 6:30–7:30

The second habit is to turn on Planning Mode explicitly. Asking a question in an implementation session is not the same action.

These are real cropped headings from official OpenAI and Anthropic documentation. They support reviewing a plan before making changes. This is a practical workflow recommendation, not a trick I discovered alone.

Planning helps when the feature is complex or I am still deciding what I want. It gives the agent room to inspect the project, identify ambiguity and ask questions before implementation. It is not a promise of lower token use. A tiny clear edit does not need a long planning ceremony.

## 9. Turn Planning Mode on — 7:30–9:00

[Point to the red rectangles and distinguish the clients.]

In the current Codex desktop command set, type slash-plan to toggle Planning Mode. The screenshot shows an earlier desktop interface, where the command menu labels it Plan mode.

In Claude Code, use the mode menu and select Plan mode. This image is the VS Code interface. In the terminal, the official workflow says to press Shift-Tab until the status bar shows plan mode on, or start with the documented plan permission mode.

Desktop, terminal and editor controls differ. See that Planning Mode is active before sending the feature request. Once the agent has explored and you have agreed on the plan, review it. Then switch into implementation with that plan. We are deliberately separating deciding the work from changing the product.

## 10. Ask necessary questions — 9:00–10:00

Now give the actual request: I want an expenses dashboard. Ask the questions needed to resolve ambiguity. Do not implement yet.

This synthetic conversation illustrates one useful question: should exporting use the selected month? We decide that it should. That small decision affects the interface, calculation and exported data.

Let the agent help uncover these decisions. Ask it to save the agreed requirements and plan. Those files let you hand implementation to another model or continue later without reconstructing the conversation. This screen is an illustration, not a measured model run.

## 11. Give the agent a check — 10:00–10:45

There is another part of the agreement: how will the agent check the result? Anthropic's documentation makes this explicit.

If the agent has no way to check what you wanted, that review work comes back to you. You inspect the result, spot a missing requirement, and ask again. The next frames illustrate that loop. They are teaching examples, not measurements of how often agents fail or how much time this saves.

## 12. The vague request — 10:45–11:30

[Pause before revealing the corrections.]

Suppose I only ask for an expenses dashboard. The agent produces a plausible screen with a table and total. It looks finished. There is no month filter and no Export CSV button.

The model could not infer every product decision I had in mind. Now I discover the gaps while using the result. A polished appearance can delay that discovery because the screen initially looks convincing.

## 13. Review, correct, repeat — 11:30–12:15

I ask where the export button is. Then I ask for a month filter. Then I clarify that the export should contain only that month.

Each correction may require another change and another review. We moved the requirements conversation into implementation. That is the avoidable part of this back-and-forth.

Clear requirements will not eliminate debugging. They give the agent information it could not otherwise know and make the remaining review more focused.

## 14. Describe a checkable result — 12:15–13:00

Here we agree on a January filter, exporting the selected rows, and a known calculation: one hundred plus two hundred is three hundred.

Ask the agent to verify the interface in the browser and the calculation using known inputs. A screenshot demonstrates appearance. A test or inspection of exported rows demonstrates behaviour. Include a failure case, such as preserving saved data when a source is unavailable.

For a communication prototype, choose checks for the intended scenario. A recurring personal tool also needs safe reruns and data preservation.

## 15. Move checks into the task — 13:00–14:00

The contrast is the workflow. On the left, I build from a vague request and become the person discovering missing requirements. On the right, the task includes a concrete result and checks the agent can perform.

The right image is a desired illustrative result, not a promise of one-shot success. The agent can still misunderstand, fail a test or need another attempt. We gave it a way to detect more gaps before asking us to review.

For a product manager, this is a useful change: make the intended result observable and ask for evidence that it happened.

## 16. Context has a limit — 14:00–14:45

Long coding sessions accumulate requirements, decisions, code and tool output. The model's active context has a limit.

This diagram shows a nearly full context. Ninety-five percent is illustrative, not the trigger used by every agent. During long work, coding agents may compact earlier context so the task can continue. That supports long-running work and gives us a reason to save important state explicitly.

## 17. Compaction — 14:45–15:30

Compaction keeps a summary of earlier material. A summary can leave out a detail that later matters.

In this illustration, the instruction to export only the selected month is dropped. A later turn asks whether to export all rows. This is a possible failure mode, not a measured retention rate or a claim that compaction always loses this information.

Keep a short, current record of decisions that the next turn needs to recover.

## 18. Save the state and goal — 15:30–17:00

Ask the agent directly to save the plan, decisions, checks and next step to a file. This synthetic screenshot shows the request and a handover document.

At the next session, tell the agent to read that file, inspect the current project and continue. A file can become stale, so the actual code and checks still matter.

Use a goal to keep the completion condition in view: implement the agreed plan and verify the acceptance criteria. Codex and Claude Code both document goal features, with different implementations and stopping behaviour.

A goal is not complete long-term memory. Files preserve details; the goal describes the finish line. Anthropic's long-running-agent work describes incomplete undocumented work and premature completion as failure patterns. Saved artifacts give later sessions something explicit to inspect.

## 19. Rules and skills — 17:00–18:00

For a rule you keep repeating, ask the agent to preserve it in project guidance: AGENTS.md or CLAUDE.md, according to the agent you use.

For a procedure you repeat, ask it to make a skill. Import validation is one example: use a fixture, simulate failure, and verify preserved data.

Keep instructions specific and short. They guide the agent; they do not enforce behaviour. Checks still establish whether the rule was followed. Start with a recurring problem you actually have rather than install every extension you can find.

## 20. Model-budget bonus — 18:00–20:00

When budget is a constraint, try allocating the strongest model to ambiguity and difficult review. A cheaper model can be a candidate for implementing a well-specified plan with the same acceptance criteria.

Pass the actual files. If repairing cheaper output repeatedly consumes the saving, change the allocation. Model names and price rankings change; compare outcomes on your own tasks.

Spotify Portal reports around ninety percent average bulk-read token savings in its testing. It routes large reads and predictable generation to a cheaper worker, keeping that material out of the expensive agent's context.

That is not ninety percent off all development cost. It does not validate the full plan, implement, review workflow here. The author describes a subtle bug the worker missed and extra latency. It is an example of selective delegation with limits. Appendix B has a dated cost-performance comparison of specific configurations for questions.

## 21. Your next feature — 20:00–21:30

These are separate actions, not one giant prompt. Add Ponytail if you want its defaults. Enable Planning Mode. Explain the outcome, answer important questions, and agree on checks. Review the plan, then implement and verify. Save a handover for the continuation.

For a clear small change, keep the process small. For an uncertain feature, spend more time resolving decisions. The agent can help write the specification and checks; you bring the intended product outcome.

This supports both a prototype that communicates an idea to developers and a personal tool you use every week. Their definitions of done differ. The common habit is to make required behaviour and evidence explicit.

## 22. Takeaways and reading — 21:30–23:00

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

Browser Print → Save as PDF also works. Container sandbox flags vary. Print CSS includes 22 main frames and excludes both appendices.
