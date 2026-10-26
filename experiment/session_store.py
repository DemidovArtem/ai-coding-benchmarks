"""Capture native SQLite stores, hashing only fully closed backup files."""

from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3


def backup_stores(source, destination):
    source, destination = Path(source), Path(destination)
    destination.mkdir(mode=0o700)
    manifest = {}
    for name in ('state_5.sqlite', 'thread_history_1.sqlite'):
        original, target = source/name, destination/name
        if not original.exists():
            continue
        with closing(sqlite3.connect(original.resolve().as_uri()+'?mode=ro', uri=True)) as before:
            with closing(sqlite3.connect(target)) as after:
                before.backup(after)
                if after.execute('pragma quick_check').fetchone()[0] != 'ok':
                    raise ValueError('Native SQLite backup failed integrity check')
        manifest[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    if 'state_5.sqlite' not in manifest:
        raise ValueError('Native state database is missing')
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    import sys
    backup_stores(sys.argv[1], sys.argv[2])
