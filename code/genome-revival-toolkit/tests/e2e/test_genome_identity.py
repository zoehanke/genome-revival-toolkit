"""Public CLI test, including portable seal verification and a real failed run."""
from pathlib import Path
import tempfile
import unittest

from tests.e2e.run_genome_identity import run


class GenomeIdentityCliTests(unittest.TestCase):
    def test_public_cli_and_copied_seal(self):
        with tempfile.TemporaryDirectory(prefix="s5b_e2e_") as directory:
            result = run(Path(directory) / "evidence")
        self.assertTrue(result["cases"]["different_sizes"]["verified"])
        self.assertTrue(result["cases"]["handoff_hash"]["seal_refused"])
        self.assertEqual(result["connection_attempts"], 0)


if __name__ == "__main__":
    unittest.main()
