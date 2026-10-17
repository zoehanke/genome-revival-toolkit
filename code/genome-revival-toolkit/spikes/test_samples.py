"""Independent construction/hand arithmetic. Never imports old code."""
import unittest
from sequence_sample import reverse_complement, scan_linear_pam
from tm_sample import tm_nn


class SequenceSampleTests(unittest.TestCase):
    def test_reverse_complement_by_hand(self):
        self.assertEqual(reverse_complement('AGTCAGAA'),'TTCTGACT')
        self.assertEqual(reverse_complement(''),'')

    def test_forward_anchor_is_at_constructed_join(self):
        sequence='A'*20+'AGG'+'T'*5
        self.assertEqual(scan_linear_pam(sequence,'NGG',20),[{'strand':1,'start':0,'end':20,'pam_start':20,'pam_end':23,'spacer':'A'*20,'pam':'AGG'}])

    def test_reverse_anchor_is_at_constructed_join(self):
        sequence='CCT'+'T'*20
        self.assertEqual(scan_linear_pam(sequence,'NGG',20),[{'strand':-1,'start':3,'end':23,'pam_start':0,'pam_end':3,'spacer':'A'*20,'pam':'AGG'}])

    def test_absent_and_out_of_bounds(self):
        self.assertEqual(scan_linear_pam('A'*20+'AGT','NGG',20),[])
        self.assertEqual(scan_linear_pam('AGG'+'T'*20,'NGG',20),[])

    def test_ambiguous_input_rejected(self):
        with self.assertRaises(ValueError): scan_linear_pam('N'*20+'AGG','NGG',20)


class TmSampleTests(unittest.TestCase):
    def test_at_homopolymer_from_hand_thermodynamics(self):
        # SantaLucia NN3: 9 AA stacks + two terminal A/T terms; saltcorr=5.
        # Independent constants/arithmetic, not Biopython or old output as oracle.
        self.assertAlmostEqual(tm_nn('A'*10,sodium_mm=50,primer_nm=250),13.824567460959202,places=8)

    def test_gc_homopolymer_from_hand_thermodynamics(self):
        # 9 GG/CC stacks + two terminal G/C terms, same salt/concentration.
        self.assertAlmostEqual(tm_nn('C'*10,sodium_mm=50,primer_nm=250),46.20545115304333,places=8)

    def test_unrecognized_base_rejected(self):
        with self.assertRaises(ValueError): tm_nn('ACGN',sodium_mm=50,primer_nm=250)


if __name__=='__main__': unittest.main()
