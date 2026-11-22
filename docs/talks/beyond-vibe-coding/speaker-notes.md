# Beyond Vibe Coding: AI Prototypes That Last

**Artem Demidov · ProductTank Lausanne · English · 23-minute talk + 7-minute Q&A**

## Run the presentation

Open `index.html` directly in a browser. It needs no server, installation or network. External source links need a connection. Use `deck.pdf` as the ten-slide fallback.

- Right / Space / Page Down: next main slide; Left / Page Up: previous.
- Home / End: first / last main slide. The main route stops on slide 10.
- F: fullscreen. A / B: appendix slides. Escape: return to the last main slide.
- ?: help. P: print the ten main slides. Appendices are excluded from printing.
- Direct links such as `index.html#slide-5` and `index.html#appendix-b` also work.

The script below is a rehearsal draft, not a measured recording of Artem's speaking speed. Bracketed cues are not spoken. Rehearse aloud and keep the talk within 22–23 minutes. The last slide remains visible for seven minutes of questions. If short on time, shorten slide 7 before cutting the acceptance criteria or benchmark caveats.

The work examples and dialogue are synthetic. They illustrate lessons from Artem's experience without using employer material. Sources and metric definitions are in `sources.md`.

## 1. My prototype got harder to change — 0:00–3:00

[Start with the personal story. Pause before explaining the diagram.]

About a year ago, I started using AI-assisted coding. At first, it felt unusually easy to turn an idea into something that worked. I described a feature, the agent wrote it, and often one iteration was enough to get a useful result.

As the application grew, that experience changed. The same idea could be described in three to five places. A new feature became more likely to need three to five attempts, more quota, more checking, and more help from me.

I was still getting code. I was spending more effort making the next change work.

Here is an illustration, using an expenses dashboard. Imagine that the table, the total, the export, the report and an alert each contain their own version of the rule for selecting a month. Now change that rule. The agent has five opportunities to update it differently, or to miss one copy.

This dashboard is invented. I cannot show material from my previous work, so the diagrams and dialogues today are illustrative. The experience of growing duplication and extra iterations is mine.

I also noticed a difference in the size of changes: some earlier features added about three thousand lines, while a later change might add three hundred and remove two hundred. Those were different features. That is a personal observation, not a controlled comparison or a percentage saving.

Today I want to share habits that make the next change easier. We will define the outcome, keep changes small, and make the workflow repeatable. I will separate my experience, my small benchmark, and recommendations from the people building these agents.

These habits apply both to a prototype you show a development team and to a small tool you intend to keep using yourself.

## 2. Acceptance criteria — 3:00–6:00

[Point to the three conditions, then the example table.]

Start with a request that sounds reasonable: build me an expenses dashboard. It leaves many decisions open. What should the filter affect? What happens when a source is unavailable? How will we know that the total is correct?

Before asking for code, turn the intended result into observations. In this example, selecting January changes both the table and the total. Two example expenses, one hundred and two hundred, produce a total of three hundred. A failed source produces a clear message and preserves saved data.

You can describe these checks without knowing how the code works. They are product decisions. The agent can help translate them into tests and browser checks.

A screenshot can show that the filter and message are visible. A check with known input values can show that the calculation is correct. Ask for both kinds of evidence when both matter. A convincing screen alone does not establish that the numbers are right.

For a throwaway communication prototype, your acceptance criteria might focus on a particular interaction and the explanation it gives your development team. You may deliberately use synthetic data and leave other journeys out.

For a personal tool you will run every week, ask more questions. Can it run twice without duplicating data? What happens during a failed import? Does it preserve the last good state? Those conditions belong in the definition of done.

My suggested starting point is a short list, not a giant specification. Pick the behaviour you care about, include a failure case, and give the agent a way to check the result. Anthropic and OpenAI both provide practical guidance on giving coding agents clear outcomes and verification criteria.

Once we have these conditions, the next question is whether we have made the important decisions yet.

## 3. Planning mode — 6:00–9:00

[Read only the first question and answer; let the audience scan the rest.]

Planning mode is useful when I have an idea but have not yet resolved what it means. Instead of asking the agent to start implementing, ask it to interview you until it can describe the expected result and how to verify it.

