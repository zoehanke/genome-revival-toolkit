"""Exercise the actual optional integration test under both configuration states."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration import test_biology_capabilities as capabilities
from dna_design_core.engine.invoker import Context


class RegisteredPrimer3SkipTests(unittest.TestCase):
    def test_no_configuration_is_one_registered_skip_and_zero_passes(self):
        result = unittest.TestResult()
        with patch.dict(os.environ, {"GRT_PRIMER3_CORE": ""}):
            capabilities.CapabilityTests("test_primer3_real_ctx_external_calls_and_recorded_fingerprint").run(result)
        self.assertEqual((result.testsRun, len(result.skipped), len(result.failures), len(result.errors)), (1, 1, 0, 0))
        self.assertEqual(result.testsRun - len(result.skipped), 0)
        self.assertIn("S1B-PRIMER3-OPTIONAL", result.skipped[0][1])
        self.assertIn("NOT_PERFORMED; not PASS", result.skipped[0][1])

    def test_configured_wrong_fingerprint_is_failure_not_skip(self):
        def wrong_report(case, *arguments, **parameters):
            Context.run_external(object(), ["configured.exe", "--about"])
            Context.run_external(object(), ["configured.exe", "--strict_tags", "fixture.txt"])
            return None, None, {"documents": {"report": {"backend": {"version": "2.6.1", "sha256": "0" * 64},
                "measurements": {"PRIMER_LEFT_0_TM": "11.745"}}}}
        result = unittest.TestResult()
        with patch.dict(os.environ, {"GRT_PRIMER3_CORE": "configured.exe"}), \
             patch.object(Context, "run_external", lambda *args: None), \
             patch.object(capabilities.CapabilityTests, "run_action", wrong_report):
            capabilities.CapabilityTests("test_primer3_real_ctx_external_calls_and_recorded_fingerprint").run(result)
        self.assertEqual((len(result.skipped), len(result.failures), len(result.errors)), (0, 1, 0))
        self.assertIn("19a546a0166fd979", result.failures[0][1])


if __name__ == "__main__":
    unittest.main()
