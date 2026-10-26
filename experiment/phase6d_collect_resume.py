"""Finish collection of the already graded recovery; never invoke a model or grader."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from experiment.collect import load
from experiment.continuous import assert_boundary, preserve_and_collect, runtime_binding, update_progress
from experiment.phase6d import CONFIG, MILESTONE, analyze, prior_rows, publish
from experiment.runner import ROOT, save, trial_lock, validate


def finish(config):
    from harness.e2e.run_milestone import MilestoneRunner

    output = Path(config['resources']['runtime_root'])/'phase6d_ponytail_r02_s04_resume01'
    parent = load(ROOT/'reports/phase6c_ponytail_r02_s03.json')
    metadata = load(output/'run_metadata.json')
    proof = load(output/'effective_profile.json')
    raw = load(output/'evaluation/evaluation_result.json')
    if (metadata['state'] != 'running' or not proof['extension'].get('recovery_of')
            or raw.get('error_message') or raw.get('infra_invalid')
            or raw.get('test_summary', {}).get('total') != 1111
            or not load(output/'skill_activation.json')['native_hook_activation_verified']):
        raise ValueError('Expected completed inference and grader evidence is absent')
    if hashlib.sha256((ROOT/'experiment/phase6d_resume.py').read_bytes()).hexdigest() != metadata['resume']['adapter_sha256']:
        raise ValueError('Inference adapter changed')
    old_store = output/'native_session_store'
    old_manifest = load(old_store/'manifest.json')
    old_actual = {name:hashlib.sha256((old_store/name).read_bytes()).hexdigest() for name in old_manifest}
    if old_manifest == old_actual:
        raise ValueError('Expected backup hash failure is absent')
    evidence = {'kind':'collection_only_recovery', 'new_model_calls':0, 'new_grader_runs':0,
                'failed_manifest':old_manifest, 'actual_failed_copy':old_actual,
                'cause':'sqlite3 connection context commits transactions but does not close; backup hash was computed before final close',
                'reproduction':'Offline backup into an existing WAL-mode target reproduced the same premature manifest hash.',
                'original_helper_sha256':metadata['resume']['adapter_sha256'],
                'backup_helper_sha256':hashlib.sha256((ROOT/'experiment/session_store.py').read_bytes()).hexdigest()}
    workspace = ROOT/config['benchmark']['dataset_root']/config['benchmark']['repo']
    runner = MilestoneRunner(workspace_root=workspace, milestone_id=MILESTONE,
        srs_path=workspace/'srs'/MILESTONE/'SRS.md', output_dir=output,
        image_name=config['benchmark']['skill_runtime_image_id'], agent_name='codex',
        agent_version=config['codex']['version'], model=config['codex']['model'],
        reasoning_effort=config['codex']['reasoning_effort'],
        timeout_ms=config['benchmark']['timeout_seconds']*1000,
        main_branch=config['benchmark']['main_branch'], keep_container=True,
        trial_name='phase6d_ponytail_r02', runtime_policy_binding=runtime_binding(config,output))
    setup = runner.container_setup
    runner.agent_runner.session_id = metadata['executor_session_id']
    runner._snapshot_baseline_commit = parent['starting_commit']
    commit = runner._get_tag_hash('agent-impl-'+MILESTONE)
    assert_boundary(runner,commit)
    if setup.docker_exec_git('merge-base','--is-ancestor',parent['ending_commit'],commit).returncode:
        raise ValueError('Fourth submission no longer descends from third')
    for previous in prior_rows(parent):
        if runner._get_tag_hash('agent-impl-'+previous['milestone_id']) != previous['ending_commit']:
            raise ValueError('Prior submission moved')
    processes=setup.docker_exec(['ps','-eo','comm']).stdout.splitlines()
    if any(p.strip() in ('codex','codex-linux-x64') for p in processes):
        raise ValueError('An executor is still active')
    backup_path='/tmp/phase6d-native-store-after-close-01'
    subprocess.run(['docker','cp',str(ROOT/'experiment/session_store.py'),setup.container_name+':/tmp/phase6d_session_store.py'],check=True,capture_output=True)
    setup.docker_exec(['python3','/tmp/phase6d_session_store.py','/home/fakeroot/.codex',backup_path],user='root')
    failed_copy=output/'native_session_store_failed_001'
    if failed_copy.exists():
        raise ValueError('Prior failed-copy preservation already exists')
    old_store.rename(failed_copy)
    subprocess.run(['docker','cp',setup.container_name+':'+backup_path,str(old_store)],check=True,capture_output=True)
    manifest=load(old_store/'manifest.json')
    if any(hashlib.sha256((old_store/name).read_bytes()).hexdigest()!=sha for name,sha in manifest.items()):
        raise ValueError('Closed SQLite backup copy hash differs')
    evidence.update(verified_manifest=manifest,ending_commit=commit)
    save(output/'collection_recovery.json',evidence)
    save(output/'collection_failure_metadata.json',metadata)
    metadata.update(state='finished', returncode=0 if raw['resolved'] else 1,
                    duration_seconds=None,
                    wall_duration_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(metadata['started_at'])).total_seconds(),
                    interruptions=[{'phase':'collection','reason':'native SQLite premature hash','recovered_without_model_or_grader':True}])
    step_config=load(output/'experiment.json')
    record,_=preserve_and_collect(runner,output,step_config,metadata,
                                 parent['usage']['executor_cumulative'],parent['ending_commit'])
    record['extension']={**proof['extension'],'collection_recovery':evidence}
    publish(record)
    if record['collection_errors']:
        raise ValueError('Source/usage collection failed')
    analyze(record)
    durable=ROOT/'results/trials'/record['trial_id']/'native_session_store'
    if any(hashlib.sha256((durable/name).read_bytes()).hexdigest()!=sha for name,sha in manifest.items()):
        raise ValueError('Durable SQLite backup differs')
    save(ROOT/'reports/phase6d_collection_recovery.json',evidence)
    update_progress('phase6d_ponytail_r02',state='finished',completed_steps=1,active_step=None,
                    last_step=output.name,failure_category=None)
    setup.cleanup()
    print('COLLECTED',record['trial_id'],'sonar=True',flush=True)


def main():
    sys.path.insert(0,str(ROOT/'vendor/SWE-Milestone'))
    config=load(CONFIG)
    validate(config)
    lock=trial_lock(Path(config['resources']['runtime_root']))
    try:finish(config)
    finally:lock.close()


if __name__=='__main__':
    main()
