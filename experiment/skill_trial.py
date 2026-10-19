"""Run one measured baseline/native-skill/Serena trial from a frozen common-runtime cohort."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import tarfile

from experiment.audit import command
from experiment.quota import read_quota
from experiment.runner import ROOT, check_quota, save, setup_fingerprint, trial_lock, validate
from experiment.security import credential_values, redact, redact_artifacts

VARIANTS = ('baseline','ponytail','caveman','serena')


def require_ready(runtime, activations):
    image = runtime.get('image_id','')
    if not re.fullmatch(r'sha256:[0-9a-f]{64}',image) or runtime.get('rust_lsp_verified') is not True:
        raise ValueError('Common runtime is not verified; no measured model call is allowed')
    for variant in VARIANTS[1:]:
        proof = activations.get(variant,{})
        verified = proof.get('native_hook_activation_verified') if variant!='serena' else proof.get('mcp_activation_verified')
        if verified is not True or proof.get('image_id') != image:
            raise ValueError('Activation on the exact common runtime is missing: '+variant)
        if variant=='serena' and not proof.get('observed_mcp_tool_calls'):
            raise ValueError('Serena must have a verified MCP tool smoke')
    return image




def freeze_config(base, runtime, activations):
    image = require_ready(runtime,activations)
    config = json.loads(json.dumps(base))
    config.update(experiment_id='ripgrep-skills-v1-pilot',stage='phase3_frozen',variants=list(VARIANTS))
    config['benchmark']['skill_runtime_image_id'] = image
    files = [ROOT/'experiment'/name for name in ('skill_trial.py','skill_profiles.py','skill_smoke.py','serena_probe.py','collect.py','metrics.py','report.py')]
    files += [path for path in (ROOT/'profiles').rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc']
    files += [ROOT/'reports'/f'{variant}_activation.json' for variant in VARIANTS[1:]]
    for path in files:
        config['pins']['file_sha256'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return config


def assert_no_profile_artifacts(snapshot):
    with tarfile.open(snapshot) as archive:
        for member in archive.getmembers():
            if any(part in ('.serena','.codex','.agents') for part in Path(member.name).parts):
                raise ValueError('Profile instructions or memory entered the grader snapshot')


def run_trial(config, output, variant):
    sys.path.insert(0,str(ROOT/'vendor/SWE-Milestone'))
    from harness.e2e.run_milestone import MilestoneRunner
    from harness.e2e.agents.codex import CodexFramework
    from experiment.profiles import activate_profile
    from experiment.skill_profiles import install_native_skill, install_serena

    class NativeHooks(CodexFramework):
        def build_run_command(self,*args,**kwargs):
            return super().build_run_command(*args,**kwargs)+' --dangerously-bypass-hook-trust'

    class SkillRunner(MilestoneRunner):
        def _load_prompt(self):
            task = super()._load_prompt()
            if variant=='baseline':
                activate_profile(self.container_setup,output,config)
            elif variant in ('ponytail','caveman'):
                install_native_skill(self.container_setup,output,config,variant)
                self.agent_runner._framework = NativeHooks(reasoning_effort=config['codex']['reasoning_effort'])
            else:
                install_serena(self.container_setup,output,config)
            tree = self.container_setup.docker_exec_git('rev-parse','HEAD^{tree}').stdout.strip()
            if tree != config['benchmark']['common_starting_tree']:
                raise ValueError('Starting tree differs from the frozen cohort')
            save(output/'quota_before_executor.json',read_quota())
            check_quota(json.loads((output/'quota_before_executor.json').read_text()),config['resources']['quota_stop_percent'])
            (output/'original_task.txt').write_text(task)
            return task

        def _run_evaluation(self,snapshot_path):
            assert_no_profile_artifacts(snapshot_path)
            started = time.monotonic()
            try:
                return super()._run_evaluation(snapshot_path)
            finally:
                save(output/'durations.json',{'evaluation':time.monotonic()-started})

    benchmark = config['benchmark']
    workspace = ROOT/benchmark['dataset_root']/benchmark['repo']
    milestone = benchmark['smoke_milestone']
    runner = SkillRunner(workspace_root=workspace,milestone_id=milestone,srs_path=workspace/'srs'/milestone/'SRS.md',
        output_dir=output,image_name=benchmark['skill_runtime_image_id'],agent_name='codex',agent_version=config['codex']['version'],
        model=config['codex']['model'],reasoning_effort=config['codex']['reasoning_effort'],timeout_ms=benchmark['timeout_seconds']*1000,
        main_branch=benchmark['main_branch'],keep_container=True,trial_name=output.name,max_retries=1)
    result = runner.run()
    bundle = '/tmp/experiment-submission.bundle'
    subprocess.run(['docker','exec','-w','/testbed',runner.container_name,'git','-c','safe.directory=/testbed','bundle','create',bundle,'--all'],check=True,capture_output=True)
    subprocess.run(['docker','cp',runner.container_name+':'+bundle,str(output/'repository.bundle')],check=True,capture_output=True)
    if variant in ('ponytail','caveman'):
        subprocess.run(['docker','cp',runner.container_name+':/home/fakeroot/.codex/skill_hook_audit.jsonl',str(output/'hook_audit.jsonl')],check=True,capture_output=True)
        audit = [json.loads(line) for line in (output/'hook_audit.jsonl').read_text().splitlines()]
        active = any(row.get('full_mode_context') if variant=='ponytail' else row.get('caveman_mode_context') for row in audit)
        save(output/'skill_activation.json',{'variant':variant,'native_hook_activation_verified':active,'audit':audit})
        if not active:
            raise ValueError('Native hook activation was not observed in the measured trial')
    if variant=='serena':
        script = "import json,pathlib; p=pathlib.Path('/testbed/.serena/memories'); f=[x for x in p.rglob('*') if x.is_file()]; print(json.dumps({'memory_files_after':len(f),'memory_bytes_after':sum(x.stat().st_size for x in f),'project_state_exists':p.parent.is_dir(),'home_state_exists':pathlib.Path('/home/fakeroot/.serena-profile').is_dir()}))"
        state = json.loads(subprocess.check_output(['docker','exec',runner.container_name,'python3','-c',script],text=True))
        stdout = output/'log/agent_stdout.txt'
        events = [json.loads(line) for line in stdout.read_text().splitlines() if line.startswith('{')]
        calls = [e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='mcp_tool_call']
        state.update(memory_files_before=0,memory_bytes_before=0,natural_mcp_tool_calls=len(calls),mcp_calls_by_tool={tool:sum(item.get('tool')==tool for item in calls) for tool in {item.get('tool') for item in calls}},
            onboarding_observed=any('onboarding' in item.get('tool','') for item in calls))
        save(output/'serena_state.json',state)
        for source,target in (('/testbed/.serena','serena_project'),('/home/fakeroot/.serena-profile','serena_home')):
            exists = state['project_state_exists'] if target=='serena_project' else state['home_state_exists']
            if exists:
                subprocess.run(['docker','cp',runner.container_name+':'+source,str(output/target)],capture_output=True,check=True)
            elif target=='serena_home':
                raise ValueError('Serena home disappeared during the trial')
    return 0 if result.resolved else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('freeze','trial'))
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--variant',choices=VARIANTS)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    runtime = json.loads((ROOT/'profiles/runtime/manifest.json').read_text())
    activations = {variant:json.loads((ROOT/'reports'/f'{variant}_activation.json').read_text())
                   for variant in VARIANTS[1:] if (ROOT/'reports'/f'{variant}_activation.json').exists()}
    image = require_ready(runtime,activations)
    if args.action=='freeze':
        frozen = freeze_config(config,runtime,activations)
        with args.output.open('x') as output:
            json.dump(frozen,output,indent=2);output.write('\n')
        args.output.chmod(0o444)
        print(json.dumps({'frozen_config':str(args.output.resolve()),'setup_fingerprint':setup_fingerprint(frozen)[0]}))
        return 0
    if not args.variant:
        parser.error('--variant is required for a measured trial')
    if config['benchmark'].get('skill_runtime_image_id') != image or config.get('stage')!='phase3_frozen':
        raise ValueError('A frozen matched skill cohort is required')
    validate(config)
    lock = trial_lock(Path(config['resources']['runtime_root']))
    output = args.output.resolve();output.mkdir(parents=True,exist_ok=False);output.chmod(0o700)
    metadata = {'phase':'trial','state':'running','trial_kind':'measured','measured_comparison':True,'variant':args.variant,
        'started_at':datetime.now(timezone.utc).isoformat(),'model':config['codex']['model'],'reasoning_effort':config['codex']['reasoning_effort'],
        'implementation_commit':command('git','rev-parse','HEAD',cwd=ROOT),'experiment_sha256':hashlib.sha256(args.config.read_bytes()).hexdigest()}
    metadata['setup_fingerprint'],conditions=setup_fingerprint(config)
    save(output/'experiment.json',config);save(output/'comparison_conditions.json',conditions);save(output/'run_metadata.json',metadata)
    secrets = credential_values(Path.home()/'.codex/auth.json');started=time.monotonic();code=2
    try:
        before=read_quota();save(output/'quota_before.json',before);check_quota(before,config['resources']['quota_stop_percent'])
        code=run_trial(config,output,args.variant);metadata.update(state='finished',returncode=code)
    except Exception as error:
        metadata.update(state='failed',failure_category='quota_pressure' if str(error).startswith('Quota pressure') else 'skill_trial_failure',error=redact(str(error),secrets))
    finally:
        metadata['duration_seconds']=time.monotonic()-started
        save(output/'quota_after.json',read_quota());save(output/'run_metadata.json',metadata)
        redact_artifacts(output,secrets)
        for folder in ('serena_project','serena_home'):
            for path in (output/folder).rglob('*'):
                if path.is_file() and path.suffix in ('.md','.yml','.yaml','.toml'):
                    path.write_text(redact(path.read_text(),secrets))
        lock.close()
    print(json.dumps(metadata));return code


if __name__=='__main__':
    raise SystemExit(main())
