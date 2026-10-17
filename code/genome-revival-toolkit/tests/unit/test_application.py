import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from dna_design_core.application import api,config
from dna_design_core.application.cli import parser
from dna_design_core.engine.invoker import Invoker
from dna_design_core.assurance import seal
from unit.test_assurance import prepared


class ApplicationTests(unittest.TestCase):
    def test_capabilities_use_one_invoker_and_one_seal_publisher(self):
        with tempfile.TemporaryDirectory() as d:
            session,_,_,_=prepared(d);boundary=[];functions=[]
            invoke=Invoker._invoke;load=Invoker._load
            def traced(self,use,*args,**kwargs):
                boundary.append(use.split('@')[0]);return invoke(self,use,*args,**kwargs)
            def loaded(self,entry):
                function=load(self,entry)
                def observed(*args,**kwargs):
                    functions.append(entry['declaration']['id']);return function(*args,**kwargs)
                return observed
            with patch.object(Invoker,'_invoke',traced),patch.object(Invoker,'_load',loaded),patch.object(seal,'publish',wraps=seal.publish) as publisher:
                result=api.call('seal',root=session.root,kit_dirs=[Path(d)/'kit'],also=['check.replay'])
            self.assertEqual(result['problems'],[],result);self.assertTrue(result['result']['sealed'])
            self.assertEqual(boundary,functions);self.assertIn('toy.length',functions);self.assertIn('format.write_json',functions)
            self.assertEqual(publisher.call_count,1)

    def test_seal_recomputes_after_an_earlier_pass(self):
        with tempfile.TemporaryDirectory() as d:
            session,_,_,_=prepared(d);kit=Path(d)/'kit'
            before=api.call('judge',root=session.root,kit_dirs=[kit]);self.assertEqual(before['result']['unsatisfied'],[])
            # Removing an available mandatory check after judge must not reuse PASS.
            original=Invoker.invoke
            def unavailable(self,use,*args,**kwargs):
                if use.split('@')[0]=='check.readback':
                    from dna_design_core.kernel.errors import ToolkitError
                    raise ToolkitError('CHECK_UNAVAILABLE','Constructed missing-runtime control.')
                return original(self,use,*args,**kwargs)
            with patch.object(Invoker,'invoke',unavailable):result=api.call('seal',root=session.root,kit_dirs=[kit])
            self.assertFalse(result['result']['sealed']);self.assertEqual(result['result']['present_files'],[])
            self.assertEqual(result['result']['unsatisfied'][0]['check'],'check.readback')
            self.assertEqual(result['result']['unsatisfied'][0]['outcome'],'UNKNOWN')

    def test_config_order_and_scientific_parameters_not_overridden(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'config.json';path.write_text('{"lang":"file","external_timeout_s":10}',encoding='utf-8')
            with patch.dict(os.environ,{'GRT_LANG':'environment','GRT_EXTERNAL_TIMEOUT':'20','GRT_SPACER':'UNUSED'}):
                result=config.load(path,{'lang':'cli'})
                self.assertEqual(result['lang'],'cli');self.assertEqual(result['external_timeout_s'],20);self.assertNotIn('spacer',result)

    def test_cli_registration_equals_closed_verb_table(self):
        registered=[]
        def visit(p):
            if 'verb' in p._defaults:registered.append(p._defaults['verb'])
            for action in p._actions:
                if isinstance(getattr(action,'choices',None),dict):
                    for child in action.choices.values():visit(child)
        visit(parser())
        self.assertEqual(set(registered),set(json.loads((ROOT/'src/dna_design_core/application/verbs.json').read_text(encoding='utf-8'))))
        self.assertEqual(len(registered),len(set(registered)))
        self.assertEqual({name.replace('_',' ') for name in api.__all__},set(registered))

    def test_api_seal_recheck_and_repeat_are_content_preserving(self):
        with tempfile.TemporaryDirectory() as d:
            session,_,_,_=prepared(d);kit=Path(d)/'kit'
            judged=api.call('judge',root=session.root,kit_dirs=[kit])
            self.assertEqual(judged['problems'],[])
            first=api.call('seal',root=session.root,kit_dirs=[kit])
            self.assertEqual(first['problems'],[],first);self.assertTrue(first['result']['sealed'])
            destination=Path(first['result']['manifest']).parent
            before={p.relative_to(destination):p.read_bytes() for p in destination.rglob('*') if p.is_file()}
            second=api.call('seal',root=session.root,kit_dirs=[kit])
            self.assertEqual(first['result']['seal_id'],second['result']['seal_id'])
            self.assertEqual(before,{p.relative_to(destination):p.read_bytes() for p in destination.rglob('*') if p.is_file()})
            changed=api.call('run abandon',root=session.root,kit_dirs=[kit]);self.assertTrue(changed['problems'])
            frozen=api.call('run execute',root=destination,kit_dirs=[kit]);self.assertTrue(frozen['problems'])
            self.assertEqual(before,{p.relative_to(destination):p.read_bytes() for p in destination.rglob('*') if p.is_file()})


if __name__=='__main__':unittest.main()
