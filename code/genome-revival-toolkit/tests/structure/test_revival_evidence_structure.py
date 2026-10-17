"""Kit boundaries, checked without importing any Kit implementation."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "kits/revival-evidence"


class EvidenceStructure(unittest.TestCase):
    def test_python_is_confined_to_capabilities_and_public_imports(self):
        for path in KIT.rglob("*.py"):
            self.assertTrue(path.is_relative_to(KIT / "capabilities"))
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("dna_design_core"):
                    self.assertEqual(node.module, "dna_design_core.kernel.public")
                if isinstance(node, ast.Name):
                    self.assertNotIn(node.id, {"Molecule", "argparse", "hashlib"})
                if isinstance(node, ast.FunctionDef):
                    self.assertNotIn(node.name, {"main", "render_report", "render_card"})


if __name__ == "__main__":
    unittest.main()
