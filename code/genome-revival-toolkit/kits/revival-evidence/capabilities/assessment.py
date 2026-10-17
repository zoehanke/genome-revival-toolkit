# ported-from: genome-revival-toolkit/kits/evidence/scripts/predictions.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
"""Facts and finite truth tables. Biological conclusion states live only in data."""
from collections import defaultdict

from dna_design_core.kernel.public import ToolkitError, document_id, require_schema


RULE_PACKS = tuple("kit:revival-evidence/knowledge/" + name + ".json" for name in
                   ("functional_revival", "genome_elimination", "control_absence", "local_prediction",
                    "fusion_plate_outgrowth"))


def read_rules(ctx):
    """ACTION and CHECK use the same hash-checked frozen package interface."""
    return [ctx.knowledge(pack) for pack in RULE_PACKS]


def matches(facts, conditions):
    """D12's closed applicability operators; None means insufficient applicability data."""
    for condition in conditions:
        field, operation, wanted = (condition[key] for key in ("field", "op", "value"))
        if field not in facts:
            return None
        actual = facts[field]
        if operation == "exists":
            result = (actual is not None) == wanted
        elif actual is None:
            return None
        elif operation == "eq":
            result = actual == wanted
        elif operation == "in":
            result = actual in wanted
        elif operation == "gte":
            result = actual >= wanted
        elif operation == "lte":
            result = actual <= wanted
        elif operation == "between":
            result = wanted[0] <= actual <= wanted[1]
        else:
            raise ToolkitError("KNOWLEDGE_SOURCE_INVALID", "Unsupported rule applicability operator.")
        if not result:
            return False
    return True


def conclude(rule, subject, facts):
    """One claim, required evidence, finite truth-table row, bounded conclusion."""
    applicable = matches(facts, rule["applies_when"])
    if applicable is False:
        return None
    data = rule["parameters"]
    rows = [row for row in data["truth_table"] if matches(facts, row["when"]) is True]
    if applicable is None or len(rows) != 1:
        return {"claim": data["claim"], "subject": subject, "status": "INSUFFICIENT",
                "applicability": "UNKNOWN", "reason": "Required rule information is missing or ambiguous.",
                "rule_ref": document_id(rule)}
    row = rows[0]
    return {"claim": data["claim"], "subject": subject, "status": row["status"],
            "applicability": "PASS", "reason": row["reason"], "rule_ref": document_id(rule)}


def assay_contexts(document):
    model = document["predictions"]
    predictions = {} if model is None else {(model["assay_id"], row["id"]): row for row in model["backgrounds"]}
    observed = document["genotype_results"]
    contexts = []
    for row in observed:
        prediction = predictions.get((row["assay_id"], row["background_id"]))
        expected = prediction["expected"] if prediction else None
        band, tolerance = row["observed_band_bp"], row["band_tolerance_bp"]
        reference_matches = bool(prediction and row.get("reference_sha256") == prediction["reference_sha256"])
        covered = bool(expected and expected["status"] != "UNDETERMINED" and reference_matches
                       and expected["product_count"] in {0, 1})
        wanted = expected["product_bp"] if expected else None
        positive = row["result"] == "positive"
        agrees = bool(expected and expected["product_count"] == 0) if row["result"] == "negative" else (
            bool(expected and expected["product_count"] == 1) and wanted is not None and band is not None
            and abs(band - wanted) <= tolerance)
        facts = {"result": row["result"], "tested": row["result"] != "not_tested", "covered": covered,
                 "controls_passed": row["control_status"] == "passed",
                 "determinate": row["result"] in {"positive", "negative"},
                 "size_known": not positive or band is not None, "agrees": agrees}
        contexts.append(({"sample_id": row["sample_id"], "assay_id": row["assay_id"],
                          "background_id": row["background_id"]}, facts))
    seen = {(row["assay_id"], row["background_id"]) for row in observed}
    for assay_id, background_id in predictions.keys() - seen:
        contexts.append(({"sample_id": None, "assay_id": assay_id, "background_id": background_id}, {"tested": False}))
    return sorted(contexts, key=lambda row: (row[0]["assay_id"], row[0]["background_id"], row[0]["sample_id"] or ""))


def count_facts(count, prefix=""):
    """Share the control-absence facts with comparison rules; missing stays missing."""
    return {prefix + "count_known": count is not None,
            prefix + "count_positive": count is not None and count > 0}


