# Continuous pilot — следующий приоритет

Для первого v1 continuous был явно отложен по handoff §9.7. Теперь реализован отдельный ограниченный runner `experiment.continuous`: host выдаёт задачи последовательно и продолжает тот же Codex thread через resume. Реальные последовательные trials пока не запускались; runtime и результаты ещё не подтверждены. [Новый протокол](phase5_protocol.md) отделяет этот режим от первоначального предложения с фоновым watcher.

Выбранный pilot/non-official subset: `milestone_seed_5f5da48_1_sub-01`, затем `milestone_seed_5f5da48_1_sub-02`. Между ними Strong FUNC edge. Повторная проверка `dependencies.csv` и `additional_dependencies.csv` не нашла внешних входящих prerequisites. [Selection evidence](continuous_feasibility.json) фиксирует CSV hashes и рёбра. Prefix `--milestones 2` не гарантирует выбор именно этой пары; нужен trial-local selected list и проверка closure. Дополнительные grader images этой пары пока не загружены.

## Порядок первых trials

По текущему запросу пользователя Serena не входит в условия запуска. План: baseline, Caveman, Ponytail и plan + implementation, по две связанные правки и два независимых повтора каждого варианта. Каждый шаг сохраняет grader/Git/Sonar; plan получает отдельную read-only подготовку перед каждым шагом. Goal_plan и расширение repository остаются последующими этапами. Завершённые single-milestone trials не доказывают непрерывность новой сессии.

Готовы single-milestone runner, planning profiles, grader, Git/Sonar collection и реестр результатов. Для выбранной пары остаётся определить размер дополнительных grader images и согласовать их загрузку. Повторный zero-model network diagnostic прошёл с прежним quarantine; причина предыдущего reachability failure не установлена, поэтому preflight остаётся обязательным.

## Первоначальная интеграция с фоновым watcher

Ниже сохранена оценка исходного полного подхода. Ограниченный host-driven pilot обходит этот blocker: следующий SRS выдаётся только после завершения предыдущего turn, а validated handoff читается до работы executor. Полный автоматический watcher здесь не реализуется.

Upstream watcher и долго живущий executor работают независимо. `E2EOrchestrator.start_watcher` наблюдает submission tags и запускает isolated grading; `_update_task_queue_file` сразу копирует runnable SRS и публикует queue. Executor читает эти файлы из своей постоянной сессии. Между появлением milestone и публикацией его SRS нет variant-aware dispatch barrier, который гарантирует завершённую read-only prep и доставку handoff до начала работы executor.

Обёртка только вокруг первого `codex exec` этого не решает. Серия новых независимых exec также не сохраняет требуемый контекст. Захват меняющегося worktree после первого submission без привязки к immutable tag может дать planner и executor разные начальные исходники. Процессу с planner-доступом нельзя передавать results предыдущего grader.

Проверенные точки интеграции в pinned upstream:

- `harness/e2e/orchestrator.py:1156` — watcher/startup и initial queue; `:2243` — публикация queue; `:2287` — видимость SRS.
- `harness/e2e/run_e2e.py:1449` — recovery цикл executor; `:1512` — создание E2EAgentRunner, сохраняющего состояние сессии.
- `harness/e2e/prompt/v2.md` — executor читает queue и SRS через файлы, без host-side prep RPC.

[Исходник orchestrator](https://github.com/DeepCommit-ai/SWE-Milestone/blob/17a8f1593e172e26b36cea15e2b30fb9536c93f5/harness/e2e/orchestrator.py#L2243), [executor recovery](https://github.com/DeepCommit-ai/SWE-Milestone/blob/17a8f1593e172e26b36cea15e2b30fb9536c93f5/harness/e2e/run_e2e.py#L1449). Evaluator/scoring/quarantine для такой интеграции менять не требуется.

## Следующий полный slice и оценка

1. **0,5–1 день:** trial-local exact subset, DAG closure assertion и stop после двух выбранных completions; одинаковая траектория для всех variants.
2. **1,5–2,5 дня:** host dispatch gate до публикации SRS. Read-only planner получает только исходный SRS и текущий immutable source tag своей траектории. Queue публикуется атомарно после handoff validation; ack/trace связывает handoff SHA с тем, что прочитал тот же executor. Baseline проходит тот же dispatch protocol без prep. Failure/quota stop не открывает SRS преждевременно.
3. **1–1,5 дня:** per-milestone authoritative tags/snapshots, production diff и Sonar; usage boundaries из raw session counters либо честные null там, где counters не разделяются. Тесты на одинаковый session ID, prep failure, timeout, повторный tag, delivery race, hidden-feedback isolation и отсутствие memory transfer между независимыми trials.

Итого **3–5 инженерных дней**, оценка по inspected integration points. Model runtime, quota windows и отдельное согласование дополнительных grader-image downloads в эту оценку не входят. После dry-run contracts нужен реальный baseline, затем plan и goal_plan на выбранной паре, затем выбор skill по Phase 3. Пока этих запусков нет и continuous score отсутствует.
