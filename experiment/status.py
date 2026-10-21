"""Refresh the human-readable experiment register from saved results and live metadata."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def cell(value):
    if value is None:
        return '—'
    if isinstance(value, float):
        return f'{value:.1f}'
    if type(value) is int:
        return f'{value:,}'.replace(',', ' ')
    return str(value).replace('|', '\\|').replace('\n', ' ')


def trial_status(row):
    if row.get('failure_category') or row.get('collection_errors') or row.get('trial_state') == 'failed':
        return 'Ошибка; результат сохранён'
    if row.get('trial_state') == 'running':
        return 'Выполняется'
    if row.get('resolved') is True:
        return 'Завершён; grader принят'
    if row.get('resolved') is False:
        return 'Завершён; grader не принят'
    return 'Результат ещё не собран'


def phase_status(rows, expected):
    variants = {r.get('variant') for r in rows}
    if expected <= variants and all(r.get('resolved') is True and not r.get('failure_category') and not r.get('collection_errors') for r in rows):
        return 'Завершён'
    if any(r.get('trial_state') == 'running' for r in rows):
        return 'Выполняется'
    return 'Частично выполнен' if rows else 'Ещё не запускался'


def render(rows, pending, continuous, updated, serena_required=None):
    p2 = [r for r in rows if r['trial_id'].startswith('phase2_')]
    p3 = [r for r in rows if r['trial_id'].startswith('phase3_')]
    active = [r for r in pending if r.get('trial_state') == 'running']
    snapshots = [r for r in rows if r.get('snapshot_sha256')]
    quota_note = ('Для Phase 5 пользователь разрешил продолжение выше 85%; явный отказ сервиса по квоте по-прежнему останавливает запуск. '
                  '[Разрешённое изменение](reports/phase5_quota_override.md).'
                  if continuous.get('quota_override') else 'Новые model trials требуют fresh quota check ниже 85% в обоих окнах.')
    summaries = [r.get('grader_metrics',{}).get('test_summary',{}) for r in rows]
    grade_note = 'Подробные F2P/P2P/N2P, failures и skipped сохранены в canonical grader records.'
    fields = ('fail_to_pass_achieved','fail_to_pass_required','pass_to_pass_achieved','pass_to_pass_required','none_to_pass_achieved','none_to_pass_required','failed','skipped')
    values = {tuple(summary.get(key) for key in fields) for summary in summaries}
    if len(values) == 1 and all(value is not None for value in next(iter(values))):
        f2p, f2p_total, p2p, p2p_total, n2p, n2p_total, failed, skipped = next(iter(values))
        grade_note = f'У {len(rows)} собранных trials: F2P {f2p}/{f2p_total}, P2P {p2p}/{p2p_total}, N2P {n2p}/{n2p_total}; raw suite: failures {failed}, skipped {skipped}.'
    lines = ['# Эксперименты: результаты и текущий статус', '',
             f'Обновлено: **{updated}**, Europe/Zurich. Это основной живой реестр проекта.', '',
             'Источник чисел — сохранённые grader/Git/usage/Sonar records. Документ обновляется после запуска, завершения, ошибки или изменения плана. Промежуточный trial не получает вымышленный результат; «—» означает, что данных нет.', '',
             '## Этапы и предстоящая работа', '',
             '| Этап | Статус | Что готово / что осталось |', '| --- | --- | --- |',
             '| Подготовка и OAuth smoke | Проверены; исторические доказательства сохранены | [Аудит среды](environment_report.md), [actual grader smoke](reports/phase1_smoke.md) |',
             f"| Phase 2: baseline / plan / goal_plan | {phase_status(p2 + [r for r in pending if r['trial_id'].startswith('phase2_')], {'baseline','plan','goal_plan'})} | [Метрики и quota-resume history](reports/phase2_progress.md) |",
             f"| Phase 3: baseline / Ponytail / Caveman / Serena | {phase_status(p3 + [r for r in pending if r['trial_id'].startswith('phase3_')], {'baseline','ponytail','caveman','serena'})} | [Профили, активация и результаты](reports/phase3_progress.md) |",
             *([f"| Дополнение: serena_required | {cell(serena_required.get('label'))} | [Обязательный Serena-first workflow](reports/serena_required_progress.md); отдельный measured trial ещё не выполнен |"] if serena_required else []),
             f"| Phase 4: Sonar before/after | {'Завершён для собранных snapshots' if snapshots and all(r.get('sonar',{}).get('analysis_ok') is True for r in snapshots) else 'Частично выполнен / ожидает анализов'} | [Общая база и solution snapshots](reports/sonar_pilot.md); raw inline tests ограничивают сравнение |",
             f"| Phase 5: continuous, 2 связанных milestone | {cell(continuous.get('label') or ('Отложен; не реализован' if continuous.get('status') == 'explicitly_deferred_engineering_integration_not_implemented' else continuous.get('status')))} | {cell(continuous.get('summary') or 'Нужен prep/dispatch/ack barrier; оценка 3–5 инженерных дней.')} [План и состояние](reports/continuous_feasibility.md) |",
             '| Phase 6: больший repo / повторы / full chain | Не запускался; отдельное согласование | Сначала определить scope, проверить квоту и бюджет новых образов/диска |', '',
             '## Корректность и размер production patch', '',
             'Каждая строка — отдельный trial или шаг continuous. Сравнивать с baseline внутри того же frozen cohort и повтора; Phase 2/3/5 не смешивать. Шаги одной траектории зависимы. Smoke не входит в A/B. «Grader принят» не означает, что вся raw test suite прошла.', '',
             '| Trial / cohort | Variant | Статус | + строк | − строк | Net | Churn | Изменено prod-файлов |',
             '| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in rows + pending:
        values = [r['trial_id'], r.get('variant'), trial_status(r), *[r.get(k) for k in ('added_prod_loc','deleted_prod_loc','net_prod_loc','churn_prod_loc','changed_prod_files')]]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    lines += ['', 'Net = добавлено − удалено; churn = добавлено + удалено. Тесты/generated/vendor и inline Rust tests исключены из production LOC. Полные raw grader decisions, new/deleted/renamed files и cumulative LOC сохранены в JSONL.', '',
              '## Токены и время', '',
              'Input уже включает cached input: эти столбцы не складывать. Planning variants учитывают prep + executor. Это токены подписки, не сумма денег и не точная стоимость квоты.', '',
              '| Trial | Input | Cached input | Output, prep + executor | Prep, с | Executor, с | Grader, с | Sonar, с | Trial всего, с |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in rows + pending:
        usage = r.get('usage',{}).get('total',{}); duration = r.get('durations_seconds',{})
        values = [r['trial_id'], *[usage.get(k) for k in ('input_tokens','cached_input_tokens','output_tokens')], *[duration.get(k) for k in ('planner','executor','evaluation','sonar')], r.get('duration_seconds')]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    lines += ['', 'Trial total включает setup и служебные операции; Sonar выполняется отдельно. Goal_plan продолжен после quota pause: active time указан без всей паузы, полное wall time есть в JSON. Время описательное: host postprocessing частично пересекался с setup следующего trial.', '',
              '## Sonar и использование навыков', '',
              'Sonar измеряет raw graded snapshot, включая различающийся inline test-код. Поэтому эти значения не доказывают production-only эффект или качество архитектуры. ncloc — строки кода без комментариев и пустых строк; cognitive complexity — статическая оценка сложности ветвлений. Remediation — оценка Sonar в минутах, не время человеческого review.', '',
              '| Trial | Sonar | ncloc | Cognitive complexity | Maintainability issues | Remediation, мин | Natural MCP calls | Memories после |',
              '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in rows + pending:
        sonar = r.get('sonar',{}); ok = sonar.get('analysis_ok'); metrics = sonar.get('metrics') or {}; state = r.get('skill_state') or {}
        values = [r['trial_id'], 'Готов' if ok is True else 'Ошибка' if ok is False else 'Не выполнен', *[metrics.get(k) if ok is True else None for k in ('ncloc','cognitive_complexity','software_quality_maintainability_issues','software_quality_maintainability_remediation_effort')], state.get('natural_mcp_tool_calls'), state.get('memory_files_after')]
        lines.append('| ' + ' | '.join(map(cell, values)) + ' |')
    lines += ['', grade_note + ' F2P — исправленные обязательные проверки, P2P — сохранённые проходившие проверки, N2P — новые проверки. Snapshot/collection failures отражаются в статусах. Native-hook audit и отдельный MCP smoke проверяют активацию, а natural usage показывает фактическое использование. Активационные smokes и их неуспешные попытки — setup overhead, не task A/B.', '',
              f"Несобранных trials: **{len(pending)}**, из них выполняется: **{len(active)}**. {quota_note} Этот документ сам ничего не запускает и не следит по расписанию.", '',
              '## Как обновляется реестр', '',
              'После изменения результатов или статуса выполняется `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status`. Команда читает `results/results.jsonl`, metadata ещё не собранных trials и continuous plan. Завершённые результаты сначала проходят существующий collector; таблица не заменяет grader и не пересчитывает scores.', '',
              '[Графики дельт](reports/plots/README.md) · [Итоговый pilot report](reports/pilot_report.md) · [Состояние требований](reports/implementation_status.md) · [CSV](results/results.csv) · [JSONL](results/results.jsonl) · [SonarQube локально](http://127.0.0.1:9000)', '']
    if continuous.get('pilot_runs'):
        table = ['## Последовательный пилот: план запусков', '',
                 'Одна траектория = две связанные правки в одной сессии. Повторы начинают новую сессию. Метрики каждого шага приведены выше; сравнение с Phase 2/3 не смешивается.', '',
                 '| Траектория | Variant | Повтор | Завершено шагов | Статус |', '| --- | --- | ---: | --- | --- |']
        states = {'planned':'Запланирован', 'waiting_quota':'Ожидает квоты', 'blocked_quarantine':'Заблокирован: quarantine', 'running':'Выполняется', 'finished':'Завершён', 'failed':'Ошибка; данные сохранены'}
        for run in continuous['pilot_runs']:
            state = 'Остановлен: квота' if run.get('failure_category') == 'quota_pressure' else states.get(run['state'], run['state'])
            values = [run['trial_id'], run['variant'], run['repetition'],
                      str(run['completed_steps']) + '/' + str(run['total_steps']), state]
            table.append('| ' + ' | '.join(map(cell, values)) + ' |')
        position = lines.index('## Корректность и размер production patch')
        lines[position:position] = table + ['', '[Протокол последовательного пилота](reports/phase5_protocol.md) · [Промежуточные результаты](reports/phase5_progress.md)', '']
    return '\n'.join(lines)


def main():
    rows = [json.loads(line) for line in (ROOT/'results/results.jsonl').read_text().splitlines() if line.strip()]
    known = {r['trial_id'] for r in rows}; pending = {}
    config = json.loads((ROOT/'experiment.yaml').read_text())
    for directory in (Path(config['resources']['runtime_root']), ROOT/'results/trials'):
        for path in directory.glob('*/run_metadata.json'):
            row = json.loads(path.read_text()); trial = path.parent.name
            if trial not in known and row.get('phase') == 'trial':
                pending[trial] = {**row, 'trial_id':trial, 'trial_state':row.get('state')}
    continuous = json.loads((ROOT/'reports/continuous_feasibility.json').read_text())
    updated = datetime.now(ZoneInfo('Europe/Zurich')).strftime('%Y-%m-%d %H:%M:%S')
    required=ROOT/'reports/serena_required_progress.json'
    required=json.loads(required.read_text()) if required.exists() else None
    (ROOT/'EXPERIMENT_STATUS.md').write_text(render(rows, list(pending.values()), continuous, updated, required))
    print('Updated EXPERIMENT_STATUS.md')


if __name__ == '__main__':
    main()
