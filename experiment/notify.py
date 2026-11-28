"""Send deduplicated operational notifications through an existing OpenClaw host."""

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess


def send(config_path, event, message, *, dry_run=False):
    """Keep credentials remote; retain ambiguous sends without automatically repeating them."""
    config_path = Path(config_path)
    config = json.loads(config_path.read_text())
    host, target = config['ssh_host'], str(config['telegram_target'])
    if not re.fullmatch(r'[\w.@-]+', host) or host.startswith('-'):
        raise ValueError('Invalid notification SSH host')
    if not re.fullmatch(r'[1-9][0-9]*', target):
        raise ValueError('Notifications require a verified private Telegram chat')
    if not event or not message.strip():
        raise ValueError('Event and message are required')
    directory = config_path.parent / 'events'
    directory.mkdir(mode=0o700, exist_ok=True)
    path = directory / (hashlib.sha256(event.encode()).hexdigest() + '.json')
    remote = ['timeout', '45', 'openclaw', 'message', 'send', '--channel', 'telegram',
              '--target', target, '--message', message, '--json']
    if dry_run:
        remote.append('--dry-run')
    command = ['ssh', '-i', str(Path(config['identity_file']).expanduser()),
               '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
               '-o', 'ServerAliveInterval=5', '-o', 'ServerAliveCountMax=2',
               '-o', 'StrictHostKeyChecking=yes', host, shlex.join(remote)]
    with (directory / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        previous = json.loads(path.read_text()) if path.exists() else None
        if previous and not dry_run:
            if previous['message'] != message:
                raise ValueError('Notification event reused for different content')
            if previous['status'] in ('sent', 'pending', 'uncertain'):
                return previous
        record = {'event': event, 'message': message, 'status': 'pending',
                  'updated_at': datetime.now(timezone.utc).isoformat()}

        def preserve():
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
            temporary.replace(path)

        if not dry_run:
            preserve()
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            reply = json.loads(result.stdout)
            payload = reply.get('payload') or {}
            if result.returncode == 0 and dry_run and reply.get('dryRun') is True:
                return {**record, 'status': 'dry_run_verified'}
            if result.returncode == 0 and payload.get('ok') is True and payload.get('messageId'):
                record.update(status='sent', message_id=str(payload['messageId']))
            else:
                record.update(status='uncertain', error='No confirmed Telegram delivery receipt')
        except OSError:
            record.update(status='failed', error='SSH process could not start')
        except (subprocess.TimeoutExpired, ValueError, TypeError, AttributeError):
            # The remote may have delivered before the connection or parser failed.
            record.update(status='uncertain', error='Delivery outcome unknown; reconcile before retry')
        if not dry_run:
            preserve()
        return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--event', required=True)
    parser.add_argument('--message-file', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    record = send(args.config, args.event, args.message_file.read_text(), dry_run=args.dry_run)
    print(json.dumps({k: record[k] for k in ('event', 'status', 'message_id', 'error') if k in record}))
    return 0 if record['status'] in ('sent', 'dry_run_verified') else 1


if __name__ == '__main__':
    raise SystemExit(main())
