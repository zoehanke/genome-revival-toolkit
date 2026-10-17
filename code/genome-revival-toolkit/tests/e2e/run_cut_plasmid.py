"""B2 via public CLI: failure, declared revision, preparation, real final judgement."""
import argparse
from copy import deepcopy
from importlib.util import find_spec
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from cut_plasmid_runtime import b2, write_material
from dna_design_core.kernel.public import material_id
from e2e.independent_check import check_output

CLI = Path(find_spec("dna_design_core.application.cli").origin)
GUARD = ROOT / "tests/e2e/network_guard.py"


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def run_b2(output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Choose a new output directory; previous evidence is retained.")
    output.mkdir(parents=True)
    case, receipts, connections = b2(), [], []
    run = output / "run"
    write(output / "construction.json", case)
    write_material(output / "vector.gb", case["vector"])
    write_material(output / "target.gb", case["target"])

    def command(*arguments, expected=0):
        number = len(receipts) + 1
        audit = output / ("network-" + str(number) + ".json")
        process = subprocess.run([sys.executable, "-X", "utf8", "-B", str(GUARD), str(audit), str(CLI), *map(str, arguments)],
                                 cwd=output, capture_output=True, text=True, encoding="utf-8", timeout=180)
        (output / ("command-" + str(number) + ".stdout.json")).write_text(process.stdout, encoding="utf-8")
        (output / ("command-" + str(number) + ".stderr.txt")).write_text(process.stderr, encoding="utf-8")
        receipt = json.loads(process.stdout)
        receipts.append({"arguments": list(map(str, arguments)), "exit_code": process.returncode, "receipt": receipt})
        write(output / "receipts.json", receipts)
        attempts = json.loads(audit.read_text(encoding="utf-8"))["attempts"]
        connections.append(attempts)
        assert attempts == 0, (arguments, attempts)
        if expected is not None:
            assert process.returncode == expected, (arguments, process.returncode, receipt)
        return receipt

    described = command("describe", "checks")
    versions = {row["id"]: row["version"] for row in described["result"]["description"]}
    command("run", "create", run)
    original = "Replace only the spacer; return complete primers and report selection status."
    goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": original,
            "sources": [{"source_id": name, "from": str(output / (name + ".gb")), "as": "artifact",
                         "input_origin": "user_file", "declared": {}} for name in ("vector", "target")],
            "declared_context": [], "targets": [{"id": "t1", "role": "construct", "required": True},
                {"id": "t2", "role": "primer_set", "required": True}, {"id": "t3", "role": "analysis", "required": True}],
            "constraints": [
                {"id": "k1", "check": "check.goal.components_present@" + versions["check.goal.components_present"],
                 "params": {"components": [{"name": "selected spacer", "sequence": case["spacer"]}]},
                 "target": "t1", "source_quote": "Replace only the spacer", "status": "active"},
                {"id": "k2", "check": "check.goal.regions_unchanged@" + versions["check.goal.regions_unchanged"],
                 "params": {"reference_material_id": material_id(case["vector"]),
                            "regions": [{"source_start": left, "source_end": right, "target_start": left, "target_end": right}
                                        for left, right in ((0, 130), (150, 360))]},
                 "target": "t1", "source_quote": "Replace only the spacer", "status": "active"},
                {"id": "k3", "check": "check.goal.claim_reported@" + versions["check.goal.claim_reported"],
                 "params": {"claim": "selection", "pointer": ""}, "target": "t3",
                 "source_quote": "report selection status", "status": "active"}], "intents": []}
    declared = command("goal", "declare", "--run", run, "--request", write(output / "goal-request.json", goal))
    params = case["params"]
    readers = [{"step_id": "read_" + name, "use": "format.read_genbank", "inputs": {"file": {"source": name}},
                "params": {"strandedness": "double"}, "why": "Read the registered synthetic GenBank source."} for name in ("vector", "target")]
    sources = {name: {"step": "read_" + name, "port": "material"} for name in ("vector", "target")}
    first = {"step_id": "s1", "use": "cut_plasmid.inspect_guide", "inputs": sources, "params": params,
             "why": "Inspect the user-supplied spacer before any replacement.",
             "expects": {"on": {"step": "s1", "port": "guide", "pointer": "/pam_valid"}, "op": "equals", "value": True}}
    plan = {"schema": "pipeline-v1", "version": 1, "goal_digest": declared["result"]["goal_digest"], "steps": readers + [first], "outputs": []}
    admitted = command("pipeline", "submit", "--run", run, "--request", write(output / "initial-plan.json", plan))
    events = [json.loads(line) for line in (run / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
    assert not any(event["type"] in ("step.started", "call.recorded") for event in events)
    initial = command("run", "execute", "--run", run, expected=1)
    assert initial["state"] == "HALTED"
    events = [json.loads(line) for line in (run / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
    failed = next(event for event in events if event["type"] == "step.failed")
    assert failed["payload"]["failure"]["code"] == "STEP_EXPECTATION_FAILED"
    reason = "The initial spacer was shifted by one base; use target [13,33) followed by AGG."
    command("declare", "--run", run, "--request", write(output / "declaration.json", {"text": reason, "origin": "plan_declared"}))
    additions = [
        {"step_id": "s2", "use": "cut_plasmid.replace_spacer", "inputs": sources, "params": {**params, "spacer": case["spacer"]},
         "why": "Replace only the selected spacer and simulate inverse PCR plus closure."},
        {"step_id": "s3", "use": "cut_plasmid.inspect_guide", "inputs": {"vector": {"step": "s2", "port": "product"}, "target": sources["target"]},
         "params": params, "why": "Reinspect actual output sequence and its target PAM.",
         "expects": {"on": {"step": "s3", "port": "guide", "pointer": "/pam_valid"}, "op": "equals", "value": True}},
        {"step_id": "s4", "use": "cut_plasmid.assess_selection", "inputs": {"vector": {"step": "s2", "port": "product"}}, "params": {},
         "why": "Report selection UNKNOWN because recipient genotype was not supplied."},
        {"step_id": "export", "use": "format.write_genbank", "inputs": {"material": {"step": "s2", "port": "product"}},
         "params": {"name": "construct.gb"}, "why": "Export an annotated synthetic GenBank candidate."},
        {"step_id": "readback", "use": "format.read_genbank", "inputs": {"file": {"step": "export", "port": "file"}},
         "params": {}, "why": "Read back the actual exported GenBank bytes."}]
    bindings = [{"name": "construct", "from": {"step": "s2", "port": "product"}, "target": "t1"},
                {"name": "primers", "from": {"step": "s2", "port": "primers"}, "target": "t2"},
                {"name": "selection", "from": {"step": "s4", "port": "selection"}, "target": "t3"}]
    operations, previous = [], "s1"
    for step in additions:
        operations.append({"op": "add_step", "after": previous, "step": step})
        previous = step["step_id"]
    operations.extend([{"op": "supersede_step", "step_id": "s1", "by": "s2"}, {"op": "set_outputs", "outputs": bindings}])
    revision = {"schema": "pipeline-revision-v1", "expected_digest": admitted["result"]["pipeline_digest"],
                "trigger": {"kind": "step_failed", "step_id": "s1", "failure_code": "STEP_EXPECTATION_FAILED", "event_refs": [failed["hash"]]},
                "reason": reason, "operations": operations}
    command("pipeline", "revise", "--run", run, "--request", write(output / "revision.json", revision))
    command("run", "execute", "--run", run)
    events = [json.loads(line) for line in (run / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
    assert failed in events
    assert len([event for event in events if event["type"] == "goal.declared"]) == 1
    assert not any(event["type"] == "goal.amended" for event in events)
    actual_products = {event["payload"]["step_id"]: event["payload"]["outputs"]["materials"] for event in events if event["type"] == "step.completed"}
    assert actual_products["s2"]["product"] == actual_products["readback"]["material"]
    judgement = command("judge", "--run", run)
    candidate = max((run / "candidate").iterdir(), key=lambda path: int(path.name))
    independent = check_output(run, candidate)
    write(output / "independent.json", independent)
    assert json.loads((candidate / "selection.json").read_text(encoding="utf-8"))["status"] == "UNKNOWN"
    sealed = command("seal", "--run", run, expected=None)
    command("record", "render", "--run", run)
    portable_verified = False
    if sealed["result"].get("sealed"):
        package = Path(sealed["result"]["manifest"]).parent
        command("verify", run)
        copied = output / "portable" / package.name
        copied.parent.mkdir()
        shutil.copytree(package, copied)
        retained_run = output / "original-run-retained"
        assert run.resolve().is_relative_to(output) and retained_run.resolve().is_relative_to(output)
        run.rename(retained_run)
        candidate = retained_run / "candidate" / candidate.name
        run = retained_run
        portable_verified = command("verify", copied)["result"]["verified"]
    else:
        assert receipts[-2]["exit_code"] == 10, sealed
        command("verify", run, expected=1)
    summary = {"acceptance_passed": portable_verified, "initial_step_failed": True, "revision_before_replacement": True,
               "original_goal_preserved": True, "independent_sequence_and_pcr": independent["outcome"], "genbank_readback_equal": True,
               "selection_status": "UNKNOWN", "seal_created": bool(sealed["result"].get("sealed")),
               "portable_verify_performed": portable_verified, "unsatisfied": judgement["result"]["unsatisfied"],
               "connection_attempts": sum(connections), "commands": len(receipts),
               "run": str(run), "candidate": str(candidate), "official_gitlab_ci": "not executed", "github_ci": "not run",
               "laboratory": "PLANNED / NOT_PERFORMED"}
    write(output / "SUMMARY.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run_b2(arguments.out), ensure_ascii=False, indent=2))
