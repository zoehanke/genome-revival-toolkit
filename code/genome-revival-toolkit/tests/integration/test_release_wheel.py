"""Offline PEP 517 build tests, without the checkout on the Python search path."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from release_fixture import source_tree


class ReleaseWheelTests(unittest.TestCase):
    def build_wheel(self, source, output):
        output.mkdir()
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        program = ("import os,sys; os.chdir(sys.argv[1]); sys.path=[p for p in sys.path if p]; "
                   "from setuptools.build_meta import build_wheel; build_wheel(sys.argv[2])")
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c", program, str(source), str(output)],
                                cwd=output, env=env, text=True, encoding="utf-8", capture_output=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return next(output.glob("*.whl"))

    def fixture(self, path):
        source = source_tree(path)
        for name in ("pyproject.toml", "ship.json"):
            shutil.copyfile(ROOT / name, source / name)
        # A synthetic Kit-shaped data directory proves that non-Python payload travels too.
        kit = source / "kits/synthetic-install-fixture"
        kit.mkdir(parents=True)
        (kit / "example.txt").write_text("Synthetic packaging bytes, not a scientific Kit.\n", encoding="utf-8")
        return source

    def test_backend_locates_build_module_and_ships_exact_payload_without_source_path(self):
        with tempfile.TemporaryDirectory(prefix="s4b_wheel_") as folder:
            root = Path(folder)
            source = self.fixture(root / "source")
            wheel = self.build_wheel(source, root / "wheel")
            with zipfile.ZipFile(wheel) as archive:
                value = json.loads(archive.read("dna_design_core/release-manifest.json"))
                listed = {row["path"]: row for row in value["files"]}
                self.assertIn("kits/synthetic-install-fixture/example.txt", listed)
                for name, row in listed.items():
                    data = archive.read("dna_design_core/" + name.removeprefix("src/dna_design_core/"))
                    self.assertEqual(len(data), row["bytes"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
                self.assertIn("dna_design_core/resources/VERSIONS.json", archive.namelist())

    def test_wheel_preserves_supplied_zip_manifest_instead_of_regenerating_identity(self):
        with tempfile.TemporaryDirectory(prefix="s4b_zip_wheel_") as folder:
            root = Path(folder)
            source = self.fixture(root / "source")
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tools/build_release.py"),
                                      "--root", str(source), "--out", str(root / "zip"), "--build-id", "synthetic-zip-fixture"],
                                     capture_output=True, text=True, encoding="utf-8", timeout=90)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            built = json.loads(process.stdout)
            with zipfile.ZipFile(root / "zip" / built["archive"]) as archive:
                original = archive.read("release-manifest.json")
                archive.extractall(root / "extracted")
            wheel = self.build_wheel(root / "extracted", root / "wheel")
            with zipfile.ZipFile(wheel) as archive:
                self.assertEqual(archive.read("dna_design_core/release-manifest.json"), original)
            self.assertEqual(hashlib.sha256(original).hexdigest(), built["release_id"])


if __name__ == "__main__":
    unittest.main()
