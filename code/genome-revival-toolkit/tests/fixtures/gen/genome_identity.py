"""S5b synthetic constructions. No Kit or Core implementation supplies answers."""
import hashlib
import json
from pathlib import Path


FORWARD = "ACGTCGATGCTAGTACCGTA"
REVERSE = "TGACCTAGCGTACAGGATCA"
# Hand complement and reverse of REVERSE, independently written and checked below.
REVERSE_SITE = "TGATCCTGTACGCTAGGTCA"


def material(sequence, *, primer=False, circular=False):
    return {"sequence": sequence, "topology": "circular" if circular else "linear",
            "strandedness": "single" if primer else "double", "ends": None, "features": []}


def build(folder, case="different_sizes"):
    """Lengths follow literal layout, before any runtime call or expected-file comparison."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    assert REVERSE.translate(str.maketrans("ACGT", "TGCA"))[::-1] == REVERSE_SITE
    original = FORWARD + "A" * 960 + REVERSE_SITE
    edited = FORWARD + "A" * 480 + "C" * 300 + "A" * 480 + REVERSE_SITE
    expected = [(1, 1000), (1, 1300)]
    status, circular = "DISTINGUISHABLE", False
    if case == "same_sizes":
        edited = FORWARD + "C" * 960 + REVERSE_SITE
        expected, status = [(1, 1000), (1, 1000)], "NOT_DISTINGUISHABLE"
    elif case == "multiple_sites":
        # Two forward sites, one reverse site: spans 1020 and 520, no certain scalar size.
        edited = FORWARD + "A" * 480 + FORWARD + "A" * 480 + REVERSE_SITE
        expected, status = [(1, 1000), (2, None)], "UNDETERMINED"
    elif case == "no_product":
        edited = "C" * 1000
        expected = [(1, 1000), (0, None)]
    elif case == "both_absent":
        original, edited = "A" * 1000, "C" * 1300
        expected, status = [(0, None), (0, None)], "NOT_DISTINGUISHABLE"
    elif case == "circular_origin":
        # Rotate ten bases: forward site crosses origin; same complete molecule and product lengths.
        original, edited = original[10:] + original[:10], edited[10:] + edited[:10]
        circular = True
    elif case == "reverse_orientation":
        original = original.translate(str.maketrans("ACGT", "TGCA"))[::-1]
        edited = edited.translate(str.maketrans("ACGT", "TGCA"))[::-1]
    elif case != "different_sizes":
        raise ValueError("Unknown synthetic construction")
    sequences = {"original": original, "edited": edited, "forward": FORWARD, "reverse": REVERSE}
    paths = {}
    for name, sequence in sequences.items():
        path = folder / (name + ".fasta")
        path.write_text(">synthetic_" + name + "\n" + sequence + "\n", encoding="utf-8", newline="\n")
        paths[name] = path
    hashes = {name: hashlib.sha256(paths[name].read_bytes()).hexdigest() for name in ("original", "edited")}
    handoff = {"schema": "identity-handoff-v1", "references": [
        {"id": name, "sha256": hashes[name], "role": name} for name in ("original", "edited")],
        "regions": [{"id": name + "_region", "reference_id": name, "start": 0, "end": len(sequences[name])}
                    for name in ("original", "edited")],
        "primers": [{"id": "forward", "sequence": FORWARD}, {"id": "reverse", "sequence": REVERSE}]}
    result = {"schema": "identity-expected-results-v1", "assay_id": "synthetic_identity",
              "backgrounds": [{"id": name, "reference_sha256": hashes[name], "primer_pair": ["forward", "reverse"],
                               "expected": {"product_count": count, "product_bp": length, "status": status}}
                              for name, (count, length) in zip(("original", "edited"), expected)]}
    for name, data in (("identity-handoff.json", handoff), ("identity-expected-results.json", result)):
        (folder / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"paths": paths, "handoff": handoff, "expected": result, "materials": {
        name: material(sequence, primer=name in ("forward", "reverse"), circular=circular and name in ("original", "edited"))
        for name, sequence in sequences.items()}}
