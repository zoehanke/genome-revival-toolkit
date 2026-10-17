"""Every decision-table row through real CLI execution, sealing and copied verification."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.revival_s1e import EvidenceRun, decision_cases, write


def run(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for case in decision_cases():
        runner = EvidenceRun(output / case["name"])
        runner.prepare(**case["parameters"])
        actual = runner.complete()
        oracle = runner.oracle()
        result = {**case, "actual": actual, "matches": actual["status"] == case["expected"], "independent_oracle": oracle}
        results.append(result)
        summary = {"cases": results, "decision_rows_covered": sorted({row["row"] for row in results}),
                   "all_match": all(row["matches"] for row in results),
                   "guarded_commands": sum(row["actual"]["commands"] for row in results),
                   "connection_attempts": sum(row["actual"]["connection_attempts"] for row in results),
                   "scope": "Developer-run synthetic calculations, not a wet experiment or human first-use evaluation.",
                   "laboratory": "PLANNED / NOT_PERFORMED", "official_gitlab_ci": "not executed", "github_ci": "not run"}
        write(output / "SUMMARY.json", summary)
        assert result["matches"], result
        print("row", case["row"], case["name"], actual["status"], "sealed/copied-verified", flush=True)
    assert summary["decision_rows_covered"] == list(range(1, 11))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    result = run(parser.parse_args().out)
    print(json.dumps({"cases": len(result["cases"]), "rows": len(result["decision_rows_covered"]),
                      "all_match": result["all_match"], "connections": result["connection_attempts"]}))
