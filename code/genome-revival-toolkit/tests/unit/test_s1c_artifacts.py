"""File delivery via public API; raw-byte oracles precede implementation."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from dna_design_core.application import api
from fixtures.contract_probe import action, port, build, goal, plan, step


def artifact_run(folder,payload=b'abc',dispatch=None):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    original=folder/'synthetic.dat';original.write_bytes(payload)
    declaration=action('copy_file',[port('file','artifact',input=True)],[port('file','artifact')])
    declaration['outputs'][0]['output_role']='analysis';declaration['effects']=['reads_files','writes_files']
    kit=build(folder/'external',[(declaration,
        'def copy_file(ctx, file):\n    destination=ctx.workdir/"report.dat"\n    destination.write_bytes(file.read_bytes())\n    return Outcome(artifacts={"file":destination})\n')])
    run=folder/'run';receipts=[]
    def call(verb,**arguments):
        result=(dispatch or api.call)(verb,root=run,kit_dirs=[kit],**arguments);receipts.append({'verb':verb,'receipt':result})
        (folder/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8',newline='\n')
        return result
    created=call('run create',directory=run);assert not created['problems'],created
    request=goal([{'source_id':'payload','from':str(original),'as':'artifact','input_origin':'user_file','declared':{}}])
    request['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'constructed','status':'active'}]
    declared=call('goal declare',request=request);assert not declared['problems'],declared
    submitted=call('pipeline submit',request=plan(declared['result']['goal_digest'],[step('s1','copy_file',{'file':{'source':'payload'}})],{'step':'s1','port':'file'}))
    assert not submitted['problems'],submitted
    executed=call('run execute');assert executed['state']=='COMPLETED',executed
    return run,kit,call


class ArtifactDeliveryTests(unittest.TestCase):
    def test_raw_file_can_seal_move_and_verify_without_original_run(self):
        for payload in [b'abc',bytes([0,255,13,10])+ '合成结果'.encode('utf-8')]:
            with self.subTest(payload_size=len(payload)),tempfile.TemporaryDirectory() as folder:
                run,kit,call=artifact_run(folder,payload)
                sealed=call('seal');self.assertEqual(sealed['problems'],[],sealed)
                self.assertTrue(sealed['result']['sealed'],sealed)
                package=Path(sealed['result']['manifest']).parent
                self.assertEqual((package/'result.dat').read_bytes(),payload)
                objects=list((package/'store/artifacts').iterdir());self.assertEqual(len(objects),1)
                self.assertEqual(objects[0].read_bytes(),payload)
                self.assertTrue(call('verify',directory=package)['result']['verified'])
                copied=Path(folder)/'portable'/package.name;shutil.copytree(package,copied)
                retained=Path(folder)/'retained-original'
                self.assertTrue(run.resolve().is_relative_to(Path(folder).resolve()));self.assertTrue(retained.resolve().is_relative_to(Path(folder).resolve()))
                run.rename(retained)
                checked=api.call('verify',directory=copied,kit_dirs=[kit]);self.assertTrue(checked['result']['verified'],checked)
                self.assertEqual((copied/'result.dat').read_bytes(),payload)

    def test_a_single_changed_artifact_byte_is_integrity_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            run,kit,call=artifact_run(folder)
            sealed=call('seal');self.assertEqual(sealed['problems'],[],sealed)
            self.assertTrue(sealed['result']['sealed'],sealed)
            package=Path(sealed['result']['manifest']).parent
            for relative in ['result.dat','store/artifacts/'+next((package/'store/artifacts').iterdir()).name]:
                with self.subTest(relative=relative):
                    path=package/relative;original=path.read_bytes();path.write_bytes(b'z'+original[1:])
                    rejected=api.call('verify',directory=package,kit_dirs=[kit])
                    self.assertEqual(rejected['problems'][0]['code'],'STORE_CORRUPT',rejected)
                    path.write_bytes(original)


if __name__=='__main__':unittest.main()
