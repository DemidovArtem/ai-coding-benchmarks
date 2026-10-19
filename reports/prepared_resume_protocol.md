# Resume quota-interrupted preparation

`experiment.resume_prepared` continues the same logical measured planning trial only when quota stopped it after validated preparation and before any executor session. The original frozen runner, prompts, profiles, benchmark evaluator, scoring and quarantine remain unchanged.

Before any model call, the adapter verifies the original experiment SHA/setup pins, saved config, planner repository fingerprint, validated bounded handoff and SHA, retained running container/image, common starting tree, absence of Codex processes/session files and executor stdout. Upstream masking may leave uncommitted test-only edits when there are no commits to squash. Those edits are accepted only when AST-filtered production content is identical; their raw hashes become part of the resume preflight. Production changes, untracked files, staged changes, session evidence, lost containers or changed setup reject continuation.

The adapter repeats the unchanged upstream lifecycle and requires the exact same executor state after preprocessing. It compares the generated original task byte-for-byte, activates the same profile, refreshes only OAuth through the audited adapter, checks fresh quota again, and injects the unchanged handoff through the frozen executor template. No second planner is run. Planner and executor session IDs must differ; grader and snapshot capture remain upstream.

Before continuation, the old terminal metadata, quota snapshots and effective profile are preserved under `interruptions/001`. Metadata records the resume adapter SHA, implementation commit, reused preparation, prior quota outcome, active duration and wall duration including the pause. Canonical records retain interruption metadata; prep token usage is counted once. A different quota window and operational resume remain experimental confounds, not a clean timing comparison.

```bash
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.resume_prepared /tmp/ai-coding-experiment/phase2_goal_plan_001 --check-only
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.resume_prepared /tmp/ai-coding-experiment/phase2_goal_plan_001
```

Use the original runtime directory/container identity, not a renamed durable copy. The first command performs no model call. The second supports one reviewed continuation, keeps the original failure in history and rejects existing executor evidence. It must not replace a missing container, silently repeat an executor, rerun preparation or delete the failed outcome. After completion, redact and update the durable trial copy, then recollect and scan its new authoritative snapshot.
