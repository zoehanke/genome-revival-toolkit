"""Pure-layer contracts; executable capability contracts are tested separately."""
import ast
import inspect
import json
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from dna_design_core.biology import public as biology

ROOT = Path(__file__).resolve().parents[2]


class BiologyContractTests(unittest.TestCase):
    def test_every_public_calculation_has_independent_answer_registration(self):
        entries = json.loads((ROOT / 'tests/fixtures/biology/oracles.json').read_text(encoding='utf-8'))['data']
        self.assertEqual(set(biology.__all__), {entry['symbol'] for entry in entries})
        for entry in entries:
            module, class_name, method = entry['test_id'].rsplit('.', 2)
            source = ROOT / 'tests/unit' / (module + '.py')
            tree = ast.parse(source.read_text(encoding='utf-8'))
            target = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name)
            self.assertIn(method, {node.name for node in target.body if isinstance(node, ast.FunctionDef)})
            self.assertIn(entry['oracle_kind'], ('construction', 'hand', 'published', 'independent_program'))
            self.assertTrue(entry['method'])

    def test_public_signatures_are_typed(self):
        for name in biology.__all__:
            function = getattr(biology, name)
            if inspect.isclass(function):
                self.assertTrue(function.__annotations__)
                continue
            signature = inspect.signature(function)
            self.assertIsNot(signature.return_annotation, inspect.Signature.empty, name)
            for parameter in signature.parameters.values():
                self.assertIsNot(parameter.annotation, inspect.Parameter.empty, name)

    def test_in_memory_algorithms_need_no_files_or_processes(self):
        with patch('builtins.open', side_effect=AssertionError('unexpected file read')), \
             patch('pathlib.Path.open', side_effect=AssertionError('unexpected path open')), \
             patch('subprocess.run', side_effect=AssertionError('unexpected process')):
            self.assertEqual(biology.calculate_tm('ACGTACGA')['tm'], '11.74530033')
            record = biology.read_fasta('>synthetic\nACGTACGA\n')
            self.assertEqual(biology.write_fasta(record), '>synthetic\nACGTACGA\n')
            self.assertEqual(biology.primer_quality('GCGAAACGC')['hairpin']['max_stem_bp'], 3)
            self.assertEqual(biology.simulate_pcr('AAACCCTTTGGG', 'TTT', 'GGG', circular=True)['sequence'], 'TTTGGGAAACCC')
            fragments = biology.digest_sequence('TTGGTCTCAAGTCCCGG', ('BsaI',), circular=True)['fragments']
            self.assertEqual(biology.ligate_fragments(fragments, circular=True)['sequence'], 'AGTCCCGGTTGGTCTCA')

    def test_7_cli_tm_references_with_fixed_print_rounding_tolerance(self):
        # Primer3 prints three decimal places. Bound fixed by serialization,
        # independent of observed differences; hand-sum tests remain separate.
        reference = json.loads((ROOT / 'tests/evidence/s1b/primer3/reference.json').read_text(encoding='utf-8'))
        self.assertEqual(reference['outcome'], 'PASS')
        self.assertEqual(len(reference['cases']), 7)
        for case in reference['cases']:
            result = biology.calculate_tm(case['sequence'], biology.TmParameters(**case['parameters']))
            delta = abs(Decimal(result['tm']) - Decimal(case['measurements']['PRIMER_LEFT_0_TM']))
            self.assertLessEqual(delta, Decimal('0.00050001'), case['id'])

    def test_boulder_parser_against_independent_cli_text(self):
        folder = ROOT / 'tests/evidence/s1b/primer3'
        parsed = biology.parse_boulder((folder / 'pair_20nt.stdout.txt').read_text(encoding='utf-8'))
        self.assertEqual(parsed['PRIMER_LEFT_0_SEQUENCE'], 'ACGTCGATGCTAGCTACGTA')
        self.assertEqual(parsed['PRIMER_RIGHT_0_SEQUENCE'], 'TAGGCTACGATTCGACGTCA')
        self.assertEqual(parsed['PRIMER_LEFT_0_GC_PERCENT'], '50.000')


if __name__ == '__main__':
    unittest.main()
