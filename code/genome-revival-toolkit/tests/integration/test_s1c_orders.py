"""Full order sequences are compared with real invocation primer values."""
import tempfile
import unittest
from tests.s1c_reaction_runtime import prepare


class OrderTableTests(unittest.TestCase):
    def test_diagnostic_assay_proposal_is_not_promoted_to_a_preparation_order(self):
        from tests.construct_runtime import create
        from dna_design_core.application import api
        with tempfile.TemporaryDirectory() as folder:
            service,receipts,execution=create(folder,'pcr')
            self.assertEqual(execution['state'],'COMPLETED')
            judged=api.call('judge',root=service.root);self.assertEqual(judged['problems'],[],judged)
            verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='check.order_table')
            self.assertEqual(verdict['outcome'],'PASS',verdict)
            self.assertEqual(len(verdict['evidence']['checked']),2)

    def test_full_primers_match_but_changed_5prime_tail_fails(self):
        for wrong,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(wrong_tail=wrong),tempfile.TemporaryDirectory() as folder:
                root,kit,call,service=prepare(folder,wrong_order=wrong)
                judged=call('judge');self.assertEqual(judged['problems'],[],judged)
                verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='check.order_table')
                self.assertEqual(verdict['outcome'],expected,verdict)
                if wrong:self.assertTrue(verdict['evidence']['differences'])


if __name__=='__main__':unittest.main()
