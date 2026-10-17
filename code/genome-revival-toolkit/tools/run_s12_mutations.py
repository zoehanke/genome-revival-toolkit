"""S1.2 manual mutations on disposable copies; never mutate the working tree."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
MUTATIONS=[
    ('inline_output','src/dna_design_core/engine/invoker.py',
     "elif kind=='document':schemas.require(port.get('schema',port.get('schema_ref')),result.documents.get(key),'CAPABILITY_OUTPUT_INVALID')",
     "elif kind=='document':pass",
     'InlineDocumentTests.test_invalid_inline_output_is_not_persisted'),
    ('knowledge_owner','src/dna_design_core/engine/invoker.py',
     "if not isinstance(pack,str) or pack.split('/',1)[0]!=owner:","if not isinstance(pack,str):",
     'KnowledgeTests.test_loaded_other_kit_package_is_not_readable'),
    ('model_comparison','src/dna_design_core/capabilities/model_agreement.py',
     'fields=[key for key in before if before[key]!=after[key]]','fields=[]',
     'ModelTests.test_model_uses_named_recorded_arguments_and_compares_content_not_annotations'),
    ('materials_collection','src/dna_design_core/kernel/references.py',
     "result=[view.material(identity) for identity in outputs['materials'][port]] if kind=='materials' and 'index' not in reference else view.material(outputs['materials'][port][index])",
     "result=view.material(outputs['materials'][port][index])",
     'MaterialsTests.test_collection_and_explicit_item_bindings_run_and_replay')]


def run(output,only=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);rows=[]
    for name,relative,old,new,test in MUTATIONS:
        if only and name!=only:continue
        with tempfile.TemporaryDirectory(prefix='s12_mutation_') as directory:
            copied=Path(directory)/'tree'
            shutil.copytree(ROOT,copied,ignore=shutil.ignore_patterns('.venv','dist','build','__pycache__','runs','*.egg-info'))
            path=copied/relative;text=path.read_text(encoding='utf-8');assert text.count(old)==1,relative
            path.write_text(text.replace(old,new),encoding='utf-8',newline='\n')
            result=subprocess.run([sys.executable,'-X','utf8','-B','-m','unittest','tests.unit.test_s1_followup2.'+test,'-v'],cwd=copied,capture_output=True,text=True,encoding='utf-8')
            transcript=(result.stdout+result.stderr).replace(str(copied),'<copied-tree>').replace(str(ROOT),'<source-tree>').replace(str(Path.home()),'<home>')
            (output/(name+'.txt')).write_text(transcript,encoding='utf-8',newline='\n')
            rows.append({'mutation':name,'file':relative,'replacement':[old,new],'test':test,'exit_code':result.returncode,
                         'detected':result.returncode!=0 and 'AssertionError' in transcript and 'FAILED (failures=' in transcript})
    (output/'RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n')
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--only',choices=[row[0] for row in MUTATIONS]);args=parser.parse_args()
    rows=run(args.out,args.only);print(json.dumps(rows,indent=2));raise SystemExit(not all(r['detected'] for r in rows))
