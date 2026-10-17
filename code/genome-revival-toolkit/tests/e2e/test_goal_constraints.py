from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests'))
from e2e.run_s1_followup import run_case


class GoalConstraintTests(unittest.TestCase):
    def test_goal_schema_recovery_names_the_goal_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(run_case('schema_recovery',Path(directory)/'schema_recovery')['passed'])

    def test_fields_constraint_allows_b1_seal(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(run_case('fields',Path(directory)/'fields')['passed'])

    def test_missing_document_field_is_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(run_case('fields_missing',Path(directory)/'fields_missing')['passed'])

    def test_constraint_parameters_are_rejected_during_goal_declaration(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(run_case('invalid_params',Path(directory)/'invalid_params')['passed'])

    def test_request_origin_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(run_case('origin',Path(directory)/'origin')['passed'])


if __name__=='__main__':unittest.main()
