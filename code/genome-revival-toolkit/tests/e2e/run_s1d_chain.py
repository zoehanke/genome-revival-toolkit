"""Public CLI handoff regression. Supplied inputs must be synthetic.

Expected DNA and PCR spans are derived from input coordinates, without importing
Core or Kit algorithms. Requests and failed commands are retained unchanged.
"""
import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "src/dna_design_core/application/cli.py"
GUARD = ROOT / "tests/e2e/network_guard.py"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sequence(path):
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        return json.loads(text)["sequence"].upper()
    if text.startswith(">"):
        return "".join(line.strip() for line in text.splitlines() if not line.startswith(">")).upper()
    return "".join(re.findall("[acgtACGT]+", text.split("\nORIGIN\n", 1)[1].split("//", 1)[0])).upper()


def rc(value):
    return value.translate(str.maketrans("ACGT", "TGCA"))[::-1]


def bands(template, forward, reverse):
    """Independent exhaustive exact-site enumeration, both orientations."""
    spans = set()
    for first, last in ((forward, reverse), (reverse, forward)):
        for left in range(len(template) - len(first) + 1):
            if template[left:left + len(first)] != first:
                continue
            for right in range(left, len(template) - len(last) + 1):
                if template[right:right + len(last)] == rc(last):
                    spans.add((left, right + len(last)))
    return sorted(end - start for start, end in spans)


def events(package):
    return [json.loads(line) for line in (package / "journal-until-seal.ndjson").read_text(encoding="utf-8").splitlines()]


