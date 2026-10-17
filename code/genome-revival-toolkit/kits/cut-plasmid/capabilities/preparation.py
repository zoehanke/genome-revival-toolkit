# ported-from: snapgene-dna-design/core/tools/grna_preparation.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
"""Guide replacement plus separately computed inverse-PCR sequence preparation."""
from copy import deepcopy
from decimal import Decimal, InvalidOperation

from Bio.SeqUtils.MeltingTemp import DNA_NN3, Tm_NN
from dna_design_core.kernel.public import Outcome, ToolkitError, capability, core_version, document_id, make, material_id
from dna_design_core.biology.public import find_binding_sites, make_material, reverse_complement
from .contracts import (CASSETTE_PARAMS, DEFAULT_TM, DESIGN_PARAMS, FINAL_CHECKS, PRIMERS, ROUTE,
                        SPACER, VECTOR_SEARCH, declaration, material_port, output)
from .guide import cassette


def tm_inputs(parameters):
    result = {}
    try:
        for name in ("dnac1_nM", "dnac2_nM", "Na_mM", "K_mM", "Tris_mM", "Mg_mM", "dNTPs_mM"):
            value = Decimal(parameters[name])
            if not value.is_finite() or value < 0:
                raise ValueError("nonnegative finite concentration required")
            result[name] = float(value)
        if result["dnac1_nM"] <= result["dnac2_nM"] / 2 or not any(result[name] for name in ("Na_mM", "K_mM", "Tris_mM", "Mg_mM")):
            raise ValueError("positive effective strand concentration and salt required")
    except (InvalidOperation, ValueError, KeyError) as error:
        raise ToolkitError("PLAN_PARAM_INVALID", "Invalid explicit Tm concentrations.") from error
    return result


def choose_primer(sequence, anchor, strand, tail, minimum, maximum, tm_min, tm_max, parameters):
    size = len(sequence)
    numeric = tm_inputs(parameters)
    try:
        lo, hi = Decimal(tm_min), Decimal(tm_max)
    except InvalidOperation as error:
        raise ToolkitError("PLAN_PARAM_INVALID", "Tm limits must be finite decimal strings.") from error
    if not lo.is_finite() or not hi.is_finite() or lo > hi or not 2 <= minimum <= maximum <= size - 20:
        raise ToolkitError("PLAN_PARAM_INVALID", "Explicit primer length and Tm windows are inconsistent.")
    in_window, ambiguous = 0, 0
    for length in range(minimum, maximum + 1):
        start = anchor if strand == 1 else anchor - length
        reference = "".join(sequence[index % size] for index in range(start, start + length))
        core = reference if strand == 1 else reverse_complement(reference)
        # PROVISIONAL(S2-Q2): exact B2 NN parameters, explicitly retained in output.
        tm = Tm_NN(core, nn_table=DNA_NN3, check=False, strict=True,
                   dnac1=numeric["dnac1_nM"], dnac2=numeric["dnac2_nM"],
                   Na=numeric["Na_mM"], K=numeric["K_mM"], Tris=numeric["Tris_mM"],
                   Mg=numeric["Mg_mM"], dNTPs=numeric["dNTPs_mM"], saltcorr=parameters["saltcorr"], selfcomp=parameters["selfcomp"])
        if not lo <= Decimal(str(tm)) <= hi:
            continue
        in_window += 1
        hits = find_binding_sites(sequence, tail + core, core_length=length, circular=True)
        if len(hits) != 1 or hits[0]["strand"] != strand or hits[0]["start"] != start % size:
            ambiguous += 1
            continue
        return {"id": "forward" if strand == 1 else "reverse", "sequence": tail + core,
                "binding_core": core, "tail_5prime": tail, "core_length": length, "length": len(tail + core),
                "strand": strand, "reference_start": start % size, "reference_end_unwrapped": start % size + length,
                "binding_site_count": 1, "tm_degC": format(tm, ".8f")}
    raise ToolkitError("PLAN_PARAM_INVALID", "No unique primer satisfies the stated length and Tm windows.",
                       {"strand": strand, "length_min": minimum, "length_max": maximum,
                        "tm_min": tm_min, "tm_max": tm_max, "in_window_count": in_window,
                        "ambiguous_binding_count": ambiguous})


REPLACE_DECLARATION = declaration("replace_spacer", "preparation", "replace_spacer",
    [material_port("vector"), material_port("target")],
    [output("product", "material", "construct"), output("primers", "document", "primer_set", PRIMERS),
     output("route", "document", None, ROUTE)],
    {**CASSETTE_PARAMS, "spacer": SPACER, **DESIGN_PARAMS, **VECTOR_SEARCH}, required=list(CASSETTE_PARAMS) + ["spacer"],
    composite=True, model="cut_plasmid.model_replace", final_checks=FINAL_CHECKS,
    step_checks=["check.primer_quality"])


