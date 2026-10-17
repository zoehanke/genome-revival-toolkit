# ported-from: genome-revival-toolkit/revival/construct.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Explicit junction primers, three-background predictions and donor warning."""
from copy import deepcopy
from pathlib import Path

from dna_design_core.kernel.public import Outcome, ToolkitError, capability, loads, material_id, require_schema
from dna_design_core.biology.public import find_binding_sites, predict_pcr_products, reverse_complement
from .contracts import ASSAY, INTEGER, PRIMERS, declaration, port

ASSAY_PARAMS = {"start": INTEGER, "end": INTEGER, "arm_length": {"type": "integer", "minimum": 1},
                "primer_length": {"type": "integer", "minimum": 2}}


def predictions(materials: dict, primers: dict) -> tuple[list, list]:
    names = [row["id"] for row in primers["primers"]]
    pair_names = [row["id"] for row in primers["pairs"]]
    by_id = {row["id"]: row for row in primers["primers"]}
    if len(set(names)) != len(names) or len(set(pair_names)) != len(pair_names):
        raise ValueError("primer and pair ids must be unique")
    if any(row["core_length"] != len(row["sequence"]) for row in by_id.values()):
        raise ValueError("junction primers must be complete untailored binding cores")
    if any(pair[key] not in by_id for pair in primers["pairs"] for key in ("forward", "reverse")):
        raise ValueError("primer pair references an absent primer")
    backgrounds, warnings = [], []
    for name in ("original", "edited", "donor"):
        material, rows = materials[name], []
        if material["topology"] != "linear" or material["strandedness"] != "double":
            raise ValueError("junction predictions require explicitly linear duplex backgrounds")
        sequence = material["sequence"]
        for pair in primers["pairs"]:
            forward, reverse = (by_id[pair[key]]["sequence"] for key in ("forward", "reverse"))
            products = predict_pcr_products(sequence, forward, reverse)
            forward_sites, reverse_sites = len(find_binding_sites(sequence, forward)), len(find_binding_sites(sequence, reverse))
            rows.append({"pair_id": pair["id"], "product_count": len(products),
                         "product_bp": len(products[0]["sequence"]) if len(products) == 1 else None,
                         "forward_sites": forward_sites, "reverse_sites": reverse_sites})
            if forward_sites > 1 or reverse_sites > 1:
                warnings.append(name + ": " + pair["id"] + " has repeated primer binding sites; uniqueness is unresolved.")
            if name == "donor" and products:
                warnings.append(pair["id"] + ": residual donor DNA also yields a band. Primers inside donor homology arms cannot establish genomic integration.")
        backgrounds.append({"id": name, "predictions": rows})
    return backgrounds, warnings


def assay_failures(backgrounds: list) -> list:
    by_id = {row["id"]: {p["pair_id"]: p for p in row["predictions"]} for row in backgrounds}
    failures = []
    for pair_id, edited in by_id["edited"].items():
        original, donor = by_id["original"][pair_id], by_id["donor"][pair_id]
        if edited["product_count"] != 1 or edited["forward_sites"] != 1 or edited["reverse_sites"] != 1:
            failures.append(pair_id + ": edited reference has no unique product")
        if donor["product_count"]:
            failures.append(pair_id + ": donor carry-over yields a product")
        if any(row["forward_sites"] > 1 or row["reverse_sites"] > 1 for row in (original, donor)):
            failures.append(pair_id + ": repeated background binding sites")
        if original["product_count"] > 1 or original["product_count"] == 1 and original["product_bp"] == edited["product_bp"]:
            failures.append(pair_id + ": original and edited references are not distinguished")
    return failures


