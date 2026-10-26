# Phase 6d: recovery after the final quota stop

The user confirmed that limits reset and authorized continued experiments on 2026-10-26. Six fourth-step assessments were already collected. Ponytail repetition two stopped with an explicit service usage-limit error after five shell calls; its source remained at the third submission commit, clean, without a fourth tag.

Recovery preserves the failed trial and native failed turn. It reuses the retained container, the same session ID, immutable three-step source and task, original frozen configuration and grading/Sonar protocols. The recovery adapter is separately hashed in run metadata; frozen Phase 6d source pins remain unchanged. It checks the native history, absence of an active executor, runtime, mounts, profile, hooks and quarantine before one new resume turn. Output is a fresh `phase6d_ponytail_r02_s04_resume01` attempt. No completed task is repeated, and no fifth task is launched.

Native cumulative counters after recovery are compared with the third-step counters, so reported fourth-step deltas include usage retained by the service across the failed attempt. Missing counters in the failed record remain missing. A recovery attempt is not an independent repetition. Source bundles, native history and SQLite backups are retained before container cleanup.

## Collection recovery

Inference and the grader completed successfully as processes. Collection then rejected a native SQLite backup hash. An offline reproduction showed that Python SQLite connection contexts do not close the connection: hashing the reused WAL-mode backup before explicit close produced the same premature hash. `experiment/session_store.py` closes both connections before hashing and rejects existing destination directories. A WAL-backed integrity/hash test covers the fix. The old copy and manifest remain preserved. `experiment/phase6d_collect_resume.py` only preserved the already submitted source/history/usage and ran Sonar; it did not invoke a model or repeat the grader. The original frozen runtime files and recovery adapter remain unchanged. See [collection evidence](phase6d_collection_recovery.json).
