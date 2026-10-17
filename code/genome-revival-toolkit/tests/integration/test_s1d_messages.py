"""Public CLI errors retain rejection and identify the action needed."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PublicCLICase(unittest.TestCase):
    def setUp(self):
        retained = os.environ.get("GRT_S1D_EVIDENCE")
        if retained:
            self.folder = Path(retained) / self._testMethodName
            self.folder.mkdir(parents=True, exist_ok=False)
        else:
            temporary = tempfile.TemporaryDirectory(prefix="s1d_cli_")
            self.addCleanup(temporary.cleanup)
            self.folder = Path(temporary.name)
        self.index = 0
        self.run_path = self.folder / "run"
        self.command("run", "create", self.run_path)

    def command(self, *arguments, request=None, expected=0):
        number = self.index
        self.index += 1
        if request is not None:
            path = self.folder / f"request-{number}.json"
            path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            arguments = (*arguments, "--request", str(path))
        audit = self.folder / f"network-{number}.json"
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
        argv = [sys.executable, "-X", "utf8", "-B", str(ROOT / "tests/e2e/network_guard.py"), str(audit),
                str(ROOT / "src/dna_design_core/application/cli.py"), *map(str, arguments)]
        process = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", check=False)
        (self.folder / f"command-{number}.stdout.txt").write_text(process.stdout, encoding="utf-8")
        (self.folder / f"command-{number}.stderr.txt").write_text(process.stderr, encoding="utf-8")
        self.assertEqual(json.loads(audit.read_text(encoding="utf-8"))["attempts"], 0)
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        return json.loads(process.stdout)


class RequestMessageTests(PublicCLICase):
    def test_empty_goal_lists_missing_paths_and_reasons(self):
        receipt = self.command("goal", "declare", "--run", self.run_path, request={}, expected=1)
        failure = receipt["result"]["failure"]
        self.assertEqual(failure["code"], "PLAN_SCHEMA_INVALID")
        findings = failure["details"]["findings"]
        locations = {row["location"] for row in findings}
        self.assertTrue({"/schema", "/version", "/sources", "/targets", "/constraints"} <= locations, findings)
        self.assertTrue(all(row.get("reason") for row in findings), findings)
        journal = (self.run_path / "journal.ndjson").read_text(encoding="utf-8")
        self.assertNotIn('"type":"goal.declared"', journal)

    def test_missing_source_declaration_names_nested_field(self):
        source = self.folder / "synthetic.fasta"
        source.write_text(">synthetic\nACGT\n", encoding="utf-8")
        goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": "Synthetic report.",
                "sources": [{"source_id": "input", "from": str(source), "as": "artifact", "input_origin": "user_file"}],
                "declared_context": [], "targets": [{"id": "result", "role": "analysis", "required": True}],
                "constraints": [], "intents": []}
        receipt = self.command("goal", "declare", "--run", self.run_path, request=goal, expected=1)
        self.assertEqual(receipt["result"]["failure"]["code"], "PLAN_SCHEMA_INVALID")
        findings = receipt["result"]["failure"]["details"]["findings"]
        row = next((row for row in findings if row["location"] == "/sources/0/declared"), None)
        self.assertIsNotNone(row, findings)
        self.assertIn("required", row["reason"].lower())

    def construct_draft(self, *, include_handoff):
        version = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))["core"]
        targets = [("donor", "construct"), ("primers", "primer_set"), ("assay", "analysis")]
        if include_handoff:
            targets.append(("handoff", "analysis"))
        sources = [{"source_id": "input_" + name, "from": str(ROOT / "kits/construct/examples" / (filename + ".fasta")),
                    "as": "artifact", "input_origin": "user_file", "declared": {}}
                   for name, filename in (("reference", "reference"), ("cargo", "cargo"))]
        request = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": "Synthetic admission test.",
                   "sources": sources, "declared_context": [], "targets": [{"id": name, "role": role, "required": True} for name, role in targets],
                   "constraints": [{"id": "present", "check": "check.goal.output_present@" + version, "params": {},
                                    "target": "donor", "source_quote": "Report the requested donor.", "status": "active"}], "intents": []}
        declared = self.command("goal", "declare", "--run", self.run_path, request=request)
        case = json.loads((ROOT / "kits/construct/examples/case.json").read_text(encoding="utf-8"))
        settings = {**case["parameters"], **case["gibson"], "goal_digest": declared["result"]["goal_digest"],
                    "reference_source": "input_reference", "cargo_source": "input_cargo",
                    "donor_target": "donor", "primers_target": "primers", "assay_target": "assay", "handoff_target": "handoff"}
        return self.command("template", "instantiate", "construct.prepare_gibson", "--run", self.run_path,
                            request=settings)["result"]["draft"]

    def test_missing_target_names_output_and_producer_role(self):
        plan = self.construct_draft(include_handoff=False)
        receipt = self.command("pipeline", "submit", "--run", self.run_path, request=plan, expected=1)
        problems = receipt["result"]["failure"]["details"]["problems"]
        row = next(row for row in problems if row["details"]["location"] == "/outputs/3")
        self.assertEqual(row["code"], "PLAN_OUTPUT_INVALID")
        for text in ("identity_handoff", "handoff", "analysis", "add", "target"):
            self.assertIn(text, row["message"].lower())

    def test_same_template_with_all_targets_is_admitted(self):
        plan = self.construct_draft(include_handoff=True)
        receipt = self.command("pipeline", "submit", "--run", self.run_path, request=plan)
        self.assertEqual(receipt["problems"], [])


if __name__ == "__main__":
    unittest.main()
