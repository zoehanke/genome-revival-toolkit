"""Keep the actual tutorial sequence in the complete local regression suite."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from e2e.run_add_a_kit import run_tutorial


class AddAKitEndToEndTests(unittest.TestCase):
    def test_tutorial_commands_portable_seal_and_single_byte_tamper(self):
        # Retain failures as well as successful runs; the test never deletes evidence.
        folder = Path(tempfile.mkdtemp(prefix="grt-add-a-kit-e2e-"))
        summary = run_tutorial(folder / "evidence")
        self.assertEqual(len(summary["copyable_blocks_executed"]), 10)
        self.assertTrue(summary["portable_verified"])
        self.assertTrue(summary["tamper_detected"])
        self.assertEqual(summary["human_review"], "NOT_PERFORMED")


if __name__ == "__main__":
    unittest.main()
