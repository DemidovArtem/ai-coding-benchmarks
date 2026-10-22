# Эксперименты: результаты и текущий статус

Обновлено: **2026-10-22 23:42:25**, Europe/Zurich. Это основной живой реестр проекта.

Источник чисел — сохранённые grader/Git/usage/Sonar records. Документ обновляется после запуска, завершения, ошибки или изменения плана. Промежуточный trial не получает вымышленный результат; «—» означает, что данных нет.

## Этапы и предстоящая работа

| Этап | Статус | Что готово / что осталось |
| --- | --- | --- |
| Подготовка и OAuth smoke | Проверены; исторические доказательства сохранены | [Аудит среды](environment_report.md), [actual grader smoke](reports/phase1_smoke.md) |
| Phase 2: baseline / plan / goal_plan | Завершён | [Метрики и quota-resume history](reports/phase2_progress.md) |
| Phase 3: baseline / Ponytail / Caveman / Serena | Завершён | [Профили, активация и результаты](reports/phase3_progress.md) |
| Дополнение: serena_required | Работает: 13 MCP calls, 2 symbol calls, 6 memories | [Обязательный Serena-first workflow](reports/serena_required_progress.md); отдельный measured trial ещё не выполнен |
| Текущий состав экспериментов | baseline, caveman, ponytail | Plan исключён из новых запусков; прежние результаты сохранены. |
| Phase 4: Sonar before/after | Завершён для собранных snapshots | [Общая база и solution snapshots](reports/sonar_pilot.md); raw inline tests ограничивают сравнение |
| Phase 5: continuous, 2 связанных milestone | Пилот остановлен: quarantine preflight | Завершено 6/8 траекторий, 12/16 правок; все 12 приняты grader и проверены Sonar. Ponytail и plan repetition 2 заблокированы проверкой сети до model invocation. [План и состояние](reports/continuous_feasibility.md) |
| Phase 5b: baseline / Caveman / Ponytail | Заменён авторизованной Phase 6 | Новые двухшаговые trials не запускаются: пользователь расширил план до четырёх setups, двух кругов по пять правок. Прежний quota failure сохранён. [Протокол](reports/phase5b_protocol.md) |
| Phase 6: baseline / Caveman / Ponytail / Serena, 2×5 | Дальнейшие запуски отменены | Serena: три шага собраны; четвёртая submission сохранена с ошибкой grader. Checkpoint и 10 memories проверены. [Протокол](reports/phase6_protocol.md) |
| Phase 6b: исправленный grader и совместимые 5 задач, 2×5 | Дальнейшие запуски отменены | Baseline остановился до модели: installer HTTP 404. Пятишаговая матрица заменена тремя правками; история сохранена. [Протокол](reports/phase6b_protocol.md) |
| Phase 6c: baseline / Caveman / Ponytail, 2×3 | Trials выполняются | Траекторий завершено 0/6; ошибок 0. Метрики по шагам и протокол ниже. [Протокол](reports/phase6c_protocol.md) |
| Дальнейшее расширение: больший repo / full chain | Не запускалось; отдельное согласование | Сначала определить scope, проверить квоту и бюджет новых образов/диска |

## Последовательный пилот: план запусков

Одна траектория = последовательные правки в одной сессии; число шагов указано в таблице. Повторы начинают новую сессию. Метрики разных frozen cohorts не смешиваются.

