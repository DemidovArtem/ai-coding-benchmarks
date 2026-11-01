"""Redraw the public continuous results from tracked JSON, without a model or Docker."""

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
MEASURES = [
    ('output_tokens', 'Cumulative output', 'tokens'),
    ('input_tokens', 'Cumulative input (includes cache)', 'tokens'),
    ('churn_prod_loc', 'Production diff: added + deleted', 'lines'),
    ('net_prod_loc', 'Production code growth', 'lines'),
    ('sonar_delta_cognitive_complexity', 'Cognitive complexity', 'delta to initial scan'),
    ('sonar_delta_complexity', 'Cyclomatic complexity', 'delta to initial scan'),
    ('sonar_delta_software_quality_maintainability_issues', 'Maintainability issues', 'delta to initial scan'),
    ('sonar_delta_duplicated_lines', 'Duplicated lines', 'delta to initial scan'),
    ('sonar_delta_software_quality_maintainability_remediation_effort', 'Remediation estimate', 'delta, analyzer minutes'),
]
METHODS = {'baseline': ('Baseline', '#526474', '-o'),
           'caveman': ('Caveman', '#8462b5', '--s'),
           'ponytail': ('Ponytail', '#148a87', '-D'),
           'serena': ('Serena', '#c9802a', ':^')}


def main():
    data = json.loads((ROOT / 'reports/plots/current_comparison.json').read_text())
    points = data['points']
    keys = [(point['variant'], point['step']) for point in points]
    assert points and len(keys) == len(set(keys)), 'Missing or duplicate method/step observations'
    assert set(method for method, _ in keys) == set(METHODS), 'Unexpected displayed methods'
    steps = sorted({point['step'] for point in points})
    assert steps == list(range(1, max(steps) + 1)), 'Non-contiguous task steps'
    assert all((method, step) in keys for method in METHODS for step in steps), 'Incomplete method prefix'
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(3, 3, figsize=(15, 11))
    for ax, (metric, title, unit) in zip(axes.flat, MEASURES):
        ax.axhline(0, color='#9ba9b5', linewidth=.8)
        for method, (name, color, style) in METHODS.items():
            selected = sorted((p for p in points if p['variant'] == method), key=lambda p: p['step'])
            observed = [p for p in selected if p['metrics'][metric]['mean'] is not None]
            if not observed:
                continue
            stats = [p['metrics'][metric] for p in observed]
            assert all(s['n'] > 0 and s['min'] <= s['mean'] <= s['max'] for s in stats), 'Invalid summary range'
            x = [0] + [p['step'] for p in observed]
            ax.plot(x, [0] + [s['mean'] for s in stats], style, color=color, linewidth=2,
                    label=f"{name} (n={stats[-1]['n']})")
            ax.fill_between(x, [0] + [s['min'] for s in stats], [0] + [s['max'] for s in stats], color=color, alpha=.12)
        ax.set(title=title, xlabel='Sequential changes', ylabel=unit, xticks=[0] + steps)
        ax.grid(True, color='#e1e7ec', linewidth=.6)
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(frameon=False, fontsize=8)
        if all(all(value == 0 for value in line.get_ydata()) for line in ax.lines):
            ax.set(ylim=(-1, 1), yticks=[0])
    fig.suptitle('Agent configurations over sequential changes', x=.035, ha='left', fontsize=19)
    fig.text(.035, .937, 'Means across independent trajectories; shading is min–max, not a confidence interval. Zero is the initial reference.', fontsize=10)
    notes = [
        'Tokens accumulate. Churn/net compare with initial source. Sonar includes inline tests and benchmark masking.',
        'Descriptive overlay: Serena uses the original runtime; other methods use its offline rebuild. Frozen cohorts are not pooled.',
        'Grading adaptations and invalid fifth-step scores are documented in docs/RESULTS.md. These are not success-rate curves.',
    ]
    if data.get('context_deviations'):
        notes.append('Ponytail r02, step 6: one API-rejected reasoning item removed from a checkpoint copy; context amended.')
    fig.text(.035, .018, '\n'.join(notes), fontsize=9, color='#526474')
    fig.tight_layout(rect=(.015, .105, .99, .92), h_pad=2, w_pad=2)
    target = ROOT / 'docs/figures'
    target.mkdir(parents=True, exist_ok=True)
    fig.savefig(target / 'continuous_results.png', dpi=120, facecolor='white')
    svg = target / 'continuous_results.svg'
    fig.savefig(svg, facecolor='white')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)
    print(f'Rendered {len(points)} method/step means from tracked data; no model calls.')


if __name__ == '__main__':
    main()
