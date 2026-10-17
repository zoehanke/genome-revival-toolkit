"""Material-port ligation, ordered overlaps and inverse-PCR sequence closure."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import gibson_material, inverse_pcr_material, ligate_material
from .._biology import declaration, input_errors, optional_integer, output, port

MODULE = __name__


@capability(declaration("assembly.ligate", "Ligate one or two explicit linear duplexes after checking actual strand geometry.", MODULE, "ligate",
    [port("left"), port("right", required=False)], [output("product")], {"circular": {"type": "boolean"}},
    final_checks=("check.assembly_product",)))
@input_errors
def ligate(ctx: object, left: dict, right: dict | None = None, circular: bool = False) -> Outcome:
    return Outcome(products={"product": ligate_material(left, right, circular=circular)},
                   unverified=["Ligation chemistry, phosphorylation and experimental yield are not established."])


@capability(declaration("assembly.gibson", "Assemble two ordered duplexes using explicit exact overlap lengths.", MODULE, "gibson",
    [port("left"), port("right")], [output("product")],
    {"overlap": {"type": "integer", "minimum": 1}, "circular": {"type": "boolean"}, "closing_overlap": optional_integer()}, ("overlap",),
    final_checks=("check.assembly_product",)))
@input_errors
def gibson(ctx: object, left: dict, right: dict, overlap: int, circular: bool = False, closing_overlap: int | None = None) -> Outcome:
    return Outcome(products={"product": gibson_material(left, right, overlap, circular=circular, closing_overlap=closing_overlap)},
                   unverified=["Only sequence overlap consistency is simulated; experimental assembly is not established."])


@capability(declaration("assembly.inverse_pcr", "Simulate circular-template PCR and closure while retaining the linear intermediate.", MODULE, "inverse_pcr",
    [port("template"), port("forward"), port("reverse")],
    [output("product", role="construct"), output("intermediate"), output("report", "document", "analysis")],
    {"forward_core_length": optional_integer(), "reverse_core_length": optional_integer(), "closing_overlap": {"type": "integer", "minimum": 0}},
    final_checks=("check.assembly_product",)))
@input_errors
def inverse_pcr(ctx: object, template: dict, forward: dict, reverse: dict, forward_core_length: int | None = None,
                reverse_core_length: int | None = None, closing_overlap: int = 0) -> Outcome:
    product, intermediate, report = inverse_pcr_material(template, forward, reverse,
        forward_core_length=forward_core_length, reverse_core_length=reverse_core_length, closing_overlap=closing_overlap)
    return Outcome(products={"product": product, "intermediate": intermediate}, documents={"report": report},
                   unverified=["Parental-template removal, phosphorylation and physical circularization remain NOT_PERFORMED."])
