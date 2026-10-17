"""Two actual source mutations in disposable copies, never the working Kit."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
TEST = "tests.unit.test_cut_plasmid.CutPlasmidTests.test_all_check_pass_and_fail_fixtures_actually_run"


def run_mutations(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    source = (ROOT / "kits/cut-plasmid/capabilities/checks.py").read_text(encoding="utf-8")
    changes = [
        ("direction_comparison_flipped", 'else "PASS" if report["direction_correct"] else "FAIL"',
         'else "PASS" if not report["direction_correct"] else "FAIL"'),
        ("invalid_pam_exception_swallowed", '                outcome = "PASS" if report["pam_valid"] else "FAIL"',
         '                try:\n                    if not report["pam_valid"]:\n                        raise ValueError("INVALID_PAM")\n                    outcome = "PASS"\n                except ValueError:\n                    outcome = "PASS"'),
    ]
    results = []
    for name, before, after in changes:
        assert source.count(before) == 1, name
        with tempfile.TemporaryDirectory(prefix="s2_mutation_") as temporary:
            copy = Path(temporary) / "project"
            copy.mkdir()
            shutil.copytree(ROOT / "src", copy / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            shutil.copytree(ROOT / "kits/cut-plasmid", copy / "kits/cut-plasmid", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for relative in ("tests/__init__.py", "tests/unit/__init__.py", "tests/cut_plasmid_runtime.py", "tests/unit/test_cut_plasmid.py", "VERSIONS.json"):
                target = copy / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            (copy / "kits/cut-plasmid/capabilities/checks.py").write_text(source.replace(before, after), encoding="utf-8", newline="\n")
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-m", "unittest", TEST, "-v"], cwd=copy,
                                     capture_output=True, text=True, encoding="utf-8", timeout=180)
            (output / (name + ".stdout.txt")).write_text(process.stdout, encoding="utf-8")
            (output / (name + ".stderr.txt")).write_text(process.stderr, encoding="utf-8")
            caught = process.returncode != 0 and "FAIL:" in process.stderr and "AssertionError:" in process.stderr and "ERROR:" not in process.stderr
            results.append({"mutation": name, "before": before, "after": after, "exit_code": process.returncode,
                            "caught_by_assertion": caught, "test": TEST})
    value = {"mutations": results, "caught": sum(row["caught_by_assertion"] for row in results), "total": len(results)}
    (output / "results.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_mutations(args.out)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["caught"] == result["total"] else 1)
