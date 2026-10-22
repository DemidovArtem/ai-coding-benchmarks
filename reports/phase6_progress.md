# Phase 6: результаты 2×5

Запрошены baseline, Caveman, Ponytail и Serena: сначала пять правок каждого setup, затем второй независимый круг. Всего 40 шагов. [Протокол](phase6_protocol.md), [основной реестр](../EXPERIMENT_STATUS.md).

| Trial | Grader | Sonar | Production + / − | Memory до / после | MCP calls |
| --- | --- | --- | --- | --- | --- |
| phase6_serena_r01_s01 | True | True | 12 / 12 | 0 / 7 | 30 |
| phase6_serena_r01_s02 | True | True | 84 / 13 | 7 / 8 | 32 |

Первый Serena turn остановился на предположении о недоступных filesystem tools. Стандартное upstream напоминание о submission продолжило тот же thread; последующая реализация прошла исходную строгую Serena-проверку без изменения policy. Дополнительные вызовы и время входят в метрики этой задачи; это не дополнительный независимый повтор.

Для warm шагов SHA-инвентарь memory до модели должен совпадать с checkpoint предыдущего шага. MCP process может перезапускаться, но memories и executor thread остаются внутри одной траектории.

## Восстановление после перезагрузки хоста

22 октября обнаружен остановленный grader второго шага Serena. Модель уже завершила turn и создала immutable tag `990ba7e51d52fdcfa8a309e1fbc08fbb1f5aa32b`; SHA-256 source snapshot — `fb3cc8b18aaeecff26e0b40e57dc877c4b9722dcc154b7302ee21494368100a0`. Inference второго шага не повторяется. До остановки строгая проверка подтвердила 32 успешных MCP-вызова, 12 semantic calls и warm-memory continuity: 7 файлов перед задачей, 8 после неё.

Операционный adapter [phase6_recover.py](phase6_recover.py) повторяет только grader для сохранённого snapshot, затем продолжает шаги 3–5 в прежнем container и executor thread. Перед продолжением проверяются image, read-only mounts, profile, Serena policy, thread, submission tags, snapshot hash и memories. После рестарта повторно установлены прежние pinned network rules. Замороженные experiment modules и model policy не изменялись. Adapter SHA и исходные metadata сохранены в локальном `host_restart.json`; длительный перерыв между шагами является операционным ограничением этой траектории. Результат второго grader до его завершения не заявляется.

Grader и Sonar второго шага завершены успешно. Служебный экспорт patches остановил дальнейшее планирование из-за отсутствующего project root в Python import path. Исправлен только host-side exporter; 28 patches из 14 исторических и новых submissions проверены воспроизведением. Продолжение читает уже собранный второй шаг, без нового inference и без повторного grader.
