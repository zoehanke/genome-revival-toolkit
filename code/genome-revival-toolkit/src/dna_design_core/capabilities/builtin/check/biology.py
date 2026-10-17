"""Read-only scientific checks using recorded materials and actual output files."""
from pathlib import Path

from dna_design_core.kernel.public import Outcome, ToolkitError, capability, core_version, make, material_id
from dna_design_core.biology.public import (
    evaluate_primer_quality, material_from_genbank, material_from_record, primer_quality, read_fasta,
)
from .._biology import declaration
from ...reactions import run as replay_reactions
from ...primer_assessment import assess as assess_preparation_primers

MODULE = __name__
HASHES = {"type": "array", "items": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "minItems": 1, "maxItems": 2}
LIMITS = {"type": ["object", "null"], "additionalProperties": False,
          "properties": {**{name: {"type": "integer", "minimum": 0} for name in (
              "length_min", "length_max", "max_T_run", "max_3prime_dimer", "max_hairpin_stem")},
              "gc_min": {"type": "string"}, "gc_max": {"type": "string"}},
          "required": ["length_min", "length_max", "gc_min", "gc_max", "max_T_run", "max_3prime_dimer", "max_hairpin_stem"]}


def _verdict(ctx, identity, scope, outcome, summary, evidence=None):
    candidate, events = ctx.view.candidate, ctx.view.events()
    applicability = {"reason": summary, "basis": [events[0]["hash"]]} if outcome == "NOT_APPLICABLE" else None
    return Outcome(verdicts=[make(check={"id": identity, "version": core_version()}, scope=scope,
        moment=candidate.get("moment", "final"), issuer=candidate.get("issuer", "check_capability"),
        subject={"kind": "run", "id": events[0]["run_id"]}, outcome=outcome, summary=summary,
        evidence=evidence or {}, basis=[event["hash"] for event in events], applicability=applicability,
        constraint_id=candidate.get("constraint", {}).get("id"),
        does_not_establish=["Experimental success or biological function.", "Independence of the shared calculation implementation."])])


@capability(declaration("check.primer_quality", "Discover marked preparation primers and assess explicit criteria; retain the explicit-limits API.", MODULE, "check_primer_quality",
    [], [], {"material_ids": HASHES, "limits": LIMITS, "min_loop": {"type": "integer", "minimum": 0}}, scope="preparation_model", effects=("reads_files",)))
def check_primer_quality(ctx: object, material_ids: list | None = None, limits: dict | None = None, min_loop: int = 3) -> Outcome:
    if material_ids is None and limits is None:
        return assess_preparation_primers(ctx)
    if limits is None:
        return _verdict(ctx, "check.primer_quality", "preparation_model", "UNKNOWN", "Explicit primer-quality limits are required.")
    identities = material_ids or [row["id"] for row in ctx.view.candidate.get("outputs", []) if row.get("kind") == "material"]
    if not identities:
        return _verdict(ctx, "check.primer_quality", "preparation_model", "UNKNOWN", "No retained primer material was selected.")
    if len(identities) > 2:
        return _verdict(ctx, "check.primer_quality", "preparation_model", "UNKNOWN", "Select one primer or one explicit primer pair per quality check.")
    rows = []
    try:
        materials = [ctx.view.material(identity) for identity in identities]
        if any(value["strandedness"] != "single" for value in materials):
            return _verdict(ctx, "check.primer_quality", "preparation_model", "UNKNOWN", "Select explicitly single-stranded complete primer materials.")
        for index, (identity, value) in enumerate(zip(identities, materials)):
            partner = materials[1 - index]["sequence"] if len(materials) == 2 else None
            metrics = primer_quality(value["sequence"], partner=partner, min_loop=min_loop)
            assessed = evaluate_primer_quality(metrics, limits)
            rows.append({"material_id": identity, "metrics": metrics, "violations": assessed["violations"]})
    except (ToolkitError, ValueError, KeyError, TypeError):
        return _verdict(ctx, "check.primer_quality", "preparation_model", "UNKNOWN", "Primer materials or explicit quality parameters are unavailable or invalid.")
    return _verdict(ctx, "check.primer_quality", "preparation_model", "FAIL" if any(row["violations"] for row in rows) else "PASS",
                    "Full oligos evaluated against explicit exact-complementarity limits.", {"primers": rows, "limits": limits})


@capability(declaration("check.format_roundtrip", "Read actual exported DNA files and compare complete kernel material identities.", MODULE, "check_format_roundtrip",
    [], [], scope="file", effects=("reads_files",), offline=False))
def check_format_roundtrip(ctx: object) -> Outcome:
    found, differences = 0, []
    try:
        for step in ctx.view.steps():
            name = step["definition"]["use"].split("@")[0]
            if name not in ("format.write_genbank", "format.write_fasta") or not step["completed"] or step["superseded"]:
                continue
            found += 1
            identity = step["started"]["payload"]["inputs"]["material"]["id"]
            artifact = step["completed"]["payload"]["outputs"]["artifacts"][0]
            path = (ctx.view.root / artifact["run_path"]).resolve()
            if not path.is_relative_to(ctx.view.root.resolve()):
                raise ValueError("artifact outside run")
            text = path.read_text(encoding="utf-8")
            loaded = material_from_genbank(text) if name == "format.write_genbank" else material_from_record(read_fasta(text))
            if material_id(loaded) != identity:
                differences.append(step["definition"]["step_id"])
    except (OSError, ToolkitError, ValueError, KeyError):
        return _verdict(ctx, "check.format_roundtrip", "file", "FAIL", "Exported material cannot be read back consistently.")
    if not found:
        return _verdict(ctx, "check.format_roundtrip", "file", "NOT_APPLICABLE", "No supported DNA file exporter was used.")
    return _verdict(ctx, "check.format_roundtrip", "file", "FAIL" if differences else "PASS", "Exported material identities compared.", {"different_steps": differences})



def _reaction_declaration(identity, function, summary):
    value=declaration(identity,summary,MODULE,function,[],[],scope="preparation_model",effects=("reads_files",))
    value["granularity"]="composite"
    return value


@capability(_reaction_declaration("check.pcr_product","check_pcr_product",
    "Recompute direct and nested PCR from actual recorded inputs and parameters."))
def check_pcr_product(ctx: object) -> Outcome:
    return replay_reactions(ctx,"check.pcr_product",names={"pcr.simulate"})


@capability(_reaction_declaration("check.assembly_product","check_assembly_product",
    "Recompute direct and nested digest, ligation, overlap and inverse-PCR products."))
def check_assembly_product(ctx: object) -> Outcome:
    return replay_reactions(ctx,"check.assembly_product",names={"restriction.digest","assembly.ligate","assembly.gibson","assembly.inverse_pcr"})
