"""Execute each declared CHECK fixture through S1 Invoker and real stored inputs."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
from biology_runtime import action_case, check_view, retained
from dna_design_core.catalog.registry import Catalog
from dna_design_core.kernel import schemas


class BiologyCheckTests(unittest.TestCase):
    def test_every_declared_pass_and_fail_fixture_actually_runs(self):
        catalog = Catalog()
        checks = [value for value in catalog.describe('checks') if value['source']['implemented_in'].startswith('dna_design_core.capabilities.builtin.check.biology:')]
        self.assertEqual({value['id'] for value in checks}, {'check.primer_quality', 'check.format_roundtrip', 'check.pcr_product', 'check.assembly_product'})
        evidence = []
        for declaration in checks:
            for variant in ('pass', 'fail'):
                with self.subTest(check=declaration['id'], variant=variant), tempfile.TemporaryDirectory() as directory:
                    fixture = json.loads((ROOT / declaration['fixtures'][variant]).read_text(encoding='utf-8'))
                    data = fixture['data']
                    session, invoker = action_case(directory, data['use'], data['inputs'], data['params'])
                    params = {}
                    if declaration['id'] == 'check.primer_quality':
                        identity = session.steps()['m1']['completed']['payload']['outputs']['materials']['material'][0]
                        params = {'material_ids': [identity], 'limits': data['limits']}
                    events = session.events()
                    if data.get('corrupt') == 'genbank_visible_sequence':
                        artifact = retained(session)['artifacts'][0]
                        text = artifact.read_text(encoding='utf-8')
                        header, separator, body = text.partition('ORIGIN\n')
                        self.assertTrue(separator)
                        prefix, last_g, suffix = body.rpartition('g')
                        self.assertEqual(last_g, 'g')
                        artifact.write_text(header + separator + prefix + 'a' + suffix, encoding='utf-8', newline='\n')
                    elif data.get('corrupt') == 'recorded_product':
                        completed = next(event for event in events if event['type'] == 'step.completed' and event['payload']['step_id'] == 'target')
                        identity = completed['payload']['outputs']['materials']['product'][0]
                        value = session.store.get('materials', identity)
                        value['sequence'] = data['wrong_sequence']
                        completed['payload']['outputs']['materials']['product'] = [session.store.put('materials', value)]
                    view = check_view(session, events)
                    before = {path.relative_to(session.root).as_posix(): path.read_bytes() for path in session.root.rglob('*') if path.is_file()}
                    result = invoker.invoke(declaration['id'], {}, params, parent='final', view=view)
                    self.assertFalse(result.products or result.documents or result.artifacts or result.values or result.unverified)
                    self.assertEqual(len(result.verdicts), 1)
                    verdict = result.verdicts[0]
                    schemas.require('verdict-v1', verdict)
                    self.assertEqual(verdict['outcome'], fixture['expected'])
                    if variant == 'fail':
                        self.assertNotEqual(verdict['outcome'], 'PASS')
                    self.assertEqual(verdict['check']['id'], declaration['id'])
                    self.assertEqual(before, {path.relative_to(session.root).as_posix(): path.read_bytes() for path in session.root.rglob('*') if path.is_file()})
                    evidence.append({'check': declaration['id'], 'fixture': declaration['fixtures'][variant], 'expected': fixture['expected'], 'actual': verdict['outcome'], 'invoker_used': True})
        folder = ROOT / 'tests/evidence/s1b/integration'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'check-fixtures.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8', newline='\n')

    def test_missing_quality_limits_is_unknown_and_no_reaction_is_not_applicable(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = json.loads((ROOT / 'tests/fixtures/biology/checks/check.primer_quality.pass.json').read_text())['data']
            session, invoker = action_case(directory, fixture['use'], fixture['inputs'], fixture['params'])
            view = check_view(session)
            identity = session.steps()['m1']['completed']['payload']['outputs']['materials']['material'][0]
            # S1c auto-discovery with no marked subject is N/A. Keep this
            # missing-limits negative by explicitly selecting its primer.
            self.assertEqual(invoker.invoke('check.primer_quality', {}, {'material_ids':[identity]}, parent='final', view=view).verdicts[0]['outcome'], 'UNKNOWN')
            invalid = {'material_ids': [identity], 'limits': {**fixture['limits'], 'gc_min': 'bad'}}
            self.assertEqual(invoker.invoke('check.primer_quality', {}, invalid, parent='final', view=view).verdicts[0]['outcome'], 'UNKNOWN')
            verdict = invoker.invoke('check.pcr_product', {}, {}, parent='final', view=view).verdicts[0]
            self.assertEqual(verdict['outcome'], 'NOT_APPLICABLE')
            self.assertTrue(verdict['applicability']['basis'])


if __name__ == '__main__':
    unittest.main()
