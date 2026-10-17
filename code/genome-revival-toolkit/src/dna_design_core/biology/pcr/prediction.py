# ported-from: snapgene-dna-design/core/tools/amplification.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Exact binding-core and PCR sequence predictions with explicit 5-prime tails."""
from __future__ import annotations

from copy import deepcopy

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from ..sequence.operations import normalize_dna, slice_record


def find_binding_sites(
    template: str, primer: str, *, core_length: int | None = None,
    circular: bool = False, strand: int | None = None,
) -> tuple[dict, ...]:
    """Find all complete exact core matches. +1 means top-reference sequence.

    The primer is always given 5-prime to 3-prime. Its core is the declared
    3-prime suffix; omitted core_length means the entire primer. No heuristic
    tail inference and no masking of repeated binding sites.
    """
    template, primer = normalize_dna(template), normalize_dna(primer)
    if strand is not None and (type(strand) is not int or strand not in (1, -1)):
        raise ValueError("strand must be 1, -1 or None")
    core_length = len(primer) if core_length is None else core_length
    if type(core_length) is not int or not 1 <= core_length <= len(primer):
        raise ValueError("core length must be an integer within the primer")
    if core_length > len(template):
        return ()
    core = primer[-core_length:]
    search = template + template[:core_length - 1] if circular else template
    positions = range(len(template)) if circular else range(len(template) - core_length + 1)
    hits = []
    for orientation in ((1, -1) if strand is None else (strand,)):
        target = core if orientation == 1 else str(Seq(core).reverse_complement())
        for start in positions:
            if search[start:start + core_length] == target:
                raw_end = start + core_length
                hits.append({
                    "start": start, "end": raw_end if raw_end <= len(template) else raw_end % len(template),
                    "end_unwrapped": raw_end, "strand": orientation,
                    "wraps_origin": raw_end > len(template), "core_length": core_length,
                    "core": core, "tail_5prime": primer[:-core_length],
                })
    return tuple(hits)


def predict_pcr_products(
    template: str, forward: str, reverse: str, *, circular: bool = False,
    forward_core_length: int | None = None, reverse_core_length: int | None = None,
) -> tuple[dict, ...]:
    """Enumerate every inward-facing pair spanning at most one template turn."""
    template = normalize_dna(template)
    forward_hits = find_binding_sites(template, forward, core_length=forward_core_length, circular=circular, strand=1)
    reverse_hits = find_binding_sites(template, reverse, core_length=reverse_core_length, circular=circular, strand=-1)
    products = []
    length = len(template)
    for first in forward_hits:
        for last in reverse_hits:
            start, end = first["start"], last["end_unwrapped"]
            span = (end - start) % length or length if circular else end - start
            if span < max(first["core_length"], last["core_length"]):
                continue
            if not circular and last["start"] < start:
                continue
            core = (template + template)[start:start + span] if circular else template[start:end]
            tail = str(Seq(last["tail_5prime"]).reverse_complement())
            products.append({
                "sequence": first["tail_5prime"] + core + tail,
                "topology": "linear", "forward_binding": deepcopy(first),
                "reverse_binding": deepcopy(last), "template_start": start,
                "template_end_unwrapped": start + span, "template_span": span,
                "wraps_origin": start + span > length,
            })
    return tuple(products)


def simulate_pcr(
    template: str, forward: str, reverse: str, *, circular: bool = False,
    forward_core_length: int | None = None, reverse_core_length: int | None = None,
) -> dict:
    """Require exactly one predicted amplicon; ambiguity never selects shortest."""
    products = predict_pcr_products(
        template, forward, reverse, circular=circular,
        forward_core_length=forward_core_length, reverse_core_length=reverse_core_length,
    )
    if len(products) != 1:
        raise ValueError(f"PCR needs exactly one predicted product; found {len(products)}")
    return products[0]


def simulate_pcr_record(
    template: SeqRecord, forward: str, reverse: str, *,
    forward_core_length: int | None = None, reverse_core_length: int | None = None,
) -> tuple[SeqRecord, dict]:
    """Predict a unique annotated PCR product; added tail bases carry no measurements."""
    topology = template.annotations.get("topology")
    if topology not in ("linear", "circular"):
        raise ValueError("PCR requires explicitly declared template topology")
    prediction = simulate_pcr(
        str(template.seq), forward, reverse, circular=topology == "circular",
        forward_core_length=forward_core_length, reverse_core_length=reverse_core_length,
    )
    start, span = prediction["template_start"], prediction["template_span"]
    end = start + span
    if topology == "circular" and end > len(template):
        end %= len(template)
    core = slice_record(template, start, end, whole=span == len(template))
    left = len(prediction["forward_binding"]["tail_5prime"])
    right = len(prediction["reverse_binding"]["tail_5prime"])
    result = deepcopy(core)
    result.letter_annotations = {}
    result.seq = Seq(prediction["sequence"])
    result.features = [feature._shift(left) for feature in core.features]
    for key, values in core.letter_annotations.items():
        result.letter_annotations[key] = [None] * left + list(values) + [None] * right
    if core.letter_annotations:
        result.annotations["comment"] = str(result.annotations.get("comment", "")) + (
            " Source per-letter values are mapped metadata, not measurements on this product; tail values unknown."
        )
    return result, prediction
