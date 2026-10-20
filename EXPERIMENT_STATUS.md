# Эксперименты: результаты и текущий статус

Обновлено: **2026-10-20 22:37:02**, Europe/Zurich. Это основной живой реестр проекта.

Источник чисел — сохранённые grader/Git/usage/Sonar records. Документ обновляется после запуска, завершения, ошибки или изменения плана. Промежуточный trial не получает вымышленный результат; «—» означает, что данных нет.

## Этапы и предстоящая работа

| Этап | Статус | Что готово / что осталось |
| --- | --- | --- |
| Подготовка и OAuth smoke | Проверены; исторические доказательства сохранены | [Аудит среды](environment_report.md), [actual grader smoke](reports/phase1_smoke.md) |
| Phase 2: baseline / plan / goal_plan | Завершён | [Метрики и quota-resume history](reports/phase2_progress.md) |
| Phase 3: baseline / Ponytail / Caveman / Serena | Завершён | [Профили, активация и результаты](reports/phase3_progress.md) |
| Дополнение: serena_required | Отложен; приоритет — continuous без Serena | [Обязательный Serena-first workflow](reports/serena_required_progress.md); отдельный measured trial ещё не выполнен |
| Phase 4: Sonar before/after | Завершён для собранных snapshots | [Общая база и solution snapshots](reports/sonar_pilot.md); raw inline tests ограничивают сравнение |
| Phase 5: continuous, 2 связанных milestone | Остановлен quota gate: 85%; результаты сохранены | Baseline 2/2 и Caveman 1/2 приняты grader, Sonar завершён. Ponytail, plan и вторые повторы ожидают квоты. [План и состояние](reports/continuous_feasibility.md) |
| Phase 6: больший repo / повторы / full chain | Не запускался; отдельное согласование | Сначала определить scope, проверить квоту и бюджет новых образов/диска |

## Последовательный пилот: план запусков

Одна траектория = две связанные правки в одной сессии. Повторы начинают новую сессию. Метрики каждого шага приведены выше; сравнение с Phase 2/3 не смешивается.

| Траектория | Variant | Повтор | Завершено шагов | Статус |
| --- | --- | ---: | --- | --- |
| phase5_baseline_r01 | baseline | 1 | 2/2 | Завершён |
| phase5_caveman_r01 | caveman | 1 | 1/2 | Остановлен: квота |
| phase5_ponytail_r01 | ponytail | 1 | 0/2 | Ожидает квоты |
| phase5_plan_r01 | plan | 1 | 0/2 | Ожидает квоты |
| phase5_baseline_r02 | baseline | 2 | 0/2 | Ожидает квоты |
| phase5_caveman_r02 | caveman | 2 | 0/2 | Ожидает квоты |
| phase5_ponytail_r02 | ponytail | 2 | 0/2 | Ожидает квоты |
| phase5_plan_r02 | plan | 2 | 0/2 | Ожидает квоты |

[Протокол последовательного пилота](reports/phase5_protocol.md) · [Промежуточные результаты](reports/phase5_progress.md)

## Корректность и размер production patch

Каждая строка — отдельный trial или шаг continuous. Сравнивать с baseline внутри того же frozen cohort и повтора; Phase 2/3/5 не смешивать. Шаги одной траектории зависимы. Smoke не входит в A/B. «Grader принят» не означает, что вся raw test suite прошла.

| Trial / cohort | Variant | Статус | + строк | − строк | Net | Churn | Изменено prod-файлов |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline_smoke_001 | baseline | Завершён; grader принят | 74 | 24 | 50 | 98 | 5 |
| phase2_baseline_001 | baseline | Завершён; grader принят | 79 | 29 | 50 | 108 | 5 |
| phase2_plan_001 | plan | Завершён; grader принят | 83 | 28 | 55 | 111 | 5 |
| phase2_goal_plan_001 | goal_plan | Завершён; grader принят | 93 | 24 | 69 | 117 | 5 |
| phase3_baseline_001 | baseline | Завершён; grader принят | 78 | 24 | 54 | 102 | 5 |
| phase3_ponytail_001 | ponytail | Завершён; grader принят | 70 | 22 | 48 | 92 | 5 |
| phase3_caveman_001 | caveman | Завершён; grader принят | 77 | 21 | 56 | 98 | 5 |
| phase3_serena_001 | serena | Завершён; grader принят | 82 | 20 | 62 | 102 | 5 |
| phase5_baseline_r01_s01 | baseline | Завершён; grader принят | 15 | 17 | -2 | 32 | 2 |
| phase5_baseline_r01_s02 | baseline | Завершён; grader принят | 98 | 18 | 80 | 116 | 4 |
| phase5_caveman_r01_s01 | caveman | Завершён; grader принят | 36 | 10 | 26 | 46 | 3 |
| phase5_caveman_r01_s02 | caveman | Ошибка; результат сохранён | — | — | — | — | — |

Net = добавлено − удалено; churn = добавлено + удалено. Тесты/generated/vendor и inline Rust tests исключены из production LOC. Полные raw grader decisions, new/deleted/renamed files и cumulative LOC сохранены в JSONL.

## Токены и время

