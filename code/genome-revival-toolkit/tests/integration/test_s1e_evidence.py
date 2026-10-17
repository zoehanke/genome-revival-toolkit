"""S1e's user-decided local inference boundary through the real CLI."""
import os
from pathlib import Path
import tempfile
import unittest

from tests.revival_s1e import EvidenceRun


class S1eEvidenceTests(unittest.TestCase):
    def evidence_run(self):
        retained = os.environ.get("GRT_S1E_EVIDENCE")
        if retained:
            folder = Path(retained) / self._testMethodName
        else:
            temporary = tempfile.TemporaryDirectory(prefix="s1e_cli_")
            self.addCleanup(temporary.cleanup)
            folder = Path(temporary.name) / "case"
        return EvidenceRun(folder)

    def test_negative_without_controls_is_insufficient_not_contradicted(self):
        run = self.evidence_run()
        run.prepare(count=1, result="negative", controls=None)
        result = run.complete()
        self.assertEqual(result["status"], "INSUFFICIENT")
        self.assertIn("reaction failure", result["reason"].lower())

    def test_invalid_control_status_lists_choices_and_still_cannot_seal(self):
        run = self.evidence_run()
        run.prepare(count=1, result="positive", band=80, controls="pass")
        receipt = run.command("run", "execute", "--run", run.root, expected=1)
        failure = receipt["result"]["failure"]
        self.assertEqual(failure["code"], "PLAN_PARAM_INVALID")
        run.command("seal", "--run", run.root, expected=1)
        self.assertFalse((run.root / "sealed").exists())
        for choice in ("passed", "failed", "unknown"):
            self.assertIn(choice, failure["message"])

    def test_only_result_draft_is_a_submittable_pipeline(self):
        run = self.evidence_run()
        run.prepare(count=1, result="positive", band=80, controls="passed", submit=False)
        rejected = run.command("pipeline", "submit", "--run", run.root, request=run.template_receipt, expected=1)
        self.assertEqual(rejected["result"]["failure"]["code"], "PLAN_SCHEMA_INVALID")
        run.command("pipeline", "submit", "--run", run.root, request=run.template_receipt["result"]["draft"])
        self.assertEqual(run.complete()["status"], "SUPPORTED")


if __name__ == "__main__":
    unittest.main()
