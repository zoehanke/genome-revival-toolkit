"""Public CLI identity tests against independently constructed package files."""
import base64
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def packaged_fixture(root):
    """A literal installed layout, not output produced by the wheel builder under test."""
    package = root / "dna_design_core"
    shutil.copytree(ROOT / "src/dna_design_core", package, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(ROOT / "VERSIONS.json", package / "resources/VERSIONS.json")
    files = []
    for path in sorted(package.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            files.append({"path": "src/dna_design_core/" + path.relative_to(package).as_posix(),
                          "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    value = {"versions": json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8")),
             "build_id": "synthetic-install-identity", "files": files, "dependencies": {}}
    # All fixture fields are ASCII and integral: this hand-written canonical form is JCS.
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest = package / "release-manifest.json"
    manifest.write_bytes(data)
    metadata = root / "genome_revival_toolkit-0.0.0.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text("Metadata-Version: 2.1\nName: genome-revival-toolkit\nVersion: 0.0.0\n", encoding="utf-8")
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
    with (metadata / "RECORD").open("w", encoding="utf-8", newline="") as stream:
        csv.writer(stream).writerow(["dna_design_core/release-manifest.json", "sha256=" + digest, len(data)])
    return manifest, hashlib.sha256(data).hexdigest()


class ReleaseIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="s4b_身份_")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def cli(self, *arguments, package=None):
        env = dict(os.environ)
        env.pop("PYTHONHOME", None)
        env["PYTHONPATH"] = str(package or ROOT / "src")
        process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", *map(str, arguments)],
                                 cwd=self.root, env=env, text=True, encoding="utf-8", capture_output=True, timeout=60)
        return process.returncode, json.loads(process.stdout)

    def test_development_tree_still_records_dev_tree(self):
        run = self.root / "development"
        code, receipt = self.cli("run", "create", run)
        self.assertEqual(code, 0, receipt)
        event = json.loads((run / "journal.ndjson").read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["payload"]["release_id"], "dev-tree")

    def test_source_build_metadata_is_not_an_installed_release(self):
        # Setuptools leaves .egg-info next to source modules when building a wheel.
        # Construct that documented source layout without using the builder under test.
        development = self.root / "development-tree"
        source = development / "src"
        shutil.copytree(ROOT / "src/dna_design_core", source / "dna_design_core",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copyfile(ROOT / "VERSIONS.json", development / "VERSIONS.json")
        (development / "pyproject.toml").write_text('[project]\nname="genome-revival-toolkit"\nversion="0.0.0"\n', encoding="utf-8")
        metadata = source / "genome_revival_toolkit.egg-info"
        metadata.mkdir()
        (metadata / "PKG-INFO").write_text("Metadata-Version: 2.1\nName: genome-revival-toolkit\nVersion: 0.0.0\n", encoding="utf-8")
        (metadata / "SOURCES.txt").write_text("src/dna_design_core/__init__.py\n", encoding="utf-8")
        run = self.root / "after-wheel-build"
        code, receipt = self.cli("run", "create", run, package=source)
        self.assertEqual(code, 0, receipt)
        self.assertEqual(receipt["result"]["release_id"], "dev-tree")

    def test_package_records_manifest_digest_and_detects_one_byte_change(self):
        site = self.root / "site"
        manifest, expected = packaged_fixture(site)
        run = self.root / "installed"
        code, receipt = self.cli("run", "create", run, package=site)
        self.assertEqual(code, 0, receipt)
        self.assertEqual(receipt["result"]["release_id"], expected)
        event = json.loads((run / "journal.ndjson").read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["payload"]["release_id"], expected)
        info = json.loads((run / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(info["release_id"], expected)
        data = manifest.read_bytes()
        manifest.write_bytes(data.replace(b"synthetic-install-identity", b"synthetic-install-identitX", 1))
        bad_run = self.root / "modified"
        code, receipt = self.cli("run", "create", bad_run, package=site)
        self.assertEqual(code, 1, receipt)
        self.assertEqual(receipt["problems"][0]["code"], "SOURCE_CHANGED")
        self.assertIn("manifest", receipt["problems"][0]["message"].lower())
        self.assertFalse((bad_run / "run.json").exists())

    def test_installed_seal_verifies_portably_but_different_release_is_rejected(self):
        site = self.root / "site"
        manifest, expected = packaged_fixture(site)
        run = self.root / "run"

        def command(*arguments):
            code, receipt = self.cli(*arguments, package=site)
            self.assertEqual(code, 0, receipt)
            return receipt["result"]

        def request(name, value):
            path = self.root / name
            path.write_text(json.dumps(value), encoding="utf-8")
            return path

        command("run", "create", run)
        version = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))["core"]
        goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": "Report a reverse complement.",
                "sources": [], "declared_context": [], "targets": [{"id": "t1", "role": "analysis", "required": True}],
                "constraints": [{"id": "present", "check": "check.goal.output_present@" + version, "params": {},
                                 "target": "t1", "source_quote": "Report", "status": "active"}], "intents": []}
        declared = command("goal", "declare", "--run", run, "--request", request("goal.json", goal))
        pipeline = {"schema": "pipeline-v1", "version": 1, "goal_digest": declared["goal_digest"],
                    "steps": [{"step_id": "rc", "use": "seq.reverse_complement", "inputs": {"sequence": {"literal": "AGTCAGAA"}},
                               "params": {}, "why": "Compute a synthetic reverse complement."}],
                    "outputs": [{"name": "result", "from": {"step": "rc", "port": "result"}, "target": "t1"}]}
        command("pipeline", "submit", "--run", run, "--request", request("pipeline.json", pipeline))
        command("run", "execute", "--run", run)
        sealed = Path(command("seal", "--run", run)["manifest"]).parent
        portable = self.root / "portable" / sealed.name
        shutil.copytree(sealed, portable)
        run.rename(self.root / "retained")
        result = command("verify", portable)
        self.assertTrue(result["verified"])
        self.assertEqual(json.loads((portable / "result.json").read_text(encoding="utf-8")), {"sequence": "TTCTGACT"})
        self.assertEqual(json.loads((portable / "manifest.json").read_text(encoding="utf-8"))["release_id"], expected)

        # A second, internally intact installation has a deliberately different build identity.
        data = manifest.read_bytes().replace(b"synthetic-install-identity", b"different-install-identity")
        manifest.write_bytes(data)
        record = next(site.glob("*.dist-info/RECORD"))
        hashed = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
        with record.open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream).writerow(["dna_design_core/release-manifest.json", "sha256=" + hashed, len(data)])
        code, receipt = self.cli("verify", portable, package=site)
        self.assertEqual(code, 1, receipt)
        self.assertEqual(receipt["problems"][0]["code"], "SOURCE_CHANGED")
        self.assertIn("release_id differs", receipt["problems"][0]["message"])

    def test_missing_manifest_and_changed_payload_never_fall_back(self):
        for change in ("missing_manifest", "changed_payload"):
            with self.subTest(change=change):
                site = self.root / change
                manifest, _ = packaged_fixture(site)
                if change == "missing_manifest":
                    manifest.unlink()
                else:
                    path = site / "dna_design_core/resources/VERSIONS.json"
                    path.write_bytes(path.read_bytes() + b" ")
                code, receipt = self.cli("run", "create", self.root / (change + "_run"), package=site)
                self.assertEqual(code, 1, receipt)
                self.assertEqual(receipt["problems"][0]["code"], "SOURCE_CHANGED")

    def test_development_seal_verifies_in_an_installed_release(self):
        # A source-generated seal is explicitly not release evidence. Its
        # scientific record must nevertheless remain independently verifiable.
        output = self.root / "source-example"
        process = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "examples/run_example.py"),
                                  "--source-tree", "--out", str(output)],
                                 cwd=self.root, text=True, encoding="utf-8", capture_output=True, timeout=120)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        summary = json.loads((output / "SUMMARY.json").read_text(encoding="utf-8"))
        portable = output / summary["portable_package"]
        manifest = json.loads((portable / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_id"], "dev-tree")
        self.assertEqual(json.loads((portable / "result.json").read_text(encoding="utf-8")), {"sequence": "TTCTGACT"})
        self.assertFalse((output / "run").exists())
        site = self.root / "installed-site"
        _, identity = packaged_fixture(site)
        self.assertEqual(len(identity), 64)
        code, receipt = self.cli("verify", portable, package=site)
        self.assertEqual(code, 0, receipt)
        self.assertTrue(receipt["result"]["verified"])
        # Changing a single result byte still invalidates the sealed record.
        result = portable / "result.json"
        data = result.read_bytes()
        self.assertIn(b"TTCTGACT", data)
        result.write_bytes(data.replace(b"TTCTGACT", b"ATCTGACT", 1))
        for package in (None, site):
            with self.subTest(package="installed" if package else "source"):
                code, receipt = self.cli("verify", portable, package=package)
                self.assertEqual(code, 1, receipt)
                self.assertFalse(receipt.get("result", {}).get("verified", False))

    def test_bundled_development_example_preserves_the_hand_answer_and_label(self):
        packages = [path for path in (ROOT / "examples/sealed/b1").iterdir() if path.is_dir()]
        self.assertEqual(len(packages), 1)
        portable = self.root / "copied-only" / packages[0].name
        shutil.copytree(packages[0], portable)
        code, receipt = self.cli("verify", portable)
        self.assertEqual(code, 0, receipt)
        self.assertTrue(receipt["result"]["verified"])
        self.assertEqual(json.loads((portable / "result.json").read_text(encoding="utf-8")), {"sequence": "TTCTGACT"})
        manifest = json.loads((portable / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["release_id"], "dev-tree")
        message = "This development-tree package is not release evidence."
        self.assertIn(message, manifest["not_verified"])
        for view in ("views/runcard.html", "views/report.md"):
            self.assertIn(message, (portable / view).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
