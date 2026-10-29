# Phase 6f: исходная шестая правка SWE

Собрано 5/7 шестых шагов. Задача: max_matches searcher migration (`milestone_seed_a6e0be3_1_sub-01`). Это продолжения прежних пяти правок: первый круг baseline/Caveman/Ponytail/Serena, затем второй круг трёх первых методов. Serena выполняется только один раз по уточнению пользователя. Первые пять задач не переигрываются.

| Подход | n | Output за 6 правок | Production churn | Δ cognitive complexity |
| --- | ---: | ---: | ---: | ---: |
| baseline | 2 | 67311.5 | 578.5 | 142 |
| caveman | 1 | 92520 | 572 | 184 |
| ponytail | 1 | 66011 | 420 | 152 |
| serena | 1 | 84165 | 701 | 156 |

| Trial | Модель и сбор | Grader | Sonar |
| --- | --- | --- | --- |
| phase6f_baseline_r01_s06 | finished | Raw resolved=False | True |
| phase6f_caveman_r01_s06 | failed | Недействителен / не завершён | None |
| phase6f_caveman_r01_s06_resume01 | finished | Raw resolved=False | True |
| phase6f_ponytail_r01_s06 | finished | Raw resolved=False | True |
| phase6f_serena_r01_s06 | failed | Недействителен / не завершён | None |
| phase6f_serena_r01_s06_resume01 | finished | Raw resolved=False | True |
| phase6f_baseline_r02_s06 | failed | Недействителен / не завершён | None |
| phase6f_baseline_r02_s06_resume01 | finished | Raw resolved=False | True |

Шестая исходная SWE-задача добавляет `SearcherBuilder::max_matches`. Grader выполняется без изменений. Пятые test scores остаются недействительными; шестая оценка не переписывает прошлые результаты.

Средние считаются по независимым повторам на том же шаге. Output накапливается; churn измеряется к исходному commit. Sonar включает inline tests. Runtime/cohort provenance и history transport сохраняются; сравнение описательное. Memories Serena сохраняются в её собственной траектории. Седьмой шаг не запускается.

[График](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Протокол](phase6f_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)
