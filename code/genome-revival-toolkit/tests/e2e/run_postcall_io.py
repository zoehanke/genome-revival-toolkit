"""Persist constructed post-call write controls through the public CLI."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tests.integration.test_postcall_io import run_case


def run(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    calls=[]

    def dispatch(verb,*,root,kit_dirs,**options):
        index=len(calls);audit=output/f'network-{index:03}.json'
        arguments=[*verb.split(),'--run',str(root),'--kit-dir',str(kit_dirs[0])]
        if 'directory' in options:arguments.append(str(options['directory']))
        if 'request' in options:
            request=output/f'request-{index:03}.json'
            request.write_text(json.dumps(options['request'],indent=2)+'\n',encoding='utf-8')
            arguments+=['--request',str(request)]
        # Deliberately exercise the real CLI with normal bytecode caching.
        # Importer bookkeeping must not become a false capability violation.
        process=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tests/e2e/network_guard.py'),
            str(audit),str(ROOT/'src/dna_design_core/application/cli.py'),*arguments],
            cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        (output/f'{index:03}.stdout.txt').write_text(process.stdout,encoding='utf-8')
        (output/f'{index:03}.stderr.txt').write_text(process.stderr,encoding='utf-8')
        result=json.loads(process.stdout);network=json.loads(audit.read_text(encoding='utf-8'))
        calls.append({'verb':verb,'exit_code':process.returncode,'receipt':result,'network':network})
        assert network['attempts']==0,calls[-1]
        return result

    cases=[
        ('allowed','(ctx.workdir/"allowed.txt").write_text("allowed",encoding="utf-8")',
         {'effects':('writes_files',)},'COMPLETED'),
        ('outside','(ctx.workdir.parent.parent/"outside.txt").write_text("written",encoding="utf-8")',{},'HALTED'),
        ('input','Path(file).write_text("changed",encoding="utf-8")',{'effects':('writes_files',)},'HALTED'),
        ('raises','(ctx.workdir.parent.parent/"outside.txt").write_text("written",encoding="utf-8")\nraise ValueError("constructed failure")',{},'HALTED'),
        ('module-load','pass',{'module_write':True},'HALTED'),
        ('caught-child','try:\n    ctx.call("contract_probe.child",inputs={},params={})\nexcept Exception:\n    pass',
         {'effects':('writes_files',),'composite':True,'child':'(ctx.workdir.parent.parent/"outside.txt").write_text("written",encoding="utf-8")'},'HALTED'),
    ]
    results=[]
    for name,body,options,expected in cases:
        folder=output/name;folder.mkdir()
        root,receipt=run_case(folder,body,dispatch=dispatch,**options)
        assert receipt['state']==expected,receipt
        code=receipt['result'].get('failure',{}).get('code')
        assert code==('CAPABILITY_OUTPUT_INVALID' if expected=='HALTED' else None),receipt
        results.append({'case':name,'expected_state':expected,'actual_state':receipt['state'],'code':code})
    # Inspect bytes after detection: this proves detection, not prevention.
    assert (output/'allowed/run/work/s1/allowed.txt').read_bytes()==b'allowed'
    assert (output/'outside/run/outside.txt').read_bytes()==b'written'
    assert (output/'input/run/inputs/input/source.txt').read_bytes()==b'changed'
    assert (output/'raises/run/outside.txt').read_bytes()==b'written'
    assert (output/'module-load/import-side-effect.txt').read_bytes()==b'written'
    assert (output/'caught-child/run/outside.txt').read_bytes()==b'written'
    value={'cases':results,'cli_calls':len(calls),'connection_attempts':sum(c['network']['attempts'] for c in calls),
           'meaning':'Post-call detection of completed writes; no sandbox, prevention or rollback.'}
    (output/'SUMMARY.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    (output/'CLI-RECEIPTS.json').write_text(json.dumps(calls,indent=2)+'\n',encoding='utf-8')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().out),indent=2))
