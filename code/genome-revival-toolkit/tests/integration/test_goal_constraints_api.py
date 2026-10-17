"""D2 through the public application API; scientific profile obligations remain independent."""
import json
from pathlib import Path
import tempfile
import unittest

from dna_design_core.application import api
from dna_design_core.kernel.public import core_version

ROOT = Path(__file__).resolve().parents[2]


class GoalConstraintApiTests(unittest.TestCase):
    def test_public_goal_execute_judge_keeps_six_constraint_answers(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            def call(verb, **params):
                receipt = api.call(verb, **params)
                self.assertEqual(receipt["problems"], [], receipt)
                return receipt
            call("run create", directory=run)
            reference = json.loads((ROOT / "tests/fixtures/goal_checks/regions_unchanged.pass.json").read_text())
            checks = {
                "topology": {"topology": "linear"}, "exact_sequence": {"sequence": "AAAATGGGTTT"},
                "components_present": {"components": [{"name": "retained", "sequence": "GGGTTT"}]},
                "components_absent": {"components": [{"name": "removed", "sequence": "CCC"}]},
                "regions_unchanged": reference["params"], "claim_reported": {"claim": "functional_revival", "pointer": ""},
            }
            goal = {"schema": "goal-v1", "version": 1, "parent_digest": None,
                    "original_request": "Replace CCC with AT; report the sequence.", "sources": [], "declared_context": [],
                    "targets": [{"id": "t1", "role": "component", "required": True}, {"id": "t2", "role": "analysis", "required": True}],
                    "constraints": [{"id": "c" + str(index), "check": "check.goal." + name + "@" + core_version(), "params": params,
                        "target": "t2" if name == "claim_reported" else "t1", "source_quote": "Replace CCC", "status": "active"}
                        for index, (name, params) in enumerate(checks.items())], "intents": []}
            declared = call("goal declare", root=run, request=goal)
            steps = [{"step_id": identity, "use": "seq.make_material", "inputs": {"sequence": {"literal": sequence}},
                      "params": {"topology": "linear", "strandedness": "double"}, "why": "Construct literal synthetic DNA."}
                     for identity, sequence in (("reference", "AAACCCGGGTTT"), ("insert", "AT"))]
            steps += [{"step_id": "edit", "use": "seq.replace_region", "inputs": {
                "material": {"step": "reference", "port": "material"}, "insert": {"step": "insert", "port": "material"}},
                "params": {"start": 3, "end": 6}, "why": "Apply the predeclared interval replacement."},
                {"step_id": "report", "use": "seq.reverse_complement", "inputs": {"sequence": {"literal": "AGTCAGAA"}},
                 "params": {}, "why": "Produce a sequence document that deliberately has no functional claim."}]
            plan = {"schema": "pipeline-v1", "version": 1, "goal_digest": declared["result"]["goal_digest"], "steps": steps,
                    "outputs": [{"name": "edited", "from": {"step": "edit", "port": "product"}, "target": "t1"},
                                {"name": "report", "from": {"step": "report", "port": "result"}, "target": "t2"}]}
            call("pipeline submit", root=run, request=plan)
            self.assertEqual(call("run execute", root=run)["state"], "COMPLETED")
            receipt = call("judge", root=run)
            actual = {row["verdict"]["check"]["id"].removeprefix("check.goal."): row["verdict"]["outcome"]
                      for row in receipt["result"]["verdicts"] if row["verdict"].get("constraint_id")}
            self.assertEqual(actual, {name: "FAIL" if name == "claim_reported" else "PASS" for name in checks})
            folder = ROOT / "tests/evidence/s1b-c2"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "public-api.json").write_text(json.dumps({"scope": "Public goal/submit/execute/judge; no seal claim.",
                "expected_basis": "Literal CCC deletion, retained AAA/GGGTTT, exact edited string and a report lacking a claim/status.",
                "actual": actual, "unsatisfied_checks": [row["check"] for row in receipt["result"]["unsatisfied"]]}, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    unittest.main()
