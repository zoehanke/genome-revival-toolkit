"""Require real CLI sealing, independent oracles and portable verification.

Run existing acceptance scripts unchanged. Add missing Construct portable checks;
their older diagnostic text is retained in the original results, not trusted.
Synthetic developer-assisted computation only. No wet-laboratory claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def write(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')


def run(output,case):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    scripts={'cut-plasmid':('run_cut_plasmid.py',['--out']),
             'construct':('run_construct.py',[]),
             'genome-identity':('run_genome_identity.py',['--out']),
             'revival-evidence':('run_revival_evidence.py',['--out'])}
    script,flags=scripts[case];folder=output/'original-acceptance'
    argv=[sys.executable,'-X','utf8','-B',str(ROOT/'tests/e2e'/script),*flags,str(folder)]
    process=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    (output/'acceptance.stdout.txt').write_text(process.stdout,encoding='utf-8')
    (output/'acceptance.stderr.txt').write_text(process.stderr,encoding='utf-8')
    assert process.returncode==0,process.stderr
    result=json.loads((folder/('results.json' if case=='construct' else 'SUMMARY.json')).read_text(encoding='utf-8'))
    if case=='cut-plasmid':
        assert result['acceptance_passed'] and result['seal_created'] and result['portable_verify_performed'],result
    elif case=='genome-identity':
        assert result['cases']['different_sizes']['verified'],result
        assert result['cases']['handoff_hash']['seal_refused'],result
    elif case=='revival-evidence':
        assert len(result['cases'])==5 and all(row['verify'] for row in result['cases'].values()),result
    else:
        portable={}
        for method in ('pcr','gibson'):
            row=result[method]
            assert row['oracle']['passed'] and row['seal']['result']['sealed'] and row['verify']['result']['verified'],row
            package=Path(row['seal']['result']['manifest']).parent;run_root=folder/method/'run'
            copied=output/'portable'/method/package.name;copied.parent.mkdir(parents=True)
            shutil.copytree(package,copied)
            # Preserve the failure/run history, but make its original path unavailable.
            retained=run_root.with_name('original-run-retained')
            assert run_root.resolve().is_relative_to(output) and retained.resolve().is_relative_to(output)
            run_root.rename(retained)
            before={path.relative_to(copied).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in copied.rglob('*') if path.is_file()}
            checked=subprocess.run([sys.executable,'-X','utf8','-B','-m','dna_design_core.application.cli','verify',str(copied)],
                                   cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
            (output/(method+'-portable.stdout.txt')).write_text(checked.stdout,encoding='utf-8')
            (output/(method+'-portable.stderr.txt')).write_text(checked.stderr,encoding='utf-8')
            receipt=json.loads(checked.stdout)
            assert checked.returncode==0 and receipt['result']['verified'],receipt
            after={path.relative_to(copied).as_posix():hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in copied.rglob('*') if path.is_file()}
            assert before==after,'Offline verification modified sealed files'
            portable[method]={'verified':True,'files':before,'oracle':row['oracle'],
                              'original_path_unavailable':not run_root.exists(),
                              'legacy_diagnostic':row['copied_sealed_package_verify']}
        result={'methods':portable}
    summary={'case':case,'result':result,'public_cli':True,'independent_oracles':True,
             'evidence_kind':'developer-assisted synthetic computation',
             'laboratory':'PLANNED / NOT_PERFORMED','official_gitlab_ci':'not executed','github_ci':'not run'}
    write(output/'SUMMARY.json',summary);return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--case',choices=['cut-plasmid','construct','genome-identity','revival-evidence'],required=True)
    args=parser.parse_args();result=run(args.out,args.case)
    print(json.dumps({'case':args.case,'accepted':True,'details':str(args.out/'SUMMARY.json')}))
