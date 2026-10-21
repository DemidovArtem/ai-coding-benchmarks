"""Retain and audit Serena memory inside one isolated continuous trajectory."""

import hashlib
import json
from pathlib import Path
import subprocess

from experiment.serena_required import verify_required_usage

POLICY = Path(__file__).resolve().parents[1] / 'profiles/serena_continuous/AGENTS.md'


def install_policy(setup):
    target = '/home/fakeroot/.codex/AGENTS.md'
    subprocess.run(['docker', 'cp', str(POLICY), setup.container_name + ':' + target], check=True, capture_output=True)
    setup.docker_exec(['chown', 'root:root', target], user='root')
    setup.docker_exec(['chmod', '0444', target], user='root')
    expected = hashlib.sha256(POLICY.read_bytes()).hexdigest()
    if setup.docker_exec(['sha256sum', target]).stdout.split()[0] != expected:
        raise ValueError('Serena continuous policy differs from its pinned source')
    # Trial memory must survive turns without entering source commits or graded snapshots.
    setup.docker_exec(['python3', '-c',
        r"from pathlib import Path; p=Path('/testbed/.git/info/exclude'); p.write_text(p.read_text()+'\n/.serena/\n')"], user='root')
    return expected


def memory_state(setup):
    if setup.docker_exec_git('ls-files', '--', '.serena').stdout.strip():
        raise ValueError('Serena memory entered a source commit')
    result = setup.docker_exec(['python3', '-c', '''import hashlib,json,pathlib
root=pathlib.Path('/testbed/.serena/memories')
files={str(p.relative_to(root)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
       for p in sorted(root.rglob('*')) if p.is_file()}
print(json.dumps({'files':files,'count':len(files),'bytes':sum(p['bytes'] for p in files.values())}))
'''])
    if result.returncode:
        raise RuntimeError('Could not inspect Serena memory')
    return json.loads(result.stdout)


def verify_memory_boundary(before, previous):
    if previous is None:
        if before['count'] or before['files']:
            raise ValueError('An independent Serena trajectory must start with cold memory')
    elif not before['count'] or before != previous:
        raise ValueError('Serena memory changed or disappeared between sequential turns')


def nonempty_symbols(item):
    for block in (item.get('result') or {}).get('content', []):
        if block.get('type') != 'text':
            continue
        try:
            data = json.loads(block['text'])
        except (ValueError, KeyError):
            continue
        if isinstance(data, list) and data or isinstance(data, dict) and any(isinstance(v, list) and v for v in data.values()):
            return True
    return False


def verify_usage(events, read_item_id, before):
    # The verified, exact task-delivery read is the sole shell exception before orientation.
    filtered = [event for event in events if not (event.get('type') == 'item.completed'
                and event.get('item', {}).get('id') == read_item_id)]
    if not before['count']:
        return {**verify_required_usage(filtered), 'memory_mode': 'cold'}
    items = [event['item'] for event in filtered if event.get('type') == 'item.completed'
             and event.get('item', {}).get('type') in ('command_execution', 'file_change', 'mcp_tool_call')]
    calls = [(n, item) for n, item in enumerate(items) if item.get('type') == 'mcp_tool_call'
             and item.get('server') == 'serena' and item.get('status') == 'completed' and not item.get('error')]
    if not calls or calls[0][0] != 0 or calls[0][1].get('tool') != 'initial_instructions':
        raise ValueError('Warm Serena turn must begin with its instructions after task delivery')
    if any(item.get('tool') == 'onboarding' for _, item in calls):
        raise ValueError('Warm Serena turn must reuse memory instead of restarting onboarding')
    reads, semantic, writes = [], [], []
    for n, item in calls:
        if item.get('tool') == 'read_memory':
            args = item.get('arguments') or {}
            if isinstance(args, str):
                args = json.loads(args)
            name = args.get('memory_name')
            if name in before['files'] or str(name) + '.md' in before['files']:
                reads.append(n)
        if item.get('tool') in ('find_symbol', 'get_symbols_overview') and nonempty_symbols(item):
            semantic.append(n)
        if item.get('tool') == 'write_memory':
            writes.append(n)
    first_shell_or_edit = next((n for n, item in enumerate(items) if item['type'] in ('command_execution', 'file_change')
        or item.get('tool') in ('replace_symbol_body', 'replace_in_files', 'rename_symbol', 'safe_delete_symbol',
                               'insert_after_symbol', 'insert_before_symbol')), len(items))
    if not reads or not semantic or not writes or not (min(reads) < min(semantic) < min(writes) < first_shell_or_edit):
        raise ValueError('Warm Serena turn must read retained memory, navigate symbols and write memory before source work')
    return {'required_usage_verified': True, 'memory_mode': 'warm', 'observed_mcp_tool_calls': len(calls),
            'semantic_calls': len(semantic), 'retained_memory_read_verified': True, 'memory_write_observed': True}


def preserve_memory(setup, output, before, usage):
    after = memory_state(setup)
    if not after['count']:
        raise ValueError('No Serena memory remains after the completed turn')
    subprocess.run(['docker', 'cp', setup.container_name + ':/testbed/.serena/memories',
                    str(output / 'serena_memories')], check=True, capture_output=True)
    state = {**usage, 'memory_files_before': before['count'], 'memory_files_after': after['count'],
             'memory_bytes_before': before['bytes'], 'memory_bytes_after': after['bytes'],
             'measured_mcp_tool_calls': usage['observed_mcp_tool_calls'],
             'usage_policy': 'required cold onboarding; required retained-memory reuse on warm turns',
             'before': before, 'after': after}
    (output / 'serena_state.json').write_text(json.dumps(state, indent=2) + '\n')
    return after
