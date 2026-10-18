# Состояние реализации v1

Статус: **не завершено**. Phase 0–1 выполнены; actual baseline grader smoke resolved=true, immutable artifacts сохранены; последующие этапы сохраняют исходный объём. Отсутствующие runtime-данные не заменяются вымышленными результатами.

| Требование | Текущее доказательство / следующий шаг |
| --- | --- |
| Phase 0: prerequisites, OAuth, ресурсы, source audit | environment_report.md, environment.json, pinned experiment.yaml, реальный CLI help, image_budget.json, quota snapshot. Git LFS отсутствует; current dataset доступен без LFS payload. |
| Версии всех компонентов | Harness/dataset/Codex и setup packages закреплены; container skills/MCP/Sonar/scanner/profile versions ещё не выбраны и остаются null. |
| Actual baseline OAuth task + grader + immutable artifacts | Выполнено: reports/phase1_smoke.md, baseline_smoke.json, durable trial с grader JSON, snapshot, trace и Git bundle. Snapshot привязан к submission commit; resolved=true. |
| Все 6 изолированных профилей и activation assertions | Baseline container activation подтверждена. Plan/goal_plan profiles реализованы, actual model activation pending; три skill profiles ещё не реализованы; skill variant не подменяется baseline. |
| Plan/goal_plan preparation + свежий executor | Adapter, общая bounded schema/templates, kernel read-only mount, source fingerprints и session separation реализованы. Zero-model runtime probe успешен. Measured baseline выполнен: resolved=true. Plan/goal_plan не запускались: quota 89% выше frozen stop threshold 85%; повторная проверка после reset. A/B gate не завершён. |
| Prompt/isolation/usage/non-leakage/reproducibility tests | Есть focused audit/runner/redaction/quota tests и upstream adapter regression tests. Также проверены footprint/usage/report/collector. Planner contract, shared prompt/profile, mutation detection, quota/lock/session tests добавлены; real session evidence появится после measured runs. |
| Git footprint против authoritative refs | Реализовано для Rust: benchmark path filters + inline-test AST exclusion; actual commit diff и cumulative LOC. Raw numstat сверены с Git; rename/binary/generated/missing refs покрыты fixtures. Python pipeline пока вне initial ripgrep smoke. |
| Sonar before/after | Не запущен. Нужен immutable Rust-capable pre-26.11 Community image, scanner/rule pins, Cargo/Clippy, loopback binding, секреты вне Git и async task completion. |
| JSONL/CSV/paired summary | Реальные JSONL/CSV/summary для одного smoke экспортированы. Grader diagnostics и failures не отбрасываются; matched A/B результатов пока нет. |
| Continuous 2–3 linked milestones | Strong-linked пара закреплена и проверена по двум DAG CSV. Upstream prefix flag существует; trial-local exact subset и read-only planner dispatch с постоянным executor ещё не реализованы. Следующий шаг: интеграция в task dispatch после isolated A/B. |
| Без paid API/credential leak/public service/quarantine relaxation | Paid API keys отсутствуют, host OAuth model smoke выполнен без tools; container benchmark выполнен через protected quarantine без изменения grader/scoring; настройки/политики не менялись, сервисы не поднимались. Secrets/runtime исключены из Git. |
| Larger repo / repetitions / full benchmark | Phase 6 не разрешена автоматически. Сначала показать pilot report и прогноз квоты/диска. |

Следующий scope: read-only planner, bounded/frozen prompts, изоляция planner/executor sessions и matched baseline/plan/goal_plan. Далее — skill profiles/activation, Sonar, continuous dispatch и соответствующие fixtures/tests/config/docs. Agent adapter, baseline smoke, Rust footprint и первичный export уже реализованы; evaluator/scoring/quarantine остаются upstream.
