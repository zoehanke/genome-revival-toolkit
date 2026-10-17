"""Structural ownership checks over the implemented runtime, with negative controls."""
import ast
import inspect
import json
from pathlib import Path
import re
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'src/dna_design_core'
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tools'))
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.loading import Loader
from docgen import documents


def verdict_literals(text):
    return [node for node in ast.walk(ast.parse(text)) if isinstance(node,ast.Dict) and any(isinstance(key,ast.Constant) and key.value=='schema' and isinstance(value,ast.Constant) and value.value=='verdict-v1' for key,value in zip(node.keys,node.values))]


def thrown_outcomes(text):
    return [node for node in ast.walk(ast.parse(text)) if isinstance(node,ast.Raise) and any(isinstance(value,ast.Constant) and value.value in {'PASS','FAIL','UNKNOWN','NOT_APPLICABLE'} for value in ast.walk(node) if isinstance(getattr(value,'value',None),str))]


class RuntimeStructureTests(unittest.TestCase):
    def test_verdict_constructor_and_exception_boundary(self,catalog=None):
        for path in SRC.rglob('*.py'):
            if path!=SRC/'kernel/verdict.py':self.assertEqual(verdict_literals(path.read_text(encoding='utf-8')),[],str(path.relative_to(SRC)))
        self.assertTrue(verdict_literals("value={'schema':'verdict-v1'}"))
        catalog=catalog or Catalog();loader=Loader()
        for entry in catalog.entries.values():
            if entry['declaration']['role']=='CHECK':
                function=loader.load(entry)
                self.assertEqual(thrown_outcomes(inspect.getsource(function)),[])
        self.assertTrue(thrown_outcomes("def check():\n    raise ValueError('FAIL')\n"))

    def test_journal_writer_locations_are_explicit(self):
        allowed={'engine/session.py','engine/executor.py','engine/invoker.py','assurance/judge.py','assurance/seal.py','assurance/verify.py','application/run_service.py','storage/journal.py'}
        found=set()
        for path in SRC.rglob('*.py'):
            tree=ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='append':
                    receiver=ast.unparse(node.func.value)
                    if 'journal' in receiver or receiver.startswith('Journal('):
                        relative=path.relative_to(SRC).as_posix();self.assertIn(relative,allowed);found.add(relative)
                        writer=next((k.value.value for k in node.keywords if k.arg=='writer' and isinstance(k.value,ast.Constant)),None)
                        self.assertEqual(writer,relative.split('/')[0])
        self.assertIn('application/run_service.py',found)
        self.assertFalse(any(path.startswith('record/') for path in found))

    def test_atomic_capabilities_do_not_call_other_capabilities(self,catalog=None):
        loader=Loader()
        for entry in (catalog or Catalog()).entries.values():
            function=loader.load(entry)
            calls=[node for node in ast.walk(ast.parse(inspect.getsource(function))) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='call']
            if entry['declaration']['granularity']=='atomic':self.assertEqual(calls,[])
            else:self.assertTrue(all(ast.unparse(node.func.value)=='ctx' for node in calls))

    def test_unique_seal_publisher_and_label_owner(self):
        for path in SRC.rglob('*.py'):
            tree=ast.parse(path.read_text(encoding='utf-8'));relative=path.relative_to(SRC).as_posix()
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='rename':self.assertEqual(relative,'assurance/seal.py')
                if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in {'UNSEALED','AMENDED_AFTER_START','INHERITED_FINDINGS','EXTERNAL_KIT'}:self.assertEqual(relative,'assurance/labels.py')
                if isinstance(node,ast.Dict):
                    for key,value in zip(node.keys,node.values):
                        if isinstance(key,ast.Constant) and key.value=='goal_digest' and isinstance(value,ast.Call):
                            self.assertEqual(ast.unparse(value.func),'digest' if relative=='engine/goal.py' else 'goal.digest')
                if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call):
                    for target in node.targets:
                        if isinstance(target,ast.Subscript) and isinstance(target.slice,ast.Constant) and target.slice.value=='goal_digest':
                            self.assertEqual(ast.unparse(node.value.func),'goal.digest')

    def test_dependencies_are_pinned_and_sufficient_for_runtime(self):
        locked={line.split('==')[0] for line in (ROOT/'requirements.lock').read_text(encoding='utf-8').splitlines()}
        self.assertEqual(locked,{'jsonschema','rfc8785'})
        biology_locked={line.split('==')[0] for line in (ROOT/'requirements-biology.lock').read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
        self.assertEqual(biology_locked,locked|{'biopython'})
        for path in SRC.rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.level==0 else []
                allowed=sys.stdlib_module_names|locked|{'dna_design_core'}
                if path.is_relative_to(SRC/'biology'):allowed=allowed|{'Bio'}
                for name in names:self.assertIn(name.split('.')[0],allowed)

    def test_generated_docs_and_vocabulary_are_fresh(self):
        for path,text in documents().items():self.assertEqual(path.read_text(encoding='utf-8'),text)

    def test_active_spec_module_paths_exist_in_d15(self):
        spec=(ROOT.parents[1]/'spec/SPEC.md').read_text(encoding='utf-8')
        tree=spec.split('## D15 ',1)[1].split('## D16 ',1)[0]
        active='\n'.join(line for line in spec.splitlines() if not line.startswith('- 删除：'))
        paths=set(re.findall(r'(?<![\w/])(?:kernel|biology|storage|knowledge|catalog|capabilities|engine|assurance|record|application)\.[a-z_]+',active))
        for name in paths:
            module,child=name.split('.')
            self.assertTrue((SRC/module/(child+'.py')).exists() or (SRC/module/child).is_dir(),name)
            self.assertRegex(tree,re.escape(child)+r'(?:\.py|/)')
        self.assertFalse((SRC/'engine/phantom.py').exists())


if __name__=='__main__':unittest.main()
