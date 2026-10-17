# ported-from: snapgene-dna-design/core/tools/snapgene_io.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/io/molecule_codec.py@750bf4849b818be00f28684513ef19c01d901bcb
# ported-from: snapgene-dna-design/core/io/input_resolution.py@750bf4849b818be00f28684513ef19c01d901bcb
"""In-memory DNA format codecs. No paths, file access or native binary writer.

GenBank equivalence covers sequence, topology and feature locations/qualifiers.
FASTA represents sequence and header only and rejects annotated input.
"""
from __future__ import annotations

from copy import deepcopy
from io import BytesIO, StringIO

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from ..sequence.operations import normalize_dna


def record_projection(record: SeqRecord) -> dict:
    """Content expressible by this GenBank codec, not a kernel material/identity."""
    return {
        "sequence": normalize_dna(str(record.seq), ambiguous=True),
        "topology": record.annotations.get("topology"),
        "molecule_type": record.annotations.get("molecule_type", "DNA"),
        "features": [{
            "type": feature.type, "location": str(feature.location),
            "qualifiers": deepcopy(feature.qualifiers),
        } for feature in record.features],
    }


def read_genbank(text: str) -> SeqRecord:
    """Read exactly one complete GenBank record; preserve supported annotations."""
    if not isinstance(text, str):
        raise TypeError("GenBank input must be text")
    if not text.rstrip().endswith("//"):
        raise ValueError("GenBank record must end with //")
    record = SeqIO.read(StringIO(text), "genbank")
    normalize_dna(str(record.seq), ambiguous=True)
    if "DNA" not in record.annotations.get("molecule_type", "").upper():
        raise ValueError("GenBank record must declare DNA")
    return record


def write_genbank(record: SeqRecord) -> str:
    """Serialize one record, refusing silent loss of sequence/topology/features."""
    expected = record_projection(record)
    if record.letter_annotations:
        raise ValueError("GenBank cannot retain per-letter annotations")
    if expected["topology"] not in (None, "linear", "circular"):
        raise ValueError("invalid topology")
    writable = deepcopy(record)
    writable.annotations.setdefault("molecule_type", "DNA")
    buffer = StringIO()
    SeqIO.write(writable, buffer, "genbank")
    text = buffer.getvalue()
    if record_projection(read_genbank(text)) != expected:
        raise ValueError("GenBank would change sequence, topology or feature annotations")
    return text


def read_fasta(text: str) -> SeqRecord:
    """Read exactly one DNA FASTA record; topology/physical ends stay unknown."""
    if not isinstance(text, str):
        raise TypeError("FASTA input must be text")
    if not text.startswith(">"):
        raise ValueError("FASTA input must begin with a header")
    record = SeqIO.read(StringIO(text), "fasta")
    normalize_dna(str(record.seq), ambiguous=True)
    record.seq = record.seq.upper()
    record.annotations["molecule_type"] = "DNA"
    return record


def write_fasta(record: SeqRecord) -> str:
    """Write sequence/header only. Annotated records need explicit projection first."""
    normalize_dna(str(record.seq), ambiguous=True)
    if record.features or record.letter_annotations or set(record.annotations) - {"molecule_type"}:
        raise ValueError("FASTA cannot preserve topology, features or other annotations")
    if record.annotations.get("molecule_type", "DNA") != "DNA":
        raise ValueError("FASTA codec accepts DNA records only")
    if not record.id or any(char.isspace() for char in record.id):
        raise ValueError("FASTA identifier must be nonempty without whitespace")
    if any(char in record.description for char in "\r\n"):
        raise ValueError("FASTA description must be one line")
    writable = deepcopy(record)
    writable.seq = writable.seq.upper()
    buffer = StringIO()
    SeqIO.write(writable, buffer, "fasta")
    return buffer.getvalue()


def read_dna(data: bytes) -> SeqRecord:
    """Read supported native .dna packets via Biopython; no sgffp dependency.

    Sequence, topology and supported feature packets are extracted. This does
    not preserve every native block and is not a full-fidelity archive reader.
    """
    if not isinstance(data, bytes):
        raise TypeError("native DNA input must be bytes")
    record = SeqIO.read(BytesIO(data), "snapgene")
    normalize_dna(str(record.seq), ambiguous=True)
    return record
