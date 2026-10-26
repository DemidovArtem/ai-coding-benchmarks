"""Resume the retained Ponytail fourth turn after its recorded quota refusal."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from experiment.checkpoint_restore import copy_to, read_turns
from experiment.continuous_resume import verify_retained_config
from experiment.phase6d import analyze, prior_rows, publish
from experiment.collect import collect, load, sonar_result
from experiment.continuous import (assert_boundary, check_resources, events_from, preserve_and_collect,
                                   resume_step, runtime_binding, update_progress, verify_dispatch, verify_images)
from experiment.quota import read_quota
from experiment.report import export
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact
from experiment.status import main as refresh_status

MILESTONE = 'milestone_seed_b610d1c_1'
CONFIG = ROOT / 'reports/phase6d_experiment.json'



def validate_failure(failed, blocked):
    if (failed['trial_state'] != 'failed' or failed.get('ending_commit')
            or failed['variant'] != 'ponytail' or failed['repetition'] != 2
            or failed['continuous']['step'] != 4
            or failed['continuous']['executor_session_id'] != '01a16e63-039b-7653-aff4-bfd3ae7116af'):
        raise ValueError('Recovery is limited to the retained Ponytail fourth quota stop')
    events = events_from(blocked / 'log/agent_stdout.txt')
    if not any(e.get('type') == 'turn.failed' and 'usage limit' in str(e).lower() for e in events):
        raise ValueError('Original quota stop is unverified')
    if any(e.get('type') == 'turn.completed' for e in events):
        raise ValueError('Original turn already completed')


def recover(config):
    chain = "phase6d_ponytail_r02"
    blocked = ROOT / "results/trials/phase6d_ponytail_r02_s04"
    failed = load(ROOT / "reports/phase6d_ponytail_r02_s04.json")
    parent = load(ROOT / "reports/phase6c_ponytail_r02_s03.json")
    checkpoint = next(row for row in load(ROOT / "reports/phase6d_checkpoints.json")["entries"]
                      if row["parent_trial"] == parent["trial_id"])
    validate_failure(failed, blocked)
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.run_milestone import MilestoneRunner
    from experiment.skill_trial import assert_no_profile_artifacts

    parent = load(ROOT / 'reports' / (checkpoint['parent_trial'] + '.json'))
    priors = prior_rows(parent)
    if parent['collection_errors'] or parent['ending_commit'] != checkpoint['ending_commit']:
        raise ValueError('Parent source checkpoint changed')
    rollout = Path(checkpoint['rollout_path'])
    if hashlib.sha256(rollout.read_bytes()).hexdigest() != checkpoint['rollout_sha256']:
        raise ValueError('Parent native history changed')
    output = Path(config['resources']['runtime_root']) / (chain + '_s04_resume01')
    if output.exists():
        raise ValueError('Existing extension attempt requires explicit recovery')
    output.mkdir(mode=0o700, parents=True)
    step_config = json.loads(json.dumps(config))
    step_config['benchmark']['smoke_milestone'] = MILESTONE
    save(output / 'experiment.json', step_config)
    session = checkpoint['session_id']
    metadata = {'phase': 'trial', 'trial_kind': 'continuous_step', 'measured_comparison': True,
                'state': 'running', 'variant': parent['variant'], 'trajectory_id': chain, 'step': 4,
                'repetition': parent['repetition'], 'model': config['codex']['model'],
                'reasoning_effort': config['codex']['reasoning_effort'],
                'started_at': datetime.now(timezone.utc).isoformat(), 'executor_session_id': session,
                'setup_fingerprint': setup_fingerprint(config)[0],
                'resume': {'attempt_of': failed['trial_id'], 'same_session_required': session,
                           'original_failure_preserved': str(blocked),
                           'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    save(output / 'run_metadata.json', metadata)
    save(output / 'quota_before.json', read_quota())
    check_quota(load(output / 'quota_before.json'), config['resources']['quota_stop_percent'])
    binding = runtime_binding(config, output)
    workspace = ROOT / config['benchmark']['dataset_root'] / config['benchmark']['repo']
    task_path = '/home/fakeroot/continuous-step-4.txt'
    task = None

    class Hooks(CodexFramework):
        def build_resume_command(self, *args, **kwargs):
            return super().build_resume_command(*args, **kwargs) + ' --dangerously-bypass-hook-trust'

    class ExtensionRunner(MilestoneRunner):
        def _load_prompt(self):
            nonlocal task
            original = super()._load_prompt()
            (output / 'original_task.txt').write_text(original)
            task = original + ('\n\nThis is one step of a sequential pilot. Preserve prior work and submission tags. '
                              'Implement only this task. After committing and tagging this step, stop and await the next user turn.\n')
            local = output / 'dispatched_task.txt'
            local.write_text(task)
            self.container_setup.verify_network_lockdown()
            quota = read_quota()
            save(output / 'quota_before_executor.json', quota)
            check_quota(quota, config['resources']['quota_stop_percent'])
            copy_to(self.container_name, local, task_path)
            self.container_setup.docker_exec(['chown', 'root:root', task_path], user='root')
            self.container_setup.docker_exec(['chmod', '0444', task_path], user='root')
            return ('Continue in this repository and session. Your first shell command must be `cat ' + task_path
                    + '`. Read the complete task and any supplied plan, then follow it. Do not work on other tasks.')

        def _run_evaluation(self, snapshot):
            audit = verify_dispatch(events_from(output / 'log/agent_stdout.txt'), session, task_path, task)
            audit.update(input_commit=parent['ending_commit'], milestone_id=MILESTONE)
            save(output / 'dispatch.json', audit)
            assert_no_profile_artifacts(snapshot)
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot)
            finally:
                save(output / 'durations.json', {'evaluation': time.monotonic() - started})

        def _extract_snapshot_from_workdir(self):
            raise RuntimeError('Continuation requires an immutable fourth submission tag')

    runner = ExtensionRunner(workspace_root=workspace, milestone_id=MILESTONE,
        srs_path=workspace / 'srs' / MILESTONE / 'SRS.md', output_dir=output,
        image_name=config['benchmark']['skill_runtime_image_id'], agent_name='codex',
        agent_version=config['codex']['version'], model=config['codex']['model'],
        reasoning_effort=config['codex']['reasoning_effort'],
        timeout_ms=config['benchmark']['timeout_seconds'] * 1000,
        main_branch=config['benchmark']['main_branch'], keep_container=True,
        trial_name=chain, runtime_policy_binding=binding)
    name = MILESTONE + '-' + chain + '-runner'
    runner.container_name = runner.container_setup.container_name = runner.agent_runner.container_name = name
    setup = runner.container_setup
    info = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
    if info['Image'] != config['benchmark']['skill_runtime_image_id']:
        raise ValueError('Retained runtime image differs')
    if {m['Destination'] for m in info['Mounts']} != {'/tmp/host-codex/auth.json'} or any(m['RW'] for m in info['Mounts']):
        raise ValueError('Retained mounts differ')
    if not info['State']['Running']:
        subprocess.run(['docker', 'start', name], check=True, capture_output=True)
    processes = setup.docker_exec(['ps', '-eo', 'comm']).stdout.splitlines()
    if any(item.strip() in ('codex', 'codex-linux-x64') for item in processes):
        raise ValueError('An executor is still running')
    runner._snapshot_baseline_commit = parent['starting_commit']
    runner.agent_runner.session_id = session
    runner.agent_runner._framework = Hooks(reasoning_effort=config['codex']['reasoning_effort'])
    assert_boundary(runner, parent['ending_commit'])
    for previous in priors:
        if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
            raise ValueError('Retained prior submission moved')
    if runner._verify_tag_exists():
        raise ValueError('Fourth task already submitted; model replay forbidden')
    verify_retained_config(setup.docker_exec(['cat', '/home/fakeroot/.codex/config.toml']).stdout,
                           (ROOT / 'profiles/ponytail/config.toml').read_text())
    proof = load(blocked / 'effective_profile.json')
    for path, expected in [('/home/fakeroot/.codex/hooks.json', proof['hooks_sha256']),
                           ('/opt/experiment-node/node', proof['node']['sha256'])]:
        if setup.docker_exec(['sha256sum', path]).stdout.split()[0] != expected:
            raise ValueError('Retained native hook runtime changed')
    old_audit = setup.docker_exec(['cat', '/home/fakeroot/.codex/skill_hook_audit.jsonl']).stdout.splitlines()
    history = read_turns(name, session)
    turns = history.get('result', {}).get('data', [])
    old_ids = failed['extension']['history_restore']['turn_ids']
    if (history.get('error') or history.get('result', {}).get('nextCursor')
            or [t['id'] for t in turns[:3]] != old_ids
            or any(t['status'] != 'completed' for t in turns[:3])
            or len(turns) != 4 or turns[-1]['status'] not in ('failed', 'interrupted')):
        raise ValueError('Retained history does not match three completed turns and one quota failure')
    save(output / 'native_history_before.json', history)
    setup.lock_network()
    if not runner.agent_runner.refresh_container_credentials():
        raise RuntimeError('OAuth refresh failed before recovery')
    extension = {**failed['extension'], 'recovery_of': failed['trial_id'],
                 'failed_turn_preserved': turns[-1]['id'],
                 'history_reimported': False,
                 'recovery_adapter_sha256': metadata['resume']['adapter_sha256']}
    proof['extension'] = extension
    save(output / 'effective_profile.json', proof)
    update_progress(chain, state='running', completed_steps=0, active_step=4, failure_category=None, resumed_attempt=output.name)
    started = time.monotonic()
    original_resume = runner.agent_runner.resume_session
    def timed_resume(*args, **kwargs):
        before = time.monotonic()
        try:
            return original_resume(*args, **kwargs)
        finally:
            save(output / 'execution.json', {'duration_seconds': time.monotonic() - before})
    runner.agent_runner.resume_session = timed_resume
    error = None
    try:
        result = resume_step(runner, session, parent['ending_commit'])
        commit = runner._get_tag_hash('agent-impl-' + MILESTONE)
        assert_boundary(runner, commit)
        if setup.docker_exec_git('merge-base', '--is-ancestor', parent['ending_commit'], commit).returncode:
            raise ValueError('Fourth submission does not descend from the third')
        for previous in priors:
            if runner._get_tag_hash('agent-impl-' + previous['milestone_id']) != previous['ending_commit']:
                raise ValueError('Previous submission tag moved during extension')
        if parent['variant'] != 'baseline':
            copy_to_path = output / 'hook_audit.jsonl'
            subprocess.run(['docker', 'cp', setup.container_name + ':/home/fakeroot/.codex/skill_hook_audit.jsonl', str(copy_to_path)], check=True, capture_output=True)
            audit = [json.loads(line) for line in copy_to_path.read_text().splitlines()]
            field = 'caveman_mode_context' if parent['variant'] == 'caveman' else 'full_mode_context'
            active = any(row.get(field) for row in audit[len(old_audit):])
            save(output / 'skill_activation.json', {'variant': parent['variant'], 'native_hook_activation_verified': active, 'audit': audit})
            if not active:
                raise RuntimeError('Restored native profile was not activated')
        raw = load(output / 'evaluation/evaluation_result.json')
        if (raw.get('error_message') or raw.get('infra_invalid')
                or not raw.get('test_summary', {}).get('total')
                or raw.get('residue_prune', {}).get('enabled') is not True):
            raise RuntimeError('Fourth grader infrastructure or pruning policy invalid')
        metadata.update(state='finished', returncode=0 if result.resolved else 1)
    except Exception as caught:
        error = caught
        metadata.update(state='failed', failure_category='quota_pressure' if runner.agent_runner._last_rate_limit else 'continuation_failure',
                        error=redact(str(caught), credential_values(Path.home() / '.codex/auth.json')))
    finally:
        metadata['duration_seconds'] = time.monotonic() - started
        save(output / 'quota_after.json', read_quota())
        # A rollout alone is insufficient for paginated native history: retain its databases too.
        setup.docker_exec(['python3', '-c', '''from pathlib import Path
import sqlite3,hashlib,json
source=Path('/home/fakeroot/.codex'); target=Path('/tmp/phase6d-native-store'); target.mkdir(exist_ok=True)
manifest={}
for name in ('state_5.sqlite','thread_history_1.sqlite'):
 p=source/name
 if not p.exists(): continue
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as before, sqlite3.connect(target/name) as after:
  before.backup(after)
 manifest[name]=hashlib.sha256((target/name).read_bytes()).hexdigest()
assert 'state_5.sqlite' in manifest
(target/'manifest.json').write_text(json.dumps(manifest,indent=2))
'''], user='root')
        subprocess.run(['docker', 'cp', setup.container_name + ':/tmp/phase6d-native-store',
                        str(output / 'native_session_store')], check=True, capture_output=True)
        stores = load(output / 'native_session_store/manifest.json')
        if any(hashlib.sha256((output / 'native_session_store' / name).read_bytes()).hexdigest() != digest
               for name, digest in stores.items()):
            raise ValueError('Native database backup hash mismatch')
        record, _ = preserve_and_collect(runner, output, step_config, metadata,
                                        parent['usage']['executor_cumulative'], parent['ending_commit'])
        record['extension'] = extension
        publish(record)
        update_progress(chain, state='failed' if error else 'running', completed_steps=0,
                        active_step=None, last_step=output.name, failure_category=metadata.get('failure_category'))
    if error:
        raise error
    if record['collection_errors']:
        raise RuntimeError('Continuation collection failed; further inference withheld')
    analyze(record)
    update_progress(chain, state='finished', completed_steps=1)
    durable = ROOT / 'results/trials' / record['trial_id']
    if any(hashlib.sha256((durable / 'native_session_store' / name).read_bytes()).hexdigest() != digest
           for name, digest in stores.items()):
        raise ValueError('Durable native database backup hash mismatch; retain container')
    setup.cleanup()
    print('STEP_COLLECTED', record['trial_id'], 'resolved=', record['resolved'], 'sonar=', True, flush=True)



def main():
    sys.path.insert(0, str(ROOT / 'vendor/SWE-Milestone'))
    config = load(CONFIG)
    validate(config)
    verify_images(config)
    check_resources(config)
    check_quota(read_quota(), config['resources']['quota_stop_percent'])
    os.environ['SWE_MILESTONE_RESIDUE_PRUNE'] = '1'
    lock = trial_lock(Path(config['resources']['runtime_root']))
    try:
        recover(config)
    finally:
        lock.close()


if __name__ == '__main__':
    main()
