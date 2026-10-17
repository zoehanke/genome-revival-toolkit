"""Real nested reaction checks with no candidate supplied to the simulator."""
import tempfile
import unittest
from unittest.mock import patch
from dna_design_core.engine.view import ReadView
from tests.s1c_reaction_runtime import prepare


def selected(receipt):return {r['verdict']['check']['id']:r['verdict'] for r in receipt['result']['verdicts']}


class ReactionChainTests(unittest.TestCase):
    def test_unrelated_coordinate_branch_is_not_a_physical_preparation_step(self):
        for wrong,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(wrong_candidate=wrong),tempfile.TemporaryDirectory() as folder:
                root,kit,call,service=prepare(folder,wrong=wrong,extra_rotation=True)
                judged=call('judge');self.assertEqual(judged['problems'],[],judged)
                verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='check.reaction_chain')
                self.assertEqual(verdict['outcome'],expected,verdict)

    def test_simulator_finishes_before_candidate_material_is_read(self):
        from dna_design_core.engine.invoker import Invoker
        with tempfile.TemporaryDirectory() as folder:
            root,kit,call,service=prepare(folder)
            payload=service.session.steps()['s1']['completed']['payload']
            candidate_id=payload['outputs']['materials']['product'][0];timeline=[]
            original_invoke=Invoker._invoke;original_material=ReadView.material
            def invoke(bound,use,inputs,params,**arguments):
                result=original_invoke(bound,use,inputs,params,**arguments)
                if use.split('@')[0]=='pcr.simulate':
                    self.assertEqual(set(inputs),{'template','forward','reverse'})
                    self.assertEqual(inputs['template']['sequence'],'TTAACTGGACTCCGATC')
                    timeline.append('simulation_completed')
                return result
            def read(view,identity):
                if identity==candidate_id:timeline.append('candidate_read')
                return original_material(view,identity)
            candidate={'catalog':service.session.snapshot(),'outputs':[]}
            with patch.object(Invoker,'_invoke',invoke),patch.object(ReadView,'material',read):
                result=service.invoker.invoke('check.reaction_chain',{}, {},parent='final',view=service.view(candidate))
            self.assertEqual(result.verdicts[0]['outcome'],'PASS',result.verdicts)
            self.assertIn('candidate_read',timeline);self.assertIn('simulation_completed',timeline)
            self.assertGreater(timeline.index('candidate_read'),timeline.index('simulation_completed'))

    def test_original_route_passes_but_one_base_candidate_fails_both_checks(self):
        for wrong,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(wrong_candidate=wrong),tempfile.TemporaryDirectory() as folder:
                root,kit,call,service=prepare(folder,wrong=wrong)
                judged=call('judge');self.assertEqual(judged['problems'],[],judged)
                verdicts=selected(judged)
                self.assertEqual(verdicts['check.reaction_chain']['outcome'],expected,verdicts['check.reaction_chain'])
                self.assertEqual(verdicts['check.model_agreement']['outcome'],expected,verdicts['check.model_agreement'])
                if not wrong:self.assertEqual(verdicts['check.pcr_product']['outcome'],'PASS',verdicts['check.pcr_product'])

    def test_actual_parameter_tamper_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            root,kit,call,service=prepare(folder)
            history=service.session.events();event=next(e for e in history if e['type']=='call.recorded' and e['payload']['capability']['id']=='pcr.simulate')
            event['payload']['params']['forward_core_length']=2
            candidate={'catalog':service.session.snapshot(),'outputs':[]}
            result=service.invoker.invoke('check.reaction_chain',{}, {},parent='final',view=ReadView(root,history,service.session.snapshot(),candidate))
            self.assertEqual(result.verdicts[0]['outcome'],'FAIL',result.verdicts)
            self.assertIn('params_digest',result.verdicts[0]['evidence']['differences'][0]['fields'])

    def test_unknown_route_remains_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            root,kit,call,service=prepare(folder,method='unsupported_reaction')
            verdict=selected(call('judge'))['check.reaction_chain']
            self.assertEqual(verdict['outcome'],'UNKNOWN',verdict)


if __name__=='__main__':unittest.main()
