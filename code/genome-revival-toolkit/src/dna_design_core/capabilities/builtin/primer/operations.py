"""Pure primer measurements with complete parameter reporting."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import TmParameters, calculate_tm, find_binding_sites, primer_quality
from .._biology import concentration_properties, declaration, input_errors, output, port

MODULE = __name__

from .preparation import enumerate_candidates, project_coverage


@capability(declaration("primer.calculate_tm", "Calculate DNA_NN3 nearest-neighbor Tm and emit every concentration parameter.", MODULE, "melting_temperature",
    [port("primer")], [output("report", "document", "analysis")], concentration_properties()))
@input_errors
def melting_temperature(ctx: object, primer: dict, sodium_mM: str = "50", magnesium_mM: str = "0",
                        dntp_mM: str = "0", total_oligo_nM: str = "50") -> Outcome:
    parameters = TmParameters(sodium_mM, magnesium_mM, dntp_mM, total_oligo_nM)
    return Outcome(documents={"report": calculate_tm(primer["sequence"], parameters)})


@capability(declaration("primer.inspect_quality", "Measure full-oligo GC, T runs and exact ungapped dimer/hairpin metrics.", MODULE, "inspect_quality",
    [port("primer"), port("partner", required=False)], [output("report", "document", "analysis")],
    {"min_loop": {"type": "integer", "minimum": 0}}))
@input_errors
def inspect_quality(ctx: object, primer: dict, partner: dict | None = None, min_loop: int = 3) -> Outcome:
    return Outcome(documents={"report": primer_quality(primer["sequence"], partner=None if partner is None else partner["sequence"], min_loop=min_loop)},
                   unverified=["Exact complementarity metrics are not thermodynamic structure predictions."])


@capability(declaration("primer.find_binding_sites", "Find every exact declared 3-prime core on both strands, including a circular origin.", MODULE, "binding_sites",
    [port("template"), port("primer")], [output("report", "document", "analysis")],
    {"core_length": {"type": ["integer", "null"], "minimum": 1}, "strand": {"enum": [None, -1, 1]}}))
@input_errors
def binding_sites(ctx: object, template: dict, primer: dict, core_length: int | None = None, strand: int | None = None) -> Outcome:
    if template["topology"] not in ("linear", "circular"):
        raise ValueError("binding-site search requires explicit topology")
    rows = find_binding_sites(template["sequence"], primer["sequence"], core_length=core_length,
                              circular=template["topology"] == "circular", strand=strand)
    return Outcome(documents={"report": {"sites": list(rows)}})
