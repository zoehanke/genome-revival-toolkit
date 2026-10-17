"""D3/D11 boundary regressions. Synthetic explicit expectations only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from dna_design_core.application import api
from dna_design_core.kernel import schemas
from fixtures.contract_probe import (action, port, build, goal, plan, step, COUNT,
    inline_definitions, knowledge_definitions, rule, model_definitions, materials_definitions)


def start(folder,definitions,**kwargs):
    folder=Path(folder);kit=build(folder/'external',definitions,**kwargs);run=folder/'run'
    created=api.call('run create',directory=run,kit_dirs=[kit])
    if created['problems']:raise AssertionError(created)
    declared=api.call('goal declare',root=run,request=goal(),kit_dirs=[kit])
    if declared['problems']:raise AssertionError(declared)
    return run,kit,declared['result']['goal_digest']


def events(run):return [json.loads(line) for line in (run/'journal.ndjson').read_text(encoding='utf-8').splitlines()]


def prepared_model(directory,*,nested=False,**changes):
    from dna_design_core.application.run_service import RunService
    from dna_design_core.assurance import stage
    folder=Path(directory);source=folder/'material.json';source.write_text('{"sequence":"ACGT"}',encoding='utf-8')
    definitions=model_definitions(**changes)
    if nested:
        wrapper=action('wrapper',copy.deepcopy(definitions[0][0]['inputs']),[port('product','material')],params=copy.deepcopy(definitions[0][0]['params']))
        wrapper['granularity']='composite'
        definitions.append((wrapper,'def wrapper(ctx, template, offset, unused):\n    return ctx.call("contract_probe.original", inputs={"template":template}, params={"offset":offset,"unused":unused})\n'))
    kit=build(folder/'external',definitions);run=folder/'run'
    created=api.call('run create',directory=run,kit_dirs=[kit]);assert not created['problems'],created
    request=goal([{'source_id':'template','from':str(source),'as':'material','input_origin':'user_file','declared':{}}])
    declared=api.call('goal declare',root=run,request=request,kit_dirs=[kit]);assert not declared['problems'],declared
    request=plan(declared['result']['goal_digest'],[step('s1','wrapper' if nested else 'original',{'template':{'source':'template'}},{'offset':2,'unused':13})],{'step':'s1','port':'product'})
    submitted=api.call('pipeline submit',root=run,request=request,kit_dirs=[kit]);assert not submitted['problems'],submitted
    executed=api.call('run execute',root=run,kit_dirs=[kit]);assert executed['state']=='COMPLETED',executed
    service=RunService(run,kit_dirs=[kit]);factory=service.view
    candidate=stage.create(run,factory({}),service.session.snapshot(),service.invoker,factory)
    return service.session,service.invoker,factory,candidate


class InlineDocumentTests(unittest.TestCase):
    def test_malformed_inline_schema_is_rejected_before_any_kit_entry(self):
        from dna_design_core.catalog.registry import Catalog
        with tempfile.TemporaryDirectory() as folder:
            rows=inline_definitions();rows[1][0]['inputs'][0]['schema']['type']='not_a_schema_type'
            kit=build(Path(folder)/'external',rows);catalog=Catalog([kit])
            self.assertNotIn('contract_probe.produce',catalog.entries);self.assertNotIn('contract_probe.consume',catalog.entries)
            self.assertEqual(catalog.problems[0]['code'],'KIT_MANIFEST_INVALID')

    def test_document_ports_require_exactly_one_schema_choice(self):
        for direction in ['inputs','outputs']:
            for choice,valid in [('inline',True),('reference',True),('both',False),('neither',False)]:
                with self.subTest(direction=direction,choice=choice):
                    item=port('document','document',input=direction=='inputs')
                    if choice in {'inline','both'}:item['schema']=COUNT
                    if choice in {'reference','both'}:item['schema_ref']='goal-v1'
                    declaration=action('probe');declaration[direction]=[item]
                    self.assertEqual(not schemas.issues('capability-v1',declaration),valid)

    def test_inline_document_roundtrip_is_frozen_and_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=start(folder,inline_definitions())
            request=plan(digest,[step('s1','produce'),step('s2','consume',{'document':{'step':'s1','port':'document'}})],{'step':'s2','port':'number'})
            self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])['problems'],[])
            result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'COMPLETED',result)
            completed=[e['payload'] for e in events(run) if e['type']=='step.completed']
            self.assertEqual(completed[-1]['values'],{'number':7})
            stored=run/'store/documents'/(completed[0]['outputs']['documents']['document'][0]+'.json')
            self.assertEqual(json.loads(stored.read_text(encoding='utf-8')),{'count':7})
            created=events(run)[0]['payload'];catalog=json.loads((run/created['catalog_ref']).read_text(encoding='utf-8'))
            declaration=next(r['declaration'] for r in catalog['capabilities'] if r['declaration']['id']=='contract_probe.produce')
            self.assertEqual(declaration['outputs'][0]['schema'],COUNT)

    def test_invalid_inline_output_is_not_persisted(self):
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=start(folder,inline_definitions(bad_output=True))
            request=plan(digest,[step('s1','produce')],{'step':'s1','port':'document'})
            self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])['problems'],[])
            result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'HALTED',result)
            failed=next(e['payload'] for e in events(run) if e['type']=='step.failed')
            self.assertEqual(failed['failure']['code'],'CAPABILITY_OUTPUT_INVALID')
            self.assertEqual(failed['retained_outputs']['outputs']['documents'],{})
            self.assertFalse(any(json.loads(p.read_text(encoding='utf-8'))=={'count':'seven'} for p in (run/'store/documents').glob('*.json')))

    def test_invalid_inline_input_fails_before_consumer(self):
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=start(folder,inline_definitions(strict_input=True))
            request=plan(digest,[step('s1','produce'),step('s2','consume',{'document':{'step':'s1','port':'document'}})],{'step':'s2','port':'number'})
            self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])['problems'],[])
            result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'HALTED',result)
            failed=next(e['payload'] for e in events(run) if e['type']=='step.failed')
            self.assertEqual(failed['step_id'],'s2');self.assertEqual(failed['failure']['code'],'PLAN_INPUT_UNBOUND')


class KnowledgeTests(unittest.TestCase):
    def test_loaded_other_kit_package_is_not_readable(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            kit=build(folder/'external',knowledge_definitions(),knowledge={'knowledge/table.json':rule(ROOT)})
            other=build(folder/'other',[(action('inspect',outputs=[port('number','value')],owner='other'),
                'def inspect(ctx):\n    return Outcome(values={"number":1})\n')],owner='other',knowledge={'knowledge/table.json':rule(ROOT)})
            run=folder/'run';kits=[kit,other]
            self.assertEqual(api.call('run create',directory=run,kit_dirs=kits)['problems'],[])
            declared=api.call('goal declare',root=run,kit_dirs=kits,request=goal())
            request=plan(declared['result']['goal_digest'],[step('s1','read',params={'pack':'kit:other/knowledge/table.json'})],{'step':'s1','port':'number'})
            self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=kits)['problems'],[])
            result=api.call('run execute',root=run,kit_dirs=kits)
            self.assertEqual(result['state'],'HALTED',result)
            self.assertEqual(result['problems'][0]['code'],'KNOWLEDGE_SOURCE_INVALID')
            self.assertIn('own owner',result['problems'][0]['message'])

    def test_core_reads_core_package_but_not_kit_package(self):
        from dna_design_core.application.run_service import RunService
        from dna_design_core.engine.invoker import Context
        from dna_design_core.kernel.errors import ToolkitError
        with tempfile.TemporaryDirectory() as folder:
            service=RunService();service.catalog.knowledge['core/knowledge/table.json']=rule(ROOT)
            service.create(Path(folder)/'run')
            ctx=Context(service.invoker,{'owner':'core'},'test',folder,None,False)
            self.assertEqual(ctx.knowledge('core/knowledge/table.json')['parameters'],{'count':7})
            with self.assertRaises(ToolkitError):ctx.knowledge('kit:contract_probe/knowledge/table.json')

    def prepare(self,folder):
        return start(folder,knowledge_definitions(),knowledge={'knowledge/table.json':rule(ROOT)})

    def submit(self,run,kit,digest,params=None):
        request=plan(digest,[step('s1','read',params=params)],{'step':'s1','port':'number'})
        self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])['problems'],[])

    def test_action_and_check_read_frozen_copy_via_one_path(self):
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=self.prepare(folder);self.submit(run,kit,digest)
            # Edit live knowledge after run creation. The frozen content remains 7.
            path=kit/'knowledge/table.json';live=json.loads(path.read_text(encoding='utf-8'));live['parameters']['count']=42
            path.write_text(json.dumps(live),encoding='utf-8')
            result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'COMPLETED',result)
            completed=next(e['payload'] for e in events(run) if e['type']=='step.completed')
            self.assertEqual(completed['values'],{'number':7})
            judged=api.call('judge',root=run,kit_dirs=[kit],also=['contract_probe.check_read'])
            verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='contract_probe.check_read')
            self.assertEqual(verdict['outcome'],'PASS',verdict)
            self.assertEqual(verdict['evidence']['count'],7)
            from dna_design_core.kernel.ports import View
            from dna_design_core.engine.view import ReadView
            self.assertFalse(hasattr(View,'knowledge'));self.assertFalse(hasattr(ReadView,'knowledge'))

    def test_changed_frozen_knowledge_is_integrity_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=self.prepare(folder);self.submit(run,kit,digest)
            catalog=json.loads((run/events(run)[0]['payload']['catalog_ref']).read_text(encoding='utf-8'))
            path=run/'store/documents'/(catalog['knowledge'][0]['digest']+'.json')
            changed=json.loads(path.read_text(encoding='utf-8'));changed['parameters']['count']=9
            path.write_text(json.dumps(changed),encoding='utf-8')
            result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'HALTED',result)
            self.assertEqual(result['problems'][0]['category'],'INTEGRITY',result)
            self.assertEqual(result['problems'][0]['code'],'STORE_CORRUPT')

    def test_cross_kit_and_core_pack_reads_are_denied(self):
        for pack in ['kit:other/knowledge/table.json','core/knowledge/table.json']:
            with self.subTest(pack=pack),tempfile.TemporaryDirectory() as folder:
                run,kit,digest=self.prepare(folder);self.submit(run,kit,digest,{'pack':pack})
                result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'HALTED',result)
                self.assertEqual(result['problems'][0]['code'],'KNOWLEDGE_SOURCE_INVALID')


class ModelTests(unittest.TestCase):
    def test_nested_model_without_recorded_parameters_is_unknown(self):
        from dna_design_core.engine.view import ReadView
        with tempfile.TemporaryDirectory() as folder:
            session,invoker,factory,candidate=prepared_model(folder,nested=True)
            history=session.events();recorded=[e for e in history if e['type']=='call.recorded' and e['payload']['capability']['id']=='contract_probe.original']
            self.assertEqual(len(recorded),1)
            # SPEC 945d702 now requires these fields on fresh records. Retain
            # the original missing-record negative through a copied legacy view.
            recorded[0]['payload'].pop('params');recorded[0]['payload'].pop('params_digest')
            result=invoker.invoke('check.model_agreement',{}, {},parent='final',view=ReadView(session.root,history,session.snapshot(),candidate))
            verdict=result.verdicts[0];self.assertEqual(verdict['outcome'],'UNKNOWN')
            self.assertEqual(verdict['evidence']['not_checked'][0]['event'],recorded[0]['hash'])

    def test_bad_model_names_and_product_ports_are_isolated(self):
        from dna_design_core.catalog.registry import Catalog
        changes=[('unknown_input',lambda rows:rows[1][0]['inputs'][0].update(name='absent')),
                 ('unknown_parameter',lambda rows:rows[1][0]['params']['properties'].update(absent={'type':'integer'})),
                 ('original_no_product',lambda rows:rows[0][0]['outputs'][0].update(name='result')),
                 ('model_no_product',lambda rows:rows[1][0]['outputs'][0].update(name='result')),
                 ('product_not_material',lambda rows:rows[1][0]['outputs'][0].update(type='materials'))]
        for name,change in changes:
            with self.subTest(case=name),tempfile.TemporaryDirectory() as folder:
                rows=model_definitions();change(rows);kit=build(Path(folder)/'external',rows)
                catalog=Catalog([kit]);self.assertNotIn('contract_probe.original',catalog.entries)
                self.assertIn('seq.reverse_complement',catalog.entries)
                error=next(p for p in catalog.problems if p['code']=='KIT_MANIFEST_INVALID')
                self.assertIn('model',error['message'].lower())

    def test_model_uses_named_recorded_arguments_and_compares_content_not_annotations(self):
        variants=[({},'PASS',[]),({'feature':True},'PASS',[]),({'sequence':'ACGA'},'FAIL',['sequence']),
                  ({'topology':'circular'},'FAIL',['topology']),({'ends':{'left':'A','right':'T'}},'FAIL',['ends'])]
        for changes,outcome,fields in variants:
            with self.subTest(changes=changes),tempfile.TemporaryDirectory() as folder:
                folder=Path(folder);source=folder/'material.json';source.write_text('{"sequence":"ACGT"}',encoding='utf-8')
                kit=build(folder/'external',model_definitions(**changes));run=folder/'run'
                self.assertEqual(api.call('run create',directory=run,kit_dirs=[kit])['problems'],[])
                request=goal([{'source_id':'template','from':str(source),'as':'material','input_origin':'user_file','declared':{}}])
                declared=api.call('goal declare',root=run,request=request,kit_dirs=[kit]);self.assertEqual(declared['problems'],[])
                request=plan(declared['result']['goal_digest'],[step('s1','original',{'template':{'source':'template'}},{'offset':2,'unused':13})],{'step':'s1','port':'product'})
                self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])['problems'],[])
                result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'COMPLETED',result)
                judged=api.call('judge',root=run,kit_dirs=[kit]);self.assertEqual(judged['problems'],[])
                verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='check.model_agreement')
                self.assertEqual(verdict['outcome'],outcome,verdict)
                self.assertEqual(verdict['evidence']['differences'][0]['fields'] if fields else [],fields)
                if not fields:self.assertEqual(verdict['evidence']['differences'],[])
                self.assertFalse(any(e['type']=='call.recorded' and e['payload']['capability']['id'] in {'contract_probe.original','contract_probe.predict'} for e in events(run)))


class MaterialsTests(unittest.TestCase):
    def test_missing_or_reordered_materials_still_fail_lineage_and_replay(self):
        from dna_design_core.application.run_service import RunService
        from dna_design_core.engine.view import ReadView
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=start(folder,materials_definitions())
            request=plan(digest,[step('s1','pieces'),step('s2','total',{'pieces':{'step':'s1','port':'pieces'}})],{'step':'s2','port':'number'})
            self.assertEqual(api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])['problems'],[])
            self.assertEqual(api.call('run execute',root=run,kit_dirs=[kit])['state'],'COMPLETED')
            service=RunService(run,kit_dirs=[kit]);snapshot=service.session.snapshot();candidate={'catalog':snapshot}
            for change in ['missing','reordered']:
                with self.subTest(change=change):
                    history=service.session.events();completed=next(e['payload'] for e in history if e['type']=='step.completed')
                    original=completed['outputs']['materials']['pieces'];self.assertEqual(len(original),2)
                    completed['outputs']['materials']['pieces']=original[:1] if change=='missing' else original[::-1]
                    for check in ['check.lineage','check.replay']:
                        result=service.invoker.invoke(check,{}, {},parent='final',view=ReadView(run,history,snapshot,candidate))
                        self.assertEqual(result.verdicts[0]['outcome'],'FAIL',result.verdicts)
                        if check=='check.replay':
                            row=next(v for v in result.verdicts[0]['evidence']['differences'] if v['step_id']=='s2')
                            self.assertIn('input_ids',row['fields'])

    def test_collection_and_explicit_item_bindings_run_and_replay(self):
        for consumer,reference,expected in [('total',{'step':'s1','port':'pieces'},8),('single',{'step':'s1','port':'pieces','index':1},4)]:
            with self.subTest(consumer=consumer),tempfile.TemporaryDirectory() as folder:
                run,kit,digest=start(folder,materials_definitions())
                request=plan(digest,[step('s1','pieces'),step('s2',consumer,{'pieces' if consumer=='total' else 'piece':reference})],{'step':'s2','port':'number'})
                result=api.call('pipeline submit',root=run,request=request,kit_dirs=[kit]);self.assertEqual(result['problems'],[],result)
                result=api.call('run execute',root=run,kit_dirs=[kit]);self.assertEqual(result['state'],'COMPLETED',result)
                self.assertEqual([e['payload']['values'] for e in events(run) if e['type']=='step.completed'][-1],{'number':expected})
                judged=api.call('judge',root=run,kit_dirs=[kit]);self.assertEqual(judged['problems'],[],judged)
                selected={r['verdict']['check']['id']:r['verdict'] for r in judged['result']['verdicts']}
                for name in ['check.lineage','check.replay']:self.assertEqual(selected[name]['outcome'],'PASS',selected[name])

    def test_lists_of_sources_or_steps_and_literal_collections_are_rejected(self):
        bad=[[{'source':'one'},{'source':'two'}],[{'step':'s1','port':'pieces','index':0},{'step':'s1','port':'pieces','index':1}],
             [{'step':'s1','port':'pieces'},{'step':'s2','port':'pieces'}],{'literal':[{'sequence':'ACGT'}]},
             {'step':'s1','port':'pieces','index':0}]
        with tempfile.TemporaryDirectory() as folder:
            run,kit,digest=start(folder,materials_definitions());before=(run/'journal.ndjson').read_bytes()
            for ref in bad:
                with self.subTest(reference=ref):
                    request=plan(digest,[step('s1','pieces'),step('s2','total',{'pieces':ref})],{'step':'s2','port':'number'})
                    result=api.call('pipeline submit',root=run,request=request,kit_dirs=[kit])
                    self.assertEqual(result['problems'][0]['category'],'INVALID_INPUT',result)
                    self.assertIn('materials',result['result']['failure']['details']['problems'][0]['message'])
                    self.assertEqual((run/'journal.ndjson').read_bytes(),before)


class LoadingSeamTests(unittest.TestCase):
    def test_external_action_and_check_use_runtime_loading_for_all_three_probes(self):
        from dna_design_core.catalog.registry import Catalog
        from dna_design_core.engine.loading import Loader
        from structure.test_runtime_contracts import RuntimeStructureTests
        from unit.test_capabilities import CapabilityTests
        with tempfile.TemporaryDirectory() as folder:
            kit=build(Path(folder)/'external',knowledge_definitions())
            catalog=Catalog([kit]);self.assertEqual(catalog.problems,[])
            self.assertIn('contract_probe.read',catalog.entries);self.assertIn('contract_probe.check_read',catalog.entries)
            RuntimeStructureTests().test_atomic_capabilities_do_not_call_other_capabilities(catalog)
            RuntimeStructureTests().test_verdict_constructor_and_exception_boundary(catalog)
            CapabilityTests().test_generated_declarations_match_decorator_exports(catalog)
            entry=catalog.entries['contract_probe.read'];entry['path'].write_text('changed=1\n',encoding='utf-8')
            from dna_design_core.kernel.errors import ToolkitError
            with self.assertRaises(ToolkitError) as caught:Loader().load(entry)
            self.assertEqual(caught.exception.problem.code,'CAPABILITY_VERSION_MISMATCH')


if __name__=='__main__':unittest.main()