@capability(REPLACE_DECLARATION)
def replace_spacer(ctx: object, vector: dict, target: dict, promoter_end: int, transcription_strand: int,
                   scaffold_sequence: str, spacer: str, length_min: int = 18, length_max: int = 36,
                   tm_min: str = "55", tm_max: str = "62", tm_parameters: dict | None = None,
                   vector_max_mismatches: int = 3) -> Outcome:
    if vector["topology"] != "circular" or vector["strandedness"] != "double":
        raise ToolkitError("PLAN_PARAM_INVALID", "Inverse-PCR replacement requires a circular double-stranded template.")
    _, positions, parts = cassette(vector, promoter_end, transcription_strand, scaffold_sequence)
    size = len(vector["sequence"])
    start = promoter_end % size if transcription_strand == 1 else (promoter_end - 20) % size
    end = (start + 20) % size
    insert_sequence = spacer if transcription_strand == 1 else reverse_complement(spacer)
    insert = make_material(insert_sequence, topology="linear", strandedness="double")
    # Explicit rotations make a wrapping edit a normal nonwrapping Core operation.
    rotated = ctx.call("seq.rotate", inputs={"material": vector}, params={"origin": start}).products["material"]
    edited = ctx.call("seq.replace_region", inputs={"material": rotated, "insert": insert}, params={"start": 0, "end": 20})
    product = ctx.call("seq.rotate", inputs={"material": edited.products["product"]}, params={"origin": (size - start) % size}).products["material"]
    # Preserve all untouched annotations and explicitly retire intersecting ones.
    retired = []
    for index, feature in enumerate(vector["features"]):
        feature_parts = feature.get("parts") or [{"start": feature["start"], "end": feature["end"]}]
        if any(part["start"] <= position < part["end"] for part in feature_parts for position in positions):
            retired.append({"index": index, "type": feature["type"], "reason": "Feature intersects the replaced spacer; intact function is not asserted."})
    product["features"].append({"start": min(p[0] for p in parts), "end": max(p[1] for p in parts),
                                "type": "misc_RNA", "label": "gRNA spacer",
                                "parts": [{"start": left, "end": right, "strand": transcription_strand} for left, right in parts],
                                "operator": "join" if len(parts) > 1 else None,
                                "qualifiers": {"label": ["gRNA spacer"]}})
    product = make_material(**product)
    tm_parameters = deepcopy(DEFAULT_TM if tm_parameters is None else tm_parameters)
    forward = choose_primer(vector["sequence"], end, 1, "", length_min, length_max, tm_min, tm_max, tm_parameters)
    reverse = choose_primer(vector["sequence"], start, -1, reverse_complement(insert_sequence),
                            length_min, length_max, tm_min, tm_max, tm_parameters)
    preparation = ctx.call("assembly.inverse_pcr", inputs={"template": vector,
        "forward": make_material(forward["sequence"], topology="linear", strandedness="single"),
        "reverse": make_material(reverse["sequence"], topology="linear", strandedness="single")},
        params={"forward_core_length": forward["core_length"], "reverse_core_length": reverse["core_length"], "closing_overlap": 0})
    rotation = (size - end) % size
    simulation = ctx.call("seq.rotate", inputs={"material": preparation.products["product"]}, params={"origin": rotation}).products["material"]
    if (simulation["sequence"], simulation["topology"], simulation["ends"]) != (product["sequence"], product["topology"], product["ends"]):
        raise ToolkitError("CAPABILITY_OUTPUT_INVALID", "Inverse PCR and circularization disagree with the independently edited circle.")
    notes = ["Hairpins, dimers and purification were not assessed."]
    if any(base * 6 in row["sequence"] for row in (forward, reverse) for base in "ACGT"):
        notes.append("Complete oligo contains a homopolymer run of at least six bases; retained as evidence, not a v1 failure.")
    primer_document = {"schema": "primer-set-v1", "template_id": material_id(vector), "primers": [forward, reverse],
                       "length_min": length_min, "length_max": length_max, "tm_min": tm_min, "tm_max": tm_max,
                       "tm_parameters": tm_parameters, "quality_notes": notes}
    labs = [{"step": name, "status": "PLANNED", "performed": "NOT_PERFORMED"}
            for name in ("inverse PCR", "DpnI template removal", "KLD circularization", "transformation", "sequencing", "gRNA activity")]
    route = {"schema": "route-plan-v1", "method": "inverse_pcr", "template_id": material_id(vector),
             "product_id": material_id(product), "spacer_parts": parts, "transcription_strand": transcription_strand,
             "reference_insert": insert_sequence, "forward_primer_id": forward["id"], "reverse_primer_id": reverse["id"],
             "closing_overlap": 0, "rotation_to_template_origin": rotation,
             "simulation": {"status": "PASS", "linear_sequence": preparation.products["intermediate"]["sequence"],
                            "product_length": len(simulation["sequence"]), "circular_sequence_matches": True},
             "annotation_changes": retired, "laboratory_steps": labs}
    self_report = make(check={"id": "check.primer_quality", "version": core_version()}, scope="preparation_model",
        moment="step", issuer="tool_self_report", subject={"kind": "document", "id": document_id(primer_document)},
        outcome="PASS", summary="Selected unique binding cores meet the explicit length and NN Tm windows.",
        evidence={"forward_core_length": forward["core_length"], "reverse_core_length": reverse["core_length"],
                  "forward_tm_degC": forward["tm_degC"], "reverse_tm_degC": reverse["tm_degC"]},
        does_not_establish=["Full-oligo thermodynamic structure or physical PCR."])
    return Outcome(products={"product": product}, documents={"primers": primer_document, "route": route},
        verdicts=[self_report], unverified=notes + [name + ": PLANNED / NOT_PERFORMED" for name in (row["step"] for row in labs)])
