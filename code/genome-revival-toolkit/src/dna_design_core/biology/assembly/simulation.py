# ported-from: snapgene-dna-design/core/models/assembly_model.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/tools/assembly.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/recipes/mutagenesis.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Sequence-only ligation, ordered overlap assembly and inverse-PCR closure.

No material factory or laboratory outcome. Duplexes are calculation results of
digest_sequence with actual strand sequences, never unverified overhang labels.
"""
from __future__ import annotations

from copy import deepcopy

from Bio.Seq import Seq

from ..pcr.prediction import simulate_pcr
from ..sequence.operations import normalize_dna


def compatible_ends(first: dict | None, second: dict | None) -> bool:
    """Compare actual 5-prime-to-3-prime extensions; unknown is not compatible."""
    if first is None or second is None:
        return False
    for end in (first, second):
        if set(end) != {"kind", "overhang"} or end["kind"] not in ("blunt", "5prime", "3prime"):
            raise ValueError("invalid end geometry")
        if end["kind"] == "blunt":
            if end["overhang"] != "":
                raise ValueError("blunt ends cannot contain an extension")
        else:
            normalize_dna(end["overhang"])
    if first["kind"] != second["kind"]:
        return False
    return first["overhang"] == str(Seq(second["overhang"]).reverse_complement())


def validate_duplex(fragment: dict) -> None:
    """Check strand pairing and every supplied end against actual strand bases."""
    top = normalize_dna(fragment["top_sequence"])
    bottom = normalize_dna(fragment["bottom_sequence"])
    if fragment["topology"] != "linear":
        raise ValueError("ligation requires linear input fragments")
    offset = fragment["bottom_offset"]
    if type(offset) is not int:
        raise TypeError("bottom offset must be an integer")
    bottom_reference = str(Seq(bottom).reverse_complement())
    lo, hi = max(0, offset), min(len(top), offset + len(bottom))
    if lo >= hi or top[lo:hi] != bottom_reference[lo - offset:hi - offset]:
        raise ValueError("duplex strands do not have a complementary shared core")
    for side, delta in (("left", offset), ("right", offset + len(bottom) - len(top))):
        end = fragment[side + "_end"]
        if end is None:
            # Natural end chemistry is unknown, but reference boundaries agree.
            if delta:
                raise ValueError("unknown end cannot specify staggered strand boundaries")
            continue
        compatible_ends(end, end)  # validate fields, not compatibility with itself
        kind, extension = end["kind"], end["overhang"]
        expected_delta = 0 if kind == "blunt" else len(extension) * (1 if kind == "5prime" else -1)
        if delta != expected_delta:
            raise ValueError("end geometry disagrees with strand boundaries")
        if kind == "blunt":
            actual = ""
        elif side == "left":
            actual = top[:len(extension)] if kind == "5prime" else bottom[-len(extension):]
        else:
            actual = bottom[:len(extension)] if kind == "5prime" else top[-len(extension):]
        if actual != extension:
            raise ValueError("end extension disagrees with actual strand sequence")


def ligate_fragments(fragments: tuple[dict, ...], *, circular: bool = False) -> dict:
    """Join ordered duplexes after validating all actual strand junctions."""
    if not isinstance(fragments, tuple) or not fragments:
        raise ValueError("a nonempty tuple of ordered fragments is required")
    for fragment in fragments:
        validate_duplex(fragment)
    count = len(fragments) if circular else len(fragments) - 1
    for index in range(count):
        if not compatible_ends(fragments[index]["right_end"], fragments[(index + 1) % len(fragments)]["left_end"]):
            raise ValueError("incompatible or unknown ligation ends")
    top = "".join(fragment["top_sequence"] for fragment in fragments)
    bottom = "".join(fragment["bottom_sequence"] for fragment in reversed(fragments))
    if circular:
        if len(top) != len(bottom):
            raise ValueError("closed duplex strands must have equal length")
        offset = fragments[0]["bottom_offset"] % len(bottom)
        reference = str(Seq(bottom).reverse_complement())
        reference = reference[-offset:] + reference[:-offset] if offset else reference
        if top != reference:
            raise ValueError("closed product strands disagree")
        return {"sequence": top, "topology": "circular"}
    result = {
        "top_sequence": top, "bottom_sequence": bottom,
        "bottom_offset": fragments[0]["bottom_offset"], "topology": "linear",
        "left_end": deepcopy(fragments[0]["left_end"]), "right_end": deepcopy(fragments[-1]["right_end"]),
    }
    validate_duplex(result)
    return result


def gibson_assemble(
    fragments: tuple[str, ...], overlap_lengths: tuple[int, ...], *, circular: bool = False,
) -> dict:
    """Assemble exact, caller-specified overlaps in a fixed order/orientation.

    Each fragment must contribute unique bases outside its incoming/outgoing
    overlap arms. No experimental overlap-length floor is asserted here.
    """
    if not isinstance(fragments, tuple) or len(fragments) < 2:
        raise ValueError("ordered overlap assembly requires at least two fragments")
    sequences = tuple(normalize_dna(sequence) for sequence in fragments)
    count = len(sequences) if circular else len(sequences) - 1
    if not isinstance(overlap_lengths, tuple) or len(overlap_lengths) != count:
        raise ValueError("one explicit overlap length is required for every junction")
    for index, overlap in enumerate(overlap_lengths):
        if type(overlap) is not int or overlap <= 0:
            raise ValueError("overlap lengths must be positive integers")
        first, second = sequences[index], sequences[(index + 1) % len(sequences)]
        if overlap >= min(len(first), len(second)) or first[-overlap:] != second[:overlap]:
            raise ValueError("declared overlap is too long or not an exact match")
    for index, sequence in enumerate(sequences):
        incoming = overlap_lengths[index - 1] if circular or index else 0
        outgoing = overlap_lengths[index] if index < count else 0
        if incoming + outgoing >= len(sequence):
            raise ValueError("each fragment must retain a unique contribution outside overlap arms")
    if circular:
        sequence = "".join(part[:-overlap] for part, overlap in zip(sequences, overlap_lengths))
    else:
        sequence = sequences[0] + "".join(part[overlap:] for part, overlap in zip(sequences[1:], overlap_lengths))
    return {"sequence": sequence, "topology": "circular" if circular else "linear", "overlap_lengths": list(overlap_lengths)}


def inverse_pcr_circularize(
    template: str, forward: str, reverse: str, *, forward_core_length: int | None = None,
    reverse_core_length: int | None = None, closing_overlap: int = 0,
) -> dict:
    """Simulate circular-template PCR then sequence closure, retaining intermediate.

    closing_overlap=0 means blunt sequence closure. Positive values identify an
    exact duplicated terminal overlap removed once. Phosphorylation, parental
    removal, reaction choice and wet-lab success are not established.
    """
    intermediate = simulate_pcr(
        template, forward, reverse, circular=True,
        forward_core_length=forward_core_length, reverse_core_length=reverse_core_length,
    )
    sequence = intermediate["sequence"]
    if type(closing_overlap) is not int or closing_overlap < 0 or 2 * closing_overlap >= len(sequence):
        raise ValueError("closing overlap must be nonnegative and leave unique sequence")
    if closing_overlap:
        if sequence[:closing_overlap] != sequence[-closing_overlap:]:
            raise ValueError("terminal closing overlap does not match")
        sequence = sequence[:-closing_overlap]
    return {"sequence": sequence, "topology": "circular", "intermediate": intermediate,
            "closing_overlap": closing_overlap}
