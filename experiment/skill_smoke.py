"""Verify one isolated native-hook or Serena MCP activation on a neutral fixture."""

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
from experiment.skill_profiles import install_native_skill, install_serena


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shared-runtime',action='store_true')
    parser.add_argument('--variant',choices=('ponytail','caveman','serena'),default='ponytail')
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
    if args.variant=='serena':
        (fixture/'src').mkdir();(fixture/'lib.rs').rename(fixture/'src/lib.rs')
        (fixture/'Cargo.toml').write_text('[package]\nname = "serena_activation_fixture"\nversion = "0.1.0"\nedition = "2021"\n')
        subprocess.run(['git','init','-q',str(fixture)],check=True)
        subprocess.run(['git','-C',str(fixture),'-c','user.name=Activation fixture','-c','user.email=probe@example.invalid','add','.'],check=True)
        subprocess.run(['git','-C',str(fixture),'-c','user.name=Activation fixture','-c','user.email=probe@example.invalid','commit','-qm','Add neutral Rust fixture'],check=True)
    image = config['images'][0]['local']
    if args.shared_runtime:
        runtime = json.loads((ROOT/'profiles/runtime/manifest.json').read_text())
        if runtime.get('rust_lsp_verified') is not True or not runtime.get('image_id'):
            raise ValueError('Shared runtime is not verified')
        image = runtime['image_id']
        config['benchmark']['skill_runtime_image_id']=image
    elif args.variant=='serena':
        raise ValueError('Serena smoke requires --shared-runtime')
    setup = ContainerSetup(container_name='experiment-'+output.name,image_name=image,
        agent_name='codex',agent_framework_name='codex',agent_version=config['codex']['version'],
        repo_name=config['benchmark']['repo'],runtime_policy_binding=binding.runtime_policy_binding)
    class NativeHooks(CodexFramework):
        def build_run_command(self,*args,**kwargs):
            return super().build_run_command(*args,**kwargs)+' --dangerously-bypass-hook-trust --skip-git-repo-check'
    result = {'success':False,'kind':'activation_smoke_not_measured','variant':args.variant,'failure_category':None}
    try:
        save(output/'quota_before.json',read_quota())
        check_quota(json.loads((output/'quota_before.json').read_text()),config['resources']['quota_stop_percent'])
        mounts=[] if args.variant=='serena' else ['--mount',f'type=bind,src={fixture},dst=/testbed,readonly']
        setup.start_container(extra_mounts=mounts)
        if args.variant=='serena':
            subprocess.run(['docker','cp',str(fixture)+'/.',setup.container_name+':/testbed'],check=True,capture_output=True)
            subprocess.run(['docker','exec',setup.container_name,'chown','-R','fakeroot:fakeroot','/testbed'],check=True,capture_output=True)
        result['image_id'] = subprocess.check_output(['docker','inspect','--format','{{.Image}}',setup.container_name],text=True).strip()
        setup.lock_network()
        if args.variant=='serena':
            install_serena(setup,output,config)
        else:
            install_native_skill(setup,output,config,args.variant,repository_mount=fixture)
        setup.prepare_agent_invocation()
        save(output/'quota_before_model.json',read_quota())
        check_quota(json.loads((output/'quota_before_model.json').read_text()),config['resources']['quota_stop_percent'])
        agent = AgentRunner(container_name=setup.container_name,agent_name='codex',model=config['codex']['model'],
            reasoning_effort=config['codex']['reasoning_effort'],timeout_ms=120000,log_dir=output/'log')
        if args.variant!='serena':
            agent._framework = NativeHooks(reasoning_effort=config['codex']['reasoning_effort'])
        prompt = 'Read the mode header already supplied by your SessionStart hook. Reply with its exact text only. Do not invoke tools or inspect files.'
        if args.variant=='serena':
            prompt='Use Serena initial_instructions, then Serena get_symbols_overview on src/lib.rs. Reply with the function name returned by that MCP tool. Do not edit files or use shell tools.'
        ok, session = agent.run(prompt)
        get_parser('codex').extract_raw_logs(setup.container_name,output/'log')
        events = [json.loads(line) for line in (output/'log/agent_stdout.txt').read_text().splitlines() if line.startswith('{')]
        usage = codex_usage(events)
        result.update(session_id=session,usage=usage)
        messages = [e.get('item',{}).get('text','').strip() for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
        proof = json.loads((output/'effective_profile.json').read_text())
        if args.variant=='serena':
            calls=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='mcp_tool_call']
            symbols=[item for item in calls if item.get('server')=='serena' and item.get('tool')=='get_symbols_overview']
            assert ok and symbols and any(item.get('status')=='completed' and not item.get('error') and any(block.get('type')=='text' and 'activation_fixture' in json.loads(block['text']).get('Function',[]) for block in item.get('result',{}).get('content',[])) for item in symbols), 'Serena symbol tool activation missing'
            assert any('activation_fixture' in text for text in messages), 'Model did not observe the MCP symbol'
            assert not usage['tool_calls'].get('shell'), 'Serena smoke unexpectedly invoked shell tools'
            proof.update(mcp_activation_verified=True,observed_mcp_tool_calls=len(calls))
            result.update(mcp_activation_verified=True,observed_mcp_tool_calls=len(calls),mcp_calls=calls)
        else:
            subprocess.run(['docker','cp',setup.container_name+':/home/fakeroot/.codex/skill_hook_audit.jsonl',str(output/'hook_audit.jsonl')],check=True,capture_output=True)
            audit = [json.loads(line) for line in (output/'hook_audit.jsonl').read_text().splitlines()]
            header = 'PONYTAIL MODE ACTIVE — level: full' if args.variant == 'ponytail' else 'CAVEMAN MODE ACTIVE — mode: caveman'
            assert ok and header in messages, 'Active mode was not observed by the model'
            assert any(row['unprivileged_uid']!=0 and ((args.variant=='ponytail' and row.get('full_mode_context') and row.get('mode')=='full') or
                (args.variant=='caveman' and row.get('caveman_mode_context') and row.get('mode')=='caveman')) for row in audit), 'Native SessionStart activation missing'
            assert not usage['tool_calls'], 'Activation smoke unexpectedly invoked tools'
            proof.update(native_hook_activation_verified=True,activation_evidence='hook_audit.jsonl',model_observed_mode=header)
        save(output/'effective_profile.json',proof)
        result.update(success=True,session_id=session,usage=usage,planner_used=False,
            fixture_read_only=args.variant!='serena',quarantine='protected')
        if args.variant!='serena':
            result.update(native_hook_activation_verified=True,audit=audit)
    except Exception as error:
        result.update(failure_category='quota_pressure' if str(error).startswith('Quota pressure') else 'skill_activation_failure',error=str(error))
    finally:
        setup.cleanup()
        result['duration_seconds']=time.monotonic()-started
        save(output/'quota_after.json',read_quota())
        save(output/'result.json',result)
        redact_artifacts(output,secrets)
        lock.close()
    print(json.dumps({key:result.get(key) for key in ('success','native_hook_activation_verified','mcp_activation_verified','failure_category','error')}))
    return 0 if result['success'] else 2


if __name__=='__main__':
    raise SystemExit(main())
