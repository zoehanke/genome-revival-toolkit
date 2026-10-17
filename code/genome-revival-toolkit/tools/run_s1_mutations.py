"""Run the three specified S1 mutations on throwaway copies, never the source tree."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
MUTATIONS=[
 ('replay','src/dna_design_core/capabilities/builtin/checks.py',
  'fields=[key for key in expected if expected[key]!=actual[key]]','fields=[]',
  'tests.unit.test_assurance.AssuranceTests.test_replay_reads_original_inputs_and_does_not_write_run'),
 ('obligation_union','src/dna_design_core/assurance/obligations.py',
  "for check in snapshot['profiles']['always']:add(check)",'for check in []:add(check)',
  'tests.unit.test_assurance.AssuranceTests.test_profile_union_cannot_be_reduced_by_roles_or_missing_loaded_kit'),
 ('journal_chain','src/dna_design_core/storage/chain.py',
  "value['hash']!=ids.event_hash(value)",'False',
  'tests.unit.test_storage.StorageTests.test_append_tail_recovery_and_no_middle_repair')]


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);rows=[]
    for name,relative,old,new,test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix='grt_mutation_') as directory:
            copied=Path(directory)/'tree'
            shutil.copytree(ROOT,copied,ignore=shutil.ignore_patterns('.venv','dist','build','__pycache__','runs','*.egg-info'))
            path=copied/relative;text=path.read_text(encoding='utf-8')
            assert text.count(old)==1,relative
            path.write_text(text.replace(old,new),encoding='utf-8',newline='\n')
            result=subprocess.run([sys.executable,'-X','utf8','-B','-m','unittest',test,'-v'],cwd=copied,capture_output=True,text=True,encoding='utf-8')
            transcript=(result.stdout+result.stderr).replace(str(copied),'<copied-tree>').replace(str(ROOT),'<source-tree>').replace(str(Path.home()),'<home>')
            (output/(name+'.txt')).write_text(transcript,encoding='utf-8',newline='\n')
            rows.append({'mutation':name,'file':relative,'replacement':[old,new],'test':test,'exit_code':result.returncode,
                         'detected':result.returncode!=0 and 'AssertionError' in transcript and 'FAILED (failures=' in transcript})
    (output/'RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    rows=run(parser.parse_args().out);print(json.dumps(rows,indent=2));raise SystemExit(not all(r['detected'] for r in rows))
