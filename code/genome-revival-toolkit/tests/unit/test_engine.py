import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import chdir
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'tests'))
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.session import Session
from dna_design_core.engine.invoker import Invoker
from dna_design_core.engine.executor import execute
from dna_design_core.engine import normalize, goal
from dna_design_core.storage.store import Store
from dna_design_core.storage.journal import Journal
from dna_design_core.kernel.errors import ToolkitError
from unit.test_catalog import toy


def session_fixture(directory,body=None):
    kit=Path(directory)/'kit'
    toy(kit,body=body or 'from dna_design_core.kernel.public import Outcome\ndef run(ctx, sequence):\n    return Outcome(values={"length":len(sequence)})\n')
    catalog=Catalog([kit]);root=Path(directory)/'run';root.mkdir()
    (root/'run.json').write_text(json.dumps({'run_id':'a'*16,'created_at':'2026-01-01T00:00:00.000Z','release_id':'dev-tree'}),encoding='utf-8')
    snapshot=catalog.snapshot('dev-tree');identity=Store(root).put('documents',snapshot)
    Journal(root,'a'*16).append('run.created',{'release_id':'dev-tree','schema_versions':{'event':1},'created_by':{'kind':'ai_host','name':'test'},'environment':{'python':'test','platform':'test','packages':{},'external_tools':[],'config_digest':'1'*64},'catalog_id':identity,'catalog_ref':'store/documents/'+identity+'.json','kits':catalog.kit_receipts},writer='application')
    session=Session(root,catalog);return session,Invoker(session)


def goal_document():
    return {'schema':'goal-v1','version':1,'parent_digest':None,'original_request':'Report four symbols.','sources':[],'declared_context':[],
            'targets':[{'id':'t1','role':'analysis','required':True}],'constraints':[],'intents':[]}


def plan_document(goal_digest,expect=4):
    return {'schema':'pipeline-v1','version':1,'goal_digest':goal_digest,
            'steps':[{'step_id':'s1','use':'toy.length','inputs':{'sequence':{'literal':'ACGT'}},'params':{},'why':'Count constructed symbols.',
                      'expects':{'on':{'step':'s1','port':'length'},'op':'equals','value':expect}}],
            'outputs':[{'name':'length','from':{'step':'s1','port':'length'},'target':'t1'}]}


