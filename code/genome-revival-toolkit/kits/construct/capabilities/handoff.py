# ported-from: genome-revival-toolkit/revival/construct.py@750bf4849b818be00f28684513ef19c01d901bcb
"""D11 file protocol. References bind actual GenBank bytes, not sequence text."""
from pathlib import Path

from dna_design_core.kernel.public import Outcome, ToolkitError, capability, dumps, file_sha256, material_id
from dna_design_core.biology.public import material_from_genbank
from .contracts import ASSAY, HANDOFF, declaration, port


@capability(declaration("construct.export_handoff", "construct.capabilities.handoff", "export_handoff",
    "Write identity-handoff.json with actual reference-file hashes and explicit primer sequences.",
    [port("original_file", "artifact"), port("edited_file", "artifact"), port("assay", "document", schema=ASSAY)],
    [port("handoff", "artifact", output=True, output_role="analysis"),
     port("reference_original", "artifact", output=True, output_role="analysis"),
     port("reference_edited", "artifact", output=True, output_role="analysis"),
     port("handoff_data", "document", schema=HANDOFF, output=True, output_role="analysis")],
    {}, effects=("reads_files", "writes_files")))
def export_handoff(ctx: object, original_file: Path, edited_file: Path, assay: dict) -> Outcome:
    files = {"original": Path(original_file), "edited": Path(edited_file)}
    contents = {}
    try:
        for name, path in files.items():
            contents[name] = path.read_bytes()
            loaded = material_from_genbank(contents[name].decode("utf-8"))
            if material_id(loaded) != assay[name + "_id"]:
                raise ToolkitError("PLAN_PARAM_INVALID", "Handoff reference file differs from the actual assay background.")
    except (OSError, ValueError) as error:
        raise ToolkitError("PLAN_PARAM_INVALID", "Handoff requires the actual exported GenBank references.") from error
    value = {"schema": "identity-handoff-v1", "references": [
        {"id": name, "sha256": file_sha256(contents[name]), "role": name} for name in files],
        "regions": assay["regions"], "primers": [{"id": row["id"], "sequence": row["sequence"]} for row in assay["primers"]["primers"]]}
    destination = ctx.workdir / "identity-handoff.json"
    destination.write_bytes(dumps(value))
    artifacts = {"handoff": destination}
    for name, data in contents.items():
        # Deliver the exact bytes referenced by D11, without a format conversion.
        path = ctx.workdir / ("reference-" + name + ".gb")
        path.write_bytes(data)
        artifacts["reference_" + name] = path
    return Outcome(artifacts=artifacts, documents={"handoff_data": value})
