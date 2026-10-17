"""S3b answers fixed by the user's five-row count construction, before execution."""
from itertools import product
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tests.oracles.revival_evidence import verify
from tests.revival_s1e import fixture
from tests.revival_support import KIT, context_for, json_file, load_kit, run_case


COMPARISONS = [{"experiment_group": "fusion", "control_group": "control"}]
REASONS = {
    "missing_fusion": "融合平板计数缺失；缺失不是零",
    "zero_fusion": '融合平板报告没有菌落，所谓"生长"不成立',
    "missing_control": "融合平板有菌落，但对照计数缺失，无法判断生长是否与对照不同",
    "positive_control": "对照也出了菌落，无法把融合平板的生长归因于所报告的处理（对照的矛盾另由 control_no_outgrowth 单独报告）",
    "supported": "融合平板有菌落而指定的无生长对照没有；这不证明功能复活，也不证明对照细胞已死",
}


def observations(fusion, control):
    return {"observations": [
        {"id": "fusion1", "group": "fusion", "colonies": fusion, "unit": "colony", "role": "fusion"},
        {"id": "control1", "group": "control", "colonies": control, "unit": "colony",
         "role": "inactivated_donor_control"}]}


class ScopedEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="s3b_scoped_")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.module = load_kit()

    def assess(self, data, comparisons=COMPARISONS, predictions=None, rules=None):
        path = json_file(self.folder / "counts.json", data)
        parsed = self.module.parse_observations(None, path, predictions).documents["document"]
        if rules is not None:
            return self.module.assess(parsed, rules, comparisons)
        return self.module.assess_observations(context_for(), parsed, comparisons).documents["assessment"]

    def scoped(self, report):
        return [row for row in report["conclusions"] if row["claim"] == "fusion_plate_outgrowth"]

    def test_five_rows_and_all_any_control_values(self):
        # Each answer is a literal from the task; the full grid exercises both "any" cells.
        answers = {
            (None, None): ("NOT_TESTED", "missing_fusion"),
            (None, 0): ("NOT_TESTED", "missing_fusion"),
            (None, 31): ("NOT_TESTED", "missing_fusion"),
            (0, None): ("CONTRADICTED", "zero_fusion"),
            (0, 0): ("CONTRADICTED", "zero_fusion"),
            (0, 31): ("CONTRADICTED", "zero_fusion"),
            (9, None): ("INSUFFICIENT", "missing_control"),
            (9, 31): ("INSUFFICIENT", "positive_control"),
            (9, 0): ("SUPPORTED", "supported"),
        }
        for fusion, control in product((None, 0, 9), (None, 0, 31)):
            with self.subTest(fusion=fusion, control=control):
                report = self.assess(observations(fusion, control))
                row, = self.scoped(report)
                state, reason = answers[fusion, control]
                self.assertEqual((row["status"], row["reason"]), (state, REASONS[reason]))
                self.assertEqual(row["subject"], COMPARISONS[0])
                self.assertEqual(row["applicability"], "PASS")
                for global_row in (item for item in report["conclusions"] if not item["subject"]):
                    self.assertIn(global_row["status"], {"INSUFFICIENT", "NOT_TESTED"})

    def test_omitted_comparisons_produce_no_scoped_outgrowth(self):
        path = json_file(self.folder / "counts.json", observations(9, 0))
        document = self.module.parse_observations(None, path).documents["document"]
        report = self.module.assess_observations(context_for(), document).documents["assessment"]
        self.assertEqual(self.scoped(report), [])
        self.assertEqual(report["comparisons"], [])

    def test_explicit_pairs_select_groups_and_support_stays_local(self):
        data = observations(9, 0)
        data["observations"].append({"id": "other1", "group": "other", "colonies": 31, "unit": "colony"})
        pairs = [{"experiment_group": "other", "control_group": "fusion"}, COMPARISONS[0]]
        rows = self.scoped(self.assess(data, pairs))
        self.assertEqual({tuple(row["subject"].values()): row["status"] for row in rows},
                         {("fusion", "control"): "SUPPORTED", ("other", "fusion"): "INSUFFICIENT"})

    def test_partial_control_count_is_not_sum_of_known_rows(self):
        data = observations(9, 0)
        data["observations"].append({"id": "unknown", "group": "control", "colonies": None,
                                     "role": "inactivated_donor_control", "unit": "colony"})
        report = self.assess(data)
        self.assertEqual(self.scoped(report)[0]["status"], "INSUFFICIENT")
        self.assertIsNone(report["comparisons"][0]["control_colonies"])

    def test_perfect_reported_input_cannot_support_global_claims(self):
        path, predicted = fixture(self.folder, result="positive", band=80, controls="passed", tolerance=0)
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(observations(9, 0))
        data["functional_results"] = [{"sample_id": "synthetic_sample", "result": "positive"}]
        report = self.assess(data, predictions=predicted)
        supported = {row["claim"] for row in report["conclusions"] if row["status"] == "SUPPORTED"}
        self.assertEqual(supported, {"fusion_plate_outgrowth", "control_no_outgrowth", "local_prediction_agreement"})
        for row in report["conclusions"]:
            if row["claim"] in {"functional_revival", "whole_genome_elimination"}:
                self.assertEqual(row["status"], "INSUFFICIENT")
                self.assertIn("Scoped conclusions supported: " + ", ".join(sorted(supported)) + ".", row["reason"])
                self.assertIn("Not established:", row["reason"])
        self.assertTrue(all(row["status"] == "SUPPORTED" for row in report["conclusions"][:3]))

    def test_eleven_existing_local_pcr_constructions_remain_unchanged(self):
        # Same eleven constructions as reviews/verification-recipes/revival_evidence_rule_table.py.
        # 80 bp = two 20 bp primer sites plus a 40 bp gap, fixed by the fixture.
        cases = [
            (0, "positive", 90, "unknown", "CONTRADICTED"),
            (0, "positive", 90, "passed", "CONTRADICTED"),
            (1, "positive", 120, "failed", "CONTRADICTED"),
            (1, "negative", None, "unknown", "INSUFFICIENT"),
            (1, "negative", None, "failed", "INSUFFICIENT"),
            (1, "negative", None, "passed", "CONTRADICTED"),
            (0, "negative", None, "unknown", "INSUFFICIENT"),
            (0, "negative", None, "passed", "SUPPORTED"),
            (1, "positive", 80, "unknown", "INSUFFICIENT"),
            (1, "positive", 80, "passed", "SUPPORTED"),
            (1, "positive", None, "passed", "INSUFFICIENT"),
        ]
        for count, result, band, controls, expected in cases:
            with self.subTest(count=count, result=result, band=band, controls=controls):
                path, predicted = fixture(self.folder, count=count, result=result, band=band, controls=controls, tolerance=0)
                report = self.assess(json.loads(path.read_text(encoding="utf-8")), comparisons=[], predictions=predicted)
                local, = [row for row in report["conclusions"] if row["claim"] == "local_prediction_agreement"]
                self.assertEqual(local["status"], expected)
                self.assertEqual(self.scoped(report), [])

    def test_global_progress_uses_actual_local_claims_and_excludes_unsupported(self):
        rules = self.module.read_rules(context_for())
        next(rule for rule in rules if rule["id"] == "evidence.fusion_plate_outgrowth")["parameters"]["claim"] = "renamed_local_claim"
        report = self.assess(observations(9, 0), rules=rules)
        for row in (item for item in report["conclusions"] if not item["subject"]):
            self.assertIn("Scoped conclusions supported: control_no_outgrowth, renamed_local_claim.", row["reason"])
            self.assertNotIn("fusion_plate_outgrowth", row["reason"])
        report = self.assess(observations(9, 31))
        for row in (item for item in report["conclusions"] if not item["subject"]):
            self.assertIn("No scoped conclusion is supported.", row["reason"])
            self.assertNotIn("Scoped conclusions supported:", row["reason"])

    def test_user_source_and_all_five_reasons_are_preserved_unverified(self):
        rule = json.loads((KIT / "knowledge/fusion_plate_outgrowth.json").read_text(encoding="utf-8"))
        self.assertEqual({row["reason"] for row in rule["parameters"]["truth_table"]}, set(REASONS.values()))
        self.assertEqual(rule["source"]["source_class"], "project_contract")
        self.assertEqual(rule["source"]["citation"], "Genome Revival Toolkit SPEC D12 与附录 B3；用户 2026-10-17 的决定（方案 B）")
        self.assertEqual(rule["source"]["verification_status"], "unverified")
        self.assertEqual(rule["source"]["supports"], [REASONS["supported"]])
        self.assertEqual(rule["source"]["does_not_support"], ["功能复活、遗传学恢复、供体来源、对照细胞死亡、记录的真实性"])
        self.assertNotIn("verification_receipt", rule["source"])
        self.assertFalse((KIT / rule["review"]).exists())

    def test_positive_control_to_supported_mutation_is_reached_and_killed(self):
        rules = self.module.read_rules(context_for())
        rule = next(rule for rule in rules if rule["id"] == "evidence.fusion_plate_outgrowth")
        cell = next(row for row in rule["parameters"]["truth_table"] if row["reason"] == REASONS["positive_control"])
        cell["status"] = "SUPPORTED"
        baseline = self.assess(observations(9, 31))
        mutated = self.assess(observations(9, 31), rules=rules)
        self.assertEqual(self.scoped(baseline)[0]["status"], "INSUFFICIENT")
        self.assertEqual(self.scoped(mutated)[0]["status"], "SUPPORTED", "Mutation must execute without crashing.")
        with self.assertRaises(AssertionError):
            self.assertEqual(self.scoped(mutated)[0]["status"], "INSUFFICIENT", "Fixed construction answer kills the mutation.")
        # Even a mutated rule file cannot teach the independent oracle the wrong state.
        rules_dir = self.folder / "mutant-rules"
        shutil.copytree(KIT / "knowledge", rules_dir)
        json_file(rules_dir / "fusion_plate_outgrowth.json", rule)
        report_file = json_file(self.folder / "mutated-report.json", mutated)
        with self.assertRaisesRegex(AssertionError, "Conclusion truth table mismatch"):
            verify(self.folder / "counts.json", rules_dir, report_file, comparisons=COMPARISONS)

    def test_oracle_checks_global_progress_and_declared_comparisons(self):
        report = self.assess(observations(9, 0))
        path = json_file(self.folder / "assessment.json", report)
        self.assertEqual(verify(self.folder / "counts.json", KIT / "knowledge", path, comparisons=COMPARISONS)["result"], "PASS")
        with self.assertRaisesRegex(AssertionError, "Selected comparisons differ"):
            verify(self.folder / "counts.json", KIT / "knowledge", path, comparisons=[])
        next(row for row in report["conclusions"] if row["claim"] == "functional_revival")["reason"] = "No scoped conclusion is supported."
        json_file(path, report)
        with self.assertRaisesRegex(AssertionError, "Conclusion reasons differ"):
            verify(self.folder / "counts.json", KIT / "knowledge", path, comparisons=COMPARISONS)

    def test_card_and_markdown_list_supported_scopes_before_original_limits(self):
        path = json_file(self.folder / "counts.json", observations(9, 0))
        service, report = run_case(self.folder, path)
        sealed = service.assess(publish=True)
        self.assertTrue(sealed["sealed"], sealed)
        package = Path(sealed["manifest"]).parent
        for name in ("runcard.html", "report.md"):
            text = (package / "views" / name).read_text(encoding="utf-8")
            start = text.index("Supported scoped conclusions (submitted records only):")
            end = text.index("Does not support:", start)
            support = text[start:end]
            for row in report["conclusions"]:
                if row["status"] == "SUPPORTED":
                    self.assertIn(row["claim"], support)
                    self.assertIn(row["reason"], support)
            self.assertIn("experiment_group=fusion", support)
            for limit in self.module.LIMITS:
                self.assertIn(limit, text[end:])


if __name__ == "__main__":
    unittest.main()