class Chain:
    def __init__(self, output):
        self.root = output.resolve()
        self.root.mkdir(parents=True, exist_ok=False)
        self.receipts = []

    def command(self, *args):
        number = len(self.receipts)
        audit = self.root / (f"network-{number:03}.json")
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(GUARD), str(audit), str(CLI), *map(str, args)],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        (self.root / f"command-{number:03}.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (self.root / f"command-{number:03}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        value = json.loads(result.stdout)
        row = {"arguments": list(map(str, args)), "exit_code": result.returncode,
               "receipt": value, "network": load(audit)}
        self.receipts.append(row)
        write(self.root / "receipts.json", self.receipts)
        assert row["network"]["attempts"] == 0, row
        assert result.returncode == 0, row
        return value["result"]

    def request(self, name, value):
        return write(self.root / "requests" / (name + ".json"), value)

    def goal(self, sources, targets, exact=None):
        version = load(ROOT / "VERSIONS.json")["core"]
        constraint = {"id": "present", "check": "check.goal.output_present@" + version,
                      "params": {}, "target": targets[0][0], "source_quote": "Retain the requested output.", "status": "active"}
        if exact is not None:
            constraint.update(id="exact", check="check.goal.exact_sequence@" + version,
                              params={"sequence": exact}, source_quote="Donor from the declared source intervals.")
        return {"schema": "goal-v1", "version": 1, "parent_digest": None,
                "original_request": "Synthetic computational handoff; laboratory work PLANNED / NOT_PERFORMED.",
                "sources": [{"source_id": name, "from": str(path.resolve()), "as": "artifact",
                             "input_origin": "user_file", "declared": {}} for name, path in sources.items()],
                "declared_context": [], "targets": [{"id": name, "role": role, "required": True} for name, role in targets],
                "constraints": [constraint], "intents": []}

    def execute(self, name, goal, template, params):
        run = self.root / name / "run"
        self.command("run", "create", run)
        declared = self.command("goal", "declare", "--run", run, "--request", self.request(name + "-goal", goal))
        request = {"goal_digest": declared["goal_digest"], **params}
        draft = self.command("template", "instantiate", template, "--run", run,
                             "--request", self.request(name + "-params", request))["draft"]
        # Submit the returned draft verbatim. No host adaptation is permitted.
        self.command("pipeline", "submit", "--run", run, "--request", self.request(name + "-pipeline", draft))
        self.command("run", "execute", "--run", run)
        self.command("judge", "--run", run)
        sealed = self.command("seal", "--run", run)
        assert sealed["sealed"], sealed
        package = Path(sealed["manifest"]).parent
        present = [Path(path).relative_to(package) for path in sealed["present_files"]]
        portable = self.root / name / "portable" / package.name
        shutil.copytree(package, portable)
        retained = run.with_name("original-run-retained")
        assert run.resolve().is_relative_to(self.root) and retained.resolve().is_relative_to(self.root)
        run.rename(retained)
        assert self.command("verify", portable)["verified"]
        return portable, [portable / path for path in present]


def run(args):
    chain = Chain(args.out)
    summary = {"scope": "developer-run synthetic regression, not an independent user evaluation",
               "laboratory": "PLANNED / NOT_PERFORMED", "official_gitlab_ci": "not executed", "github_ci": "not run"}
    try:
        reference, cargo = sequence(args.reference), sequence(args.cargo)
        start, end, arm, length = args.start, args.end, args.arm_length, args.primer_length
        selected = cargo[args.cargo_start:args.cargo_end]
        donor = reference[start-arm:start] + selected + reference[end:end+arm]
        edited = reference[:start] + selected + reference[end:]
        forward, reverse = reference[start-arm-length:start-arm], rc(edited[start:start+length])
        wanted = {"original": bands(reference, forward, reverse), "edited": bands(edited, forward, reverse)}
        assert wanted["original"] == [] and wanted["edited"] == [arm + 2 * length], wanted
        summary["independent_construction"] = {"donor_bp": len(donor), "bands": wanted}
        targets = [("donor", "construct"), ("primers", "primer_set"), ("assay", "analysis"), ("handoff", "analysis")]
        construct, delivered = chain.execute("construct", chain.goal({"input_reference": args.reference, "input_cargo": args.cargo}, targets, donor),
            "construct.prepare_gibson", {"reference_source": "input_reference", "cargo_source": "input_cargo",
                "donor_target": "donor", "primers_target": "primers", "assay_target": "assay", "handoff_target": "handoff",
                "start": start, "end": end, "arm_length": arm, "cargo_start": args.cargo_start,
                "cargo_end": args.cargo_end, "primer_length": length, "overlap": args.overlap})
        handoff_path = next(path for path in delivered if path.suffix == ".json" and load(path).get("schema") == "identity-handoff-v1")
        handoff = load(handoff_path)
        # Only public delivery files, never the work directory, can supply inputs.
        bound = {}
        for row in handoff["references"]:
            matches = [path for path in delivered if sha(path) == row["sha256"]]
            assert len(matches) == 1, "Handoff " + row["role"] + " reference is absent from present_files."
            bound[row["role"]] = matches[0]
        assert sequence(bound["original"]) == reference and sequence(bound["edited"]) == edited
        manifest = load(construct / "manifest.json")
        donors = [construct / row["path"] for row in manifest["files"] if row["role"] == "construct"]
        assert len(donors) == 1 and sequence(donors[0]) == donor
        oligos = {row["id"]: row["sequence"] for row in handoff["primers"]}
        assert oligos["left_forward"] == forward and oligos["left_reverse"] == reverse
        identity, identity_files = chain.execute("identity", chain.goal({**bound, "handoff": handoff_path}, [("table", "analysis")]),
            "genome-identity.from_handoff", {"original_source": "original", "edited_source": "edited", "handoff_source": "handoff",
                "original_topology": "linear", "edited_topology": "linear", "target": "table", "assay_id": "left_junction",
                "forward_id": "left_forward", "reverse_id": "left_reverse"})
        table_path = next(path for path in identity_files if path.suffix == ".json" and load(path).get("schema") == "identity-expected-results-v1")
        table = load(table_path)
        for row in table["backgrounds"]:
            products = wanted[row["id"]]
            assert row["reference_sha256"] == sha(bound[row["id"]])
            assert row["expected"] == {"product_count": len(products), "product_bp": products[0] if products else None,
                                      "status": "DISTINGUISHABLE"}, row
        observations = {"observations": [], "observation_origin": "SYNTHETIC_NOT_EXPERIMENTAL", "genotype_results": [
            {"sample_id": "constructed_" + name, "assay_id": "left_junction", "background_id": name,
             "reference_sha256": sha(bound[name]), "result": "positive" if products else "negative",
             "observed_band_bp": products[0] if products else None, "control_status": "passed", "band_tolerance_bp": 0}
            for name, products in wanted.items()]}
        observation_path = chain.request("synthetic-observations", observations)
        evidence, _ = chain.execute("evidence", chain.goal({"observations": observation_path, "predictions": table_path}, [("t1", "analysis")]),
            "revival-evidence.assess_predictions", {"source_id": "observations", "predictions_source": "predictions",
                "observation_origin": "SYNTHETIC_NOT_EXPERIMENTAL", "comparisons": []})
        assessment = load(evidence / "assessment.json")
        local = [row for row in assessment["conclusions"] if row["claim"] == "local_prediction_agreement"]
        assert len(local) == 2 and all(row["status"] == "SUPPORTED" for row in local), local
        links = []
        for producer, consumer, path, source in (("Construct", identity, handoff_path, "handoff"),
                                                ("Genome Identity", evidence, table_path, "predictions")):
            registered = next(row["payload"]["file_sha256"] for row in events(consumer)
                              if row["type"] == "input.registered" and row["payload"]["source_id"] == source)
            assert sha(path) == registered
            links.append({"source": producer, "target": "Genome Identity" if source == "handoff" else "Revival Evidence",
                          "basis": "hash_equal", "sha256": registered})
        summary.update(passed=True, sealed_runs=3, local_agreement="SUPPORTED", hash_links=links,
                       templates_submitted_without_edits=True, primer_files_created=False)
        description = "Three synthetic sealed runs. Donor: " + str(len(donor)) + " bp. Local PCR: " + str(wanted) + "."
        diagram = '<svg viewBox="0 0 900 110" role="img" aria-label="Equal-file-hash links">'
        for index, name in enumerate(("Construct", "Genome Identity", "Revival Evidence")):
            x = 10 + index * 300
            diagram += f'<rect x="{x}" y="10" width="240" height="65" fill="#eef3ef" stroke="#53665a"/>'
            diagram += f'<text x="{x+10}" y="35">{escape(name)}</text>'
            if index < 2:
                diagram += f'<path data-basis="hash_equal" d="M{x+240},45 H{x+300}" fill="none" stroke="#176246" stroke-width="3"/>'
                diagram += f'<text x="{x+10}" y="62">{links[index]["sha256"][:12]}</text>'
        diagram += '</svg>'
        (chain.root / "chain-card.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Synthetic handoff</title>'
            '<h1>Three-Kit handoff</h1><p>' + escape(description) + '</p>' + diagram +
            '<p>Links verify equal file bytes only. Example projection of three sealed records, not a causal claim. '
            'Local agreement: SUPPORTED. Laboratory: PLANNED / NOT_PERFORMED.</p></html>', encoding="utf-8")
    except (AssertionError, KeyError, StopIteration, ValueError, IndexError) as error:
        summary.update(passed=False, failure=str(error) or type(error).__name__)
    summary.update(commands=len(chain.receipts), connection_attempts=sum(row["network"]["attempts"] for row in chain.receipts))
    write(chain.root / "SUMMARY.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--cargo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    for field in ("start", "end", "arm-length", "cargo-start", "cargo-end", "primer-length", "overlap"):
        parser.add_argument("--" + field, type=int, required=True)
    result = run(parser.parse_args())
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
