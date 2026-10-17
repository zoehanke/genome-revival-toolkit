"""Manual mutations of the S3 consistency checker, on disposable Kit copies."""
from copy import deepcopy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revival_support import KIT, AlteredView, context_for, load_kit, run_case


class EvidenceMutations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.temporary.name)
        cls.service, cls.report = run_case(cls.folder, KIT / "examples/no_ids.csv")
        cls.service.assess()
        cls.view = cls.service.view({"root": str(cls.service.root), "outputs": [], "catalog": cls.service.session.snapshot()})
        first, second = cls.view.steps()
        cls.parsed_id = first["completed"]["payload"]["outputs"]["documents"]["document"][0]
        cls.report_id = second["completed"]["payload"]["outputs"]["documents"]["assessment"][0]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def mutant(self, name, old, new):
        root = self.folder / name
        shutil.copytree(KIT, root)
        path = root / "capabilities/evidence.py"
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1)
        path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
        return load_kit(root, name)

    def test_skip_parse_comparison_killed_by_missing_count_fixture(self):
        mutant = self.mutant("skip_parse", "if actual != expected:\n                        failures.append(identity)\n                    parsed", "if False:\n                        failures.append(identity)\n                    parsed")
        document = self.view.document(self.parsed_id)
        document["observations"][1]["colonies"] = 0
        # Keep the derived report coherent with this wrong parse: only source rereading catches it.
        report = mutant.assess(document, mutant.read_rules(context_for(self.view)), [{"experiment_group": "fusion", "control_group": "control"}])
        view = AlteredView(self.view, {self.parsed_id: document, self.report_id: report})
        baseline = load_kit().check_record_consistency(context_for(view)).verdicts[0]
        changed = mutant.check_record_consistency(context_for(view)).verdicts[0]
        self.assertEqual(baseline["outcome"], "FAIL")
        self.assertEqual(changed["outcome"], "PASS", "Mutation must be reached and falsify the fixture, not crash.")

    def test_skip_assessment_comparison_killed_by_claim_fixture(self):
        mutant = self.mutant("skip_assessment", "if actual != expected:\n                        failures.append(identity)\n                    assessed", "if False:\n                        failures.append(identity)\n                    assessed")
        report = deepcopy(self.report)
        next(row for row in report["conclusions"] if row["claim"] == "functional_revival")["status"] = "SUPPORTED"
        view = AlteredView(self.view, {self.report_id: report})
        self.assertEqual(load_kit().check_record_consistency(context_for(view)).verdicts[0]["outcome"], "FAIL")
        self.assertEqual(mutant.check_record_consistency(context_for(view)).verdicts[0]["outcome"], "PASS")

    def test_skip_failure_aggregation_killed_by_wrong_difference_fixture(self):
        mutant = self.mutant("skip_failures", "if failures:\n                outcome = \"FAIL\"", "if False:\n                outcome = \"FAIL\"")
        report = deepcopy(self.report)
        report["comparisons"][0]["difference"] = 0
        view = AlteredView(self.view, {self.report_id: report})
        self.assertEqual(load_kit().check_record_consistency(context_for(view)).verdicts[0]["outcome"], "FAIL")
        self.assertEqual(mutant.check_record_consistency(context_for(view)).verdicts[0]["outcome"], "PASS")


if __name__ == "__main__":
    unittest.main()
