# ported-from: snapgene-dna-design/core/models/molecule.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/io/molecule_codec.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Pure adapters to S1 kernel material dictionaries, never a second material type."""
from __future__ import annotations

import base64
import textwrap
from copy import deepcopy

from Bio.Seq import Seq
from Bio.SeqFeature import CompoundLocation, ExactPosition, SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord

from dna_design_core.kernel import canonical, ids
from dna_design_core.kernel.material import normalize
from .formats.records import read_genbank, record_projection, write_fasta, write_genbank
from .sequence.operations import normalize_dna
from .assembly.simulation import validate_duplex


def make_material(
    sequence: str, *, topology: str | None = None, strandedness: str | None = None,
    ends: dict | None = None, features: list | None = None,
) -> dict:
    """Construct through kernel.material.normalize with explicit physical unknowns."""
    sequence = normalize_dna(sequence, ambiguous=True)
    if topology not in (None, "linear", "circular") or strandedness not in (None, "single", "double"):
        raise ValueError("invalid topology or strandedness")
    if ends is not None:
        if topology != "linear" or strandedness != "double" or set(ends) != {"left", "right"}:
            raise ValueError("duplex ends require an explicitly linear double-stranded material")
        ends = deepcopy(ends)
        for end in ends.values():
            if end is None:
                continue
            if set(end) != {"kind", "overhang"} or end["kind"] not in ("blunt", "5prime", "3prime"):
                raise ValueError("invalid duplex end")
            if end["kind"] == "blunt":
                if end["overhang"] != "":
                    raise ValueError("blunt end cannot carry an extension")
            else:
                end["overhang"] = normalize_dna(end["overhang"])
        if all(end is None for end in ends.values()):
            ends = None
    value = normalize({"sequence": sequence, "topology": topology, "strandedness": strandedness,
                       "ends": ends, "features": deepcopy(features or [])})
    record_from_material(value)  # validate exact feature coordinates and qualifier representation
    if ends is not None:
        material_to_duplex(value)
    return value


def record_from_material(material: dict) -> SeqRecord:
    """Convert exact local features without changing their biological part order."""
    value = normalize(material)
    record = SeqRecord(Seq(value["sequence"]), id="material", name="material", description="material",
                       annotations={"molecule_type": "DNA"})
    if value["topology"] is not None:
        record.annotations["topology"] = value["topology"]
    for feature in value["features"]:
        if not isinstance(feature["type"], str) or not isinstance(feature["label"], str):
            raise ValueError("feature type and label must be strings")
        parts = feature.get("parts") or [{"start": feature["start"], "end": feature["end"], "strand": feature.get("strand")}]
        locations = []
        for part in parts:
            start, end, strand = part["start"], part["end"], part.get("strand")
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(record):
                raise ValueError("exact feature part outside material")
            if strand not in (None, -1, 0, 1):
                raise ValueError("invalid feature strand")
            locations.append(SimpleLocation(start, end, strand=strand))
        if min(int(part.start) for part in locations) != feature["start"] or max(int(part.end) for part in locations) != feature["end"]:
            raise ValueError("feature envelope differs from its parts")
        qualifiers = deepcopy(feature.get("qualifiers", {}))
        if not isinstance(qualifiers, dict) or any(not isinstance(key, str) or not isinstance(values, list)
                or any(not isinstance(item, str) for item in values) for key, values in qualifiers.items()):
            raise ValueError("qualifiers require string keys and arrays of strings")
        if feature["label"] and "label" not in qualifiers:
            qualifiers["label"] = [feature["label"]]
        location = locations[0] if len(locations) == 1 else CompoundLocation(locations, feature.get("operator") or "join")
        record.features.append(SeqFeature(location, type=feature["type"], qualifiers=qualifiers))
    return record


