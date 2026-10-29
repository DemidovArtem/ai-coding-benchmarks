# Phase 6g: исходная седьмая правка SWE

Собрано 0/7 седьмых шагов. Задача: JSON output replacement support (`milestone_seed_292bc54_1`). Это продолжения прежних шести правок: первый круг baseline/Caveman/Ponytail/Serena, затем второй круг трёх первых методов. Serena выполняется только один раз по уточнению пользователя. Первые шесть задач не переигрываются.

| Подход | n | Output за 7 правок | Production churn | Δ cognitive complexity |
| --- | ---: | ---: | ---: | ---: |

| Trial | Модель и сбор | Grader | Sonar |
| --- | --- | --- | --- |

Седьмая исходная SWE-задача добавляет replacement-поле в JSON submatch при `--replace`. Grader выполняется без изменений. Пятые test scores остаются недействительными; седьмая оценка не переписывает прошлые результаты.

Средние считаются по независимым повторам на том же шаге. Output накапливается; churn измеряется к исходному commit. Sonar включает inline tests. Runtime/cohort provenance и history transport сохраняются; сравнение описательное. Memories Serena сохраняются в её собственной траектории. Ponytail r02 наследует отмеченное изменение reasoning-контекста шестого шага. Восьмой шаг не запускается.

[График](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Протокол](phase6g_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)
