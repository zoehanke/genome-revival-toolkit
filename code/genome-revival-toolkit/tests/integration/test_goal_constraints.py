"""Six D2 checks through real Catalog/admission/Invoker/View/Store, with literal oracles."""
from copy import deepcopy
import importlib
import inspect
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from goal_runtime import bytes_in, fixture_case, invoke
from dna_design_core.assurance import judge, obligations
from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.view import ReadView
from dna_design_core.kernel import schemas
from dna_design_core.kernel.public import ToolkitError

NAMES = ("topology", "exact_sequence", "components_present", "components_absent", "regions_unchanged", "claim_reported")
EVIDENCE = ROOT / "tests/evidence/s1b-c2"


def fixture(name, variant="pass"):
    return json.loads((ROOT / "tests/fixtures/goal_checks" / (name + "." + variant + ".json")).read_text(encoding="utf-8"))


class GoalConstraintTests(unittest.TestCase):
    def test_six_declarations_params_signatures_and_independent_fixtures(self):
        catalog = Catalog()
        self.assertEqual(catalog.problems, [])
        for name in NAMES:
            value = catalog.declaration("check.goal." + name)
            schemas.require("capability-v1", value)
            self.assertEqual((value["role"], value["scope"], value["evaluates_constraint"], value["offline"]), ("CHECK", "user_goal", True, True))
            module, function = value["source"]["implemented_in"].split(":")
            actual = getattr(importlib.import_module(module), function)
            self.assertEqual(actual.declaration, value)
            signature = inspect.signature(actual)
            self.assertEqual(set(signature.parameters) - {"ctx"}, set(value["params"]["properties"]))
            for variant in ("pass", "fail"):
                control = fixture(name, variant)
                schemas.require(value["params"], control["params"])
                self.assertTrue(control["oracle"]["reason"])
                self.assertEqual(control["expected"], variant.upper())
            for invalid in ({}, {**fixture(name)["params"], "invented": True}):
                with self.assertRaises(ToolkitError):
                    schemas.require(value["params"], invalid)

    def test_all_twelve_literal_fixtures_execute_and_preserve_bytes(self):
        evidence = []
        for name in NAMES:
            for variant in ("pass", "fail"):
                with self.subTest(check=name, variant=variant), tempfile.TemporaryDirectory() as directory:
                    control = fixture(name, variant)
                    session, invoker, candidate = fixture_case(directory, control)
                    before = bytes_in(session.root)
                    verdict = invoke(session, invoker, candidate, control["check"], control["params"])
                    self.assertEqual(verdict["outcome"], control["expected"], verdict)
                    self.assertEqual(verdict["constraint_id"], "c2")
                    self.assertEqual(before, bytes_in(session.root))
                    evidence.append({"fixture": name + "." + variant, "oracle": control["oracle"], "verdict": verdict})
        folder = EVIDENCE
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "check-fixtures.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    def test_target_binding_unknowns_and_no_empty_success(self):
        with tempfile.TemporaryDirectory() as directory:
            control = fixture("topology")
            session, invoker, candidate = fixture_case(directory, control)
            for selected, expected in (({}, "UNKNOWN"), ({"id": "c2", "target": "different"}, "FAIL")):
                changed = {**candidate, "constraint": selected}
                self.assertEqual(invoke(session, invoker, changed, control["check"], control["params"])["outcome"], expected)
            candidate["outputs"] = []
            for name in NAMES:
                self.assertEqual(invoke(session, invoker, candidate, "check.goal." + name, fixture(name)["params"])["outcome"], "FAIL")

    def test_known_mismatch_dominates_unknown_topology_and_null_is_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            control = fixture("topology")
            control["value"]["topology"] = None
            session, invoker, candidate = fixture_case(directory, control)
            self.assertEqual(invoke(session, invoker, candidate, control["check"], control["params"])["outcome"], "UNKNOWN")
            identity = session.store.put("materials", {**control["value"], "topology": "linear"})
            candidate["outputs"].append({"id": identity, "kind": "material", "target": "t1"})
            self.assertEqual(invoke(session, invoker, candidate, control["check"], control["params"])["outcome"], "FAIL")

    def test_exact_sequence_keeps_origin_and_treats_iupac_literally(self):
        with tempfile.TemporaryDirectory() as directory:
            control = fixture("exact_sequence")
            session, invoker, candidate = fixture_case(directory, control)
            for sequence, expected in (("agtcagaa", "PASS"), ("GTCAGAAA", "FAIL"), ("NGTCAGAA", "FAIL"), ("TTCTGACT", "FAIL")):
                self.assertEqual(invoke(session, invoker, candidate, control["check"], {"sequence": sequence})["outcome"], expected)

    def test_component_origin_strand_and_ambiguous_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            control = fixture("components_present")
            control["value"]["topology"] = "circular"
            session, invoker, candidate = fixture_case(directory, control)
            params = {"components": [{"name": "wrap", "sequence": "TTAA"}]}
            wrapped = invoke(session, invoker, candidate, control["check"], params)
            self.assertEqual(wrapped["outcome"], "PASS")
            self.assertEqual(wrapped["evidence"]["components"][0]["positions"], [10])
            params = {"components": [{"name": "reverse", "sequence": "GGGT", "strand": -1}]}
            self.assertEqual(invoke(session, invoker, candidate, control["check"], params)["evidence"]["components"][0]["positions"], [2])
            for sequence, topology in (("AAANNN", "linear"), ("AAATTT", None)):
                identity = session.store.put("materials", {**control["value"], "sequence": sequence, "topology": topology})
                candidate["outputs"][0]["id"] = identity
                params = {"components": [{"name": "uncertain", "sequence": "CCCG"}]}
                for name in ("components_present", "components_absent"):
                    self.assertEqual(invoke(session, invoker, candidate, "check.goal." + name, params)["outcome"], "UNKNOWN")

    def test_region_missing_reference_and_invalid_span_are_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            control = fixture("regions_unchanged")
            session, invoker, candidate = fixture_case(directory, control)
            params = {**control["params"], "reference_material_id": "0" * 64}
            self.assertEqual(invoke(session, invoker, candidate, control["check"], params)["outcome"], "UNKNOWN")
            params = deepcopy(control["params"])
            params["regions"][0]["source_end"] = 999
            self.assertEqual(invoke(session, invoker, candidate, control["check"], params)["outcome"], "UNKNOWN")
            with self.assertRaises(ToolkitError):
                invoke(session, invoker, candidate, control["check"], {**params, "regions": []})

    def test_claim_is_structured_status_and_target_specific_not_truth(self):
        with tempfile.TemporaryDirectory() as directory:
            control = fixture("claim_reported")
            session, invoker, candidate = fixture_case(directory, control)
            passed = invoke(session, invoker, candidate, control["check"], control["params"])
            self.assertEqual(passed["evidence"]["reported_status"], "INSUFFICIENT")
            for value, params, expected in (
                ({"claim": "functional_revival", "status": "UNKNOWN"}, {"claim": "functional_revival", "pointer": ""}, "PASS"),
                ({"claims": [{"claim": "functional_revival", "status": " "}]}, control["params"], "FAIL"),
                ({"claims": [{"claim": "functional_revival", "status": "YES"}] * 2}, control["params"], "FAIL"),
                ({"claims": [{"claim": "different", "status": "YES"}], "notes": "functional_revival"}, control["params"], "FAIL"),
            ):
                identity = session.store.put("documents", value)
                selected = {**candidate, "outputs": [{"id": identity, "kind": "document", "target": "t1"}]}
                self.assertEqual(invoke(session, invoker, selected, control["check"], params)["outcome"], expected)
            with self.assertRaises(ToolkitError):
                invoke(session, invoker, candidate, control["check"], {"claim": "functional_revival", "pointer": "/bad~2token"})
            path = session.root / candidate["outputs"][0]["path"]
            path.write_text('{"claims": []}', encoding="utf-8")
            self.assertEqual(invoke(session, invoker, candidate, control["check"], control["params"])["outcome"], "UNKNOWN")

    def test_six_active_constraints_derive_and_issue_real_judge_verdicts(self):
        for name in NAMES:
            with self.subTest(check=name), tempfile.TemporaryDirectory() as directory:
                control = fixture(name)
                session, invoker, candidate = fixture_case(directory, control)
                required = obligations.derive(session.snapshot(), session.current_goal(), session.current_pipeline(), session.events())
                selected = [item for item in required if item["check"] == control["check"]]
                self.assertEqual(len(selected), 1)
                factory = lambda value: ReadView(session.root, session.events(), session.snapshot(), value)
                result = judge.run(invoker, factory, session.journal, candidate, selected)
                self.assertEqual(result["unsatisfied"], [], result)
                self.assertEqual(result["verdicts"][0]["verdict"]["constraint_id"], "c2")


if __name__ == "__main__":
    unittest.main()
