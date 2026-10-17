"""Independent standard-library oracle. Reads actual output files, never imports Kit/Core."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def rc(sequence):
    return sequence.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def sites(sequence, target):
    return [index for index in range(len(sequence) - len(target) + 1)
            if all(sequence[index + offset] == base for offset, base in enumerate(target))]


def pcr(template, forward, reverse, forward_core=None, reverse_core=None):
    first_length, last_length = forward_core or len(forward), reverse_core or len(reverse)
    if not 0 < first_length <= len(forward) or not 0 < last_length <= len(reverse):
        raise ValueError("core length outside complete primer")
    products = []
    for first in sites(template, forward[-first_length:]):
        for last in sites(template, rc(reverse[-last_length:])):
            end = last + last_length
            if last >= first and end - first >= max(first_length, last_length):
                products.append(forward[:-first_length] + template[first:end] + rc(reverse[:-last_length]))
    return products


def fasta(path):
    return "".join(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith(">")).upper()


def genbank(path):
    text = path.read_text(encoding="utf-8")
    section = text.split("\nORIGIN\n", 1)[1].split("//", 1)[0]
    return "".join(re.findall("[acgtACGT]+", section)).upper()


def verify_run(root):
    root = Path(root)
    events = [json.loads(line) for line in (root / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
    started = {row["payload"]["step_id"]: row["payload"] for row in events if row["type"] == "step.started"}
    completed = {row["payload"]["step_id"]: row["payload"] for row in events if row["type"] == "step.completed"}
    registered = {row["payload"]["source_id"]: row["payload"] for row in events if row["type"] == "input.registered"}
    checked, problems = [], []
    def check(name, condition):
        checked.append(name)
        if not condition:
            problems.append(name)
    def material(identity):
        return json.loads((root / "store/materials" / (identity + ".json")).read_text(encoding="utf-8"))
    def document(step, port):
        identity = completed[step]["outputs"]["documents"][port][0]
        return json.loads((root / "store/documents" / (identity + ".json")).read_text(encoding="utf-8"))
    def artifact(step):
        return root / completed[step]["outputs"]["artifacts"][0]["run_path"]
    def source(step):
        origin = started[step]["inputs"]["file"]["origin"]
        row = registered[origin["ref"]]
        path = root / row["run_path"]
        check(step + " input hash", hashlib.sha256(path.read_bytes()).hexdigest() == row["file_sha256"])
        return fasta(path)
    reference, cargo = source("reference"), source("cargo")
    params = started["design"]["params"]
    start, end, arm = params["start"], params["end"], params["arm_length"]
    cstart, cend = params["cargo_start"], params["cargo_end"]
    check("homology arm coordinates", 0 <= start - arm < start <= end < end + arm <= len(reference))
    expected = reference[start - arm:start] + cargo[cstart:cend] + reference[end:end + arm]
    expected_edited = reference[:start] + cargo[cstart:cend] + reference[end:]
    donor = genbank(artifact("donor_file"))
    edited = genbank(artifact("edited_file"))
    check("donor length from construction", len(donor) == 2 * arm + cend - cstart)
    check("donor sequence from source intervals", donor == expected)
    check("edited reference from source replacement", edited == expected_edited)
    check("original reference file", genbank(artifact("original_file")) == reference)
    route = document("design", "route")
    recomputed = {}
    for reaction in route["reactions"]:
        inputs = [recomputed.get(identity, material(identity)["sequence"]) for identity in reaction["inputs"]]
        if reaction["method"] == "pcr":
            products = pcr(*inputs, reaction["params"]["forward_core_length"], reaction["params"]["reverse_core_length"])
            check(reaction["id"] + " unique PCR", len(products) == 1)
            calculated = products[0] if len(products) == 1 else ""
        else:
            overlap = reaction["params"]["overlap"]
            check(reaction["id"] + " actual overlap", inputs[0][-overlap:] == inputs[1][:overlap])
            calculated = inputs[0] + inputs[1][overlap:]
        check(reaction["id"] + " retained sequence", material(reaction["product_id"])["sequence"] == calculated)
        recomputed[reaction["product_id"]] = calculated
    check("reaction chain final output", bool(route["reactions"]) and calculated == donor)
    report = document("assay", "assay")
    primers = {row["id"]: row["sequence"] for row in report["primers"]["primers"]}
    backgrounds = {row["id"]: {p["pair_id"]: p for p in row["predictions"]} for row in report["backgrounds"]}
    for pair in report["primers"]["pairs"]:
        forward, reverse = primers[pair["forward"]], primers[pair["reverse"]]
        predictions = {}
        for name, sequence in (("original", reference), ("edited", edited), ("donor", donor)):
            products = pcr(sequence, forward, reverse)
            expected_row = {"pair_id": pair["id"], "product_count": len(products),
                "product_bp": len(products[0]) if len(products) == 1 else None,
                "forward_sites": len(sites(sequence, forward)) + len(sites(sequence, rc(forward))),
                "reverse_sites": len(sites(sequence, reverse)) + len(sites(sequence, rc(reverse)))}
            check(name + " " + pair["id"] + " every-base binding and length", backgrounds[name][pair["id"]] == expected_row)
            check(name + " " + pair["id"] + " no repeated primer sites", expected_row["forward_sites"] <= 1 and expected_row["reverse_sites"] <= 1)
            predictions[name] = products
        check(pair["id"] + " edited has unique product", len(predictions["edited"]) == 1)
        check(pair["id"] + " no residual donor band", not predictions["donor"])
        if cstart != cend:
            check(pair["id"] + " no original band", not predictions["original"])
        else:
            check(pair["id"] + " flanking length discriminates", len(predictions["original"]) == 1 and
                  len(predictions["original"][0]) != len(predictions["edited"][0]))
    handoff_path = artifact("handoff")
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    check("D11 exact handoff fields", set(handoff) == {"schema", "references", "regions", "primers"} and handoff["schema"] == "identity-handoff-v1")
    for row in handoff["references"]:
        path = artifact(row["role"] + "_file")
        check(row["role"] + " reference byte hash", row["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest())
    check("handoff exact primers", handoff["primers"] == [{"id": row["id"], "sequence": row["sequence"]} for row in report["primers"]["primers"]])
    check("handoff arm coordinates", {row["id"]: [row["start"], row["end"]] for row in handoff["regions"]} == {
        "replacement": [start, start + cend - cstart], "left_arm": [start - arm, start],
        "right_arm": [start + cend - cstart, start + cend - cstart + arm]})
    check("handoff file hash recorded by executor", completed["handoff"]["outputs"]["artifacts"][0]["sha256"] == hashlib.sha256(handoff_path.read_bytes()).hexdigest())
    return {"checked": checked, "problems": problems, "passed": not problems, "donor_bp": len(donor),
            "laboratory_status": "NOT_PERFORMED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify_run(args.run)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(text, end="")
    return int(not result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