def assess(document, rules, comparisons=()):
    groups = defaultdict(list)
    for row in document["observations"]:
        groups[row["group"]].append(row)
    totals = []
    for name, rows in sorted(groups.items()):
        known = all(row["colonies"] is not None for row in rows)
        totals.append({"group": name, "sample_ids": [row["id"] for row in rows],
                       "colonies": sum(row["colonies"] for row in rows) if known else None,
                       "record_count": len(rows), "units": sorted({row["unit"] for row in rows if row["unit"] is not None})})
    differences, comparison_contexts = [], []
    for comparison in comparisons:
        exp, control = (comparison[key] for key in ("experiment_group", "control_group"))
        if exp not in groups or control not in groups:
            raise ToolkitError("PLAN_PARAM_INVALID", "Comparison groups must occur in submitted observations.")
        left, right = (next(row for row in totals if row["group"] == name) for name in (exp, control))
        data = groups[exp] + groups[control]
        known = left["colonies"] is not None and right["colonies"] is not None
        unit_known = all(row["unit"] == "colony" for row in data)
        volumes = {row["plated_volume_uL"] for row in data}
        differences.append({**comparison, "experiment_colonies": left["colonies"], "control_colonies": right["colonies"],
                            "difference": left["colonies"] - right["colonies"] if known and unit_known else None,
                            "outcome": "PASS" if known and unit_known else "UNKNOWN",
                            "equal_reported_plated_volumes": len(volumes) == 1 and None not in volumes,
                            "limits": ["Raw reported colony-count difference; not efficiency or a causal effect."]})
        comparison_contexts.append((dict(comparison), {
            **count_facts(left["colonies"]), **count_facts(right["colonies"], "control_")}))
    counts = any(row["colonies"] is not None for row in document["observations"])
    genotypes = any(row["result"] != "not_tested" for row in document["genotype_results"])
    functional = any(row["result"] != "not_tested" for row in document["functional_results"])
    contexts = {"summary": [({}, {"observed_counts": counts, "tested_genotypes": genotypes,
                                  "tested_function": functional, "any_tested": counts or genotypes or functional})],
                "observation": [({"sample_id": row["id"]}, {"role": row["role"],
                    **count_facts(row["colonies"])}) for row in document["observations"]],
                "assay": assay_contexts(document), "comparison": comparison_contexts}
    conclusions, used = [], []
    for rule in sorted(rules, key=lambda row: row["id"]):
        require_schema("rule-v1", rule, "KNOWLEDGE_SOURCE_INVALID")
        if rule["status"] != "active":
            continue
        used.append(document_id(rule))
        data = rule["parameters"]
        for subject, facts in contexts[data["context"]]:
            result = conclude(rule, subject, facts)
            if result is not None:
                conclusions.append(result)
    supported = sorted({row["claim"] for row in conclusions if row["subject"] and row["status"] == "SUPPORTED"})
    progress = ("Scoped conclusions supported: " + ", ".join(supported) + "." if supported
                else "No scoped conclusion is supported.")
    for row in conclusions:
        if not row["subject"]:
            row["reason"] += (" " + progress + " Not established: genotype confirmation, donor-dependent "
                              "functional or genetic validation, genome-wide elimination.")
    conclusions.sort(key=lambda row: row["status"] != "SUPPORTED")
    unverified = list(document["unverified"])
    for row in document["genotype_results"]:
        if row["result"] != "not_tested" and row["control_status"] != "passed":
            unverified.append("Assay controls were not confirmed as passed (reported control_status=" +
                row["control_status"] + ") for sample " + row["sample_id"] + ", assay " + row["assay_id"] +
                ", background " + row["background_id"] + ". Report comparison does not authenticate the observation or genotype.")
    if not genotypes:
        unverified.append("PCR and genetic evidence: NOT_PERFORMED; genotype observations were not supplied.")
    if not functional:
        unverified.append("Functional validation: NOT_PERFORMED; functional observations were not supplied.")
    unverified.extend(["Whole-genome origin, elimination and causal dependencies were not tested.",
                       "Rules are AI drafted and have no human review; source verification remains unverified.",
                       "Biological replication and comparability of reported conditions were not established."])
    return {"conclusions": conclusions, "groups": totals, "comparisons": differences,
            "genotype_tests": "INSUFFICIENT" if genotypes else "NOT_TESTED",
            "functional_tests": "INSUFFICIENT" if functional else "NOT_TESTED",
            "observation_origin": document["observation_origin"], "rule_refs": used,
            "input_files": document["input_files"], "generated_ids": document["generated_ids"],
            "unverified": unverified,
            "limits": ["Only submitted records and local predictions are compared.",
                       "Colony formation alone does not establish functional revival.",
                       "Local PCR does not establish whole-genome identity or elimination."]}
