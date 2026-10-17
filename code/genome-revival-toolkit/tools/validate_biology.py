"""Developer evidence runner for S1b, not a product CLI or gate closer.

Run structure first. If it fails, later results remain diagnostic and the
overall result cannot be PASS. No package installation or network access.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUTPUT = ROOT / "tests/evidence/s1b"


def suite_result(folder: str, pattern: str = "test*.py") -> dict:
    suite = unittest.TestLoader().discover(str(ROOT / "tests" / folder), pattern=pattern, top_level_dir=str(ROOT / "tests"))
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    target = OUTPUT / (folder + ".txt")
    target.write_text(log.getvalue(), encoding="utf-8", newline="\n")
    return {
        "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped),
        "failed_tests": [test.id() for test, _ in result.failures + result.errors],
        "exit_code": 0 if result.wasSuccessful() else 1, "output": target.name,
    }


def command_result(name: str, arguments: list[str]) -> dict:
    environment = dict(os.environ, PYTHONPATH="src")
    process = subprocess.run([sys.executable, "-X", "utf8", "-B", *arguments], cwd=ROOT, env=environment,
                             text=True, capture_output=True, encoding="utf-8", timeout=120)
    target = OUTPUT / (name + ".txt")
    target.write_text(process.stdout + process.stderr, encoding="utf-8", newline="\n")
    return {"command": arguments, "exit_code": process.returncode, "output": target.name}


def compare_primer3() -> dict:
    from dna_design_core.biology.public import TmParameters, calculate_tm, primer_quality

    reference = json.loads((OUTPUT / "primer3/reference.json").read_text(encoding="utf-8"))
    if reference["outcome"] != "PASS":
        return {"outcome": "UNKNOWN", "case_count": 0, "reason": reference.get("reason", "Reference backend unavailable")}
    comparisons = []
    for case in reference["cases"]:
        calculated = calculate_tm(case["sequence"], TmParameters(**case["parameters"]))
        quality = primer_quality(case["sequence"], partner=case["partner"])
        expected = case["measurements"]["PRIMER_LEFT_0_TM"]
        comparisons.append({
            "id": case["id"], "parameters": calculated["parameters"], "calculated_tm_degC": calculated["tm"],
            "primer3_tm_degC": expected, "delta_degC": str(Decimal(calculated["tm"]) - Decimal(expected)),
            "exact_complementarity": quality,
            "primer3_thermodynamic_metrics_degC": {key: value for key, value in case["measurements"].items()
                                                   if key.endswith(("_SELF_ANY_TH", "_SELF_END_TH", "_HAIRPIN_TH", "_COMPL_ANY_TH", "_COMPL_END_TH"))},
            "comparison_scope": "Tm has matching parameters. Contiguous bp and thermodynamic degC are different metrics and cannot be subtracted.",
        })
    result = {
        "reference_program": {"version": reference["version"], "sha256": reference["sha256"]},
        "tm_print_rounding_tolerance_degC": "0.00050001",
        "max_abs_tm_delta_degC": str(max(abs(Decimal(case["delta_degC"])) for case in comparisons)),
        "difference_reason": "Primer3 prints Tm to three decimals. Exact complementarity omits mismatches, bulges, loop energies, salt and terminal stacking; Primer3 thermodynamic structure Tm is a separate measurement.",
        "cases": comparisons,
    }
    (OUTPUT / "primer3-comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return {"case_count": len(comparisons), "max_abs_tm_delta_degC": result["max_abs_tm_delta_degC"]}


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = {}
    results["check_structure"] = command_result("check_structure", [str(ROOT / "tools/check_structure.py")])
    results["check_schemas"] = command_result("check_schemas", [str(ROOT / "tools/check_schemas.py")])
    results["structure"] = suite_result("structure")
    results["spec_lint"] = command_result("spec_lint", [str(ROOT / "tools/spec_lint.py"), str(REPO / "spec/SPEC.md")])
    structure_green = all(results[name]["exit_code"] == 0 for name in ("check_structure", "check_schemas", "structure", "spec_lint"))
    # Continuing collects development evidence, never stage acceptance after red structure.
    results["contract"] = suite_result("contract")
    results["unit"] = suite_result("unit")
    results["integration"] = suite_result("integration")
    results["e2e"] = suite_result("e2e")
    results["primer3_reference"] = command_result("primer3_reference", [str(ROOT / "tests/oracles/primer3_reference.py"),
        "--executable", os.environ.get("GRT_PRIMER3_CORE", str(OUTPUT / "nonexistent-primer3_core.exe")),
        "--output", str(OUTPUT / "primer3")])
    results["mutations"] = command_result("mutations", [str(ROOT / "tests/oracles/biology_mutations.py")])
    results["primer3_comparison"] = compare_primer3()
    results["structure_green"] = structure_green
    results["environment"] = {"PYTHONPATH": "src", "GRT_PRIMER3_CORE_configured": bool(os.environ.get("GRT_PRIMER3_CORE"))}
    results["capability_contract_tests"] = 3
    results["new_capabilities"] = 22
    results["check_fixtures_executed"] = len(json.loads((OUTPUT / "integration/check-fixtures.json").read_text())) if (OUTPUT / "integration/check-fixtures.json").exists() else 0
    green = structure_green and all(value.get("exit_code", 0) == 0 for value in results.values() if isinstance(value, dict)) and results["primer3_comparison"].get("case_count") == 7
    results["runtime_material_integration"] = "PASS" if results["integration"]["exit_code"] == 0 else "FAIL"
    results["overall_outcome"] = "PASS" if green else "FAIL"
    results["scope"] = "S1b developer verification only; S1 and S1b stage gates remain with the specification owner. No wet-laboratory or Kit acceptance."
    (OUTPUT / "validation.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    raise SystemExit(0 if green else 1)
