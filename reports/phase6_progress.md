# Phase 6: результаты 2×5

Запрошены baseline, Caveman, Ponytail и Serena: сначала пять правок каждого setup, затем второй независимый круг. Всего 40 шагов. [Протокол](phase6_protocol.md), [основной реестр](../EXPERIMENT_STATUS.md).

| Trial | Grader | Sonar | Production + / − | Memory до / после | MCP calls |
| --- | --- | --- | --- | --- | --- |
| phase6_serena_r01_s01 | True | True | 12 / 12 | 0 / 7 | 30 |
| phase6_serena_r01_s02 | True | True | 84 / 13 | 7 / 8 | 32 |
| phase6_serena_r01_s03_retry01 | False | True | 133 / 21 | 8 / 10 | 55 |
| phase6_serena_r01_s04 | Ошибка grader | True | 214 / 37 | 10 / 11 | 65 |

Первый Serena turn остановился на предположении о недоступных filesystem tools. Стандартное upstream напоминание о submission продолжило тот же thread; последующая реализация прошла исходную строгую Serena-проверку без изменения policy. Дополнительные вызовы и время входят в метрики этой задачи; это не дополнительный независимый повтор.

Для warm шагов SHA-инвентарь memory до модели должен совпадать с checkpoint предыдущего шага. MCP process может перезапускаться, но memories и executor thread остаются внутри одной траектории.

## Восстановление после перезагрузки хоста

22 октября обнаружен остановленный grader второго шага Serena. Модель уже завершила turn и создала immutable tag `990ba7e51d52fdcfa8a309e1fbc08fbb1f5aa32b`; SHA-256 source snapshot — `fb3cc8b18aaeecff26e0b40e57dc877c4b9722dcc154b7302ee21494368100a0`. Inference второго шага не повторяется. До остановки строгая проверка подтвердила 32 успешных MCP-вызова, 12 semantic calls и warm-memory continuity: 7 файлов перед задачей, 8 после неё.

Операционный adapter [phase6_recover.py](phase6_recover.py) повторяет только grader для сохранённого snapshot, затем продолжает шаги 3–5 в прежнем container и executor thread. Перед продолжением проверяются image, read-only mounts, profile, Serena policy, thread, submission tags, snapshot hash и memories. После рестарта повторно установлены прежние pinned network rules. Замороженные experiment modules и model policy не изменялись. Adapter SHA и исходные metadata сохранены в локальном `host_restart.json`; длительный перерыв между шагами является операционным ограничением этой траектории. Результат второго grader до его завершения не заявляется.

Grader и Sonar второго шага завершены успешно. Служебный экспорт patches остановил дальнейшее планирование из-за отсутствующего project root в Python import path. Исправлен только host-side exporter; 28 patches из 14 исторических и новых submissions проверены воспроизведением. Продолжение читает уже собранный второй шаг, без нового inference и без повторного grader.

Перед executor третьего шага запрос `account/rateLimits/read` превысил 20-секундный timeout. Модель не вызывалась; failed attempt `phase6_serena_r01_s03` сохранён с отсутствующими метриками. Повторная свежая quota observation успешна (26% short / 4% weekly); подготовка продолжается как `phase6_serena_r01_s03_retry01`, с прежним submitted source и executor thread.

Третий submitted шаг имеет raw `resolved=false`: новая проверка `walk::tests::min_depth` проходит, P2P — 1092/1093, failure `glob::tests::re35`. Task-local filtered evaluation даёт `resolved=true` (P2P 1081/1081). Основной реестр по замороженному протоколу сохраняет исходный raw grader и не подменяет его filtered-результатом. Это расхождение ограничивает интерпретацию: до сравнения остальных setups нельзя приписывать его качеству одного workflow. Результаты grader не передаются executor; четвёртый шаг продолжает исходный план.

### Ограничение raw scoring: порядок веток regex

Для `glob::tests::re35` в grader второго milestone записано `toregex!(re35, "{a,b}", r"^(?:a|b)$")`, а в третьем — `toregex!(re35, "{a,b}", r"^(?:b|a)$")`. Проверка сравнивает строковое представление regex. В данном выражении обе ветки распознают одинаковое множество строк; расхождение не доказывает ухудшения matching behavior. Единственный raw P2P failure третьего шага соответствует этому различию. Значения raw и filtered сохраняются раздельно, canonical `resolved=false` не переписан. Остальные 13 failures raw suite этим наблюдением не объясняются и не переклассифицируются. [Проверенные образы, test declarations и failure excerpt](phase6_grader_compatibility.json). Никакая grader-информация не передана executor.

## Остановка четвёртого grader

`phase6_serena_r01_s04` завершил model turn и строгую Serena-проверку (65 MCP calls; memories 10 → 11), но grader не получил test reports. Оба bases, END и START, дали E0761: одновременно присутствуют `crates/printer/src/hyperlink.rs` из agent snapshot и `crates/printer/src/hyperlink/mod.rs` из grader tree. Это инфраструктурная ошибка композиции source tree; она не трактуется как установленный defect модели. Четвёртый snapshot, submission tag, thread и memory checkpoint сохранены; пятый шаг и остальные setups не запускаются.

В upstream уже предусмотрен A/B-переключатель `SWE_MILESTONE_RESIDUE_PRUNE=1`, удаляющий остаточные source files базового дерева с защитой tests/assets. Запущена отдельная zero-model проверка этого режима на неизменённом четвёртом snapshot. Исходный score и frozen cohort не переписываются; новый результат пока не заявляется. Upstream evaluator, task SRS, images и quarantine не изменены.

Zero-model replay с upstream pruning удалил два residue source файла (`hyperlink/mod.rs`, `hyperlink/aliases.rs`) и получил полноценные test reports без infrastructure error. Raw score остаётся false: P2P 1085/1104 (10 failed, 9 missing); F2P 1/1. Это отдельная grading-конфигурация, её результат не заменяет первоначальный failed grader. Sonar четвёртого snapshot завершён успешно по прежним frozen rules. [Диагностика pruning](phase6_prune_diagnostic.json).

### Пятая задача исходного набора несовместима с общей базой

Synthetic zero-model probe after-context grader с source snapshot после четвёртой правки упал при компиляции injected tests: `SearcherBuilder::max_matches` отсутствует. SRS этой задачи описывает два performance fix для line buffer/context scanning и не требует данный API. Probe использовал отдельный diagnostic clone и synthetic task tag; ни одна исходная submission/tag не изменена. Это не исполнение пятой задачи и не её model score. Исходный probe с чужим tag был корректно отклонён guard и также сохранён локально.

Для нового cohort готовится совместимый набор: nested alternates, unclosed classes, min_depth, maintenance fixes, global gitignore. Maintenance fixes уже использует согласованный локальный grader из Phase 3. Strong dependency closure для пяти задач проверен по обоим CSV. Набор и grading setting будут заморожены отдельно; исходные Phase 6 результаты не перезаписываются и не усредняются с новым cohort. До завершения zero-model preflight новые model calls не выполняются.

Подготовка Phase 6b завершена: zero-model reference controls с составленными сохранёнными решениями дали test reports для maintenance fixes и global gitignore; dry-run pruning не меняет grader source tree первых трёх snapshots. 91 harness test прошёл. Scope, источники, images и grading setting заморожены в отдельном fingerprint `c53820c8b7c305ea62470dc29a8263843c8c7b6b680c3d50364513d8eb0bfb33`. Новая очередь начинает с baseline; прежние Phase 6 executions не считаются независимыми повторами новой серии. [Preflight](phase6b_preflight.json), [протокол](phase6b_protocol.md).
