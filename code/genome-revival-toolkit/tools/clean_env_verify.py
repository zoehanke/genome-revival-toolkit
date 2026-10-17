"""Prepare or explicitly execute the separately authorized fresh-environment installation step."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import venv
import zipfile

from check_release import inspect_zip


def plan(archive, workdir):
    archive, workdir = Path(archive).resolve(), Path(workdir).resolve()
    python = workdir / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    source = workdir / "source"
    return {"status": "NOT_PERFORMED", "requires_user_authorization": True,
        "reason": "Task S4a requires separate user authorization for installation into a fresh environment.",
        "archive": str(archive), "workdir": str(workdir), "system_site_packages": False, "child_pythonpath": "removed",
        "commands": [[str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(source / "requirements-release.lock")],
                     [str(python), "-m", "pip", "install", "--disable-pip-version-check", "--no-build-isolation", "--no-deps", str(source)],
                     [str(python), "-X", "utf8", "-B", str(source / "examples/run_example.py"), "--out", str(workdir / "new-example"), "--python", str(python)],
                     [str(python), "-m", "dna_design_core.application.cli", "verify", "<each bundled examples/sealed/**/manifest.json parent>"]],
        "network": "Dependency installation can download locked packages; application examples run locally."}


def execute(archive, workdir):
    proposal = plan(archive, workdir)
    if Path(workdir).exists():
        raise ValueError("Use a new workdir; earlier failures and environments must be retained.")
    checked = inspect_zip(archive)
    if checked["status"] != "PASS":
        raise ValueError("Release archive validation failed: " + json.dumps(checked))
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True)
    source = workdir / "source"
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(source)
    # This path is entered only after the operator explicitly supplies --execute.
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(workdir / "venv")
    python = workdir / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    environment = dict(os.environ)
    for name in ("PYTHONPATH", "PYTHONHOME"):
        environment.pop(name, None)
    receipts = []
    def run(command):
        name = "command-" + str(len(receipts))
        with (workdir / (name + ".stdout.txt")).open("w", encoding="utf-8", newline="\n") as output, \
             (workdir / (name + ".stderr.txt")).open("w", encoding="utf-8", newline="\n") as errors:
            process = subprocess.run(command, cwd=workdir, env=environment, stdout=output, stderr=errors,
                                     text=True, encoding="utf-8", timeout=1800)
        receipts.append({"command": command, "exit_code": process.returncode, "stdout": name + ".stdout.txt", "stderr": name + ".stderr.txt"})
        result = {"status": "FAIL" if process.returncode else "RUNNING", "release": checked, "commands": receipts}
        (workdir / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
        if process.returncode:
            raise ValueError("Fresh-environment command failed; logs were retained.")
        return (workdir / (name + ".stdout.txt")).read_text(encoding="utf-8")
    for command in proposal["commands"][:2]:
        run(command)
    example = json.loads(run(proposal["commands"][2]))
    installed = json.loads(run([str(python), "-c", "import json, dna_design_core; print(json.dumps({'module':dna_design_core.__file__}))"]))
    if not Path(installed["module"]).resolve().is_relative_to(workdir / "venv"):
        raise ValueError("Imported package did not come from the fresh environment.")
    seals = sorted((source / "examples/sealed").rglob("manifest.json"))
    if not seals:
        raise ValueError("No bundled sealed example was supplied.")
    for manifest in seals:
        response = json.loads(run([str(python), "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", "verify", str(manifest.parent)]))
        if response["problems"] or not response["result"].get("verified"):
            raise ValueError("Bundled sealed example failed verification.")
    identity_matches = example.get("release_id") == checked["release_id"]
    result = {"status": "PASS" if identity_matches else "INCOMPLETE", "release": checked, "commands": receipts,
        "installed_package": installed["module"], "bundled_seals_verified": len(seals),
        "example_release_id": example.get("release_id"), "release_identity_matches": identity_matches,
        "scope": "Fresh installation, synthetic example and retained-record verification only. No human trial or wet experiment."}
    (workdir / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="Only after separate authorization; creates a fresh venv and can download dependencies.")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = execute(args.archive, args.workdir) if args.execute else plan(args.archive, args.workdir)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    if args.execute and result["status"] != "PASS":
        raise SystemExit(2)
