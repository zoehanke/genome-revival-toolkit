"""Independent enumeration of the small sourced interpretation table."""
from itertools import product
import json
from pathlib import Path
import unittest

RULE = Path(__file__).resolve().parents[2] / "kits/revival-evidence/knowledge/local_prediction.json"
FIELDS = ("tested", "covered", "controls_passed", "determinate", "size_known", "agrees")


def rows_for(facts):
    table = json.loads(RULE.read_text(encoding="utf-8"))["parameters"]["truth_table"]
    return [row for row in table if all(condition["op"] == "eq" and facts.get(condition["field"]) == condition["value"]
                                      for condition in row["when"])]


class LocalRulePartitionTests(unittest.TestCase):
    def test_complete_boolean_fact_space_has_one_conclusion_per_case(self):
        for observed in ("positive", "negative"):
            for values in product((False, True), repeat=len(FIELDS)):
                facts = {**dict(zip(FIELDS, values)), "result": observed}
                with self.subTest(facts=facts):
                    self.assertEqual(len(rows_for(facts)), 1)

    def test_report_comparison_is_distinct_from_control_confidence(self):
        base = dict.fromkeys(FIELDS, True)
        base["result"] = "positive"
        # Answers come from the requested record-comparison boundaries, not Kit output.
        for changes, expected in (({}, "SUPPORTED"), ({"controls_passed": False}, "INSUFFICIENT"),
            ({"controls_passed": False, "agrees": False}, "CONTRADICTED"),
            ({"controls_passed": False, "agrees": False, "covered": False}, "INSUFFICIENT"),
            ({"controls_passed": False, "agrees": False, "size_known": False}, "INSUFFICIENT"),
            ({"tested": False}, "NOT_TESTED")):
            with self.subTest(changes=changes):
                rows = rows_for({**base, **changes})
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["status"], expected)

    def test_negative_mismatch_requires_reported_passed_controls(self):
        facts = {**dict.fromkeys(FIELDS, True), "result": "negative", "agrees": False}
        self.assertEqual(rows_for({**facts, "controls_passed": False})[0]["status"], "INSUFFICIENT")
        self.assertEqual(rows_for(facts)[0]["status"], "CONTRADICTED")


if __name__ == "__main__":
    unittest.main()
