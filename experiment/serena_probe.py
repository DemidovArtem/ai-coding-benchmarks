"""Prove the shared runtime can serve Rust symbols over MCP with no network or credentials."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from experiment.runner import ROOT, save

PROBE = r'''
import asyncio,json,os,pathlib,tomllib
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    home=pathlib.Path('/tmp/home');home.mkdir()
    profile=home/'.serena-profile';profile.mkdir()
    (profile/'serena_config.yml').write_bytes(pathlib.Path('/probe/server_config.yml').read_bytes())
    server=tomllib.loads(pathlib.Path('/probe/config.toml').read_text())['mcp_servers']['serena']
    env={**server['env'],'HOME':str(home),'SERENA_HOME':str(profile),'CARGO_NET_OFFLINE':'true',
         'RUSTUP_HOME':'/usr/local/rustup','CARGO_HOME':'/usr/local/cargo'}
    async with stdio_client(StdioServerParameters(command=server['command'],args=server['args'],env=env,cwd='/testbed')) as streams:
        async with ClientSession(*streams) as session:
            initialized=await session.initialize()
            tools=await session.list_tools()
            assert 'get_symbols_overview' in [t.name for t in tools.tools]
            result=await session.call_tool('get_symbols_overview',{'relative_path':'src/lib.rs','depth':1})
            data=result.model_dump(mode='json')
            assert not result.isError and 'activation_fixture' in json.dumps(data),data
            print(json.dumps({'success':True,'rust_lsp_verified':True,'mcp_tool':'get_symbols_overview',
                'symbol':'activation_fixture','server':initialized.serverInfo.model_dump(),'result':data,
                'network':'none','credentials_mounted':False,'unprivileged_uid':os.getuid()}))

asyncio.run(asyncio.wait_for(main(),150))
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    runtime=json.loads((ROOT/'profiles/runtime/manifest.json').read_text())
    image=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}','ai-coding-skill-runtime:rust-1.88.0-python-3.13.14'],text=True).strip()
    context=Path(runtime['local_build_context'])
    assert hashlib.sha256((context/'node').read_bytes()).hexdigest()==runtime['node']['sha256']
    inventory_path=Path(runtime['inventory_path'])
    assert hashlib.sha256(inventory_path.read_bytes()).hexdigest()==runtime['inventory_sha256']
    for name,record in json.loads(inventory_path.read_text()).items():
        path=context/name
        if 'symlink' in record:
            assert path.is_symlink() and str(path.readlink())==record['symlink'],name
        else:
            assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],name
    fixture=output/'fixture';(fixture/'src').mkdir(parents=True)
    (fixture/'Cargo.toml').write_text('[package]\nname = "serena_activation_fixture"\nversion = "0.1.0"\nedition = "2021"\n')
    (fixture/'src/lib.rs').write_text('pub fn activation_fixture() -> usize { 42 }\n')
    subprocess.run(['git','init','-q',str(fixture)],check=True)
    subprocess.run(['git','-C',str(fixture),'config','--local','user.email','probe@example.invalid'],check=True)
    subprocess.run(['git','-C',str(fixture),'config','--local','user.name','Runtime probe'],check=True)
    subprocess.run(['git','-C',str(fixture),'add','.'],check=True)
    subprocess.run(['git','-C',str(fixture),'commit','-qm','Add neutral Rust fixture'],check=True)
    name='experiment-serena-probe-'+output.name
    try:
        result=subprocess.run(['docker','run','--rm','--name',name,'--network','none','--user','1000:1000',
            '--cap-drop','ALL','--security-opt','no-new-privileges','--memory','2g','--cpus','2',
            '--tmpfs','/tmp:exec,size=512m,mode=1777','--mount',f'type=bind,src={fixture},dst=/testbed',
            '--mount',f'type=bind,src={ROOT/"profiles/serena"},dst=/probe,readonly',
            '-e','PYTHONPATH=/opt/experiment-serena/site-packages','-e','PYTHONDONTWRITEBYTECODE=1',
            '--entrypoint','/opt/experiment-serena/python/bin/python3',image,'-c',PROBE],capture_output=True,text=True,timeout=180)
        (output/'stdout.jsonl').write_text(result.stdout);(output/'stderr.log').write_text(result.stderr)
        if result.returncode:
            raise RuntimeError('Offline MCP/Rust probe failed; inspect '+str(output/'stderr.log'))
        proof=json.loads(result.stdout.strip());proof['image_id']=image
        assert proof['success'] and proof['unprivileged_uid']==1000
        save(output/'result.json',proof)
        runtime.update(status='common_runtime_offline_mcp_rust_verified',image_id=image,rust_lsp_verified=True,
                       offline_probe_path=str(output),offline_probe_sha256=hashlib.sha256((output/'result.json').read_bytes()).hexdigest())
        save(ROOT/'profiles/runtime/manifest.json',runtime)
        budget=json.loads((ROOT/'profiles/runtime/download_budget.json').read_text())
        budget.update(status='user_approved_components_installed',registry_images_downloaded=0)
        save(ROOT/'profiles/runtime/download_budget.json',budget)
        print(json.dumps(proof))
    finally:
        subprocess.run(['docker','rm','-f',name],capture_output=True)


if __name__=='__main__':
    main()
