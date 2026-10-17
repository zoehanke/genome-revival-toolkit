"""Kit contribution shape and bad-manifest controls, without executing capabilities."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from dna_design_core.catalog.kits import read
from dna_design_core.kernel.public import ToolkitError
from tests.oracles.genome_identity_metadata import export

KIT = Path(__file__).resolve().parents[2] / "kits/genome-identity"


class GenomeIdentityStructureTests(unittest.TestCase):
    def test_manifest_contributions_and_generated_contract_are_complete(self):
        manifest = read(KIT)
        for category in ("capabilities", "templates", "text"):
            self.assertEqual(set(manifest["contributes"][category]),
                             {p.relative_to(KIT).as_posix() for p in (KIT / category).glob("*.json")})
        self.assertEqual(manifest["contributes"]["knowledge"], [])
        self.assertEqual(export(check=True), {"different": []})

    def test_bad_manifest_and_missing_contribution_are_actually_rejected(self):
        manifest = read(KIT)
        with tempfile.TemporaryDirectory(prefix="s5b_bad_manifest_") as directory:
            root = Path(directory) / "kit"
            shutil.copytree(KIT, root)
            bad = deepcopy(manifest)
            bad["profiles"] = {}
            (root / "kit.json").write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ToolkitError):
                read(root)
            (root / "kit.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / manifest["contributes"]["capabilities"][0]).unlink()
            with self.assertRaises(ToolkitError):
                read(root)


if __name__ == "__main__":
    unittest.main()
