"""Rehearsal validation must expose actual failures and injected violations."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.validate_kit_drafts import validate_tree


class KitDraftValidationTests(unittest.TestCase):
    def test_known_rehearsal_failures_are_preserved(self):
        report = validate_tree(ROOT / "docs/kit-prep")
        self.assertEqual(report["draft_documents"], 58)
        self.assertEqual((report["schema_invalid_documents"], report["a14_invalid_documents"]), (3, 1))
        self.assertEqual(report["question_ids"], ["K1", "K2", "K3", "K4", "K5", "K6"])
        invalid = next(row for row in report["records"] if row["file"].endswith("probes/source-missing.json"))
        self.assertIn("'source_class' is a required property", [error["message"] for error in invalid["schema_errors"]])
        self.assertFalse(list((ROOT / "docs/kit-prep/drafts").rglob("*.py")))

    def test_injected_capability_field_is_not_hidden_by_expected_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "prep"
            shutil.copytree(ROOT / "docs/kit-prep/drafts", target / "drafts")
            shutil.copy2(ROOT / "docs/kit-prep/rehearsal-index.json", target / "rehearsal-index.json")
            path = target / "drafts/cut-plasmid/capabilities/inspect_guide.json"
            value = json.loads(path.read_text())
            value["unapproved_field"] = True
            path.write_text(json.dumps(value), encoding="utf-8")
            report = validate_tree(target)
            row = next(item for item in report["records"] if item["file"].endswith("capabilities/inspect_guide.json"))
            self.assertFalse(row["valid"])
            self.assertTrue(any("unapproved_field" in error["message"] for error in row["schema_errors"]))
            self.assertEqual(report["schema_invalid_documents"], 4)

    def test_sources_and_shared_need_counts_have_distinct_meanings(self):
        audit = json.loads((ROOT / "docs/kit-prep/source-audit.json").read_text())
        self.assertEqual((audit["legacy_total"], audit["legacy_source_present"]), (24, 24))
        self.assertEqual(audit["legacy_source_missing"], [])
        matrix = json.loads((ROOT / "docs/kit-prep/shared-needs.json").read_text())["implemented_shared"]
        self.assertEqual(len(matrix), 4)
        self.assertTrue(all(len(set(kits)) >= 2 for kits in matrix.values()))


if __name__ == "__main__":
    unittest.main()
