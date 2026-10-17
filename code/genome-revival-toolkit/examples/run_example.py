"""Run the fixed B1 answer through the public CLI; installed mode never adds source paths."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(output, python, source_tree=False):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError("Choose a new output directory; previous evidence is retained.")
    output.mkdir(parents=True)
    environment = dict(os.environ)
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    if source_tree:
        environment["PYTHONPATH"] = str(ROOT / "src")
    receipts = []
    def command(*arguments):
        process = subprocess.run([str(python), "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", *map(str, arguments)],
            cwd=output, env=environment, capture_output=True, text=True, encoding="utf-8")
        index = len(receipts)
        (output / (str(index) + ".stdout.txt")).write_text(process.stdout, encoding="utf-8", newline="\n")
        (output / (str(index) + ".stderr.txt")).write_text(process.stderr, encoding="utf-8", newline="\n")
        receipt = json.loads(process.stdout)
        receipts.append({"command": list(map(str, arguments)), "exit_code": process.returncode, "receipt": receipt})
        (output / "receipts.json").write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8", newline="\n")
        if process.returncode or receipt["problems"]:
            raise ValueError("Example command failed; retained receipt index " + str(index))
        return receipt["result"]
    def request(name, value):
        path = output / name
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
        return path
    version = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))["core"]
    run_root = output / "run"
    created = command("run", "create", run_root)
    goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": "Report the reverse complement of AGTCAGAA.",
        "sources": [], "declared_context": [], "targets": [{"id": "t1", "role": "analysis", "required": True}],
        "constraints": [{"id": "c1", "check": "check.goal.output_present@" + version, "params": {"fields": ["sequence"]},
            "target": "t1", "source_quote": "Report the reverse complement", "status": "active"}], "intents": []}
    declared = command("goal", "declare", "--run", run_root, "--request", request("goal.json", goal))
    plan = {"schema": "pipeline-v1", "version": 1, "goal_digest": declared["goal_digest"], "steps": [
        {"step_id": "reverse", "use": "seq.reverse_complement", "inputs": {"sequence": {"literal": "AGTCAGAA"}}, "params": {},
         "why": "Reverse and complement a synthetic eight-base literal.",
         "expects": {"on": {"step": "reverse", "port": "result", "pointer": "/sequence"}, "op": "equals", "value": "TTCTGACT"}}],
        "outputs": [{"name": "result", "from": {"step": "reverse", "port": "result"}, "target": "t1"}]}
    command("pipeline", "submit", "--run", run_root, "--request", request("pipeline.json", plan))
    command("run", "execute", "--run", run_root)
    judged = command("judge", "--run", run_root)
    if judged["unsatisfied"]:
        raise AssertionError(judged)
    sealed = command("seal", "--run", run_root)
    package = Path(sealed["manifest"]).parent
    if json.loads((package / "result.json").read_text(encoding="utf-8")) != {"sequence": "TTCTGACT"}:
        raise AssertionError("The independent hand answer is TTCTGACT.")
    portable = output / "portable" / package.name
    shutil.copytree(package, portable)
    # Make the original location unavailable; verify must use the portable package.
    retained = output / "run-retained"
    if not run_root.is_relative_to(output) or not retained.is_relative_to(output):
        raise ValueError("Example paths must remain within their new output directory.")
    run_root.rename(retained)
    verified = command("verify", portable)
    if not verified["verified"]:
        raise AssertionError(verified)
    result = {"expected": {"sequence": "TTCTGACT"}, "verified": True, "portable_package": portable.relative_to(output).as_posix(),
        "release_id": created["release_id"], "execution": "source tree" if source_tree else "installed package",
        "scope": "Synthetic reverse-complement calculation and portable sealed-record verification; no Kit or laboratory result."}
    (output / "SUMMARY.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--source-tree", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.out, args.python, args.source_tree), indent=2))
