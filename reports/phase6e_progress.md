# Phase 6e: исходная пятая правка SWE

Собрано 0/7 пятых шагов. Задача: after-context (`milestone_seed_8c6595c_1`). Это продолжения прежних четырёх правок: первый круг baseline/Caveman/Ponytail/Serena, затем второй круг трёх первых методов. Serena выполняется только один раз по уточнению пользователя. Первые четыре задачи не переигрываются.

| Подход | n | Output за 5 правок | Production churn | Δ cognitive complexity |
| --- | ---: | ---: | ---: | ---: |

| Trial | Модель и сбор | Grader | Sonar |
| --- | --- | --- | --- |

Исходный grader этой задачи ранее требовал `SearcherBuilder::max_matches`, которого нет в SRS. Такой compile failure сохраняется как несовместимость grader, а не как измеренные нулевые test scores. Raw records остаются неизменными; source/usage/Sonar учитываются отдельно. Модель не получает grader feedback или дополнительных API requirements.

Средние считаются по независимым повторам на том же шаге. Output накапливается; churn измеряется к исходному commit. Sonar включает inline tests. Runtime/cohort provenance и history transport сохраняются; сравнение описательное. Memories Serena сохраняются в её собственной траектории. Шестой шаг не запускается.

[График](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Протокол](phase6e_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)
