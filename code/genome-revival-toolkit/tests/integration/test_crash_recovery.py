from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dna_design_core.storage.journal import Journal
import json


CHILD='''import os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[2])
from dna_design_core.storage.journal import Journal
root=Path(sys.argv[1]);journal=Journal(root,"a"*16)
journal.append("run.abandoned",{"reason":"Constructed complete event.","by":{"kind":"ai_host","name":"test"}},writer="engine")
with journal.path.open("ab") as stream:
    stream.write(b'{"seq":');stream.flush();os.fsync(stream.fileno())
print("ready",flush=True)
sys.stdin.read()
'''

EXECUTING_CHILD='''import os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[2])
from dna_design_core.application import api
from dna_design_core.engine.invoker import Invoker
root=Path(sys.argv[1]);api.run_create(directory=root)
goal={"schema":"goal-v1","version":1,"parent_digest":None,"original_request":"Synthetic interrupted calculation.","sources":[],"declared_context":[],"targets":[{"id":"t1","role":"analysis","required":True}],"constraints":[],"intents":[]}
declared=api.goal_declare(root=root,request=goal)
plan={"schema":"pipeline-v1","version":1,"goal_digest":declared["result"]["goal_digest"],"steps":[{"step_id":"s1","use":"seq.reverse_complement","inputs":{"sequence":{"literal":"AGTCAGAA"}},"params":{},"why":"Calculate a constructed reverse complement."}],"outputs":[{"name":"result","from":{"step":"s1","port":"result"},"target":"t1"}]}
assert not api.pipeline_submit(root=root,request=plan)["problems"]
def interrupted(self,*args,**kwargs):
    with self.session.journal.path.open("ab") as stream:
        stream.write(b'{"seq":');stream.flush();os.fsync(stream.fileno())
    print("ready",flush=True);sys.stdin.read()
Invoker._invoke=interrupted
api.run_execute(root=root)
'''


class CrashRecoveryTests(unittest.TestCase):
    def test_public_execute_recovers_killed_tail_and_records_interrupted_step(self):
        with tempfile.TemporaryDirectory() as d:
            run=Path(d)/'run'
            process=subprocess.Popen([sys.executable,'-X','utf8','-B','-c',EXECUTING_CHILD,str(run),str(ROOT/'src')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
            try:
                self.assertEqual(process.stdout.readline().strip(),'ready')
                process.kill();process.communicate(timeout=10)
            finally:
                if process.poll() is None:process.kill();process.communicate(timeout=10)
            result=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'src/dna_design_core/application/cli.py'),'run','execute','--run',str(run)],capture_output=True,text=True,encoding='utf-8')
            receipt=json.loads(result.stdout);self.assertEqual(result.returncode,1,receipt)
            self.assertEqual(receipt['state'],'HALTED');self.assertEqual(receipt['problems'][0]['code'],'STEP_INTERRUPTED')
            events=Journal(run,receipt['run_id']).events()
            self.assertTrue(any(e['type']=='journal.recovered' and e['payload']['discarded_bytes']==7 for e in events))
            self.assertFalse(any(e['type']=='step.completed' for e in events))

    def test_killed_writer_recovers_only_partial_tail(self):
        with tempfile.TemporaryDirectory() as d:
            process=subprocess.Popen([sys.executable,'-X','utf8','-B','-c',CHILD,d,str(ROOT/'src')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
            try:
                self.assertEqual(process.stdout.readline().strip(),'ready')
                process.kill();process.communicate(timeout=10)
            finally:
                if process.poll() is None:process.kill();process.communicate(timeout=10)
            journal=Journal(Path(d),'a'*16);before=journal.path.read_bytes();self.assertTrue(before.endswith(b'{"seq":'))
            journal.recover();events=journal.events()
            self.assertEqual(len(events),2);self.assertEqual(events[0]['payload']['reason'],'Constructed complete event.')
            self.assertEqual(events[1]['type'],'journal.recovered');self.assertEqual(events[1]['payload']['discarded_bytes'],7)


if __name__=='__main__':unittest.main()
