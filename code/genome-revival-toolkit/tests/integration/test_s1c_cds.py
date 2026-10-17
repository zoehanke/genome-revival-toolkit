"""CDS checks use literal codons and manually specified coordinate transforms."""
from copy import deepcopy
import tempfile
import unittest
from tests.s1c_runtime import material,run_material


class CDSValidityTests(unittest.TestCase):
    def test_shifted_old_cds_without_supported_mapping_is_undetermined_and_fails(self):
        source=material(kind='CDS',sequence='ATGTAATAA')
        product=deepcopy(source);product['sequence']='CCC'+source['sequence']
        product['features'][0].update(start=3,end=12)
        product['features'][0]['parts']=[{'start':3,'end':12,'strand':1}]
        with tempfile.TemporaryDirectory() as folder:
            root,kit,call,judged,verdicts=run_material(folder,source,product)
            verdict=verdicts['check.cds_validity'];self.assertEqual(verdict['outcome'],'FAIL',verdict)
            row=next(f for f in verdict['evidence']['findings'] if f['code']=='INTERNAL_STOP')
            self.assertEqual(row['origin'],'UNDETERMINED')

    def test_complete_cds_and_introduced_internal_stop_have_opposite_verdicts(self):
        for sequence,expected in [('ATGAAATAA','PASS'),('ATGTAATAA','FAIL')]:
            with self.subTest(sequence_case=expected),tempfile.TemporaryDirectory() as folder:
                root,kit,call,judged,verdicts=run_material(folder,material(kind='CDS'),material(kind='CDS',sequence=sequence))
                verdict=verdicts['check.cds_validity'];self.assertEqual(verdict['outcome'],expected,verdict)
                if expected=='FAIL':
                    row=next(f for f in verdict['evidence']['findings'] if f['code']=='INTERNAL_STOP')
                    self.assertEqual(row['origin'],'INTRODUCED');self.assertEqual(row['internal_stop_count'],1)

    def test_inherited_internal_stop_is_pass_for_exact_copy_and_unique_rotation(self):
        bad=material(kind='CDS',sequence='ATGTAATAA')
        source=deepcopy(bad);source['sequence']='CCCATGTAATAAGGG';source['topology']='circular'
        source['features'][0].update(start=3,end=12);source['features'][0]['parts']=[{'start':3,'end':12,'strand':1}]
        rotated=deepcopy(bad);rotated.update(sequence='ATGTAATAAGGGCCC',topology='circular')
        for original,product,mode in [(bad,None,'EXACT_COPY'),(source,rotated,'CIRCULAR_ROTATION')]:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as folder:
                root,kit,call,judged,verdicts=run_material(folder,original,product)
                verdict=verdicts['check.cds_validity'];self.assertEqual(verdict['outcome'],'PASS',verdict)
                row=next(f for f in verdict['evidence']['findings'] if f['code']=='INTERNAL_STOP')
                self.assertEqual(row['origin'],'INHERITED');self.assertEqual(row['comparison']['mode'],mode)
                self.assertIn('Inherited input findings remain',judged['labels'])

    def test_new_frame_start_and_terminal_stop_errors_fail(self):
        for sequence,code in [('ATGAAAATAA','FRAME_LENGTH'),('CCCAAATAA','START_CODON'),('ATGAAACAA','TERMINAL_STOP')]:
            with self.subTest(code=code),tempfile.TemporaryDirectory() as folder:
                product=material(kind='CDS',sequence=sequence)
                product['features'][0]['end']=len(sequence);product['features'][0]['parts'][0]['end']=len(sequence)
                root,kit,call,judged,verdicts=run_material(folder,material(kind='CDS'),product)
                verdict=verdicts['check.cds_validity'];self.assertEqual(verdict['outcome'],'FAIL',verdict)
                self.assertTrue(any(f['code']==code for f in verdict['evidence']['findings']))


if __name__=='__main__':unittest.main()
