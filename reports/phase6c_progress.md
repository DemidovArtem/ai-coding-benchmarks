# Phase 6c: два круга по три правки

Согласованный этап завершён: baseline, Caveman и Ponytail выполнили по два независимых повтора из трёх последовательных правок. Собраны все 18 результатов и 18 анализов Sonar. Внутри траектории сохраняется одна сессия и накапливается код; между траекториями сессии и репозитории изолированы.

| Подход | Output, круг 1 | Output, круг 2 | Средний output за 3 правки | Средний production churn после 3 правок | Средняя Δ cognitive complexity |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 27156 | 22400 | 24778 | 175.5 | 28 |
| caveman | 33714 | 33411 | 33562.5 | 168 | 24 |
| ponytail | 24726 | 25229 | 24977.5 | 151.5 | 39 |

Output берётся из native usage. Production churn — добавлено плюс удалено относительно общего начального snapshot; cumulative churn по шагам не суммируется. Input включает cached input. Sonar измеряет raw snapshot с inline tests; это ограничивает выводы о production-only качестве.

Canonical grader принял 12 из 18 правок. У остальных 6 отклонений совпадает проверка `glob::tests::re35`: точное сравнение regex зависит от порядка эквивалентных альтернатив. Исходные оценки не изменены. Подробные test summaries и сопоставление с task-local filtered results сохранены в [grader observations](phase6c_grader_observations.json).

Caveman во втором круге имел одну ошибку до первого модельного вызова: host обновил Node. Неудачная попытка сохранена. Повтор `phase6c_caveman_r02_retry01` использовал точные frozen Node bytes в отдельном host mount namespace; глобальный runtime, конфигурация, image и проверяемый код не менялись. [Доказательство восстановления](phase6c_node_recovery.json).

Проверены независимость шести сессий, последовательность input/submission commits, SHA-256 snapshots и Git bundles, replay cumulative/incremental patches и реальная native-hook activation. Средние каждого шага baseline/Caveman/Ponytail имеют n=2; показаны min/max, а не confidence interval. Serena остаётся на общем рисунке со своим исходным cohort и n=1.

[Общие графики](plots/mean_curves_current.png) · [Текстовые точки и provenance](plots/current_comparison.json) · [Параметры запусков](plots/run_parameters.md) · [Сохранённые diff](patches/README.md) · [Живой реестр](../EXPERIMENT_STATUS.md)

Более длинные цепочки, дополнительные повторы и новые репозитории не запускались. Для этого нужен отдельный план. Два повтора на трёх задачах дают предварительное сравнение, но ещё не надёжный рейтинг подходов.
