# Serena: работоспособность подтверждена

Отдельный required-usage smoke `serena_required_smoke_003` успешно завершён на нейтральном Rust fixture с тем же локальным runtime. Зарегистрированный MCP server реально вызван: **13 успешных MCP calls, 2 semantic calls, 6 memory files**. Проверены cold onboarding, получение непустых symbols, запись памяти до shell/source operations и неизменность исходного файла. Ни grader, ни новая benchmark trajectory не запускались.

[Подробный результат](serena_required_smoke_003.json), [текущий статус](serena_required_progress.json), [обязательная инструкция](../profiles/serena_required/AGENTS.md).

Первая попытка этого продолжения, `serena_required_smoke_002`, уже выполнила semantic calls и записала memories, но нарушила строгий порядок startup: shell использовался во время onboarding до ориентационной памяти. Её failure сохранён в [отдельном отчёте](serena_required_smoke_002.json). Уточнённая инструкция явно требует Serena tools для стартовых чтений даже non-code files. Validator не ослаблялся. Повтор `003` прошёл исходную строгую проверку.

Проверка использует усиленную immutable registry policy Phase 5b. Это activation/workflow smoke, а не measured comparison. Исторический Phase 3 Serena trial с нулём natural MCP calls остаётся неизменным; его метрики не подменяются smoke. Пользователь ещё не разрешал новый benchmark после остановки очереди.

## Использование при следующей отмашке

Перед отдельным Serena trial требуется подключить профиль `profiles/serena/config.toml` и политику `profiles/serena_required/AGENTS.md`, а затем проверять реальные calls через `verify_required_usage`. Один server startup недостаточен. Подготовленный smoke runner уже принимает явный `--config`, сохраняя frozen trial-bound quarantine. Текущий baseline/Caveman/Ponytail runner сам Serena не регистрирует; добавление measured Serena variant потребует отдельного ограниченного изменения и нового cohort.
