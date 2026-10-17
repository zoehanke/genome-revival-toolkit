"""Constructed S3 answers: 9-31=-22; missing is unknown; local matches stay local."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revival_support import KIT, AlteredView, context_for, json_file, load_kit, run_case
from dna_design_core.kernel.public import ToolkitError
from dna_design_core.assurance.stage import outputs as staged_outputs


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_kit()

    def parse(self, path, predictions=None):
        return self.module.parse_observations(None, path, predictions, "SYNTHETIC_EXAMPLE")

    def assessment(self, path, predictions=None, comparisons=()):
        document = self.parse(path, predictions).documents["document"]
        return self.module.assess_observations(context_for(), document, comparisons).documents["assessment"]

    def states(self, report, claim):
        return [row["status"] for row in report["conclusions"] if row["claim"] == claim]

    def test_b3_counts_and_global_boundary(self):
        report = self.assessment(KIT / "examples/b3.csv", comparisons=[{"experiment_group": "fusion", "control_group": "control"}])
        self.assertEqual(report["comparisons"][0]["difference"], -22)
        self.assertEqual(self.states(report, "functional_revival"), ["INSUFFICIENT"])
        self.assertEqual(self.states(report, "control_no_outgrowth"), ["CONTRADICTED"])
        self.assertEqual(report["genotype_tests"], "NOT_TESTED")
        self.assertEqual(report["functional_tests"], "NOT_TESTED")

    def test_empty_records_are_explicitly_not_tested(self):
        report = self.assessment(KIT / "examples/empty.json")
        self.assertEqual(self.states(report, "functional_revival"), ["NOT_TESTED"])
        self.assertEqual(self.states(report, "whole_genome_elimination"), ["NOT_TESTED"])
        self.assertEqual(len(report["conclusions"]), 2)

    def test_eight_legacy_truth_table_cells_preserved(self):
        # Independent construction: 2 claims x 4 presence combinations from SPEC D12/B3.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "presence.json"
            for counts, genotypes in ((False, False), (True, False), (False, True), (True, True)):
                with self.subTest(counts=counts, genotypes=genotypes):
                    data = {"observations": [{"id": "x", "group": "test", "colonies": 1, "role": "fusion"}] if counts else [],
                            "genotype_results": [{"sample_id": "s", "assay_id": "a", "background_id": "b", "result": "indeterminate"}] if genotypes else []}
                    report = self.assessment(json_file(path, data))
                    self.assertEqual(self.states(report, "functional_revival"), ["INSUFFICIENT" if counts or genotypes else "NOT_TESTED"])
                    self.assertEqual(self.states(report, "whole_genome_elimination"), ["INSUFFICIENT" if genotypes else "NOT_TESTED"])

    def test_missing_count_remains_missing_and_ids_recorded(self):
        outcome = self.parse(KIT / "examples/no_ids.csv")
        document = outcome.documents["document"]
        self.assertIsNone(document["observations"][1]["colonies"])
        self.assertEqual(document["generated_ids"], [{"row": 1, "id": "row_1"}, {"row": 2, "id": "row_2"}])
        self.assertTrue(any("row_2" in text for text in outcome.unverified))
        self.assertEqual(outcome.verdicts[0]["issuer"], "tool_self_report")
        report = self.module.assess_observations(context_for(), document, [{"experiment_group": "fusion", "control_group": "control"}]).documents["assessment"]
        self.assertIsNone(report["comparisons"][0]["difference"])
        self.assertEqual(self.states(report, "control_no_outgrowth"), ["NOT_TESTED"])

    def test_partial_group_counts_do_not_sum_known_subset(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "mixed.csv"
            path.write_text("id,group,colonies,unit,role\nx,fusion,5,colony,fusion\ny,fusion,,colony,fusion\nz,control,0,colony,inactivated_donor_control\n", encoding="utf-8")
            report = self.assessment(path, comparisons=[{"experiment_group": "fusion", "control_group": "control"}])
            self.assertIsNone(next(row for row in report["groups"] if row["group"] == "fusion")["colonies"])
            self.assertIsNone(report["comparisons"][0]["difference"])

    def test_zero_control_is_reported_absence_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "zero.csv"
            path.write_text("id,group,colonies,unit,role\nx,control,0,colony,inactivated_donor_control\n", encoding="utf-8")
            self.assertEqual(self.states(self.assessment(path), "control_no_outgrowth"), ["SUPPORTED"])

    def test_missing_unit_yields_unknown_comparison(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "counts.csv"
            path.write_text("group,colonies,role\nfusion,9,fusion\ncontrol,31,inactivated_donor_control\n", encoding="utf-8")
            report = self.assessment(path, comparisons=[{"experiment_group": "fusion", "control_group": "control"}])
            self.assertEqual(report["comparisons"][0]["outcome"], "UNKNOWN")
            self.assertIsNone(report["comparisons"][0]["difference"])

    def test_tidy_csv_supported(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tidy.csv"
            path.write_text("group,measure,value,unit\nfusion,colony_count,9,colony\n", encoding="utf-8-sig")
            self.assertEqual(self.parse(path).documents["document"]["observations"][0]["colonies"], 9)

    def test_count_input_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            for count in [-1, True, "1.5", "NaN", "Infinity"]:
                with self.subTest(count=count):
                    json_file(path, {"observations": [{"group": "fusion", "colonies": count}]})
                    with self.assertRaises(ToolkitError):
                        self.parse(path)

    def test_duplicate_ids_rejected_generated_ids_do_not_collide(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ids.csv"
            path.write_text("id,group,colonies\nrow_2,fusion,1\n,control,0\n", encoding="utf-8")
            self.assertEqual(self.parse(path).documents["document"]["generated_ids"], [{"row": 2, "id": "row_2_auto"}])
            path.write_text("id,group,colonies\nx,fusion,1\nx,control,0\n", encoding="utf-8")
            with self.assertRaises(ToolkitError):
                self.parse(path)

    def test_s5b_handoff_supported_and_opposite_local_results(self):
        report = self.assessment(KIT / "examples/local_observations.json", KIT / "examples/identity-expected-results.json")
        states = {row["subject"]["background_id"]: row["status"] for row in report["conclusions"] if row["claim"] == "local_prediction_agreement"}
        self.assertEqual(states, {"edited": "CONTRADICTED", "original": "SUPPORTED"})
        self.assertEqual(self.states(report, "functional_revival"), ["INSUFFICIENT"])
        self.assertEqual(self.states(report, "whole_genome_elimination"), ["INSUFFICIENT"])

    def test_no_bands_cannot_be_inferred_from_colonies(self):
        report = self.assessment(KIT / "examples/b3.csv", KIT / "examples/identity-expected-results.json")
        self.assertEqual(self.states(report, "local_prediction_agreement"), ["NOT_TESTED", "NOT_TESTED"])

    def test_local_assay_evidence_requirements(self):
        base = json.loads((KIT / "examples/local_observations.json").read_text(encoding="utf-8"))
        base["genotype_results"] = base["genotype_results"][:1]
        mutations = [({"control_status": "unknown"}, "INSUFFICIENT"), ({"reference_sha256": "3" * 64}, "INSUFFICIENT"),
                     ({"reference_sha256": None}, "INSUFFICIENT"), ({"observed_band_bp": None}, "INSUFFICIENT"),
                     ({"result": "indeterminate", "observed_band_bp": None}, "INSUFFICIENT"),
                     ({"result": "not_tested", "observed_band_bp": None}, "NOT_TESTED"),
                     ({"result": "negative", "observed_band_bp": None}, "CONTRADICTED")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "observations.json"
            for change, expected in mutations:
                with self.subTest(change=change):
                    current = deepcopy(base)
                    current["genotype_results"][0].update(change)
                    if current["genotype_results"][0].get("reference_sha256") is None:
                        current["genotype_results"][0].pop("reference_sha256", None)
                    json_file(path, current)
                    rows = self.assessment(path, KIT / "examples/identity-expected-results.json")["conclusions"]
                    self.assertEqual(next(row for row in rows if row["subject"].get("sample_id") == "sample1")["status"], expected)

    def test_negative_prediction_and_explicit_tolerance(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            predicted = json.loads((KIT / "examples/identity-expected-results.json").read_text(encoding="utf-8"))
            observed = json.loads((KIT / "examples/local_observations.json").read_text(encoding="utf-8"))
            observed["genotype_results"] = observed["genotype_results"][:1]
            observed["genotype_results"][0].update(observed_band_bp=1001, band_tolerance_bp=1)
            model = json_file(folder / "expected.json", predicted)
            path = json_file(folder / "observed.json", observed)
            self.assertIn("SUPPORTED", self.states(self.assessment(path, model), "local_prediction_agreement"))
            predicted["backgrounds"][0]["expected"]["product_bp"] = None
            predicted["backgrounds"][0]["expected"]["product_count"] = 0
            json_file(model, predicted)
            self.assertIn("CONTRADICTED", self.states(self.assessment(path, model), "local_prediction_agreement"))
            observed["genotype_results"][0].update(result="negative", observed_band_bp=None)
            json_file(path, observed)
            self.assertIn("SUPPORTED", self.states(self.assessment(path, model), "local_prediction_agreement"))

    def test_invalid_handoff_is_not_guessed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = json_file(Path(folder) / "old.json", {"schema_version": "identity-expected-results-v1", "rows": [], "references": {}})
            with self.assertRaises(ToolkitError):
                self.parse(KIT / "examples/b3.csv", path)

    def test_new_team_can_change_claim_table_without_engine_change(self):
        rules = self.module.read_rules(context_for())
        rules[0]["parameters"]["claim"] = "team_defined_record_claim"
        rules[0]["parameters"]["truth_table"][1]["status"] = "SUPPORTED"
        parsed = self.parse(KIT / "examples/b3.csv").documents["document"]
        report = self.module.assess(parsed, rules)
        self.assertEqual(self.states(report, "team_defined_record_claim"), ["SUPPORTED"])

    def test_deterministic_parse_and_assessment(self):
        first = self.assessment(KIT / "examples/no_ids.csv")
        self.assertEqual(first, self.assessment(KIT / "examples/no_ids.csv"))

    def test_checker_pass_and_deliberate_fail_fixtures(self):
        for variant in ("pass", "fail"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as folder:
                service, report = run_case(Path(folder))
                judged = service.assess()
                fixture = json.loads((KIT / "capabilities/fixtures" / ("consistency." + variant + ".json")).read_text(encoding="utf-8"))
                report["comparisons"][0]["difference"] = fixture["reported_difference"]
                step = service.view().steps()[-1]
                identity = step["completed"]["payload"]["outputs"]["documents"]["assessment"][0]
                candidate = next((service.root / "candidate").iterdir())
                original = service.view({"root": str(candidate), "outputs": [], "catalog": service.session.snapshot()})
                view = AlteredView(original, {identity: report})
                verdict = self.module.check_record_consistency(context_for(view)).verdicts[0]
                self.assertEqual(verdict["outcome"], fixture["expected"])
                self.assertTrue(judged["verdicts"])

    def test_checker_catches_parse_missingness_and_claim_mutations(self):
        with tempfile.TemporaryDirectory() as folder:
            service, report = run_case(Path(folder), KIT / "examples/no_ids.csv")
            service.assess()
            base = service.view({"root": str(next((service.root / "candidate").iterdir())), "outputs": [], "catalog": service.session.snapshot()})
            first, second = base.steps()
            parsed_id = first["completed"]["payload"]["outputs"]["documents"]["document"][0]
            report_id = second["completed"]["payload"]["outputs"]["documents"]["assessment"][0]
            parsed = base.document(parsed_id)
            parsed["observations"][1]["colonies"] = 0
            report["conclusions"][0]["status"] = "SUPPORTED"
            for alteration in ({parsed_id: parsed}, {report_id: report}):
                with self.subTest(ids=list(alteration)):
                    view = AlteredView(base, alteration)
                    self.assertEqual(self.module.check_record_consistency(context_for(view)).verdicts[0]["outcome"], "FAIL")

    def test_checker_without_assessment_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            service, _ = run_case(Path(folder))
            base = service.view({"root": str(service.root), "outputs": [], "catalog": service.session.snapshot()})
            view = AlteredView(base, {})
            view.steps = lambda: []
            self.assertEqual(self.module.check_record_consistency(context_for(view)).verdicts[0]["outcome"], "UNKNOWN")

    def test_zero_and_multiple_predictions_are_distinct(self):
        report = self.assessment(KIT / "examples/product-count-observations.json", KIT / "examples/product-count-predictions.json")
        local = {row["subject"]["background_id"]: row["status"] for row in report["conclusions"]
                 if row["claim"] == "local_prediction_agreement"}
        self.assertEqual(local, {"absent": "SUPPORTED", "single": "SUPPORTED", "multiple": "INSUFFICIENT"})
        self.assertEqual(self.states(report, "functional_revival"), ["INSUFFICIENT"])

    def test_handoff_count_and_size_and_primer_pair_contract(self):
        baseline = json.loads((KIT / "examples/identity-expected-results.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "expected.json"
            for count, size in [(0, 1000), (1, None), (2, 1000), (-1, None), (True, 1000)]:
                with self.subTest(count=count, size=size):
                    model = deepcopy(baseline)
                    model["backgrounds"][0]["expected"].update(product_count=count, product_bp=size)
                    with self.assertRaises(ToolkitError):
                        self.parse(KIT / "examples/b3.csv", json_file(path, model))
            for pair in ("forward", ["forward"], ["f", "r", "third"]):
                with self.subTest(primer_pair=pair):
                    model = deepcopy(baseline)
                    model["backgrounds"][0]["primer_pair"] = pair
                    with self.assertRaises(ToolkitError):
                        self.parse(KIT / "examples/b3.csv", json_file(path, model))
            model = deepcopy(baseline)
            del model["backgrounds"][0]["expected"]["product_count"]
            with self.assertRaises(ToolkitError):
                self.parse(KIT / "examples/b3.csv", json_file(path, model))

    def test_claim_constraint_reports_insufficient_and_derives_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            service, _ = run_case(Path(folder))
            constraint = service.view().goal["constraints"][0]
            self.assertEqual(constraint["origin"], "user_quoted")
            judged = service.assess()
            verdict = next(row["verdict"] for row in judged["verdicts"]
                           if row["verdict"]["check"]["id"] == "check.goal.claim_reported")
            self.assertEqual(verdict["outcome"], "PASS")
            self.assertEqual(verdict["evidence"]["reported_status"], "INSUFFICIENT")

    def test_missing_requested_theme_prevents_sealing(self):
        with tempfile.TemporaryDirectory() as folder:
            service, _ = run_case(Path(folder), claim="missing_theme")
            sealed = service.assess(publish=True)
            self.assertFalse(sealed["sealed"])
            self.assertIn({"check": "check.goal.claim_reported", "outcome": "FAIL"},
                          [{key: row[key] for key in ("check", "outcome")} for row in sealed["unsatisfied"]])

    def test_action_check_and_verify_use_frozen_knowledge(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            kit = folder / "external-kit"
            shutil.copytree(KIT, kit)
            def change_live_rules(service):
                path = kit / "knowledge/functional_revival.json"
                rule = json.loads(path.read_text(encoding="utf-8"))
                rule["parameters"]["truth_table"][1]["status"] = "SUPPORTED"
                json_file(path, rule)
            with patch("dna_design_core.catalog.registry.BUNDLED", folder / "no-bundled"):
                service, report = run_case(folder, kit_dirs=[kit], before_execute=change_live_rules)
                self.assertEqual(self.states(report, "functional_revival"), ["INSUFFICIENT"])
                sealed = service.assess(publish=True)
                self.assertTrue(sealed["sealed"], sealed)
                package = Path(sealed["manifest"]).parent
                self.assertTrue(service.verify(package)["verified"])

    def test_invoked_checker_rejects_changed_export_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as folder:
            service, report = run_case(Path(folder))
            service.assess()
            candidate_root = next((service.root / "candidate").iterdir())
            report["conclusions"][0]["status"] = "SUPPORTED"
            path = json_file(candidate_root / "assessment.json", report)
            before = path.read_bytes()
            snapshot = service.session.snapshot()
            rows = [{key: value for key, value in row.items() if key != "value"} for row in staged_outputs(service.view(), snapshot)]
            view = service.view({"root": str(candidate_root), "outputs": rows, "catalog": snapshot})
            result = service.invoker.invoke("evidence.check_record_consistency", {}, {}, parent="final", view=view)
            self.assertEqual(result.verdicts[0]["outcome"], "FAIL")
            self.assertEqual(path.read_bytes(), before)

    def test_seal_portability_and_not_done(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            service, _ = run_case(folder)
            self.assertEqual(service.assess()["unsatisfied"], [])
            sealed = service.assess(publish=True)
            package = Path(sealed["manifest"]).parent
            copied = folder / "portable" / package.name
            shutil.copytree(package, copied)
            service.root.rename(folder / "retained")
            receipt = service.verify(copied)
            self.assertTrue(receipt["verified"], receipt)
            self.assertFalse(any((copied / "store/materials").glob("*.json")))
            manifest = json.loads((copied / "manifest.json").read_text(encoding="utf-8"))
            card = (copied / "views/runcard.html").read_text(encoding="utf-8")
            self.assertTrue(any("PCR" in text and "NOT_PERFORMED" in text for text in manifest["not_verified"]))
            self.assertTrue(all(text in card for text in manifest["not_verified"]))
            self.assertIn("evidence.check_record_consistency", [row["check"] for row in manifest["verdicts"]])


if __name__ == "__main__":
    unittest.main()
