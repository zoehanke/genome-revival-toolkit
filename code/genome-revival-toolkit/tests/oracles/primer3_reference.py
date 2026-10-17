"""Independent Primer3 CLI experiment, deliberately no dna_design_core import.

This developer oracle is not a runtime capability or a substitute run_external.
All sequences are synthetic. Output preserves each exact request and response.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def run_reference(executable: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    if not executable.is_file():
        result = {"outcome": "UNKNOWN", "reason": "Primer3 executable missing",
                  "recovery": "Configure GRT_PRIMER3_CORE with a local primer3_core executable; do not install automatically.",
                  "cases": []}
        (output / "reference.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result
    about = subprocess.run([str(executable), "--about"], capture_output=True, text=True,
                           timeout=15, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    version_output = about.stdout + about.stderr
    version = re.search(r"release\s+(\d+\.\d+\.\d+)", version_output)
    if about.returncode or version is None:
        raise RuntimeError("Primer3 version probe failed: " + version_output)
    data_path = executable.parent / "primer3_config"
    specifications = [
        ("hand_8nt", "ACGTACGA", None, "0", "0"),
        ("symmetry_8nt", "ACGTACGT", None, "0", "0"),
        ("ordinary_20nt", "ACGTCGATGCTAGCTACGTA", None, "0", "0"),
        ("magnesium_20nt", "ACGTCGATGCTAGCTACGTA", None, "2", "0.5"),
        ("hairpin_20nt", "GCGAAACGCTATACGAGCTT", None, "0", "0"),
        ("polyT_20nt", "ACGTTTTTTTTAGCTACGTA", None, "0", "0"),
        ("pair_20nt", "ACGTCGATGCTAGCTACGTA", "TAGGCTACGATTCGACGTCA", "0", "0"),
    ]
    cases = []
    for name, sequence, partner, magnesium, dntp in specifications:
        # Request constructed here without using production encoder/builder.
        tags = {
            "SEQUENCE_ID": name, "PRIMER_TASK": "check_primers", "PRIMER_PICK_ANYWAY": "1",
            "SEQUENCE_PRIMER": sequence, "PRIMER_PICK_LEFT_PRIMER": "1",
            "PRIMER_PICK_RIGHT_PRIMER": "0" if partner is None else "1",
            "PRIMER_MIN_SIZE": "2", "PRIMER_OPT_SIZE": str(len(sequence)), "PRIMER_MAX_SIZE": str(max(len(sequence), len(partner or ""))),
            "PRIMER_TM_FORMULA": "1", "PRIMER_SALT_CORRECTIONS": "1",
            "PRIMER_SALT_MONOVALENT": "50", "PRIMER_SALT_DIVALENT": magnesium,
            "PRIMER_DNTP_CONC": dntp, "PRIMER_DNA_CONC": "50",
            "PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT": "1", "PRIMER_SECONDARY_STRUCTURE_ALIGNMENT": "1",
            "PRIMER_THERMODYNAMIC_PARAMETERS_PATH": str(data_path) + "/", "PRIMER_EXPLAIN_FLAG": "1",
        }
        if partner is not None:
            tags["SEQUENCE_PRIMER_REVCOMP"] = partner
        request = "\n".join(key + "=" + value for key, value in tags.items()) + "\n=\n"
        process = subprocess.run([str(executable), "--strict_tags"], input=request,
                                 text=True, capture_output=True, timeout=30,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        (output / (name + ".request.txt")).write_text(request, encoding="utf-8", newline="\n")
        (output / (name + ".stdout.txt")).write_text(process.stdout, encoding="utf-8", newline="\n")
        (output / (name + ".stderr.txt")).write_text(process.stderr, encoding="utf-8", newline="\n")
        raw = dict(line.split("=", 1) for line in process.stdout.splitlines() if "=" in line and line != "=")
        if process.returncode or "PRIMER_ERROR" in raw or "PRIMER_LEFT_0_TM" not in raw:
            raise RuntimeError(f"Primer3 case {name} failed: {process.stdout}\n{process.stderr}")
        measurements = {key: value for key, value in raw.items() if key.startswith(("PRIMER_LEFT_0_", "PRIMER_RIGHT_0_", "PRIMER_PAIR_0_"))}
        cases.append({"id": name, "sequence": sequence, "partner": partner,
                      "parameters": {"sodium_mM": "50", "magnesium_mM": magnesium, "dntp_mM": dntp, "total_oligo_nM": "50"},
                      "measurements": measurements, "exit_code": process.returncode,
                      "request": name + ".request.txt", "stdout": name + ".stdout.txt", "stderr": name + ".stderr.txt"})
    result = {"outcome": "PASS", "version": version.group(1), "version_output": version_output.strip(),
              "executable": str(executable), "sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
              "thermodynamic_files": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                       for path in sorted(data_path.iterdir()) if path.is_file()},
              "command": [str(executable), "--strict_tags"], "timeout_s": 30, "cases": cases}
    (output / "reference.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    result = run_reference(arguments.executable, arguments.output)
    print(json.dumps({"outcome": result["outcome"], "case_count": len(result["cases"]),
                      "version": result.get("version"), "sha256": result.get("sha256")}))
