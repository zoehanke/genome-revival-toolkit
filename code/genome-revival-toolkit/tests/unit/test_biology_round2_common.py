"""Independent hand/construction answers for the four non-CRISPR shared functions."""
import unittest
from dna_design_core.biology import public as biology


class Round2CommonTests(unittest.TestCase):
    def test_region_edit_sequence_and_annotation_retirement(self):
        plain = biology.make_material("AAACCCGGGTTT", topology="linear", strandedness="double")
        replacement = biology.make_material("AT", topology="linear", strandedness="double")
        plain_product, _ = biology.replace_material_region(plain, 3, 6, replacement)
        self.assertEqual(plain_product["sequence"], "AAAATGGGTTT")
        source = biology.make_material("AAACCCGGGTTT", topology="linear", strandedness="double", features=[
            {"start": 0, "end": 3, "type": "gene", "label": "left", "strand": 1},
            {"start": 3, "end": 6, "type": "CDS", "label": "replaced", "strand": 1},
            {"start": 9, "end": 12, "type": "gene", "label": "right", "strand": 1}])
        insert = biology.make_material("AT", topology="linear", strandedness="double")
        product, report = biology.replace_material_region(source, 3, 6, insert)
        self.assertEqual(product["sequence"], "AAAATGGGTTT")
        self.assertEqual([(feature["label"], feature["start"], feature["end"]) for feature in product["features"]],
                         [("left", 0, 3), ("right", 8, 11)])
        self.assertEqual(report["retired_features"][0]["type"], "CDS")
        self.assertEqual(source["sequence"], "AAACCCGGGTTT")
        deletion, _ = biology.replace_material_region(source, 3, 6)
        self.assertEqual(deletion["sequence"], "AAAGGGTTT")
        with self.assertRaises(ValueError):
            biology.replace_material_region(source, 9, 2, insert)

    def test_cds_hand_translation_frame_and_partial_unknown(self):
        valid = biology.inspect_cds("ATGAAATAA", 1)
        self.assertTrue(valid["complete_cds_consistent"])
        self.assertEqual(valid["translation"], "MK")
        self.assertEqual(valid["internal_stop_count"], 0)
        self.assertFalse(biology.inspect_cds("ATGTAATAA", 1)["complete_cds_consistent"])
        self.assertEqual(biology.inspect_cds("ATGTAATAA", 1)["internal_stop_count"], 1)
        self.assertEqual(biology.inspect_cds("AATGAAATAA", 1, codon_start=2)["translation"], "MK")
        self.assertIsNone(biology.inspect_cds("ATGNNNTAA", 1)["complete_cds_consistent"])
        self.assertIsNone(biology.inspect_cds("ATGAAA", 1, partial=True)["complete_cds_consistent"])

    def test_primer_candidates_core_tail_and_reverse_anchor(self):
        parameters = biology.TmParameters()
        forward = biology.enumerate_primer_candidates("AAACCCTTTGGG", 0, 1, [3, 4], circular=False,
                                                     parameters=parameters, tail_5prime="GC")
        self.assertEqual([row["binding_core"] for row in forward["candidates"]], ["AAA", "AAAC"])
        self.assertEqual([row["full_sequence"] for row in forward["candidates"]], ["GCAAA", "GCAAAC"])
        self.assertEqual(forward["candidates"][0]["quality"]["length"], 5)
        self.assertEqual(forward["candidates"][0]["tm"]["length"], 3)
        reverse = biology.enumerate_primer_candidates("AAACCCTTTGGG", 6, -1, [3], circular=False, parameters=parameters)
        self.assertEqual(reverse["candidates"][0]["binding_core"], "GGG")
        circular = biology.enumerate_primer_candidates("AAACCCTTTGGG", 10, 1, [4], circular=True, parameters=parameters)
        self.assertEqual(circular["candidates"][0]["binding_core"], "GGAA")

    def test_coverage_first_usable_base_is_after_primer_plus_trim(self):
        result = biology.sequencing_read_coverage("AAACCCTTTGGG", ["AAAC"], circular=False, read_length=4, trim=1)
        self.assertEqual(result["forward_positions"], [5, 6, 7])
        self.assertEqual(result["combined_gaps"], [[0, 5], [8, 12]])
        reverse = biology.sequencing_read_coverage("AAACCCTTTGGG", ["AAAG"], circular=False, read_length=3, trim=1)
        self.assertEqual(reverse["reverse_positions"], [2, 3])
        circle = biology.sequencing_read_coverage("AAACCCTTTGGG", ["TGGG"], circular=True, read_length=3, trim=0)
        self.assertEqual(circle["forward_positions"], [0, 1, 2])
        ambiguous = biology.sequencing_read_coverage("ACGTAAAACGT", ["ACGT"], circular=False, read_length=4, trim=0)
        self.assertFalse(ambiguous["all_primers_unique"])
        self.assertEqual(ambiguous["forward_positions"], [])


if __name__ == "__main__":
    unittest.main()
