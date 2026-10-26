# Phase 6d: продолжение четвёртой правкой

Этап завершён: собрано 7/7 продолжений. Первые три правки не повторяются. Для baseline, Caveman и Ponytail предусмотрены оба прежних повтора; для Serena переоценивается её готовая четвёртая submission без нового inference.

| Подход | Повтор | Output четвёртой правки | Накопленный output | Production churn | Δ cognitive complexity | Sonar | Raw grader |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| serena | 1 | 21486 | 53216 | 251 | 30 | Готов | False |
| baseline | 1 | 9944 | 37100 | 249 | 34 | Готов | False |
| caveman | 1 | 20860 | 54574 | 255 | 34 | Готов | False |
| ponytail | 1 | 12956 | 37682 | 230 | 44 | Готов | False |
| baseline | 2 | 12615 | 35015 | 274 | 29 | Готов | False |
| caveman | 2 | 12845 | 46256 | 262 | 35 | Готов | False |
| ponytail | 2 | 7063 | 32292 | 213 | 36 | Готов | False |

Средние после четырёх правок:

| Подход | n | Накопленный output | Production churn | Δ cognitive complexity |
| --- | ---: | ---: | ---: | ---: |
| baseline | 2 | 36057.5 | 261.5 | 31.5 |
| caveman | 2 | 50415 | 258.5 | 34.5 |
| ponytail | 2 | 34987 | 221.5 | 40 |
| serena | 1 | 53216 | 251 | 30 |

Output Serena относится к исходному выполнению; повторная оценка не расходует модельные токены и не добавляет независимый повтор. Churn считается относительно исходного source tree, а не суммой churn шагов. Sonar включает inline tests и benchmark masking.

Четвёртый grader использует source-residue pruning для всех подходов; исходные три оценки заморожены. У всех семи submissions целевой тест global gitignore проходит, но полный набор имеет по 19 падений и 9 отсутствующих P2P identities. Наборы raw падений совпадают; причины ещё не изолированы. Помимо известного `re35` имеются проверки JSON replacement, CRLF, BOM и более поздних regression cases. Эти падения нельзя автоматически приписать накоплению ошибок модели или только проблеме grader. Raw scores сохранены.

Восстановление Phase 6c сохраняет session ID и все сообщения через native legacy rollout transport: прежняя paginated SQLite не была архивирована. Копия меняет только header хранения. Смена storage transport может влиять на cache/context cost; сравнение токенов с исходным paginated запуском Serena не изолирует эффект подхода. Новые SQLite stores архивируются с проверкой SHA перед очисткой контейнера. Serena сохраняет исходные memories; её повторная оценка не запускает новую сессию.

[Общий график](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Точные результаты](phase6d_progress.json) · [Протокол](phase6d_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)

Ponytail второго повтора завершён после quota stop в той же сессии. Исходная неудачная попытка сохранена; она не добавляет независимый повтор. Native counters четвёртого шага вычитаются из исходных counters третьего шага. Отдельная ошибка SQLite collection восстановлена без повторного inference или grader: SHA вычисляется после явного закрытия соединений. Ошибочная копия сохранена, новая проходит integrity check и совпадает по SHA в контейнере и durable artifacts. [Recovery protocol](phase6d_resume_protocol.md), [collection proof](phase6d_collection_recovery.json).

Первые 12 средних точек (четыре подхода × три правки) точно совпадают с отчётом commit `173ea51`. Добавлены семь наблюдений четвёртого шага; их средние имеют n=2/2/2/1. Пятая правка не выполнялась.

[Финальный аудит snapshots, bundles, patches и средних](phase6d_completion_audit.json).
