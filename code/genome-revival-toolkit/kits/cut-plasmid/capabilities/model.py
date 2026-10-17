"""Independent per-base expected edit; no producer, cassette or PCR imports."""
from copy import deepcopy

from dna_design_core.kernel.public import Outcome, ToolkitError, capability, normalize_material
from .contracts import CASSETTE_PARAMS, SPACER, declaration, material_port, output


@capability(declaration("model_replace", "model", "model_replace", [material_port("vector")],
                        [output("product", "material")],
                        {"promoter_end": CASSETTE_PARAMS["promoter_end"],
                         "transcription_strand": CASSETTE_PARAMS["transcription_strand"], "spacer": SPACER}))
def model_replace(ctx: object, vector: dict, promoter_end: int, transcription_strand: int, spacer: str) -> Outcome:
    if vector["topology"] != "circular" or vector["strandedness"] != "double" or not 20 <= len(vector["sequence"]) or not 0 <= promoter_end <= len(vector["sequence"]):
        raise ToolkitError("PLAN_PARAM_INVALID", "Independent model requires an explicit circular duplex and in-range boundary.")
    value = deepcopy(vector)
    bases = list(value["sequence"])
    complements = {"A": "T", "C": "G", "G": "C", "T": "A"}
    for index, base in enumerate(spacer):
        location = (promoter_end + index if transcription_strand == 1 else promoter_end - 1 - index) % len(bases)
        bases[location] = base if transcription_strand == 1 else complements[base]
    value["sequence"] = "".join(bases)
    return Outcome(products={"product": normalize_material(value)})
