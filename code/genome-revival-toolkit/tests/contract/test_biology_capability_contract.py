"""Decorator/export/signature/Outcome contracts for the new S1b capabilities."""
import importlib
import inspect
import json
from pathlib import Path
import unittest

from dna_design_core.catalog.registry import Catalog
from dna_design_core.kernel import schemas
from dna_design_core.kernel.public import core_version

ROOT = Path(__file__).resolve().parents[2]


class BiologyCapabilityContractTests(unittest.TestCase):
    def declarations(self):
        return [value for value in Catalog().describe('capabilities') if value['source']['implemented_in'].split(':')[0] in {
            'dna_design_core.capabilities.builtin.' + name for name in (
                'format.operations', 'seq.operations', 'primer.operations', 'primer.backend', 'pcr.operations',
                'restriction.operations', 'assembly.operations', 'check.biology')}]

    def test_exported_json_matches_decorator_and_schema(self):
        declarations = self.declarations()
        self.assertEqual(len(declarations), 22)
        for declaration in declarations:
            schemas.require('capability-v1', declaration)
            module, function = declaration['source']['implemented_in'].split(':')
            implementation = getattr(importlib.import_module(module), function)
            self.assertEqual(implementation.declaration, declaration)
            self.assertEqual(declaration['version'], core_version())
            self.assertTrue(declaration['does_not_establish'])
            self.assertEqual(json.loads((ROOT / 'src/dna_design_core/resources/capabilities' / (declaration['id'] + '.json')).read_text()), declaration)

    def test_declarations_match_full_typed_signatures(self):
        for declaration in self.declarations():
            module, function = declaration['source']['implemented_in'].split(':')
            signature = inspect.signature(getattr(importlib.import_module(module), function))
            inputs = {port['name'] for port in declaration['inputs']}
            params = set(declaration['params']['properties'])
            self.assertEqual(set(signature.parameters) - {'ctx'}, inputs | params, declaration['id'])
            for name, parameter in signature.parameters.items():
                self.assertIsNot(parameter.annotation, inspect.Parameter.empty, (declaration['id'], name))
                if name == 'ctx':
                    continue
                required = next((port['required'] for port in declaration['inputs'] if port['name'] == name), name in declaration['params']['required'])
                self.assertEqual(parameter.default is inspect.Parameter.empty, required, (declaration['id'], name))
            self.assertIsNot(signature.return_annotation, inspect.Signature.empty)

    def test_each_capability_has_independent_answer_or_executed_check_fixtures(self):
        registry = json.loads((ROOT / 'tests/fixtures/biology/capability-oracles.json').read_text())['data']
        self.assertEqual(set(registry), {value['id'] for value in self.declarations()})
        for declaration in self.declarations():
            entry = registry[declaration['id']]
            self.assertIn(entry['kind'], ('hand', 'construction', 'independent_program'))
            self.assertTrue(entry['test_id'])
            if declaration['role'] == 'CHECK':
                for variant in ('pass', 'fail'):
                    fixture = json.loads((ROOT / declaration['fixtures'][variant]).read_text())
                    self.assertEqual(fixture['expected'], 'PASS' if variant == 'pass' else 'FAIL')


if __name__ == '__main__':
    unittest.main()
