"""Run synthetic Genome Identity through public CLI, sealing and portable verification."""
import argparse
from copy import deepcopy
from importlib.util import find_spec
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from dna_design_core.kernel.public import core_version
from tests.fixtures.gen.genome_identity import build
from tests.oracles.genome_identity import check

CLI = Path(find_spec("dna_design_core.application.cli").origin)
GUARD = ROOT / "tests/e2e/network_guard.py"


def run(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Choose a new output directory; earlier evidence is retained.")
    output.mkdir(parents=True)
    receipts, audits = [], []

    def write(path, data):
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
        return path

    def command(folder, *arguments, expected=0):
        audit = output / ("network-" + str(len(audits)) + ".json")
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", str(GUARD), str(audit), str(CLI), *map(str, arguments)],
            cwd=folder, capture_output=True, text=True, encoding="utf-8", check=False,
        )
        # Retain stdout/stderr even if parsing a broken receipt fails.
        number = len(receipts)
        (output / ("command-" + str(number) + ".stdout.txt")).write_text(completed.stdout, encoding="utf-8")
        (output / ("command-" + str(number) + ".stderr.txt")).write_text(completed.stderr, encoding="utf-8")
        receipt = json.loads(completed.stdout)
        receipts.append({"arguments": list(map(str, arguments)), "exit_code": completed.returncode, "receipt": receipt})
        write(output / "receipts.json", receipts)
        audit_result = json.loads(audit.read_text(encoding="utf-8"))
        audits.append(audit_result)
        assert audit_result["attempts"] == 0, audit_result
        allowed = expected if isinstance(expected, tuple) else (expected,)
        assert completed.returncode in allowed, receipts[-1]
        return receipt

    summaries = {}
    for name in ("different_sizes", "handoff_hash"):
        folder = output / name
        fixture = build(folder, "different_sizes")
        if name == "handoff_hash":
            handoff = deepcopy(fixture["handoff"])
            handoff["references"][0]["sha256"] = "0" * 64
            write(folder / "identity-handoff.json", handoff)
        directory = folder / "run"
        request_path = folder / "request.json"
        created = command(folder, "run", "create", directory)
        assert created["result"]["kit_diagnostics"] == [], created
        text = "Report exact synthetic PCR expectations for the original and edited supplied references."
        sources = [{"source_id": role, "from": str(path), "as": "artifact", "input_origin": "user_file", "declared": {}}
                   for role, path in fixture["paths"].items()]
        sources.append({"source_id": "handoff_file", "from": str(folder / "identity-handoff.json"),
                        "as": "artifact", "input_origin": "user_file", "declared": {}})
        goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": text,
                "sources": sources, "declared_context": [],
                "targets": [{"id": "expectations", "role": "analysis", "required": True}],
                "constraints": [{"id": "present", "check": "check.goal.output_present@" + core_version(), "params": {},
                                 "target": "expectations", "source_quote": text, "status": "active"}], "intents": []}
        declared = command(folder, "goal", "declare", "--run", directory, "--request", write(request_path, goal))
        params = {"goal_digest": declared["result"]["goal_digest"],
                  **{role + "_source": role for role in ("original", "edited")},
                  "handoff_source": "handoff_file", "original_topology": "linear", "edited_topology": "linear",
                  "target": "expectations", "assay_id": "synthetic_identity", "forward_id": "forward", "reverse_id": "reverse"}
        instantiated = command(folder, "template", "instantiate", "genome-identity.from_handoff",
                               "--run", directory, "--request", write(request_path, params))
        command(folder, "pipeline", "submit", "--run", directory,
                "--request", write(request_path, instantiated["result"]["draft"]))
        executed = command(folder, "run", "execute", "--run", directory, expected=1 if name == "handoff_hash" else 0)
        if name == "handoff_hash":
            assert executed["state"] == "HALTED", executed
            assert executed["result"]["failure"]["code"] == "SOURCE_CHANGED", executed
            refused = command(folder, "seal", "--run", directory, expected=1)
            assert not (directory / "sealed").exists()
            summaries[name] = {"halted": True, "failure_code": "SOURCE_CHANGED", "seal_refused": bool(refused["problems"])}
            continue
        assert executed["state"] == "COMPLETED", executed
        sealed = command(folder, "seal", "--run", directory, expected=(0, 10))
        is_sealed = sealed["result"]["sealed"]
        package = Path(sealed["result"]["manifest"]).parent if is_sealed else directory / "candidate/1"
        table_path = package / "identity-expected-results.json"
        actual = json.loads(table_path.read_text(encoding="utf-8"))
        assert actual == fixture["expected"], actual
        oracle = check(fixture["paths"]["original"], fixture["paths"]["edited"],
                       fixture["paths"]["forward"], fixture["paths"]["reverse"], table_path,
                       handoff=folder / "identity-handoff.json")
        if not is_sealed:
            unknown = sealed["result"]["unsatisfied"]
            assert {row["check"] for row in unknown} == {
                "check.annotation_integrity", "check.cds_validity", "check.biological_sanity"}, unknown
            assert all(row["outcome"] == "UNKNOWN" for row in unknown)
            summaries[name] = {"sealed": False, "verified": False, "oracle": oracle,
                               "blocked_by_shared_checks": unknown,
                               "candidate": package.relative_to(output).as_posix()}
            continue
        command(folder, "verify", directory)
        portable = folder / "portable" / package.name
        shutil.copytree(package, portable)
        # Only the sealed directory is copied. Move the original run out of its recorded location.
        directory.rename(folder / "original-run-retained")
        verified = command(folder, "verify", portable)
        assert verified["result"]["verified"], verified
        manifest = json.loads((portable / "manifest.json").read_text(encoding="utf-8"))
        assert any("Annealing temperature" in row for row in manifest["not_verified"])
        assert any("Whole-genome specificity" in row for row in manifest["not_verified"])
        assert all(row["outcome"] in ("PASS", "NOT_APPLICABLE") for row in manifest["verdicts"])
        summaries[name] = {"portable_package": portable.relative_to(output).as_posix(),
                           "verified": True, "oracle": oracle,
                           "unverified": manifest["not_verified"], "release_id": manifest["release_id"]}
    summary = {"cases": summaries, "commands": len(receipts),
               "connection_attempts": sum(audit["attempts"] for audit in audits),
               "evidence_kind": "developer-assisted synthetic computational test",
               "official_gitlab_ci": "not executed", "github_ci": "not run", "laboratory_status": "NOT_PERFORMED"}
    write(output / "SUMMARY.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    result = run(parser.parse_args().out)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["cases"]["different_sizes"]["verified"] else 2)
