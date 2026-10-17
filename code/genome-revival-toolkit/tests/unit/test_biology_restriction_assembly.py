"""Hand-labelled enzyme cuts, strands, extensions and assembled sequences."""
import copy
import random
import unittest

from dna_design_core.biology import public as biology


class RestrictionTests(unittest.TestCase):
    def test_database_definition_known_ecori_geometry(self):
        definition = biology.enzyme_definition("EcoRI")
        self.assertEqual((definition["recognition"], definition["top_offset"], definition["bottom_offset_from_end"]),
                         ("GAATTC", 1, -1))
        self.assertEqual(definition["source_class"], "database_record")
        for name in ("not_an_enzyme", "RestrictionBatch", "BcgI"):
            with self.assertRaises(ValueError):
                biology.enzyme_definition(name)

    def test_ecori_pst_and_blunt_cut_coordinates_hand_answer(self):
        cases = [("CCGAATTCTT", "EcoRI", 3, 7, "5prime", "AATT"),
                 ("AACTGCAGTT", "PstI", 7, 3, "3prime", "TGCA"),
                 ("CCGATATCGG", "EcoRV", 5, 5, "blunt", "")]
        for sequence, enzyme, top, bottom, kind, extension in cases:
            with self.subTest(enzyme=enzyme):
                hits = biology.scan_restriction_sites(sequence, enzyme)
                self.assertEqual(len(hits), 1)
                self.assertEqual((hits[0]["top_cut"], hits[0]["bottom_cut"], hits[0]["overhang_kind"],
                                  hits[0]["reference_overhang"]), (top, bottom, kind, extension))

    def test_type_iis_both_orientations_and_insufficient_flank(self):
        forward = biology.scan_restriction_sites("TTGGTCTCAAGTCCCGG", "BsaI")[0]
        reverse = biology.scan_restriction_sites("TTAGTCAGAGACCCC", "BsaI")[0]
        self.assertEqual((forward["start"], forward["strand"], forward["top_cut"], forward["bottom_cut"]), (2, 1, 9, 13))
        self.assertEqual((reverse["start"], reverse["strand"], reverse["top_cut"], reverse["bottom_cut"]), (7, -1, 2, 6))
        self.assertEqual(forward["reference_overhang"], "AGTC")
        self.assertEqual(reverse["reference_overhang"], "AGTC")
        hit = biology.scan_restriction_sites("TTGGTCTC", "BsaI")[0]
        self.assertFalse(hit["cuts_within_sequence"])
        self.assertIsNone(hit["reference_overhang"])

    def test_origin_spanning_recognition(self):
        # Constructed GAATTC at circular 8..14: suffix GA + prefix ATTC.
        hit = biology.scan_restriction_sites("ATTCCGGGGA", "EcoRI", circular=True)[0]
        self.assertEqual((hit["start"], hit["end_unwrapped"], hit["top_cut"], hit["bottom_cut"]), (8, 14, 9, 3))
        self.assertTrue(hit["wraps_origin"])
        self.assertEqual(hit["reference_overhang"], "AATT")
        self.assertEqual(biology.scan_restriction_sites("ATTCCGGGGA", "EcoRI"), ())

    def test_digest_actual_top_bottom_strands_hand_answer(self):
        result = biology.digest_sequence("CCGAATTCTT", ("EcoRI",))
        first, second = result["fragments"]
        self.assertEqual(result["cut_count"], 1)
        self.assertEqual((first["top_sequence"], first["bottom_sequence"], first["bottom_offset"]), ("CCG", "AATTCGG", 0))
        self.assertEqual((second["top_sequence"], second["bottom_sequence"], second["bottom_offset"]), ("AATTCTT", "AAG", 4))
        self.assertIsNone(first["left_end"])
        self.assertIsNone(second["right_end"])
        self.assertEqual(first["right_end"], {"kind": "5prime", "overhang": "AATT"})
        self.assertEqual(second["left_end"], {"kind": "5prime", "overhang": "AATT"})

    def test_digest_nonpalindromic_actual_extensions_and_threeprime(self):
        first, second = biology.digest_sequence("TTGGTCTCAAGTCCCGG", ("BsaI",))["fragments"]
        self.assertEqual(first["right_end"], {"kind": "5prime", "overhang": "GACT"})
        self.assertEqual(second["left_end"], {"kind": "5prime", "overhang": "AGTC"})
        first, second = biology.digest_sequence("AACTGCAGTT", ("PstI",))["fragments"]
        self.assertEqual((first["top_sequence"], first["bottom_sequence"]), ("AACTGCA", "GTT"))
        self.assertEqual((second["top_sequence"], second["bottom_sequence"], second["bottom_offset"]),
                         ("GTT", "AACTGCA", -4))

    def test_multienzyme_digest_and_no_cut(self):
        sequence = "AAAGAATTCCCCGGATCCTTT"
        result = biology.digest_sequence(sequence, ("EcoRI", "BamHI"))
        self.assertEqual(result["cut_count"], 2)
        self.assertEqual([fragment["top_interval"] for fragment in result["fragments"]], [[0, 4], [4, 13], [13, 21]])
        untouched = biology.digest_sequence("AAACCC", ("EcoRI",), circular=True)
        self.assertEqual(untouched["cut_count"], 0)
        self.assertEqual(untouched["fragments"][0]["topology"], "circular")
        self.assertIsNone(untouched["fragments"][0]["left_end"])