| Траектория | Variant | Повтор | Завершено шагов | Статус |
| --- | --- | ---: | --- | --- |
| phase5_baseline_r01 | baseline | 1 | 2/2 | Завершён |
| phase5_caveman_r01 | caveman | 1 | 2/2 | Завершён |
| phase5_ponytail_r01_retry01 | ponytail | 1 | 2/2 | Завершён |
| phase5_plan_r01_retry01 | plan | 1 | 2/2 | Завершён |
| phase5_baseline_r02 | baseline | 2 | 2/2 | Завершён |
| phase5_caveman_r02 | caveman | 2 | 2/2 | Завершён |
| phase5_ponytail_r02 | ponytail | 2 | 0/2 | Заблокирован: quarantine |
| phase5_plan_r02 | plan | 2 | 0/2 | Исключён из новых запусков |
| phase5b_ponytail_r02_retry01 | ponytail | 2 | 0/2 | Исключён из новых запусков |
| phase5b_baseline_r02 | baseline | 2 | 0/2 | Исключён из новых запусков |
| phase5b_caveman_r02 | caveman | 2 | 0/2 | Исключён из новых запусков |
| phase6_serena_r01 | serena | 1 | 3/5 | Ошибка; данные сохранены |
| phase6_baseline_r01 | baseline | 1 | 0/5 | Исключён из новых запусков |
| phase6_caveman_r01 | caveman | 1 | 0/5 | Исключён из новых запусков |
| phase6_ponytail_r01 | ponytail | 1 | 0/5 | Исключён из новых запусков |
| phase6_serena_r02 | serena | 2 | 0/5 | Исключён из новых запусков |
| phase6_baseline_r02 | baseline | 2 | 0/5 | Исключён из новых запусков |
| phase6_caveman_r02 | caveman | 2 | 0/5 | Исключён из новых запусков |
| phase6_ponytail_r02 | ponytail | 2 | 0/5 | Исключён из новых запусков |
| phase6b_baseline_r01 | baseline | 1 | 0/5 | Ошибка; данные сохранены |
| phase6b_caveman_r01 | caveman | 1 | 0/5 | Исключён из новых запусков |
| phase6b_ponytail_r01 | ponytail | 1 | 0/5 | Исключён из новых запусков |
| phase6b_serena_r01 | serena | 1 | 0/5 | Исключён из новых запусков |
| phase6b_baseline_r02 | baseline | 2 | 0/5 | Исключён из новых запусков |
| phase6b_caveman_r02 | caveman | 2 | 0/5 | Исключён из новых запусков |
| phase6b_ponytail_r02 | ponytail | 2 | 0/5 | Исключён из новых запусков |
| phase6b_serena_r02 | serena | 2 | 0/5 | Исключён из новых запусков |
| phase6c_baseline_r01 | baseline | 1 | 2/3 | Выполняется |
| phase6c_caveman_r01 | caveman | 1 | 0/3 | Запланирован |
| phase6c_ponytail_r01 | ponytail | 1 | 0/3 | Запланирован |
| phase6c_baseline_r02 | baseline | 2 | 0/3 | Запланирован |
| phase6c_caveman_r02 | caveman | 2 | 0/3 | Запланирован |
| phase6c_ponytail_r02 | ponytail | 2 | 0/3 | Запланирован |

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
| phase5_ponytail_r01_s01 | ponytail | Ошибка; результат сохранён | — | — | — | — | — |
| phase5_caveman_r01_s02_resume02 | caveman | Ошибка; результат сохранён | — | — | — | — | — |
| phase5_plan_r01_s01 | plan | Ошибка; результат сохранён | — | — | — | — | — |
| phase5_caveman_r01_s02_resume03 | caveman | Завершён; grader принят | 114 | 11 | 103 | 125 | 5 |
| phase5_ponytail_r01_retry01_s01 | ponytail | Завершён; grader принят | 14 | 14 | 0 | 28 | 2 |
| phase5_ponytail_r01_retry01_s02 | ponytail | Завершён; grader принят | 73 | 15 | 58 | 88 | 4 |
| phase5_plan_r01_retry01_s01 | plan | Завершён; grader принят | 20 | 14 | 6 | 34 | 2 |
| phase5_plan_r01_retry01_s02 | plan | Завершён; grader принят | 99 | 15 | 84 | 114 | 4 |
| phase5_baseline_r02_s01 | baseline | Завершён; grader принят | 13 | 16 | -3 | 29 | 2 |
| phase5_baseline_r02_s02 | baseline | Ошибка; результат сохранён | — | — | — | — | — |
| phase5_baseline_r02_s02_resume01 | baseline | Завершён; grader принят | 87 | 17 | 70 | 104 | 4 |
| phase5_caveman_r02_s01 | caveman | Завершён; grader принят | 15 | 13 | 2 | 28 | 2 |
| phase5_caveman_r02_s02 | caveman | Завершён; grader принят | 90 | 14 | 76 | 104 | 4 |
| phase5_ponytail_r02_s01 | ponytail | Ошибка; результат сохранён | — | — | — | — | — |
| phase5b_ponytail_r02_s01 | ponytail | Ошибка; результат сохранён | — | — | — | — | — |
| phase6_serena_r01_s01 | serena | Завершён; grader принят | 12 | 12 | 0 | 24 | 2 |
| phase6_serena_r01_s02 | serena | Завершён; grader принят | 84 | 13 | 71 | 97 | 4 |
| phase6_serena_r01_s03 | serena | Ошибка; результат сохранён | — | — | — | — | — |
| phase6_serena_r01_s03_retry01 | serena | Завершён; grader не принят | 133 | 21 | 112 | 154 | 5 |
| phase6_serena_r01_s04 | serena | Ошибка; результат сохранён | 214 | 37 | 177 | 251 | 7 |
| phase6b_baseline_r01_s01 | baseline | Ошибка; результат сохранён | — | — | — | — | — |
| phase6c_baseline_r01_s01 | baseline | Завершён; grader принят | 17 | 19 | -2 | 36 | 2 |
| phase6c_baseline_r01_s02 | baseline | Завершён; grader принят | 98 | 21 | 77 | 119 | 4 |
| phase6c_baseline_r01_s03 | baseline | Выполняется | — | — | — | — | — |

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
| phase5_ponytail_r01_s01 | — | — | — | 0 | 191.5 | — | — | 271.1 |
| phase5_caveman_r01_s02_resume02 | — | — | — | 0 | — | — | — | 41.3 |
| phase5_plan_r01_s01 | — | — | — | — | — | — | — | — |
| phase5_caveman_r01_s02_resume03 | 818 688 | 748 928 | 7 829 | 0 | 157.7 | 71.5 | 37.2 | 253.0 |
| phase5_ponytail_r01_retry01_s01 | 580 057 | 527 872 | 7 079 | 0 | 160.4 | 72.9 | 18.0 | 344.1 |
| phase5_ponytail_r01_retry01_s02 | 929 347 | 879 488 | 10 346 | 0 | 220.1 | 65.1 | 17.1 | 309.5 |
| phase5_plan_r01_retry01_s01 | 1 016 152 | 888 448 | 12 644 | 99.9 | 228.8 | 72.2 | 17.1 | 469.5 |
| phase5_plan_r01_retry01_s02 | 1 141 163 | 1 069 184 | 12 917 | 119.9 | 202.8 | 65.2 | 15.9 | 413.4 |
| phase5_baseline_r02_s01 | 536 389 | 489 728 | 6 213 | 0 | 143.3 | 71.3 | 37.1 | 280.7 |
| phase5_baseline_r02_s02 | — | — | — | 0 | — | — | — | 0.6 |
| phase5_baseline_r02_s02_resume01 | 746 778 | 681 856 | 8 920 | 0 | 274.3 | 115.0 | 29.6 | 414.7 |
| phase5_caveman_r02_s01 | 573 366 | 471 424 | 7 296 | 0 | 237.3 | 126.9 | 30.1 | 533.8 |
| phase5_caveman_r02_s02 | 964 192 | 908 800 | 11 644 | 0 | 366.3 | 116.2 | 29.6 | 510.0 |
| phase5_ponytail_r02_s01 | — | — | — | 0 | — | — | — | 116.5 |
| phase5b_ponytail_r02_s01 | — | — | — | 0 | — | — | — | 183.1 |
| phase6_serena_r01_s01 | 1 202 433 | 1 128 960 | 8 691 | 0 | 231.1 | 112.2 | 30.4 | 484.4 |
| phase6_serena_r01_s02 | 1 428 783 | 1 400 320 | 13 143 | 0 | 289.9 | 100.5 | 38.7 | 392.1 |
| phase6_serena_r01_s03 | — | — | — | 0 | — | — | — | 44.0 |
| phase6_serena_r01_s03_retry01 | 2 189 873 | 2 050 432 | 9 896 | 0 | 272.2 | 101.3 | 29.9 | 402.2 |
| phase6_serena_r01_s04 | 4 249 057 | 4 202 496 | 21 486 | 0 | 577.6 | 163.9 | 32.3 | 770.3 |
| phase6b_baseline_r01_s01 | — | — | — | 0 | — | — | — | 19.9 |
| phase6c_baseline_r01_s01 | 603 396 | 530 688 | 7 182 | 0 | 177.0 | 73.3 | 17.4 | 312.7 |
| phase6c_baseline_r01_s02 | 1 050 095 | 999 552 | 10 982 | 0 | 242.4 | 68.9 | 19.5 | 335.7 |
| phase6c_baseline_r01_s03 | — | — | — | — | — | — | — | — |

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
| phase5_ponytail_r01_s01 | Не выполнен | — | — | — | — | — | — |
| phase5_caveman_r01_s02_resume02 | Не выполнен | — | — | — | — | — | — |
| phase5_plan_r01_s01 | Не выполнен | — | — | — | — | — | — |
| phase5_caveman_r01_s02_resume03 | Готов | 31 482 | 2 424 | 282 | 1 438 | — | — |
| phase5_ponytail_r01_retry01_s01 | Готов | 31 079 | 2 391 | 282 | 1 438 | — | — |
| phase5_ponytail_r01_retry01_s02 | Готов | 31 145 | 2 406 | 282 | 1 438 | — | — |
| phase5_plan_r01_retry01_s01 | Готов | 31 389 | 2 409 | 282 | 1 438 | — | — |
| phase5_plan_r01_retry01_s02 | Готов | 31 616 | 2 429 | 282 | 1 438 | — | — |
| phase5_baseline_r02_s01 | Готов | 31 079 | 2 392 | 282 | 1 438 | — | — |
| phase5_baseline_r02_s02 | Не выполнен | — | — | — | — | — | — |
| phase5_baseline_r02_s02_resume01 | Готов | 31 126 | 2 404 | 282 | 1 438 | — | — |
| phase5_caveman_r02_s01 | Готов | 31 086 | 2 391 | 282 | 1 438 | — | — |
| phase5_caveman_r02_s02 | Готов | 31 131 | 2 402 | 282 | 1 438 | — | — |
| phase5_ponytail_r02_s01 | Не выполнен | — | — | — | — | — | — |
| phase5b_ponytail_r02_s01 | Не выполнен | — | — | — | — | — | — |
| phase6_serena_r01_s01 | Готов | 31 086 | 2 392 | 282 | 1 438 | — | 7 |
| phase6_serena_r01_s02 | Готов | 31 128 | 2 409 | 282 | 1 438 | — | 8 |
| phase6_serena_r01_s03 | Не выполнен | — | — | — | — | — | — |
| phase6_serena_r01_s03_retry01 | Готов | 31 298 | 2 426 | 282 | 1 438 | — | 10 |
| phase6_serena_r01_s04 | Готов | 31 388 | 2 430 | 282 | 1 438 | — | 11 |
| phase6b_baseline_r01_s01 | Не выполнен | — | — | — | — | — | — |
| phase6c_baseline_r01_s01 | Готов | 31 079 | 2 392 | 281 | 1 433 | — | — |
| phase6c_baseline_r01_s02 | Готов | 31 131 | 2 414 | 281 | 1 433 | — | — |
| phase6c_baseline_r01_s03 | Не выполнен | — | — | — | — | — | — |

