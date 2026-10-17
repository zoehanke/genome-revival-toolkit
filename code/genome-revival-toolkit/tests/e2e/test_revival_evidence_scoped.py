"""Five existing cases plus all S3b rows execute through the public CLI."""
import os
from pathlib import Path
import tempfile
import unittest

from tests.e2e.run_revival_evidence import run_examples


class ScopedEvidenceCLI(unittest.TestCase):
    def test_scoped_count_rows_and_existing_cases_seal_and_verify_after_copy(self):
        retained = os.environ.get("GRT_S3B_EVIDENCE")
        if retained:
            output = Path(retained)
        else:
            temporary = tempfile.TemporaryDirectory(prefix="s3b_cli_")
            self.addCleanup(temporary.cleanup)
            output = Path(temporary.name) / "examples"
        summary = run_examples(output, scoped=True)
        self.assertEqual(len(summary["cases"]), 11)
        self.assertEqual(summary["commands"], 99)
        self.assertEqual(summary["connection_attempts"], 0)
        self.assertTrue(all(row["verify"] for row in summary["cases"].values()))


if __name__ == "__main__":
    unittest.main()