class AssemblyTests(unittest.TestCase):
    def test_actual_extensions_must_be_reverse_complements(self):
        self.assertTrue(biology.compatible_ends({"kind": "5prime", "overhang": "AGTC"}, {"kind": "5prime", "overhang": "GACT"}))
        self.assertFalse(biology.compatible_ends({"kind": "5prime", "overhang": "AGTC"}, {"kind": "5prime", "overhang": "AGTC"}))
        self.assertFalse(biology.compatible_ends(None, {"kind": "blunt", "overhang": ""}))
        self.assertFalse(biology.compatible_ends({"kind": "5prime", "overhang": "AGTC"}, {"kind": "3prime", "overhang": "GACT"}))
        self.assertTrue(biology.compatible_ends({"kind": "blunt", "overhang": ""}, {"kind": "blunt", "overhang": ""}))

    def test_linear_ligation_independent_original_sequence(self):
        for sequence, enzyme in [("CCGAATTCTT", "EcoRI"), ("AACTGCAGTT", "PstI"),
                                 ("CCGATATCGG", "EcoRV"), ("TTGGTCTCAAGTCCCGG", "BsaI")]:
            fragments = biology.digest_sequence(sequence, (enzyme,))["fragments"]
            original = copy.deepcopy(fragments)
            for fragment in fragments:
                self.assertIsNone(biology.validate_duplex(fragment))
            result = biology.ligate_fragments(fragments)
            self.assertEqual(result["top_sequence"], sequence)
            self.assertEqual(result["topology"], "linear")
            self.assertEqual(fragments, original)

    def test_circular_ligation_including_nonpalindromic_stagger(self):
        for sequence, enzyme, expected in [("CCGAATTCTT", "EcoRI", "AATTCTTCCG"),
                                           ("TTGGTCTCAAGTCCCGG", "BsaI", "AGTCCCGGTTGGTCTCA"),
                                           ("AACTGCAGTT", "PstI", "GTTAACTGCA")]:
            fragments = biology.digest_sequence(sequence, (enzyme,), circular=True)["fragments"]
            result = biology.ligate_fragments(fragments, circular=True)
            self.assertEqual(result, {"sequence": expected, "topology": "circular"})

    def test_tampered_end_labels_and_actual_strand_mismatch_fail(self):
        fragments = biology.digest_sequence("TTGGTCTCAAGTCCCGG", ("BsaI",))["fragments"]
        bad = copy.deepcopy(fragments)
        bad[0]["right_end"]["overhang"] = "AAAA"
        bad[1]["left_end"]["overhang"] = "TTTT"
        with self.assertRaisesRegex(ValueError, "actual strand"):
            biology.ligate_fragments(bad)
        bad = copy.deepcopy(fragments[1])
        bad["bottom_sequence"] = "AAAA"
        with self.assertRaises(ValueError):
            biology.validate_duplex(bad)
        with self.assertRaisesRegex(ValueError, "unknown"):
            biology.ligate_fragments(fragments, circular=True)

    def test_gibson_hand_linear_and_circular_products(self):
        result = biology.gibson_assemble(("AAACCC", "CCCATGGG", "GGGTTT"), (3, 3))
        self.assertEqual(result["sequence"], "AAACCCATGGGTTT")
        self.assertEqual(result["topology"], "linear")
        result = biology.gibson_assemble(("GGGAAACCC", "CCCTTTGGG"), (3, 3), circular=True)
        self.assertEqual(result["sequence"], "GGGAAACCCTTT")
        self.assertEqual(result["topology"], "circular")
        for sequences, overlaps in [(("AAACCC", "CCCTTT"), (4,)), (("AAACCC", "CCCGGG", "GGGTTT"), (3, 3))]:
            with self.assertRaises(ValueError):
                biology.gibson_assemble(sequences, overlaps)
        with self.assertRaises(ValueError):
            biology.gibson_assemble(("GGGAAACCC", "CCCTTTAAA"), (3, 3), circular=True)

    def test_inverse_pcr_intermediate_and_both_closure_models(self):
        result = biology.inverse_pcr_circularize("AAACCCTTTGGG", "ACTTT", "GGG", forward_core_length=3)
        self.assertEqual(result["sequence"], "ACTTTGGGAAACCC")
        self.assertEqual(result["intermediate"]["sequence"], "ACTTTGGGAAACCC")
        self.assertEqual(result["intermediate"]["topology"], "linear")
        overlap = biology.inverse_pcr_circularize(
            "AAACCCTTTGGG", "CCCTTT", "GGG", forward_core_length=3, closing_overlap=3,
        )
        self.assertEqual(overlap["intermediate"]["sequence"], "CCCTTTGGGAAACCC")
        self.assertEqual(overlap["sequence"], "CCCTTTGGGAAA")
        with self.assertRaises(ValueError):
            biology.inverse_pcr_circularize("AAACCCTTTGGG", "ACTTT", "GGG", forward_core_length=3, closing_overlap=2)

    def test_constructed_random_overlap_assemblies_100_cases(self):
        generator = random.Random(198211)
        for _ in range(100):
            # Draw independent unique blocks and homology arms, then know product
            # before constructing fragments. No implementation constructs answers.
            a, b, c, left, right = ["".join(generator.choice("ACGT") for _ in range(width))
                                    for width in (11, 13, 17, 4, 5)]
            expected = a + left + b + right + c
            result = biology.gibson_assemble((a + left, left + b + right, right + c), (4, 5))
            self.assertEqual(result["sequence"], expected)


if __name__ == "__main__":
    unittest.main()
