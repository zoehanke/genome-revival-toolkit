# ported-from: genome-revival-toolkit/revival/construct.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Independent expected donor. No preparation, PCR, editing or assembly imports."""
from dna_design_core.kernel.public import Outcome, ToolkitError, capability, normalize_material
from .contracts import BOUNDS, declaration, port


@capability(declaration("construct.model_donor", "construct.capabilities.model", "model_donor",
    "Compute the independent linear donor expectation from explicit source intervals.",
    [port("reference"), port("cargo")], [port("product", output=True)], BOUNDS))
def model_donor(ctx: object, reference: dict, cargo: dict, start: int, end: int,
                arm_length: int, cargo_start: int, cargo_end: int) -> Outcome:
    reference, cargo = normalize_material(reference), normalize_material(cargo)
    if reference["topology"] != "linear" or reference["strandedness"] != "double":
        raise ToolkitError("PLAN_PARAM_INVALID", "Expected donor needs an explicitly linear duplex reference.")
    sequence, insert = reference["sequence"], cargo["sequence"]
    if not (0 <= start <= end <= len(sequence) and start >= arm_length and end + arm_length <= len(sequence)
            and 0 <= cargo_start <= cargo_end <= len(insert)):
        raise ToolkitError("PLAN_PARAM_INVALID", "Selected interval or homology arms extend outside the supplied sequence.")
    # Deliberately independent of the preparation path's slice_material/PCR/assembly.
    bases = [sequence[position] for position in range(start - arm_length, start)]
    bases.extend(insert[position] for position in range(cargo_start, cargo_end))
    bases.extend(sequence[position] for position in range(end, end + arm_length))
    product = normalize_material({"sequence": "".join(bases), "topology": "linear", "strandedness": "double",
        "ends": {"left": {"kind": "blunt", "overhang": ""}, "right": {"kind": "blunt", "overhang": ""}}, "features": []})
    return Outcome(products={"product": product})
