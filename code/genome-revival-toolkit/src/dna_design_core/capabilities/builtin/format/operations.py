"""Local format IO; biological codecs and kernel material creation stay pure."""
from pathlib import Path

from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import (
    make_material, material_from_genbank, material_from_record, material_to_fasta,
    material_to_genbank, read_dna, read_fasta,
)
from .._biology import declaration, input_errors, output, port

MODULE = __name__
OVERRIDES = {"topology": {"enum": [None, "linear", "circular"]}, "strandedness": {"enum": [None, "single", "double"]}}
NAME = {"name": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]*$"}}


def _declared(value, topology, strandedness):
    for key, wanted in (("topology", topology), ("strandedness", strandedness)):
        if wanted is not None:
            if value[key] is not None and value[key] != wanted:
                raise ValueError("declared physical property contradicts file content")
            value[key] = wanted
    return make_material(**value)


@capability(declaration("format.read_genbank", "Read GenBank content into a kernel material.", MODULE, "read_genbank_file",
    [port("file", "artifact")], [output("material")], OVERRIDES, effects=("reads_files",)))
@input_errors
def read_genbank_file(ctx: object, file: Path, topology: str | None = None, strandedness: str | None = None) -> Outcome:
    value = material_from_genbank(Path(file).read_text(encoding="utf-8"))
    return Outcome(products={"material": _declared(value, topology, strandedness)})


@capability(declaration("format.read_fasta", "Read FASTA DNA; undeclared physical properties remain unknown.", MODULE, "read_fasta_file",
    [port("file", "artifact")], [output("material")], OVERRIDES, effects=("reads_files",)))
@input_errors
def read_fasta_file(ctx: object, file: Path, topology: str | None = None, strandedness: str | None = None) -> Outcome:
    value = material_from_record(read_fasta(Path(file).read_text(encoding="utf-8")))
    return Outcome(products={"material": _declared(value, topology, strandedness)})


@capability(declaration("format.read_dna", "Read supported native DNA fields through Biopython; no native writer.", MODULE, "read_dna_file",
    [port("file", "artifact")], [output("material")], OVERRIDES, effects=("reads_files",)))
@input_errors
def read_dna_file(ctx: object, file: Path, topology: str | None = None, strandedness: str | None = None) -> Outcome:
    value = material_from_record(read_dna(Path(file).read_bytes()))
    return Outcome(products={"material": _declared(value, topology, strandedness)},
                   unverified=["Only Biopython-supported native fields were read; other native blocks and physical ends remain unverified."])


@capability(declaration("format.write_genbank", "Write GenBank with a visible-content-bound material supplement.", MODULE, "write_genbank_file",
    [port("material")], [output("file", "artifact", None)], NAME, ("name",), effects=("writes_files",),
    final_checks=("check.format_roundtrip",)))
@input_errors
def write_genbank_file(ctx: object, material: dict, name: str) -> Outcome:
    path = ctx.workdir / name
    path.write_text(material_to_genbank(material), encoding="utf-8", newline="\n")
    return Outcome(artifacts={"file": path})


@capability(declaration("format.write_fasta", "Write the FASTA-representable material subset; refuse silent metadata loss.", MODULE, "write_fasta_file",
    [port("material")], [output("file", "artifact", None)], NAME, ("name",), effects=("writes_files",),
    final_checks=("check.format_roundtrip",)))
@input_errors
def write_fasta_file(ctx: object, material: dict, name: str) -> Outcome:
    path = ctx.workdir / name
    path.write_text(material_to_fasta(material), encoding="utf-8", newline="\n")
    return Outcome(artifacts={"file": path})
