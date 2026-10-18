# Состояние реализации v1

Статус: **не завершено**. Выполнена Phase 0 по указанию First action handoff; последующие этапы сохраняют исходный объём. Отсутствующие runtime-данные не заменяются вымышленными результатами.

| Требование | Текущее доказательство / следующий шаг |
| --- | --- |
| Phase 0: prerequisites, OAuth, ресурсы, source audit | environment_report.md, environment.json, pinned experiment.yaml, реальный CLI help, image_budget.json, quota snapshot. Git LFS отсутствует; current dataset доступен без LFS payload. |
| Версии всех компонентов | Harness/dataset/Codex и setup packages закреплены; container skills/MCP/Sonar/scanner/profile versions ещё не выбраны и остаются null. |
| Actual baseline OAuth task + grader + immutable artifacts | Не запускались. Нужны согласованные два образа, runtime storage и безопасный pinned adapter. |
| Все 6 изолированных профилей и activation assertions | Пока не реализованы. У каждого status=not_implemented, activation=false; baseline не подменяет skill variant. |
| Plan/goal_plan preparation + свежий executor | Не реализовано. Требуются одинаковые planner budgets/schema, read-only repo protection, hashed plan artifacts и раздельные session IDs. |
| Prompt/isolation/usage/non-leakage/reproducibility tests | Есть 6 focused audit tests. Pipeline tests Phase 2 ещё отсутствуют; audit tests не доказывают pipeline. |
| Git footprint против authoritative refs | Не реализовано. Использовать metadata source/test/exclusion patterns; проверить numstat/rename/binary/generated и incremental/cumulative counts на реальных refs. |
| Sonar before/after | Не запущен. Нужен immutable Rust-capable pre-26.11 Community image, scanner/rule pins, Cargo/Clippy, loopback binding, секреты вне Git и async task completion. |
| JSONL/CSV/paired summary | Измерений нет; не созданы фиктивные results. Реализация normalization/reporting предстоит после vertical smoke. |
| Continuous 2–3 linked milestones | Strong-linked пара закреплена и проверена по двум DAG CSV. Upstream prefix flag существует; trial-local exact subset и read-only planner dispatch с постоянным executor ещё не реализованы. Следующий шаг: интеграция в task dispatch после isolated A/B. |
| Без paid API/credential leak/public service/quarantine relaxation | Paid API keys отсутствуют, модельные benchmark-запросы не выполнялись; настройки/политики не менялись, сервисы не поднимались. Secrets/runtime исключены из Git. |
| Larger repo / repetitions / full benchmark | Phase 6 не разрешена автоматически. Сначала показать pilot report и прогноз квоты/диска. |

Scope реализации следующего этапа: agent adapter, его single-runner caller и focused tests; evaluator/scoring/quarantine остаются upstream. Дальнейший scope: profiles/prompts, collection/metrics/report, Sonar, continuous dispatch, соответствующие fixtures/tests/config/docs.
