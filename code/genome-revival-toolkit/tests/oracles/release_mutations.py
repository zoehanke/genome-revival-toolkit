"""Deliberately break release checks/build output in disposable tool copies."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tests/evidence/s4a/mutations"
MUTATIONS = (
    ("license_bypass", "check_release.py", "actual != APACHE_SHA256", "False", "test_license_missing_and_one_byte_changed_both_reject"),
    ("size_bypass", "check_release.py", "size >= LIMIT", "False", "test_actual_tracked_size_over_fifty_megabytes_rejects"),
    ("placeholder_bypass", "check_release.py", "count = sum(placeholders.values())", "count = 0", "test_placeholders_are_counted_and_block_the_build"),
    ("manifest_hash_wrong", "build_release.py", '"sha256": digest(data)', '"sha256": "0" * 64', "test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata"),
    ("timestamp_wrong", "build_release.py", "STAMP = (1980, 1, 1, 0, 0, 0)", "STAMP = (2000, 1, 1, 0, 0, 0)", "test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata"),
    ("live_metadata_generation", "build_release.py", "files = selected(root)", "files = selected(root)\n    files['THIRD_PARTY.md'] = third_party(root)", "test_build_reads_frozen_notices_without_installed_metadata_generation"),
)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, module, before, after, test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="s4a_mutation_") as directory:
            root = Path(directory)
            tools = root / "tools"
            tools.mkdir()
            shutil.copyfile(ROOT / "VERSIONS.json", root / "VERSIONS.json")
            for filename in ("build_release.py", "check_release.py"):
                shutil.copyfile(ROOT / "tools" / filename, tools / filename)
            path = tools / module
            original = path.read_text(encoding="utf-8")
            if original.count(before) != 1:
                raise AssertionError("Mutation target must be unique: " + name)
            path.write_text(original.replace(before, after), encoding="utf-8", newline="\n")
            script = "import build_release, check_release, unittest; import test_release_engineering as tests; " + \
                     "result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([tests.ReleaseEngineeringTests(" + repr(test) + ")])); raise SystemExit(not result.wasSuccessful())"
            environment = dict(os.environ, PYTHONPATH=os.pathsep.join((str(tools), str(ROOT / "tests/unit"), str(ROOT / "tests"))))
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c", script], cwd=root, env=environment,
                capture_output=True, text=True, encoding="utf-8", timeout=90)
            output = process.stdout + process.stderr
            caught = process.returncode != 0 and "FAIL:" in output and "AssertionError:" in output and "ERROR:" not in output
            (OUTPUT / (name + ".txt")).write_text(output, encoding="utf-8", newline="\n")
            results.append({"id": name, "before": before, "after": after, "test": test, "exit_code": process.returncode,
                            "caught_by_assertion": caught, "output": name + ".txt"})
            print(json.dumps({"mutation": name, "caught_by_assertion": caught}), flush=True)
    (OUTPUT / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    raise SystemExit(0 if all(row["caught_by_assertion"] for row in results) else 1)