Here is an illustrative exchange. The agent asks which month an expense without a date belongs to. We decide to flag it for review, rather than guess. The agent asks what an unsuccessful import should do. We decide to keep saved data and explain the failure.

These are small questions with visible consequences. If we leave them unanswered, implementation still requires a choice. We just discover that choice later, when the product behaves differently from what we expected.

Ask the agent to save the agreement. A specification records the outcome and acceptance criteria. A plan records the implementation steps, the checks, and the boundaries of the change. The filenames on the slide are examples; the important part is that the next session can read them.

For a simple, clear change, a long planning process may add little. For an ambiguous feature, it gives us a place to think before changing the application. Both Anthropic's practical guidance and OpenAI's Codex guide discuss asking the agent to clarify the task first.

Do not promise yourself that planning automatically saves tokens. In my earlier, very small planning pilot, the planning conditions used more output tokens. It did not establish an efficiency advantage. I recommend planning here to improve agreement about the work.

Once the plan is clear, we can decide what model should implement it. I will return to that briefly. First, we need to control how much new machinery the agent introduces while doing the work.

## 4. Ponytail and small changes — 9:00–12:00

[Connect the shared rule to the five copies in the opening.]

My next suggestion is to ask for the smallest complete change that satisfies the acceptance criteria. The word complete matters. Necessary validation, error handling and tests remain part of the work.

Return to the dashboard. Before creating another way to select a month, ask the agent to find what already does that job. If an existing function can serve the new feature, reusing it may avoid another copy of the same business rule.

This diagram shows the intended relationship: one place owns the month-selection rule, and several parts of the application use it. It is a teaching example, not a universal instruction to put every similar-looking piece of code into one function.

Ponytail is a third-party skill I have experimented with. It gives the agent a set of instructions around reuse, small changes and avoiding unnecessary complexity. It is one convenient way to make these expectations explicit.

You can also start with plain language: reuse what exists; make the smallest change that meets the requirements; do not add features or abstractions for hypothetical needs; keep the checks needed to prove it works.

Anthropic has guidance against overengineering, including unnecessary files and abstractions. That supports the principle. It does not mean Anthropic built, endorsed or benchmarked Ponytail.

There is a temptation to turn this into a competition for the smallest number of lines. Avoid that. Removing a necessary check could make the code shorter and the product worse. Our target is less unnecessary maintenance work while keeping the behaviour we need.

To see whether this configuration changed anything measurable, I built a small benchmark. Here is what it found, and what it did not establish.

## 5. Exploratory benchmark — 12:00–15:00

[Explain the left chart first. Keep the limitations visible.]

This comparison keeps the model fixed and changes the agent configuration. It uses one repository, ripgrep, with six sequential code changes. Baseline and Ponytail each have two independent trajectories. The six changes within a trajectory depend on the previous changes, so they are not six independent repetitions.

The left chart shows net production-code growth at the end: lines added minus lines deleted, comparing the initial and final source states. The baseline mean is four hundred and thirteen point five lines. Ponytail is three hundred and one. That is about twenty-seven percent lower mean growth in this sample.

The right chart shows cumulative output tokens over those six changes. The means are about sixty-seven thousand three hundred for baseline and sixty-two thousand eight hundred for Ponytail. The descriptive difference is six point eight percent.

Output tokens are only one part of usage. These numbers are not dollar savings, subscription prices or a direct measurement of human time.

The quality result is less encouraging. The sixth-step evaluations remained unresolved: all seven trajectories in that wider experiment passed seven of eight new tests. Static quality measurements did not identify a consistent winner. Earlier grading and protocol issues also limit the interpretation.

So I can say that Ponytail produced less net growth and fewer output tokens in this small comparison. I cannot say that it made the code universally better, or that it will save you the same percentage.

The appendix and public repository contain the ranges and limitations, including a disclosed context amendment in one Ponytail continuation. There are too few repetitions to claim statistical significance.

For a product manager, the useful lesson is to compare configuration changes against behaviour checks and a small set of measurements. A preference for smaller changes is a hypothesis we can inspect, rather than a reason to stop checking quality.

## 6. Handover and goals — 15:00–17:30

