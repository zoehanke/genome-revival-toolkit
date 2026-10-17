"""S2b constructed marker names, host context and source boundaries."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from cut_plasmid_runtime import KIT, retained, run_case
from dna_design_core.kernel.public import require_schema
from e2e.test_cut_plasmid_selection import YEAST, ZEOCIN_PLATE


class CutPlasmidSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def selection(self, label, genotype=None):
        # Hand-constructed complete CDS: ATG, AAA, TAA; no functional claim.
        case = {"vector": {"sequence": "ATGAAATAACCC", "topology": "circular",
                           "features": [{"start": 0, "end": 9, "type": "CDS", "label": label, "strand": 1}]},
                "target": {"sequence": "ACGT", "topology": "linear", "features": []}}
        service, result = run_case(self.directory / str(len(list(self.directory.iterdir()))), case=case,
                                  operation="assess_selection", parameters={"strain_genotype": genotype or YEAST})
        self.assertEqual(result["state"], "COMPLETED", result)
        return retained(service)["documents"]["selection"]

    def test_ble_aliases_match_real_annotations_case_insensitively(self):
        for label in ("ble", "bler", "BleoR", "Sh ble", "ble marker", "ZeOcIn", "phleomycin", "BLEOMYCIN"):
            with self.subTest(label=label):
                report = self.selection(label)
                self.assertEqual(report["status"], "DECLARED_COMPATIBLE")
                self.assertEqual([marker["marker_id"] for marker in report["markers"]], ["ble"])
                self.assertEqual(report["markers"][0]["plate_options"][0]["plate"], ZEOCIN_PLATE)

    def test_common_words_do_not_match_ble(self):
        for label in ("stable", "table", "cable", "able", "bleach"):
            with self.subTest(label=label):
                report = self.selection(label)
                self.assertEqual(report["status"], "UNKNOWN")
                self.assertEqual(report["markers"], [])

    def test_ble_conflicts_with_recipient_ble_and_is_not_applicable_to_ecoli(self):
        report = self.selection("BleoR", {**YEAST, "existing_markers": ["Sh ble"]})
        self.assertEqual(report["status"], "CONFLICT")
        self.assertEqual(report["markers"][0]["compatibility"], "CONFLICT")
        report = self.selection("BleoR", {"organism": "E. coli", "existing_markers": []})
        self.assertEqual(report["status"], "UNKNOWN")
        self.assertEqual(report["markers"][0]["compatibility"], "NOT_APPLICABLE")
        self.assertEqual(report["markers"][0]["plate_options"], [])

    def test_new_rule_and_both_sources_remain_unverified_with_separate_scopes(self):
        pack = json.loads((KIT / "knowledge/selection_markers.json").read_text(encoding="utf-8"))
        rows = pack["parameters"]["rows"]
        self.assertEqual(len(rows), 11)
        self.assertEqual(len({row["id"] for row in rows}), 11)
        rule = next(row for row in rows if row["id"] == "selection.ble.yeast")
        require_schema("rule-v1", rule)
        self.assertEqual(rule["parameters"]["marker_id"], "ble")
        self.assertEqual(rule["parameters"]["host"], "yeast")
        self.assertIsNone(rule["parameters"]["auxotrophy"])
        self.assertEqual(rule["parameters"]["plate"], ZEOCIN_PLATE)
        primary = rule["source"]
        self.assertEqual(primary["source_class"], "official_method")
        self.assertIn("25-0078", primary["citation"])
        self.assertIn("Version J", primary["citation"])
        self.assertIn("2002-08-22", primary["citation"])
        self.assertIn("50–300 µg/mL", " ".join(primary["supports"]))
        supplement, = rule["parameters"]["supplementary_sources"]
        self.assertEqual(supplement["source_class"], "literature")
        self.assertIn("10.1093/nar/18.13.4009", supplement["citation"])
        self.assertIn("1695734", supplement["citation"])
        self.assertIn("PMC331125", supplement["citation"])
        self.assertIn("Specific Zeocin concentrations", " ".join(supplement["does_not_support"]))
        self.assertNotIn("50", " ".join(supplement["supports"]))
        for source in (primary, supplement):
            with self.subTest(source=source["source_class"]):
                sourced_rule = deepcopy(rule)
                sourced_rule["source"] = source
                require_schema("rule-v1", sourced_rule)
                self.assertEqual(source["retrieved_at"], "2026-10-17")
                self.assertEqual(source["verification_status"], "unverified")
                self.assertNotIn("verification_receipt", source)
                self.assertIsNone(source["content_ref"])
        self.assertFalse((KIT / rule["review"]).exists())


if __name__ == "__main__":
    unittest.main()
