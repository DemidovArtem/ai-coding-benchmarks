# Phase 6c: three edits for baseline, Caveman and Ponytail

The user shortened the active experiment on 2026-10-22: retain the three collected Serena edits and run the other approaches through the same first three tasks. No further Serena inference is scheduled. Plan remains excluded. The previously authorized second independent round remains scheduled after every first-round workflow completes.

## Fixed scope

Run baseline, Caveman and Ponytail, three consecutive edits each, then repeat that order in independent containers and Codex sessions. This is six trajectories and eighteen model tasks. The tasks are nested alternates, unclosed classes and min_depth, exactly the first three tasks of the retained Serena trajectory. Source commits and executor context accumulate within each trajectory. No source, session or memory is shared between independent trajectories. Grader feedback remains hidden from the executor.

Use the original upstream grading policy for these first three tasks; the optional residue-pruning override is absent. The incompatible fourth and fifth tasks and the Phase 6b replacement tasks are outside this scope. Existing grader images are already local. No new image download is needed.

All three workflows use the verified offline Codex runtime described in [the runtime amendment](phase6b_offline_runtime.md): exact Codex 0.163.0 payload copied from the retained runtime, with no credentials baked into the image. The startup smoke passed without model inference. This avoids the installer URL that returned HTTP 404 before the initial Phase 6b baseline could invoke a model.

This runtime change and shortened scope receive a distinct frozen configuration and fingerprint. Old Serena results remain visible in their original cohort; they are not silently pooled into the new means. Model, reasoning effort, common source tree, native skill activation, quarantine and Sonar rules remain pinned. Results are reported by edit count; independent repeats contribute to the same within-cohort means, with n and min/max.

Quota is checked before each model turn. The user's prior percentage override remains active; actual service refusal, unavailable quota evidence, infrastructure failure or resource reserve failure stops further inference. Negative task scores remain measured outcomes. Failed attempts are retained and never silently restarted under the same ID.

## Retained Serena checkpoint

The third collected step is `phase6_serena_r01_s03_retry01`, commit `6a402155d716d43e52911dc6deddf185505c7919`. Its cumulative and incremental patches, Git bundle, verified source snapshot, ten memory files and session traces remain local. The fourth submitted edit and its grader infrastructure failure are also retained; they are not counted as a fourth completed graded edit.

Patches restore source, not model context. The retained thread has already seen edit four. A future restart from edit three must restore that source and its corresponding memory checkpoint into a separate session. Continuing the latest retained thread instead requires resolving its fourth-step grader failure. Neither recovery is launched by this scope change.

Every launch, completion, failure and analysis updates [the register](../EXPERIMENT_STATUS.md). Completed verified stages are committed and pushed; credentials and ignored raw artifacts stay local.