Input уже включает cached input: эти столбцы не складывать. Planning variants учитывают prep + executor. Это токены подписки, не сумма денег и не точная стоимость квоты.

| Trial | Input | Cached input | Output, prep + executor | Prep, с | Executor, с | Grader, с | Sonar, с | Trial всего, с |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_smoke_001 | 1 011 952 | 952 960 | 9 196 | 0 | 168.7 | — | 29.3 | 315.4 |
| phase2_baseline_001 | 692 777 | 635 392 | 9 125 | 0 | 185.1 | 65.4 | 28.7 | 339.8 |
| phase2_plan_001 | 1 332 672 | 1 229 312 | 14 022 | 146.6 | 247.7 | 97.5 | 31.3 | 583.8 |
| phase2_goal_plan_001 | 1 796 269 | 1 668 224 | 20 023 | 139.0 | 343.4 | 94.6 | 31.0 | 756.9 |
| phase3_baseline_001 | 730 529 | 672 512 | 10 294 | 0 | 164.4 | 100.7 | 33.5 | 362.4 |
| phase3_ponytail_001 | 917 133 | 850 816 | 10 092 | 0 | 175.9 | 105.9 | 29.5 | 388.7 |
| phase3_caveman_001 | 1 287 328 | 1 206 144 | 13 205 | 0 | 243.2 | 64.6 | 17.3 | 408.2 |
| phase3_serena_001 | 682 290 | 584 448 | 9 732 | 0 | 170.7 | 65.0 | 18.3 | 375.2 |
| phase5_baseline_r01_s01 | 752 475 | 697 344 | 7 684 | 0 | 183.5 | 110.8 | 40.4 | 377.8 |
| phase5_baseline_r01_s02 | 918 381 | 876 928 | 10 996 | 0 | 215.3 | 101.8 | 31.2 | 343.9 |
| phase5_caveman_r01_s01 | 550 342 | 501 888 | 6 898 | 0 | 172.6 | 114.3 | 31.2 | 374.1 |
| phase5_caveman_r01_s02 | — | — | — | 0 | — | — | — | 1.0 |

Trial total включает setup и служебные операции; Sonar выполняется отдельно. Goal_plan продолжен после quota pause: active time указан без всей паузы, полное wall time есть в JSON. Время описательное: host postprocessing частично пересекался с setup следующего trial.

## Sonar и использование навыков

Sonar измеряет raw graded snapshot, включая различающийся inline test-код. Поэтому эти значения не доказывают production-only эффект или качество архитектуры. ncloc — строки кода без комментариев и пустых строк; cognitive complexity — статическая оценка сложности ветвлений. Remediation — оценка Sonar в минутах, не время человеческого review.

| Trial | Sonar | ncloc | Cognitive complexity | Maintainability issues | Remediation, мин | Natural MCP calls | Memories после |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_smoke_001 | Готов | 31 461 | 2 424 | 283 | 1 443 | — | — |
| phase2_baseline_001 | Готов | 31 477 | 2 423 | 284 | 1 449 | — | — |
| phase2_plan_001 | Готов | 31 812 | 2 423 | 282 | 1 438 | — | — |
| phase2_goal_plan_001 | Готов | 31 838 | 2 442 | 283 | 1 444 | — | — |
| phase3_baseline_001 | Готов | 31 763 | 2 421 | 283 | 1 443 | — | — |
| phase3_ponytail_001 | Готов | 31 774 | 2 412 | 283 | 1 443 | — | — |
| phase3_caveman_001 | Готов | 31 767 | 2 425 | 284 | 1 449 | — | — |
| phase3_serena_001 | Готов | 31 799 | 2 421 | 283 | 1 443 | 0 | 0 |
| phase5_baseline_r01_s01 | Готов | 31 078 | 2 391 | 282 | 1 438 | — | — |
| phase5_baseline_r01_s02 | Готов | 31 176 | 2 405 | 282 | 1 438 | — | — |
| phase5_caveman_r01_s01 | Готов | 31 287 | 2 405 | 282 | 1 438 | — | — |
| phase5_caveman_r01_s02 | Не выполнен | — | — | — | — | — | — |

Подробные F2P/P2P/N2P, failures и skipped сохранены в canonical grader records. F2P — исправленные обязательные проверки, P2P — сохранённые проходившие проверки, N2P — новые проверки. Snapshot/collection failures отражаются в статусах. Native-hook audit и отдельный MCP smoke проверяют активацию, а natural usage показывает фактическое использование. Активационные smokes и их неуспешные попытки — setup overhead, не task A/B.

Несобранных trials: **0**, из них выполняется: **0**. Новые model trials требуют fresh quota check ниже 85% в обоих окнах. Этот документ сам ничего не запускает и не следит по расписанию.

## Как обновляется реестр

После изменения результатов или статуса выполняется `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status`. Команда читает `results/results.jsonl`, metadata ещё не собранных trials и continuous plan. Завершённые результаты сначала проходят существующий collector; таблица не заменяет grader и не пересчитывает scores.

[Итоговый pilot report](reports/pilot_report.md) · [Состояние требований](reports/implementation_status.md) · [CSV](results/results.csv) · [JSONL](results/results.jsonl) · [SonarQube локально](http://127.0.0.1:9000)
