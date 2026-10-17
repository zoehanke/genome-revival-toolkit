"""Independent literal constructions for Genome Identity; no legacy output oracle."""
from copy import deepcopy
import importlib.util
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from dna_design_core.kernel.public import ToolkitError, require_schema
from tests.fixtures.gen.genome_identity import build, material
from tests.oracles.genome_identity import check

ROOT = Path(__file__).resolve().parents[2]
OPERATIONS_PATH = ROOT / "kits/genome-identity/capabilities/operations.py"


def operations(path=None):
    spec = importlib.util.spec_from_file_location("s5b_unit", path or OPERATIONS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenomeIdentityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="s5b_unit_")
        self.addCleanup(self.directory.cleanup)
        self.module = operations()
        self.case = build(self.directory.name)

    def analyze(self, case=None, *, handoff=True, **updates):
        case = case or self.case
        args = {"reference_original": case["materials"]["original"],
                "reference_edited": case["materials"]["edited"],
                "forward": case["materials"]["forward"], "reverse": case["materials"]["reverse"],
                "reference_original_file": case["paths"]["original"],
                "reference_edited_file": case["paths"]["edited"],
                "assay_id": "synthetic_identity", "forward_id": "forward", "reverse_id": "reverse"}
        if handoff:
            args["handoff"] = case["handoff"] if handoff is True else handoff
        args.update(updates)
        return self.module.analyze_assay(None, **args)

    def assert_case(self, name):
        case = build(Path(self.directory.name) / name, name)
        before = deepcopy(case)
        outcome = self.analyze(case)
        self.assertEqual(outcome.documents["expected_results"], case["expected"])
        self.assertEqual(case, before)
        require_schema(self.module.EXPECTED_SCHEMA, outcome.documents["expected_results"])
        actual_path = Path(self.directory.name) / (name + "-actual.json")
        actual_path.write_text(json.dumps(outcome.documents["expected_results"]), encoding="utf-8")
        circle = case["materials"]["original"]["topology"] == "circular"
        check(case["paths"]["original"], case["paths"]["edited"], case["paths"]["forward"],
              case["paths"]["reverse"], actual_path, handoff=Path(self.directory.name) / name / "identity-handoff.json",
              circular_original=circle, circular_edited=circle)

    def test_different_sizes(self):
        self.assert_case("different_sizes")

    def test_same_sizes(self):
        self.assert_case("same_sizes")

    def test_multiple_sites(self):
        self.assert_case("multiple_sites")

    def test_circular_origin(self):
        self.assert_case("circular_origin")

    def test_reverse_orientation(self):
        self.assert_case("reverse_orientation")

    def test_no_product(self):
        self.assert_case("no_product")

    def test_both_absent(self):
        self.assert_case("both_absent")

    def test_without_handoff_uses_actual_hashes_and_fixed_port_ids(self):
        expected = deepcopy(self.case["expected"])
        for row, role in zip(expected["backgrounds"], ("original", "edited")):
            row["id"] = "reference_" + role
        self.assertEqual(self.analyze(handoff=False).documents["expected_results"], expected)

    def test_handoff_hash_mismatch_is_failure(self):
        handoff = deepcopy(self.case["handoff"])
        handoff["references"][0]["sha256"] = "0" * 64
        with self.assertRaises(ToolkitError) as caught:
            self.analyze(handoff=handoff)
        self.assertEqual(caught.exception.problem.code, "SOURCE_CHANGED")

    def test_same_sequence_with_changed_file_header_fails_handoff_hash(self):
        path = self.case["paths"]["original"]
        path.write_text(path.read_text().replace("synthetic_original", "changed_header"), encoding="utf-8")
        with self.assertRaises(ToolkitError) as caught:
            self.analyze()
        self.assertEqual(caught.exception.problem.code, "SOURCE_CHANGED")

    def test_material_cannot_be_substituted_under_a_valid_file_hash(self):
        with self.assertRaises(ToolkitError) as caught:
            self.analyze(reference_original=self.case["materials"]["edited"])
        self.assertEqual(caught.exception.problem.code, "SOURCE_CHANGED")

    def test_swapping_files_cannot_bypass_material_binding(self):
        with self.assertRaises(ToolkitError) as caught:
            self.analyze(reference_original_file=self.case["paths"]["edited"])
        self.assertEqual(caught.exception.problem.code, "SOURCE_CHANGED")

    def test_primer_id_and_sequence_must_match_handoff(self):
        with self.assertRaises(ToolkitError):
            self.analyze(forward=self.case["materials"]["reverse"])

    def test_unknown_topology_and_degenerate_reference_do_not_become_no_product(self):
        for field, value in (("topology", None), ("sequence", "N" * 1000)):
            invalid = deepcopy(self.case["materials"]["original"])
            invalid[field] = value
            with self.subTest(field=field), self.assertRaises(ToolkitError):
                self.analyze(reference_original=invalid)

    def test_unknown_or_double_stranded_primer_is_rejected(self):
        primer = deepcopy(self.case["materials"]["forward"])
        primer["strandedness"] = "double"
        with self.assertRaises(ToolkitError):
            self.analyze(forward=primer)

    def test_semantic_handoff_failures(self):
        for change in (lambda h: h["references"][1].update(role="original"),
                       lambda h: h["references"][1].update(id="original"),
                       lambda h: h["regions"][0].update(reference_id="missing"),
                       lambda h: h["regions"][0].update(end=1001),
                       lambda h: h["regions"][0].update(start=1000),
                       lambda h: h["primers"][1].update(id="forward")):
            handoff = deepcopy(self.case["handoff"])
            change(handoff)
            args = deepcopy(self.case)
            args["handoff"] = handoff
            with self.subTest(handoff=handoff), self.assertRaises(ToolkitError):
                self.analyze(args)

    def test_read_handoff_and_legacy_shape_refusal(self):
        path = Path(self.directory.name) / "identity-handoff.json"
        result = self.module.read_handoff(None, path)
        self.assertEqual(result.documents["handoff"], self.case["handoff"])
        path.write_text(json.dumps({"schema_version": "construct-identity-handoff-v1", "assays": []}), encoding="utf-8")
        with self.assertRaises(ToolkitError):
            self.module.read_handoff(None, path)

    def test_compare_regions_hand_distances(self):
        # Manual unit costs: equal=0; substitution=1; insertion=1; deletion=1; transposition=2.
        for left, right, distance in (("ACGT", "ACGT", 0), ("ACGT", "ATGT", 1),
                                      ("ACGT", "ACGGT", 1), ("ACGT", "ACT", 1),
                                      ("ACGT", "AGCT", 2)):
            with self.subTest(left=left, right=right):
                value = self.module.compare_regions(None, material(left), material(right)).documents["comparison"]
                self.assertEqual(value["edit_distance"], distance)
                self.assertEqual(value["identical"], distance == 0)

    def test_explicit_intervals_and_out_of_bounds(self):
        left, right = material("TTACGTAA"), material("GGACGTCC")
        value = self.module.compare_regions(None, left, right, 2, 6, 2, 6).documents["comparison"]
        self.assertEqual(value["edit_distance"], 0)
        for start, end in ((6, 2), (0, 9), (2, 2)):
            with self.assertRaises(ToolkitError):
                self.module.compare_regions(None, left, right, start, end)

    def test_limitations_remain_in_unverified(self):
        limitations = " ".join(self.analyze().unverified)
        for text in ("Annealing temperature", "Whole-genome specificity", "NOT_PERFORMED"):
            self.assertIn(text, limitations)

    def test_exported_declarations_match_decorators_and_typed_signatures(self):
        for name in ("read_handoff", "compare_regions", "analyze_assay"):
            function = getattr(self.module, name)
            declaration = function.declaration
            path = ROOT / "kits/genome-identity/capabilities" / (name + ".json")
            self.assertEqual(json.loads(path.read_text()), declaration)
            require_schema("capability-v1", declaration)
            signature = inspect.signature(function)
            self.assertEqual(set(signature.parameters) - {"ctx"},
                             {p["name"] for p in declaration["inputs"]} | set(declaration["params"]["properties"]))
            for parameter in signature.parameters.values():
                self.assertIsNot(parameter.annotation, inspect.Parameter.empty)

    def test_expected_schema_refuses_no_product_encoded_as_ambiguous(self):
        wrong = deepcopy(self.case["expected"])
        wrong["backgrounds"][0]["expected"].update(product_count=1, product_bp=None)
        with self.assertRaises(ToolkitError):
            require_schema(self.module.EXPECTED_SCHEMA, wrong)

    def test_independent_oracle_rejects_a_false_size(self):
        wrong = deepcopy(self.case["expected"])
        wrong["backgrounds"][1]["expected"]["product_bp"] = 1299
        path = Path(self.directory.name) / "wrong-expected.json"
        path.write_text(json.dumps(wrong), encoding="utf-8")
        with self.assertRaises(AssertionError):
            check(self.case["paths"]["original"], self.case["paths"]["edited"],
                  self.case["paths"]["forward"], self.case["paths"]["reverse"], path,
                  handoff=Path(self.directory.name) / "identity-handoff.json")


if __name__ == "__main__":
    unittest.main()
