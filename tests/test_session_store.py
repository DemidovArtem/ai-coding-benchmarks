import hashlib
from pathlib import Path
import sqlite3
import tempfile
import unittest

from experiment.session_store import backup_stores


class SessionStoreTests(unittest.TestCase):
    def test_wal_backup_hash_stays_valid_after_connection_close(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            source=root/'source';source.mkdir()
            connection=sqlite3.connect(source/'state_5.sqlite')
            try:
                connection.execute('pragma journal_mode=wal')
                connection.execute('create table turns (id text)')
                connection.execute("insert into turns values ('retained')")
                connection.commit()
                output=root/'backup'
                manifest=backup_stores(source,output)
                self.assertEqual(manifest['state_5.sqlite'],hashlib.sha256((output/'state_5.sqlite').read_bytes()).hexdigest())
                copy=sqlite3.connect((output/'state_5.sqlite').resolve().as_uri()+'?mode=ro',uri=True)
                try:self.assertEqual(copy.execute('select id from turns').fetchall(),[('retained',)])
                finally:copy.close()
                with self.assertRaises(FileExistsError):backup_stores(source,output)
            finally:connection.close()
