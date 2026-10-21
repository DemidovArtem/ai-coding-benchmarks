"""Render paired experiment charts from a credential-free, versioned data snapshot.

Run with Matplotlib installed. --refresh-data reads the local canonical JSONL;
without it, the committed data.json is sufficient to reproduce the charts.
"""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COLORS = {'baseline': '#526474', 'caveman': '#8462b5', 'ponytail': '#148a87',
          'plan': '#cc8230', 'goal_plan': '#bb5373', 'serena': '#427ab6'}
NAMES = {'baseline': 'Baseline', 'caveman': 'Caveman', 'ponytail': 'Ponytail',
         'plan': 'Plan', 'goal_plan': 'Goal + plan', 'serena': 'Serena'}
PAIR_FIELDS = ('repo', 'milestone_id', 'repetition', 'starting_tree', 'dataset_version',
               'model', 'reasoning_effort', 'setup_fingerprint')
FOOTPRINT = ('added_prod_loc', 'deleted_prod_loc', 'net_prod_loc', 'churn_prod_loc')


def data_snapshot():
    source = ROOT / 'results/results.jsonl'
    records = []
    for line in source.read_text().splitlines():
        row = json.loads(line)
        saved = {key: row.get(key) for key in (
            'trial_id', 'variant', 'resolved', 'failure_category', 'collection_errors',
            'trial_state', 'measured_comparison', *PAIR_FIELDS, *FOOTPRINT)}
        saved['tokens'] = row['usage']['total']
        saved['durations'] = row['durations_seconds']
        saved['sonar'] = row['sonar'].get('metrics') if row['sonar'].get('analysis_ok') is True else None
        saved['continuous'] = {key: row.get('continuous', {}).get(key)
                               for key in ('trajectory_id', 'step', 'executor_session_id')}
        records.append(saved)
    snapshot = {'source': 'results/results.jsonl', 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'phase5_selection': json.loads((ROOT / 'reports/phase5_comparison.json').read_text()),
                'records': records}
    (HERE / 'data.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')


def verified(row):
    assert row['resolved'] is True and not row['collection_errors'] and not row['failure_category']
    assert row['sonar'] is not None


def paired(row, baseline):
    assert all(row.get(key) is not None and row[key] == baseline[key] for key in PAIR_FIELDS), row['trial_id']


def metrics(steps):
    for row in steps:
        verified(row)
    final = steps[-1]
    tokens = {key: sum(row['tokens'][key] for row in steps)
              for key in ('input_tokens', 'cached_input_tokens', 'output_tokens')}
    assert tokens['input_tokens'] >= tokens['cached_input_tokens']
    duration = sum(row['durations']['planner'] + row['durations']['executor'] for row in steps)
    return {**{key: final[key] for key in FOOTPRINT}, **tokens,
            'uncached_input_tokens': tokens['input_tokens'] - tokens['cached_input_tokens'],
            'model_seconds': duration, **final['sonar']}


def delta(value, baseline, percent):
    if value is None or baseline is None or percent and baseline == 0:
        return None
    return (value - baseline) / baseline * 100 if percent else value - baseline


def number(value, signed=False):
    if abs(value - round(value)) < 1e-8:
        return f'{value:+.0f}' if signed and value else f'{value:.0f}'
    return (f'{value:+.1f}' if signed else f'{value:.1f}').replace('.', ',')


