import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import shutil
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from unit.test_engine import session_fixture,goal_document,plan_document
from dna_design_core.assurance import obligations,stage,judge,seal,verify
from dna_design_core.engine.session import Session
from dna_design_core.engine.invoker import Invoker
from dna_design_core.engine.executor import execute
from dna_design_core.engine.view import ReadView
from dna_design_core.kernel.errors import ToolkitError


def prepared(directory):
    session,invoker=session_fixture(directory);goal=goal_document()
    goal['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'Report','status':'active'}]
    declared=session.set_goal(goal);session.submit(plan_document(declared['goal_digest']));execute(session,invoker)
    factory=lambda candidate:ReadView(session.root,session.events(),session.snapshot(),candidate)
    candidate=stage.create(session.root,factory({}),session.snapshot(),invoker,factory)
    return session,invoker,factory,candidate


class AssuranceTests(unittest.TestCase):
    def test_registered_old_inputs_remain_checked_after_goal_amendment(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);source=Path(d)/'old.txt';source.write_bytes(b'abc')
            goal=goal_document();goal['sources']=[{'source_id':'old','from':str(source),'input_origin':'user_file','as':'artifact','declared':{}}]
            first=session.set_goal(goal);session.submit(plan_document(first['goal_digest']));execute(session,invoker)
            goal.update(version=2,parent_digest=first['goal_digest'],sources=[]);session.set_goal(goal,'Remove the unused current source declaration.')
            (session.root/'inputs/old/old.txt').write_bytes(b'changed')
            result=invoker.invoke('check.inputs_unchanged',{}, {},parent='final',view=ReadView(session.root,session.events(),session.snapshot(),{}))
            self.assertEqual(result.verdicts[0]['outcome'],'FAIL')
            self.assertEqual(result.verdicts[0]['evidence']['different_sources'],['old'])

    def test_self_report_pass_cannot_satisfy_a_required_check(self):
        body='''from dna_design_core.kernel.public import Outcome,make,core_version
def run(ctx,sequence):
    verdict=make(check={"id":"check.goal.nonempty","version":core_version()},scope="user_goal",moment="final",issuer="check_capability",subject={"kind":"run","id":"a"*16},outcome="PASS",summary="Tool self-report control.",does_not_establish=["Qualification."])
    return Outcome(values={"length":len(sequence)},verdicts=[verdict])
'''
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d,body);declared=session.set_goal(goal_document());session.submit(plan_document(declared['goal_digest']))
            execute(session,invoker)
            earlier=[e['payload']['verdict'] for e in session.events() if e['type']=='verdict.issued']
            self.assertEqual(earlier[0]['issuer'],'tool_self_report');self.assertEqual(earlier[0]['moment'],'step')
            factory=lambda c:ReadView(session.root,session.events(),session.snapshot(),c)
            candidate=stage.create(session.root,factory({}),session.snapshot(),invoker,factory)
            required=obligations.derive(session.snapshot(),session.current_goal(),session.current_pipeline(),session.events())
            result=judge.run(invoker,factory,session.journal,candidate,required)
            self.assertTrue(any(r['check']=='check.goal.nonempty' and r['outcome']=='UNKNOWN' for r in result['unsatisfied']))

    def test_snapshot_material_checks_remain_required_when_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            from unit.test_catalog import toy
            from dna_design_core.application import api
            folder=Path(d);kit=folder/'kit';run=folder/'run'
            toy(kit,body='from dna_design_core.kernel.public import Outcome\ndef run(ctx,sequence):\n    return Outcome(products={"length":{"sequence":sequence,"features":[]}})\n')
            path=kit/'capabilities/unit.json';declaration=json.loads(path.read_text(encoding='utf-8'))
            declaration['outputs']=[{'name':'length','type':'material','output_role':'analysis'}]
            path.write_text(json.dumps(declaration),encoding='utf-8')
            self.assertEqual(api.run_create(directory=run,kit_dirs=[kit])['problems'],[])
            goal=goal_document();goal['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'Report','status':'active'}]
            declared=api.goal_declare(root=run,request=goal,kit_dirs=[kit]);plan=plan_document(declared['result']['goal_digest']);plan['steps'][0].pop('expects')
            self.assertEqual(api.pipeline_submit(root=run,request=plan,kit_dirs=[kit])['problems'],[])
            self.assertEqual(api.run_execute(root=run,kit_dirs=[kit])['state'],'COMPLETED')
            # S1c implements both checks. Deliberately remove runtime availability,
            # retaining the frozen declarations and the original UNKNOWN oracle.
            from dna_design_core.catalog.registry import Catalog
            available=Catalog.available
            def unavailable(catalog,use):
                return False if use.split('@')[0] in {'check.annotation_integrity','check.cds_validity'} else available(catalog,use)
            with patch.object(Catalog,'available',unavailable):
                result=api.seal(root=run,kit_dirs=[kit])
            self.assertEqual(result['problems'],[],result)
            missing={r['check']:r['outcome'] for r in result['result']['unsatisfied']}
            self.assertEqual(missing['check.annotation_integrity'],'UNKNOWN');self.assertEqual(missing['check.cds_validity'],'UNKNOWN')
            self.assertFalse(result['result']['sealed']);self.assertEqual(result['result']['present_files'],[])
            self.assertTrue(list((run/'store/materials').glob('*.json')))

    def test_all_check_controls_are_readonly(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker,factory,candidate=prepared(d)
            names=[r['declaration']['id'] for r in session.snapshot()['capabilities'] if r['declaration']['role']=='CHECK']
            for name in names:
                before={p.relative_to(session.root):p.read_bytes() for p in session.root.rglob('*') if p.is_file()}
                declaration=session.catalog.declaration(name)
                fixture_root=session.catalog.entries[name]['root'] or ROOT
                control=json.loads((fixture_root/declaration['fixtures']['pass']).read_text(encoding='utf-8'))
                invoker.invoke(name,{},control.get('params',{}),parent='final',view=factory(candidate))
                self.assertEqual(before,{p.relative_to(session.root):p.read_bytes() for p in session.root.rglob('*') if p.is_file()},name)

    def test_sealed_copy_verifies_without_the_original_run_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker,factory,candidate=prepared(d)
            required=obligations.derive(session.snapshot(),session.current_goal(),session.current_pipeline(),session.events())
            result=judge.run(invoker,factory,session.journal,candidate,required)
            seal.preconditions(session.state(),factory(candidate))
            sealed=seal.create(session.root,session.journal,candidate,result,required,session.snapshot(),session.current_goal(),session.current_pipeline(),lambda *a:{'html':'<html>Unit fixture</html>','markdown':'Unit fixture'})
            self.assertTrue(sealed['sealed']);original=Path(sealed['manifest']).parent
            copied=Path(d)/'copied'/sealed['seal_id'];shutil.copytree(original,copied)
            catalog=session.catalog;shutil.rmtree(session.root)
            manifest,events=verify.inspect(copied)
            offline=Session(copied,catalog,journal_name='journal-until-seal.ndjson');invoker=Invoker(offline)
            view=lambda c:ReadView(copied,events,offline.snapshot(),c)
            before={p.relative_to(copied):p.read_bytes() for p in copied.rglob('*') if p.is_file()}
            checked=verify.run(copied,invoker,view,manifest,events,offline.snapshot())
            self.assertTrue(checked['verified'],checked)
            self.assertEqual(before,{p.relative_to(copied):p.read_bytes() for p in copied.rglob('*') if p.is_file()})
            (copied/'length.json').write_bytes(b'5')
            with self.assertRaises(ToolkitError):verify.inspect(copied)

    def test_atomic_publish_retry_is_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'staging';source.mkdir()
            with patch.object(Path,'rename',side_effect=PermissionError),patch('dna_design_core.assurance.seal.time.sleep') as sleep:
                with self.assertRaises(ToolkitError):seal.publish(source,root/'sealed')
            self.assertEqual(sleep.call_count,5);self.assertTrue(source.exists());self.assertFalse((root/'sealed').exists())

    def test_real_checks_and_union_with_missing_check(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker,factory,candidate=prepared(d)
            required=obligations.derive(session.snapshot(),session.current_goal(),session.current_pipeline(),session.events())
            result=judge.run(invoker,factory,session.journal,candidate,required)
            self.assertEqual(result['unsatisfied'],[],result)
            self.assertEqual((Path(candidate['root'])/'length.json').read_bytes(),b'4')
            added=obligations.derive(session.snapshot(),session.current_goal(),session.current_pipeline(),session.events(),['absent.check_missing'])
            self.assertLessEqual({r['id'] for r in required},{r['id'] for r in added})
            result=judge.run(invoker,factory,session.journal,candidate,added)
            self.assertEqual(result['unsatisfied'][0]['outcome'],'UNKNOWN')
            self.assertEqual(result['verdicts'][-1]['verdict']['evidence']['failure']['code'],'CHECK_UNAVAILABLE')

    def test_profile_union_cannot_be_reduced_by_roles_or_missing_loaded_kit(self):
        with tempfile.TemporaryDirectory() as d:
            session,_,_,_=prepared(d)
            snap=session.snapshot();events=session.events();plan=session.current_pipeline()
            action=next(r['declaration'] for r in snap['capabilities'] if r['declaration']['id']=='toy.length')
            action['final_checks']=[{'check':'toy.check_required'}];action['model']='toy.model'
            for role in ['analysis','component','construct','primer_set']:
                action['outputs'][0]['output_role']=role
                event=next(e for e in events if e['type']=='step.completed');event['payload']['outputs']['materials']={'invented_by_test':['1'*64]}
                rows=obligations.derive(snap,session.current_goal(),plan,events)
                names={r['check'] for r in rows}
                self.assertLessEqual(set(snap['profiles']['always']+snap['profiles']['on_material_output']),names)
                self.assertIn('toy.check_required',names);self.assertIn('check.model_agreement',names)

    def test_replay_reads_original_inputs_and_does_not_write_run(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker,factory,candidate=prepared(d)
            before={p.relative_to(session.root):p.read_bytes() for p in session.root.rglob('*') if p.is_file()}
            result=invoker.invoke('check.replay',{}, {},parent='final',view=factory(candidate))
            self.assertEqual(result.verdicts[0]['outcome'],'PASS')
            self.assertEqual(before,{p.relative_to(session.root):p.read_bytes() for p in session.root.rglob('*') if p.is_file()})
            events=session.events();done=next(e for e in events if e['type']=='step.completed');done['payload']['values']['length']=5
            altered=ReadView(session.root,events,session.snapshot(),candidate)
            result=invoker.invoke('check.replay',{}, {},parent='final',view=altered)
            self.assertEqual(result.verdicts[0]['outcome'],'FAIL')
            self.assertEqual(result.verdicts[0]['evidence']['differences'][0]['fields'],['values'])

    def test_each_check_has_constructed_positive_and_negative(self):
        names=[json.loads(p.read_text(encoding='utf-8'))['check'] for p in sorted((ROOT/'tests/fixtures/checks').glob('*.pass.json'))]
        for name in names:
            with self.subTest(check=name),tempfile.TemporaryDirectory() as d:
                if name=='check.model_agreement':
                    from unit.test_s1_followup2 import prepared_model
                    session,invoker,factory,candidate=prepared_model(d)
                else:session,invoker,factory,candidate=prepared(d)
                if name=='check.dna_value_valid':
                    identity=session.store.put('documents',{'sequence':'AGTCAGAA'})
                    candidate['outputs']=[{'id':identity,'kind':'document'}]
                result=invoker.invoke(name,{}, {},parent='final',view=factory(candidate))
                expected=json.loads((ROOT/'tests/fixtures/checks'/(name+'.pass.json')).read_text(encoding='utf-8'))['expected']
                self.assertEqual(result.verdicts[0]['outcome'],expected)
                self.assertEqual(result.verdicts[0]['check']['id'],name)
                view=factory(candidate)
                if name in {'check.readback','check.manifest','check.goal.output_present'}:(Path(candidate['root'])/'length.json').unlink()
                elif name=='check.journal_chain':
                    bad=Path(d)/'broken.ndjson';bad.write_bytes(b'{}\n');view._candidate['journal_path']=str(bad)
                elif name=='check.store_hashes':
                    corrupt=session.root/'store/documents'/('f'*64+'.json');corrupt.write_bytes(b'{}')
                elif name=='check.inputs_unchanged':view.goal['sources']=[{'source_id':'absent','path':'inputs/missing','sha256':'0'*64}]
                elif name=='check.goal.nonempty':view.goal['constraints']=[]
                elif name=='check.goal.target_role_met':view.goal['targets'][0]['role']='construct'
                elif name=='check.lineage':next(e for e in view._events if e['type']=='step.started')['payload']['inputs']['sequence']['id']='0'*64
                elif name=='check.replay':next(e for e in view._events if e['type']=='step.completed')['payload']['values']['length']=99
                elif name=='check.model_agreement':
                    different=session.store.put('materials',{'sequence':'ACGA','topology':'linear','ends':None})
                    next(e for e in view._events if e['type']=='step.completed')['payload']['outputs']['materials']['product']=[different]
                else:
                    invalid=session.store.put('documents',{'sequence':'INVALID'});view._candidate['outputs'][0]['id']=invalid
                # Invoker reconstructs its own view from facts; change facts too.
                if name.startswith('check.goal.') or name=='check.inputs_unchanged':
                    next(e for e in view._events if e['type']=='goal.declared')['payload']['document']=copy.deepcopy(view.goal)
                result=invoker.invoke(name,{}, {},parent='final',view=view)
                expected=json.loads((ROOT/'tests/fixtures/checks'/(name+'.fail.json')).read_text(encoding='utf-8'))['expected']
                self.assertEqual(result.verdicts[0]['outcome'],expected)


if __name__=='__main__':unittest.main()
