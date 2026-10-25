"""Restore retained native history without replaying completed model work."""

import hashlib
import json
from pathlib import Path
import selectors
import subprocess
import time


def legacy_rollout(raw, session):
    lines = raw.splitlines(keepends=True)
    header = json.loads(lines[0])
    if header.get('type') != 'session_meta' or header['payload'].get('id') != session:
        raise ValueError('Checkpoint has a different native session')
    if header['payload'].get('history_mode') not in ('paginated', 'legacy'):
        raise ValueError('Unsupported native history representation')
    events = [json.loads(line) for line in lines]
    turns = [event['payload']['turn_id'] for event in events
             if event.get('payload', {}).get('type') == 'task_complete']
    if not turns or events[-1].get('payload', {}).get('type') != 'task_complete':
        raise ValueError('Checkpoint is not a completed native turn boundary')
    header['payload']['history_mode'] = 'legacy'
    restored = (json.dumps(header) + '\n').encode() + b''.join(lines[1:])
    assert restored.splitlines()[1:] == raw.splitlines()[1:]
    return restored, {'source_sha256': hashlib.sha256(raw).hexdigest(),
                      'restored_sha256': hashlib.sha256(restored).hexdigest(),
                      'turn_ids': turns, 'messages_changed': False,
                      'transport': 'native legacy header; original response/event bytes retained'}


def verify_turns(response, expected):
    if 'error' in response:
        raise ValueError('Native history API rejected restored thread')
    result = response['result']
    turns = result['data']
    if result.get('nextCursor') or [turn['id'] for turn in turns] != expected:
        raise ValueError('Restored native history is incomplete or different')
    if any(turn['status'] != 'completed' for turn in turns):
        raise ValueError('Restored thread contains an unfinished turn')
    return len(turns)


def read_turns(container, session, timeout=30):
    """Read local history only: never resume a thread or start a model turn."""
    command = ['docker', 'exec', '-i', '--user', 'fakeroot', '-e', 'HOME=/home/fakeroot',
               '-w', '/testbed', container, 'codex', 'app-server', '--stdio']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, bufsize=0)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    def send(value):
        process.stdin.write((json.dumps(value) + '\n').encode())
        process.stdin.flush()
    send({'id': 1, 'method': 'initialize', 'params': {
        'clientInfo': {'name': 'benchmark-continuation-audit', 'version': '1.0'}}})
    pending = b''
    deadline = time.monotonic() + timeout
    try:
        while time.monotonic() < deadline:
            if not selector.select(1):
                continue
            chunk = process.stdout.read(65536)
            if not chunk:
                break
            pending += chunk
            while b'\n' in pending:
                line, pending = pending.split(b'\n', 1)
                event = json.loads(line)
                if event.get('id') == 1:
                    if 'error' in event:
                        raise ValueError('History reader initialization failed')
                    send({'method': 'initialized'})
                    send({'id': 2, 'method': 'thread/turns/list', 'params': {
                        'threadId': session, 'limit': 100, 'sortDirection': 'asc', 'itemsView': 'full'}})
                if event.get('id') == 2:
                    return event
        raise RuntimeError('Native history read timed out or exited')
    finally:
        selector.close()
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdin.close()
        process.stdout.close()


def copy_to(container, source, target):
    subprocess.run(['docker', 'cp', str(source), container + ':' + target],
                   check=True, capture_output=True)


def restore_history(setup, parent, output):
    files = list((Path(parent['artifacts_path']) / 'log/codex').glob('*.jsonl'))
    if len(files) != 1:
        raise ValueError('Exactly one native rollout is required')
    source = files[0]
    session = parent['continuous']['executor_session_id']
    restored, proof = legacy_rollout(source.read_bytes(), session)
    private = output / 'restored_rollout.jsonl'
    private.write_bytes(restored)
    date = source.name[len('rollout-'):][:10].replace('-', '/')
    target = '/home/fakeroot/.codex/sessions/' + date
    setup.docker_exec(['mkdir', '-p', target], user='root')
    destination = target + '/' + source.name
    if setup.docker_exec(['test', '-e', destination], check=False).returncode == 0:
        raise ValueError('Refuse to overwrite existing native history')
    copy_to(setup.container_name, private, destination)
    setup.docker_exec(['chown', '-R', 'fakeroot:fakeroot', '/home/fakeroot/.codex/sessions'], user='root')
    response = read_turns(setup.container_name, session)
    (output / 'native_history_read.json').write_text(json.dumps(response) + '\n')
    proof.update(session_id=session, completed_turns=verify_turns(response, proof['turn_ids']),
                 parent_trial=parent['trial_id'], new_model_calls=0)
    (output / 'restore_proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    return proof
