# Сохранённые diffs по шагам

Для каждой проверенной continuous submission сохраняются **два текстовых patch-файла**. Актуальный список и SHA находятся в [manifest.json](manifest.json). Для каждого шага есть:

- `*.incremental.patch` — изменение относительно входного commit этого шага.
- `*.cumulative.patch` — изменение относительно исходного commit всей траектории.

[manifest.json](manifest.json) содержит trial/trajectory/step, starting и ending commits, ending tree, snapshot SHA, SHA-256 каждого patch, исходный executor session ID и путь/SHA локального Git bundle. Предыдущие trials, failures и raw session traces сохранены в локальном ignored `results/`; credentials не экспортируются.

Каждый patch уже применён к временному Git index правильного base commit. Полученный tree SHA совпал с immutable submitted tree. Для каждого экспортированного patch проверено точное воспроизведение submitted tree. Binary diffs и file modes сохранены через Git `--binary --full-index`.

Это точные **полные repository diffs**, включая benchmark test masking и тестовые изменения. Они не совпадают с production-only LOC на графиках: production LOC отдельно фильтрует тесты. Patch-файлы не следует применять к пользовательскому checkout вслепую; для просмотра или восстановления используйте отдельный scratch repository с указанными commits.

Пример восстановления исходников второго шага завершённого baseline. Команды создают новый каталог; они не выполнялись автоматически и не запускают модель:

```bash
git clone results/trials/phase5_baseline_r01_s02/repository.bundle /tmp/inspect-baseline-step2
git -C /tmp/inspect-baseline-step2 checkout --detach <ending_commit из manifest.json>
```

Для восстановления только через cumulative patch начните с `starting_commit`, указанного в manifest, затем выполните `git apply --check` и `git apply` нужного patch в том же scratch checkout. Восстановленный tree уже проверен генератором.

Патч восстанавливает исходники, **не контекст модели**. Для продолжения именно прежнего Codex thread нужны сохранённые session traces, валидная сессия и соответствующий runner. Checkpoint третьей правки Serena, включая 10 memories, проверен отдельно: [доказательство сохранности](../serena_checkpoint_retention.json). Текущий thread уже видел четвёртую правку; точный restart с третьей требует отдельной сессии с восстановленным source/memory checkpoint. Новые запуски Serena не запланированы.

Чтобы повторить экспорт из существующих локальных immutable artifacts:

```bash
PYTHONPATH=.:vendor/SWE-Milestone .venv/bin/python reports/plots/export_patches.py
```

[Средние кривые](../plots/MEAN_CURVES.md) · [Реестр](../../EXPERIMENT_STATUS.md).
