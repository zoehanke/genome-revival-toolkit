"""Standard-library-only S2 output oracle. No Kit, Core or Biopython imports."""
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def reverse_complement(sequence):
    complement = {"A": "T", "C": "G", "G": "C", "T": "A"}
    return "".join(complement[base] for base in reversed(sequence))


def sites(sequence, primer, core_length, circular):
    core = primer[-core_length:]
    size = len(sequence)
    found = []
    if core_length > size:
        return found
    for start in range(size if circular else size - core_length + 1):
        reference = "".join(sequence[(start + index) % size] for index in range(core_length))
        if reference == core:
            found.append((start, start + core_length, 1))
        if reference == reverse_complement(core):
            found.append((start, start + core_length, -1))
    return found


def check_output(run, candidate):
    """Recompute solely from actual retained inputs, primers and candidate files."""
    events = [json.loads(line) for line in (run / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
    started = next(event["payload"] for event in events if event["type"] == "step.started" and
                   event["payload"]["capability"]["id"] == "cut_plasmid.replace_spacer")
    completed = next(event["payload"] for event in events if event["type"] == "step.completed" and
                     event["payload"]["step_id"] == started["step_id"])
    template = load(run / "store/materials" / (started["inputs"]["vector"]["id"] + ".json"))
    target = load(run / "store/materials" / (started["inputs"]["target"]["id"] + ".json"))
    product = load(candidate / "construct.json")
    primers = load(candidate / "primers.json")
    route = load(run / "store/documents" / (completed["outputs"]["documents"]["route"][0] + ".json"))
    original, actual = template["sequence"], product["sequence"]
    size, params = len(original), started["params"]
    if len(actual) != size or product["topology"] != "circular":
        raise ValueError("Output must retain template length and explicit circular topology.")
    boundary, strand, guide = params["promoter_end"], params["transcription_strand"], params["spacer"]
    changed = [(boundary + index if strand == 1 else boundary - 1 - index) % size for index in range(20)]
    expected = list(original)
    for index, base in zip(changed, guide if strand == 1 else guide.translate(str.maketrans("ACGT", "TGCA"))):
        expected[index] = base
    if actual != "".join(expected):
        raise ValueError("Candidate differs from the independently specified spacer-only edit.")
    if any(actual[index] != original[index] for index in range(size) if index not in changed):
        raise ValueError("Bases outside the spacer changed.")
    valid = 0
    for oriented in (target["sequence"], reverse_complement(target["sequence"])):
        search = oriented + oriented[:22] if target["topology"] == "circular" else oriented
        for index in range(len(oriented)):
            if search[index:index + 20] == guide and len(search[index + 20:index + 23]) == 3 and search[index + 21:index + 23] == "GG":
                valid += 1
    if not valid:
        raise ValueError("Selected spacer has no exact target followed by NGG.")
    by_id = {primer["id"]: primer for primer in primers["primers"]}
    forward, reverse = by_id[route["forward_primer_id"]], by_id[route["reverse_primer_id"]]
    first = sites(original, forward["sequence"], forward["core_length"], True)
    last = sites(original, reverse["sequence"], reverse["core_length"], True)
    if len(first) != 1 or len(last) != 1 or first[0][2] != 1 or last[0][2] != -1:
        raise ValueError("Full declared primer cores must bind uniquely in the intended directions.")
    span = (last[0][1] - first[0][0]) % size or size
    if span < max(forward["core_length"], reverse["core_length"]):
        raise ValueError("Primer binding intervals cannot form the retained amplicon.")
    extension = "".join(original[(first[0][0] + index) % size] for index in range(span))
    forward_tail = forward["sequence"][:-forward["core_length"]]
    reverse_tail = reverse["sequence"][:-reverse["core_length"]]
    linear = forward_tail + extension + reverse_complement(reverse_tail)
    if linear != route["simulation"]["linear_sequence"] or route["closing_overlap"] != 0:
        raise ValueError("Independently extended linear PCR differs from the retained intermediate.")
    reference_end = (boundary + 20) % size if strand == 1 else boundary % size
    rotation = (size - reference_end) % size
    circular = linear[rotation:] + linear[:rotation]
    if rotation != route["rotation_to_template_origin"] or circular != actual:
        raise ValueError("Independent inverse-PCR and blunt circularization disagree with the candidate base by base.")
    return {"outcome": "PASS", "template_bp": size, "product_bp": len(actual),
            "outside_spacer_unchanged": True, "exact_NGG_target_count": valid,
            "primer_binding_site_counts": [len(first), len(last)], "linear_intermediate_matches": True,
            "inverse_pcr_circularization_matches": True, "candidate_sealed": False,
            "scope": "Synthetic sequence and reaction models only; physical experiments NOT_PERFORMED."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = check_output(args.run, args.candidate)
    except (ValueError, KeyError, OSError, StopIteration) as error:
        result = {"outcome": "FAIL", "reason": str(error)}
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["outcome"] == "PASS" else 1)
