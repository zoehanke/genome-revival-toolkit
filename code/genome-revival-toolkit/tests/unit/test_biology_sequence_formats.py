"""Independent answers: literal format records and hand-labelled coordinates."""
import copy
import random
import struct
import unittest

from Bio.Seq import Seq
from Bio.SeqFeature import CompoundLocation, SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord

from dna_design_core.biology import public as biology


GENBANK = """LOCUS       synthetic                 12 bp    DNA     circular SYN 01-JAN-2000
DEFINITION  Constructed test record.
ACCESSION   synthetic
VERSION     synthetic
KEYWORDS    .
SOURCE      synthetic DNA
  ORGANISM  synthetic DNA
            other sequences; artificial sequences.
FEATURES             Location/Qualifiers
     misc_feature    join(10..12,1..3)
                     /label="origin_feature"
                     /note="constructed"
     gene            complement(4..9)
                     /gene="synthetic_gene"
ORIGIN
        1 aaaccctttggg
//
"""


def synthetic_record(sequence="AAACCCTTTGGG", topology="circular"):
    return SeqRecord(Seq(sequence), id="synthetic", name="synthetic",
                     description="synthetic", annotations={"molecule_type": "DNA", "topology": topology})


class SequenceTests(unittest.TestCase):
    def test_normalization_is_strict(self):
        self.assertEqual(biology.normalize_dna("acgt"), "ACGT")
        self.assertEqual(biology.normalize_dna("aRYn", ambiguous=True), "ARYN")
        for value in ("A C", "AU", "N", "", "AC\n"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                biology.normalize_dna(value)
        with self.assertRaises(TypeError):
            biology.normalize_dna(123)

    def test_hand_interval_segments(self):
        self.assertEqual(biology.interval_segments(8, 2, 10, circular=True), ((8, 10), (0, 2)))
        self.assertEqual(biology.interval_segments(0, 10, 10), ((0, 10),))
        self.assertEqual(biology.interval_segments(3, 3, 10, circular=True, whole=True), ((3, 10), (0, 3)))
        self.assertEqual(biology.interval_segments(0, 0, 10, circular=True, whole=True), ((0, 10),))
        for args, options in [((8, 2, 10), {}), ((3, 3, 10), {}), ((3, 3, 10), {"circular": True}),
                              ((-1, 3, 10), {}), ((10, 2, 10), {"circular": True}), ((0, 1, 0), {})]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                biology.interval_segments(*args, **options)
        for coordinate in (True, "2", 2.0):
            with self.assertRaises(TypeError):
                biology.interval_segments(coordinate, 5, 10)

    def test_hand_sequence_extraction_both_strands(self):
        self.assertEqual(biology.slice_sequence("AAACCCTTTGGG", 9, 3, circular=True), "GGGAAA")
        self.assertEqual(biology.slice_sequence("AAACCCTTTGGG", 9, 3, circular=True, strand=-1), "TTTCCC")
        self.assertEqual(biology.slice_sequence("AAACCCTTTGGG", 3, 9), "CCCTTT")
        with self.assertRaises(ValueError):
            biology.slice_sequence("ACGT", 0, 4, strand=0)

    def test_feature_mapping_hand_forward_reverse_and_partial_cds(self):
        feature = SeqFeature(SimpleLocation(2, 10, strand=1), type="CDS",
                             qualifiers={"label": ["synthetic"], "translation": ["unused"], "codon_start": ["1"]})
        original = copy.deepcopy(feature)
        mapped = biology.map_feature(feature, ((4, 9),), source_length=12)
        self.assertEqual((int(mapped.location.start), int(mapped.location.end)), (0, 5))
        self.assertEqual(mapped.qualifiers["partial"], ["true"])
        self.assertNotIn("translation", mapped.qualifiers)
        self.assertEqual(mapped.qualifiers["codon_start"], ["2"])
        self.assertEqual(feature, original)
        feature.location = SimpleLocation(2, 10, strand=-1)
        mapped = biology.map_feature(feature, ((4, 9),), source_length=12)
        self.assertEqual(mapped.qualifiers["codon_start"], ["3"])
        self.assertEqual(mapped.location.strand, -1)
        self.assertIsNone(biology.map_feature(feature, ((10, 12),), source_length=12))

    def test_slice_record_retains_biological_order_and_qualifiers(self):
        record = biology.read_genbank(GENBANK)
        fragment = biology.slice_record(record, 9, 3)
        self.assertEqual(str(fragment.seq), "GGGAAA")
        self.assertEqual(str(fragment.features[0].extract(fragment.seq)), "GGGAAA")
        self.assertEqual(fragment.features[0].qualifiers["note"], ["constructed"])
        self.assertEqual(fragment.annotations["topology"], "linear")
        reverse = biology.slice_record(record, 3, 9, strand=-1)
        self.assertEqual(str(reverse.seq), "AAAGGG")
        self.assertEqual(reverse.features[0].location.strand, 1)
        unknown = synthetic_record()
        unknown.annotations.pop("topology")
        with self.assertRaises(ValueError):
            biology.slice_record(unknown, 0, 4)

    def test_feature_interrupted_at_new_linear_ends(self):
        record = synthetic_record()
        record.features = [SeqFeature(SimpleLocation(2, 9, strand=1), type="primer_bind",
                                      qualifiers={"label": ["intact_in_source"]})]
        fragment = biology.slice_record(record, 6, 6, whole=True)
        self.assertEqual(fragment.features[0].type, "misc_feature")
        self.assertEqual(fragment.features[0].qualifiers["partial"], ["true"])
        rotated = biology.rotate_record(record, 6)
        self.assertEqual(rotated.features[0].type, "primer_bind")
        self.assertNotIn("partial", rotated.features[0].qualifiers)

    def test_rotation_of_compound_reverse_feature(self):
        record = synthetic_record()
        record.features = [SeqFeature(CompoundLocation([
            SimpleLocation(0, 3, strand=-1), SimpleLocation(9, 12, strand=-1),
        ]), type="gene", qualifiers={"label": ["reverse_across_origin"]})]
        rotated = biology.rotate_record(record, 2)
        self.assertEqual(str(rotated.seq), "ACCCTTTGGGAA")
        self.assertEqual(str(rotated.features[0].extract(rotated.seq)), "TTTCCC")
        self.assertEqual(str(record.seq), "AAACCCTTTGGG")
        with self.assertRaises(ValueError):
            biology.rotate_record(synthetic_record(topology="linear"), 1)

    def test_fixed_seed_properties_200_cases(self):
        generator = random.Random(486103)
        for _ in range(200):
            sequence = "".join(generator.choice("ACGT") for _ in range(generator.randrange(8, 90)))
            origin = generator.randrange(len(sequence))
            record = synthetic_record(sequence)
            record.features = [SeqFeature(SimpleLocation(2, len(sequence) - 1, strand=-1), type="gene")]
            rotated = biology.rotate_record(record, origin)
            restored = biology.rotate_record(rotated, (-origin) % len(sequence))
            self.assertEqual(str(restored.seq), sequence)
            self.assertEqual(str(rotated.features[0].extract(rotated.seq)), str(record.features[0].extract(record.seq)))
            # Every cyclic k-mer occurs with the same multiplicity after rotation.
            for width in (1, 3):
                expected = sorted((sequence + sequence)[index:index + width] for index in range(len(sequence)))
                actual = str(rotated.seq)
                self.assertEqual(sorted((actual + actual)[index:index + width] for index in range(len(actual))), expected)
            reverse = biology.slice_sequence(sequence, 0, len(sequence), strand=-1)
            self.assertEqual(biology.slice_sequence(reverse, 0, len(reverse), strand=-1), sequence)


class FormatTests(unittest.TestCase):
    def test_genbank_independent_literal_answer_and_roundtrip(self):
        record = biology.read_genbank(GENBANK)
        self.assertEqual(str(record.seq), "AAACCCTTTGGG")
        self.assertEqual(record.annotations["topology"], "circular")
        self.assertEqual([(int(part.start), int(part.end), part.strand) for part in record.features[0].location.parts],
                         [(9, 12, 1), (0, 3, 1)])
        self.assertEqual(str(record.features[1].extract(record.seq)), "AAAGGG")
        expected = {"sequence": "AAACCCTTTGGG", "topology": "circular", "molecule_type": "DNA",
                    "features": [
                        {"type": "misc_feature", "location": "join{[9:12](+), [0:3](+)}",
                         "qualifiers": {"label": ["origin_feature"], "note": ["constructed"]}},
                        {"type": "gene", "location": "[3:9](-)", "qualifiers": {"gene": ["synthetic_gene"]}},
                    ]}
        self.assertEqual(biology.record_projection(record), expected)
        serialized = biology.write_genbank(record)
        self.assertEqual(biology.record_projection(biology.read_genbank(serialized)), expected)
        with self.assertRaises(ValueError):
            biology.read_genbank(GENBANK.replace("//", ""))
        with self.assertRaises(ValueError):
            biology.read_genbank(GENBANK + GENBANK)

    def test_genbank_fuzzy_positions_roundtrip_but_transform_rejected(self):
        record = biology.read_genbank(GENBANK.replace("complement(4..9)", "complement(<4..>9)"))
        serialized = biology.write_genbank(record)
        self.assertIn("complement(<4..>9)", serialized)
        with self.assertRaises(ValueError):
            biology.rotate_record(record, 2)

    def test_fasta_header_sequence_roundtrip_unknown_topology(self):
        record = biology.read_fasta(">synthetic Constructed sequence\nacgtn\nTTAA\n")
        self.assertEqual(record.id, "synthetic")
        self.assertEqual(record.description, "synthetic Constructed sequence")
        self.assertEqual(str(record.seq), "ACGTNTTAA")
        self.assertNotIn("topology", record.annotations)
        self.assertEqual(biology.write_fasta(record), ">synthetic Constructed sequence\nACGTNTTAA\n")
        with self.assertRaises(ValueError):
            biology.write_fasta(synthetic_record())
        with self.assertRaises(ValueError):
            biology.read_fasta(">one\nACGT\n>two\nGGCC\n")
        with self.assertRaises(ValueError):
            biology.read_fasta(">bad\nACGU\n")

    def test_native_binary_constructed_packet_answer(self):
        def packet(kind, data):
            return bytes([kind]) + struct.pack(">I", len(data)) + data
        # Packet layout independently built from installed parser's documented TLV.
        cookie = packet(9, struct.pack(">8sHHH", b"SnapGene", 1, 1, 1))
        sequence = packet(0, b"\x01AAACCCTTTGGG")
        feature = packet(10, b'<Features><Feature name="constructed" type="gene" directionality="1">'
                             b'<Segment range="10-3" type="standard"/></Feature></Features>')
        record = biology.read_dna(cookie + sequence + feature)
        self.assertEqual(str(record.seq), "AAACCCTTTGGG")
        self.assertEqual(record.annotations["topology"], "circular")
        self.assertEqual(str(record.features[0].extract(record.seq)), "GGGAAA")
        self.assertEqual(record.features[0].qualifiers["label"], ["constructed"])
        with self.assertRaises(ValueError):
            biology.read_dna(cookie + sequence[:-2])
        with self.assertRaises(TypeError):
            biology.read_dna("not bytes")


if __name__ == "__main__":
    unittest.main()