[Walk through “remaining” and “next”; do not read every line.]

A long conversation is a difficult place to find the current state of a project. Context is finite, and agents may compact or summarise earlier work. Save the information needed to continue outside the conversation.

For this dashboard, a handover can fit on a few lines. It records the requirements, the decision about undated rows, the checks that passed, the remaining browser check, and the next action. The statuses here are illustrative, not results from an application we tested.

Ask the next session to read that file and inspect the actual project before continuing. A file can become stale too. It should guide verification rather than replace it.

Anthropic's long-running-agent article describes failures such as leaving incomplete work without useful documentation and declaring completion too early. The article uses progress artifacts and incremental work to help bridge sessions.

A plan and a goal serve different purposes. The plan describes what to do. The goal describes the condition that counts as done. Current Codex and Claude Code documentation both describe goal features, although their implementations differ.

A goal keeps an objective in view within its thread or session. It is not a complete memory of every decision, and it does not independently guarantee correct work. Keep the details in files and require evidence for the completion claim.

There is no need to make manual compaction a ritual before every task. For a separate piece of work, a focused new session with an explicit handover can be easier to manage.

## 7. Model choice — 17:30–19:30

[Distinguish the suggested workflow from the Spotify result.]

When budget is a constraint, consider which parts of the task need the strongest model. A workflow to try is a stronger model for clarification, a cheaper model for well-specified implementation, and stronger review when failures or risky changes justify it.

Pass the actual saved plan and acceptance criteria. The cheaper implementation still has to pass the same checks. If fixing its output repeatedly consumes the saving, change the allocation.

The Spotify Portal article is a useful but narrower example. It reports around ninety percent average bulk-read token savings in its testing. A cheaper worker reads large files or generates predictable code, keeping that material out of the more expensive agent's context.

That is not ninety percent off the total development bill. It is also not a test of the full plan, implement and review workflow on this slide. The author reports a subtle bug the worker missed, which is a useful reason to keep difficult reasoning and review in the picture.

Model names and prices change. Compare the cost and outcome on your own tasks. I have a configuration-specific benchmark comparison in the appendix if that is useful during questions.

## 8. Reusable instructions — 19:30–21:00

If you repeat the same rule in several conversations, ask the agent to put it into the project's instruction file. In Claude Code that is commonly CLAUDE.md; in Codex, AGENTS.md. These files provide guidance loaded into context automatically.

Our example rule is to preserve existing import data if a source fails. Keep that rule short and specific, along with how to check it.

If you repeat a procedure, a skill is a place to package it. Here the procedure is to validate an import with a fixture, simulate a failure, and check the preserved data. Skills are loaded or invoked for relevant work.

Instructions are not enforcement. A written rule does not prove the application follows it. Keep the test or inspection that establishes the behaviour.

You do not need to learn every extension mechanism today. Start with one recurring problem. Save the useful instruction, and check whether it improves the next attempt.

## 9. Your next feature — 21:00–22:00

[Pause so the audience can photograph the prompt.]

Here is a prompt you can adapt for your next feature. Ask for an interview first, save the agreement, reuse existing functionality, and request the smallest complete change. Then require checks, honest results, and a handover.

The important part is to replace the generic acceptance criteria with conditions for your product. Ask the agent to help if you cannot formulate them yet.

This works as a starting process for a prototype you hand to developers and for a tool you maintain yourself. The checks should reflect which kind of product you are building.

## 10. Takeaways and reading — 22:00–23:00

[Leave this slide visible for questions.]

For your next change, define what done looks like. Ask for a small, complete implementation. Keep the checks and a handover so you can continue with evidence.

Start with Anthropic's practical best-practice guide. The extension overview explains instruction files, skills, hooks and the other components when you want to go deeper. The linked materials include OpenAI guidance, the Spotify case, and my experiment's data and limitations.

Thank you. I would like to hear which part of maintaining your prototypes is becoming difficult.

## Q&A reference — outside the 23-minute script

**Does less code mean better code?** No. Net growth measures size change. Correctness needs behaviour checks. Static quality metrics are useful evidence with their own limits.

