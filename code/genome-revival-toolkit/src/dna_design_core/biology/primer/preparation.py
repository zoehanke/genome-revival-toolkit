# ported-from: snapgene-dna-design/core/recipes/verification.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/tools/amplification.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Exact candidate enumeration and stated-distance read projection, no Kit policy."""
from __future__ import annotations

from Bio.Seq import Seq
from ..pcr.prediction import find_binding_sites
from ..sequence.operations import normalize_dna
from .quality import primer_quality
from .thermodynamics import TmParameters, calculate_tm


def enumerate_primer_candidates(sequence: str, anchor: int, strand: int, lengths: list[int], *,
                                circular: bool, parameters: TmParameters, tail_5prime: str = "") -> dict:
    """Enumerate explicit lengths at a 5-prime reference boundary; do not rank.

    Forward cores occupy [anchor,anchor+length); reverse cores occupy
    [anchor-length,anchor), read as reverse complements. Tm is for the binding
    core; quality metrics are for the entire tailed oligo. All sites are retained.
    """
    sequence = normalize_dna(sequence)
    if type(anchor) is not int or not 0 <= anchor <= len(sequence) or strand not in (-1, 1) or type(strand) is not int:
        raise ValueError("explicit anchor boundary and strand are required")
    if not isinstance(lengths, list) or not lengths or len(set(lengths)) != len(lengths) or any(type(n) is not int or not 2 <= n <= len(sequence) for n in lengths):
        raise ValueError("candidate lengths must be distinct integers between 2 and template length")
    tail = normalize_dna(tail_5prime) if tail_5prime else ""
    candidates, excluded = [], []
    for length in sorted(lengths):
        start = anchor if strand == 1 else anchor - length
        end = start + length
        if not circular and not 0 <= start < end <= len(sequence):
            excluded.append({"length": length, "reason": "outside linear template"})
            continue
        reference = "".join(sequence[index % len(sequence)] for index in range(start, end))
        core = reference if strand == 1 else str(Seq(reference).reverse_complement())
        full = tail + core
        sites = find_binding_sites(sequence, full, core_length=length, circular=circular)
        candidates.append({"core_length": length, "binding_core": core, "tail_5prime": tail, "full_sequence": full,
            "reference_start": start % len(sequence) if circular else start, "reference_end_unwrapped": (start % len(sequence) if circular else start) + length,
            "strand": strand, "tm": calculate_tm(core, parameters), "quality": primer_quality(full),
            "binding_sites": list(sites), "binding_site_count": len(sites)})
    return {"candidates": candidates, "excluded_lengths": excluded, "anchor": anchor, "strand": strand,
            "method": "explicit_length_enumeration_without_ranking"}


def sequencing_read_coverage(sequence: str, primers: list[str], *, circular: bool, read_length: int, trim: int) -> dict:
    """Project usable positions from unique primer 3-prime ends; no observed reads."""
    sequence = normalize_dna(sequence)
    if type(read_length) is not int or type(trim) is not int or not 0 <= trim < read_length:
        raise ValueError("require explicit integer 0 <= trim < read_length")
    if not isinstance(primers, list):
        raise TypeError("primers must be a list of complete sequences")
    covered = {1: set(), -1: set()}
    rows = []
    for primer in primers:
        sites = find_binding_sites(sequence, primer, circular=circular)
        if len(sites) != 1:
            rows.append({"binding_site_count": len(sites), "usable": False})
            continue
        site = sites[0]
        positions = (range(site["end_unwrapped"] + trim, site["end_unwrapped"] + read_length) if site["strand"] == 1
                     else range(site["start"] - read_length, site["start"] - trim))
        mapped = {position % len(sequence) for position in positions} if circular else {position for position in positions if 0 <= position < len(sequence)}
        covered[site["strand"]].update(mapped)
        rows.append({"binding_site_count": 1, "usable": True, "strand": site["strand"], "start": site["start"],
                     "end_unwrapped": site["end_unwrapped"], "covered_positions": sorted(mapped)})

    def gaps(positions):
        intervals = []
        for position in range(len(sequence)):
            if position not in positions:
                if intervals and intervals[-1][1] == position:
                    intervals[-1][1] += 1
                else:
                    intervals.append([position, position + 1])
        return intervals

    return {"primers": rows, "forward_positions": sorted(covered[1]), "reverse_positions": sorted(covered[-1]),
            "combined_gaps": gaps(covered[1] | covered[-1]), "read_length": read_length, "trim": trim,
            "all_primers_unique": bool(rows) and all(row["usable"] for row in rows),
            "assumptions": "Stated read-distance geometry only; no chromatogram or experimental quality evidence."}
