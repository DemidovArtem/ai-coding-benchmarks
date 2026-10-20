# Sonar pilot — реальные raw snapshot metrics

Общая база и восемь решений проанализированы Sonar 26.9/Rust 1.8.1.3395. Для каждого подтверждены graded snapshot binding, одинаковый protocol и покрытие всех 79 Rust-файлов. Все CE tasks завершились успешно.

| Snapshot | ncloc | Cognitive complexity | Maintainability issues | Remediation effort, min |
| --- | --- | --- | --- | --- |
| Common base | 31636 | 2400 | 282 | 1438 |
| baseline_smoke_001 | 31461 | 2424 | 283 | 1443 |
| phase2_baseline_001 | 31477 | 2423 | 284 | 1449 |
| phase2_plan_001 | 31812 | 2423 | 282 | 1438 |
| phase2_goal_plan_001 | 31838 | 2442 | 283 | 1444 |
| phase3_baseline_001 | 31763 | 2421 | 283 | 1443 |
| phase3_ponytail_001 | 31774 | 2412 | 283 | 1443 |
| phase3_caveman_001 | 31767 | 2425 | 284 | 1449 |
| phase3_serena_001 | 31799 | 2421 | 283 | 1443 |

Raw snapshots содержат разный inline test-код; эти дельты не являются production-only quality effects и не ранжируют workflows. Physical production LOC отдельно считает AST-filtered Git pipeline. Remediation effort — оценка Sonar, не измеренное время review.

Canonical JSONL сохраняет complexity, duplication, все доступные metrics и дельты к common base только при одинаковом starting tree/protocol/exclusions. New-code issues остаются null: независимые project keys не дают валидной PR/new-code reference state. Отсутствующие metrics не превращаются в нули.

Clippy запускается offline/locked, default-feature workspace lib/bin, с --cap-lints warn; compilation errors остаются fatal. Scanner импортирует JSON вне executor, с project-scoped token, который отзывается. Rules/profile проверяются до и после scan. Неуспешные infrastructure attempts сохранены отдельно, включая первый Phase 3 baseline scan до завершения durable bundle copy; успешный retry не заменяет историю ошибки.

[Raw/normalized metrics](sonar_pilot.json), [frozen protocol](../sonar/analysis_protocol.json), [runtime versions](sonar_runtime.json), [rerun instructions](../sonar/README.md). Raw logs/API/Clippy artifacts: ignored results/sonar/common_base и results/trials/<trial>/sonar.
