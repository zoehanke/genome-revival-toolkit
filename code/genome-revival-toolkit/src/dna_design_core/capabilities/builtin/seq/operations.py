"""Sequence/material adapters. seq.reverse_complement remains owned by S1."""
from dna_design_core.kernel.public import Outcome, capability
from dna_design_core.biology.public import make_material, rotate_material, slice_material
from .._biology import declaration, input_errors, output, port

MODULE = __name__

# Keep metadata discoverable by the existing declaration exporter; no new registry.
from .preparation import inspect_cds_material, replace_region


@capability(declaration("seq.make_material", "Construct a kernel material with explicit physical properties or unknowns.", MODULE, "create_material",
    [{**port("sequence", "value"), "constraints": {"type": "string", "pattern": "^[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+$"}}], [output("material")],
    {"topology": {"enum": [None, "linear", "circular"]}, "strandedness": {"enum": [None, "single", "double"]},
     "ends": {"type": ["object", "null"]}, "features": {"type": "array", "items": {"type": "object"}}}))
@input_errors
def create_material(ctx: object, sequence: str, topology: str | None = None, strandedness: str | None = None,
                    ends: dict | None = None, features: list | None = None) -> Outcome:
    return Outcome(products={"material": make_material(sequence, topology=topology, strandedness=strandedness, ends=ends, features=features)})


@capability(declaration("seq.slice", "Extract a zero-based half-open interval and transform exact annotations.", MODULE, "extract_material",
    [port("material")], [output("material")],
    {"start": {"type": "integer", "minimum": 0}, "end": {"type": "integer", "minimum": 0},
     "whole": {"type": "boolean"}, "strand": {"enum": [-1, 1]}}, ("start", "end")))
@input_errors
def extract_material(ctx: object, material: dict, start: int, end: int, whole: bool = False, strand: int = 1) -> Outcome:
    return Outcome(products={"material": slice_material(material, start, end, whole=whole, strand=strand)},
                   unverified=["Extraction is a sequence operation; physical preparation and newly cut ends are not established."])


@capability(declaration("seq.rotate", "Rotate a declared circle; D9 identity changes with the selected origin.", MODULE, "rotate_circle",
    [port("material")], [output("material")], {"origin": {"type": "integer", "minimum": 0}}, ("origin",)))
@input_errors
def rotate_circle(ctx: object, material: dict, origin: int) -> Outcome:
    return Outcome(products={"material": rotate_material(material, origin)})
