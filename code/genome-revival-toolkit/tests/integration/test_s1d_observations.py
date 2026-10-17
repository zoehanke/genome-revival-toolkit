"""Reported observations and constructed predictions stay separate."""
import hashlib
import json
from pathlib import Path
import unittest

from tests.fixtures.gen.genome_identity import build
from tests.integration import test_s1d_messages as cli_support

ROOT = Path(__file__).resolve().parents[2]


class ObservationMessageTests(cli_support.PublicCLICase):
    def assessment(self, *, band=1000, controls="passed", include_predictions=True,
                   result="positive", case_name="different_sizes", background="original", reference_bound=True):
        fixture = build(self.folder / "fixture", case_name)
        reference = next(row for row in fixture["handoff"]["references"] if row["id"] == background)
        observations = {"observations": [], "observation_origin": "SYNTHETIC_NOT_EXPERIMENTAL", "genotype_results": [
            {"sample_id": "constructed_sample", "assay_id": "synthetic_identity", "background_id": background,
             "reference_sha256": reference["sha256"] if reference_bound else hashlib.sha256(b"unrelated synthetic reference").hexdigest(),
             "result": result, "control_status": controls,
             "observed_band_bp": band, "band_tolerance_bp": 0}]}
        path = self.folder / "observations.json"
        path.write_text(json.dumps(observations), encoding="utf-8")
        sources = {"observations": path}
        if include_predictions:
            sources["predictions"] = self.folder / "fixture/identity-expected-results.json"
        version = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))["core"]
        goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": "Compare constructed reports only.",
                "sources": [{"source_id": name, "from": str(path), "as": "artifact", "input_origin": "researcher_observation" if name == "observations" else "user_file", "declared": {}}
                            for name, path in sources.items()],
                "declared_context": [], "targets": [{"id": "t1", "role": "analysis", "required": True}],
                "constraints": [{"id": "present", "check": "check.goal.output_present@" + version, "params": {},
                                 "target": "t1", "source_quote": "Compare constructed reports only.", "status": "active"}], "intents": []}
        declared = self.command("goal", "declare", "--run", self.run_path, request=goal)
        settings = {"goal_digest": declared["result"]["goal_digest"], "source_id": "observations",
                    "observation_origin": "SYNTHETIC_NOT_EXPERIMENTAL", "comparisons": []}
        if include_predictions:
            settings["predictions_source"] = "predictions"
        template = "revival-evidence." + ("assess_predictions" if include_predictions else "assess_observations")
        draft = self.command("template", "instantiate", template, "--run", self.run_path, request=settings)["result"]["draft"]
        self.command("pipeline", "submit", "--run", self.run_path, request=draft)
        self.command("run", "execute", "--run", self.run_path)
        self.command("judge", "--run", self.run_path)
        return json.loads((self.run_path / "candidate/1/assessment.json").read_text(encoding="utf-8"))

    def local(self, report):
        return next(row for row in report["conclusions"] if row["claim"] == "local_prediction_agreement"
                    and row["subject"].get("sample_id") == "constructed_sample")

    def test_positive_without_size_and_controls_is_explicitly_incomplete(self):
        conclusion = self.local(self.assessment(band=None, controls="unknown"))
        self.assertEqual(conclusion["status"], "INSUFFICIENT")
        self.assertIn("incomplete", conclusion["reason"].lower())
        self.assertIn("observed_band_bp", conclusion["reason"])

    def test_positive_without_size_is_incomplete_even_without_prediction(self):
        conclusion = self.local(self.assessment(band=None, controls="unknown", include_predictions=False))
        self.assertEqual(conclusion["status"], "INSUFFICIENT")
        self.assertIn("incomplete", conclusion["reason"].lower())
        self.assertIn("observed_band_bp", conclusion["reason"])

    def test_complete_positive_still_agrees_with_constructed_1000_bp(self):
        # 20 + 960 + 20 = 1000, fixed by fixture construction before execution.
        self.assertEqual(self.local(self.assessment())["status"], "SUPPORTED")

    def test_negative_without_size_remains_a_valid_negative_record(self):
        self.assertEqual(self.local(self.assessment(band=None, result="negative"))["status"], "CONTRADICTED")

    def test_no_product_prediction_and_reported_positive_are_contradicted_without_controls(self):
        # The edited fixture is all C: neither of the constructed primer sites exists.
        report = self.assessment(band=85, controls="unknown", case_name="no_product", background="edited")
        conclusion = self.local(report)
        self.assertEqual(conclusion["status"], "CONTRADICTED")
        self.assertIn("contradict", conclusion["reason"].lower())
        self.assertNotIn("control", conclusion["reason"].lower())
        self.assertTrue(any("control" in row.lower() and "unknown" in row and "constructed_sample" in row
                            for row in report["unverified"]), report["unverified"])

    def test_agreeing_record_without_controls_is_still_insufficient(self):
        report = self.assessment(controls="unknown")
        self.assertEqual(self.local(report)["status"], "INSUFFICIENT")
        self.assertTrue(any("control" in row.lower() and "unknown" in row for row in report["unverified"]))

    def test_failed_controls_do_not_hide_reported_mismatch(self):
        report = self.assessment(band=85, controls="failed", case_name="no_product", background="edited")
        self.assertEqual(self.local(report)["status"], "CONTRADICTED")
        self.assertTrue(any("control" in row.lower() and "failed" in row for row in report["unverified"]))

    def test_unbound_reference_cannot_establish_a_contradiction(self):
        report = self.assessment(band=85, controls="unknown", case_name="no_product", background="edited", reference_bound=False)
        self.assertEqual(self.local(report)["status"], "INSUFFICIENT")

    def test_negative_matches_no_product_but_missing_controls_remain_insufficient(self):
        report = self.assessment(band=None, controls="unknown", case_name="no_product", background="edited", result="negative")
        self.assertEqual(self.local(report)["status"], "INSUFFICIENT")

    def test_incomplete_positive_is_not_used_to_contradict_a_prediction(self):
        report = self.assessment(band=None, controls="unknown", case_name="no_product", background="edited")
        conclusion = self.local(report)
        self.assertEqual(conclusion["status"], "INSUFFICIENT")
        self.assertIn("incomplete", conclusion["reason"].lower())


if __name__ == "__main__":
    unittest.main()
