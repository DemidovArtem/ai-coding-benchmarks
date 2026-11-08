"""Verify Python symbols over the pinned local MCP server without model calls."""

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
    env={**server['env'],'HOME':str(home),'SERENA_HOME':str(profile)}
    async with stdio_client(StdioServerParameters(command=server['command'],args=server['args'],env=env,cwd='/testbed')) as streams:
        async with ClientSession(*streams) as session:
            initialized=await session.initialize()
            result=await session.call_tool('get_symbols_overview',{'relative_path':'fixture.py','depth':1})
            data=result.model_dump(mode='json')
            assert not result.isError and 'activation_fixture' in json.dumps(data),data
            print(json.dumps({'success':True,'python_lsp_verified':True,'mcp_tool':'get_symbols_overview',
                'symbol':'activation_fixture','server':initialized.serverInfo.model_dump(),'result':data,
                'network':'none','credentials_mounted':False,'unprivileged_uid':os.getuid(),'model_calls':0}))

asyncio.run(asyncio.wait_for(main(),150))
'''


def main():
    output = ROOT / 'results/scikit_preflight/python_mcp'
    output.mkdir(parents=True, exist_ok=False)
    fixture = output / 'fixture'
    fixture.mkdir()
    (fixture / 'fixture.py').write_text('def activation_fixture(value: int) -> int:\n    return value + 1\n')
    subprocess.run(['git', 'init', '-q', str(fixture)], check=True)
    runtime = json.loads((ROOT / 'profiles/scikit_runtime/manifest.json').read_text())
    image = runtime['image_id']
    result = subprocess.run(['docker', 'run', '--rm', '--pull=never', '--network', 'none', '--user', '1000:1000',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--memory', '2g', '--cpus', '2',
        '--tmpfs', '/tmp:exec,size=512m,mode=1777', '--mount', f'type=bind,src={fixture},dst=/testbed',
        '--mount', f'type=bind,src={ROOT / "profiles/scikit_serena"},dst=/probe,readonly',
        '-e', 'PYTHONPATH=/opt/experiment-serena/site-packages', '-e', 'PYTHONDONTWRITEBYTECODE=1',
        '--entrypoint', '/opt/experiment-serena/python/bin/python3', image, '-c', PROBE],
        capture_output=True, text=True, timeout=180)
    (output / 'stdout.jsonl').write_text(result.stdout)
    (output / 'stderr.log').write_text(result.stderr)
    if result.returncode:
        raise RuntimeError('Offline Python MCP probe failed; inspect private probe logs')
    proof = json.loads(result.stdout.strip())
    if not proof['success'] or proof['unprivileged_uid'] != 1000:
        raise ValueError('Python probe identity or result differs')
    proof['image_id'] = image
    save(ROOT / 'reports/scikit_python_mcp_preflight.json', proof)
    runtime.update(status='python_mcp_offline_verified', python_lsp_verified=True,
                   offline_probe='reports/scikit_python_mcp_preflight.json')
    save(ROOT / 'profiles/scikit_runtime/manifest.json', runtime)
    print('Offline Python symbol call verified; zero model calls.')


if __name__ == '__main__':
    main()
