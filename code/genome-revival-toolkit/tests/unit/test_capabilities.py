import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from dna_design_core.biology.public import reverse_complement
from dna_design_core.kernel.errors import ToolkitError
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.loading import Loader
from dna_design_core.application import api
from fixtures.toy.build import build
from unit.test_engine import goal_document


class CapabilityTests(unittest.TestCase):
    def test_reverse_complement_has_hand_constructed_oracles(self):
        for source,expected in [('AGTCAGAA','TTCTGACT'),('NRY','RYN'),('acgt','ACGT')]:
            self.assertEqual(reverse_complement(source),expected)
        with self.assertRaises(ToolkitError):reverse_complement('AGTZAGAA')

    def test_generated_declarations_match_decorator_exports(self,catalog=None):
        catalog=catalog or Catalog();loader=Loader()
        for row in catalog.entries.values():
            function=loader.load(row)
            self.assertEqual(row['declaration'],function.declaration)
            if row['declaration']['role']=='CHECK':
                self.assertLessEqual(set(row['declaration']['effects']),{'pure','reads_files'})
                for path in row['declaration']['fixtures'].values():self.assertTrue(((row['root'] or ROOT)/path).is_file())

    def test_external_two_step_non_dna_kit_and_incorrect_algorithm_control(self):
        for faulty,missing in [(False,False),(True,False),(False,True)]:
            with self.subTest(faulty=faulty,missing_dependency=missing),tempfile.TemporaryDirectory() as d:
                folder=Path(d);kit=build(folder/'external');run=folder/'run'
                fixture=json.loads((kit/'fixtures'/('check.fail.json' if faulty else 'check.pass.json')).read_text(encoding='utf-8'))
                if faulty:
                    path=kit/'capabilities/flow.py';text=path.read_text(encoding='utf-8')
                    path.write_text(text.replace('counts["control"]-counts["test"]','counts["control"]-counts["test"]+1'),encoding='utf-8')
                if missing:
                    path=kit/'capabilities/check_difference.json';declaration=json.loads(path.read_text(encoding='utf-8'))
                    declaration['requires_runtime']=[{'kind':'python_package','name':'grt_synthetic_dependency_that_is_absent','probe':None}]
                    path.write_text(json.dumps(declaration),encoding='utf-8')
                source=folder/'counts.csv';source.write_text('name,count\n'+''.join(name+','+str(value)+'\n' for name,value in fixture['counts'].items()),encoding='utf-8',newline='\n')
                created=api.call('run create',directory=run,kit_dirs=[kit]);self.assertEqual(created['problems'],[])
                self.assertTrue(created['result']['notices'])
                goal=goal_document();goal['sources']=[{'source_id':'table','from':str(source),'as':'artifact','input_origin':'researcher_observation','declared':{}}]
                goal['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'Report','status':'active'}]
                declared=api.call('goal declare',root=run,request=goal,kit_dirs=[kit]);self.assertEqual(declared['problems'],[])
                plan={'schema':'pipeline-v1','version':1,'goal_digest':declared['result']['goal_digest'],'steps':[
                    {'step_id':'s1','use':'toy.parse_counts','inputs':{'table':{'source':'table'}},'params':{},'why':'Parse synthetic reported counts.'},
                    {'step_id':'s2','use':'toy.difference','inputs':{'counts':{'step':'s1','port':'counts'}},'params':{},'why':'Compute the count difference.'}],
                    'outputs':[{'name':'analysis','from':{'step':'s2','port':'analysis'},'target':'t1'}]}
                self.assertEqual(api.call('pipeline submit',root=run,request=plan,kit_dirs=[kit])['problems'],[])
                self.assertEqual(api.call('run execute',root=run,kit_dirs=[kit])['state'],'COMPLETED')
                judged=api.call('judge',root=run,kit_dirs=[kit]);self.assertEqual(judged['problems'],[],judged)
                verdicts=[v['verdict'] for v in judged['result']['verdicts']]
                actual=next(v['outcome'] for v in verdicts if v['check']['id']=='toy.check_difference')
                self.assertEqual(actual,'UNKNOWN' if missing else fixture['expected'])
                self.assertEqual(next(v['outcome'] for v in verdicts if v['check']['id']=='check.replay'),'PASS')
                self.assertFalse((run/'store/materials').exists())
                self.assertFalse(any(v['scope']=='preparation_model' for v in verdicts))


if __name__=='__main__':unittest.main()
