"""Tests at the static-scanner seam. Every covered scanner gets a violating copy."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from check_structure import scan


def write(root,path,text):
    target=root/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(text,encoding='utf-8',newline='\n')


def mutate_json(root,path,change):
    target=root/path
    data=json.loads(target.read_text(encoding='utf-8'))
    change(data)
    write(root,path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')


R='src/dna_design_core/'
RES=R+'resources/'


def declaration(root,change=lambda x:None):
    value=json.loads((root/'tests/fixtures/schemas/capability-v1.valid.json').read_text(encoding='utf-8'))['data']
    change(value)
    write(root,RES+'capabilities/synthetic.json',json.dumps(value))


def cycle(root):
    write(root,R+'biology/sequence/one.py','from . import two\n')
    write(root,R+'biology/sequence/two.py','from . import one\n')


def rule_without_source(root):
    value=json.loads((root/'tests/fixtures/schemas/rule-v1.valid.json').read_text(encoding='utf-8'))['data']
    del value['source']
    write(root,R+'knowledge/packs/synthetic.json',json.dumps(value))


def undeclared_file_write(root):
    def changed(value):
        value['effects']=['pure']
        value['source']['implemented_in']='dna_design_core.capabilities.builtin.misdeclared_io:run'
    declaration(root,changed)
    write(root,R+'capabilities/builtin/misdeclared_io.py','def run(ctx):\n    (ctx.workdir/"unexpected.txt").write_text("constructed",encoding="utf-8")\n')


def undeclared_import_write(root):
    undeclared_file_write(root)
    write(root,R+'capabilities/builtin/misdeclared_io.py','from pathlib import Path\nPath("unexpected.txt").write_text("constructed",encoding="utf-8")\ndef run(ctx):\n    pass\n')


MUTATIONS={
 'INV-C4':undeclared_file_write,
 'INV-L1':lambda r:write(r,R+'biology/sequence/bad.py','from ...engine import executor\n'),
 'INV-L2':lambda r:write(r,'kits/toy/capabilities/bad.py','from dna_design_core.engine import executor\n'),
 'INV-L3':cycle,
 'INV-C6':lambda r:write(r,R+'catalog/check_registry.py',''),
 'INV-P2':lambda r:mutate_json(r,RES+'schemas/pipeline-v1.json',lambda x:x['properties'].update(gates={'type':'array'})),
 'INV-I1':lambda r:write(r,R+'biology/sequence/bad.py','from hashlib import sha256 as digest\n'),
 'INV-T1':lambda r:write(r,R+'record/bad.py','def render(journal):\n    journal.append_event({})\n'),
 'INV-K1':lambda r:write(r,'kits/toy/main.py','import argparse\n'),
 'INV-K2':lambda r:write(r,'kits/toy/capabilities/bad.py','from dna_design_core.storage import journal\n'),
 'INV-K7':lambda r:mutate_json(r,RES+'schemas/kit-v1.json',lambda x:x['properties'].update(profiles={'type':'object'})),
 'INV-V1':lambda r:write(r,R+'kernel/bad.py',"outcome='ACCEPTED'\n"),
 'INV-W2':lambda r:write(r,'pyproject.toml',(r/'pyproject.toml').read_text(encoding='utf-8').replace('dynamic = ["version"]','version = "1.2.3"')),
 'INV-X1':lambda r:write(r,R+'biology/sequence/bad.py',"from os import environ as environment\nx=environment['X']\n"),
 'INV-Q3':lambda r:mutate_json(r,'tests/fixtures/schemas/goal-v1.valid.json',lambda x:x.pop('oracle')),
 'INV-C2':lambda r:declaration(r,lambda x:x.update(does_not_establish=[])),
 'INV-C8':lambda r:declaration(r,lambda x:x.update(id='demo.check_length')),
 'INV-D5':lambda r:write(r,R+'kernel/bad.py','class GATE_REFUSED(Exception):\n    pass\n'),
 'INV-K6':lambda r:(write(r,'kits/other/capabilities/ok.py',''),write(r,'kits/toy/capabilities/bad.py','import other.capabilities.ok\n')),
 'INV-N1':rule_without_source,
 'INV-V2':lambda r:write(r,R+'kernel/bad.py',"raise ToolkitError(code='UNREGISTERED_CODE')\n"),
 'INV-V3':lambda r:write(r,R+'kernel/bad.py','class NewError(Exception):\n    pass\n'),
 'INV-F4':lambda r:write(r,R+'biology/sequence/bad.py','snapgene_product = None\n'),
 'INV-F5':lambda r:write(r,'.gitignore','__pycache__/\n'),
 'INV-W1':lambda r:write(r,R+'kernel/bad.py',"VERSION='1.2.3'\n"),
 'INV-X3':lambda r:write(r,R+'biology/sequence/bad.py','import socket as net\n'),
 'INV-X4':lambda r:write(r,R+'biology/sequence/bad.py',"import subprocess\nsubprocess.run(['echo'],shell=True)\n"),
 'INV-Q4':lambda r:write(r,'tests/SKIPS.json',json.dumps([{'test':'toy','reason':'example','condition':'none','expires':'2000-01-01'}])),
 'DEP-12':lambda r:write(r,R+'biology/sequence/bad.py',"print('leak')\n"),
 'DEP-13':lambda r:write(r,R+'biology/sequence/bad.py','try:\n    pass\nexcept Exception:\n    pass\n'),
 'SCHEMA':lambda r:mutate_json(r,RES+'schemas/goal-v1.json',lambda x:x.update(additionalProperties=True)),
 'CONTRACT':lambda r:write(r,'contracts.toml',(r/'contracts.toml').read_text(encoding='utf-8').replace('biology = ["kernel"]','biology = ["kernel", "engine"]')),
 'VOCAB':lambda r:mutate_json(r,RES+'vocab.json',lambda x:x['outcome'].append({'value':'ACCEPTED','description':'Invalid addition.'})),
 'ERRORS':lambda r:mutate_json(r,RES+'errors.json',lambda x:x.pop()),
 'PROFILES':lambda r:mutate_json(r,RES+'profiles.json',lambda x:x['always'].remove('check.readback')),
 'INVENTORY':lambda r:mutate_json(r,'tests/PENDING_INV.json',lambda x:x.pop()),
}


class ContractTreeTests(unittest.TestCase):
    def test_empty_runtime_tree_conforms(self):
        self.assertEqual(scan(ROOT),[])

    def test_positive_declaration_and_legal_imports(self):
        with tempfile.TemporaryDirectory(prefix='s0_验证_') as directory:
            root=Path(directory)/'tree'
            shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','runs','*.egg-info','.venv','dist','build'))
            declaration(root)
            write(root,R+'biology/sequence/legal.py','from ...kernel.public import Material\n')
            write(root,'kits/toy/capabilities/legal.py','from dna_design_core.biology.public import reverse_complement\n')
            self.assertEqual(scan(root),[])


def make_mutation_test(code,mutate):
    def test(self):
        with tempfile.TemporaryDirectory(prefix='s0_mutation_') as directory:
            root=Path(directory)/'tree'
            shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','runs','*.egg-info','.venv','dist','build'))
            mutate(root)
            findings=scan(root)
            self.assertIn(code,{f['id'] for f in findings},f'{code} violation was not detected')
    return test


for code,mutate in MUTATIONS.items():
    setattr(ContractTreeTests,'test_reject_'+code.replace('-','_'),make_mutation_test(code,mutate))
setattr(ContractTreeTests,'test_reject_INV_C4_import',make_mutation_test('INV-C4',undeclared_import_write))


class SpecScannerTests(unittest.TestCase):
    def run_copy(self,change):
        repository=ROOT.parents[1]
        text=(repository/'spec/SPEC.md').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='s0_spec_') as directory:
            path=Path(directory)/'SPEC.md'
            path.write_text(change(text),encoding='utf-8',newline='\n')
            return subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/spec_lint.py'),str(path)],capture_output=True,text=True,encoding='utf-8',check=False)

    def test_spec_baseline(self):
        result=self.run_copy(lambda s:s)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


def make_spec_test(code,addition):
    def test(self):
        result=self.run_copy(lambda s:s.replace('## D1 ',addition+'\n\n## D1 ',1) if code!='S6' else s.replace('`PASS`','`PASS`、`EXTRA`',1))
        self.assertNotEqual(result.returncode,0)
        self.assertIn(code,result.stdout)
    return test


for code,addition in {'S1':'`step.phantom`','S2':'`grt teleport`','S4':'INV-Z999','S5':'`INCONCLUSIVE` is active.','S6':''}.items():
    setattr(SpecScannerTests,'test_reject_INV_'+code,make_spec_test(code,addition))


if __name__=='__main__': unittest.main()
