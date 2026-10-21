# Continuous pilot: текущее состояние

Ограниченный host-driven runner реализован. Завершены 6 из 8 траекторий и 12 из 16 правок: первый повтор baseline/Caveman/Ponytail/plan и второй повтор baseline/Caveman. Все 12 grader решений приняты, collection errors отсутствуют, 12 Sonar scan завершены. Внутри каждой траектории проверены один executor thread, последовательные commits, точное чтение задания и immutable snapshot. Plan использует отдельный read-only planner перед каждым шагом. [Результаты](phase5_progress.md), [основной реестр](../EXPERIMENT_STATUS.md).

Ponytail repetition 2 остановлен до вызова модели из-за quarantine preflight. `static.crates.io` разрешился в `199.232.142.137`, который допускается frozen firewall. Успешное TCP-соединение воспроизведено. Plan repetition 2 не запускался. Продолжение требует отдельного решения по исправлению и фиксации quarantine; менять условия внутри текущего frozen cohort нельзя. [Диагностика](phase5_quarantine_failure.md).

Выбранный pilot/non-official subset: `milestone_seed_5f5da48_1_sub-01`, затем `milestone_seed_5f5da48_1_sub-02`. Между ними Strong FUNC edge; внешних Strong prerequisites нет. Grader images загружены с разрешения пользователя. Serena, goal_plan, больший repository и full-chain watcher не входят в этот ограниченный пилот.

Далее сохранена первоначальная оценка фонового watcher. Она не является текущим списком недостающих работ для уже реализованного host-driven runner.

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

Итого **3–5 инженерных дней**, оценка по inspected integration points. Model runtime, quota windows и отдельное согласование дополнительных grader-image downloads в эту оценку не входят. После dry-run contracts нужен реальный baseline, затем plan и goal_plan на выбранной паре, затем выбор skill по Phase 3. Эта оценка сохранена как история планирования; текущие подтверждённые результаты host-driven пилота приведены в начале документа.
