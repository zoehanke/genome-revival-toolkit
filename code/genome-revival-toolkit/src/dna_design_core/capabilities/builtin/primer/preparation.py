"""Shared primer enumeration and usable-read projection capabilities."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import TmParameters, enumerate_primer_candidates, sequencing_read_coverage
from .._biology import concentration_properties, declaration, input_errors, output, port

MODULE = __name__


@capability(declaration("primer.enumerate_candidates", "Enumerate explicitly bounded primer lengths; retain every exact binding site.", MODULE, "enumerate_candidates",
    [port("template"), port("tail", required=False)], [output("report", "document", "analysis")],
    {"anchor": {"type": "integer", "minimum": 0}, "strand": {"enum": [-1, 1]},
     "lengths": {"type": "array", "items": {"type": "integer", "minimum": 2}, "minItems": 1, "uniqueItems": True},
     **concentration_properties()}, ("anchor", "strand", "lengths")))
@input_errors
def enumerate_candidates(ctx: object, template: dict, anchor: int, strand: int, lengths: list[int], tail: dict | None = None,
                         sodium_mM: str = "50", magnesium_mM: str = "0", dntp_mM: str = "0", total_oligo_nM: str = "50") -> Outcome:
    if template["topology"] not in ("linear", "circular"):
        raise ValueError("primer enumeration needs explicit topology")
    report = enumerate_primer_candidates(template["sequence"], anchor, strand, lengths,
        circular=template["topology"] == "circular", parameters=TmParameters(sodium_mM, magnesium_mM, dntp_mM, total_oligo_nM),
        tail_5prime="" if tail is None else tail["sequence"])
    return Outcome(documents={"report": report}, unverified=["Candidates are unranked proposals; complete thermodynamic QC and actual PCR success are not established."])


@capability(declaration("primer.sequencing_coverage", "Project stated usable sequencing distances from unique complete primer sites.", MODULE, "project_coverage",
    [port("template"), {**port("primers", "value"), "constraints": {"type": "array", "items": {"type": "string"}, "minItems": 1}}],
    [output("report", "document", "analysis")],
    {"read_length": {"type": "integer", "minimum": 1}, "trim": {"type": "integer", "minimum": 0}}, ("read_length", "trim")))
@input_errors
def project_coverage(ctx: object, template: dict, primers: list[str], read_length: int, trim: int) -> Outcome:
    if template["topology"] not in ("linear", "circular"):
        raise ValueError("read projection needs explicit topology")
    report = sequencing_read_coverage(template["sequence"], primers, circular=template["topology"] == "circular", read_length=read_length, trim=trim)
    return Outcome(documents={"report": report}, unverified=["Read-length assumptions are projections, not chromatograms or measured sequencing quality."])
