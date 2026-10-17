"""Hand arithmetic and preconstructed primer/core/amplicon answers."""
import copy
import math
import unittest

from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord

from dna_design_core.biology import public as biology


class PrimerTests(unittest.TestCase):
    def test_tm_hand_sum_non_self_complementary(self):
        # ACGTACGA: AC,CG,GT,TA,AC,CG,GA stacks sum to -61.8/-165.1.
        # Two terminal AT pairs add 4.6/8.2; effective concentration = 50e-9/4.
        expected = -57200 / (-156.9 + 0.368 * 7 * math.log(0.05) + 1.987 * math.log(50e-9 / 4)) - 273.15
        result = biology.calculate_tm("ACGTACGA")
        self.assertAlmostEqual(float(result["tm"]), expected, places=7)
        self.assertEqual(result["parameters"]["nn_table"], "DNA_NN3")
        self.assertEqual(result["parameters"]["dnac1_nM"], "25")
        self.assertFalse(result["parameters"]["self_complementary"])
        self.assertEqual(result["unit"], "degC")

    def test_tm_hand_symmetry_and_magnesium_conversion(self):
        # Self-complementary AT: -7.2+4.6 kcal; -20.4+8.2-1.4 cal/K.
        expected = -2600 / (-13.6 + 0.368 * math.log(0.05) + 1.987 * math.log(50e-9)) - 273.15
        result = biology.calculate_tm("AT")
        self.assertAlmostEqual(float(result["tm"]), expected, places=7)
        self.assertTrue(result["parameters"]["self_complementary"])
        # Method 5 uses sodium equivalent Na+120*sqrt(Mg-dNTP) in mM.
        parameters = biology.TmParameters(magnesium_mM="2", dntp_mM="0.5")
        sodium_M = (50 + 120 * math.sqrt(1.5)) / 1000
        expected_mg = -57200 / (-156.9 + 0.368 * 7 * math.log(sodium_M) + 1.987 * math.log(50e-9 / 4)) - 273.15
        self.assertAlmostEqual(float(biology.calculate_tm("ACGTACGA", parameters)["tm"]), expected_mg, places=7)

    def test_tm_invalid_inputs_and_explicit_concentrations(self):
        for sequence in ("A", "ACGN", ""):
            with self.assertRaises(ValueError):
                biology.calculate_tm(sequence)
        for value in ("0", "NaN", "-2", "Infinity", "bogus"):
            with self.assertRaises(ValueError):
                biology.TmParameters(sodium_mM=value).concentrations()
        with self.assertRaises(TypeError):
            biology.TmParameters(total_oligo_nM=50).concentrations()

    def test_dimer_full_and_second_3prime_hand_alignment(self):
        self.assertEqual(biology.dimer_metrics("AAAACCCC", "GGGGTTTT"),
                         {"max_contiguous_bp": 8, "max_3prime_bp": 8})
        # RC(GGTT)=AACC, match at first[0:4]; second's 3-prime anchors entire run.
        self.assertEqual(biology.dimer_metrics("AACCGT", "GGTT"),
                         {"max_contiguous_bp": 4, "max_3prime_bp": 4})
        self.assertEqual(biology.dimer_metrics("AAAA", "AAAA"),
                         {"max_contiguous_bp": 0, "max_3prime_bp": 0})

    def test_hairpin_and_counts_hand_answer(self):
        self.assertEqual(biology.hairpin_metrics("GCGAAACGC"),
                         {"max_stem_bp": 3, "max_3prime_stem_bp": 3, "min_loop_nt": 3})
        self.assertEqual(biology.hairpin_metrics("AAAAA")["max_stem_bp"], 0)
        result = biology.primer_quality("ACGTTTTTGC", partner="AAAA")
        self.assertEqual((result["length"], result["gc_percent"], result["longest_T_run_nt"],
                          result["longest_run_nt"], result["gc_in_last_5nt"]), (10, "40.00000000", 5, 5, 2))

    def test_quality_explicit_limits_pass_fail(self):
        limits = {"length_min": 8, "length_max": 15, "gc_min": "20", "gc_max": "80",
                  "max_T_run": 4, "max_3prime_dimer": 20, "max_hairpin_stem": 20}
        passed = biology.evaluate_primer_quality(biology.primer_quality("ACGTACGA"), limits)
        failed = biology.evaluate_primer_quality(biology.primer_quality("ACGTTTTTGC"), limits)
        self.assertEqual(passed["violations"], [])
        self.assertEqual(failed["violations"], ["poly_T"])
        self.assertFalse(failed["checks"]["poly_T"])
        with self.assertRaises(ValueError):
            biology.evaluate_primer_quality({}, {})
        with self.assertRaises(ValueError):
            biology.evaluate_primer_quality(biology.primer_quality("ACGTACGA"), {**limits, "gc_min": "bad"})

    def test_boulder_codec_exact_answer_and_rejections(self):
        text = "SEQUENCE_ID=constructed\nSEQUENCE_TEMPLATE=ACGT\nPRIMER_NUM_RETURN=2\n=\n"
        tags = {"SEQUENCE_ID": "constructed", "SEQUENCE_TEMPLATE": "ACGT", "PRIMER_NUM_RETURN": 2}
        self.assertEqual(biology.encode_boulder(tags), text)
        self.assertEqual(biology.parse_boulder(text), {key: str(value) for key, value in tags.items()})
        self.assertEqual(biology.parse_boulder("PRIMER_LEFT_0_SELF_ANY_STUCT=SEQ\tAC\nSTR\tTG\n\n=\n"),
                         {"PRIMER_LEFT_0_SELF_ANY_STUCT": "SEQ\tAC\nSTR\tTG"})
        for invalid in ("A=1\nA=2\n=\n", "A=1\n", "A=1\n=\nA=2\n=\n", "nonsense\n=\n"):
            with self.assertRaises(ValueError):
                biology.parse_boulder(invalid)
        with self.assertRaises(ValueError):
            biology.encode_boulder({"A": "unsafe\nB=1"})

    def test_primer3_request_complete_oligos_and_parameters(self):
        text = biology.primer3_check_request("ACGTACGA", reverse="AACCGGTT", thermodynamic_path="config/")
        # Literal request fields independent of the parser under test.
        for line in ("SEQUENCE_PRIMER=ACGTACGA\n", "SEQUENCE_PRIMER_REVCOMP=AACCGGTT\n",
                     "PRIMER_DNA_CONC=50\n", "PRIMER_TM_FORMULA=1\n", "PRIMER_SALT_CORRECTIONS=1\n",
                     "PRIMER_SALT_DIVALENT=0\n", "PRIMER_DNTP_CONC=0\n"):
            self.assertIn(line, text)
        with self.assertRaises(ValueError):
            biology.primer3_check_request("ACGT" * 10, thermodynamic_path="config/")