def material_from_record(record: SeqRecord, *, strandedness: str | None = None, ends: dict | None = None) -> dict:
    """Preserve exact parts/qualifiers; reject fuzzy or remote material conversion."""
    features = []
    for feature in record.features:
        if feature.location is None:
            raise ValueError("material feature requires a location")
        parts = []
        for part in feature.location.parts:
            if type(part.start) is not ExactPosition or type(part.end) is not ExactPosition or part.ref or part.ref_db:
                raise ValueError("kernel material adapter requires exact local feature positions")
            parts.append({"start": int(part.start), "end": int(part.end), "strand": part.strand})
        label = feature.qualifiers.get("label", feature.qualifiers.get("gene", [""]))
        features.append({"start": min(p["start"] for p in parts), "end": max(p["end"] for p in parts),
                         "type": feature.type, "label": label[0] if label else "", "parts": parts,
                         "operator": getattr(feature.location, "operator", None), "qualifiers": deepcopy(feature.qualifiers)})
    return make_material(str(record.seq), topology=record.annotations.get("topology"),
                         strandedness=strandedness, ends=ends, features=features)


def material_to_duplex(material: dict) -> dict:
    """Derive both strands from the top sequence plus actual physical extensions."""
    value = normalize(material)
    if value["topology"] != "linear" or value["strandedness"] != "double":
        raise ValueError("duplex operation requires explicitly linear double-stranded material")
    sequence = normalize_dna(value["sequence"])
    ends = value["ends"] or {"left": None, "right": None}
    left, right = ends["left"], ends["right"]
    left_kind = left["kind"] if left else "blunt"
    right_kind = right["kind"] if right else "blunt"
    left_extension = left["overhang"] if left else ""
    right_extension = right["overhang"] if right else ""
    start = len(left_extension) if left_kind == "5prime" else 0
    end = len(sequence) - (len(right_extension) if right_kind == "3prime" else 0)
    if start >= end:
        raise ValueError("duplex needs a nonempty shared core")
    bottom_reference = (
        (str(Seq(left_extension).reverse_complement()) if left_kind == "3prime" else "")
        + sequence[start:end]
        + (str(Seq(right_extension).reverse_complement()) if right_kind == "5prime" else "")
    )
    offset = -len(left_extension) if left_kind == "3prime" else start
    result = {"top_sequence": sequence, "bottom_sequence": str(Seq(bottom_reference).reverse_complement()),
              "bottom_offset": offset, "topology": "linear", "left_end": deepcopy(left), "right_end": deepcopy(right)}
    validate_duplex(result)
    return result


def material_from_duplex(fragment: dict, *, features: list | None = None) -> dict:
    """Build a kernel material after validating actual calculated strand bases."""
    validate_duplex(fragment)
    return make_material(fragment["top_sequence"], topology="linear", strandedness="double",
                         ends={"left": fragment["left_end"], "right": fragment["right_end"]}, features=features)


def material_to_genbank(material: dict) -> str:
    """Bind kernel-only fields to the visible GenBank projection, preserving identity.

    This is the copied codec's authenticated supplement idea: it never restores
    a different visible sequence/feature record. Hashing stays in kernel.ids.
    """
    value = normalize(material)
    record = record_from_material(value)
    supplement = {"projection": ids.document_id(record_projection(record)), "material": value}
    encoded = base64.b64encode(canonical.dumps(supplement)).decode("ascii")
    record.annotations["comment"] = "GRT-MATERIAL:\n" + "\n".join(textwrap.wrap(encoded, 60))
    return write_genbank(record)


def material_from_genbank(text: str) -> dict:
    """Restore a supplement only when its visible content binding still matches."""
    record = read_genbank(text)
    comment = record.annotations.get("comment", "")
    if "GRT-MATERIAL:" not in comment:
        return material_from_record(record)
    encoded = "".join(comment.split("GRT-MATERIAL:", 1)[1].split())
    supplement = canonical.loads(base64.b64decode(encoded, validate=True))
    actual = record_projection(record)
    value = normalize(supplement["material"])
    if supplement["projection"] != ids.document_id(actual) or record_projection(record_from_material(value)) != actual:
        raise ValueError("GenBank material supplement no longer matches visible content")
    return make_material(**value)


def material_to_fasta(material: dict) -> str:
    """Refuse metadata loss; FASTA round-trips only the representable subset."""
    value = normalize(material)
    if any(value[key] is not None for key in ("topology", "strandedness", "ends")) or value["features"]:
        raise ValueError("FASTA cannot preserve material topology, strands, ends or features")
    return write_fasta(record_from_material(value))
