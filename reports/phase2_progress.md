# Phase 2 — все три варианта завершены

Baseline, plan и goal_plan прошли неизменённый grader на одной задаче. Goal_plan продолжен после quota interruption с прежним handoff; это отдельный operational confound, сохранённый в history.

| Trial | Resolved | Production + / − | Churn | Output tokens, prep + executor | Active wall time |
| --- | --- | --- | --- | --- | --- |
| phase2_baseline_001 | True | 79 / 29 | 108 | 9125 | 339.78 s |
| phase2_plan_001 | True | 83 / 28 | 111 | 14022 | 583.82 s |
| phase2_goal_plan_001 | True | 93 / 24 | 117 | 20023 | 756.91 s |

Stable F2P 2/2, P2P 1093/1093, N2P 2/2 во всех вариантах. Raw suite сохраняет 15 failures и 1 skipped. Snapshot SHA, submission tag и Rust bytes проверены; collection errors отсутствуют. Starting tree и frozen setup fingerprint одинаковы. Planner repositories не менялись; planner и executor sessions различаются.

Goal_plan: prep выполнен один раз; после quota 88% executor не стартовал. Resume сохранил этот terminal outcome в `interruptions/001`, проверил тот же container/image/tree, отсутствие executor session и test-only masking edits. Неизменённый handoff передан свежему executor. Active duration включает оба setup-прохода; full wall duration с паузой записана отдельно. Старый failure не удалён из history; prep usage не удваивается.

На этом одном task планирование не улучшило correctness; token output и code churn выросли. Это наблюдение одного trial на вариант, без repetitions и без статистического вывода. Разные quota windows, resume adapter и toolchain activity дополнительно ограничивают временные сравнения.

[Baseline](phase2_baseline.json), [plan](phase2_plan.json), [goal_plan с interruption/resume history](phase2_goal_plan.json), [Sonar pilot](sonar_pilot.md), [общий summary](summary.md). Canonical JSONL/CSV и raw artifacts сохранены в ignored `results/`. Исходный smoke исключён из measured pairs.

Skill A/B и continuous pilot остаются незавершёнными. Raw Sonar metrics включают различающийся inline test-код и не являются production-only quality effects.
