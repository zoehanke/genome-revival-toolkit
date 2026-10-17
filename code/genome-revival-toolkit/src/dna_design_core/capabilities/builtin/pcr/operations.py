"""PCR capability on material ports, retaining binding/tail calculations."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import pcr_material
from .._biology import declaration, input_errors, optional_integer, output, port

MODULE = __name__
INPUTS = [port("template"), port("forward"), port("reverse")]
CORE_PARAMETERS = {"forward_core_length": optional_integer(), "reverse_core_length": optional_integer()}


@capability(declaration("pcr.simulate", "Predict one unique annotated PCR product; reject missing or ambiguous products.", MODULE, "simulate",
    INPUTS, [output("product"), output("report", "document", "analysis")], CORE_PARAMETERS,
    final_checks=("check.pcr_product",)))
@input_errors
def simulate(ctx: object, template: dict, forward: dict, reverse: dict,
             forward_core_length: int | None = None, reverse_core_length: int | None = None) -> Outcome:
    product, report = pcr_material(template, forward, reverse,
        forward_core_length=forward_core_length, reverse_core_length=reverse_core_length)
    return Outcome(products={"product": product}, documents={"report": report},
                   unverified=["Ideal blunt PCR sequence model only; polymerase chemistry and experimental success are not established."])
