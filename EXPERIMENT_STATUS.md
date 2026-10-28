# Эксперименты: результаты и текущий статус

Обновлено: **2026-10-28 01:34:00**, Europe/Zurich. Это основной живой реестр проекта.

Источник чисел — сохранённые grader/Git/usage/Sonar records. Документ обновляется после запуска, завершения, ошибки или изменения плана. Промежуточный trial не получает вымышленный результат; «—» означает, что данных нет.

## Этапы и предстоящая работа

| Этап | Статус | Что готово / что осталось |
| --- | --- | --- |
| Подготовка и OAuth smoke | Проверены; исторические доказательства сохранены | [Аудит среды](environment_report.md), [actual grader smoke](reports/phase1_smoke.md) |
| Phase 2: baseline / plan / goal_plan | Завершён | [Метрики и quota-resume history](reports/phase2_progress.md) |
| Phase 3: baseline / Ponytail / Caveman / Serena | Завершён | [Профили, активация и результаты](reports/phase3_progress.md) |
| Дополнение: serena_required | Работает: 13 MCP calls, 2 symbol calls, 6 memories | [Обязательный Serena-first workflow](reports/serena_required_progress.md); отдельный measured trial ещё не выполнен |
| Текущий состав экспериментов | baseline, caveman, ponytail, serena | Plan исключён из новых запусков; прежние результаты сохранены. |
| Phase 4: Sonar before/after | Завершён для собранных snapshots | [Общая база и solution snapshots](reports/sonar_pilot.md); raw inline tests ограничивают сравнение |
| Phase 5: continuous, 2 связанных milestone | Пилот остановлен: quarantine preflight | Завершено 6/8 траекторий, 12/16 правок; все 12 приняты grader и проверены Sonar. Ponytail и plan repetition 2 заблокированы проверкой сети до model invocation. [План и состояние](reports/continuous_feasibility.md) |
| Phase 5b: baseline / Caveman / Ponytail | Заменён авторизованной Phase 6 | Новые двухшаговые trials не запускаются: пользователь расширил план до четырёх setups, двух кругов по пять правок. Прежний quota failure сохранён. [Протокол](reports/phase5b_protocol.md) |
| Phase 6: baseline / Caveman / Ponytail / Serena, 2×5 | Дальнейшие запуски отменены | Serena: три шага собраны; четвёртая submission сохранена с ошибкой grader. Checkpoint и 10 memories проверены. [Протокол](reports/phase6_protocol.md) |
| Phase 6b: исправленный grader и совместимые 5 задач, 2×5 | Дальнейшие запуски отменены | Baseline остановился до модели: installer HTTP 404. Пятишаговая матрица заменена тремя правками; история сохранена. [Протокол](reports/phase6b_protocol.md) |
| Phase 6c: baseline / Caveman / Ponytail, 2×3 | Завершён: два круга по три правки | Завершены 6/6 независимых траекторий и 18/18 правок; Sonar готов для всех 18. Средние baseline/Caveman/Ponytail имеют n=2 в каждой точке. [Итоги и ограничения](reports/phase6c_progress.md). Ошибка Node до модели и retry сохранены отдельно. [Протокол](reports/phase6c_protocol.md) |
| Phase 6d: четвёртая правка как продолжение, включая Serena | Завершён: четвёртый шаг всех семи траекторий | Собраны 7/7 четвёртых шагов и 7/7 Sonar assessments: baseline/Caveman/Ponytail по два повтора, Serena один сохранённый. Первые три шага не повторялись. Quota failure Ponytail и ошибка SQLite collection сохранены с recovery proofs. [Протокол](reports/phase6d_protocol.md) |
| Phase 6e: исходная пятая правка SWE, after-context | Trials выполняются | Траекторий завершено 5/7; ошибок 0. Метрики по шагам и протокол ниже. [Протокол](reports/phase6e_protocol.md) |
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
| phase6c_baseline_r01 | baseline | 1 | 3/3 | Завершён |
| phase6c_caveman_r01 | caveman | 1 | 3/3 | Завершён |
| phase6c_ponytail_r01 | ponytail | 1 | 3/3 | Завершён |
| phase6c_baseline_r02 | baseline | 2 | 3/3 | Завершён |
| phase6c_caveman_r02_retry01 | caveman | 2 | 3/3 | Завершён |
| phase6c_ponytail_r02 | ponytail | 2 | 3/3 | Завершён |
| phase6d_baseline_r01 | baseline | 1 | 1/1 | Завершён |
| phase6d_caveman_r01 | caveman | 1 | 1/1 | Завершён |
| phase6d_ponytail_r01 | ponytail | 1 | 1/1 | Завершён |
| phase6d_baseline_r02 | baseline | 2 | 1/1 | Завершён |
| phase6d_caveman_r02 | caveman | 2 | 1/1 | Завершён |
| phase6d_ponytail_r02 | ponytail | 2 | 1/1 | Завершён |
| phase6d_serena_r01 | serena | 1 | 1/1 | Завершён |
| phase6e_baseline_r01 | baseline | 1 | 1/1 | Завершён |
| phase6e_caveman_r01 | caveman | 1 | 1/1 | Завершён |
| phase6e_ponytail_r01 | ponytail | 1 | 1/1 | Завершён |
| phase6e_serena_r01 | serena | 1 | 1/1 | Завершён |
| phase6e_baseline_r02 | baseline | 2 | 1/1 | Завершён |
| phase6e_caveman_r02 | caveman | 2 | 0/1 | Выполняется |
| phase6e_ponytail_r02 | ponytail | 2 | 0/1 | Запланирован |

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
| phase6c_baseline_r01_s03 | baseline | Завершён; grader не принят | 149 | 28 | 121 | 177 | 5 |
| phase6c_caveman_r01_s01 | caveman | Завершён; grader принят | 15 | 15 | 0 | 30 | 2 |
| phase6c_caveman_r01_s02 | caveman | Завершён; grader принят | 81 | 16 | 65 | 97 | 4 |
| phase6c_caveman_r01_s03 | caveman | Завершён; grader не принят | 136 | 23 | 113 | 159 | 5 |
| phase6c_ponytail_r01_s01 | ponytail | Завершён; grader принят | 12 | 16 | -4 | 28 | 2 |
| phase6c_ponytail_r01_s02 | ponytail | Завершён; grader принят | 71 | 17 | 54 | 88 | 4 |
| phase6c_ponytail_r01_s03 | ponytail | Завершён; grader не принят | 124 | 24 | 100 | 148 | 5 |
| phase6c_baseline_r02_s01 | baseline | Завершён; grader принят | 12 | 16 | -4 | 28 | 2 |
| phase6c_baseline_r02_s02 | baseline | Завершён; grader принят | 91 | 17 | 74 | 108 | 4 |
| phase6c_baseline_r02_s03 | baseline | Завершён; grader не принят | 149 | 25 | 124 | 174 | 5 |
| phase6c_caveman_r02_s01 | caveman | Ошибка; результат сохранён | — | — | — | — | — |
| phase6c_caveman_r02_retry01_s01 | caveman | Завершён; grader принят | 19 | 15 | 4 | 34 | 2 |
| phase6c_caveman_r02_retry01_s02 | caveman | Завершён; grader принят | 103 | 16 | 87 | 119 | 4 |
| phase6c_caveman_r02_retry01_s03 | caveman | Завершён; grader не принят | 156 | 21 | 135 | 177 | 5 |
| phase6c_ponytail_r02_s01 | ponytail | Завершён; grader принят | 12 | 16 | -4 | 28 | 2 |
| phase6c_ponytail_r02_s02 | ponytail | Завершён; grader принят | 76 | 17 | 59 | 93 | 4 |
| phase6c_ponytail_r02_s03 | ponytail | Завершён; grader не принят | 133 | 22 | 111 | 155 | 5 |
| phase6d_serena_r01_s04 | serena | Завершён; grader не принят | 214 | 37 | 177 | 251 | 7 |
| phase6d_baseline_r01_s04 | baseline | Завершён; grader не принят | 212 | 37 | 175 | 249 | 6 |
| phase6d_caveman_r01_s04 | caveman | Завершён; grader не принят | 216 | 39 | 177 | 255 | 6 |
| phase6d_ponytail_r01_s04 | ponytail | Завершён; grader не принят | 189 | 41 | 148 | 230 | 6 |
| phase6d_baseline_r02_s04 | baseline | Завершён; grader не принят | 233 | 41 | 192 | 274 | 6 |
| phase6d_caveman_r02_s04 | caveman | Завершён; grader не принят | 232 | 30 | 202 | 262 | 6 |
| phase6d_ponytail_r02_s04 | ponytail | Ошибка; результат сохранён | — | — | — | — | — |
| phase6d_ponytail_r02_s04_resume01 | ponytail | Завершён; grader не принят | 183 | 30 | 153 | 213 | 6 |
| phase6e_baseline_r01_s05 | baseline | Ошибка; результат сохранён | 274 | 85 | 189 | 359 | 8 |
| phase6e_caveman_r01_s05 | caveman | Ошибка; результат сохранён | 294 | 81 | 213 | 375 | 9 |
| phase6e_ponytail_r01_s05 | ponytail | Ошибка; результат сохранён | 204 | 53 | 151 | 257 | 8 |
| phase6e_serena_r01_s05 | serena | Ошибка; результат сохранён | 271 | 89 | 182 | 360 | 9 |
| phase6e_baseline_r02_s05 | baseline | Ошибка; результат сохранён | 276 | 53 | 223 | 329 | 9 |
| phase6e_serena_r01_s05_quota01 | serena | Ошибка; результат сохранён | — | — | — | — | — |

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
| phase6c_baseline_r01_s03 | 1 231 539 | 1 193 984 | 8 992 | 0 | 180.2 | 68.0 | 17.4 | 272.6 |
| phase6c_caveman_r01_s01 | 648 985 | 604 544 | 8 344 | 0 | 204.0 | 72.6 | 16.1 | 359.1 |
| phase6c_caveman_r01_s02 | 1 026 873 | 999 936 | 12 775 | 0 | 292.9 | 66.5 | 16.1 | 383.8 |
| phase6c_caveman_r01_s03 | 1 416 510 | 1 384 064 | 12 595 | 0 | 282.6 | 99.2 | 30.3 | 407.4 |
| phase6c_ponytail_r01_s01 | 692 895 | 629 120 | 7 930 | 0 | 191.6 | 107.8 | 27.6 | 373.5 |
| phase6c_ponytail_r01_s02 | 922 570 | 877 312 | 9 052 | 0 | 195.3 | 99.8 | 28.6 | 321.2 |
| phase6c_ponytail_r01_s03 | 1 530 043 | 1 486 208 | 7 744 | 0 | 159.6 | 97.2 | 26.7 | 283.5 |
| phase6c_baseline_r02_s01 | 653 125 | 593 280 | 6 213 | 0 | 213.1 | 113.7 | 38.9 | 416.0 |
| phase6c_baseline_r02_s02 | 881 084 | 853 376 | 8 901 | 0 | 296.8 | 103.3 | 32.5 | 427.7 |
| phase6c_baseline_r02_s03 | 1 065 462 | 1 037 440 | 7 286 | 0 | 228.1 | 103.1 | 30.5 | 357.9 |
| phase6c_caveman_r02_s01 | — | — | — | 0 | — | — | — | 69.7 |
| phase6c_caveman_r02_retry01_s01 | 793 114 | 724 992 | 9 466 | 0 | 227.8 | 113.8 | 30.9 | 428.5 |
| phase6c_caveman_r02_retry01_s02 | 1 251 323 | 1 216 768 | 15 205 | 0 | 394.4 | 103.6 | 30.1 | 524.7 |
| phase6c_caveman_r02_retry01_s03 | 1 318 382 | 1 285 376 | 8 740 | 0 | 215.9 | 103.1 | 30.9 | 345.7 |
| phase6c_ponytail_r02_s01 | 462 204 | 413 568 | 6 320 | 0 | 183.7 | 114.2 | 28.8 | 374.0 |
| phase6c_ponytail_r02_s02 | 910 645 | 872 960 | 10 981 | 0 | 314.9 | 103.0 | 28.9 | 444.4 |
| phase6c_ponytail_r02_s03 | 1 348 685 | 1 318 912 | 7 928 | 0 | 248.5 | 103.2 | 30.2 | 378.3 |
| phase6d_serena_r01_s04 | 4 249 057 | 4 202 496 | 21 486 | 0 | — | 99.9 | — | 99.9 |
| phase6d_baseline_r01_s04 | 1 953 889 | 1 793 024 | 9 944 | 0 | 627.9 | 102.2 | 38.7 | 755.7 |
| phase6d_caveman_r01_s04 | 1 970 461 | 1 809 024 | 20 860 | 0 | 590.5 | 102.0 | 32.6 | 718.4 |
| phase6d_ponytail_r01_s04 | 2 435 297 | 2 257 408 | 12 956 | 0 | 369.1 | 106.9 | 32.5 | 501.9 |
| phase6d_baseline_r02_s04 | 2 014 961 | 1 873 792 | 12 615 | 0 | 352.8 | 107.9 | 31.4 | 486.3 |
| phase6d_caveman_r02_s04 | 2 118 184 | 1 948 928 | 12 845 | 0 | 744.8 | 103.4 | 30.1 | 873.9 |
| phase6d_ponytail_r02_s04 | — | — | — | 0 | 22.4 | — | — | 45.7 |
| phase6d_ponytail_r02_s04_resume01 | 2 052 035 | 1 741 312 | 7 063 | 0 | 199.4 | 111.7 | 31.9 | — |
| phase6e_baseline_r01_s05 | 2 860 033 | 2 662 144 | 8 015 | 0 | 173.9 | 91.9 | 39.1 | 291.9 |
| phase6e_caveman_r01_s05 | 3 942 015 | 3 751 168 | 9 407 | 0 | 217.3 | 91.0 | 31.4 | 334.1 |
| phase6e_ponytail_r01_s05 | 2 436 624 | 2 229 760 | 6 499 | 0 | 137.0 | 90.4 | 28.6 | 253.2 |
| phase6e_serena_r01_s05 | 3 868 588 | 3 630 848 | 9 072 | 0 | 192.6 | 88.4 | 30.1 | 307.0 |
| phase6e_baseline_r02_s05 | 3 925 047 | 3 728 896 | 13 927 | 0 | 326.9 | 89.6 | 29.8 | 442.2 |
| phase6e_serena_r01_s05_quota01 | — | — | — | — | — | — | — | — |

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
| phase6c_baseline_r01_s03 | Готов | 31 361 | 2 430 | 281 | 1 433 | — | — |
| phase6c_caveman_r01_s01 | Готов | 31 086 | 2 391 | 282 | 1 438 | — | — |
| phase6c_caveman_r01_s02 | Готов | 31 130 | 2 408 | 282 | 1 438 | — | — |
| phase6c_caveman_r01_s03 | Готов | 31 354 | 2 423 | 284 | 1 448 | — | — |
| phase6c_ponytail_r01_s01 | Готов | 31 079 | 2 391 | 282 | 1 438 | — | — |
| phase6c_ponytail_r01_s02 | Готов | 31 148 | 2 405 | 282 | 1 438 | — | — |
| phase6c_ponytail_r01_s03 | Готов | 31 294 | 2 442 | 282 | 1 438 | — | — |
| phase6c_baseline_r02_s01 | Готов | 31 079 | 2 391 | 282 | 1 438 | — | — |
| phase6c_baseline_r02_s02 | Готов | 31 128 | 2 404 | 282 | 1 438 | — | — |
| phase6c_baseline_r02_s03 | Готов | 31 328 | 2 426 | 282 | 1 438 | — | — |
| phase6c_caveman_r02_s01 | Не выполнен | — | — | — | — | — | — |
| phase6c_caveman_r02_retry01_s01 | Готов | 31 088 | 2 391 | 282 | 1 438 | — | — |
| phase6c_caveman_r02_retry01_s02 | Готов | 31 140 | 2 410 | 282 | 1 438 | — | — |
| phase6c_caveman_r02_retry01_s03 | Готов | 31 354 | 2 425 | 282 | 1 438 | — | — |
| phase6c_ponytail_r02_s01 | Готов | 31 079 | 2 391 | 282 | 1 438 | — | — |
| phase6c_ponytail_r02_s02 | Готов | 31 153 | 2 405 | 282 | 1 438 | — | — |
| phase6c_ponytail_r02_s03 | Готов | 31 289 | 2 436 | 282 | 1 438 | — | — |
| phase6d_serena_r01_s04 | Готов | 31 388 | 2 430 | 282 | 1 438 | — | 11 |
| phase6d_baseline_r01_s04 | Готов | 31 459 | 2 434 | 281 | 1 433 | — | — |
| phase6d_caveman_r01_s04 | Готов | 31 512 | 2 434 | 285 | 1 453 | — | — |
| phase6d_ponytail_r01_s04 | Готов | 31 359 | 2 444 | 283 | 1 443 | — | — |
| phase6d_baseline_r02_s04 | Готов | 31 405 | 2 429 | 282 | 1 438 | — | — |
| phase6d_caveman_r02_s04 | Готов | 31 489 | 2 435 | 282 | 1 438 | — | — |
| phase6d_ponytail_r02_s04 | Не выполнен | — | — | — | — | — | — |
| phase6d_ponytail_r02_s04_resume01 | Готов | 31 346 | 2 436 | 282 | 1 438 | — | — |
| phase6e_baseline_r01_s05 | Готов | 31 616 | 2 455 | 281 | 1 433 | — | — |
| phase6e_caveman_r01_s05 | Готов | 31 690 | 2 461 | 285 | 1 453 | — | — |
| phase6e_ponytail_r01_s05 | Готов | 31 483 | 2 464 | 283 | 1 443 | — | — |
| phase6e_serena_r01_s05 | Готов | 31 544 | 2 462 | 282 | 1 439 | — | 12 |
| phase6e_baseline_r02_s05 | Готов | 31 542 | 2 444 | 282 | 1 438 | — | — |
| phase6e_serena_r01_s05_quota01 | Не выполнен | — | — | — | — | — | — |

