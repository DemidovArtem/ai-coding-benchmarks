# Phase 6d: продолжение четвёртой правкой

Собрано 4/7 продолжений. Первые три правки не повторяются. Для baseline, Caveman и Ponytail предусмотрены оба прежних повтора; для Serena переоценивается её готовая четвёртая submission без нового inference.

| Подход | Повтор | Output четвёртой правки | Накопленный output | Production churn | Δ cognitive complexity | Sonar | Raw grader |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| serena | 1 | 21486 | 53216 | 251 | 30 | Готов | False |
| baseline | 1 | 9944 | 37100 | 249 | 34 | Готов | False |
| caveman | 1 | 20860 | 54574 | 255 | 34 | Готов | False |
| ponytail | 1 | 12956 | 37682 | 230 | 44 | Готов | False |

Output Serena относится к исходному выполнению; повторная оценка не расходует модельные токены и не добавляет независимый повтор. Churn считается относительно исходного source tree, а не суммой churn шагов. Sonar включает inline tests и benchmark masking.

Четвёртый grader использует source-residue pruning для всех подходов; исходные три оценки заморожены. У готовых Serena и baseline целевой тест global gitignore проходит, но полный набор имеет по 19 падений и 9 отсутствующих P2P identities. Наборы raw падений совпадают; причины ещё не изолированы. Помимо известного `re35` имеются проверки JSON replacement, CRLF, BOM и более поздних regression cases. Эти падения нельзя автоматически приписать накоплению ошибок модели или только проблеме grader. Raw scores сохранены.

Восстановление Phase 6c сохраняет session ID и все сообщения через native legacy rollout transport: прежняя paginated SQLite не была архивирована. Копия меняет только header хранения. Новые SQLite stores архивируются с проверкой SHA перед очисткой контейнера. Serena сохраняет исходные memories; её повторная оценка не запускает новую сессию.

[Общий график](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Точные результаты](phase6d_progress.json) · [Протокол](phase6d_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)
