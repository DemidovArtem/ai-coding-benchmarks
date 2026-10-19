# Phase 2 — частичный результат

Baseline и plan завершены. Goal_plan остановлен после подготовки до старта executor; полный A/B gate не завершён.

| Trial | Resolved | Production + / − | Churn | Outcome |
| --- | --- | --- | --- | --- |
| phase2_baseline_001 | true | 79 / 29 | 108 | Grader complete |
| phase2_plan_001 | true | 83 / 28 | 111 | Grader complete |
| phase2_goal_plan_001 | null | null / null | null | Quota gate before executor |

Оба завершённых trial имеют stable F2P 2/2, P2P 1093/1093, N2P 2/2. Raw suite сохраняет 15 failures и 1 skipped; scoring не менялся. Plan относительно baseline: churn +3. Это один task без repetitions; broad conclusions не поддерживаются. Baseline и plan выполнялись в разных quota windows.

Starting tree завершённых runs: `ae9e34953dc822672095250a5f9a6045968f1358`. Frozen setup fingerprint: `eb3b65310f12605fc6a5ee8641dc99bcf89a8b86094503d969b3ac122542a7dd`. Graded snapshot SHA, submission tag и Rust bytes проверены; collection errors отсутствуют. У plan capture diagnostics сохраняют один uncommitted lost path; footprint рассчитан по verified graded tag, а не по оставшейся рабочей копии.

Plan preparation валидна, repo не изменён; planner и executor имеют разные sessions. Goal_plan preparation также валидна, repo не изменён. После неё quota 88% превысила frozen stop threshold 85%; executor не запускался. Handoff, planner trace и prep usage сохранены. Нельзя считать этот trial успешным, удалять его из результатов или повторять prep без учёта уже понесённого расхода.

Следующий шаг: свежая проверка quota ниже 85%, затем проверяемое продолжение той же попытки с прежним handoff и pristine executor. Resume adapter ещё не реализован; старый failed outcome должен остаться в history. Нельзя просто перезапустить CLI в тот же output directory.

[Baseline record](phase2_baseline.json), [plan record](phase2_plan.json), [goal_plan interrupted record](phase2_goal_plan.json), [общий summary](summary.md). Canonical JSONL/CSV и raw artifacts находятся в ignored `results/`. Исходный Phase 1 smoke не входит в measured pairs.

Sonar service запущен по отдельному разрешению. Actual common base и все существующие solution scans подтверждены; raw before/after measures и ограничения inline tests опубликованы в [Sonar pilot](sonar_pilot.md). Skill A/B и continuous pilot также остаются незавершёнными.
