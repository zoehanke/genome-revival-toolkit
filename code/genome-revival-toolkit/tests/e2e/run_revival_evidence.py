"""Public CLI S3 cases, retained receipts, portable seals, and independent oracle."""
import argparse
from importlib.util import find_spec
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "kits/revival-evidence"
CLI = Path(find_spec("dna_design_core.application.cli").origin)
GUARD = ROOT / "tests/e2e/network_guard.py"
ORACLE = ROOT / "tests/oracles/revival_evidence.py"


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def run_examples(output, *, scoped=False):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts, summaries, oracles = [], {}, []

    def command(cwd, *arguments, expected=0):
        audit = output / ("network-" + str(len(receipts)) + ".json")
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(GUARD), str(audit), str(CLI),
                                 *map(str, arguments)], cwd=cwd, text=True, capture_output=True, encoding="utf-8")
        receipt = json.loads(result.stdout)
        record = {"arguments": list(map(str, arguments)), "exit_code": result.returncode,
                  "receipt": receipt, "stderr": result.stderr, "network": json.loads(audit.read_text(encoding="utf-8"))}
        receipts.append(record)
        write(output / "receipts.json", receipts)
        assert record["network"]["attempts"] == 0, record
        assert result.returncode == expected, record
        return receipt

    cases = [("b3", "b3.csv", None), ("missing_count_and_ids", "no_ids.csv", None),
             ("local_predictions", "local_observations.json", "identity-expected-results.json"),
             ("empty", "empty.json", None),
             ("product_counts", "product-count-observations.json", "product-count-predictions.json")]
    scoped_answers = {}
    if scoped:
        # Literal expected answers from the S3b task, not output from Kit or oracle.
        for name, fusion, control, state in [
            ("fusion_missing", None, 0, "NOT_TESTED"),
            ("fusion_zero", 0, 31, "CONTRADICTED"),
            ("control_missing", 9, None, "INSUFFICIENT"),
            ("control_positive", 9, 31, "INSUFFICIENT"),
            ("fusion_supported", 9, 0, "SUPPORTED"),
            ("no_comparisons", 9, 0, None),
        ]:
            observation = write(output / (name + "-observations.json"), {"observations": [
                {"id": "f1", "group": "fusion", "colonies": fusion, "role": "fusion", "unit": "colony"},
                {"id": "c1", "group": "control", "colonies": control,
                 "role": "inactivated_donor_control", "unit": "colony"}]})
            cases.append((name, observation, None))
            scoped_answers[name] = state
    for name, observation_name, prediction_name in cases:
        folder = output / name
        folder.mkdir()
        run = folder / "run"
        observations = KIT / "examples" / observation_name
        predictions = KIT / "examples" / prediction_name if prediction_name else None
        command(folder, "run", "create", run)
        goal = json.loads((KIT / "examples/goal.json").read_text(encoding="utf-8"))
        declaration = json.loads((CLI.parents[1] / "resources/capabilities/check.goal.claim_reported.json").read_text(encoding="utf-8"))
        goal["constraints"][0]["check"] = declaration["id"] + "@" + declaration["version"]
        goal["sources"][0]["from"] = str(observations)
        if predictions:
            goal["sources"].append({"source_id": "predictions", "from": str(predictions), "as": "artifact",
                                    "input_origin": "user_file", "declared": {}})
        declared = command(folder, "goal", "declare", "--run", run, "--request", write(folder / "goal.json", goal))
        comparisons = [{"experiment_group": "fusion", "control_group": "control"}] if (
            name in {"b3", "missing_count_and_ids"} or name in scoped_answers and name != "no_comparisons") else []
        request = {"goal_digest": declared["result"]["goal_digest"], "source_id": "observations",
                   "observation_origin": "SYNTHETIC_EXAMPLE", "comparisons": comparisons}
        instantiated = command(folder, "template", "instantiate", "revival-evidence.assess_observations", "--request", write(folder / "template.json", request))
        plan = instantiated["result"]["draft"]
        if name == "no_comparisons":
            del plan["steps"][1]["params"]["comparisons"]
        if predictions:
            plan["steps"][0]["inputs"]["predictions"] = {"source": "predictions"}
        command(folder, "pipeline", "submit", "--run", run, "--request", write(folder / "plan.json", plan))
        events = [json.loads(line) for line in (run / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
        assert not any(row["type"] == "step.started" for row in events)
        executed = command(folder, "run", "execute", "--run", run)
        assert executed["state"] == "COMPLETED", executed
        judged = command(folder, "judge", "--run", run)
        assert judged["result"]["unsatisfied"] == [], judged
        sealed = command(folder, "seal", "--run", run)
        package = Path(sealed["result"]["manifest"]).parent
        report = json.loads((package / "assessment.json").read_text(encoding="utf-8"))
        if name == "b3":
            assert report["comparisons"][0]["difference"] == -22
            assert next(row for row in report["conclusions"] if row["claim"] == "functional_revival")["status"] == "INSUFFICIENT"
        if name == "missing_count_and_ids":
            assert report["comparisons"][0]["difference"] is None and report["generated_ids"]
        if name == "product_counts":
            local = {row["subject"]["background_id"]: row["status"] for row in report["conclusions"]
                     if row["claim"] == "local_prediction_agreement"}
            assert local == {"absent": "SUPPORTED", "single": "SUPPORTED", "multiple": "INSUFFICIENT"}, local
        if name in scoped_answers:
            rows = [row for row in report["conclusions"] if row["claim"] == "fusion_plate_outgrowth"]
            expected = scoped_answers[name]
            assert [row["status"] for row in rows] == ([] if expected is None else [expected]), rows
            assert all(row["status"] in {"INSUFFICIENT", "NOT_TESTED"} for row in report["conclusions"]
                       if row["claim"] in {"functional_revival", "whole_genome_elimination"})
        command(folder, "verify", run)
        copied = folder / "portable" / package.name
        shutil.copytree(package, copied)
        run.rename(folder / "retained-run")
        before = {path.relative_to(copied).as_posix(): path.read_bytes() for path in copied.rglob("*") if path.is_file()}
        verified = command(folder, "verify", copied)
        assert verified["result"]["verified"] and verified["result"]["not_rerun"] == [], verified
        assert before == {path.relative_to(copied).as_posix(): path.read_bytes() for path in copied.rglob("*") if path.is_file()}
        assert not any((copied / "store/materials").glob("*.json"))
        manifest = json.loads((copied / "manifest.json").read_text(encoding="utf-8"))
        assert all(row["scope"] != "preparation_model" for row in manifest["verdicts"])
        assert "evidence.check_record_consistency" in {row["check"] for row in manifest["verdicts"]}
        assert "check.goal.claim_reported" in {row["check"] for row in manifest["verdicts"]}
        card = (copied / "views/runcard.html").read_text(encoding="utf-8")
        assert all(text in card for text in manifest["not_verified"])
        for view in (card, (copied / "views/report.md").read_text(encoding="utf-8")):
            supported = [row for row in report["conclusions"] if row["subject"] and row["status"] == "SUPPORTED"]
            if supported:
                first = view.index("Supported scoped conclusions (submitted records only):")
                last = view.index("Does not support:", first)
                for row in supported:
                    assert row["claim"] in view[first:last] and row["reason"] in view[first:last]
            else:
                assert "No scoped conclusion is supported." in view
        arguments = [sys.executable, "-X", "utf8", "-B", str(ORACLE), "--observations", str(observations),
                     "--rules-dir", str(KIT / "knowledge"), "--assessment", str(copied / "assessment.json")]
        if predictions:
            arguments.extend(["--predictions", str(predictions)])
        arguments.extend(["--comparisons", str(write(folder / "comparisons.json", comparisons))])
        result = subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        oracles.append({"case": name, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        write(output / "oracle-receipts.json", oracles)
        assert result.returncode == 0, oracles[-1]
        summaries[name] = {"package": copied.relative_to(output).as_posix(), "verify": verified["result"]["verified"],
                           "conclusions": report["conclusions"], "release_id": manifest["release_id"],
                           "offline_checks": len(verified["result"]["verdicts"]), "oracle": json.loads(result.stdout),
                           **({"expected_scoped_status": scoped_answers[name]} if name in scoped_answers else {})}
        write(output / "cases.json", summaries)
        print(name + ": sealed, copied verification and independent oracle passed", file=sys.stderr, flush=True)
    summary = {"cases": summaries, "commands": len(receipts), "connection_attempts": sum(row["network"]["attempts"] for row in receipts),
               "limits": ["Constructed S5b interface files; actual cross-Kit execution was not performed.",
                          "Synthetic observations; wet-laboratory outcomes and authenticity were not verified."],
               "official_gitlab_ci": "not executed", "github_ci": "not run"}
    write(output / "SUMMARY.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scoped", action="store_true", help="Include all five S3b rows and omission of comparisons.")
    args = parser.parse_args()
    print(json.dumps(run_examples(args.out, scoped=args.scoped), ensure_ascii=False, indent=2))
