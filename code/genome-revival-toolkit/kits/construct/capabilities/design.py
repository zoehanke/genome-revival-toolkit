# ported-from: genome-revival-toolkit/revival/construct.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Prepare from actual templates. The expected-model function is never called."""
from dna_design_core.kernel.public import Outcome, ToolkitError, capability, material_id
from dna_design_core.biology.public import (
    find_binding_sites, make_material, replace_material_region, reverse_complement, slice_material,
)
from .contracts import BOUNDS, INTEGER, PRIMERS, ROUTE, declaration, port

PARAMETERS = {**BOUNDS, "preparation_method": {"enum": ["gibson", "pcr"]},
              "primer_length": {"type": "integer", "minimum": 2},
              "overlap": {"type": "integer", "minimum": 1}, "donor_start": INTEGER, "donor_end": INTEGER}


@capability(declaration("construct.design_donor", "construct.capabilities.design", "design_donor",
    "Prepare a linear donor by explicit PCR or PCR-fragment Gibson assembly.",
    [port("reference"), port("cargo"), port("donor_template", required=False)],
    [port("product", output=True, output_role="construct"), port("edited", output=True),
     port("oligos", "materials", output=True), port("intermediates", "materials", output=True),
     port("primers", "document", schema=PRIMERS, output=True, output_role="primer_set"),
     port("route", "document", schema=ROUTE, output=True, output_role="analysis")],
    PARAMETERS, list(BOUNDS) + ["preparation_method", "primer_length"], composite=True,
    model="construct.model_donor", checks=("construct.check_preparation",)))
def design_donor(ctx: object, reference: dict, cargo: dict, start: int, end: int, arm_length: int,
                 cargo_start: int, cargo_end: int, preparation_method: str, primer_length: int,
                 donor_template: dict | None = None, overlap: int | None = None,
                 donor_start: int | None = None, donor_end: int | None = None) -> Outcome:
    if reference["topology"] != "linear" or reference["strandedness"] != "double" or cargo["strandedness"] != "double":
        raise ToolkitError("PLAN_PARAM_INVALID", "Use a linear duplex reference and an explicitly duplex cargo source.")
    if not (0 <= start <= end <= len(reference["sequence"]) and start - arm_length >= 0
            and end + arm_length <= len(reference["sequence"])
            and 0 <= cargo_start <= cargo_end <= len(cargo["sequence"])):
        raise ToolkitError("PLAN_PARAM_INVALID", "Edit, cargo or homology-arm bounds exceed the supplied sources.")
    selected = slice_material(cargo, cargo_start, cargo_end) if cargo_start != cargo_end else None
    if preparation_method == "gibson" and (overlap is None or donor_template is not None or donor_start is not None or donor_end is not None):
        raise ToolkitError("PLAN_PARAM_INVALID", "Gibson requires explicit overlap and no donor-template PCR fields.")
    if preparation_method == "pcr" and (overlap is not None or donor_template is None or donor_start is None or donor_end is None):
        raise ToolkitError("PLAN_PARAM_INVALID", "PCR requires the actual donor template and its interval; overlap is a Gibson parameter.")
    primers, oligos, pairs, intermediates, reactions = [], [], [], [], []

    def amplify(name: str, template: dict, begin: int, finish: int,
                forward_tail: str = "", reverse_tail: str = "") -> dict:
        if not 0 <= begin < finish <= len(template["sequence"]) or finish - begin < primer_length:
            raise ToolkitError("PLAN_PARAM_INVALID", "Primer binding cores exceed the selected preparation interval.")
        forward = forward_tail + template["sequence"][begin:begin + primer_length]
        reverse = reverse_tail + reverse_complement(template["sequence"][finish - primer_length:finish])
        made = []
        for suffix, sequence in (("forward", forward), ("reverse", reverse)):
            if len(find_binding_sites(template["sequence"], sequence, core_length=primer_length,
                                      circular=template["topology"] == "circular")) != 1:
                raise ToolkitError("PLAN_PARAM_INVALID", "Preparation primer has repeated binding sites; no unique product is selected.")
            primer = make_material(sequence, topology="linear", strandedness="single")
            primers.append({"id": name + "_" + suffix, "sequence": sequence, "core_length": primer_length, "purpose": "preparation"})
            oligos.append(primer)
            made.append(primer)
        pairs.append({"id": name, "forward": name + "_forward", "reverse": name + "_reverse"})
        parameters = {"forward_core_length": primer_length, "reverse_core_length": primer_length}
        result = ctx.call("pcr.simulate", inputs={"template": template, "forward": made[0], "reverse": made[1]}, params=parameters)
        product = result.products["product"]
        reactions.append({"id": name, "method": "pcr", "inputs": [material_id(template), *(material_id(p) for p in made)],
                          "params": parameters, "product_id": material_id(product)})
        intermediates.append(product)
        return product

    def join(name: str, left: dict, right: dict) -> dict:
        result = ctx.call("assembly.gibson", inputs={"left": left, "right": right}, params={"overlap": overlap})
        product = result.products["product"]
        reactions.append({"id": name, "method": "gibson", "inputs": [material_id(left), material_id(right)],
                          "params": {"overlap": overlap}, "product_id": material_id(product)})
        intermediates.append(product)
        return product

    if preparation_method == "pcr":
        product = amplify("donor", donor_template, donor_start, donor_end)
    else:
        if overlap > arm_length:
            raise ToolkitError("PLAN_PARAM_INVALID", "Overlap exceeds a selected fragment.")
        if selected is not None:
            # Put homology overlaps in cargo primer tails. Trimming those tails
            # during assembly preserves the complete source cargo CDS annotation.
            left = amplify("left_arm", reference, start - arm_length, start)
            middle = amplify("cargo", cargo, cargo_start, cargo_end,
                             forward_tail=reference["sequence"][start - overlap:start],
                             reverse_tail=reverse_complement(reference["sequence"][end:end + overlap]))
            right = amplify("right_arm", reference, end, end + arm_length)
            product = join("join_right", join("join_cargo", left, middle), right)
        else:
            left = amplify("left_arm", reference, start - arm_length, start,
                           reverse_tail=reverse_complement(reference["sequence"][end:end + overlap]))
            right = amplify("right_arm", reference, end, end + arm_length)
            product = join("join_arms", left, right)
    edited, _ = replace_material_region(reference, start, end, selected)
    parameters = {"start": start, "end": end, "arm_length": arm_length, "cargo_start": cargo_start, "cargo_end": cargo_end}
    return Outcome(products={"product": product, "edited": edited, "oligos": oligos, "intermediates": intermediates},
        documents={"primers": {"schema": "primer-set-v1", "primers": primers, "pairs": pairs},
                   "route": {"schema": "route-plan-v1", "method": preparation_method, "laboratory_status": "NOT_PERFORMED",
                             "parameters": parameters, "reference_id": material_id(reference), "cargo_id": material_id(cargo), "reactions": reactions}},
        unverified=["PLANNED donor PCR/assembly; NOT_PERFORMED in the laboratory.",
                    "Exact primer binding geometry is simulated; thermodynamic acceptance remains a separate obligation."])
