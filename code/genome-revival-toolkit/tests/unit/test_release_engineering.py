"""Actual positive/negative release checks with construction answers, not another implementation's output."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
from build_release import build, digest, payload, STAMP, third_party
from check_release import inspect_tree, inspect_zip
from clean_env_verify import plan
from release_fixture import HEADINGS, source_tree, write


class ReleaseEngineeringTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="s4a_发行_")
        self.addCleanup(self.temporary.cleanup)
        self.root = source_tree(Path(self.temporary.name) / "source")

    def assert_fails(self, name):
        result = inspect_tree(self.root)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn(name, {row["check"] for row in result["findings"]}, result)
        return result

    def test_valid_independent_tree_passes_every_f10_item(self):
        result = inspect_tree(self.root)
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["license_sha256"], "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30")
        self.assertGreater(result["tracked_bytes"], 0)
        self.assertLess(result["tracked_bytes"], 50_000_000)

    def test_license_missing_and_one_byte_changed_both_reject(self):
        license_path = self.root / "LICENSE"
        original = license_path.read_bytes()
        license_path.unlink()
        self.assert_fails("license")
        license_path.write_bytes(original + b"x")
        self.assert_fails("license")

    def test_each_required_readme_section_is_executed_as_negative(self):
        path = self.root / "README.md"
        original = path.read_text(encoding="utf-8")
        results = []
        for heading in HEADINGS:
            with self.subTest(section=heading):
                path.write_text(original.replace("## " + heading + "\n\nSynthetic test content.", "", 1), encoding="utf-8")
                result = self.assert_fails("readme")
                results.append({"removed": heading, "actual": result["status"], "findings": result["findings"]})
        path.write_text(original.replace("Synthetic test content.", "", 1), encoding="utf-8")
        self.assert_fails("readme")
        folder = ROOT / "tests/evidence/s4a"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "readme-negatives.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")

    def test_lock_missing_unpinned_and_conflicting_reject(self):
        path = self.root / "requirements.lock"
        path.unlink()
        self.assert_fails("dependencies")
        write(self.root, "requirements.lock", "rfc8785>=0.1\n")
        self.assert_fails("dependencies")
        write(self.root, "requirements.lock", "rfc8785==0.1.4\n")
        write(self.root, "requirements-other.lock", "rfc8785==0.1.3\n")
        self.assert_fails("dependencies")

    def test_each_forbidden_selected_extension_rejects(self):
        for suffix in (".exe", ".bin", ".dll", ".pyd"):
            with self.subTest(suffix=suffix):
                path = write(self.root, "src/forbidden" + suffix, "Synthetic extension control, not executable code.\n")
                self.assert_fails("compiled")
                path.unlink()

    def test_excluded_but_tracked_binary_is_still_rejected(self):
        path = write(self.root, "not-shipped/tool.DLL", "Synthetic tracked-file control.\n")
        subprocess.run(["git", "-C", str(self.root), "add", "--", path.relative_to(self.root).as_posix()], check=True, capture_output=True)
        self.assert_fails("compiled")

    def test_actual_tracked_size_over_fifty_megabytes_rejects(self):
        path = self.root / "large-tracked.txt"
        with path.open("wb") as stream:
            stream.truncate(50_000_001)
        subprocess.run(["git", "-C", str(self.root), "add", "--", path.name], check=True, capture_output=True)
        result = self.assert_fails("tracked_size")
        self.assertGreater(result["tracked_bytes"], 50_000_000)

    def test_second_literal_version_or_wrong_provider_rejects(self):
        path = self.root / "pyproject.toml"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace('dynamic=["version"]', 'version="9.9.9"'), encoding="utf-8")
        self.assert_fails("versions")
        path.write_text(original.replace('tools.build_release.VERSION', 'other.VERSION'), encoding="utf-8")
        self.assert_fails("versions")
        path.write_text(original, encoding="utf-8")
        write(self.root, "tools/build_release.py", 'VERSION = "0.0.0"\n')
        self.assert_fails("versions")

    def test_placeholders_are_counted_and_block_the_build(self):
        write(self.root, "docs/judges/disclosure.md", "Pending: 【待用户填写】 and 【待用户填写】\n")
        result = inspect_tree(self.root)
        self.assertEqual((result["status"], result["placeholder_count"]), ("INCOMPLETE", 2))
        output = self.root.parent / "blocked-output"
        self.assertFalse(build(self.root, output, "constructed")["build_created"])
        self.assertFalse(output.exists())

    def test_personal_path_and_generated_file_exclusion_reject(self):
        private = ":/".join(("C", "Users")) + "/SyntheticPerson/private.txt"
        write(self.root, "docs/judges/private.md", private)
        self.assert_fails("personal_paths")
        (self.root / "docs/judges/private.md").unlink()
        value = json.loads((self.root / "ship.json").read_text())
        value["exclude"] = ["THIRD_PARTY.md"]
        write(self.root, "ship.json", value)
        self.assert_fails("ship")

    def test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata(self):
        first = build(self.root, self.root.parent / "a", "fixed-construction")
        second = build(self.root, self.root.parent / "b", "fixed-construction")
        self.assertEqual(first, second)
        left = self.root.parent / "a" / first["archive"]
        right = self.root.parent / "b" / second["archive"]
        self.assertEqual(left.read_bytes(), right.read_bytes())
        checked = inspect_zip(left)
        self.assertEqual(checked["status"], "PASS", checked)
        with zipfile.ZipFile(left) as bundle:
            self.assertEqual(bundle.namelist(), sorted(bundle.namelist()))
            self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in bundle.infolist()))
            manifest = json.loads(bundle.read("release-manifest.json"))
            self.assertNotIn("release_id", manifest)
            self.assertNotIn("release-manifest.json", {row["path"] for row in manifest["files"]})
            import hashlib
            self.assertEqual(hashlib.sha256(bundle.read("release-manifest.json")).hexdigest(), first["release_id"])
            self.assertEqual(json.loads(bundle.read("src/dna_design_core/resources/VERSIONS.json")), manifest["versions"])

    def test_build_reads_frozen_notices_without_installed_metadata_generation(self):
        with patch("build_release.third_party", side_effect=AssertionError("build must not depend on installed distribution metadata")):
            built = build(self.root, self.root.parent / "frozen-notices", "fixed")
        self.assertTrue(built["build_created"])
        with zipfile.ZipFile(self.root.parent / "frozen-notices" / built["archive"]) as archive:
            self.assertEqual(archive.read("THIRD_PARTY.md"), (self.root / "THIRD_PARTY.md").read_bytes())
        write(self.root, "THIRD_PARTY.md", "# Stale dependency inventory\n")
        self.assert_fails("ship")

    def test_tampered_archive_member_cannot_pass(self):
        built = build(self.root, self.root.parent / "original", "fixed")
        path = self.root.parent / "original" / built["archive"]
        altered = self.root.parent / "altered.zip"
        with zipfile.ZipFile(path) as original, zipfile.ZipFile(altered, "w") as changed:
            for info in original.infolist():
                data = original.read(info.filename)
                changed.writestr(info, data + b"changed" if info.filename == "README.md" else data)
        result = inspect_zip(altered)
        self.assertEqual(result["status"], "FAIL", result)
        self.assertIn("File bytes differ: README.md", result["findings"])

    def test_zip_with_an_unlisted_compiled_member_is_rejected(self):
        built = build(self.root, self.root.parent / "a", "fixed")
        path = self.root.parent / "a" / built["archive"]
        with zipfile.ZipFile(path, "a") as bundle:
            bundle.writestr("extra.exe", b"Synthetic archive rejection control")
        self.assertEqual(inspect_zip(path)["status"], "FAIL")

    def test_fresh_environment_plan_never_creates_or_installs(self):
        output = self.root.parent / "fresh"
        with patch("venv.EnvBuilder", side_effect=AssertionError("installation is not authorized")), \
             patch("subprocess.run", side_effect=AssertionError("no command should run")):
            result = plan(self.root.parent / "future.zip", output)
        self.assertEqual(result["status"], "NOT_PERFORMED")
        self.assertFalse(result["system_site_packages"])
        self.assertFalse(output.exists())
        self.assertIn("requirements-release.lock", result["commands"][0][-1])
        self.assertNotIn("--source-tree", result["commands"][2])

    def test_public_check_command_nonzero_on_invalid_and_incomplete(self):
        for text, expected in (("# No required sections\n", "FAIL"), ((self.root / "README.md").read_text(encoding="utf-8") + "\n【待用户填写】\n", "INCOMPLETE")):
            with self.subTest(expected=expected):
                write(self.root, "README.md", text)
                process = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tools/check_release.py"), "--root", str(self.root)], capture_output=True, text=True, encoding="utf-8")
                self.assertNotEqual(process.returncode, 0)
                self.assertEqual(json.loads(process.stdout)["status"], expected)


if __name__ == "__main__":
    unittest.main()
