"""Verify native Ponytail lifecycle injection with one isolated, tool-free OAuth turn."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from experiment.metrics import codex_usage
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, save, trial_lock, validate
from experiment.security import credential_values, redact_artifacts
from experiment.skill_profiles import install_ponytail


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    config = json.loads((ROOT/'experiment.yaml').read_text())
    validate(config)
    lock = trial_lock(Path(config['resources']['runtime_root']))
    output = args.output.resolve()
    output.mkdir(parents=True,exist_ok=False)
    output.chmod(0o700)
    started = time.monotonic()
    secrets = credential_values(Path.home()/'.codex/auth.json')
    sys.path.insert(0,str(ROOT/'vendor/SWE-Milestone'))
    from harness.e2e.run_milestone import MilestoneRunner
    from harness.e2e.container_setup import ContainerSetup
    from harness.e2e.agent_runner import AgentRunner
    from harness.e2e.agents.codex import CodexFramework
    from harness.e2e.log_parser import get_parser
    workspace = ROOT/config['benchmark']['dataset_root']/config['benchmark']['repo']
    milestone = config['benchmark']['smoke_milestone']
    binding = MilestoneRunner(workspace_root=workspace,milestone_id=milestone,
        srs_path=workspace/'srs'/milestone/'SRS.md',output_dir=output/'bindings',agent_name='codex',
        main_branch=config['benchmark']['main_branch'],agent_version=config['codex']['version'])
    fixture = output/'fixture';fixture.mkdir()
    (fixture/'lib.rs').write_text('pub fn activation_fixture() {}\n')
    setup = ContainerSetup(container_name='experiment-'+output.name,image_name=config['images'][0]['local'],
        agent_name='codex',agent_framework_name='codex',agent_version=config['codex']['version'],
        repo_name=config['benchmark']['repo'],runtime_policy_binding=binding.runtime_policy_binding)
    class NativeHooks(CodexFramework):
        def build_run_command(self,*args,**kwargs):
            return super().build_run_command(*args,**kwargs)+' --dangerously-bypass-hook-trust --skip-git-repo-check'
    result = {'success':False,'kind':'activation_smoke_not_measured','variant':'ponytail','failure_category':None}
    try:
        save(output/'quota_before.json',read_quota())
        check_quota(json.loads((output/'quota_before.json').read_text()),config['resources']['quota_stop_percent'])
        setup.start_container(extra_mounts=['--mount',f'type=bind,src={fixture},dst=/testbed,readonly'])
        setup.lock_network()
        install_ponytail(setup,output,config,repository_mount=fixture)
        setup.prepare_agent_invocation()
        save(output/'quota_before_model.json',read_quota())
        check_quota(json.loads((output/'quota_before_model.json').read_text()),config['resources']['quota_stop_percent'])
        agent = AgentRunner(container_name=setup.container_name,agent_name='codex',model=config['codex']['model'],
            reasoning_effort=config['codex']['reasoning_effort'],timeout_ms=120000,log_dir=output/'log')
        agent._framework = NativeHooks(reasoning_effort=config['codex']['reasoning_effort'])
        ok, session = agent.run('Read the mode header already supplied by your SessionStart hook. Reply with its exact text only. Do not invoke tools or inspect files.')
        get_parser('codex').extract_raw_logs(setup.container_name,output/'log')
        subprocess.run(['docker','cp',setup.container_name+':/home/fakeroot/.codex/skill_hook_audit.jsonl',str(output/'hook_audit.jsonl')],check=True,capture_output=True)
        audit = [json.loads(line) for line in (output/'hook_audit.jsonl').read_text().splitlines()]
        events = [json.loads(line) for line in (output/'log/agent_stdout.txt').read_text().splitlines() if line.startswith('{')]
        usage = codex_usage(events)
        messages = [e.get('item',{}).get('text','').strip() for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
        assert ok and 'PONYTAIL MODE ACTIVE — level: full' in messages, 'Active mode was not observed by the model'
        assert any(row['entrypoint']=='ponytail-activate.js' and row['full_mode_context'] and row['mode']=='full' and row['unprivileged_uid']!=0 for row in audit), 'Native SessionStart activation missing'
        assert not usage['tool_calls'], 'Activation smoke unexpectedly invoked tools'
        proof = json.loads((output/'effective_profile.json').read_text())
        proof.update(native_hook_activation_verified=True,activation_evidence='hook_audit.jsonl',model_observed_mode='PONYTAIL MODE ACTIVE — level: full')
        save(output/'effective_profile.json',proof)
        result.update(success=True,native_hook_activation_verified=True,session_id=session,usage=usage,audit=audit,
            planner_used=False,fixture_read_only=True,quarantine='protected')
    except Exception as error:
        result.update(failure_category='skill_activation_failure',error=str(error))
    finally:
        setup.cleanup()
        result['duration_seconds']=time.monotonic()-started
        save(output/'quota_after.json',read_quota())
        save(output/'result.json',result)
        redact_artifacts(output,secrets)
        lock.close()
    print(json.dumps({key:result.get(key) for key in ('success','native_hook_activation_verified','failure_category','error')}))
    return 0 if result['success'] else 2


if __name__=='__main__':
    raise SystemExit(main())
