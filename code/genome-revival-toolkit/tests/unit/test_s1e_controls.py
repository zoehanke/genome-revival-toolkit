"""Only control-status error wording changes; allowed values come from the task."""
import json
from pathlib import Path
import tempfile
import unittest

from dna_design_core.kernel.public import ToolkitError
from tests.revival_support import load_kit


class ControlMessageTests(unittest.TestCase):
    def parse(self, **updates):
        module = load_kit()
        row = {"sample_id": "synthetic", "assay_id": "local", "background_id": "reference",
               "result": "positive", "observed_band_bp": 80, **updates}
        with tempfile.TemporaryDirectory(prefix="s1e_control_") as temporary:
            path = Path(temporary) / "observations.json"
            path.write_text(json.dumps({"observations": [], "genotype_results": [row]}), encoding="utf-8")
            return module.parse_observations(None, path).documents["document"]

    def test_all_three_existing_values_remain_accepted(self):
        for value in ("passed", "failed", "unknown"):
            with self.subTest(value=value):
                self.assertEqual(self.parse(control_status=value)["genotype_results"][0]["control_status"], value)

    def test_omission_still_defaults_to_unknown(self):
        self.assertEqual(self.parse()["genotype_results"][0]["control_status"], "unknown")

    def test_invalid_values_remain_rejected_and_list_choices(self):
        for value in (None, True, [], "pass"):
            with self.subTest(value=value), self.assertRaises(ToolkitError) as caught:
                self.parse(control_status=value)
            self.assertEqual(caught.exception.problem.code, "PLAN_PARAM_INVALID")
            for choice in ("passed", "failed", "unknown"):
                self.assertIn(choice, caught.exception.problem.message)

    def test_other_enum_errors_keep_generic_schema_message(self):
        with self.assertRaises(ToolkitError) as caught:
            self.parse(result="invalid")
        self.assertNotIn("control_status must be", caught.exception.problem.message)
        self.assertEqual(caught.exception.problem.details["findings"][0]["location"], "/genotype_results/0/result")


if __name__ == "__main__":
    unittest.main()
