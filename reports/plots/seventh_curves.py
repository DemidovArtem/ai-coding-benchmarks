"""Render seventh-step extensions while preserving the frozen six-step observations."""

import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def annotated_footer(text, ready):
    if ready and text.startswith('Churn/Net') and 'Правка 6:' in text:
        return text + '\nПравка 7: исходная SWE JSON replacement; Printer Cleanup отложен до выполнения Strong dependency.'
    return text


def main():
    from matplotlib.figure import Figure
    from reports.plots import mean_curves, context_curves
    from reports.plots.seventh_view import append_seventh
    rows = [json.loads(line) for line in (ROOT / 'results/results.jsonl').read_text().splitlines() if line.strip()]
    ready = any((r.get('continuous') or {}).get('step') == 7 and r['trial_state'] == 'finished'
                and not r['collection_errors'] and r['sonar'].get('analysis_ok') is True for r in rows)
    original = Figure.text
    def text(figure, x, y, s, *args, **kwargs):
        return original(figure, x, y, annotated_footer(s, ready), *args, **kwargs)
    with patch.object(mean_curves, 'append_fourth', append_seventh), patch.object(Figure, 'text', text):
        context_curves.main()


if __name__ == '__main__':
    main()