class PCRTests(unittest.TestCase):
    def test_binding_cross_origin_on_each_strand(self):
        hits = biology.find_binding_sites("AAACCCTTTGGG", "GGAA", circular=True, strand=1)
        self.assertEqual(hits, ({"start": 10, "end": 2, "end_unwrapped": 14, "strand": 1,
                                 "wraps_origin": True, "core_length": 4, "core": "GGAA", "tail_5prime": ""},))
        reverse = biology.find_binding_sites("AAACCCTTTGGG", "TTCC", circular=True, strand=-1)
        self.assertEqual((reverse[0]["start"], reverse[0]["end"]), (10, 2))
        self.assertEqual(biology.find_binding_sites("AAACCCTTTGGG", "GGAA", strand=1), ())

    def test_pcr_tails_hand_answer(self):
        template = "ACGTAACCGGTTGATC"
        # F core ACGTA at 0; R core GATC binds 12..16; tails TT and GC.
        result = biology.simulate_pcr(template, "TTACGTA", "GCGATC", forward_core_length=5, reverse_core_length=4)
        self.assertEqual(result["sequence"], "TTACGTAACCGGTTGATCGC")
        self.assertEqual(result["template_span"], 16)
        self.assertEqual(result["forward_binding"]["tail_5prime"], "TT")
        # Default is full-primer matching: no silently inferred tail.
        self.assertEqual(biology.predict_pcr_products(template, "TTACGTA", "GCGATC"), ())

    def test_circular_pcr_literal_cross_origin_product(self):
        result = biology.simulate_pcr("AAACCCTTTGGG", "TTT", "GGG", circular=True)
        self.assertEqual(result["sequence"], "TTTGGGAAACCC")
        self.assertEqual(result["template_start"], 6)
        self.assertEqual(result["template_end_unwrapped"], 18)
        self.assertTrue(result["wraps_origin"])
        self.assertEqual(biology.predict_pcr_products("AAACCCTTTGGG", "TTT", "GGG"), ())

    def test_repeated_sites_enumerated_and_unique_simulator_rejects(self):
        template = "ACGTAAAACGTCCC"
        products = biology.predict_pcr_products(template, "ACGT", "GGG")
        self.assertEqual([product["sequence"] for product in products], ["ACGTAAAACGTCCC", "ACGTCCC"])
        with self.assertRaisesRegex(ValueError, "found 2"):
            biology.simulate_pcr(template, "ACGT", "GGG")
        with self.assertRaisesRegex(ValueError, "found 0"):
            biology.simulate_pcr(template, "TTTT", "GGG")

    def test_pcr_record_coordinate_mapping_and_no_mutation(self):
        template = SeqRecord(Seq("ACGTAACCGGTTGATC"), id="constructed",
                             annotations={"molecule_type": "DNA", "topology": "linear"})
        template.features = [SeqFeature(SimpleLocation(5, 9, strand=-1), type="gene", qualifiers={"label": ["C1"]})]
        template.letter_annotations["synthetic_values"] = list(range(16))
        original = copy.deepcopy(template)
        result, prediction = biology.simulate_pcr_record(
            template, "TTACGTA", "GCGATC", forward_core_length=5, reverse_core_length=4,
        )
        self.assertEqual(str(result.seq), "TTACGTAACCGGTTGATCGC")
        self.assertEqual((int(result.features[0].location.start), int(result.features[0].location.end)), (7, 11))
        self.assertEqual(result.features[0].location.strand, -1)
        self.assertEqual(result.letter_annotations["synthetic_values"], [None, None] + list(range(16)) + [None, None])
        self.assertEqual(str(template.seq), str(original.seq))
        self.assertEqual(template.features, original.features)
        self.assertEqual(prediction["sequence"], str(result.seq))


if __name__ == "__main__":
    unittest.main()
