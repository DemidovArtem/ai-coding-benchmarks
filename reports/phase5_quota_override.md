# Разрешённое продолжение при низкой квоте

Пользователь явно разрешил продолжать Phase 5 несмотря на низкую квоту. Это заменяет процентный порог 85% для оставшихся запусков этого пилота. Оригинальный frozen `phase5_experiment.json` и историческая остановка Caveman сохранены. Файл `phase5_authorized_execution.json` содержит отдельный runtime override: значение 101 отключает остановку по проценту использованной квоты, но явные `rateLimitReachedType` / `spendControlReached`, ошибки авторизации и фактический отказ сервиса по лимитам по-прежнему прекращают запуск. Переход на paid API не разрешён и не выполняется.

Model, effort, prompts, tasks, profiles, runtime, evaluator, scoring и quarantine остаются прежними. `setup_fingerprint` до и после override проверен на равенство: resources не входят в условия A/B. Изменённый scheduling/quota policy и пауза сохраняются как ограничения временного сравнения. Оставшиеся trials запускаются через прежний frozen runner с новым execution config.

Ponytail repetition 1 запущен первым, пока готовится recovery Caveman. Затем восстанавливается withheld второй шаг Caveman через `experiment.continuous_resume`, после него идут plan и вторые повторы. Это явное отклонение от исходного порядка запуска, не случайная рандомизация.

## Recovery Caveman

Исходный `phase5_caveman_r01_s02` остаётся terminal quota failure. Новая попытка `phase5_caveman_r01_s02_resume01` продолжает тот же Codex thread, retained container и исходный commit первой правки. Recovery допускает только остановку до публикации задания/вызова executor; проверяет отсутствие активного executor, неизменность native profile, прежний submission, чистый worktree и ожидаемый thread. Он не повторяет начальное маскирование тестов и не начинает новую сессию. После старта сохранённого контейнера восстанавливаются те же pinned quarantine rules, поскольку network namespace после stop/start создаётся заново.

Проверяются чтение полного задания перед работой, сохранение thread, происхождение нового submission от предыдущего и новая native-hook activation на resume. Метрики нового шага вычитают cumulative usage предыдущего успешного шага. Старый quota failure не заменяется новой строкой. Adapter SHA записывается в metadata recovery; исходный runner остаётся неизменным. Recovery для уже начатого или частично выполненного второго шага этот adapter не поддерживает.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.continuous trial --config reports/phase5_authorized_execution.json --variant ponytail --repetition 1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.continuous_resume results/trials/phase5_caveman_r01_s02 --output /tmp/ai-coding-experiment/phase5_caveman_r01_s02_resume01
```

OS lock сохраняет один executor trial одновременно. Следующая команда выполняется только после terminal state предыдущей. Sonar и collection используют сохранённые immutable snapshots и не дают обратную связь модели.

## Продолжение 21 октября

После рестарта host временные файлы в `/tmp` исчезли. Новые запуски используют `phase5_resilient_execution.json` с ignored runtime в `results/runtime/phase5`; условия A/B и setup fingerprint неизменны. Конфиг Codex в retained container проверяется семантически: допустимо только добавление `projects./testbed.trust_level=trusted`, которое записывает CLI; прочие изменения и изменение native hooks отвергаются. Первая recovery preflight остановка сохранена как setup failure; следующая остановка из-за timeout quota API сохранена отдельным trial record без model invocation.

Ponytail получает свежую двухшаговую попытку `phase5_ponytail_r01_retry01`, исходная частично выполненная сессия остаётся сохранённой. Plan получает `phase5_plan_r01_retry01`, так как исходный host runtime утрачен, а retained executor не содержит ни сессии, ни выданного задания. Все прерванные попытки остаются в JSONL и истории плана. Это infrastructure/quota retries, а не дополнительные независимые успешные repetitions.
