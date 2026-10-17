"""Round2 shared capabilities through actual admitted S1 plans and Invoker."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from biology_runtime import action_case, material, retained, run_steps
from dna_design_core.catalog.registry import Catalog
from dna_design_core.kernel import schemas


class Round2CapabilityTests(unittest.TestCase):
    def test_four_declarations_and_real_outputs(self):
        cases = [
            ("seq.replace_region", {"material": material("AAACCCGGG", "linear", "double"), "insert": material("AT", "linear", "double")},
             {"start": 3, "end": 6}, "product", "AAAATGGG"),
            ("seq.inspect_cds", {"material": material("ATGAAATAA", "linear", "double")}, {"translation_table": 1}, "translation", "MK"),
            ("primer.enumerate_candidates", {"template": material("AAACCCTTTGGG", "linear", "double")},
             {"anchor": 0, "strand": 1, "lengths": [3]}, "candidate", "AAA"),
        ]
        for identity, inputs, params, field, expected in cases:
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as directory:
                session, _ = action_case(directory, identity, inputs, params)
                result = retained(session)
                actual = result["products"]["product"][0]["sequence"] if field == "product" else (
                    result["documents"]["report"]["translation"] if field == "translation" else result["documents"]["report"]["candidates"][0]["binding_core"])
                self.assertEqual(actual, expected)
        with tempfile.TemporaryDirectory() as directory:
            steps = [{"step_id": "template", "use": "seq.make_material", "inputs": {"sequence": {"literal": "AAACCCTTTGGG"}},
                      "params": {"topology": "linear", "strandedness": "double"}, "why": "Construct a labelled synthetic sequence."},
                     {"step_id": "target", "use": "primer.sequencing_coverage", "inputs": {
                         "template": {"step": "template", "port": "material"}, "primers": {"literal": ["AAAC"]}},
                      "params": {"read_length": 4, "trim": 1}, "why": "Project a manually determined usable interval."}]
            session, _ = run_steps(directory, steps)
            self.assertEqual(retained(session)["documents"]["report"]["forward_positions"], [5, 6, 7])
        for identity in [case[0] for case in cases] + ["primer.sequencing_coverage"]:
            declaration = Catalog().declaration(identity)
            schemas.require("capability-v1", declaration)
            module, function = declaration["source"]["implemented_in"].split(":")
            self.assertEqual(getattr(importlib.import_module(module), function).declaration, declaration)
            self.assertEqual(json.loads((ROOT / "src/dna_design_core/resources/capabilities" / (identity + ".json")).read_text()), declaration)


if __name__ == "__main__":
    unittest.main()
