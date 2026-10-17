"""Automatic primer subjects and declared criteria; no invented thermal limits."""
import json
import math
from pathlib import Path
import tempfile
import unittest
from dna_design_core.application import api
from tests.s1c_reaction_runtime import prepare
from tests.s1c_runtime import material,run_material


class AutomaticPrimerQualityTests(unittest.TestCase):
    def test_explicit_nn_window_is_enforced_with_hand_computed_annealing_tm(self):
        # AACT: AA/TT + AC/TG + CT/GA = -24.1/-65.6; NN3
        # terminal A/T = +4.6/+8.2, effective strand 250 nM, Na 50 mM.
        expected_tm=-19500/(-57.4+.368*3*math.log(.05)+1.987*math.log(250e-9))-273.15
        for window,expected in [(('-200','200'),'PASS'),(('100','101'),'FAIL')]:
            with self.subTest(window=window),tempfile.TemporaryDirectory() as folder:
                root,kit,call,service=prepare(folder,thermal_window=window)
                judged=call('judge');self.assertEqual(judged['problems'],[],judged)
                verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='check.primer_quality')
                self.assertEqual(verdict['outcome'],expected,verdict)
                first=verdict['evidence']['primers'][0]
                self.assertAlmostEqual(float(first['annealing_tm']['tm']),expected_tm,places=8)
                self.assertNotIn('Thermal acceptance was not assessed: no temperature window and concentrations were supplied.',verdict['does_not_establish'])

    def test_recorded_length_passes_but_document_core_length_tamper_fails(self):
        for wrong,expected in [(False,'PASS'),(True,'FAIL')]:
            with self.subTest(wrong_core=wrong),tempfile.TemporaryDirectory() as folder:
                root,kit,call,service=prepare(folder,wrong_length=wrong)
                judged=call('judge');self.assertEqual(judged['problems'],[],judged)
                verdict=next(r['verdict'] for r in judged['result']['verdicts'] if r['verdict']['check']['id']=='check.primer_quality')
                self.assertEqual(verdict['outcome'],expected,verdict)
                self.assertIn('Thermal acceptance was not assessed: no temperature window and concentrations were supplied.',verdict['does_not_establish'])

    def test_construct_can_seal_length_only_and_records_thermal_limit(self):
        from tests.construct_runtime import create
        with tempfile.TemporaryDirectory() as folder:
            service,receipts,execution=create(folder,'pcr');self.assertEqual(execution['state'],'COMPLETED')
            sealed=api.call('seal',root=service.root);self.assertEqual(sealed['problems'],[],sealed)
            self.assertTrue(sealed['result']['sealed'],sealed)
            package=Path(sealed['result']['manifest']).parent;manifest=json.loads((package/'manifest.json').read_text(encoding='utf-8'))
            note='Thermal acceptance was not assessed: no temperature window and concentrations were supplied.'
            self.assertIn(note,manifest['not_verified']);self.assertIn(note,(package/'views/report.md').read_text(encoding='utf-8'))

    def test_no_marked_primers_is_not_applicable_with_basis(self):
        with tempfile.TemporaryDirectory() as folder:
            root,kit,call,judged,verdicts=run_material(folder,material(),checks=['check.primer_quality'])
            verdict=verdicts['check.primer_quality'];self.assertEqual(verdict['outcome'],'NOT_APPLICABLE',verdict)
            self.assertTrue(verdict['applicability']['basis'])


if __name__=='__main__':unittest.main()
