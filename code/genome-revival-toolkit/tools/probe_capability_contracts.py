"""Run the three unchanged contract assertions with explicitly supplied Kit roots."""
import argparse
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'tests'))
from dna_design_core.catalog.registry import Catalog
from structure.test_runtime_contracts import RuntimeStructureTests
from unit.test_capabilities import CapabilityTests


def probe(kit_dirs):
    catalog=Catalog(kit_dirs)
    if catalog.problems:raise AssertionError(catalog.problems)
    assertions=[RuntimeStructureTests().test_atomic_capabilities_do_not_call_other_capabilities,
                RuntimeStructureTests().test_verdict_constructor_and_exception_boundary,
                CapabilityTests().test_generated_declarations_match_decorator_exports]
    suite=unittest.TestSuite(unittest.FunctionTestCase(lambda method=method:method(catalog),description=method.__name__) for method in assertions)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--kit-dir',action='append',type=Path,required=True)
    args=parser.parse_args();raise SystemExit(not probe(args.kit_dir).wasSuccessful())
