# Последовательный пилот: промежуточные результаты

**Phase 5b:** после запроса пользователя выполняется отдельная пара Ponytail + baseline с усиленной изоляцией registry. Проверка сети без модели успешна; результаты будут сравниваться только внутри новой пары. [Протокол](phase5b_protocol.md), [реестр](../EXPERIMENT_STATUS.md).

[Графики дельт к baseline, Sonar и накопления по шагам](plots/README.md) · [PDF](plots/comparison.pdf). Повторы показаны отдельно; отсутствующие результаты не заменяются нулями.

## Второй repetition: остановлен проверкой quarantine

Baseline и Caveman завершили обе правки: все четыре grader результата приняты, collection errors отсутствуют, все четыре Sonar scan завершены. Ponytail repetition 2 остановлен до model invocation: preflight воспроизвёл доступность запрещённого registry. Plan repetition 2 не запускался и заблокирован тем же условием. Завершено 12/16 правок, все 12 приняты grader и проверены Sonar. [Причина и доказательства](phase5_quarantine_failure.md).

| Вариант | Статус | Cumulative production + / − | Churn | Output, два шага с prep |
| --- | --- | --- | ---: | ---: |
| baseline | Завершён, 2/2 | +87 / −17 | 104 | 15 133 |
| caveman | Завершён, 2/2 | +90 / −14 | 104 | 18 940 |
| ponytail | Заблокирован: quarantine, 0/2 | — | — | — |
| plan | Заблокирован: quarantine, 0/2 | — | — | — |

Второй шаг baseline продолжен после фактического quota stop в том же executor thread; исходная остановка сохранена отдельной строкой. Caveman прошёл оба шага без recovery. Актуальные шаги — в [основном реестре](../EXPERIMENT_STATUS.md).

## Первый полный repetition: 21 октября

Все четыре варианта завершили по две связанные правки. Все восемь task execution приняты grader, collection errors отсутствуют, Sonar завершён для каждого snapshot. Проверены одинаковый frozen cohort/paired key, одна executor session на траекторию, чтение полного задания и точные Git/snapshot bindings. [Машинная сводка](phase5_comparison.json).

| Вариант | Cumulative production + / − | Churn | Output, два шага с prep | Sonar ncloc | Cognitive complexity | Maintainability issues |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | +98 / −18 | 116 | 18,680 | 31176 | 2405 | 282 |
| caveman | +114 / −11 | 125 | 14,727 | 31482 | 2424 | 282 |
| ponytail | +73 / −15 | 88 | 17,425 | 31145 | 2406 | 282 |
| plan | +99 / −15 | 114 | 25,561 | 31616 | 2429 | 282 |

Cumulative LOC сравнивает финальный submission с исходным состоянием; значения шагов не складываются. Одна траектория на вариант не даёт статистического рейтинга. Sonar включает различающийся inline test-код; production LOC исключает тесты. Во всех восьми raw grader suites остаются baseline/flaky failures; принятие grader означает выполнение обязательных F2P/P2P/N2P, а не отсутствие всех raw failures.

Caveman продолжен после quota pause в исходной сессии. Ponytail и plan здесь — явно названные fresh infrastructure retries; прежние прерванные попытки сохранены. Повтор 2 запущен с baseline. Актуальная очередь — в [основном реестре](../EXPERIMENT_STATUS.md).

## История первоначальной остановки

На 20 октября 2026 года выполнены три task execution из запланированных шестнадцати. Baseline завершил две связанные правки в одном Codex thread. Caveman завершил первую правку; перед второй quota gate остановил запуск при 85% использования основного окна. Второй шаг Caveman не вызывал модель и не имеет grader/LOC/Sonar результата. Этот отказ сохранён отдельно, а не заменён успешным trial.

| Вариант, повтор 1 | Шаг | Grader | F2P | P2P | N2P | Production + / − от начала | Churn | Output этого шага | Sonar maintainability issues |
| --- | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| baseline | 1 | Принят | 9/9 | 1084/1084 | 0/0 | +15 / −17 | 32 | 7 684 | 282 |
| baseline | 2 | Принят | 1/1 | 1102/1102 | 9/9 | +98 / −18 | 116 | 10 996 | 282 |
| Caveman | 1 | Принят | 9/9 | 1084/1084 | 0/0 | +36 / −10 | 46 | 6 898 | 282 |
| Caveman | 2 | Не запускался: quota gate | — | — | — | — | — | — | — |

