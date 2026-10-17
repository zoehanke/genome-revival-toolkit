"""Build metadata offline in a temporary copy, without creating or installing an environment."""
import email
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ReleaseMetadataTests(unittest.TestCase):
    def test_actual_backend_reads_a_changed_single_version_source(self):
        with tempfile.TemporaryDirectory(prefix="s4a_metadata_") as directory:
            root = Path(directory)
            for name in ("pyproject.toml", "README.md", "LICENSE", "VERSIONS.json"):
                shutil.copyfile(ROOT / name, root / name)
            (root / "tools").mkdir()
            for name in ("__init__.py", "build_release.py"):
                shutil.copyfile(ROOT / "tools" / name, root / "tools" / name)
            (root / "src/dna_design_core").mkdir(parents=True)
            (root / "src/dna_design_core/__init__.py").write_text("", encoding="utf-8")
            value = json.loads((root / "VERSIONS.json").read_text())
            value["toolkit"] = "0.0.7"
            (root / "VERSIONS.json").write_text(json.dumps(value), encoding="utf-8")
            (root / "metadata").mkdir()
            environment = dict(os.environ)
            environment.pop("PYTHONPATH", None)
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c",
                "from setuptools.build_meta import prepare_metadata_for_build_wheel; prepare_metadata_for_build_wheel('metadata')"],
                cwd=root, env=environment, capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            files = list((root / "metadata").rglob("METADATA"))
            self.assertEqual(len(files), 1)
            metadata = email.message_from_string(files[0].read_text(encoding="utf-8"))
            self.assertEqual(metadata["Version"], "0.0.7")


if __name__ == "__main__":
    unittest.main()
