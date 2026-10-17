"""Run the existing synthetic Kit cases using only a genuinely installed Core.

Launch with the NEW environment's Python from outside the source directory.
Scientific expectations and independent checkers are reused unchanged.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def run(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    import dna_design_core
    package = Path(dna_design_core.__file__).resolve().parent
    if not package.is_relative_to(Path(sys.prefix).resolve()):
        raise AssertionError("Core was not imported from this environment.")
    if sys.prefix == sys.base_prefix:
        raise AssertionError("A new virtual environment is required.")
    # The installed payload carries the same test helpers as the selected source ZIP.
    from dna_design_core.tests.s4b_support import Commands, isolated_env
    log = Commands(output / "construct-commands", [(package, "<INSTALLED>"), (output, "<OUTPUT>")])
    environment = isolated_env()
    manifest_bytes = (package / "release-manifest.json").read_bytes()
    expected_release = hashlib.sha256(manifest_bytes).hexdigest()
    results = {"module": str(dna_design_core.__file__), "python": sys.executable,
               "module_inside_new_environment": True, "manifest_sha256": expected_release,
               "kits": {}, "laboratory": "PLANNED / NOT_PERFORMED"}

    def save():
        (output / "RESULTS.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    save()
    cut = importlib.import_module("dna_design_core.tests.e2e.run_cut_plasmid")
    results["kits"]["cut-plasmid"] = cut.run_b2(output / "cut-plasmid")
    if not results["kits"]["cut-plasmid"]["seal_created"]:
        raise AssertionError("Cut Plasmid did not seal.")
    save()

    construction = importlib.import_module("dna_design_core.tests.construct_runtime")
    oracle = importlib.import_module("dna_design_core.tests.oracles.construct_verify")
    construct = {}
    for method in ("gibson", "pcr"):
        folder = output / "construct" / method
        folder.mkdir(parents=True)

        def dispatch(verb, *, root, request=None, kit_dirs=(), **options):
            if kit_dirs:
                raise AssertionError("Only bundled installed Kits are allowed in this check.")
            command = [sys.executable, "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", *verb.split()]
            if verb == "run create":
                command.append(str(options["directory"]))
            elif verb == "template instantiate":
                command.append(options["name"])
            elif verb == "verify":
                command.append(str(options.get("directory", root)))
            if verb != "verify":
                command += ["--run", str(root)]
            if request is not None:
                path = folder / ("request-" + str(len(log.rows)) + ".json")
                path.write_text(json.dumps(request), encoding="utf-8")
                command += ["--request", str(path)]
            process = log.run(command, cwd=folder, env=environment, timeout=300)
            receipt = json.loads(process.stdout)
            if process.returncode or receipt["problems"]:
                raise AssertionError(receipt)
            return receipt

        service, _, execution = construction.create(folder, method, dispatch=dispatch)
        if execution["state"] != "COMPLETED":
            raise AssertionError(execution)
        independent = oracle.verify_run(service.root)
        if not independent["passed"]:
            raise AssertionError(independent)
        dispatch("judge", root=service.root)
        sealed = dispatch("seal", root=service.root)
        dispatch("verify", root=service.root)
        original = Path(sealed["result"]["manifest"]).parent
        portable = folder / "portable" / original.name
        shutil.copytree(original, portable)
        retained = folder / "original-run-retained"
        if not service.root.resolve().is_relative_to(output) or not retained.resolve().is_relative_to(output):
            raise ValueError("Original-run move must stay inside the new example directory.")
        service.root.rename(retained)
        verified = dispatch("verify", root=portable)
        if not verified["result"]["verified"]:
            raise AssertionError(verified)
        construct[method] = {"sealed": True, "portable_verified": True, "independent": independent,
                             "package": str(portable)}
        (folder / "independent.json").write_text(json.dumps(independent, indent=2) + "\n", encoding="utf-8")
    results["kits"]["construct"] = construct
    save()
    identity = importlib.import_module("dna_design_core.tests.e2e.run_genome_identity")
    results["kits"]["genome-identity"] = identity.run(output / "genome-identity")
    if not results["kits"]["genome-identity"]["cases"]["different_sizes"]["verified"]:
        raise AssertionError("Genome Identity did not seal and verify.")
    save()
    evidence = importlib.import_module("dna_design_core.tests.e2e.run_revival_evidence")
    results["kits"]["revival-evidence"] = evidence.run_examples(output / "revival-evidence")
    save()
    seals = list(output.glob("**/portable/*/manifest.json"))
    if len(seals) != 9:
        # One Cut Plasmid, two Construct, one Identity, five Evidence example packages.
        raise AssertionError({"expected_synthetic_seals": 9, "actual": len(seals)})
    for manifest in seals:
        if json.loads(manifest.read_text(encoding="utf-8"))["release_id"] != expected_release:
            raise AssertionError("An example did not record the installed manifest digest.")
    results["portable_seals"] = len(seals)
    results["status"] = "PASS"
    save()
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    result = run(parser.parse_args().out)
    print(json.dumps({"status": result["status"], "portable_seals": result["portable_seals"],
                      "manifest_sha256": result["manifest_sha256"], "module_inside_new_environment": True}))
