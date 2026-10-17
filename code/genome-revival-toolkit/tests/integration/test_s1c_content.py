"""Real engine/CHECK runs; feature/sequence oracles come from construction."""
from copy import deepcopy
import tempfile
import unittest
from tests.s1c_runtime import material,run_material


class AnnotationIntegrityTests(unittest.TestCase):
    def test_legal_and_introduced_bad_strand_have_opposite_verdicts(self):
        source=material()
        for changed,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(introduced=changed),tempfile.TemporaryDirectory() as folder:
                product=material(strand=2) if changed else None
                root,kit,call,judged,verdicts=run_material(folder,source,product)
                verdict=verdicts['check.annotation_integrity'];self.assertEqual(verdict['outcome'],expected,verdict)
                if changed:self.assertEqual(verdict['evidence']['findings'][0]['origin'],'INTRODUCED')

    def test_unchanged_bad_input_annotation_is_explicitly_inherited(self):
        with tempfile.TemporaryDirectory() as folder:
            root,kit,call,judged,verdicts=run_material(folder,material(strand=2))
            verdict=verdicts['check.annotation_integrity'];self.assertEqual(verdict['outcome'],'PASS',verdict)
            self.assertEqual(verdict['evidence']['findings'][0]['origin'],'INHERITED')
            self.assertIn('Inherited input findings remain',judged['labels'])

    def test_new_compound_envelope_error_and_valid_wrap_control(self):
        source=material();source['topology']='circular'
        valid=deepcopy(source);valid['features'][0].update(start=0,end=9,operator='join',parts=[{'start':6,'end':9,'strand':1},{'start':0,'end':3,'strand':1}])
        for broken,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(broken=broken),tempfile.TemporaryDirectory() as folder:
                product=deepcopy(valid)
                if broken:product['features'][0]['parts'][0]['end']=10
                root,kit,call,judged,verdicts=run_material(folder,source,product)
                self.assertEqual(verdicts['check.annotation_integrity']['outcome'],expected,verdicts['check.annotation_integrity'])


if __name__=='__main__':unittest.main()
