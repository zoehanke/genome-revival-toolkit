"""Recognition scan and material-valued digestion."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import digest_material, scan_restriction_sites
from .._biology import declaration, input_errors, output, port

MODULE = __name__


@capability(declaration("restriction.scan_sites", "Scan both recognition orientations and report double-strand cut geometry.", MODULE, "scan_sites",
    [port("material")], [output("report", "document", "analysis")], {"enzyme": {"type": "string", "minLength": 1}}, ("enzyme",)))
@input_errors
def scan_sites(ctx: object, material: dict, enzyme: str) -> Outcome:
    if material["topology"] not in ("linear", "circular"):
        raise ValueError("restriction scan requires explicit topology")
    return Outcome(documents={"report": {"sites": list(scan_restriction_sites(material["sequence"], enzyme, circular=material["topology"] == "circular"))}})


@capability(declaration("restriction.digest", "Produce annotated kernel fragments with actual cohesive end sequences.", MODULE, "digest",
    [port("material")], [output("fragments", "materials"), output("report", "document", "analysis")],
    {"enzymes": {"type": "array", "items": {"type": "string", "minLength": 1}, "minItems": 1, "uniqueItems": True}}, ("enzymes",),
    final_checks=("check.assembly_product",)))
@input_errors
def digest(ctx: object, material: dict, enzymes: list[str]) -> Outcome:
    products, report = digest_material(material, enzymes)
    return Outcome(products={"fragments": products}, documents={"report": report},
                   unverified=["Methylation effects and experimental cleavage are not established."])