@capability(declaration("construct.design_junction_assay", "construct.capabilities.assay", "design_junction_assay",
    "Design external junction primers or assess supplied primers on original, edited and donor backgrounds.",
    [port("original"), port("edited"), port("donor"), port("primer_file", "artifact", required=False)],
    [port("primers", "document", schema=PRIMERS, output=True, output_role="primer_set"),
     port("assay", "document", schema=ASSAY, output=True, output_role="analysis")],
    ASSAY_PARAMS, effects=("reads_files",), checks=("construct.check_junction_assay",)))
def design_junction_assay(ctx: object, original: dict, edited: dict, donor: dict, start: int,
                          end: int, arm_length: int, primer_length: int, primer_file: Path | None = None) -> Outcome:
    primers = None
    if primer_file is not None:
        primers = require_schema(PRIMERS, loads(Path(primer_file).read_bytes()), "PLAN_PARAM_INVALID")
    inserted_length = len(edited["sequence"]) - len(original["sequence"]) + end - start
    if not (0 <= start <= end <= len(original["sequence"]) and inserted_length >= 0
            and start >= arm_length and end + arm_length <= len(original["sequence"])):
        raise ToolkitError("PLAN_PARAM_INVALID", "Invalid junction or homology-arm interval.")
    if edited["sequence"][:start] != original["sequence"][:start] or edited["sequence"][start + inserted_length:] != original["sequence"][end:]:
        raise ToolkitError("PLAN_PARAM_INVALID", "Edited reference changes sequence outside the declared replacement.")
    regions = [{"id": "replacement", "reference_id": "edited", "start": start, "end": start + inserted_length},
               {"id": "left_arm", "reference_id": "edited", "start": start - arm_length, "end": start},
               {"id": "right_arm", "reference_id": "edited", "start": start + inserted_length,
                "end": start + inserted_length + arm_length}]
    if primers is None:
        if start - arm_length < primer_length or end + arm_length + primer_length > len(original["sequence"]):
            raise ToolkitError("PLAN_PARAM_INVALID", "Reference lacks sequence outside homology arms for junction primers.")
        if inserted_length and inserted_length < primer_length:
            raise ToolkitError("PLAN_PARAM_INVALID", "Cargo is shorter than the explicitly selected junction-primer length.")
        # PROVISIONAL(S5A-P2): fixed external/cargo geometry; no hidden primer ranking.
        external_forward = original["sequence"][start - arm_length - primer_length:start - arm_length]
        external_reverse = reverse_complement(original["sequence"][end + arm_length:end + arm_length + primer_length])
        if inserted_length:
            sequences = [("left_forward", external_forward),
                         ("left_reverse", reverse_complement(edited["sequence"][start:start + primer_length])),
                         ("right_forward", edited["sequence"][start + inserted_length - primer_length:start + inserted_length]),
                         ("right_reverse", external_reverse)]
            pairs = [{"id": side, "forward": side + "_forward", "reverse": side + "_reverse"} for side in ("left", "right")]
        else:
            sequences = [("flanking_forward", external_forward), ("flanking_reverse", external_reverse)]
            pairs = [{"id": "flanking", "forward": "flanking_forward", "reverse": "flanking_reverse"}]
        primers = {"schema": "primer-set-v1", "primers": [{"id": name, "sequence": sequence, "core_length": len(sequence), "purpose": "junction_qc"}
                   for name, sequence in sequences], "pairs": pairs}
    try:
        backgrounds, warnings = predictions({"original": original, "edited": edited, "donor": donor}, primers)
    except (ValueError, KeyError, TypeError) as error:
        raise ToolkitError("PLAN_PARAM_INVALID", "Junction primer document is inconsistent.") from error
    return Outcome(documents={"primers": deepcopy(primers), "assay": {
        "schema": "junction-assay-v1", "original_id": material_id(original), "edited_id": material_id(edited),
        "donor_id": material_id(donor), "primers": deepcopy(primers), "regions": regions, "backgrounds": backgrounds, "warnings": warnings}},
        unverified=warnings + ["PLANNED junction PCR; NOT_PERFORMED in the laboratory.", "Predictions cover only supplied references and residual donor DNA."])
