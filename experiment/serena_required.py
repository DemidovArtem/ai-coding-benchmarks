"""Verify an explicit Serena-first policy without changing the frozen natural-use cohort."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from experiment.metrics import codex_usage
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, save, trial_lock, validate
from experiment.security import credential_values, redact, redact_artifacts
from experiment.skill_profiles import install_serena


def verify_required_usage(events):
    """Reject configured-but-unused, failed, or late semantic navigation."""
    items = [e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type') in ('command_execution','file_change','mcp_tool_call')]
    successful = [(n,item) for n,item in enumerate(items) if item.get('type')=='mcp_tool_call' and item.get('server')=='serena' and item.get('status')=='completed' and not item.get('error')]
    positions = {}
    for n,item in successful:
        positions.setdefault(item.get('tool'),n)
    for tool in ('initial_instructions','onboarding','write_memory'):
        if tool not in positions:
            raise ValueError('Required successful Serena call missing: '+tool)
    if not items or items[0].get('tool')!='initial_instructions' or positions['initial_instructions']!=0:
        raise ValueError('Serena initial_instructions must precede shell/source operations')
    def has_symbols(item):
        for block in item.get('result',{}).get('content',[]):
            if block.get('type')!='text':
                continue
            value=json.loads(block['text'])
            if isinstance(value,list) and value or isinstance(value,dict) and any(isinstance(v,list) and v for v in value.values()):
                return True
        return False
    semantic = [n for n,item in successful if item.get('tool') in ('get_symbols_overview','find_symbol') and has_symbols(item)]
    if not semantic:
        raise ValueError('No nonempty successful Serena symbol result')
    source_tools={'replace_symbol_body','replace_in_files','rename_symbol','safe_delete_symbol','insert_after_symbol','insert_before_symbol'}
    first_source_edit = next((n for n,item in enumerate(items) if item['type']=='file_change' or item.get('tool') in source_tools),len(items))
    if not (positions['onboarding'] < min(semantic) < positions['write_memory'] < first_source_edit):
        raise ValueError('Cold onboarding and semantic navigation must precede memory/source edits')
    if any(item['type']=='command_execution' for item in items[:positions['write_memory']]):
        raise ValueError('Shell work preceded mandatory Serena orientation')
    return {'required_usage_verified':True,'observed_mcp_tool_calls':len(successful),
            'semantic_calls':sum(item.get('tool') in ('get_symbols_overview','find_symbol') for _,item in successful),
            'onboarding_observed':True,'memory_write_observed':True}


def install_required_policy(setup, output):
    source=ROOT/'profiles/serena_required/AGENTS.md';name=setup.container_name
    target='/home/fakeroot/.codex/AGENTS.md'
    subprocess.run(['docker','cp',str(source),name+':'+target],check=True,capture_output=True)
    subprocess.run(['docker','exec',name,'chown','root:root',target],check=True,capture_output=True)
    subprocess.run(['docker','exec',name,'chmod','0444',target],check=True,capture_output=True)
    actual=subprocess.check_output(['docker','exec',name,'sha256sum',target],text=True).split()[0]
    assert actual==hashlib.sha256(source.read_bytes()).hexdigest()
    proof=json.loads((output/'effective_profile.json').read_text());proof.update(variant='serena_required',required_policy_sha256=actual,
        required_policy_path=target,policy_in_repository=False,required_usage_verified=False)
    save(output/'effective_profile.json',proof)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    config=json.loads((ROOT/'reports/phase3_experiment.json').read_text());validate(config)
    lock=trial_lock(Path(config['resources']['runtime_root']));output=args.output.resolve();output.mkdir(parents=True,exist_ok=False);output.chmod(0o700)
    secrets=credential_values(Path.home()/'.codex/auth.json');started=time.monotonic()
    sys.path.insert(0,str(ROOT/'vendor/SWE-Milestone'))
    from harness.e2e.run_milestone import MilestoneRunner
    from harness.e2e.container_setup import ContainerSetup
    from harness.e2e.agent_runner import AgentRunner
    from harness.e2e.log_parser import get_parser
    workspace=ROOT/config['benchmark']['dataset_root']/config['benchmark']['repo'];milestone=config['benchmark']['smoke_milestone']
    binding=MilestoneRunner(workspace_root=workspace,milestone_id=milestone,srs_path=workspace/'srs'/milestone/'SRS.md',output_dir=output/'bindings',agent_name='codex',main_branch=config['benchmark']['main_branch'],agent_version=config['codex']['version'])
    setup=ContainerSetup(container_name='experiment-'+output.name,image_name=config['benchmark']['skill_runtime_image_id'],agent_name='codex',agent_framework_name='codex',agent_version=config['codex']['version'],repo_name=config['benchmark']['repo'],runtime_policy_binding=binding.runtime_policy_binding)
    result={'success':False,'variant':'serena_required','kind':'activation_smoke_not_measured','grader_run':False,'failure_category':None}
    try:
        before=read_quota();save(output/'quota_before.json',before);check_quota(before,config['resources']['quota_stop_percent'])
        setup.start_container();setup.lock_network()
        fixture=output/'fixture';(fixture/'src').mkdir(parents=True)
        (fixture/'Cargo.toml').write_text('[package]\nname="required_policy_fixture"\nversion="0.1.0"\nedition="2021"\n')
        (fixture/'src/lib.rs').write_text('pub fn orientation_fixture() -> usize { 42 }\n')
        source_hash=hashlib.sha256((fixture/'src/lib.rs').read_bytes()).hexdigest()
        subprocess.run(['git','init','-q',str(fixture)],check=True);subprocess.run(['git','-C',str(fixture),'add','.'],check=True)
        subprocess.run(['git','-C',str(fixture),'-c','user.name=Policy fixture','-c','user.email=probe@example.invalid','commit','-qm','Add neutral fixture'],check=True)
        subprocess.run(['docker','cp',str(fixture)+'/.',setup.container_name+':/testbed'],check=True,capture_output=True)
        subprocess.run(['docker','exec',setup.container_name,'chown','-R','fakeroot:fakeroot','/testbed'],check=True,capture_output=True)
        install_serena(setup,output,config);install_required_policy(setup,output);setup.prepare_agent_invocation()
        before=read_quota();save(output/'quota_before_model.json',before);check_quota(before,config['resources']['quota_stop_percent'])
        agent=AgentRunner(container_name=setup.container_name,agent_name='codex',model=config['codex']['model'],reasoning_effort=config['codex']['reasoning_effort'],timeout_ms=180000,log_dir=output/'log')
        ok,session=agent.run('Summarize the public function in this Rust repository. Do not change source files.')
        get_parser('codex').extract_raw_logs(setup.container_name,output/'log')
        events=[json.loads(l) for l in (output/'log/agent_stdout.txt').read_text().splitlines() if l.startswith('{')]
        result.update(session_id=session,usage=codex_usage(events))
        assert ok,'Policy smoke model turn failed'
        result.update(verify_required_usage(events))
        after=subprocess.check_output(['docker','exec',setup.container_name,'sha256sum','/testbed/src/lib.rs'],text=True).split()[0];assert after==source_hash
        state=json.loads(subprocess.check_output(['docker','exec',setup.container_name,'python3','-c',"import pathlib,json; f=[p for p in pathlib.Path('/testbed/.serena/memories').rglob('*') if p.is_file()]; print(json.dumps({'memory_files_after':len(f),'memory_bytes_after':sum(p.stat().st_size for p in f)}))"],text=True))
        assert state['memory_files_after']>0,'No cold onboarding memory persisted'
        result.update(state,success=True,source_unchanged=True,memory_files_before=0,memory_bytes_before=0,image_id=config['benchmark']['skill_runtime_image_id'])
    except Exception as error:
        result.update(failure_category='quota_pressure' if str(error).startswith('Quota pressure') else 'required_serena_activation_failure',error=redact(str(error),secrets))
    finally:
        for source,target in (('/home/fakeroot/.serena-profile/logs','serena_logs'),('/testbed/.serena','serena_project')):
            subprocess.run(['docker','cp',setup.container_name+':'+source,str(output/target)],capture_output=True)
        setup.cleanup();result['duration_seconds']=time.monotonic()-started
        save(output/'quota_after.json',read_quota());save(output/'result.json',result);redact_artifacts(output,secrets)
        for path in (output/'serena_project').rglob('*'):
            if path.is_file() and path.suffix in ('.md','.yml','.yaml'):
                path.write_text(redact(path.read_text(),secrets))
        lock.close()
    print(json.dumps({k:result.get(k) for k in ('success','required_usage_verified','failure_category','error')}))
    return 0 if result['success'] else 2


if __name__=='__main__':raise SystemExit(main())
