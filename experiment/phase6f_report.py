"""Refresh sixth-step reports from collected records; never invoke a model."""

import copy
import json
from pathlib import Path
import statistics

from experiment.runner import ROOT, save
from experiment.status import main as refresh_status


def main():
    rows=[json.loads(line) for line in (ROOT/'results/results.jsonl').read_text().splitlines() if line.strip()]
    attempts=[r for r in rows if r['trial_id'].startswith('phase6f_')]
    finished=[r for r in attempts if r['trial_state']=='finished' and not r['collection_errors']
              and r['sonar'].get('analysis_ok') is True]
    means=[]
    for variant in ('baseline','caveman','ponytail','serena'):
        group=[r for r in finished if r['variant']==variant]
        if group:
            means.append({'variant':variant,'n':len(group),
                'output_tokens':statistics.mean(r['usage']['executor_cumulative']['output_tokens'] for r in group),
                'production_churn':statistics.mean(r['churn_prod_loc'] for r in group),
                'sonar_delta_cognitive_complexity':statistics.mean(r['sonar']['delta_vs_common_base']['cognitive_complexity'] for r in group)})
    save(ROOT/'reports/phase6f_progress.json',{'task':'milestone_seed_a6e0be3_1_sub-01','completed':len(finished),
        'planned':7,'means_after_six_edits':means,
        'trials':[{'trial_id':r['trial_id'],'state':r['trial_state'],'grading_state':r.get('grading_state'),
                   'source_trial':r.get('extension',{}).get('parent_trial'),
                   'collection_errors':r['collection_errors'],'sonar':r['sonar'].get('analysis_ok')} for r in attempts]})
    lines=['# Phase 6f: исходная шестая правка SWE','',
        f'Собрано {len(finished)}/7 шестых шагов. Задача: max_matches searcher migration (`milestone_seed_a6e0be3_1_sub-01`). '
        'Это продолжения прежних пяти правок: первый круг baseline/Caveman/Ponytail/Serena, затем второй круг трёх первых методов. '
        'Serena выполняется только один раз по уточнению пользователя. Первые пять задач не переигрываются.','',
        '| Подход | n | Output за 6 правок | Production churn | Δ cognitive complexity |',
        '| --- | ---: | ---: | ---: | ---: |']
    for r in means:
        lines.append(f"| {r['variant']} | {r['n']} | {r['output_tokens']:g} | {r['production_churn']:g} | {r['sonar_delta_cognitive_complexity']:g} |")
    lines+=['','| Trial | Модель и сбор | Grader | Sonar |','| --- | --- | --- | --- |']
    for r in attempts:
        grade=r.get('grading_state',{})
        label=(f"Raw resolved={r['resolved']}" if grade.get('valid') else 'Недействителен / не завершён')
        lines.append(f"| {r['trial_id']} | {r['trial_state']} | {label} | {r['sonar'].get('analysis_ok')} |")
    lines+=['','Шестая исходная SWE-задача добавляет `SearcherBuilder::max_matches`. Grader выполняется без изменений. '
        'Пятые test scores остаются недействительными; шестая оценка не переписывает прошлые результаты.','',
        'Средние считаются по независимым повторам на том же шаге. Output накапливается; churn измеряется к исходному commit. '
        'Sonar включает inline tests. Runtime/cohort provenance и history transport сохраняются; сравнение описательное. '
        'Memories Serena сохраняются в её собственной траектории. Седьмой шаг не запускается.','',
        '[График](plots/mean_curves_current.png) · [Параметры](plots/run_parameters.md) · [Протокол](phase6f_protocol.md) · [Реестр](../EXPERIMENT_STATUS.md)','']
    (ROOT/'reports/phase6f_progress.md').write_text('\n'.join(lines))
    path=ROOT/'reports/plots/run_parameters.json'
    parameters=json.loads(path.read_text())
    by_id={r['trial_id']:r for r in parameters}
    for row in attempts:
        link=row['extension'];parent=by_id[link['parent_trial']]
        directory=Path(row['artifacts_path'])
        config=json.loads((directory/'experiment.json').read_text())
        metadata=json.loads((directory/'run_metadata.json').read_text())
        item=copy.deepcopy(parent)
        item.update(trial_id=row['trial_id'],step=6,state=row['trial_state'],resolved=row['resolved'],
            setup_fingerprint=row['setup_fingerprint'],image_id=config['benchmark']['skill_runtime_image_id'],
            snapshot_sha256=row['snapshot_sha256'],quota_before=row['quota']['before'],resume=row['resume'],
            started_at=metadata['started_at'],failure_category=row['failure_category'],
            parent_trial=link['parent_trial'],new_inference_executed=True,usage_origin_trial=row['trial_id'],
            profile_config_sha256=row['effective_profile']['config_sha256'],
            selected_milestones=config['benchmark']['continuous_pilot']['milestones'],
            grading_policy=config['benchmark']['grading_policy'],grading_state=row.get('grading_state'),
            history_transport=link['history_restore']['transport'])
        item.pop('assessment_implementation_commit',None)
        if row['trial_id'] in by_id:
            parameters[parameters.index(by_id[row['trial_id']])]=item
        else:parameters.append(item)
        by_id[row['trial_id']]=item
    save(path,parameters)
    path=ROOT/'reports/plots/run_parameters.md'
    text=path.read_text();head,tail=text.split('\n\nСмена условий:',1)
    head='\n'.join(line for line in head.splitlines() if not line.startswith('| phase6f_'))
    for item in parameters:
        if item['trial_id'].startswith('phase6f_'):
            head+=f"\n| {item['trial_id']} | {item['variant']} | {item['repetition']} / 6 | {item['model']} / {item['effort']} | {item['setup_fingerprint'][:12]} | {item['state']} / grading valid={item.get('grading_state',{}).get('valid')} |"
    text=head+'\n\nСмена условий:'+tail
    if 'Phase 6f продолжает исходной шестой' not in text:
        text+='\n\nPhase 6f продолжает исходной шестой задачей max_matches searcher migration. Семь model turns из пятых checkpoints; Serena один раз. Grader выполняется без изменений; при инфраструктурной ошибке очередь останавливается. [Протокол](../phase6f_protocol.md).\n'
    path.write_text(text)
    refresh_status()
    print('Sixth results collected:',len(finished),'/7')


if __name__=='__main__':main()
