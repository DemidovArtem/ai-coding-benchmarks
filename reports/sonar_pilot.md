# Sonar pilot — реальные raw snapshot metrics

Общий исходный baseline и три существующих solution snapshots обработаны закреплённым Sonar 26.9/Rust 1.8.1.3395. Для каждого подтверждены snapshot binding и покрытие всех 79 Rust-файлов; rules/profile проверены до и после анализа. Goal_plan не имеет solution snapshot: executor ещё не запускался.

| Snapshot | ncloc | Cognitive complexity | Maintainability issues | Remediation effort, min |
| --- | --- | --- | --- | --- |
| Common base | 31636 | 2400 | 282 | 1438 |
| baseline_smoke_001 | 31461 | 2424 | 283 | 1443 |
| phase2_baseline_001 | 31477 | 2423 | 284 | 1449 |
| phase2_plan_001 | 31812 | 2423 | 282 | 1438 |

**Не ранжировать workflow по этой таблице:** snapshots содержат различающийся inline test-код. Это raw source measurements, а не production-only quality effect. Production physical LOC отдельно считает AST-filtered Git pipeline. Remediation effort — оценка Sonar, не измеренное время review.

Clippy запускается offline/locked, default-feature workspace lib/bin, с `--cap-lints warn`: lint diagnostics сохраняются, compilation errors не подавляются. Scanner импортирует JSON в отдельном процессе с project-scoped token; Cargo никогда не получает credentials. Tokens отзываются.

Canonical results содержат aggregate deltas к common base только при одинаковых starting tree/protocol/exclusions. `new_maintainability_issues=null`: независимые project keys не создают достоверной new-code reference state. Missing metrics остаются null. Failed infrastructure attempts сохранены под `/tmp/ai-coding-sonar/`, не записаны как нулевые scores.

[Machine-readable results](sonar_pilot.json), [frozen rules/protocol](../sonar/analysis_protocol.json), [setup and rerun instructions](../sonar/README.md). Raw scanner/Clippy/API artifacts сохранены в ignored `results/sonar/common_base` и `results/trials/<trial>/sonar`.
