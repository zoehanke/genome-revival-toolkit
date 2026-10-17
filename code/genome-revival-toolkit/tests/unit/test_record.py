import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from unit.test_assurance import prepared
from dna_design_core.assurance import judge,obligations,labels
from dna_design_core.record.projections import project,FOOTER
from dna_design_core.record.render.runcard import render


class RecordTests(unittest.TestCase):
    def test_offline_render_is_repeatable_readonly_and_keeps_issuers_separate(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker,factory,candidate=prepared(d)
            required=obligations.derive(session.snapshot(),session.current_goal(),session.current_pipeline(),session.events())
            result=judge.run(invoker,factory,session.journal,candidate,required)
            events=session.events();snapshot=session.snapshot();verdicts=[v['verdict'] for v in result['verdicts']]
            label_set=labels.collect(events,snapshot,verdicts=verdicts)
            not_done=labels.not_verified(events,snapshot,session.current_goal(),verdicts)
            before={p.relative_to(session.root):p.read_bytes() for p in session.root.rglob('*') if p.is_file()}
            texts=render(events,snapshot,label_set,not_done)
            self.assertEqual(texts,render(events,snapshot,label_set,not_done))
            self.assertEqual(before,{p.relative_to(session.root):p.read_bytes() for p in session.root.rglob('*') if p.is_file()})
            for label in ['Checked by the program','Declared only','Not done','Technical details',FOOTER]:self.assertIn(label,texts['html'])
            self.assertIn('Through event '+str(events[-1]['seq']),texts['html'])
            self.assertNotIn('http://',texts['html']);self.assertNotIn('https://',texts['html']);self.assertNotIn('<script',texts['html'])
            card=project(events,snapshot,label_set,not_done)
            self.assertTrue(any('host_expectation' in s for s in card['declared']))
            self.assertFalse(any('host_expectation' in s for s in card['checked']))
            self.assertLessEqual(set(not_done),set(card['not_done']))

    def test_solid_links_require_explicit_binding_and_matching_file_hash(self):
        with tempfile.TemporaryDirectory() as d:
            session,_,_,_=prepared(d);events=session.events();snapshot=session.snapshot()
            declaration=next(r['declaration'] for r in snapshot['capabilities'] if r['declaration']['id']=='toy.length')
            declaration['outputs']=[{'name':'file','type':'artifact','output_role':'analysis'}]
            done=next(e for e in events if e['type']=='step.completed')
            done['payload']['outputs']={'materials':{},'documents':{},'artifacts':[{'run_path':'work/s1/first.json','sha256':'1'*64,'role':'analysis','media_type':'application/json'}]}
            done['payload']['values']={}
            second=copy.deepcopy(next(e for e in events if e['type']=='step.started'))
            second.update(seq=len(events)+1,hash='2'*64);second['payload'].update(step_id='s2',inputs={'file':{'id':'1'*64,'origin':{'kind':'step','ref':{'step_id':'s1','port':'file'}}}})
            events.append(second)
            self.assertEqual(sum(e['basis']=='hash_equal' for e in project(events,snapshot,{},[])['links']),1)
            second['payload']['inputs']['file']['id']='3'*64
            self.assertFalse(any(e['basis']=='hash_equal' for e in project(events,snapshot,{},[])['links']))
            second['payload']['inputs']['file']={'id':'1'*64,'origin':{'kind':'literal','ref':None}}
            self.assertFalse(any(e['basis']=='hash_equal' for e in project(events,snapshot,{},[])['links']))


if __name__=='__main__':unittest.main()
