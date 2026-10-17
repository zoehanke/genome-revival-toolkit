"""Round2 evidence: default-CI skips, configured backend, pure functions and drafts."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parents[1]
OUTPUT = ROOT / "tests/evidence/s1b-round2"


def run(name, arguments, *, configured=None):
    environment = dict(os.environ, PYTHONPATH="src")
    environment.pop("GRT_PRIMER3_CORE", None)
    if configured is not None:
        environment["GRT_PRIMER3_CORE"] = str(configured)
    process = subprocess.run([sys.executable, "-X", "utf8", "-B", *arguments], cwd=ROOT, env=environment,
                             capture_output=True, text=True, encoding="utf-8", timeout=600)
    text = process.stdout + process.stderr
    path = OUTPUT / (name + ".txt")
    path.write_text(text, encoding="utf-8", newline="\n")
    result = {"command": arguments, "PYTHONPATH": "src", "primer3_configured": configured is not None,
              "exit_code": process.returncode, "output": path.name}
    found = re.search(r"Ran (\d+) tests? in", text)
    if found:
        count = int(found.group(1))
        skipped = int(re.search(r"skipped=(\d+)", text).group(1)) if re.search(r"skipped=(\d+)", text) else 0
        failures = int(re.search(r"failures=(\d+)", text).group(1)) if re.search(r"failures=(\d+)", text) else 0
        errors = int(re.search(r"errors=(\d+)", text).group(1)) if re.search(r"errors=(\d+)", text) else 0
        result.update(tests=count, passed=count - skipped - failures - errors, skipped=skipped, failures=failures, errors=errors)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primer3-core", type=Path)
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = {}
    results["structure"] = run("check_structure", ["tools/check_structure.py"])
    results["schemas"] = run("check_schemas", ["tools/check_schemas.py"])
    results["spec_lint"] = run("spec_lint", [str(ROOT / "tools/spec_lint.py"), str(REPO / "spec/SPEC.md")])
    results["all_tests_without_primer3_configuration"] = run("all-tests-default-ci", ["-m", "unittest", "discover", "-s", "tests", "-v"])
    if args.primer3_core is not None:
        results["actual_configured_primer3"] = run("configured-primer3", ["-m", "unittest", "discover", "-s", "tests/integration", "-p", "test_biology_capabilities.py",
            "-k", "test_primer3_real_ctx_external_calls_and_recorded_fingerprint", "-v"], configured=args.primer3_core)
    else:
        results["actual_configured_primer3"] = {"outcome": "UNKNOWN", "reason": "NOT_PERFORMED: no configured executable; not counted as PASS."}
    results["mutations"] = run("mutations", ["tests/oracles/round2_mutations.py"])
    results["kit_draft_validation"] = run("kit-drafts", ["tools/validate_kit_drafts.py", "--report", "docs/kit-prep/schema-report.json", "--write-markdown"])
    draft = json.loads((ROOT / "docs/kit-prep/schema-report.json").read_text(encoding="utf-8"))
    results["draft_findings"] = {key: draft[key] for key in ("draft_documents", "schema_invalid_documents", "a14_invalid_documents", "question_ids")}
    results["skip_policy"] = {"id": "S1B-PRIMER3-OPTIONAL", "missing_config": "Registered NOT_PERFORMED skip; zero passes for that numerical verification.",
        "configured_bad_result": "Actual integration test is exercised with a deliberately wrong fingerprint; expected failure and zero skips are asserted by unit tests."}
    checks = [value["exit_code"] == 0 for key, value in results.items() if isinstance(value, dict) and "exit_code" in value and key != "kit_draft_validation"]
    results["implementation_checks"] = "PASS" if all(checks) else "FAIL"
    results["kit_drafts"] = "FAIL" if draft["schema_invalid_documents"] or draft["a14_invalid_documents"] or draft["semantic_findings"] else "PASS"
    results["scope"] = "Kit migration rehearsal only; no Kit code, Kit runtime, wet-lab or new gate closure. Implementation tests and invalid draft findings remain separate."
    (OUTPUT / "validation.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if all(checks) and results["kit_draft_validation"]["exit_code"] == 1 else 1)