Ponytail запущен после разрешения пользователя продолжать выше 85%, но первый шаг прерван фактическим usage limit сервиса без submission tag. Grader/LOC/Sonar для этого незавершённого шага отсутствуют. Plan + implementation ещё не запускался. Вторые независимые повторы всех четырёх вариантов тоже ожидают квоты. Полный план и статусы — в [основном реестре](../EXPERIMENT_STATUS.md).

## Что подтверждено

Baseline сохранил один thread ID `01a15af2-3426-7102-aef4-985436aa8d5d` и один repository между двумя задачами. На обоих шагах проверены полное чтение выданного задания, immutable submission tag, snapshot SHA/Rust bytes, чистая граница шага и сохранение предыдущего submission. Второй commit происходит от первого. Per-step usage получен разностью cumulative counters одной сессии. Второй шаг baseline имеет incremental production churn 84 относительно первого, а cumulative churn 116 относительно начала траектории.

Caveman native-hook audit подтвердил реальную активацию. Его первый шаг использует тот же frozen cohort и ту же задачу, что первый шаг baseline. В этом единственном парном наблюдении Caveman имеет production churn на 14 строк больше и output на 786 токенов меньше. Это не статистический вывод о навыке и не сравнение завершённых двухшаговых траекторий.

Все три grader результата приняты, collection errors отсутствуют, три Sonar scan завершены и связаны с точными graded snapshots. Исходные raw suites содержат ошибки: на первых шагах baseline/Caveman 18 failed и 2 skipped; на втором шаге baseline 12 failed и 1 skipped. Решение grader учитывает обязательные F2P/P2P/N2P и stable classification; оно не означает прохождение всей raw suite.

Sonar maintainability issues и remediation effort остаются 282 и 1438 минут на трёх снимках. Cognitive complexity: baseline шаг 1 — 2391, baseline шаг 2 — 2405, Caveman шаг 1 — 2405. Raw Sonar включает различающийся inline test-код. Его aggregate deltas не доказывают ухудшение production-кода. Production LOC отдельно исключает тесты.

## Остановка и сохранённые ограничения

Snapshot квоты от 20 октября, 22:33 Europe/Zurich: primary 85%, secondary 15%. Ожидаемый reset primary — 21 октября около 02:55 Europe/Zurich. Это приблизительные общие лимиты аккаунта; перед продолжением нужен новый read. Первоначальная остановка при 85% сохранена в истории. Затем пользователь разрешил продолжение выше 85%: [execution override и recovery](phase5_quota_override.md). Ponytail был действительно запущен, но сервис отказал при primary 100%, secondary 17% с `rate_limit_reached`; это уже фактический предел доступа, а не локальный процентный gate. Незавершённый контейнер Caveman и его исходная сессия оставлены для диагностики; автоматического продолжения пока нет. Повторное использование уже занятых trial IDs запрещено. Для withheld второго шага Caveman реализован и протестирован отдельный recovery adapter, сохраняющий историю остановки; он пока не запускался. Частично выполненный первый шаг Ponytail этим adapter не поддерживается. Обе сессии и контейнеры сохранены для восстановления.

Неудачная преждевременная попытка Sonar для второго шага baseline сохранена в `results/trials/phase5_baseline_r01_s02/analysis_attempts/sonar_001`. Она остановилась до scan из-за ещё не сохранённого Git bundle. Повторный scan после завершения сборки артефактов успешен; эта попытка не была ошибкой модели или grader.

В диагностическом выводе процессов оказался временный project-scoped scanner token. После scan проверено его отсутствие в активных tokens: токен отозван. OAuth credentials и постоянные Sonar credentials не выводились; raw process arguments больше не используются для диагностики.

Проверен последовательный baseline. Полная матрица, mandatory Serena, plan dispatch на реальной модели и два повтора каждого варианта ещё не подтверждены.
