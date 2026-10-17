"""Real template controls and source mutants with constructed, literal answers."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.loading import Loader
from dna_design_core.kernel.public import require_schema

TEMPLATE = ROOT / "examples/kit-template"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def functions(root):
    catalog = Catalog([root])
    if catalog.problems:
        raise AssertionError(catalog.problems)
    namespace = next(row["id"].split(".")[0] for row in catalog.describe("capabilities")
                     if row["owner"] == "kit:" + load_json(root / "kit.json")["name"])
    loader = Loader()
    return (loader.load(catalog.entries[namespace + ".count_words"]),
            loader.load(catalog.entries[namespace + ".check_count"]))


def context(root, text, report, moment="final"):
    rule = load_json(root / "knowledge/minimum_words.json")
    prefix = rule["evaluator"].split(".")[0]
    retained = {"outputs": {"documents": {"report": ["retained-report"]}}}
    step = {"definition": {"step_id": "count", "use": prefix + ".count_words"},
            "started": {"payload": {"params": {"text": text}}},
            "completed": {"payload": retained}, "superseded": False}
    candidate = {"moment": moment, "issuer": "tool_self_report" if moment == "step" else "check_capability",
                 "step_id": "count", "step_outputs": retained}
    view = SimpleNamespace(candidate=candidate, steps=lambda: [deepcopy(step)],
                           document=lambda identity: deepcopy(report), events=lambda: [{"run_id": "a" * 16}])
    return SimpleNamespace(knowledge=lambda pack: deepcopy(rule), view=view)


def assert_controls(case, root):
    _, check = functions(root)
    for name in ("pass", "fail"):
        fixture = load_json(root / ("capabilities/fixtures/count." + name + ".json"))
        case.assertEqual(fixture["oracle"]["kind"], "construction")
        for moment in ("step", "final"):
            result = check(context(root, fixture["text"], fixture["report"], moment))
            case.assertEqual(result.verdicts[0]["outcome"], fixture["expected"], (name, moment))
            case.assertEqual(result.verdicts[0]["moment"], moment)


class KitTemplateTests(unittest.TestCase):
    def test_template_is_explicit_only_and_contributions_match_declarations(self):
        baseline = Catalog()
        self.assertNotIn("word-count", [row["name"] for row in baseline.kit_receipts])
        catalog = Catalog([TEMPLATE])
        self.assertEqual(catalog.problems, [])
        action, check = functions(TEMPLATE)
        for function in (action, check):
            self.assertEqual(function.declaration, catalog.declaration(function.declaration["id"]))
        self.assertEqual(len(catalog.entries) - len(baseline.entries), 2)
        self.assertEqual(action.declaration["step_checks"], [check.declaration["id"]])
        self.assertEqual(action.declaration["final_checks"], [{"check": check.declaration["id"]}])
        self.assertEqual(Catalog().describe("capabilities"), baseline.describe("capabilities"))

    def test_all_template_contracts_sources_and_inline_schema_are_valid(self):
        manifest = load_json(TEMPLATE / "kit.json")
        require_schema("kit-v1", manifest)
        for names in manifest["contributes"].values():
            for name in names:
                value = load_json(TEMPLATE / name)
                if "schema" in value:
                    require_schema(value["schema"], value)
        rule = load_json(TEMPLATE / "knowledge/minimum_words.json")
        self.assertEqual(rule["source"]["source_class"], "project_contract")
        self.assertEqual(rule["source"]["verification_status"], "unverified")
        self.assertTrue(rule["source"]["citation"])
        self.assertFalse((TEMPLATE / "knowledge/review").exists())
        self.assertFalse(TEMPLATE.is_relative_to(ROOT / "kits"))

    def test_capability_imports_use_only_public_interface_and_own_package(self):
        for path in (TEMPLATE / "capabilities").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertTrue(node.level or node.module == "dna_design_core.kernel.public", path)
                self.assertNotIsInstance(node, ast.Import, path)

    def test_action_matches_constructed_counts_and_decisions(self):
        action, check = functions(TEMPLATE)
        # Literal tokens fix these answers before either implementation runs.
        cases = [("", 0, False), (" \t\n", 0, False), ("red", 1, False),
                 ("red green", 2, False), ("red green blue", 3, True),
                 (" red\tgreen\nblue\u00a0gold ", 4, True), ("red,green", 1, False)]
        for text, count, decision in cases:
            ctx = context(TEMPLATE, text, {})
            result = action(ctx, text)
            self.assertEqual(result.documents["report"]["word_count"], count)
            self.assertEqual(result.documents["report"]["meets_minimum"], decision)
            self.assertEqual(result.documents, action(ctx, text).documents)
            require_schema(action.declaration["outputs"][0]["schema"], result.documents["report"])
            self.assertEqual(check(context(TEMPLATE, text, result.documents["report"])).verdicts[0]["outcome"], "PASS")

    def test_positive_and_negative_controls_really_run_at_both_moments(self):
        assert_controls(self, TEMPLATE)

    def test_missing_records_are_unknown(self):
        _, check = functions(TEMPLATE)
        ctx = context(TEMPLATE, "red", {})
        ctx.view.steps = lambda: []
        self.assertEqual(check(ctx).verdicts[0]["outcome"], "UNKNOWN")

    def test_count_and_threshold_source_mutants_are_rejected(self):
        mutations = [("len(text.split())", "len(text.split()) + 1"),
                     ("count >= minimum", "count < minimum")]
        for old, new in mutations:
            with tempfile.TemporaryDirectory(prefix="grt-word-mutant-") as temporary:
                copied = Path(temporary) / "word-count"
                shutil.copytree(TEMPLATE, copied)
                path = copied / "capabilities/count.py"
                body = path.read_text(encoding="utf-8")
                self.assertEqual(body.count(old), 1)
                path.write_text(body.replace(old, new), encoding="utf-8")
                action, check = functions(copied)
                report = action(context(copied, "red green blue gold", {}), "red green blue gold").documents["report"]
                self.assertEqual(check(context(copied, "red green blue gold", report)).verdicts[0]["outcome"], "FAIL")

    def test_disabled_check_comparison_is_caught_by_negative_control(self):
        with tempfile.TemporaryDirectory(prefix="grt-check-mutant-") as temporary:
            copied = Path(temporary) / "word-count"
            shutil.copytree(TEMPLATE, copied)
            path = copied / "capabilities/check.py"
            body = path.read_text(encoding="utf-8")
            self.assertEqual(body.count("report == expected"), 1)
            path.write_text(body.replace("report == expected", "True"), encoding="utf-8")
            with self.assertRaises(AssertionError):
                assert_controls(self, copied)


if __name__ == "__main__":
    unittest.main()
