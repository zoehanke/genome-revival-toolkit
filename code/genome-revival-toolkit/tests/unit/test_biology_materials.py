"""Material answers use literal coordinates, strand geometry and D9 kernel hashes."""
import copy
import unittest

from Bio.Seq import Seq
from Bio.SeqFeature import CompoundLocation, SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord

from dna_design_core.biology import public as biology
from dna_design_core.kernel import ids


class MaterialTests(unittest.TestCase):
    def test_make_material_unknowns_and_content_identity(self):
        value = biology.make_material("acgtacga")
        self.assertEqual(value, {"sequence": "ACGTACGA", "topology": None, "strandedness": None, "ends": None, "features": []})
        self.assertEqual(ids.material_id(value), ids.material_id({**value, "name": "decoration"}))
        with self.assertRaises(ValueError):
            biology.make_material("ACGT", topology="circular", strandedness="double", ends={"left": None, "right": None})

    def test_material_record_compound_feature_biological_order(self):
        record = SeqRecord(Seq("AAACCCTTTGGG"), annotations={"molecule_type": "DNA", "topology": "circular"})
        record.features = [SeqFeature(CompoundLocation([SimpleLocation(9, 12, strand=1), SimpleLocation(0, 3, strand=1)]),
                                     type="gene", qualifiers={"label": ["origin"], "note": ["literal note"]})]
        value = biology.material_from_record(record, strandedness="double")
        self.assertEqual(value["features"][0]["parts"], [{"start": 9, "end": 12, "strand": 1}, {"start": 0, "end": 3, "strand": 1}])
        restored = biology.record_from_material(value)
        self.assertEqual(str(restored.features[0].extract(restored.seq)), "GGGAAA")
        self.assertEqual(restored.features[0].qualifiers["note"], ["literal note"])

    def test_duplex_conversion_nonpalindromic_end_geometry(self):
        ends = {"left": {"kind": "5prime", "overhang": "AGTC"}, "right": {"kind": "5prime", "overhang": "GACT"}}
        value = biology.make_material("AGTCCCGG", topology="linear", strandedness="double", ends=ends)
        duplex = biology.material_to_duplex(value)
        self.assertEqual(duplex["top_sequence"], "AGTCCCGG")
        self.assertEqual(duplex["bottom_sequence"], "GACTCCGG")
        self.assertEqual(duplex["bottom_offset"], 4)
        self.assertEqual(biology.material_from_duplex(duplex), value)
        bad = copy.deepcopy(duplex)
        bad["left_end"]["overhang"] = "AAAA"
        with self.assertRaises(ValueError):
            biology.material_from_duplex(bad)

    def test_genbank_material_identity_roundtrip_and_tamper(self):
        value = biology.make_material("AAACCCTTTGGG", topology="linear", strandedness="double",
            ends={"left": {"kind": "blunt", "overhang": ""}, "right": {"kind": "blunt", "overhang": ""}},
            features=[{"start": 0, "end": 3, "type": "gene", "label": "synthetic", "strand": 1}])
        text = biology.material_to_genbank(value)
        self.assertEqual(biology.material_from_genbank(text), value)
        self.assertEqual(ids.material_id(biology.material_from_genbank(text)), ids.material_id(value))
        header, separator, body = text.partition("ORIGIN\n")
        self.assertTrue(separator)
        prefix, last_g, suffix = body.rpartition("g")
        self.assertEqual(last_g, "g")
        with self.assertRaises(ValueError):
            biology.material_from_genbank(header + separator + prefix + "a" + suffix)

    def test_fasta_material_subset_only(self):
        unknown = biology.make_material("ACGTACGA")
        self.assertEqual(biology.material_to_fasta(unknown), ">material\nACGTACGA\n")
        with self.assertRaises(ValueError):
            biology.material_to_fasta({**unknown, "topology": "linear"})

    def test_material_slice_and_rotation_follow_D9(self):
        source = biology.make_material("AAACCCTTTGGG", topology="circular", strandedness="double")
        self.assertEqual(biology.slice_material(source, 9, 3)["sequence"], "GGGAAA")
        rotated = biology.rotate_material(source, 2)
        self.assertEqual(rotated["sequence"], "ACCCTTTGGGAA")
        self.assertNotEqual(ids.material_id(source), ids.material_id(rotated))
        self.assertEqual(ids.material_id(source), ids.material_id(biology.rotate_material(source, 0)))

    def test_pcr_material_retains_blunt_intermediate(self):
        template = biology.make_material("ACGTAACCGGTTGATC", topology="linear", strandedness="double")
        forward = biology.make_material("TTACGTA", strandedness="single")
        reverse = biology.make_material("GCGATC", strandedness="single")
        product, _ = biology.pcr_material(template, forward, reverse, forward_core_length=5, reverse_core_length=4)
        self.assertEqual(product["sequence"], "TTACGTAACCGGTTGATCGC")
        self.assertEqual(product["ends"], {"left": {"kind": "blunt", "overhang": ""}, "right": {"kind": "blunt", "overhang": ""}})

    def test_digest_and_ligate_material_exact_known_circle(self):
        source = biology.make_material("TTGGTCTCAAGTCCCGG", topology="circular", strandedness="double")
        products, report = biology.digest_material(source, ["BsaI"])
        self.assertEqual(report["cut_count"], 1)
        self.assertEqual(products[0]["sequence"], "AGTCCCGGTTGGTCTCA")
        self.assertEqual(products[0]["ends"]["left"], {"kind": "5prime", "overhang": "AGTC"})
        self.assertEqual(products[0]["ends"]["right"], {"kind": "5prime", "overhang": "GACT"})
        closed = biology.ligate_material(products[0], circular=True)
        self.assertEqual(closed["sequence"], "AGTCCCGGTTGGTCTCA")
        self.assertEqual((closed["topology"], closed["ends"]), ("circular", None))

    def test_gibson_material_preconstructed_answer(self):
        left = biology.make_material("AAACCC", topology="linear", strandedness="double")
        right = biology.make_material("CCCTTT", topology="linear", strandedness="double")
        self.assertEqual(biology.gibson_material(left, right, 3)["sequence"], "AAACCCTTT")

    def test_inverse_pcr_material_retains_both_topologies(self):
        template = biology.make_material("AAACCCTTTGGG", topology="circular", strandedness="double")
        forward = biology.make_material("ACTTT", strandedness="single")
        reverse = biology.make_material("GGG", strandedness="single")
        product, intermediate, _ = biology.inverse_pcr_material(template, forward, reverse, forward_core_length=3)
        self.assertEqual(product["sequence"], "ACTTTGGGAAACCC")
        self.assertEqual(intermediate["sequence"], "ACTTTGGGAAACCC")
        self.assertEqual((product["topology"], intermediate["topology"]), ("circular", "linear"))


if __name__ == "__main__":
    unittest.main()
