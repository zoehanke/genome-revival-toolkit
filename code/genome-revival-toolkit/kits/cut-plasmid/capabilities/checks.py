"""Final read-only checks recompute from recorded materials, not action reports."""
from dna_design_core.kernel.public import Outcome, ToolkitError, capability, make
from .contracts import VERSION, declaration
from .guide import inspect


def _reports(ctx):
    rows = []
    for step in ctx.view.steps():
        name = step["definition"]["use"].split("@")[0]
        if name not in ("cut_plasmid.inspect_guide", "cut_plasmid.replace_spacer") or not step["completed"] or step["superseded"]:
            continue
        inputs = step["started"]["payload"]["inputs"]
        vector_id = (step["completed"]["payload"]["outputs"]["materials"]["product"][0]
                     if name == "cut_plasmid.replace_spacer" else inputs["vector"]["id"])
        params = step["started"]["payload"]["params"]
        report = inspect(ctx.view.material(vector_id), ctx.view.material(inputs["target"]["id"]),
                         params["promoter_end"], params["transcription_strand"], params["scaffold_sequence"], params.get("vector_max_mismatches", 3))
        rows.append((step["definition"]["step_id"], report))
    return rows


def _check(ctx, name):
    events, candidate = ctx.view.events(), ctx.view.candidate
    results = []
    try:
        for step_id, report in _reports(ctx):
            if name == "check_direction":
                outcome = ("UNKNOWN" if not report["orientation_distinguishable"] or report["direction_correct"] is None
                           else "PASS" if report["direction_correct"] else "FAIL")
            elif name == "check_pam":
                outcome = "PASS" if report["pam_valid"] else "FAIL"
            else:
                exact = any(hit["mismatches"] == 0 for hit in report["vector_self_targets"])
                # PROVISIONAL(S2-Q4): exact self-target fails; bounded near matches are unresolved risk.
                outcome = "FAIL" if exact else "UNKNOWN" if report["vector_self_targets"] or not report["vector_search_complete"] else "PASS"
            results.append({"step_id": step_id, "vector_id": report["vector_id"], "target_id": report["target_id"],
                            "outcome": outcome, "direction_status": report["direction_status"],
                            "valid_target_locus_count": report["valid_target_locus_count"],
                            "vector_self_target_count": len(report["vector_self_targets"]),
                            "vector_max_mismatches": report["vector_max_mismatches"],
                            "vector_search_complete": report["vector_search_complete"],
                            "annotation_findings": report["annotation_findings"]})
    except (ToolkitError, KeyError, ValueError, TypeError):
        outcome = "UNKNOWN"
        summary = "Recorded cassette inputs cannot be recomputed."
    else:
        outcome = "FAIL" if any(row["outcome"] == "FAIL" for row in results) else "UNKNOWN" if not results or any(row["outcome"] == "UNKNOWN" for row in results) else "PASS"
        summary = "Recomputed supplied-sequence " + name.removeprefix("check_").replace("_", " ") + "."
    return Outcome(verdicts=[make(check={"id": "cut_plasmid." + name, "version": VERSION},
        scope="content_model", moment=candidate.get("moment", "final"), issuer=candidate.get("issuer", "check_capability"),
        subject={"kind": "run", "id": events[0]["run_id"]}, outcome=outcome, summary=summary,
        evidence={"results": results}, basis=[event["hash"] for event in events if event["type"] in ("step.started", "step.completed")],
        does_not_establish=["Cleavage activity", "Editing efficiency", "Genome-wide off-target safety"])])


@capability(declaration("check_direction", "checks", "check_direction", [], [], {}, scope="content_model"))
def check_direction(ctx: object) -> Outcome:
    return _check(ctx, "check_direction")


@capability(declaration("check_pam", "checks", "check_pam", [], [], {}, scope="content_model"))
def check_pam(ctx: object) -> Outcome:
    return _check(ctx, "check_pam")


@capability(declaration("check_vector_self_target", "checks", "check_vector_self_target", [], [], {}, scope="content_model"))
def check_vector_self_target(ctx: object) -> Outcome:
    return _check(ctx, "check_vector_self_target")