Подробные F2P/P2P/N2P, failures и skipped сохранены в canonical grader records. F2P — исправленные обязательные проверки, P2P — сохранённые проходившие проверки, N2P — новые проверки. Snapshot/collection failures отражаются в статусах. Native-hook audit и отдельный MCP smoke проверяют активацию, а natural usage показывает фактическое использование. Активационные smokes и их неуспешные попытки — setup overhead, не task A/B.

Несобранных trials: **1**, из них выполняется: **0**. Для Phase 5 пользователь разрешил продолжение выше 85%; явный отказ сервиса по квоте по-прежнему останавливает запуск. [Разрешённое изменение](reports/phase5_quota_override.md). Этот документ сам ничего не запускает и не следит по расписанию.

## Как обновляется реестр

После изменения результатов или статуса выполняется `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status`. Команда читает `results/results.jsonl`, metadata ещё не собранных trials и continuous plan. Завершённые результаты сначала проходят существующий collector; таблица не заменяет grader и не пересчитывает scores.

[Средние кривые по правкам](reports/plots/MEAN_CURVES.md) · [Сохранённые patches](reports/patches/README.md) · [История графиков](reports/plots/README.md) · [Итоговый pilot report](reports/pilot_report.md) · [Состояние требований](reports/implementation_status.md) · [CSV](results/results.csv) · [JSONL](results/results.jsonl) · [SonarQube локально](http://127.0.0.1:9000)
