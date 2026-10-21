# Phase 6: результаты 2×5

Запрошены baseline, Caveman, Ponytail и Serena: сначала пять правок каждого setup, затем второй независимый круг. Всего 40 шагов. [Протокол](phase6_protocol.md), [основной реестр](../EXPERIMENT_STATUS.md).

| Trial | Grader | Sonar | Production + / − | Memory до / после | MCP calls |
| --- | --- | --- | --- | --- | --- |
| phase6_serena_r01_s01 | True | True | 12 / 12 | 0 / 7 | 30 |

Первый Serena turn остановился на предположении о недоступных filesystem tools. Стандартное upstream напоминание о submission продолжило тот же thread; последующая реализация прошла исходную строгую Serena-проверку без изменения policy. Дополнительные вызовы и время входят в метрики этой задачи; это не дополнительный независимый повтор.

Для warm шагов SHA-инвентарь memory до модели должен совпадать с checkpoint предыдущего шага. MCP process может перезапускаться, но memories и executor thread остаются внутри одной траектории.
