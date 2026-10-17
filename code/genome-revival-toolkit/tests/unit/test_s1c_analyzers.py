"""Hand/construction oracles for the newly public pure calculations."""
from copy import deepcopy
import math
import unittest

from dna_design_core.biology.public import annotation_findings,cds_findings,sanity_findings,calculate_tm_explicit


def material():
    return {'sequence':'ATGAAATAA','topology':'linear','strandedness':'double','ends':None,
            'features':[{'start':0,'end':9,'type':'CDS','label':'synthetic',
                         'parts':[{'start':0,'end':9,'strand':1}],'operator':None,'qualifiers':{}}]}


class AnalyzerTests(unittest.TestCase):
    def test_annotation_bounds_and_strand_from_construction(self):
        value=material();self.assertEqual(annotation_findings(value),[])
        wrong=deepcopy(value);wrong['features'][0]['parts'][0]['strand']=2
        self.assertEqual(annotation_findings(wrong),[{'feature_index':0,'code':'INVALID_STRAND'}])
        wrong=deepcopy(value);wrong['features'][0]['parts'][0]['end']=10
        self.assertIn({'feature_index':0,'code':'PART_OUT_OF_BOUNDS'},annotation_findings(wrong))

    def test_cds_literal_start_internal_and_final_codons(self):
        value=material();self.assertEqual(cds_findings(value),[])
        # ATG | TAA | TAA: exactly one internal and one terminal stop, code 1.
        value['sequence']='ATGTAATAA'
        self.assertEqual(cds_findings(value),[{'feature_index':0,'code':'INTERNAL_STOP',
                                             'coding_length':9,'internal_stop_count':1,'translation_table':1}])

    def test_sanity_literal_alphabet_empty_and_end_conflict(self):
        value=material();self.assertEqual(sanity_findings(value),[])
        empty={**value,'sequence':''};self.assertEqual(sanity_findings(empty),[{'code':'EMPTY_MATERIAL'}])
        self.assertEqual(sanity_findings({**value,'sequence':'ACX'}),[{'code':'INVALID_DNA_SYMBOL'}])
        wrong={**value,'topology':'circular','ends':{'left':None,'right':None}}
        self.assertEqual(sanity_findings(wrong),[{'code':'PHYSICAL_END_CONFLICT'}])

    def test_explicit_nn_concentrations_against_hand_sum(self):
        # DNA_NN3 Allawi/SantaLucia 1997 entries for AC CG GT TA AC CG GA:
        # stack H=-61.8 kcal/mol, S=-165.1 cal/K/mol; NN3 init=0/0,
        # two terminal A/T corrections=4.6/8.2. Method-5 salt entropy
        # is .368*(8-1)*ln(.05); effective strand=dnac1-dnac2/2.
        parameters={'dnac1_nM':'250','dnac2_nM':'0','Na_mM':'50','K_mM':'0',
                    'Tris_mM':'0','Mg_mM':'0','dNTPs_mM':'0',
                    'nn_table':'DNA_NN3','saltcorr':5,'selfcomp':False}
        h=(-61.8+4.6)*1000;s=-165.1+8.2+.368*7*math.log(.05)
        expected=h/(s+1.987*math.log(250e-9))-273.15
        actual=calculate_tm_explicit('ACGTACGA',parameters)
        self.assertAlmostEqual(float(actual['tm']),expected,places=8)
        self.assertEqual(actual['parameters'],parameters)
        for changed in ({'Na_mM':'-1'},{'dnac1_nM':'0'},{'nn_table':'undefined'}):
            with self.subTest(invalid=changed),self.assertRaises(ValueError):
                calculate_tm_explicit('ACGTACGA',{**parameters,**changed})


if __name__=='__main__':unittest.main()
