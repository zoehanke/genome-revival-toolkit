"""Independent standard-library FASTA/PCR oracle. Imports no Core or Kit code."""
import argparse
import hashlib
import json
from pathlib import Path


def fasta(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    headers = [line for line in lines if line.startswith(">")]
    if len(headers) != 1 or not lines or not lines[0].startswith(">"):
        raise ValueError("Oracle accepts exactly one FASTA record")
    sequence = "".join(line.strip() for line in lines[1:]).upper()
    if not sequence or set(sequence) - set("ACGT"):
        raise ValueError("Oracle requires concrete DNA")
    return sequence


def products(sequence, forward, reverse, circular=False):
    """Enumerate candidate physical windows and check each endpoint base by base."""
    size = len(sequence)
    matches = set()
    for left, right in ((forward, reverse), (reverse, forward)):
        target = right.translate(str.maketrans("ACGT", "TGCA"))[::-1]
        if max(len(left), len(target)) > size:
            continue
        for start in range(size):
            if not circular and start + len(left) > size:
                continue
            if not all(sequence[(start + i) % size] == base for i, base in enumerate(left)):
                continue
            last_span = size if circular else size - start
            for span in range(max(len(left), len(target)), last_span + 1):
                right_start = start + span - len(target)
                if all(sequence[(right_start + i) % size] == base for i, base in enumerate(target)):
                    matches.add((start, span))
    return sorted(matches)


def check(original, edited, forward, reverse, expected, *, circular_original=False,
          circular_edited=False, handoff=None, forward_id="forward", reverse_id="reverse"):
    table = json.loads(Path(expected).read_text(encoding="utf-8"))
    assert set(table) == {"schema", "assay_id", "backgrounds"}
    assert table["schema"] == "identity-expected-results-v1" and len(table["backgrounds"]) == 2
    oligos = fasta(forward), fasta(reverse)
    paths = [Path(original), Path(edited)]
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
    identifiers = ["reference_original", "reference_edited"]
    if handoff is not None:
        document = json.loads(Path(handoff).read_text(encoding="utf-8"))
        assert document["schema"] == "identity-handoff-v1"
        refs = {row["role"]: row for row in document["references"]}
        identifiers = [refs[role]["id"] for role in ("original", "edited")]
        assert [refs[role]["sha256"] for role in ("original", "edited")] == hashes
        primers = {row["id"]: row["sequence"].upper() for row in document["primers"]}
        assert (primers[forward_id], primers[reverse_id]) == oligos
    predictions = [products(fasta(path), *oligos, circular=circle)
                   for path, circle in zip(paths, (circular_original, circular_edited))]
    counts = [len(rows) for rows in predictions]
    lengths = [rows[0][1] if len(rows) == 1 else None for rows in predictions]
    if max(counts) > 1:
        status = "UNDETERMINED"
    elif (counts[0], lengths[0]) == (counts[1], lengths[1]):
        status = "NOT_DISTINGUISHABLE"
    else:
        status = "DISTINGUISHABLE"
    rows = {row["id"]: row for row in table["backgrounds"]}
    assert len(rows) == 2 and set(rows) == set(identifiers)
    for identifier, digest, count, length in zip(identifiers, hashes, counts, lengths):
        row = rows[identifier]
        assert set(row) == {"id", "reference_sha256", "primer_pair", "expected"}
        assert row["reference_sha256"] == digest and row["primer_pair"] == [forward_id, reverse_id]
        assert row["expected"] == {"status": status, "product_count": count, "product_bp": length}, row
    return {"checked_backgrounds": 2, "product_counts": counts, "product_bp": lengths, "status": status,
            "oracle": "independent standard-library window enumeration", "laboratory_status": "NOT_PERFORMED"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "edited", "forward", "reverse", "expected"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--handoff", type=Path)
    parser.add_argument("--circular-original", action="store_true")
    parser.add_argument("--circular-edited", action="store_true")
    parser.add_argument("--forward-id", default="forward")
    parser.add_argument("--reverse-id", default="reverse")
    print(json.dumps(check(**vars(parser.parse_args())), indent=2))
