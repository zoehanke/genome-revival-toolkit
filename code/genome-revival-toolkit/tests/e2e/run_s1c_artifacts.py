"""Retain CLI proof of byte-preserving artifact delivery and portable verification."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
from unit.test_s1c_artifacts import artifact_run


def run(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);commands=[]
    def command(verb,*,root,kit_dirs,request=None,**options):
        argv=[sys.executable,'-X','utf8','-B','-m','dna_design_core.application.cli',*verb.split()]
        if verb in {'run create','verify'}:argv.append(str(options['directory']))
        argv.extend(['--run',str(root)])
        for path in kit_dirs:argv.extend(['--kit-dir',str(path)])
        if request is not None:
            path=output/('request-'+str(len(commands))+'.json');path.write_text(json.dumps(request,indent=2)+'\n',encoding='utf-8')
            argv.extend(['--request',str(path)])
        result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');receipt=json.loads(result.stdout)
        commands.append({'verb':verb,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        (output/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
        return receipt
    original,kit,call=artifact_run(output/'case',bytes([0,255,13,10])+'合成结果'.encode('utf-8'),dispatch=command)
    sealed=call('seal');assert not sealed['problems'] and sealed['result']['sealed'],sealed
    package=Path(sealed['result']['manifest']).parent
    assert call('verify',directory=package)['result']['verified']
    copied=output/'portable'/package.name;shutil.copytree(package,copied)
    retained=output/'original-retained'
    assert original.resolve().is_relative_to(output) and retained.resolve().is_relative_to(output)
    original.rename(retained)
    verified=command('verify',root=copied,directory=copied,kit_dirs=[kit]);assert verified['result']['verified'],verified
    path=copied/'result.dat';data=path.read_bytes();path.write_bytes(bytes([data[0]^1])+data[1:])
    rejected=command('verify',root=copied,directory=copied,kit_dirs=[kit]);assert rejected['problems'][0]['code']=='STORE_CORRUPT',rejected
    summary={'sealed':True,'portable_verify':True,'single_byte_tamper':'STORE_CORRUPT','commands':len(commands),'wet_laboratory':'NOT_PERFORMED'}
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    print(json.dumps(run(parser.parse_args().out),indent=2))
