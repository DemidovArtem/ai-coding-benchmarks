# Phase 2 — частичный результат

**Baseline завершён; matched A/B ещё не завершено.** Нельзя делать выводы о plan/goal_plan до выполнения обоих вариантов.

- Trial `phase2_baseline_001`: `resolved=true`, stable F2P 2/2, P2P 1093/1093, N2P 2/2. Raw suite сохраняет 15 failures и 1 skipped; scoring не изменялся.
- Production footprint: **+79 / −29**, net **50**, churn **108**, 5 changed source files. Inline Rust tests исключены.
- Starting tree совпал с frozen baseline: `ae9e34953dc822672095250a5f9a6045968f1358`.
- Setup fingerprint: `eb3b65310f12605fc6a5ee8641dc99bcf89a8b86094503d969b3ac122542a7dd`.
- Snapshot, submission ref и все 79 Rust-файлов сверены; collection errors отсутствуют.
- Duration: 339.78 s; evaluation отдельно: 65.36 s.
- [Машинный результат](phase2_baseline.json), [постоянные artifacts](../results/trials/phase2_baseline_001/), [общий summary](summary.md). Исходный smoke помечен отдельно и не используется для measured pairs.

## Quota gate

После trial API сообщил **89%** пятичасового окна, выше заранее закреплённого stop threshold **85%**. Поэтому `phase2_plan_001` и `phase2_goal_plan_001` **не запускались**. Нет retries, API key fallback или изменения threshold.

API reset timestamp: **2026-10-19T02:24:01+02:00**, Europe/Zurich. Это прогноз окна, а не разрешение запускать модель без проверки. Следующий шаг — получить свежий quota snapshot, затем выполнить plan и goal_plan по одному, сохраняя frozen prompts/code/pins.

Static environment audit проверяет source pins и setup, но не заменяет runtime quota gate. Полный v1 остаётся незавершённым; skill A/B, Sonar и continuous pilot ещё впереди.
