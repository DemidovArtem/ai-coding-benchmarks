# Phase 6f: исходная шестая правка SWE

Собрано 0/7 шестых шагов. Задача: max_matches searcher migration (`milestone_seed_a6e0be3_1_sub-01`). Это продолжения прежних пяти правок: первый круг baseline/Caveman/Ponytail/Serena, затем второй круг трёх первых методов. Serena выполняется только один раз по уточнению пользователя. Первые пять задач не переигрываются.

| Подход | n | Output за 6 правок | Production churn | Δ cognitive complexity |
| --- | ---: | ---: | ---: | ---: |

| Trial | Модель и сбор | Grader | Sonar |
| --- | --- | --- | --- |

Шестая исходная SWE-задача добавляет `SearcherBuilder::max_matches`. Grader выполняется без изменений. Пятые test scores остаются недействительными; шестая оценка не переписывает прошлые результаты.

Средние считаются по независимым повторам на том же шаге. Output накапливается; churn измеряется к исходному commit. Sonar включает inline tests. Runtime/cohort provenance и history transport сохраняются; сравнение описательное. Memories Serena сохраняются в её собственной траектории. Седьмой шаг не запускается.

[График](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Протокол](phase6f_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)
