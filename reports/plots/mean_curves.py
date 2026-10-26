"""Render the primary mean curves; no model or benchmark execution."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from experiment.curves import aggregate
from reports.plots.current_view import comparison_view
from reports.plots.extension_view import append_fourth

COLORS={'baseline':'#526474','caveman':'#8462b5','ponytail':'#148a87','serena':'#c9802a'}
STYLES={'baseline':'-o','caveman':'--s','ponytail':'-D','serena':':^'}
NAMES={'baseline':'Baseline','caveman':'Caveman','ponytail':'Ponytail','serena':'Serena'}
MEASURES=[('output_tokens','Накопленный output','токены'),
          ('input_tokens','Накопленный input, включая cache','токены'),
          ('churn_prod_loc','Размер production-дифа','строки: добавлено + удалено'),
          ('net_prod_loc','Чистый прирост production-кода','строки: добавлено − удалено'),
          ('sonar_delta_cognitive_complexity','Когнитивная сложность','Δ к исходному Sonar'),
          ('sonar_delta_complexity','Цикломатическая сложность','Δ к исходному Sonar'),
          ('sonar_delta_software_quality_maintainability_issues','Maintainability issues','Δ числа проблем'),
          ('sonar_delta_duplicated_lines','Дублирование','Δ дублированных строк'),
          ('sonar_delta_software_quality_maintainability_remediation_effort','Remediation effort','Δ оценки Sonar, мин')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-data',action='store_true')
    args=parser.parse_args()
    if args.refresh_data:
        source=ROOT/'results/results.jsonl'
        # Linked extensions have no new independent prefix; append them explicitly below.
        rows=[json.loads(line) for line in source.read_text().splitlines() if line.strip()]
        data=aggregate([row for row in rows if not row.get('extension')])
        data['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
        (HERE/'mean_data.json').write_text(json.dumps(data,indent=2)+'\n')
    data=json.loads((HERE/'mean_data.json').read_text())
    cohorts=sorted({p['setup_fingerprint'] for p in data['points']})
    if not cohorts:raise ValueError('No completed measured points to plot')
    combined=comparison_view(data,json.loads((ROOT/'reports/phase6c_experiment.json').read_text()),
                             json.loads((ROOT/'reports/phase6_experiment.json').read_text()))
    combined=append_fourth(combined,[json.loads(line) for line in (ROOT/'results/results.jsonl').read_text().splitlines() if line.strip()])
    (HERE/'current_comparison.json').write_text(json.dumps(combined,indent=2)+'\n')
    views=([(None,combined['points'],list(NAMES))] if combined['points'] else [])
    for cohort in cohorts:
        points=[p for p in data['points'] if p['setup_fingerprint']==cohort]
        variants=list(NAMES) if any(p['variant']=='serena' for p in points) else ['baseline','caveman','ponytail']
        views.append((cohort,points,variants))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'svg.fonttype':'none'})
    with PdfPages(HERE/'mean_comparison.pdf') as pdf:
        for cohort,points,variants in views:
            for paired in ((False,) if cohort is None else (False,True)):
                fig,axes=plt.subplots(3,3,figsize=(15,11))
                for ax,(metric,title,unit) in zip(axes.flat,MEASURES):
                    ax.axhline(0,color='#9ba9b5',linewidth=.8)
                    observed=False
                    for variant in variants:
                        values=sorted([p for p in points if p['variant']==variant],key=lambda p:p['step'])
                        field='paired_delta' if paired else 'metrics'
                        values=[p for p in values if p[field][metric]['mean'] is not None]
                        if not values:
                            ax.plot([],[],STYLES[variant],color=COLORS[variant],label=NAMES[variant]+' · нет данных')
                            continue
                        observed=True
                        x=[0]+[p['step'] for p in values]
                        stats=[{'mean':0,'min':0,'max':0,'n':0}]+[p[field][metric] for p in values]
                        label=f"{NAMES[variant]} · n={values[-1][field][metric]['n']}"
                        ax.plot(x,[s['mean'] for s in stats],STYLES[variant],color=COLORS[variant],linewidth=2,label=label)
                        ax.fill_between(x,[s['min'] for s in stats],[s['max'] for s in stats],color=COLORS[variant],alpha=.12)
                    ax.set_title(title,loc='left',fontsize=11)
                    ax.set_xlabel('Количество правок')
                    axis_unit=unit
                    if paired:
                        axis_unit='строки' if metric in ('churn_prod_loc','net_prod_loc') else unit.replace('Δ к исходному Sonar','единицы')
                    ax.set_ylabel(axis_unit,fontsize=9)
                    ax.set_xticks(range(max(p['step'] for p in points)+1))
                    ax.grid(True,color='#e1e7ec',linewidth=.6)
                    ax.spines[['top','right']].set_visible(False)
                    ax.legend(frameon=False,fontsize=8,loc='best')
                    if not observed:
                        ax.text(.5,.35,'Нет завершённых пар' if paired else 'Нет измерений',
                                transform=ax.transAxes,ha='center',color='#526474',fontsize=10)
                    if all(abs(value)<1e-12 for line in ax.lines for value in line.get_ydata()):
                        ax.set_ylim(-1,1);ax.set_yticks([0])
                title='Средние изменения по правкам' if not paired else 'Средние парные дельты к baseline по правкам'
                fig.suptitle(title,x=.035,ha='left',fontsize=19,fontweight='medium')
                subtitle='Линия — среднее повторов; полоса — min–max. n — число наблюдений в последней точке.'
                fig.text(.035,.936,subtitle+(' Один cohort.' if cohort else ' Продолжения связаны с исходными траекториями.'),fontsize=10,color='#526474')
                provenance=('Serena: исходный runtime; остальные: offline-сборка с тем же Codex 0.163.0. Средние каждой линии сохранены.'
                            if cohort is None else 'Правка 0 — исходная точка отсчёта. Мало повторов; полосы не являются доверительным интервалом. Cohort: '+cohort[:12])
                if cohort is None and combined.get('extension_sources'):
                    provenance='Правка 4: отдельный протокол grader с pruning. Serena — исходная submission; остальные — восстановленная история.'
                fig.text(.035,.028,'Churn/Net сравниваются с началом траектории; токены накапливаются. Sonar включает тесты и маскирование.\n'
                         +provenance,fontsize=9,color='#526474')
                fig.tight_layout(rect=(.015,.08,.99,.915),h_pad=2,w_pad=2)
                suffix='mean_deltas' if paired else 'mean_curves'
                extra='_current' if cohort is None else '_'+cohort[:8] if len(cohorts)>1 or combined['points'] else ''
                fig.savefig(HERE/(suffix+extra+'.png'),dpi=120,facecolor='white')
                svg=HERE/(suffix+extra+'.svg')
                fig.savefig(svg,facecolor='white')
                svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
                if cohort is None:
                    (HERE/'mean_curves.png').write_bytes((HERE/(suffix+extra+'.png')).read_bytes())
                    (HERE/'mean_curves.svg').write_bytes(svg.read_bytes())
                pdf.savefig(fig,facecolor='white');plt.close(fig)
    print('Mean curves rendered:',len(views),'views from',len(cohorts),'source cohorts.')


if __name__=='__main__':main()
