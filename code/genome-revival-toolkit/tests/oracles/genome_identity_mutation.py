"""Flip the discrimination comparison in a copy and execute the same independent-answer tests."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Choose a new evidence directory; earlier failures are retained")
    output.mkdir(parents=True)
    source = ROOT / "kits/genome-identity/capabilities/operations.py"
    text = source.read_text(encoding="utf-8")
    needle = 'len(signatures) == len(predictions)'
    assert text.count(needle) == 1
    mutant = output / "operations-mutant.py"
    mutant.write_text(text.replace(needle, 'len(signatures) != len(predictions)'), encoding="utf-8")
    results = []
    for name, path in (("baseline", source), ("mutant", mutant)):
        program = "\n".join([
            "from pathlib import Path", "import unittest, sys",
            "from tests.unit import test_genome_identity as subject",
            "subject.OPERATIONS_PATH = Path(sys.argv[1])",
            "suite=unittest.TestSuite(subject.GenomeIdentityTests(name) for name in ('test_different_sizes','test_same_sizes'))",
            "result=unittest.TextTestRunner(verbosity=2).run(suite)",
            "sys.exit(0 if result.wasSuccessful() else 1)",
        ])
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", "-c", program, str(path)],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        (output / (name + ".txt")).write_text(result.stdout + result.stderr, encoding="utf-8")
        results.append({"variant": name, "exit_code": result.returncode, "output": name + ".txt"})
    assert results[0]["exit_code"] == 0 and results[1]["exit_code"] == 1, results
    summary = {"mutation": "== changed to != in the count/size discrimination comparison",
               "caught": True, "runs": results, "oracle_kind": "construction"}
    (output / "results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    print(json.dumps(run(parser.parse_args().out), indent=2))
