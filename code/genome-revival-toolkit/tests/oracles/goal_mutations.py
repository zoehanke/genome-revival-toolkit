"""Six D2 source mutations in temporary package copies; the original literal tests must fail."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tests/evidence/s1b-c2/mutations"
CHANGES = (
    ("topology", 'value != topology for value in actual', 'value == topology for value in actual'),
    ("exact_sequence", '["sequence"] == sequence.upper()', '["sequence"] != sequence.upper()'),
    ("components_present", '_components(ctx, components, False)', '_components(ctx, components, True)'),
    ("components_absent", '_components(ctx, components, True)', '_components(ctx, components, False)'),
    ("regions_unchanged", 'expected == target[c:d]', 'expected != target[c:d]'),
    ("claim_reported", 'passed = len(matches) == 1 and isinstance(matches[0].get("status"), str) and bool(matches[0]["status"].strip())', 'passed = True'),
)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, before, after in CHANGES:
        with tempfile.TemporaryDirectory(prefix="s1b_c2_mutation_") as directory:
            root = Path(directory)
            package = root / "src/dna_design_core"
            shutil.copytree(ROOT / "src/dna_design_core", package, ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copyfile(ROOT / "VERSIONS.json", root / "VERSIONS.json")
            path = package / "capabilities/builtin/check/goal.py"
            original = path.read_text(encoding="utf-8")
            if original.count(before) != 1:
                raise AssertionError("mutation target is not unique: " + name)
            path.write_text(original.replace(before, after, 1), encoding="utf-8", newline="\n")
            # Run the unchanged assertion method over the selected check's two literal fixtures.
            script = "import unittest, test_goal_constraints as tests; tests.NAMES = (" + repr(name) + ",); tests.EVIDENCE = tests.Path('evidence'); " + \
                "result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([tests.GoalConstraintTests('test_all_twelve_literal_fixtures_execute_and_preserve_bytes')])); " + \
                "raise SystemExit(not result.wasSuccessful())"
            environment = dict(os.environ, PYTHONPATH=os.pathsep.join((str(root / "src"), str(ROOT / "tests/integration"), str(ROOT / "tests"))))
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c", script], cwd=root, env=environment,
                                     capture_output=True, text=True, encoding="utf-8", timeout=90)
            output = process.stdout + process.stderr
            caught = process.returncode != 0 and "FAIL:" in output and "AssertionError:" in output and "ERROR:" not in output
            (OUTPUT / (name + ".txt")).write_text(output, encoding="utf-8", newline="\n")
            results.append({"check": "check.goal." + name, "before": before, "after": after,
                            "exit_code": process.returncode, "caught_by_assertion": caught, "output": name + ".txt"})
            print(json.dumps({"check": name, "caught_by_assertion": caught}), flush=True)
    (OUTPUT / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    raise SystemExit(0 if all(row["caught_by_assertion"] for row in results) else 1)
