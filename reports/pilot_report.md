# Итоговый pilot v1

Выполнены реальные isolated сравнения всех шести вариантов на одном milestone ripgrep: Phase 2 baseline/plan/goal_plan и отдельный Phase 3 baseline/ponytail/caveman/serena. Все семь measured trials и исходный smoke получили grader resolved=true. Данные описывают одну задачу, без repetitions. Continuous отдельно отложен по явному исключению handoff §9.7 и definition of done; он не реализован и не оценён.

[Живой реестр результатов и будущих этапов](../EXPERIMENT_STATUS.md) обновляется при каждом изменении состояния экспериментов.

## Наблюдения

Планирование на этом задании не изменило correctness, но увеличило output tokens и production churn. В отдельном skill cohort Ponytail и Caveman дали меньший churn; это не доказывает устойчивый выигрыш. Serena не использовала MCP в measured trial, поэтому вывод о semantic tools или памяти невозможен. Ни один результат не является leaderboard или full benchmark score.

| Cohort | Variant | Resolved | Production + / − | Churn | Total output tokens | Active time, s |
| --- | --- | --- | --- | --- | --- | --- |
| Phase 2 | baseline | true | 79 / 29 | 108 | 9125 | 339.78 |
| Phase 2 | plan | true | 83 / 28 | 111 | 14022 | 583.82 |
| Phase 2 | goal_plan | true | 93 / 24 | 117 | 20023 | 756.91 |
| Phase 3 | baseline | true | 78 / 24 | 102 | 10294 | 362.40 |
| Phase 3 | ponytail | true | 70 / 22 | 92 | 10092 | 388.71 |
| Phase 3 | caveman | true | 77 / 21 | 98 | 13205 | 408.23 |
| Phase 3 | serena | true | 82 / 20 | 102 | 9732 | 375.18 |

Все trials: F2P 2/2, P2P 1093/1093, N2P 2/2. Raw suite сохраняет 15 failures и 1 skipped; upstream scoring не менялся. Snapshot SHA, authoritative tags и 79 Rust files проверены для каждого решения. Прямой Git numstat независимо сверён со всеми raw file rows. Production footprint исключает metadata tests/generated/vendor и inline Rust tests через pinned AST filter; новые/удалённые/переименованные файлы, binary/formatting-only changes и cumulative LOC остаются в JSONL.

Baseline не получает experiment hooks, MCP, host AGENTS/config или memories. Planner read-only, получает только исходный task/source; plan и goal_plan имеют отдельные planner/executor sessions. Goal_plan после quota pause использовал тот же validated handoff без повторной prep; interruption history сохранена. Native Ponytail/Caveman source и Node hashes закреплены, hooks исполняются с UID 1000 в protected контейнере. Serena cold home/project state не переносится между trials.

Общая база и все восемь solutions имеют успешный Sonar before/after scan, exact snapshot binding и одинаковые 78 Rust rules. Raw ncloc/complexity/issues включают различающийся inline test-код, поэтому их нельзя интерпретировать как production-only quality effects. New-code issue counts остаются null; Sonar debt minutes не являются human review time. [Все Sonar metrics и ограничения](sonar_pilot.md).

## Версии и воспроизводимость

- Codex CLI 0.163.0, gpt-6.1-sol, high, ChatGPT OAuth; paid API не использовался.
- SWE-Milestone upstream 17a8f1593e172e26b36cea15e2b30fb9536c93f5, reviewed OAuth/profile patch; evaluator/scoring/quarantine исходные. Dataset v1.0.2, commit 3500478e740d42583277c2658aa7729eb36e10f4.
- Initial commit d4b620ee55bcf3b2e85d23576878161540b67948, tree ae9e34953dc822672095250a5f9a6045968f1358; milestone maintenance_fixes_1_sub-01.
- Ponytail 5.3.2/full; Caveman v4.0.1 at d262ab3882952a59312ff3537cd86d894523c5ab/canonical caveman mode; Serena 1.6.1, Python 3.13.14, Node v24.19.0, Rust/rust-analyzer/rust-src 1.88.0.
- Sonar 26.9.0.129388-community, Rust plugin 1.8.1.3395, Scanner 8.1.0.6389; immutable image digests and rule hashes recorded.

[Phase 2 frozen inputs](../experiment.yaml), [Phase 3 frozen inputs](phase3_experiment.json), [skill manifests](../profiles/runtime/manifest.json), [Sonar runtime](sonar_runtime.json), [image identities](downloaded_images.json), [Phase 2 detail](phase2_progress.md), [Phase 3 detail](phase3_progress.md), [completion evidence](completion_audit.json), [воспроизведение и сохранённые artifacts](reproduction.md). Each cohort has its own fingerprint; cross-cohort baseline pairing is forbidden. Raw logs/bundles/snapshots and JSONL/CSV are local, ignored artifacts. Re-running a trial requires a fresh directory and live quota check.

## Ограничения и следующий scope

Нет repetitions, randomization или longitudinal inference. Порядок Phase 3 заранее задан baseline/ponytail/caveman/serena. Между cohorts различается runtime; есть quota windows, goal_plan operational resume и отсутствующий rustfmt. Host-side postprocessing частично пересекался с setup следующего trial, поэтому elapsed time не доказывает speed advantage. Activation debugging расходует отдельную setup-квоту; ChatGPT limits округлены, не дают точную стоимость trial. API token prices к подписке не применяются.

Continuous: выбран Strong-linked subset milestone_seed_5f5da48_1_sub-01 и sub-02. Blocker — отсутствующий host dispatch/ack barrier между read-only prep и публикацией SRS текущему executor. Следующий slice и оценка 3–5 инженерных дней опубликованы в [continuous feasibility](continuous_feasibility.md). Независимые exec не выдаются за continuous.

Phase 6 (larger repo, repetitions/full chain) не запускалась и не разрешена автоматически. Перед расширением нужны отдельный scope, actual image download budget и новый quota/storage gate. Последний approximate snapshot: 92% primary / 74% secondary; новых model requests после cohort нет. Суммарно семь measured runs выдали 86493 output tokens, но это не forecast квоты следующего проекта. Наблюдённый active runtime isolated trials примерно 6–13 минут, включая prep у planning; larger repo этим не прогнозируется.

Свободно на момент завершения: Docker/runtime раздел 13.06 GiB, workspace 1.96 GiB. Это не бюджет нового dataset/images: перед расширением повторить measurement. Дополнительные образы/модели/пакеты не загружались после согласованных prerequisites.

Локальный Sonar доступен только на 127.0.0.1:9000 через approved relay к internal Docker network. Credentials не попадают в tracked files или Cargo/model environment.
