from pathlib import Path
import tempfile
import unittest
from e2e.run_s1_followup2 import run_case


class Followup2CliTests(unittest.TestCase):
    def test_inline_document_cli(self):
        with tempfile.TemporaryDirectory() as folder:self.assertTrue(run_case('inline',Path(folder)/'case')['passed'])

    def test_frozen_knowledge_cli(self):
        with tempfile.TemporaryDirectory() as folder:self.assertTrue(run_case('knowledge',Path(folder)/'case')['passed'])

    def test_model_convention_cli(self):
        with tempfile.TemporaryDirectory() as folder:self.assertTrue(run_case('model',Path(folder)/'case')['passed'])

    def test_materials_cli(self):
        with tempfile.TemporaryDirectory() as folder:self.assertTrue(run_case('materials',Path(folder)/'case')['passed'])

    def test_external_loader_cli(self):
        with tempfile.TemporaryDirectory() as folder:self.assertTrue(run_case('loader',Path(folder)/'case')['passed'])


if __name__=='__main__':unittest.main()
