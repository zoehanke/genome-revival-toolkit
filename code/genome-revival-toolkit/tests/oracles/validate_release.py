"""S4a local evidence, streaming raw output; no dependency installation or new virtual environment."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parents[1]
OUTPUT = ROOT / "tests/evidence/s4a"


def command(name, arguments, expected=0, primer3=None):
    environment = dict(os.environ, PYTHONPATH="src")
    environment.pop("GRT_PRIMER3_CORE", None)
    if primer3:
        environment["GRT_PRIMER3_CORE"] = str(primer3)
    path = OUTPUT / (name + ".txt")
    print(json.dumps({"started": name, "output": path.name}), flush=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        process = subprocess.run([sys.executable, "-X", "utf8", "-B", *arguments], cwd=ROOT, env=environment,
                                 stdout=stream, stderr=subprocess.STDOUT, text=True, encoding="utf-8", timeout=1800)
    text = path.read_text(encoding="utf-8")
    result = {"command": arguments, "PYTHONPATH": "src", "exit_code": process.returncode, "expected_exit": expected,
              "met_expectation": process.returncode == expected, "output": path.name}
    match = re.search(r"Ran (\d+) tests? in", text)
    if match:
        counts = {name: int(found.group(1)) if (found := re.search(name + r"=(\d+)", text)) else 0 for name in ("failures", "errors", "skipped")}
        result.update(tests=int(match[1]), **counts)
        result["passed"] = result["tests"] - sum(counts.values())
    print(json.dumps({name: result}), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primer3-core", type=Path)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    checks = {}
    for name, arguments in {
        "structure": ["tools/check_structure.py"], "schemas": ["tools/check_schemas.py"],
        "spec_lint": [str(ROOT / "tools/spec_lint.py"), str(REPO / "spec/SPEC.md")],
        "generated_docs": ["tools/docgen.py", "--check"],
        "all-tests": ["-m", "unittest", "discover", "-s", "tests", "-v"],
    }.items():
        checks[name] = command(name, arguments)
        if not checks[name]["met_expectation"]:
            break
    if all(row["met_expectation"] for row in checks.values()) and args.primer3_core:
        checks["configured-primer3"] = command("configured-primer3", ["-m", "unittest", "discover", "-s", "tests/integration",
            "-p", "test_biology_capabilities.py", "-k", "test_primer3_real_ctx_external_calls_and_recorded_fingerprint", "-v"], primer3=args.primer3_core)
    checks["actual-release-tree"] = command("actual-release-tree", ["tools/check_release.py", "--report", str(OUTPUT / "release-check.json")], expected=2)
    mutation_path = OUTPUT / "mutations/results.json"
    mutations = json.loads(mutation_path.read_text()) if mutation_path.exists() else []
    example_path = ROOT / "dist/s4a-b1-source/SUMMARY.json"
    if example_path.exists():
        (OUTPUT / "source-example-summary.json").write_bytes(example_path.read_bytes())
    result = {"checks": checks, "mutations": {"executed_separately": True, "total": len(mutations), "caught": sum(row["caught_by_assertion"] for row in mutations)},
        "engineering_tests": "PASS" if all(row["met_expectation"] for row in checks.values()) and len(mutations) == 6 and all(row["caught_by_assertion"] for row in mutations) else "FAIL",
        "release_ready": False, "fresh_environment_installation": "NOT_PERFORMED; separate authorization required",
        "official_gitlab_ci": "未执行", "github_ci": "未运行",
        "scope": "Existing local environment only; F10 controls, deterministic synthetic source builds, offline build metadata and source-mode example. Not S4 approval."}
    (OUTPUT / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    raise SystemExit(result["engineering_tests"] != "PASS")
