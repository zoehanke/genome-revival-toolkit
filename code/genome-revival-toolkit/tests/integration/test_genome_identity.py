"""Exercise both templates and bounded negative findings through the existing public API."""
import json
from pathlib import Path
import tempfile
import unittest

from dna_design_core.application.api import call
from dna_design_core.kernel.public import core_version
from tests.fixtures.gen.genome_identity import build
from tests.oracles.genome_identity import check


class GenomeIdentityIntegrationTests(unittest.TestCase):
    def run_case(self, folder, name, *, use_handoff=True):
        case = build(folder, name)
        directory = folder / "run"

        def invoke(verb, request=None, **options):
            receipt = call(verb, root=directory if verb != "run create" else None, request=request, **options)
            self.assertEqual(receipt["problems"], [], receipt)
            return receipt["result"]

        created = invoke("run create", directory=directory)
        self.assertEqual(created["kit_diagnostics"], [])
        text = "Report the synthetic supplied-reference PCR expectations."
        sources = [{"source_id": name, "from": str(path), "as": "artifact",
                    "input_origin": "user_file", "declared": {}} for name, path in case["paths"].items()]
        if use_handoff:
            sources.append({"source_id": "handoff_file", "from": str(folder / "identity-handoff.json"),
                            "as": "artifact", "input_origin": "user_file", "declared": {}})
        goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": text,
                "sources": sources, "declared_context": [], "targets": [{"id": "t1", "role": "analysis", "required": True}],
                "constraints": [{"id": "k1", "check": "check.goal.output_present@" + core_version(),
                                 "params": {}, "target": "t1", "source_quote": text, "status": "active"}], "intents": []}
        goal_digest = invoke("goal declare", goal)["goal_digest"]
        params = {"goal_digest": goal_digest,
                  **{role + "_source": role for role in ("original", "edited", "forward", "reverse")},
                  "original_topology": case["materials"]["original"]["topology"],
                  "edited_topology": case["materials"]["edited"]["topology"],
                  "target": "t1", "assay_id": "synthetic_identity", "forward_id": "forward", "reverse_id": "reverse"}
        if use_handoff:
            params["handoff_source"] = "handoff_file"
            for role in ("forward", "reverse"):
                params.pop(role + "_source")
        template = "genome-identity." + ("from_handoff" if use_handoff else "from_references")
        draft = invoke("template instantiate", params, name=template)["draft"]
        self.assertTrue(all(isinstance(value, dict) for step in draft["steps"] for value in step["inputs"].values()))
        invoke("pipeline submit", draft)
        invoke("run execute")
        judged = invoke("judge")
        self.assertEqual(judged["unsatisfied"], [])
        outcomes = {row["verdict"]["check"]["id"]: row["verdict"]["outcome"] for row in judged["verdicts"]}
        # D7: supplied synthetic references have valid DNA and no CDS features.
        # This says nothing about whether their PCR bands distinguish them.
        self.assertEqual(outcomes["check.annotation_integrity"], "PASS")
        self.assertEqual(outcomes["check.cds_validity"], "NOT_APPLICABLE")
        self.assertEqual(outcomes["check.biological_sanity"], "PASS")
        # These tests retain the exact analysis conclusions through Judge.
        package = directory / "candidate/1"
        table_path = package / "identity-expected-results.json"
        expected = case["expected"]
        if not use_handoff:
            for row, role in zip(expected["backgrounds"], ("original", "edited")):
                row["id"] = "reference_" + role
        self.assertEqual(json.loads(table_path.read_text(encoding="utf-8")), expected)
        circle = name == "circular_origin"
        checked = check(case["paths"]["original"], case["paths"]["edited"], case["paths"]["forward"],
                        case["paths"]["reverse"], table_path, circular_original=circle, circular_edited=circle,
                        handoff=folder / "identity-handoff.json" if use_handoff else None)
        self.assertEqual(checked["status"], expected["backgrounds"][0]["expected"]["status"])

    def test_same_sized_products_remain_not_distinguishable(self):
        with tempfile.TemporaryDirectory(prefix="s5b_same_") as path:
            self.run_case(Path(path), "same_sizes")

    def test_multiple_sites_remain_undetermined(self):
        with tempfile.TemporaryDirectory(prefix="s5b_multi_") as path:
            self.run_case(Path(path), "multiple_sites")

    def test_circular_origin_binding_reaches_public_pipeline_and_judge(self):
        with tempfile.TemporaryDirectory(prefix="s5b_circle_") as path:
            self.run_case(Path(path), "circular_origin")

    def test_template_without_handoff_has_no_untracked_material_list(self):
        with tempfile.TemporaryDirectory(prefix="s5b_refs_") as path:
            self.run_case(Path(path), "different_sizes", use_handoff=False)


if __name__ == "__main__":
    unittest.main()
