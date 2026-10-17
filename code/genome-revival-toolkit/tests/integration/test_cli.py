import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from unit.test_engine import goal_document
from dna_design_core.kernel import schemas


def cli(cwd,*arguments):
    result=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'src/dna_design_core/application/cli.py'),*map(str,arguments)],cwd=cwd,capture_output=True,text=True,encoding='utf-8')
    receipt=json.loads(result.stdout);schemas.require('receipt-v1',receipt)
    return result.returncode,receipt


class CliTests(unittest.TestCase):
    def test_source_import_through_public_cli_preserves_bytes_and_rejects_id_change(self):
        with tempfile.TemporaryDirectory(prefix='grt_输入_') as directory:
            folder=Path(directory);run=folder/'运行';source=folder/'构造.txt';source.write_bytes(b'abc')
            self.assertEqual(cli(folder,'run','create',run)[0],0)
            request=goal_document();request['sources']=[{'source_id':'s1','from':source.name,'input_origin':'user_file','as':'artifact','declared':{}}]
            path=folder/'请求.json';path.write_text(json.dumps(request,ensure_ascii=False),encoding='utf-8')
            code,receipt=cli(folder,'goal','declare','--run',run,'--request',path)
            self.assertEqual(code,0,receipt);digest=receipt['result']['goal_digest']
            goal=json.loads((run/'store/documents'/(digest+'.json')).read_text(encoding='utf-8'))
            self.assertEqual(goal['sources'][0]['path'],'inputs/s1/构造.txt')
            self.assertEqual(goal['sources'][0]['sha256'],'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            self.assertNotIn('from',goal['sources'][0])
            self.assertEqual((run/'inputs/s1/构造.txt').read_bytes(),b'abc')
            self.assertFalse(any(str(folder).encode('utf-8') in p.read_bytes() for p in run.rglob('*') if p.is_file()))
            info=json.loads((run/'run.json').read_text(encoding='utf-8'));self.assertEqual(set(info),{'run_id','created_at','release_id'})
            events=[json.loads(line) for line in (run/'journal.ndjson').read_text(encoding='utf-8').splitlines()]
            event=next(e for e in events if e['type']=='input.registered');self.assertEqual(event['payload']['size'],3)
            self.assertEqual(event['actor']['kind'],'program');self.assertEqual(event['payload']['declared_by']['kind'],'ai_host')
            before=(run/'journal.ndjson').read_bytes();source.write_bytes(b'abcd')
            request.update(version=2,parent_digest=digest,reason='Explicit change request.')
            path.write_text(json.dumps(request,ensure_ascii=False),encoding='utf-8')
            code,receipt=cli(folder,'goal','amend','--run',run,'--request',path)
            self.assertEqual(code,1);self.assertEqual(receipt['problems'][0]['category'],'INVALID_INPUT')
            self.assertEqual(before,(run/'journal.ndjson').read_bytes())

    def test_bad_command_is_a_receipt_and_doctor_installs_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            code,receipt=cli(d,'teleport');self.assertEqual(code,1);self.assertTrue(receipt['problems'])
            code,receipt=cli(d,'doctor');self.assertEqual(code,0)
            self.assertTrue(all(p['available'] for p in receipt['result']['packages'].values()))
            self.assertEqual(list(Path(d).iterdir()),[])


if __name__=='__main__':unittest.main()