**Is the Ponytail result statistically significant?** No claim of significance. Two trajectories per method on one task chain provide descriptive observations. Sequential steps are dependent. Wider replication is needed.

**What exactly is production LOC?** Physical lines under the study's pinned production-source filtering, including comments and blank lines. Upstream metadata excludes tests, generated files and vendor code; a pinned Rust AST filter removes inline tests. Net change is additions minus deletions between the initial and final filtered trees. Production churn is additions plus deletions between those trees, not the sum of every intermediate edit. Cumulative output tokens sum across steps in each trajectory before averaging repetitions. Sonar uses a different scope, including inline tests and benchmark masking.

**Did planning save tokens in your experiment?** No. The separate earlier planning pilot had one observation per condition and higher output for planning. It cannot establish a general planning effect and must not be pooled with this cohort.

**What is the context amendment?** In the second Ponytail trajectory at step 6, one API-rejected encrypted reasoning record was removed from a checkpoint copy with user authorization. The mean includes this trajectory. Source, prior submissions and the rest of the history were preserved. See the public results for recovery and runtime limitations.

**What did Sonar show?** Baseline mean cognitive-complexity delta was 142, Ponytail 150.5. These are descriptive snapshot deltas and do not establish a quality advantage. Other methods and full charts are in the public results.

**Is Codex cheaper than Claude Code?** Appendix B compares specific agent/model/settings combinations on Artificial Analysis, not subscriptions or all tasks. Checked 22 November 2026: Claude Code + Sonnet 5.5, Max with Default Fallback: index 56.33, mean API cost $11.40/task. Codex + GPT-6.2 Sol, Xhigh: index 49.79, $0.90/task. Quality and cost differ. The index is not a percentage of code correctness.

**Can I develop indefinitely without reading code?** This talk does not establish that. Requirements, tests and review provide evidence and expose failures; they do not remove every need for engineering judgement. Ask for suitable technical review when the consequences of a failure warrant it.

## Organizer handoff and rehearsal checklist

- Title: **Beyond Vibe Coding: AI Prototypes That Last**.
- Speaker: **Artem Demidov**.
- Proposed bio, **56 words**, based only on information supplied for this talk:

> Artem Demidov experiments with AI-assisted coding and studies how agent configurations affect code growth, quality metrics, and token use. His open-source benchmark compares workflows across successive changes to an existing repository. In this talk, he shares lessons from practical use, preliminary experiment results, and documented techniques for building prototypes that remain easier to change over time.

- Photo: organizer guidelines allow the LinkedIn photo by default. Confirm the intended profile/photo with Artem; no image has been selected or sent.
- Event date and meetup link: not provided. Send draft slides or outline at least **72 hours before the event**; register once the link is available.
- Confirm whether Artem's laptop will be used and whether a clicker is available. Bring the HTML and PDF. Arrive **30–45 minutes early**.
- Human rehearsal still required: record the actual duration twice, aim for **22–23 minutes**, and reserve **7 minutes for Q&A**. The software timing labels are a schedule, not proof of delivery time.
- Venue projector, clicker, actual fullscreen behaviour on the presentation laptop, and the author's delivery speed require a real-world check.
- No organizer message, event registration or public post has been sent by the agent.

## Maintainer notes

Run `python3 verify.py` from this directory to check the slide count, timing schedule, script/bio lengths and benchmark values against the pinned public Git input. It needs only Python's standard library and Git. This is a public-analysis/structure check, not a new benchmark run or a substitute for browser, PDF and human rehearsal checks.

Edit HTML text directly. Chart and appendix-B values live in the `evidence-data` JSON block in `index.html`; the bar charts and model rows are rendered from it. Keep the main-slide table, appendix A, notes and sources consistent when changing data. Preserve the frozen experiment's scope and date; new experiments belong in their own comparison.

To regenerate the PDF using an installed Chrome, run from this directory:

```bash
google-chrome --headless --print-to-pdf="$PWD/deck.pdf" --no-pdf-header-footer "file://$PWD/index.html"
```

The sandbox flags required in some automated containers are environment-specific. Normal browser Print → Save as PDF also works. The print stylesheet includes only the ten main slides at 16:9. Recheck all ten PDF pages after changes.
