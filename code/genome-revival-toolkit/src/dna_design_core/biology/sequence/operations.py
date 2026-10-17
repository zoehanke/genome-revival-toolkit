# ported-from: snapgene-dna-design/core/interval.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/tools/sequence_ops.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/tools/snapgene_io.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Strict sequence intervals and annotation transforms; no material identities.

SeqRecord is a format/annotation carrier here, never a kernel material substitute.
All coordinates are zero-based, half-open. Inputs are never mutated.
"""
from __future__ import annotations

from dna_design_core.kernel.public import CapabilityError

from copy import deepcopy

from Bio.Seq import Seq
from Bio.SeqFeature import CompoundLocation, ExactPosition, SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord


def normalize_dna(sequence: str, *, ambiguous: bool = False) -> str:
    """Validate a nonempty DNA string without deleting whitespace or symbols."""
    if not isinstance(sequence, str):
        raise TypeError("sequence must be a DNA string")
    normalized = sequence.upper()
    alphabet = "ACGTRYSWKMBDHVN" if ambiguous else "ACGT"
    if not normalized or any(base not in alphabet for base in normalized):
        raise ValueError("sequence must contain only the declared DNA alphabet")
    return normalized


def interval_segments(
    start: int, end: int, length: int, *, circular: bool = False, whole: bool = False,
) -> tuple[tuple[int, int], ...]:
    """Resolve an interval to ordered linear segments; equal ends need whole=True."""
    if any(type(value) is not int for value in (start, end, length)):
        raise TypeError("interval coordinates and sequence length must be integers")
    if length <= 0 or not 0 <= start <= length or not 0 <= end <= length:
        raise ValueError("interval outside nonempty sequence")
    if circular and start == length:
        raise ValueError("circular start must be below sequence length")
    if start < end:
        return ((start, end),)
    if not circular:
        raise ValueError("linear interval must have positive width and increasing ends")
    if start == end:
        if not whole:
            raise ValueError("equal circular ends require explicit whole=True")
        return ((start, length), (0, start)) if start else ((0, length),)
    return ((start, length), (0, end)) if end else ((start, length),)


def slice_sequence(
    sequence: str, start: int, end: int, *, circular: bool = False,
    strand: int = 1, whole: bool = False,
) -> str:
    """Extract an exact interval, optionally reverse the extracted strand."""
    sequence = normalize_dna(sequence, ambiguous=True)
    if type(strand) is not int or strand not in (1, -1):
        raise ValueError("strand must be 1 or -1")
    segments = interval_segments(start, end, len(sequence), circular=circular, whole=whole)
    selected = "".join(sequence[left:right] for left, right in segments)
    return selected if strand == 1 else str(Seq(selected).reverse_complement())


def map_feature(
    feature: SeqFeature, segments: tuple[tuple[int, int], ...], *,
    source_length: int, linearized: bool = False,
) -> SeqFeature | None:
    """Clip and map exact local feature parts, preserving biological part order.

    Fuzzy/remote locations are rejected rather than silently made exact. Partial
    CDS translations are removed; partial primer annotations become misc_feature.
    """
    if feature.location is None:
        raise ValueError("feature has no location")
    source_parts = feature.location.parts
    offsets = []
    total = 0
    for left, right in segments:
        if not 0 <= left < right <= source_length:
            raise ValueError("mapping segment outside sequence")
        offsets.append(total)
        total += right - left
    mapped = []
    covered = 0
    removed_5prime = 0
    first_retained = False
    for part in source_parts:
        if type(part.start) is not ExactPosition or type(part.end) is not ExactPosition:
            raise ValueError("coordinate transforms require exact feature positions")
        if part.ref is not None or part.ref_db is not None:
            raise ValueError("coordinate transforms require local feature locations")
        left, right = int(part.start), int(part.end)
        if not 0 <= left < right <= source_length:
            raise ValueError("feature outside sequence")
        overlaps = []
        for (seg_left, seg_right), offset in zip(segments, offsets):
            lo, hi = max(left, seg_left), min(right, seg_right)
            if lo < hi:
                overlaps.append((lo, hi, SimpleLocation(
                    lo - seg_left + offset, hi - seg_left + offset, strand=part.strand,
                )))
        overlaps.sort(key=lambda item: item[0], reverse=part.strand == -1)
        if not first_retained:
            if overlaps:
                lo, hi, _ = overlaps[0]
                removed_5prime += right - hi if part.strand == -1 else lo - left
                first_retained = True
            else:
                removed_5prime += right - left
        covered += sum(hi - lo for lo, hi, _ in overlaps)
        mapped.extend(location for _, _, location in overlaps)
    if not mapped:
        return None
    result = deepcopy(feature)
    result.location = mapped[0] if len(mapped) == 1 else CompoundLocation(
        mapped, operator=getattr(feature.location, "operator", "join"),
    )
    # Crossing the new linear origin interrupts even a fully retained primer.
    split_primer = linearized and "primer" in feature.type.lower() and any(
        (a.strand != -1 and int(a.end) == total and int(b.start) == 0)
        or (a.strand == -1 and int(a.start) == 0 and int(b.end) == total)
        for a, b in zip(mapped, mapped[1:])
    )
    if covered < len(feature.location) or split_primer:
        result.qualifiers["partial"] = ["true"]
        notes = result.qualifiers.setdefault("note", [])
        if not isinstance(notes, list):
            notes = result.qualifiers["note"] = [str(notes)]
        notes.append("Feature interrupted by extraction; complete function is not asserted.")
        if feature.type == "CDS":
            result.qualifiers.pop("translation", None)
            codon = result.qualifiers.get("codon_start", ["1"])
            if not isinstance(codon, list) or len(codon) != 1 or codon[0] not in ("1", "2", "3"):
                raise ValueError("CDS codon_start must be 1, 2 or 3")
            result.qualifiers["codon_start"] = [str((int(codon[0]) - 1 - removed_5prime) % 3 + 1)]
        if "primer" in feature.type.lower():
            result.type = "misc_feature"
            result.qualifiers["source_feature_type"] = [feature.type]
    return result


def slice_record(
    record: SeqRecord, start: int, end: int, *, whole: bool = False, strand: int = 1,
) -> SeqRecord:
    """Extract annotated DNA using the record's explicitly declared topology."""
    topology = record.annotations.get("topology")
    if topology not in ("linear", "circular"):
        raise ValueError("record topology must be explicitly linear or circular")
    segments = interval_segments(start, end, len(record), circular=topology == "circular", whole=whole)
    result = SeqRecord(Seq(slice_sequence(
        str(record.seq), start, end, circular=topology == "circular", whole=whole,
    )), id=record.id, name=record.name, description=record.description,
        annotations=deepcopy(record.annotations), dbxrefs=list(record.dbxrefs))
    result.features = [mapped for feature in record.features if (mapped := map_feature(
        feature, segments, source_length=len(record), linearized=topology == "circular",
    )) is not None]
    for key, values in record.letter_annotations.items():
        result.letter_annotations[key] = [value for lo, hi in segments for value in values[lo:hi]]
    if type(strand) is not int or strand not in (1, -1):
        raise ValueError("strand must be 1 or -1")
    if strand == -1:
        result = result.reverse_complement(
            id=True, name=True, description=True, annotations=True, dbxrefs=True,
        )
    result.annotations["topology"] = "linear"
    return result


def rotate_record(record: SeqRecord, origin: int) -> SeqRecord:
    """Rotate a declared circle; split features retain their biological order."""
    if record.annotations.get("topology") != "circular":
        raise ValueError("origin rotation requires an explicitly circular record")
    segments = interval_segments(origin, origin, len(record), circular=True, whole=True)
    result = deepcopy(record)
    # Clear length-bound annotations before changing seq, then map all of them.
    result.letter_annotations = {}
    result.seq = Seq("".join(str(record.seq)[lo:hi] for lo, hi in segments).upper())
    result.features = [mapped for feature in record.features if (mapped := map_feature(
        feature, segments, source_length=len(record),
    )) is not None]
    for key, values in record.letter_annotations.items():
        result.letter_annotations[key] = [value for lo, hi in segments for value in values[lo:hi]]
    return result


def reverse_complement(sequence: str) -> str:
    alphabet='ACGTRYSWKMBDHVN'
    if not isinstance(sequence,str) or not sequence or not set(sequence.upper())<=set(alphabet):
        raise CapabilityError('PLAN_PARAM_INVALID','Sequence must use the IUPAC DNA alphabet.')
    return sequence.upper().translate(str.maketrans(alphabet,'TGCAYRSWMKVHDBN'))[::-1]
