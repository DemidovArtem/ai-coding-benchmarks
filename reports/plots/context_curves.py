"""Render frozen mean curves with visible, authorized context-deviation annotations."""

import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
NOTE = 'Ponytail r02, шаг 6: по разрешению удалён один отвергнутый reasoning-элемент; контекст изменён.'


def annotated_footer(text, enabled):
    if enabled and text.startswith('Churn/Net') and 'Правка 6:' in text:
        return text + '\n' + NOTE
    return text


def main():
    from matplotlib.figure import Figure
    from reports.plots import mean_curves
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    deviations = [{'trial_id': r['trial_id'], **r['extension']['context_deviation']}
                  for r in rows if r.get('extension', {}).get('context_deviation')
                  and r['trial_state'] == 'finished' and not r['collection_errors']
                  and r['sonar'].get('analysis_ok') is True]
    original = Figure.text
    def text(figure, x, y, s, *args, **kwargs):
        return original(figure, x, y, annotated_footer(s, bool(deviations)), *args, **kwargs)
    # The renderer is frozen in the measured cohort; extend only its visible footer.
    with patch.object(Figure, 'text', text):
        mean_curves.main()
    path = ROOT / 'reports/plots/current_comparison.json'
    view = json.loads(path.read_text())
    view['context_deviations'] = deviations
    path.write_text(json.dumps(view, indent=2) + '\n')
    parameters_path = ROOT / 'reports/plots/run_parameters.json'
    parameters = json.loads(parameters_path.read_text())
    by_id = {r['trial_id']: r for r in rows}
    for item in parameters:
        deviation = by_id[item['trial_id']].get('extension', {}).get('context_deviation')
        if deviation:
            item.update(context_deviation=deviation, strict_history_continuation=False)
    parameters_path.write_text(json.dumps(parameters, indent=2) + '\n')
    path = ROOT / 'reports/plots/run_parameters.md'
    text = path.read_text()
    if deviations and NOTE not in text:
        path.write_text(text + '\n\n' + NOTE + ' [Протокол](../phase6f_ponytail_context_protocol.md).\n')


if __name__ == '__main__':
    main()
