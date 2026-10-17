import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from dna_design_core.storage.journal import Journal
from dna_design_core.storage.store import Store
from dna_design_core.storage.lock import RunLock
from dna_design_core.kernel.errors import ToolkitError


class StorageTests(unittest.TestCase):
    def test_append_tail_recovery_and_no_middle_repair(self):
        with tempfile.TemporaryDirectory() as d:
            journal=Journal(Path(d),'a'*16)
            first=journal.append('run.abandoned',{'reason':'Synthetic stop.','by':{'kind':'ai_host','name':'test'}},writer='engine')
            original=journal.path.read_bytes()
            with journal.path.open('ab') as stream:stream.write(b'{"seq":')
            journal.recover()
            events=journal.events()
            self.assertEqual(events[0],first)
            self.assertEqual(events[1]['type'],'journal.recovered')
            self.assertEqual(events[1]['payload']['discarded_bytes'],7)
            self.assertTrue(journal.path.read_bytes().startswith(original))
            broken=journal.path.read_bytes().replace(b'Synthetic stop.',b'Changed content',1)
            journal.path.write_bytes(broken)
            with self.assertRaises(ToolkitError):journal.recover()
            self.assertEqual(journal.path.read_bytes(),broken)

    def test_store_is_content_addressed_and_detects_change(self):
        with tempfile.TemporaryDirectory() as d:
            store=Store(Path(d))
            value={'count':9};identity=store.put('documents',value)
            before=store.path('documents',identity).read_bytes()
            self.assertEqual(store.put('documents',{'count':9}),identity)
            self.assertEqual(store.path('documents',identity).read_bytes(),before)
            returned=store.get('documents',identity);returned['count']=31
            self.assertEqual(store.get('documents',identity),{'count':9})
            store.path('documents',identity).write_text('{"count":31}',encoding='utf-8')
            with self.assertRaises(ToolkitError) as caught:store.get('documents',identity)
            self.assertEqual(caught.exception.problem.code,'STORE_CORRUPT')

    def test_lock_excludes_another_writer_and_releases(self):
        with tempfile.TemporaryDirectory() as d:
            with RunLock(Path(d)):
                with self.assertRaises(ToolkitError) as caught:
                    with RunLock(Path(d)):pass
                self.assertEqual(caught.exception.problem.code,'RUN_LOCKED')
            with RunLock(Path(d)):pass

    def test_writer_matrix_rejects_wrong_owner(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ToolkitError):
                Journal(Path(d),'a'*16).append('run.completed',{'pipeline_digest':'1'*64,'executed_steps':[]},writer='record')
            self.assertFalse((Path(d)/'journal.ndjson').exists())


if __name__=='__main__':unittest.main()
