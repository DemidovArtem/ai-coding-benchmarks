# Параметры отдельных запусков

Измеряемые условия внутри одного setup fingerprint фиксированы. Меняются случайный результат модели, независимая сессия и наблюдаемая квота. Повторы усредняются; условия не усредняются. Полные безопасные значения — в [JSON](run_parameters.json).

| Trial | Вариант | Повтор / шаг | Model / effort | Cohort | Статус |
| --- | --- | --- | --- | --- | --- |
| phase5_baseline_r01_s01 | baseline | 1 / 1 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_baseline_r01_s02 | baseline | 1 / 2 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_caveman_r01_s01 | caveman | 1 / 1 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_caveman_r01_s02 | caveman | 1 / 2 | gpt-6.1-sol / high | b9bf8525af17 | failed / resolved=None |
| phase5_ponytail_r01_s01 | ponytail | 1 / 1 | gpt-6.1-sol / high | b9bf8525af17 | failed / resolved=None |
| phase5_caveman_r01_s02_resume02 | caveman | 1 / 2 | gpt-6.1-sol / high | b9bf8525af17 | failed / resolved=None |
| phase5_caveman_r01_s02_resume03 | caveman | 1 / 2 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_ponytail_r01_retry01_s01 | ponytail | 1 / 1 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_ponytail_r01_retry01_s02 | ponytail | 1 / 2 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_plan_r01_retry01_s01 | plan | 1 / 1 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_plan_r01_retry01_s02 | plan | 1 / 2 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_baseline_r02_s01 | baseline | 2 / 1 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_baseline_r02_s02 | baseline | 2 / 2 | gpt-6.1-sol / high | b9bf8525af17 | failed / resolved=None |
| phase5_baseline_r02_s02_resume01 | baseline | 2 / 2 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_caveman_r02_s01 | caveman | 2 / 1 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_caveman_r02_s02 | caveman | 2 / 2 | gpt-6.1-sol / high | b9bf8525af17 | finished / resolved=True |
| phase5_ponytail_r02_s01 | ponytail | 2 / 1 | gpt-6.1-sol / high | b9bf8525af17 | failed / resolved=None |
| phase5b_ponytail_r02_s01 | ponytail | 2 / 1 | gpt-6.1-sol / high | a9f194e85949 | failed / resolved=None |
| phase6_serena_r01_s01 | serena | 1 / 1 | gpt-6.1-sol / high | 5b12ad30f6f6 | finished / resolved=True |
| phase6_serena_r01_s02 | serena | 1 / 2 | gpt-6.1-sol / high | 5b12ad30f6f6 | finished / resolved=True |
| phase6_serena_r01_s03 | serena | 1 / 3 | gpt-6.1-sol / high | 5b12ad30f6f6 | failed / resolved=None |
| phase6_serena_r01_s03_retry01 | serena | 1 / 3 | gpt-6.1-sol / high | 5b12ad30f6f6 | finished / resolved=False |
| phase6_serena_r01_s04 | serena | 1 / 4 | gpt-6.1-sol / high | 5b12ad30f6f6 | failed / resolved=False |
| phase5_plan_r01_s01 | plan | 1 / 1 | gpt-6.1-sol / high | b9bf8525af17 | failed / resolved=None |
| phase6b_baseline_r01_s01 | baseline | 1 / 1 | gpt-6.1-sol / high | c53820c8b7c3 | failed / resolved=None |
| phase6c_baseline_r01_s01 | baseline | 1 / 1 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_baseline_r01_s02 | baseline | 1 / 2 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_baseline_r01_s03 | baseline | 1 / 3 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=False |
| phase6c_caveman_r01_s01 | caveman | 1 / 1 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_caveman_r01_s02 | caveman | 1 / 2 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_caveman_r01_s03 | caveman | 1 / 3 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=False |
| phase6c_ponytail_r01_s01 | ponytail | 1 / 1 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_ponytail_r01_s02 | ponytail | 1 / 2 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_ponytail_r01_s03 | ponytail | 1 / 3 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=False |
| phase6c_baseline_r02_s01 | baseline | 2 / 1 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_baseline_r02_s02 | baseline | 2 / 2 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_baseline_r02_s03 | baseline | 2 / 3 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=False |
| phase6c_caveman_r02_s01 | caveman | 2 / 1 | gpt-6.1-sol / high | e6a3c102dc4c | failed / resolved=None |
| phase6c_caveman_r02_retry01_s01 | caveman | 2 / 1 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_caveman_r02_retry01_s02 | caveman | 2 / 2 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=True |
| phase6c_caveman_r02_retry01_s03 | caveman | 2 / 3 | gpt-6.1-sol / high | e6a3c102dc4c | finished / resolved=False |

Смена условий: исходный Phase 5 использует прежнюю registry policy. Phase 5b добавляет Fastly deny ranges и explicit runtime binding; в нём нет завершённых measured trials. Старые quota failures и recovery attempts сохранены. Plan отменён для новых запусков по запросу пользователя.

Для каждого исходного measured trial CLI 0.163.0, model gpt-6.1-sol, effort high и общий runtime зафиксированы в frozen configs. Нулевые/отсутствующие поля в JSON не подменяются текущими настройками host.

Phase 6 использует прежний model/runtime и усиленную registry policy, но новый scope: четыре workflows и пять задач, два независимых круга. Serena cold memories создаются заново в каждом круге, warm memories сохраняются между задачами. Перезапуск grader второго шага после перезагрузки хоста зафиксирован отдельно; inference не повторялся.

Phase 6b заморожен отдельно: включён существующий upstream source-residue pruning, after-context заменён совместимыми maintenance fixes, timeout quota observation повторяется один раз. Model/CLI/runtime/Sonar/quarantine прежние. Phase 6 и Phase 6b не усредняются вместе. [Новый протокол](../phase6b_protocol.md).

Phase 6c использует первые три задачи Phase 6, baseline/Caveman/Ponytail и два независимых круга. Serena сохранена без новых запусков. Все новые workflows используют один offline runtime с тем же Codex 0.163.0, но новым image ID; grader работает в исходном режиме без pruning override. Поэтому setup fingerprint `e6a3c102dc4c` отделён от старых cohorts. [Текущий протокол](../phase6c_protocol.md).

Основной рисунок теперь показывает четыре подхода вместе по одинаковым первым трём задачам. Serena сохраняет свой исходный runtime/cohort; остальные — новый offline runtime. Расчёт средних каждой линии и исходные данные групп сохранены. [Общий вид и provenance](current_comparison.json).
