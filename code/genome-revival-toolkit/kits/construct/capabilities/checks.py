"""Read-only checks on actual retained sources, oligos, reactions and assays."""
from dna_design_core.kernel.public import Outcome, ToolkitError, capability, core_version, make, material_id
from dna_design_core.biology.public import gibson_material, pcr_material
from .assay import assay_failures, predictions
from .contracts import LIMITS, declaration


def verdict(ctx: object, identity: str, outcome: str, summary: str, evidence: dict) -> Outcome:
    events, candidate = ctx.view.events(), ctx.view.candidate
    return Outcome(verdicts=[make(check={"id": identity, "version": core_version()}, scope="preparation_model",
        moment=candidate.get("moment", "final"), issuer=candidate.get("issuer", "check_capability"),
        subject={"kind": "run", "id": events[0]["run_id"]}, outcome=outcome, summary=summary,
        evidence=evidence, basis=[row["hash"] for row in events], does_not_establish=LIMITS)])


@capability(declaration("construct.check_preparation", "construct.capabilities.checks", "check_preparation",
    "Recompute every retained donor reaction from actual templates and complete primers.",
    [], [], {}, effects=("reads_files",), scope="preparation_model"))
def check_preparation(ctx: object) -> Outcome:
    found, differences = 0, []
    try:
        for step in ctx.view.steps():
            if step["definition"]["use"].split("@")[0] != "construct.design_donor" or not step["completed"] or step["superseded"]:
                continue
            found += 1
            completed, started = step["completed"]["payload"], step["started"]["payload"]
            route = ctx.view.document(completed["outputs"]["documents"]["route"][0])
            if any(route[name + "_id"] != started["inputs"][name]["id"] for name in ("reference", "cargo")):
                differences.append(step["definition"]["step_id"] + ": source bindings")
            computed = {}
            for reaction in route["reactions"]:
                materials = [computed[identity] if identity in computed else ctx.view.material(identity) for identity in reaction["inputs"]]
                if reaction["method"] == "pcr":
                    result = pcr_material(*materials, **reaction["params"])[0]
                else:
                    result = gibson_material(*materials, **reaction["params"])
                identity = material_id(result)
                if identity != reaction["product_id"]:
                    differences.append(reaction["id"])
                computed[reaction["product_id"]] = result
            # The actual candidate is consulted only after all reactions were recomputed.
            actual = completed["outputs"]["materials"]["product"][0]
            if not route["reactions"] or material_id(result) != actual:
                differences.append(step["definition"]["step_id"] + ": final product")
    except (ToolkitError, ValueError, KeyError, TypeError, IndexError):
        return verdict(ctx, "construct.check_preparation", "UNKNOWN", "Donor reaction records cannot be recomputed.", {"steps_checked": found})
    return verdict(ctx, "construct.check_preparation", "FAIL" if differences else "PASS" if found else "UNKNOWN",
                   "Source-derived PCR and Gibson products compared.", {"steps_checked": found, "differences": differences})


@capability(declaration("construct.check_junction_assay", "construct.capabilities.checks", "check_junction_assay",
    "Recompute junction products and reject residual donor bands or ambiguous binding.",
    [], [], {}, effects=("reads_files",), scope="preparation_model"))
def check_junction_assay(ctx: object) -> Outcome:
    found, differences, warnings = 0, [], []
    try:
        for step in ctx.view.steps():
            if step["definition"]["use"].split("@")[0] != "construct.design_junction_assay" or not step["completed"] or step["superseded"]:
                continue
            found += 1
            report = ctx.view.document(step["completed"]["payload"]["outputs"]["documents"]["assay"][0])
            bindings = step["started"]["payload"]["inputs"]
            materials = {name: ctx.view.material(bindings[name]["id"]) for name in ("original", "edited", "donor")}
            if any(report[name + "_id"] != bindings[name]["id"] for name in materials):
                differences.append("assay source binding")
            backgrounds, messages = predictions(materials, report["primers"])
            if backgrounds != report["backgrounds"] or messages != report["warnings"]:
                differences.append("recorded predictions differ from recomputation")
            differences.extend(assay_failures(backgrounds))
            warnings.extend(messages)
    except (ToolkitError, ValueError, KeyError, TypeError):
        return verdict(ctx, "construct.check_junction_assay", "UNKNOWN", "Assay inputs or records are unavailable.", {"assays_checked": found})
    return verdict(ctx, "construct.check_junction_assay", "FAIL" if differences else "PASS" if found else "UNKNOWN",
                   "Edited, original and residual donor backgrounds compared.",
                   {"assays_checked": found, "differences": differences, "warnings": warnings})
