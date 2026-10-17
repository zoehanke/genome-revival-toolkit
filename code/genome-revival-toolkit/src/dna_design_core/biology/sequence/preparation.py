# ported-from: snapgene-dna-design/core/tools/sequence_ops.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/models/construct_model.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Non-CRISPR preparation calculations shared by at least two planned Kits."""
from __future__ import annotations

from copy import deepcopy

from Bio.Data import CodonTable
from Bio.Seq import Seq
from dna_design_core.kernel.material import normalize
from ..materials import make_material, material_from_record, record_from_material
from .operations import normalize_dna


def replace_material_region(material: dict, start: int, end: int, insert: dict | None = None) -> tuple[dict, dict]:
    """Replace an explicit nonwrapping half-open interval; retain only untouched features.

    Features overlapping the changed interval are retired, never silently kept as
    intact CDSs. An insertion inside a feature also retires that feature. Circular
    origin changes are explicit caller operations using rotate_material.
    """
    value = normalize(material)
    if value["topology"] not in ("linear", "circular"):
        raise ValueError("region editing requires explicitly declared topology")
    if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(value["sequence"]):
        raise ValueError("region must be a nonwrapping zero-based half-open interval")
    replacement = None if insert is None else normalize(insert)
    if replacement is not None and replacement["topology"] == "circular":
        raise ValueError("select a linear insert region before using a circular source")
    inserted = "" if replacement is None else normalize_dna(replacement["sequence"], ambiguous=True)
    sequence = value["sequence"][:start] + inserted + value["sequence"][end:]
    if not sequence:
        raise ValueError("editing cannot produce an empty DNA material")
    if start == end and not inserted:
        return value, {"retired_features": [], "source_interval": [start, end], "insert_length": 0}
    source = record_from_material(value)
    delta = len(inserted) - (end - start)
    features, retired = [], []
    for index, feature in enumerate(source.features):
        overlaps = any((int(part.start) < end and int(part.end) > start) if start != end
                       else int(part.start) < start < int(part.end) for part in feature.location.parts)
        if overlaps:
            retired.append({"index": index, "type": feature.type, "reason": "Feature intersects the edited region; intact function is not asserted."})
            continue
        shifted_parts = []
        for part in feature.location.parts:
            shifted_parts.append(part._shift(delta) if int(part.start) >= end else deepcopy(part))
        updated = deepcopy(feature)
        if len(shifted_parts) == 1:
            updated.location = shifted_parts[0]
        else:
            from Bio.SeqFeature import CompoundLocation
            updated.location = CompoundLocation(shifted_parts, operator=feature.location.operator)
        features.append(updated)
    if replacement is not None:
        features.extend(feature._shift(start) for feature in record_from_material(replacement).features)
    result = record_from_material(make_material(sequence, topology=value["topology"], strandedness=value["strandedness"]))
    result.features = features
    return material_from_record(result, strandedness=value["strandedness"]), {
        "source_interval": [start, end], "insert_length": len(inserted), "length_delta": delta, "retired_features": retired,
    }


def inspect_cds(sequence: str, translation_table: int, *, codon_start: int = 1, partial: bool = False) -> dict:
    """Report CDS frame/start/stop consistency, without expression or phenotype claims."""
    sequence = normalize_dna(sequence, ambiguous=True)
    if type(translation_table) is not int or translation_table not in CodonTable.unambiguous_dna_by_id:
        raise ValueError("unknown explicit translation table")
    if type(codon_start) is not int or codon_start not in (1, 2, 3) or type(partial) is not bool:
        raise ValueError("codon_start must be 1..3 and partial must be boolean")
    table = CodonTable.unambiguous_dna_by_id[translation_table]
    coding = sequence[codon_start - 1:]
    complete_length = len(coding) // 3 * 3
    codons = [coding[index:index + 3] for index in range(0, complete_length, 3)]
    ambiguous = sum(base not in "ACGT" for base in coding)
    start = bool(codons) and codons[0] in table.start_codons
    stop = bool(codons) and len(coding) % 3 == 0 and codons[-1] in table.stop_codons
    internal_stops = sum(codon in table.stop_codons for codon in (codons[:-1] if stop else codons))
    consistent = bool(codons) and start and stop and internal_stops == 0 and len(coding) % 3 == 0
    translation = str(Seq(coding[:complete_length]).translate(table=translation_table))
    if consistent and not ambiguous and not partial:
        translation = str(Seq(coding).translate(table=translation_table, cds=True))
    return {"length": len(sequence), "coding_length": len(coding), "trailing_bases": len(coding) % 3,
            "start_codon_present": start, "terminal_stop_present": stop, "internal_stop_count": internal_stops,
            "ambiguous_base_count": ambiguous, "translation": translation,
            "complete_cds_consistent": None if partial or ambiguous else consistent,
            "parameters": {"translation_table": translation_table, "codon_start": codon_start, "partial": partial},
            "does_not_establish": ["Expression, selectable phenotype or biological function."]}
