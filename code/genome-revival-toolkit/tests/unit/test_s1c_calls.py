"""Nested PCR records actual parameters and retains replayable input values."""
import json
from pathlib import Path
import tempfile
import unittest

from dna_design_core.application import api
from dna_design_core.storage.store import Store
from tests.fixtures.contract_probe import action, port, build, goal, plan, step


def nested_pcr(folder,core_length):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    declarations=action('nested_pcr',outputs=[port('product','material')],params={
        'type':'object','properties':{'core_length':{'type':'integer'}},'required':['core_length'],'additionalProperties':False})
    declarations['granularity']='composite'
    kit=build(folder/'external',[(declarations,'''def nested_pcr(ctx, core_length):
    result=ctx.call("pcr.simulate", inputs={
        "template":{"sequence":"TTAACTGGACTCCGATC","topology":"linear","strandedness":"double"},
        "forward":{"sequence":"AACT","topology":"linear","strandedness":"single"},
        "reverse":{"sequence":"GATC","topology":"linear","strandedness":"single"}},
        params={"forward_core_length":core_length,"reverse_core_length":4})
    return Outcome(products={"product":result.products["product"]})
''')])
    run=folder/'run'
    created=api.call('run create',directory=run,kit_dirs=[kit]);assert not created['problems'],created
    declared=api.call('goal declare',root=run,kit_dirs=[kit],request=goal())
    request=plan(declared['result']['goal_digest'],[step('s1','nested_pcr',params={'core_length':core_length})],{'step':'s1','port':'product'})
    submitted=api.call('pipeline submit',root=run,kit_dirs=[kit],request=request);assert not submitted['problems'],submitted
    result=api.call('run execute',root=run,kit_dirs=[kit])
    events=[json.loads(s) for s in (run/'journal.ndjson').read_text(encoding='utf-8').splitlines()]
    record=next(e for e in events if e['type']=='call.recorded' and e['payload']['capability']['id']=='pcr.simulate')
    return run,kit,result,record


class NestedCallTests(unittest.TestCase):
    def test_parameter_tamper_fails_independent_nested_model_check(self):
        from tests.unit.test_s1_followup2 import prepared_model
        from dna_design_core.engine.view import ReadView
        with tempfile.TemporaryDirectory() as folder:
            session,invoker,factory,candidate=prepared_model(folder,nested=True)
            good=invoker.invoke('check.model_agreement',{}, {},parent='final',view=factory(candidate))
            self.assertEqual(good.verdicts[0]['outcome'],'PASS',good.verdicts)
            history=session.events()
            event=next(e for e in history if e['type']=='call.recorded' and e['payload']['capability']['id']=='contract_probe.original')
            event['payload']['params']['offset']=3
            bad=invoker.invoke('check.model_agreement',{}, {},parent='final',view=ReadView(session.root,history,session.snapshot(),candidate))
            self.assertEqual(bad.verdicts[0]['outcome'],'FAIL',bad.verdicts)
            self.assertEqual(bad.verdicts[0]['evidence']['differences'][0]['fields'],['params_digest'])

    def test_actual_nested_parameters_distinguish_unique_and_ambiguous_pcr(self):
        records=[]
        for core_length,state in [(4,'COMPLETED'),(2,'HALTED')]:
            with self.subTest(core_length=core_length),tempfile.TemporaryDirectory() as folder:
                run,kit,result,record=nested_pcr(folder,core_length)
                self.assertEqual(result['state'],state,result)
                self.assertIn('params',record['payload'])
                self.assertEqual(record['payload']['params'],{'forward_core_length':core_length,'reverse_core_length':4})
                self.assertEqual(len(record['payload']['params_digest']),64)
                records.append(record['payload']['params_digest'])
                template=Store(run).get('materials',record['payload']['input_ids']['template'])
                self.assertEqual(template['sequence'],'TTAACTGGACTCCGATC')
                if core_length==4:
                    product=Store(run).get('materials',record['payload']['outputs']['materials']['product'][0])
                    self.assertEqual(product['sequence'],'AACTGGACTCCGATC')
                else:self.assertIn('found 2',record['payload']['failure']['details']['reason'])
        self.assertEqual(len(records),2)
        self.assertNotEqual(records[0],records[1])


if __name__=='__main__':unittest.main()
