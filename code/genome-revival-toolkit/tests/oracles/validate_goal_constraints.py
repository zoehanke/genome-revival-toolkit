"""Merged S1/S1b verification plus the six D2 constraint checks; preserve earlier round2 evidence."""
import argparse
import json
from pathlib import Path

import validate_round2 as shared


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primer3-core", type=Path)
    args = parser.parse_args()
    shared.OUTPUT = shared.ROOT / "tests/evidence/s1b-c2"
    shared.OUTPUT.mkdir(parents=True, exist_ok=True)
    checks = {}
    commands = {
        "structure": ["tools/check_structure.py"],
        "schemas": ["tools/check_schemas.py"],
        "generated_docs": ["tools/docgen.py", "--check"],
        "spec_lint": [str(shared.ROOT / "tools/spec_lint.py"), str(shared.REPO / "spec/SPEC.md")],
        "all_tests_without_primer3": ["-m", "unittest", "discover", "-s", "tests", "-v"],
    }
    for name, arguments in commands.items():
        checks[name] = shared.run(name, arguments)
        print(json.dumps({name: checks[name]}), flush=True)
    if args.primer3_core is not None:
        checks["configured_primer3"] = shared.run("configured_primer3", ["-m", "unittest", "discover", "-s", "tests/integration",
            "-p", "test_biology_capabilities.py", "-k", "test_primer3_real_ctx_external_calls_and_recorded_fingerprint", "-v"], configured=args.primer3_core)
    else:
        checks["configured_primer3"] = {"outcome": "NOT_PERFORMED", "reason": "No executable configuration supplied; not a numerical PASS."}
    mutation_path = shared.OUTPUT / "mutations/results.json"
    mutations = json.loads(mutation_path.read_text()) if mutation_path.exists() else []
    mutation_evidence = {"output": "mutations/results.json", "mutations": len(mutations),
                         "caught": sum(row["caught_by_assertion"] for row in mutations), "execution": "Separate goal_mutations.py command; not rerun by this runner."}
    passed = all(row.get("exit_code", 0) == 0 for row in checks.values()) and len(mutations) == 6 and mutation_evidence["caught"] == 6
    result = {"checks": checks, "source_mutations": mutation_evidence,
              "scope": "Merged S1/S1b tests and six target-bound D2 checks. No new Kit implementation, full scientific seal acceptance, wet experiment or CI.",
              "implementation_checks": "PASS" if passed else "FAIL"}
    (shared.OUTPUT / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2), flush=True)
    raise SystemExit(result["implementation_checks"] != "PASS")
