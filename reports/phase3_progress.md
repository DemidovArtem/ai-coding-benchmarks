# Phase 3 — все четыре trial завершены

Baseline и три skills прошли один unchanged SWE-Milestone grader с одинаковым original task, starting tree, model/high effort и frozen setup fingerprint. Все snapshot/Git/Sonar checks прошли.

| Variant | Resolved | Production + / − | Churn | Delta vs baseline | Output tokens | Active time, s |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | true | 78 / 24 | 102 | 0 | 10294 | 362.40 |
| ponytail | true | 70 / 22 | 92 | -10 | 10092 | 388.71 |
| caveman | true | 77 / 21 | 98 | -4 | 13205 | 408.23 |
| serena | true | 82 / 20 | 102 | 0 | 9732 | 375.18 |

У всех F2P 2/2, P2P 1093/1093, N2P 2/2. Raw suite: 1117 total, 1101 passed, 15 failed, 1 skipped; resolved=true не означает отсутствие всех raw failures.

Ponytail и Caveman имеют native-hook audit в каждом measured trial. Serena прошла реальный Codex MCP symbol smoke; measured server startup и 23-tool inventory подтверждены логом, но model выполнила 0 MCP calls, 0 onboarding и создала 0 memories. Эти данные не доказывают пользу semantic navigation или warm memory. Measured prompt не заставлял использовать MCP.

Ponytail churn меньше baseline на 10 строк, Caveman на 4, Serena совпала с baseline. Это описания одного задания без repetitions, не доказательство превосходства. Phase 2 baseline относится к другому окружению и не используется в этих paired deltas.

Serena setup потребовал explicit offline Rust paths и required=true для ожидания MCP до initial catalog. Failed/blocked smokes и их usage сохранены; setup overhead не включается в measured task tokens. Goal_plan interruption относится к отдельному Phase 2 cohort.

Sonar raw snapshots включают разные inline tests; aggregate metrics не являются production-only quality effects. В образе нет rustfmt для Rust 1.88.0; runtime не менялся посреди cohort. Host collection/Sonar частично шли во время setup следующего executor, поэтому elapsed times описательные.

[Protocol](phase3_protocol.md), [frozen config](phase3_experiment.json), [machine-readable results](phase3_progress.json), [Sonar](sonar_pilot.md), [overall pilot](pilot_report.md). Raw artifacts сохранены в ignored results/trials.
