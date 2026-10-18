# Phase 2 — frozen protocol

Состояние: adapter реализован, dry-run gates пройдены; matched model trials ещё не завершены. Phase 1 smoke не переиспользуется как measured baseline.

## Общие условия

Порядок: baseline, plan, goal_plan; одна repetition, одна задача `maintenance_fixes_1_sub-01`, один trial за раз. Model `gpt-6.1-sol`, effort `high`, CLI 0.163.0, executor timeout 1800 s. Dataset, image digests, scoring, tests и quarantine неизменны. Shared starting tree закреплён в experiment.yaml и проверяется до агента.

Общие planner/executor templates, profiles и execution code закреплены SHA-256 **до первой measured попытки**. Оригинальный task сохраняется отдельно; plan/goal_plan добавляют только generated JSON handoff. `experiment.json` и `comparison_conditions.json` сохраняются на старте каждого trial, поэтому поздние изменения основного config не переписывают условия результатов.

## Read-only preparation

Native Codex sandbox внутри стандартного Docker container не может создать user namespace. Host sysctl, Docker seccomp/capabilities и benchmark network policy не менялись.

Planner работает в отдельном стандартном protected container. Он получает Git clone только текущего подготовленного baseline из executor, после удаления будущих refs и masking. Clone монтируется в `/testbed` kernel read-only. Только auth и этот repository имеют host mounts; оба read-only. Planner container не получает dataset workspace, grader outputs, предыдущие попытки или executor Codex session.

Перед моделью выполняется реальная попытка записи: требуется `EROFS`, не только отсутствие permission по UID. Snapshot fingerprint, включая untracked paths и symlinks, сравнивается до/после planning. [Полный runtime probe](planner_runtime_probe.json) подтвердил pinned CLI, clean profile, protected quarantine, EROFS и неизменность repo при **0 model requests**.

Planner использует тот же upstream invocation timeout/kill contract. CLI sandbox bypass остаётся только внутри изолированного container; source mutation блокирует Docker read-only mount. Временные Codex session/log files пишутся вне repository. Planner container удаляется до executor, а его trace и output сохраняются как experiment artifacts.

## Output и handoff

Одна общая JSON schema: objective, steps, verification, risks, goal. Для plan goal обязан быть null; для goal_plan содержит acceptance criteria, constraints, non-goals, regression invariants. Common planner instruction отличается только этой goal instruction. Оба варианта имеют 180 s timeout, 12000 UTF-8 byte output cap, до 12 элементов на список и до 1000 characters на элемент.

Schema/bounds, отсутствие duplicate JSON keys и code fences проверяются локально. Невалидный output не редактируется вручную: trial останавливается до executor. Generated output сохраняется как есть, вместе с SHA-256 и input/output sizes. Семантическое соблюдение «не писать implementation» дополнительно задаётся instruction; автоматическая проверка не заявляет полного понимания содержания.

Executor получает original task + handoff и стартует с новым Codex thread в своём исходном container. Session IDs planner/executor обязаны отличаться. Между ними нет filesystem/session memory transfer, кроме validated handoff. Usage обоих фаз суммируется; cumulative counters внутри одного thread не суммируются повторно.

## Quota и сбор

Перед trial и после preparation считывается приблизительная квота. Stop threshold — 85% любого reporting window либо явный rate/spend limit. При quota/auth failure нет API key fallback и автоматического повторения модели. OS flock предотвращает concurrent model trials. Квота повторно сохраняется после trial.

Collector сохраняет failures и missing data, использует frozen per-trial experiment.json и публикует paired deltas только для полного совпадения task/repetition/starting tree/model/effort/dataset/setup fingerprint. Smoke rows не образуют measured pairs. Native usage units и CLI event counts не объявляются одинаковыми единицами.
