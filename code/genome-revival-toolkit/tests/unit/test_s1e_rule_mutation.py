"""A controls-free negative must fail the fixed decision-table expectation if mutated."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import types
import unittest

from tests.oracles.revival_evidence import verify
from tests.revival_s1e import fixture
from tests.revival_support import KIT, context_for, load_kit


class NegativeRuleMutationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="s1e_mutation_")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.observations, self.predictions = fixture(self.folder, count=1, result="negative", controls="unknown")
        self.module = load_kit()
        self.document = self.module.parse_observations(None, self.observations, self.predictions).documents["document"]

    def state(self, report):
        return next(row["status"] for row in report["conclusions"] if row["claim"] == "local_prediction_agreement")

    def test_mutating_negative_without_controls_back_to_contradicted_is_caught(self):
        context = context_for()
        normal = self.module.assess_observations(context, self.document).documents["assessment"]
        self.assertEqual(self.state(normal), "INSUFFICIENT", "User decision: a failed reaction remains possible.")
        def mutant_knowledge(pack):
            rule = context.knowledge(pack)
            if rule["id"] == "evidence.local_prediction":
                row = next(row for row in rule["parameters"]["truth_table"]
                           if {part["field"]: part["value"] for part in row["when"]}.get("result") == "negative"
                           and {part["field"]: part["value"] for part in row["when"]}.get("controls_passed") is False)
                row["status"] = "CONTRADICTED"
            return rule
        changed = self.module.assess_observations(types.SimpleNamespace(knowledge=mutant_knowledge),
                                                 self.document).documents["assessment"]
        self.assertEqual(self.state(changed), "CONTRADICTED", "Mutation must be reached without a crash.")
        with self.assertRaises(AssertionError):
            self.assertEqual(self.state(changed), "INSUFFICIENT", "Fixed acceptance answer rejects the mutation.")

    def test_independent_oracle_rejects_false_negative_contradiction(self):
        report = self.module.assess_observations(context_for(), self.document).documents["assessment"]
        path = self.folder / "assessment.json"
        path.write_text(json.dumps(report), encoding="utf-8")
        self.assertEqual(verify(self.observations, KIT / "knowledge", path, self.predictions)["result"], "PASS")
        wrong = deepcopy(report)
        next(row for row in wrong["conclusions"] if row["claim"] == "local_prediction_agreement")["status"] = "CONTRADICTED"
        path.write_text(json.dumps(wrong), encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "Conclusion truth table mismatch"):
            verify(self.observations, KIT / "knowledge", path, self.predictions)


if __name__ == "__main__":
    unittest.main()
