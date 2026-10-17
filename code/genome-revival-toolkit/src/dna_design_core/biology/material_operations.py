# ported-from: snapgene-dna-design/core/tools/amplification.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/tools/assembly.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Pure annotated operations on kernel material values."""
from __future__ import annotations

from copy import deepcopy
from dna_design_core.kernel.material import normalize

from .materials import make_material, material_from_record, material_to_duplex, record_from_material
from .sequence.operations import rotate_record, slice_record
from .pcr.prediction import simulate_pcr_record
from .restriction.digestion import digest_sequence
from .assembly.simulation import gibson_assemble, inverse_pcr_circularize, ligate_fragments


def slice_material(material: dict, start: int, end: int, *, whole: bool = False, strand: int = 1) -> dict:
    result = slice_record(record_from_material(material), start, end, whole=whole, strand=strand)
    return material_from_record(result, strandedness=material.get("strandedness"))


def rotate_material(material: dict, origin: int) -> dict:
    result = rotate_record(record_from_material(material), origin)
    if origin == 0:
        return normalize(material)
    return material_from_record(result, strandedness=material.get("strandedness"))


def pcr_material(template: dict, forward: dict, reverse: dict, **parameters: int | None) -> tuple[dict, dict]:
    if template.get("strandedness") != "double" or any(primer.get("strandedness") != "single" for primer in (forward, reverse)):
        raise ValueError("PCR model requires a double-stranded template and explicit single-stranded primers")
    record, report = simulate_pcr_record(record_from_material(template), forward["sequence"], reverse["sequence"], **parameters)
    product = material_from_record(record, strandedness="double", ends={
        "left": {"kind": "blunt", "overhang": ""}, "right": {"kind": "blunt", "overhang": ""}})
    return product, report


def digest_material(material: dict, enzymes: list[str]) -> tuple[list[dict], dict]:
    if material.get("strandedness") != "double" or material.get("topology") not in ("linear", "circular"):
        raise ValueError("digest requires explicit double-stranded DNA and topology")
    ends = material.get("ends") or {"left": None, "right": None}
    if any(end and end["kind"] != "blunt" for end in ends.values()):
        raise ValueError("digestion of cohesive-ended inputs requires an explicit duplex-recognition model")
    report = digest_sequence(material["sequence"], tuple(enzymes), circular=material["topology"] == "circular")
    if not report["cut_count"]:
        return [make_material(**material)], {"cut_count": 0, "sites": list(report["sites"])}
    products = []
    record = record_from_material(material)
    for index, fragment in enumerate(report["fragments"]):
        start, end = fragment["top_interval"]
        if material["topology"] == "circular" and end > len(record):
            end %= len(record)
        selected = slice_record(record, start, end, whole=fragment["top_interval"][1] - start == len(record))
        left, right = fragment["left_end"], fragment["right_end"]
        if material["topology"] == "linear":
            if index == 0:
                left = ends["left"]
            if index == len(report["fragments"]) - 1:
                right = ends["right"]
        products.append(material_from_record(selected, strandedness="double", ends={"left": left, "right": right}))
    return products, {"cut_count": report["cut_count"], "sites": list(report["sites"])}


def ligate_material(left: dict, right: dict | None = None, *, circular: bool = False) -> dict:
    materials = (left,) if right is None else (left, right)
    calculated = ligate_fragments(tuple(material_to_duplex(value) for value in materials), circular=circular)
    features, offset = [], 0
    for material in materials:
        features.extend(feature._shift(offset) for feature in record_from_material(material).features)
        offset += len(material["sequence"])
    record = record_from_material(make_material(
        calculated["sequence"] if circular else calculated["top_sequence"],
        topology="circular" if circular else "linear", strandedness="double"))
    record.features = features
    ends = None if circular else {"left": calculated["left_end"], "right": calculated["right_end"]}
    return material_from_record(record, strandedness="double", ends=ends)


def gibson_material(left: dict, right: dict, overlap: int, *, circular: bool = False, closing_overlap: int | None = None) -> dict:
    for value in (left, right):
        if value.get("topology") != "linear" or value.get("strandedness") != "double":
            raise ValueError("overlap assembly requires explicit linear duplex inputs")
    overlaps = (overlap, closing_overlap) if circular else (overlap,)
    calculation = gibson_assemble((left["sequence"], right["sequence"]), overlaps, circular=circular)
    first, second = record_from_material(left), record_from_material(right)
    if circular:
        a = slice_record(first, 0, len(first) - overlap)
        b = slice_record(second, 0, len(second) - closing_overlap)
    else:
        a, b = deepcopy(first), slice_record(second, overlap, len(second))
    record = record_from_material(make_material(calculation["sequence"], topology=calculation["topology"], strandedness="double"))
    record.features = deepcopy(a.features) + [feature._shift(len(a)) for feature in b.features]
    ends = None if circular else {"left": (left.get("ends") or {}).get("left"), "right": (right.get("ends") or {}).get("right")}
    return material_from_record(record, strandedness="double", ends=ends)


def inverse_pcr_material(template: dict, forward: dict, reverse: dict, *, closing_overlap: int = 0, **parameters: int | None) -> tuple[dict, dict, dict]:
    if template.get("topology") != "circular":
        raise ValueError("inverse PCR requires a circular template")
    intermediate, report = pcr_material(template, forward, reverse, **parameters)
    calculation = inverse_pcr_circularize(template["sequence"], forward["sequence"], reverse["sequence"],
                                         closing_overlap=closing_overlap, **parameters)
    record = record_from_material(intermediate)
    if closing_overlap:
        record = slice_record(record, 0, len(record) - closing_overlap)
    record.annotations["topology"] = "circular"
    product = material_from_record(record, strandedness="double")
    if product["sequence"] != calculation["sequence"]:
        raise ValueError("annotated inverse-PCR product differs from sequence model")
    return product, intermediate, report