def panel(ax, observations, metric, baselines):
    key, title, percent, unit = metric
    values = [None if item['metrics'] is None else delta(item['metrics'].get(key),
              baselines[item['rep']].get(key), percent) for item in observations]
    bound = max([abs(value) for value in values if value is not None] + [1]) * 1.7
    ax.set_xlim(-bound, bound)
    ax.axvline(0, color='#596773', linewidth=1, zorder=1)
    ax.xaxis.grid(True, color='#e3e8ec', linewidth=.7)
    ax.set_axisbelow(True)
    for y, (item, value) in enumerate(zip(observations, values)):
        if value is None:
            ax.text(.08 * bound, y, 'нет данных', color='#778590', va='center', ha='left', fontsize=9)
            continue
        ax.barh(y, value, height=.6, color=COLORS[item['variant']], alpha=1 if item['rep'] == 1 else .55, zorder=2)
        if value == 0:
            ax.plot(0, y, 'o', color=COLORS[item['variant']], markersize=4, zorder=3)
        ax.text(value + (.035 * bound if value >= 0 else -.035 * bound), y,
                number(value, True) + ('%' if percent else ''), va='center',
                ha='left' if value >= 0 else 'right', fontsize=9.5, color='#243645')
    ax.set_yticks(range(len(observations)), [item['label'] for item in observations])
    ax.set_ylim(len(observations) - .45, -.65)
    ax.set_title(title, loc='left', fontweight='medium', pad=12)
    refs = ' / '.join(number(baselines[rep][key]) for rep in sorted(baselines))
    ax.set_xlabel(f'Δ к baseline, {unit}\nBaseline {" / ".join(map(str, sorted(baselines)))}: {refs}', fontsize=9)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    for side in ('top', 'right', 'left'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#ccd5dd')
    ax.tick_params(axis='y', length=0)


def chart_grid(observations, baselines, measures, title, subtitle, footer):
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    for ax, measure in zip(axes.flat, measures):
        panel(ax, observations, measure, baselines)
    fig.suptitle(title, x=.04, ha='left', fontsize=18, fontweight='medium')
    fig.text(.04, .93, subtitle, fontsize=11, color='#526474')
    fig.text(.04, .025, footer, fontsize=10, color='#526474', va='bottom')
    fig.tight_layout(rect=(.02, .08, .99, .9), h_pad=2.3, w_pad=2.8)
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-data', action='store_true')
    args = parser.parse_args()
    if args.refresh_data:
        data_snapshot()
    snapshot = json.loads((HERE / 'data.json').read_text())
    rows = {row['trial_id']: row for row in snapshot['records']}
    assert len(rows) == len(snapshot['records'])
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10.5,
                         'axes.titlesize': 12, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    selection = snapshot['phase5_selection']['repetitions']
    trajectories, baselines = {}, {}
    for rep, variants in selection.items():
        for variant, details in variants.items():
            steps = [rows[trial] for trial in details['trial_ids']]
            assert [row['continuous']['step'] for row in steps] == [1, 2]
            assert steps[0]['continuous']['executor_session_id'] == steps[1]['continuous']['executor_session_id']
            for row in steps:
                paired(row, rows[variants['baseline']['trial_ids'][row['continuous']['step'] - 1]])
            trajectories[int(rep), variant] = steps
        baselines[int(rep)] = metrics(trajectories[int(rep), 'baseline'])
    completed = sum(map(len, trajectories.values()))
    assert completed == snapshot['phase5_selection']['completed_task_executions']
    assert len({steps[0]['continuous']['executor_session_id'] for steps in trajectories.values()}) == len(trajectories)
    observations = [{'variant': variant, 'rep': rep, 'label': f'{NAMES[variant]} · {rep}',
                     'metrics': metrics(trajectories[rep, variant]) if (rep, variant) in trajectories else None}
                    for variant in ('caveman', 'ponytail', 'plan') for rep in (1, 2)]
    measures = [('churn_prod_loc', 'Размер production-дифа', True, '%'),
                ('net_prod_loc', 'Чистый прирост production-кода', False, 'строки'),
                ('output_tokens', 'Output: planner + executor', True, '%'),
                ('input_tokens', 'Input, включая cached input', True, '%'),
                ('uncached_input_tokens', 'Input без cached input', True, '%'),
                ('model_seconds', 'Время: planner + executor', True, '%')]
    footer = ('Δ = подход − baseline; Δ% = 100 × Δ / baseline того же повтора. Меньше не обязательно лучше.\n'
              f'Завершено {completed}/16 правок; все приняты grader. Нет данных — незавершённый повтор, не ноль.')
    figures = [('phase5_deltas', chart_grid(observations, baselines, measures,
        'Continuous-пилот · дельты к baseline',
        'Две связанные правки. 1 и 2 — независимые повторы; их результаты показаны отдельно.', footer))]
    quality = [('ncloc', 'Sonar ncloc', False, 'строки'),
               ('complexity', 'Цикломатическая сложность', False, 'единицы'),
               ('cognitive_complexity', 'Когнитивная сложность', False, 'единицы'),
               ('software_quality_maintainability_issues', 'Maintainability issues', False, 'проблемы'),
               ('software_quality_maintainability_remediation_effort', 'Remediation effort', False, 'минуты оценки'),
               ('duplicated_lines', 'Дублирование', False, 'строки')]
    figures.append(('phase5_sonar', chart_grid(observations, baselines, quality,
        'Sonar · дельты финального снимка', 'Каждый подход сравнивается с baseline своего повтора.',
        'Sonar включает различающийся inline test-код; это не production-only оценка качества.\nRemediation effort — оценка анализатора, не измеренное время работы человека. Нулевые значения отмечены точками.')))
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharey='row')
    for column, rep in enumerate((1, 2)):
        for variant in ('baseline', 'caveman', 'ponytail', 'plan'):
            if (rep, variant) not in trajectories:
                continue
            steps = trajectories[rep, variant]
            style = {'baseline': '-o', 'caveman': '--s', 'ponytail': '-D', 'plan': ':^'}[variant]
            axes[0, column].plot([0, 1, 2], [0] + [row['churn_prod_loc'] for row in steps],
                style, color=COLORS[variant], label=NAMES[variant], linewidth=2)
            output = [row['tokens']['output_tokens'] for row in steps]
            axes[1, column].plot([0, 1, 2], [0, output[0], sum(output)], style,
                color=COLORS[variant], label=NAMES[variant], linewidth=2)
        for row, ylabel in ((0, 'Production churn, строки'), (1, 'Output с prep, токены')):
            ax = axes[row, column]
            ax.set_title(f'Повтор {rep}', loc='left')
            ax.set_xticks([0, 1, 2], ['Исходное', 'Правка 1', 'Правка 2'])
            ax.set_ylim(bottom=0)
            ax.set_ylabel(ylabel)
            ax.grid(True, color='#e3e8ec', linewidth=.7)
            ax.spines[['top', 'right']].set_visible(False)
            ax.legend(frameon=False, loc='upper left', fontsize=9)
    fig.suptitle('Накопление изменений в одном repository', x=.04, ha='left', fontsize=18, fontweight='medium')
    fig.text(.04, .93, 'Churn сравнивается с исходным commit. Output суммируется по завершённым шагам.', fontsize=11, color='#526474')
    fig.text(.04, .025, 'Две точки после исходного состояния не доказывают долгосрочный тренд. Показаны только завершённые траектории.', fontsize=10, color='#526474')
    fig.tight_layout(rect=(.02, .07, .99, .9), h_pad=2, w_pad=3)
    figures.append(('phase5_trajectories', fig))
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    for index, (phase, variants) in enumerate(((2, ('plan', 'goal_plan')), (3, ('ponytail', 'caveman', 'serena')))):
        baseline = rows[f'phase{phase}_baseline_001']
        obs = []
        for variant in variants:
            record = rows[f'phase{phase}_{variant}_001']
            paired(record, baseline)
            obs.append({'variant': variant, 'rep': 1, 'label': NAMES[variant], 'metrics': metrics([record])})
        for ax, measure in zip(axes[index], (measures[0], measures[2], quality[2])):
            panel(ax, obs, measure, {1: metrics([baseline])})
            ax.set_title(f'Phase {phase} · {measure[1]}', loc='left', fontsize=11)
    fig.suptitle('Прежние одношаговые trials · свой baseline для каждой фазы', x=.04, ha='left', fontsize=17, fontweight='medium')
    fig.text(.04, .93, 'Phase 2: планирование. Phase 3: навыки. Один trial на подход, без усреднения между фазами.', fontsize=11, color='#526474')
    fig.text(.04, .025, 'Serena: 0 measured MCP calls; её результат не показывает эффект реального использования Serena.\nSonar включает тесты. Все показанные trials приняты grader; небольшой пилот не даёт статистического рейтинга.', fontsize=10, color='#526474')
    fig.tight_layout(rect=(.02, .08, .99, .9), h_pad=2.3, w_pad=2.8)
    figures.append(('earlier_cohorts', fig))
    with PdfPages(HERE / 'comparison.pdf') as pdf:
        for name, fig in figures:
            fig.savefig(HERE / f'{name}.png', dpi=120, facecolor='white')
            fig.savefig(HERE / f'{name}.svg', facecolor='white')
            pdf.savefig(fig, facecolor='white')
            plt.close(fig)
    print(f'Rendered four figures and comparison.pdf; verified {completed} Phase 5 executions and all within-cohort pairs.')


if __name__ == '__main__':
    main()
