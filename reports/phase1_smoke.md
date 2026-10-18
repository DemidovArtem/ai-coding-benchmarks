# Phase 1 — baseline OAuth/grader smoke

**Gate выполнен. Полный эксперимент v1 ещё не завершён.** Это инфраструктурный smoke, а не измеренное сравнение вариантов. Планировщик не использовался.

## Реальный результат

- Trial: `baseline_smoke_001`, ripgrep, `maintenance_fixes_1_sub-01`.
- Model: `gpt-6.1-sol`, effort `high`, CLI 0.163.0, ChatGPT OAuth; API keys не использовались.
- Upstream `resolved = true`: F2P **2/2**, P2P **1093/1093**, N2P **2/2**; stable P2P regressions — **0**.
- Raw suite: **1117** tests, **1101 passed**, **15 failed**, **1 skipped**, **0 errors**. Upstream использует stable classification для primary gate. Raw failures сохранены, не заменены утверждением «все тесты прошли».
- Полный runtime: **315.42 s**; executor wall clock из native stats — **168.749 s**. Отдельное evaluation time пока `null`.

## Связь артефактов

- Starting commit: `d4b620ee55bcf3b2e85d23576878161540b67948`.
- Starting tree: `ae9e34953dc822672095250a5f9a6045968f1358`.
- Submission commit: `f838fd6e05edd5e4832760a68b02c6c9c492f214`; authoritative tag `agent-impl-maintenance_fixes_1_sub-01`.
- Snapshot SHA-256: `184930e84c07ff9888bf120ec6cabf260fb62a5e6722392a9a40ca8ec1c7a34b`.
- Все **79 Rust-файлов** в snapshot сверены byte-for-byte с submission commit. Capture integrity подтверждена, потерянных uncommitted source paths нет.
- [Постоянная копия trial](../results/trials/baseline_smoke_001/), [grader JSON](../results/trials/baseline_smoke_001/evaluation/evaluation_result.json), [Git bundle](../results/trials/baseline_smoke_001/repository.bundle), [activation proof](../results/trials/baseline_smoke_001/effective_profile.json).

Raw artifacts исключены из Git, но сохранены в workspace; они больше не зависят только от `/tmp`. Git хранит компактный [машинный результат](baseline_smoke.json), версии, hashes и инструкции.

## Footprint

Production rules: `.rs` внутри frozen benchmark source paths; test directories, generated/vendor paths и inline Rust tests исключены. Inline tests распознаёт тот же pinned AST helper, который использует harness; evaluator не изменялся. LOC — физические строки, включая comments/blank lines, не Sonar ncloc. Cargo manifests учитываются в raw diff, но не в production Rust LOC.

- Добавлено **74**, удалено **24**, net **50**, churn **98**.
- Изменено **5** production files; новых, удалённых, переименованных — **0**.
- Cumulative production LOC после test-region exclusion: **33739**.
- Binary changes и formatting-only files не обнаружены.

[Независимая сверка Git](footprint_validation.json) подтверждает raw numstat каждого actual changed file. Fixture tests дополнительно проверяют rename, binary, generated files, inline tests, missing refs и NUL-delimited filenames.

## Usage и ограничения

CLI cumulative counters: input **1011952**, cached input **952960**, output **9196**, reasoning output **1508**. Поля сохранены как сообщает CLI; output/reasoning не складываются автоматически. Planner usage — 0, поскольку planner не запускался.

CLI trace содержит **32 completed command items**, один thread и один completed CLI turn. Upstream native parser сообщает **21 tool calls** и **22 turns**; эти наблюдения сохранены отдельно, без объявления разных единиц равными. API-price estimates upstream не используются как стоимость подписки.

Квота до/после: примерно **47% / 60%** пятичасового окна и **35% / 37%** недельного. В интервал входит также работа этой беседы и возможных других клиентов; это не точная per-task quota cost.

Baseline activation проверена внутри контейнера: CLI 0.163.0, без experiment skills/MCP/memories, без host config mount, auth read-only, server-side connected tools/web отключены. Quarantine OUTPUT DROP, blocked registries/GitHub и отсутствие sudo privileges проверены upstream. Sandbox bypass действует только внутри isolated benchmark container, как в upstream.

## Следующие обязательные gates

1. Freeze planner prompts; реализовать read-only preparation и отдельный executor для matched baseline/plan/goal_plan с полным usage accounting.
2. Изолировать и проверить activation Ponytail/Caveman/Serena; не запускать неактивный variant как baseline.
3. SonarQube до/после: ещё не запускался; нужен отдельный pinned Rust-capable image/scanner setup и Clippy. Текущая image approval покрывает только два benchmark-образа.
4. Continuous strong-linked pilot: trial-local subset и per-milestone planning dispatch с сохранением executor session ещё не реализованы.

Один успешный smoke не доказывает преимущество workflow/skill и не заменяет Phase 2–5.
