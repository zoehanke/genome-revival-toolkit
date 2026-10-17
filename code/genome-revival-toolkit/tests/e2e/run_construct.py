"""Retained public CLI executions; blocked acceptance is never counted as sealed."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tests.construct_runtime import create
from tests.oracles.construct_verify import verify_run


def run(directory):
    directory = Path(directory)
    if directory.exists():
        raise ValueError("Choose a new evidence directory; previous failures are retained.")
    directory.mkdir(parents=True)
    commands, results = [], {}

    def dispatch(verb, *, root, request=None, kit_dirs=(), **options):
        argv = [sys.executable, "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", *verb.split()]
        if verb == "run create":
            argv.append(str(options["directory"]))
        elif verb == "template instantiate":
            argv.append(options["name"])
        elif verb == "verify":
            argv.append(str(options.get("directory", root)))
        argv.extend(["--run", str(root)])
        for path in kit_dirs:
            argv.extend(["--kit-dir", str(path)])
        if request is not None:
            path = directory / ("request-" + str(len(commands)).zfill(3) + ".json")
            path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            argv.extend(["--request", str(path)])
        process = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", check=False)
        commands.append({"verb": verb, "argv": argv[1:], "exit_code": process.returncode,
                         "stdout": process.stdout, "stderr": process.stderr})
        (directory / "commands.json").write_text(json.dumps(commands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        return json.loads(process.stdout)

    for method in ("gibson", "pcr"):
        service, _, execution = create(directory / method, method, dispatch=dispatch)
        if execution["problems"]:
            raise AssertionError(execution)
        oracle = verify_run(service.root)
        if not oracle["passed"]:
            raise AssertionError(oracle)
        (directory / (method + "-independent.json")).write_text(json.dumps(oracle, indent=2) + "\n", encoding="utf-8", newline="\n")
        judged = dispatch("judge", root=service.root)
        sealed = dispatch("seal", root=service.root)
        verified = dispatch("verify", root=service.root)
        rendered = dispatch("record render", root=service.root)
        results[method] = {"execution": execution, "oracle": oracle, "judge": judged, "seal": sealed,
                           "verify": verified, "render": rendered, "copied_sealed_package_verify": "NOT_PERFORMED: no sealed package exists"}
    # Separate output-binding diagnostic, with every construct-role obligation retained.
    service, _, execution = create(directory / "diagnostic", "pcr", outputs="diagnostic", dispatch=dispatch)
    results["diagnostic"] = {"execution": execution, "judge": dispatch("judge", root=service.root), "seal": dispatch("seal", root=service.root)}
    (directory / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    results = run(args.directory)
    print(json.dumps({name: {"executed": value["execution"]["state"],
                            "seal_problems": value["seal"]["problems"],
                            "sealed": value["seal"]["result"].get("sealed", False)} for name, value in results.items()}, ensure_ascii=False))
