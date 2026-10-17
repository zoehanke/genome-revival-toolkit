"""Shared interval editing and coding-frame inspection, with no Kit logic."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import inspect_cds, replace_material_region
from .._biology import declaration, input_errors, output, port

MODULE = __name__


@capability(declaration("seq.replace_region", "Replace an explicit nonwrapping interval and retire intersecting annotations.", MODULE, "replace_region",
    [port("material"), port("insert", required=False)], [output("product"), output("report", "document", "analysis")],
    {"start": {"type": "integer", "minimum": 0}, "end": {"type": "integer", "minimum": 0}}, ("start", "end")))
@input_errors
def replace_region(ctx: object, material: dict, start: int, end: int, insert: dict | None = None) -> Outcome:
    product, report = replace_material_region(material, start, end, insert)
    return Outcome(products={"product": product}, documents={"report": report},
                   unverified=["Sequence-edit model only; physical preparation and retired annotation function are not established."])


@capability(declaration("seq.inspect_cds", "Report frame, start/stop and ambiguity under an explicit genetic code.", MODULE, "inspect_cds_material",
    [port("material")], [output("report", "document", "analysis")],
    {"translation_table": {"type": "integer", "minimum": 1}, "codon_start": {"enum": [1, 2, 3]}, "partial": {"type": "boolean"}}, ("translation_table",)))
@input_errors
def inspect_cds_material(ctx: object, material: dict, translation_table: int, codon_start: int = 1, partial: bool = False) -> Outcome:
    return Outcome(documents={"report": inspect_cds(material["sequence"], translation_table, codon_start=codon_start, partial=partial)},
                   unverified=["Frame consistency is not expression, selectable phenotype or inherited-finding correspondence."])
