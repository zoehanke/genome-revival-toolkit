"""Physical consistency checks with construction-defined material declarations."""
from copy import deepcopy
import tempfile
import unittest
from tests.s1c_runtime import material,run_material


class BiologicalSanityTests(unittest.TestCase):
    def test_circular_no_ends_passes_but_circular_linear_ends_fail(self):
        for contradictory,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(contradictory=contradictory),tempfile.TemporaryDirectory() as folder:
                product=material();product['topology']='circular'
                if contradictory:product['ends']={'left':{'kind':'blunt','overhang':''},'right':{'kind':'blunt','overhang':''}}
                root,kit,call,judged,verdicts=run_material(folder,material(),product)
                verdict=verdicts['check.biological_sanity'];self.assertEqual(verdict['outcome'],expected,verdict)

    def test_empty_material_fails_and_iupac_unknowns_are_not_erased(self):
        for sequence,expected in [('', 'FAIL'),('ACGTRYSWKMBDHVN','PASS')]:
            with self.subTest(case=expected),tempfile.TemporaryDirectory() as folder:
                product=material(sequence=sequence);product['features']=[]
                root,kit,call,judged,verdicts=run_material(folder,material(),product)
                self.assertEqual(verdicts['check.biological_sanity']['outcome'],expected,verdicts['check.biological_sanity'])

    def test_bad_physical_input_does_not_receive_inherited_exemption(self):
        with tempfile.TemporaryDirectory() as folder:
            bad=material();bad['topology']='circular';bad['ends']={'left':None,'right':None}
            root,kit,call,judged,verdicts=run_material(folder,bad)
            verdict=verdicts['check.biological_sanity'];self.assertEqual(verdict['outcome'],'FAIL',verdict)
            self.assertFalse(any(f.get('origin')=='INHERITED' for f in verdict['evidence']['findings']))


if __name__=='__main__':unittest.main()
