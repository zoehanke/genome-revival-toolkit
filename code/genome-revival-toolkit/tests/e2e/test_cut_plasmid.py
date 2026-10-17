"""Public-CLI B2 plus independent negative controls; unresolved seal stays visible."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from e2e.run_cut_plasmid import run_b2
from e2e.independent_check import check_output


class CutPlasmidEndToEndTests(unittest.TestCase):
    def test_public_cli_revision_reaction_readback_and_honest_seal_result(self):
        evidence = ROOT / "tests/evidence/s2"
        evidence.mkdir(parents=True, exist_ok=True)
        # Retain every attempt, including assertion failures, under the owned evidence directory.
        root = Path(tempfile.mkdtemp(prefix="b2-suite-", dir=evidence))
        self.run_retained_b2(root)

    def run_retained_b2(self, root):
        summary = run_b2(root / "b2")
        self.assertTrue(summary["initial_step_failed"])
        self.assertTrue(summary["original_goal_preserved"])
        self.assertTrue(summary["genbank_readback_equal"])
        self.assertEqual(summary["connection_attempts"], 0)
        self.assertEqual(summary["independent_sequence_and_pcr"], "PASS")
        self.assertEqual(summary["selection_status"], "UNKNOWN")
        run, candidate = Path(summary["run"]), Path(summary["candidate"])
        if summary["seal_created"]:
            self.assertTrue(summary["portable_verify_performed"])
        else:
            self.assertFalse(summary["acceptance_passed"])
            self.assertTrue(summary["unsatisfied"])
        self.assertEqual(check_output(run, candidate)["outcome"], "PASS")
        for name in ("wrong_candidate", "wrong_primer_tail"):
            wrong = root / name
            shutil.copytree(candidate, wrong)
            path = wrong / ("construct.json" if name == "wrong_candidate" else "primers.json")
            value = json.loads(path.read_text(encoding="utf-8"))
            if name == "wrong_candidate":
                sequence = value["sequence"]
                value["sequence"] = ("A" if sequence[0] != "A" else "C") + sequence[1:]
            else:
                sequence = value["primers"][1]["sequence"]
                value["primers"][1]["sequence"] = ("A" if sequence[0] != "A" else "C") + sequence[1:]
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.subTest(negative=name), self.assertRaises(ValueError):
                check_output(run, wrong)


if __name__ == "__main__":
    unittest.main()