class EngineTests(unittest.TestCase):
    def test_concurrent_revision_and_frozen_failed_history(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);declared=session.set_goal(goal_document());session.submit(plan_document(declared['goal_digest'],5))
            execute(session,invoker);original=session.current_pipeline();before_failure=session.steps()['s1']['failure']
            from dna_design_core.kernel import ids
            barrier=Barrier(2)
            def change(name):
                replacement=copy.deepcopy(original['steps'][0]);replacement['step_id']=name;replacement['expects'].update(on={'step':name,'port':'length'},value=4)
                request={'schema':'pipeline-revision-v1','expected_digest':ids.document_id(original),'trigger':{'kind':'host_observation','event_refs':[]},'reason':'Four symbols are present.',
                         'operations':[{'op':'add_step','after':'s1','step':replacement},{'op':'supersede_step','step_id':'s1','by':name},
                                       {'op':'set_outputs','outputs':[{'name':'length','from':{'step':name,'port':'length'},'target':'t1'}]}]}
                barrier.wait(timeout=5)
                try:session.revise(request);return 'success'
                except ToolkitError as error:return error.problem.code
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(change,['s2','s3']))
            self.assertEqual(results.count('success'),1);self.assertTrue(set(results)<={'success','RUN_LOCKED','PLAN_SCHEMA_INVALID'})
            current=session.current_pipeline();self.assertEqual(current['steps'][0],original['steps'][0]);self.assertEqual(session.steps()['s1']['failure'],before_failure)
            self.assertEqual(execute(session,invoker)['state'],'COMPLETED')
            events=session.events();revision=next(e for e in events if e['type']=='pipeline.revised')
            reason=next(e for e in events if e['hash']==revision['payload']['reason_event'])
            new_started=next(e for e in events if e['type']=='step.started' and e['payload']['step_id']!='s1')
            self.assertLess(reason['seq'],new_started['seq'])
            last=current['steps'][-1]['step_id'];bad=copy.deepcopy(current['steps'][-1]);bad.update(step_id='s4',inputs={'sequence':{'step':'s1','port':'length'}})
            request={'schema':'pipeline-revision-v1','expected_digest':ids.document_id(current),'trigger':{'kind':'host_observation','event_refs':[]},'reason':'Attempt to use a superseded output.',
                     'operations':[{'op':'add_step','after':last,'step':bad}]}
            with self.assertRaises(ToolkitError):session.revise(request)

    def test_revision_normalizes_compact_refs_before_validation(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);declared=session.set_goal(goal_document());plan=plan_document(declared['goal_digest'],5)
            admitted=session.submit(plan);execute(session,invoker)
            replacement=copy.deepcopy(plan['steps'][0]);replacement['step_id']='s2';replacement['expects']={'on':'@s2.length','op':'equals','value':4}
            request={'schema':'pipeline-revision-v1','expected_digest':admitted['pipeline_digest'],
                     'trigger':{'kind':'host_observation','event_refs':[]},'reason':'Four symbols were provided.',
                     'operations':[{'op':'add_step','after':'s1','step':replacement},{'op':'supersede_step','step_id':'s1','by':'s2'},
                                   {'op':'set_outputs','outputs':[{'name':'length','from':'@s2.length','target':'t1'}]}]}
            session.revise(request)
            self.assertEqual(session.current_pipeline()['steps'][-1]['expects']['on'],{'step':'s2','port':'length'})
            self.assertEqual(execute(session,invoker)['state'],'COMPLETED')

    def test_normalization_equivalence_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            session,_=session_fixture(d);declared=session.set_goal(goal_document())
            canonical=plan_document(declared['goal_digest']);compact=copy.deepcopy(canonical)
            compact['outputs'][0]['from']='@s1.length';compact['steps'][0]['expects']['on']='@s1.length'
            normalized=session.admit(compact)
            self.assertEqual(normalized,session.admit(canonical))
            self.assertEqual(normalized,normalize.pipeline(normalized,session.declarations(),set()))

    def test_closed_plan_rejects_controls_forward_refs_and_unbound_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);declared=session.set_goal(goal_document())
            mutations=[lambda p:p.update(checks=[]),lambda p:p.update(gates=[]),lambda p:p.update(required_scopes=[]),
                       lambda p:p['steps'][0].update(use='check.readback'),
                       lambda p:p['outputs'][0].update(deliver_as='analysis'),
                       lambda p:p['steps'][0]['inputs'].update(sequence={'step':'s2','port':'length'}),
                       lambda p:p['steps'][0]['inputs'].update(sequence={'artifact':'unregistered.txt'}),
                       lambda p:p['steps'][0]['params'].update(unknown={'step':'s1','port':'length'}),
                       lambda p:p['steps'][0].update(why=''),lambda p:p['steps'][0]['inputs'].update(sequence='ACGT'),
                       lambda p:p['steps'][0].update(use='toy.length@99.0.0')]
            before=session.journal.path.read_bytes()
            for index,mutate in enumerate(mutations):
                plan=plan_document(declared['goal_digest']);mutate(plan)
                with self.subTest(index=index),self.assertRaises(ToolkitError):session.submit(plan)
            self.assertEqual(invoker.calls,0);self.assertEqual(session.journal.path.read_bytes(),before)

    def test_goal_original_and_constraint_ids_survive_amendment(self):
        with tempfile.TemporaryDirectory() as d:
            session,_=session_fixture(d);request=goal_document()
            request['constraints']=[{'id':'c1','check':'check.goal.output_present@0.0.0','params':{},'target':'t1','source_quote':'four symbols','status':'active'}]
            first=session.set_goal(request);self.assertEqual(session.current_goal()['constraints'][0]['origin'],'user_quoted')
            amended=copy.deepcopy(request);amended.update(version=2,parent_digest=first['goal_digest'])
            removed=copy.deepcopy(amended);removed['constraints']=[]
            changed=copy.deepcopy(amended);changed['original_request']='Different request'
            for bad in [removed,changed]:
                with self.assertRaises(ToolkitError):session.set_goal(bad,'Change goal.')
            amended['constraints'][0].update(status='dropped',drop_reason='Reported change in requirements.',source_quote='not in the original')
            session.set_goal(amended,'Retain a visible dropped constraint.')
            saved=session.current_goal();self.assertEqual(saved['constraints'][0]['origin'],'host_derived')
            self.assertEqual(saved['constraints'][0]['id'],'c1');self.assertEqual(saved['original_request'],request['original_request'])
            self.assertTrue(all(e['actor']['kind']=='ai_host' for e in session.events() if e['type'].startswith('goal.')))

    def test_action_needs_admitted_parent_and_interrupt_needs_new_step(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);declared=session.set_goal(goal_document());session.submit(plan_document(declared['goal_digest']))
            with self.assertRaises(ToolkitError):invoker.invoke('toy.length',{'sequence':'ABCD'},{},parent='missing')
            execute(session,invoker);started=next(e for e in session.events() if e['type']=='step.started')
            # A crash immediately after step.started leaves this exact prefix.
            lines=session.journal.path.read_bytes().splitlines(keepends=True)
            session.journal.path.write_bytes(b''.join(lines[:started['seq']]))
            calls=invoker.calls;self.assertEqual(execute(session,invoker)['state'],'HALTED');self.assertEqual(invoker.calls,calls)
            self.assertEqual(session.steps()['s1']['failure']['payload']['failure']['code'],'STEP_INTERRUPTED')

    def test_relative_unicode_source_and_same_content_amendment(self):
        with tempfile.TemporaryDirectory() as d:
            session,_=session_fixture(d)
            source=Path(d)/'构造.txt';source.write_bytes(b'abc')
            request=goal_document();request['sources']=[{'source_id':'synth','from':source.name,'input_origin':'researcher_observation','as':'artifact','declared':{}}]
            original=copy.deepcopy(request);run_before=(session.root/'run.json').read_bytes()
            with chdir(d):first=session.set_goal(request)
            self.assertEqual(request,original)
            renamed=Path(d)/'different.txt';renamed.write_bytes(b'abc')
            amended=copy.deepcopy(request);amended.update(version=2,parent_digest=first['goal_digest']);amended['sources'][0]['from']=str(renamed)
            session.set_goal(amended,'Retain the same observed content.')
            self.assertEqual(session.current_goal()['sources'][0]['path'],'inputs/synth/构造.txt')
            events=[e for e in session.events() if e['type']=='input.registered']
            self.assertEqual(len(events),1)
            self.assertEqual(events[0]['payload']['input_origin'],'researcher_observation')
            self.assertEqual(events[0]['payload']['size'],3)
            self.assertEqual((session.root/'run.json').read_bytes(),run_before)

    def test_invalid_sources_leave_no_imported_files_or_events(self):
        with tempfile.TemporaryDirectory() as d:
            session,_=session_fixture(d);source=Path(d)/'source.txt';source.write_bytes(b'abc')
            valid={'source_id':'synth','from':str(source),'input_origin':'user_file','as':'artifact','declared':{}}
            cases=[[{**valid,'path':'ignored'}],[{**valid,'sha256':'0'*64}],[valid,copy.deepcopy(valid)],[valid,{**valid,'source_id':'second','from':str(Path(d)/'missing')}]]
            for sources in cases:
                request=goal_document();request['sources']=sources;before=session.journal.path.read_bytes()
                with self.subTest(sources=len(sources)),self.assertRaises(ToolkitError) as caught:session.set_goal(request)
                self.assertEqual(caught.exception.problem.category,'INVALID_INPUT')
                self.assertNotIn(str(source),json.dumps(caught.exception.problem.as_dict()))
                self.assertEqual(session.journal.path.read_bytes(),before)
                self.assertFalse((session.root/'inputs').exists())

    def test_goal_import_uses_actual_bytes_and_does_not_persist_from(self):
        with tempfile.TemporaryDirectory() as d:
            session,_=session_fixture(d)
            source=Path(d)/'source.txt';source.write_bytes(b'abc')
            request=goal_document();request['sources']=[{'source_id':'synth','from':str(source),'input_origin':'user_file','as':'artifact','declared':{}}]
            declared=session.set_goal(request)
            saved=session.current_goal()['sources'][0]
            self.assertEqual(saved['path'],'inputs/synth/source.txt')
            self.assertEqual(saved['sha256'],'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            self.assertNotIn('from',saved)
            self.assertEqual((session.root/saved['path']).read_bytes(),b'abc')
            self.assertFalse(any(str(source).encode('utf-8') in p.read_bytes() for p in session.root.rglob('*') if p.is_file()))
            before=session.journal.path.read_bytes();source.write_bytes(b'abcd')
            amended=copy.deepcopy(request);amended.update(version=2,parent_digest=declared['goal_digest'])
            with self.assertRaises(ToolkitError) as caught:session.set_goal(amended,'Use the changed file.')
            self.assertEqual(caught.exception.problem.category,'INVALID_INPUT')
            self.assertEqual(session.journal.path.read_bytes(),before)
            self.assertEqual((session.root/saved['path']).read_bytes(),b'abc')

    def test_no_plan_no_execution(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d)
            with self.assertRaises(ToolkitError):execute(session,invoker)
            self.assertEqual(invoker.calls,0)

    def test_admission_checks_entire_plan_without_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);goal=session.set_goal(goal_document())
            plan=plan_document(goal['goal_digest']);second=copy.deepcopy(plan['steps'][0]);second['step_id']='s2';second['params']={'unknown':1};plan['steps'].append(second)
            before=session.journal.path.read_bytes()
            with self.assertRaises(ToolkitError):session.submit(plan)
            self.assertEqual(invoker.calls,0);self.assertEqual(session.journal.path.read_bytes(),before)

    def test_failure_revision_replacement_retains_facts(self):
        with tempfile.TemporaryDirectory() as d:
            session,invoker=session_fixture(d);declared=session.set_goal(goal_document());plan=plan_document(declared['goal_digest'],5)
            admitted=session.submit(plan);self.assertEqual(invoker.calls,0)
            self.assertEqual(execute(session,invoker)['state'],'HALTED')
            failure=next(e for e in session.events() if e['type']=='step.failed')
            step=copy.deepcopy(plan['steps'][0]);step['step_id']='s2';step['expects']['on']['step']='s2';step['expects']['value']=4
            request={'schema':'pipeline-revision-v1','expected_digest':admitted['pipeline_digest'],'reason':'Correct a constructed expectation.',
                     'trigger':{'kind':'step_failed','step_id':'s1','failure_code':'STEP_EXPECTATION_FAILED','event_refs':[failure['hash']]},
                     'operations':[{'op':'supersede_step','step_id':'s1','by':'s2'},{'op':'add_step','after':'s1','step':step},{'op':'set_outputs','outputs':[{'name':'length','from':{'step':'s2','port':'length'},'target':'t1'}]}]}
            session.revise(request)
            self.assertEqual(execute(session,invoker)['state'],'COMPLETED')
            self.assertEqual(next(e for e in session.events() if e['hash']==failure['hash']),failure)
            self.assertEqual(session.steps()['s2']['completed']['payload']['values'],{'length':4})
            with self.assertRaises(ToolkitError):session.revise(request)


if __name__=='__main__':unittest.main()
