# ported-from: snapgene-dna-design/core/tools/restriction.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Recognition and double-strand cut geometry on explicit synthetic duplexes.

Returned dictionaries are sequence-calculation data, not kernel materials.
Natural ends remain unknown. Methylation, cleavage efficiency and chemistry are
not inferred. Enzyme definitions come from the pinned Biopython database.
"""
from __future__ import annotations

from Bio import Restriction
from Bio.Data.IUPACData import ambiguous_dna_values
from Bio.Seq import Seq

from ..sequence.operations import normalize_dna


def enzyme_definition(name: str) -> dict:
    """Resolve an exact database name with one double-strand cleavage pair."""
    if not isinstance(name, str):
        raise TypeError("enzyme name must be a string")
    enzyme = getattr(Restriction, name, None)
    if enzyme not in Restriction.AllEnzymes:
        raise ValueError("unknown exact restriction enzyme name")
    if enzyme.fst5 is None or enzyme.fst3 is None or enzyme.scd5 is not None or enzyme.scd3 is not None:
        raise ValueError("enzyme must have exactly one known double-strand cleavage pair")
    return {
        "name": name, "recognition": str(enzyme.site),
        "top_offset": int(enzyme.fst5), "bottom_offset_from_end": int(enzyme.fst3),
        "source_class": "database_record", "source": f"Bio.Restriction:{name}",
    }


def scan_restriction_sites(sequence: str, enzyme: str, *, circular: bool = False) -> tuple[dict, ...]:
    """Report both motif orientations, including uncuttable out-of-bounds sites."""
    sequence = normalize_dna(sequence)
    definition = enzyme_definition(enzyme)
    site = definition["recognition"]
    reverse = str(Seq(site).reverse_complement())
    length, width = len(sequence), len(site)
    if width > length:
        return ()
    searchable = sequence + sequence[:width - 1] if circular else sequence
    positions = range(length) if circular else range(length - width + 1)
    orientations = ((site, 1),) if reverse == site else ((site, 1), (reverse, -1))
    hits = []
    for start in positions:
        window = searchable[start:start + width]
        for motif, strand in orientations:
            if not all(base in ambiguous_dna_values[symbol] for base, symbol in zip(window, motif)):
                continue
            if strand == 1:
                top = start + definition["top_offset"]
                bottom = start + width + definition["bottom_offset_from_end"]
            else:
                top = start - definition["bottom_offset_from_end"]
                bottom = start + width - definition["top_offset"]
            within = circular or (0 <= top <= length and 0 <= bottom <= length)
            lo, hi = sorted((top, bottom))
            if circular and hi - lo >= length:
                raise ValueError("cut staggering must be shorter than one complete circle")
            extension = None if not within else (
                "".join(sequence[index % length] for index in range(lo, hi)) if circular else sequence[lo:hi]
            )
            hits.append({
                "enzyme": enzyme, "start": start, "end_unwrapped": start + width,
                "strand": strand, "wraps_origin": start + width > length,
                "top_cut": top % length if circular else top,
                "bottom_cut": bottom % length if circular else bottom,
                "top_cut_unwrapped": top, "bottom_cut_unwrapped": bottom,
                "cuts_within_sequence": within,
                "overhang_kind": "blunt" if top == bottom else "5prime" if top < bottom else "3prime",
                "reference_overhang": extension,
            })
    return tuple(hits)


def digest_sequence(sequence: str, enzymes: tuple[str, ...], *, circular: bool = False) -> dict:
    """Calculate top/bottom strands and actual extensions of digest fragments.

    Cuts must have the same order on both strands. Closely interleaving cuts
    and terminal cuts leaving a single-stranded product are explicitly refused.
    Such fragments require a richer material model than this sequence simulator.
    """
    sequence = normalize_dna(sequence)
    if not isinstance(enzymes, tuple) or not enzymes or len(set(enzymes)) != len(enzymes):
        raise ValueError("enzymes must be a nonempty tuple of distinct exact names")
    sites = [hit for name in enzymes for hit in scan_restriction_sites(sequence, name, circular=circular)]
    cuts = {}
    for hit in sites:
        if hit["cuts_within_sequence"]:
            key = hit["top_cut"]
            stagger = hit["bottom_cut_unwrapped"] - hit["top_cut_unwrapped"]
            if key in cuts and cuts[key]["bottom_cut_unwrapped"] - cuts[key]["top_cut_unwrapped"] != stagger:
                raise ValueError("different bottom-strand cuts at one top-strand boundary")
            cuts[key] = hit
    ordered = sorted(cuts.values(), key=lambda hit: hit["top_cut"])
    length = len(sequence)

    def endpoint(hit: dict | None, side: str) -> dict | None:
        if hit is None:
            return None
        extension = hit["reference_overhang"]
        kind = hit["overhang_kind"]
        if (kind == "5prime" and side == "right") or (kind == "3prime" and side == "left"):
            extension = str(Seq(extension).reverse_complement())
        return {"kind": kind, "overhang": extension}

    if not ordered:
        return {"sites": sites, "cut_count": 0, "fragments": ({
            "top_sequence": sequence, "bottom_sequence": str(Seq(sequence).reverse_complement()),
            "bottom_offset": 0, "top_interval": [0, length], "bottom_interval": [0, length],
            "left_end": None, "right_end": None, "topology": "circular" if circular else "linear",
        },)}
    # Unwrap bottom boundaries relative to the same top-strand origin.
    boundaries = [(hit["top_cut"], hit["top_cut"] + hit["bottom_cut_unwrapped"] - hit["top_cut_unwrapped"], hit)
                  for hit in ordered]
    intervals = []
    if circular:
        for index, (top, bottom, left_hit) in enumerate(boundaries):
            end_top, end_bottom, right_hit = boundaries[(index + 1) % len(boundaries)]
            if index == len(boundaries) - 1:
                end_top += length
                end_bottom += length
            intervals.append((top, end_top, bottom, end_bottom, left_hit, right_hit))
    else:
        linear_boundaries = [(0, 0, None), *boundaries, (length, length, None)]
        for (top, bottom, left_hit), (end_top, end_bottom, right_hit) in zip(linear_boundaries, linear_boundaries[1:]):
            if top == end_top and bottom == end_bottom:
                continue
            intervals.append((top, end_top, bottom, end_bottom, left_hit, right_hit))
    fragments = []
    for top, end_top, bottom, end_bottom, left_hit, right_hit in intervals:
        if top >= end_top or bottom >= end_bottom or max(top, bottom) >= min(end_top, end_bottom):
            raise ValueError("interleaved or terminal cuts leave no supported duplex core")
        if circular:
            top_sequence = "".join(sequence[index % length] for index in range(top, end_top))
            bottom_reference = "".join(sequence[index % length] for index in range(bottom, end_bottom))
        else:
            top_sequence, bottom_reference = sequence[top:end_top], sequence[bottom:end_bottom]
        fragments.append({
            "top_sequence": top_sequence, "bottom_sequence": str(Seq(bottom_reference).reverse_complement()),
            "bottom_offset": bottom - top, "top_interval": [top, end_top],
            "bottom_interval": [bottom, end_bottom], "left_end": endpoint(left_hit, "left"),
            "right_end": endpoint(right_hit, "right"), "topology": "linear",
        })
    return {"sites": sites, "cut_count": len(ordered), "fragments": tuple(fragments)}