Подробные F2P/P2P/N2P, failures и skipped сохранены в canonical grader records. F2P — исправленные обязательные проверки, P2P — сохранённые проходившие проверки, N2P — новые проверки. Snapshot/collection failures отражаются в статусах. Native-hook audit и отдельный MCP smoke проверяют активацию, а natural usage показывает фактическое использование. Активационные smokes и их неуспешные попытки — setup overhead, не task A/B.

Несобранных trials: **1**, из них выполняется: **1**. Для Phase 5 пользователь разрешил продолжение выше 85%; явный отказ сервиса по квоте по-прежнему останавливает запуск. [Разрешённое изменение](reports/phase5_quota_override.md). Этот документ сам ничего не запускает и не следит по расписанию.

## Как обновляется реестр

После изменения результатов или статуса выполняется `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status`. Команда читает `results/results.jsonl`, metadata ещё не собранных trials и continuous plan. Завершённые результаты сначала проходят существующий collector; таблица не заменяет grader и не пересчитывает scores.

[Средние кривые по правкам](reports/plots/MEAN_CURVES.md) · [Сохранённые patches](reports/patches/README.md) · [История графиков](reports/plots/README.md) · [Итоговый pilot report](reports/pilot_report.md) · [Состояние требований](reports/implementation_status.md) · [CSV](results/results.csv) · [JSONL](results/results.jsonl) · [SonarQube локально](http://127.0.0.1:9000)
