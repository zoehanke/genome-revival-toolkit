"""Independent standard-library oracle; never imports Core or Kit implementations."""
import argparse
import csv
from decimal import Decimal
import json
from pathlib import Path


def number(value):
    if value is None or value == "":
        return None
    parsed = Decimal(str(value))
    assert not isinstance(value, bool) and parsed.is_finite() and parsed >= 0 and parsed == int(parsed)
    return int(parsed)


def input_records(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    if text.lstrip().startswith("{"):
        data = json.loads(text)
    else:
        data = {"observations": list(csv.DictReader(text.splitlines()))}
    taken = {row["id"] for row in data["observations"] if row.get("id")}
    observations = []
    for position, row in enumerate(data["observations"], 1):
        identity = row.get("id")
        if not identity:
            identity = "row_" + str(position)
            while identity in taken:
                identity += "_auto"
            taken.add(identity)
        observations.append({"id": identity, "group": row["group"],
                             "count": number(row.get("colonies") if "colonies" in row else row.get("value")),
                             "role": row.get("role") or None, "unit": row.get("unit") or None})
    return observations, data.get("genotype_results", []), data.get("functional_results", [])


def condition_result(values, condition):
    if condition["field"] not in values:
        return None
    current, target = values[condition["field"]], condition["value"]
    operation = condition["op"]
    if operation == "exists":
        return (current is not None) == target
    if current is None:
        return None
    operators = {"eq": lambda: current == target, "in": lambda: current in target,
                 "gte": lambda: current >= target, "lte": lambda: current <= target,
                 "between": lambda: target[0] <= current <= target[1]}
    return operators[operation]()


def applies(values, conditions):
    results = [condition_result(values, row) for row in conditions]
    return False if False in results else None if None in results else True


def verdict_key(row):
    return (row["claim"], json.dumps(row["subject"], sort_keys=True), row["status"], row["applicability"])


def fusion_state(experiment, control):
    """Literal S3b construction table, independent of the rule's status cells."""
    if experiment is None:
        return "NOT_TESTED"
    if experiment == 0:
        return "CONTRADICTED"
    if control is None or control > 0:
        return "INSUFFICIENT"
    return "SUPPORTED"


def recompute(observations_file, rules_dir, predictions_file=None, comparisons=()):
    observations, assays, functions = input_records(observations_file)
    tested_counts = any(row["count"] is not None for row in observations)
    tested_genotypes = any(row["result"] != "not_tested" for row in assays)
    tested_functions = any(row["result"] != "not_tested" for row in functions)
    summary = {"observed_counts": tested_counts, "tested_genotypes": tested_genotypes,
               "tested_function": tested_functions, "any_tested": tested_counts or tested_genotypes or tested_functions}
    domains = {"summary": [({}, summary)], "observation": [], "assay": [], "comparison": []}
    for row in observations:
        domains["observation"].append(({"sample_id": row["id"]}, {
            "role": row["role"], "count_known": row["count"] is not None,
            "count_positive": row["count"] is not None and row["count"] > 0}))
    for comparison in comparisons:
        group_counts = [[row["count"] for row in observations if row["group"] == comparison[key]]
                        for key in ("experiment_group", "control_group")]
        assert all(group_counts), "Selected comparison group is missing"
        first, second = [None if None in values else sum(values) for values in group_counts]
        domains["comparison"].append((dict(comparison), {
            "count_known": first is not None, "count_positive": first is not None and first > 0,
            "control_count_known": second is not None, "control_count_positive": second is not None and second > 0,
            "experiment": first, "control": second}))
    predictions = json.loads(Path(predictions_file).read_text(encoding="utf-8")) if predictions_file else None
    for assay in assays:
        matches = [] if predictions is None or predictions["assay_id"] != assay["assay_id"] else [
            row for row in predictions["backgrounds"] if row["id"] == assay["background_id"]]
        model = matches[0] if len(matches) == 1 else None
        covered = bool(model and model["expected"]["status"] != "UNDETERMINED"
                       and model["expected"]["product_count"] in (0, 1)
                       and model["reference_sha256"] == assay.get("reference_sha256"))
        size = assay.get("observed_band_bp")
        expected_size = model["expected"]["product_bp"] if model else None
        agrees = False
        if assay["result"] == "negative":
            agrees = bool(model and model["expected"]["product_count"] == 0)
        elif model and model["expected"]["product_count"] == 1 and size is not None and expected_size is not None:
            lower = expected_size - assay.get("band_tolerance_bp", 0)
            upper = expected_size + assay.get("band_tolerance_bp", 0)
            agrees = lower <= size <= upper
        domains["assay"].append(({key: assay[key] for key in ("sample_id", "assay_id", "background_id")}, {
            "result": assay["result"], "tested": assay["result"] != "not_tested", "covered": covered,
            "controls_passed": assay.get("control_status") == "passed",
            "determinate": assay["result"] in ("positive", "negative"),
            "size_known": assay["result"] != "positive" or size is not None, "agrees": agrees}))
    if predictions:
        for background in predictions["backgrounds"]:
            if not any(row["assay_id"] == predictions["assay_id"] and row["background_id"] == background["id"] for row in assays):
                domains["assay"].append(({"sample_id": None, "assay_id": predictions["assay_id"],
                                          "background_id": background["id"]}, {"tested": False}))
    conclusions = []
    for path in sorted(Path(rules_dir).glob("*.json")):
        rule = json.loads(path.read_text(encoding="utf-8"))
        if rule.get("schema") != "rule-v1" or rule["status"] != "active":
            continue
        assert rule["source"]["source_class"] in {"literature", "official_method", "project_contract", "lab_protocol", "database_record"}
        for subject, facts in domains[rule["parameters"]["context"]]:
            applicable = applies(facts, rule["applies_when"])
            if applicable is False:
                continue
            selected = [row for row in rule["parameters"]["truth_table"] if applies(facts, row["when"]) is True]
            state, applicability = (selected[0]["status"], "PASS") if applicable is True and len(selected) == 1 else ("INSUFFICIENT", "UNKNOWN")
            if rule["parameters"]["claim"] == "fusion_plate_outgrowth":
                state, applicability = fusion_state(facts["experiment"], facts["control"]), "PASS"
            reason = selected[0]["reason"] if applicability == "PASS" else "Required rule information is missing or ambiguous."
            conclusions.append({"claim": rule["parameters"]["claim"], "subject": subject, "status": state,
                                "applicability": applicability, "reason": reason})
    supported = sorted({row["claim"] for row in conclusions if row["subject"] and row["status"] == "SUPPORTED"})
    for row in conclusions:
        if not row["subject"]:
            row["reason"] += (" " + ("Scoped conclusions supported: " + ", ".join(supported) + "." if supported
                                    else "No scoped conclusion is supported.") +
                              " Not established: genotype confirmation, donor-dependent functional or genetic validation, genome-wide elimination.")
    return observations, conclusions


def verify(observations_file, rules_dir, assessment_file, predictions_file=None, comparisons=None):
    report = json.loads(Path(assessment_file).read_text(encoding="utf-8"))
    reported_comparisons = [{key: row[key] for key in ("experiment_group", "control_group")} for row in report["comparisons"]]
    if comparisons is None:
        comparisons = reported_comparisons
    assert comparisons == reported_comparisons, "Selected comparisons differ from the submitted configuration"
    observations, expected = recompute(observations_file, rules_dir, predictions_file, comparisons)
    assert sorted(map(verdict_key, expected)) == sorted(map(verdict_key, report["conclusions"])), "Conclusion truth table mismatch"
    assert sorted((verdict_key(row), row["reason"]) for row in expected) == sorted(
        (verdict_key(row), row["reason"]) for row in report["conclusions"]), "Conclusion reasons differ"
    counts = {}
    for row in observations:
        counts.setdefault(row["group"], []).append(row)
    total = {name: None if any(row["count"] is None for row in rows) else sum(row["count"] for row in rows)
             for name, rows in counts.items()}
    assert {row["group"]: row["colonies"] for row in report["groups"]} == total, "Missing counts or group sums differ"
    for comparison in report["comparisons"]:
        first, second = comparison["experiment_group"], comparison["control_group"]
        comparable = all(row["unit"] == "colony" for row in counts[first] + counts[second]) and total[first] is not None and total[second] is not None
        difference = total[first] - total[second] if comparable else None
        assert comparison["experiment_colonies"] == total[first] and comparison["control_colonies"] == total[second]
        assert comparison["difference"] == difference and comparison["outcome"] == ("PASS" if comparable else "UNKNOWN"), "Count comparison differs"
    return {"conclusions_compared": len(expected), "groups_compared": len(total),
            "comparisons_compared": len(report["comparisons"]), "result": "PASS",
            "method": "Independent standard-library parsing, count arithmetic and rule-file lookup; S3b states fixed by the user's construction table."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--rules-dir", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--comparisons", type=Path, help="JSON array of submitted comparison pairs; otherwise use the report's declared pairs.")
    args = parser.parse_args()
    comparisons = json.loads(args.comparisons.read_text(encoding="utf-8")) if args.comparisons else None
    print(json.dumps(verify(args.observations, args.rules_dir, args.assessment, args.predictions, comparisons), indent=2))
