"""S2b selection through public CLI commands on constructed GenBank inputs."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from cut_plasmid_runtime import write_material

CLI = ROOT / "src/dna_design_core/application/cli.py"
GUARD = ROOT / "tests/e2e/network_guard.py"
YEAST = {"organism": "S. cerevisiae", "existing_markers": [], "auxotrophies": []}
# Exact task text, independent of the knowledge file under test.
ZEOCIN_PLATE = (
    "YPD or minimal medium + Zeocin (reported working range 50–300 µg/mL; "
    "the lowest effective dose depends on strain, pH and ionic strength, so "
    "determine it with a kill curve; test medium pH 6.5–8). Electroporated cells: "
    "YPD + 1 M sorbitol. Do not plate spheroplasts directly onto Zeocin medium."
)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def run_selection(directory, label, genotype):
    """Retain every CLI attempt, including failed commands, outside source files."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    run, receipts = directory / "run", []
    # ATG AAA TAA is a complete synthetic CDS, not a functional resistance gene.
    vector = {"sequence": "ATGAAATAACCC", "topology": "circular", "features": []}
    if label is not None:
        vector["features"] = [{"start": 0, "end": 9, "strand": 1, "type": "CDS", "label": label}]
    write_material(directory / "vector.gb", vector)

    def command(*arguments):
        number = len(receipts) + 1
        audit = directory / (f"command-{number}.network.json")
        argv = [sys.executable, "-X", "utf8", "-B", str(GUARD), str(audit), str(CLI), *map(str, arguments)]
        result = subprocess.run(argv, cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=180)
        (directory / f"command-{number}.stdout.json").write_text(result.stdout, encoding="utf-8")
        (directory / f"command-{number}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        receipts.append({"argv": argv, "exit_code": result.returncode})
        write_json(directory / "commands.json", receipts)
        assert result.returncode == 0, (arguments, result.returncode, result.stdout, result.stderr, str(directory))
        assert json.loads(audit.read_text(encoding="utf-8"))["attempts"] == 0
        return json.loads(result.stdout)

    described = command("describe", "checks")
    versions = {row["id"]: row["version"] for row in described["result"]["description"]}
    command("run", "create", run)
    goal = {
        "schema": "goal-v1", "version": 1, "parent_digest": None,
        "original_request": "Report selection for a synthetic plasmid.",
        "sources": [{"source_id": "vector", "from": str(directory / "vector.gb"),
                     "input_origin": "user_file", "as": "artifact", "declared": {}}],
        "declared_context": [], "targets": [{"id": "selection", "role": "analysis", "required": True}],
        "constraints": [{"id": "present", "check": "check.goal.output_present@" + versions["check.goal.output_present"],
                         "params": {}, "target": "selection", "status": "active", "source_quote": "Report selection"}],
        "intents": [],
    }
    declared = command("goal", "declare", "--run", run, "--request", write_json(directory / "goal.json", goal))
    plan = {
        "schema": "pipeline-v1", "version": 1, "goal_digest": declared["result"]["goal_digest"],
        "steps": [
            {"step_id": "read", "use": "format.read_genbank", "inputs": {"file": {"source": "vector"}},
             "params": {"strandedness": "double"}, "why": "Read the constructed synthetic GenBank file."},
            {"step_id": "selection", "use": "cut_plasmid.assess_selection",
             "inputs": {"vector": {"step": "read", "port": "material"}},
             "params": {} if genotype is None else {"strain_genotype": genotype},
             "why": "Interpret marker annotations with only the explicitly supplied genotype."},
        ],
        "outputs": [{"name": "selection", "from": {"step": "selection", "port": "selection"}, "target": "selection"}],
    }
    command("pipeline", "submit", "--run", run, "--request", write_json(directory / "plan.json", plan))
    executed = command("run", "execute", "--run", run)
    assert executed["state"] == "COMPLETED", executed
    command("judge", "--run", run)
    candidate = max((run / "candidate").iterdir(), key=lambda path: int(path.name))
    report = json.loads((candidate / "selection.json").read_text(encoding="utf-8"))
    write_json(directory / "selection.json", report)
    return report


class CutPlasmidSelectionCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Keep failing and passing runs available for inspection after unittest exits.
        cls.directory = Path(tempfile.mkdtemp(prefix="grt-s2b-cli-"))
        print("S2b CLI evidence: " + str(cls.directory), flush=True)

    def test_ble_with_declared_yeast_genotype_has_exact_zeocin_plate_and_warning(self):
        report = run_selection(self.directory / "ble-declared", "BleoR", YEAST)
        self.assertEqual(report["status"], "DECLARED_COMPATIBLE")
        self.assertEqual([marker["marker_id"] for marker in report["markers"]], ["ble"])
        option = report["markers"][0]["plate_options"][0]
        self.assertEqual(option["plate"], ZEOCIN_PLATE)
        self.assertEqual(option["rule_id"], "selection.ble.yeast")
        self.assertIn("Do not plate spheroplasts directly onto Zeocin medium.", option["plate"])

    def test_ble_without_genotype_is_unknown_without_plate_options(self):
        report = run_selection(self.directory / "ble-missing", "BleoR", None)
        self.assertEqual(report["status"], "UNKNOWN")
        self.assertEqual(report["genotype_source"], "NOT_PROVIDED")
        self.assertEqual([marker["marker_id"] for marker in report["markers"]], ["ble"])
        self.assertEqual(report["markers"][0]["compatibility"], "UNKNOWN")
        self.assertEqual(report["markers"][0]["plate_options"], [])

    def test_unmarked_plasmid_keeps_unknown_without_plate_options(self):
        report = run_selection(self.directory / "unmarked", None, YEAST)
        self.assertEqual(report["status"], "UNKNOWN")
        self.assertEqual(report["markers"], [])
        self.assertEqual(report["annotation_conflicts"], [])
        self.assertEqual(report["unmapped_markers"], [])

    def test_existing_leu2_mapping_keeps_its_plate(self):
        genotype = deepcopy(YEAST)
        genotype["auxotrophies"] = ["leu2"]
        report = run_selection(self.directory / "leu2", "LEU2", genotype)
        self.assertEqual(report["status"], "DECLARED_COMPATIBLE")
        self.assertEqual([marker["marker_id"] for marker in report["markers"]], ["leu2"])
        self.assertEqual(report["markers"][0]["plate_options"][0]["plate"], "Synthetic defined medium without leucine")


if __name__ == "__main__":
    unittest.main()
