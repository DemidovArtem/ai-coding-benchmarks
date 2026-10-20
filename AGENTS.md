# Repository workflow

Keep `EXPERIMENT_STATUS.md` as the user-facing experiment register. Update it after every trial launch, completion, failure, collection/analysis result, or change to the experiment plan. Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status` after updating the authoritative records/status files, then inspect the changed table. Preserve previous trials and failures when updating `results/results.jsonl`; do not replace the full register with one trial.

Do not invent metrics for unfinished work. Preserve missing values, distinguish activation smoke from measured task usage, and keep Phase 2/Phase 3 baseline comparisons within their frozen cohort. Update the generator/roadmap when introducing a new phase or task scope.

Mention meaningful register updates in the chat and include a link to `EXPERIMENT_STATUS.md` in the final result. Commit and push completed, verified stages to the user-approved repository; never include credentials or ignored raw artifacts.
