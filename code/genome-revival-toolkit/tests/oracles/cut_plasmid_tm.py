"""Independent B2 nearest-neighbor arithmetic and explicit Primer3 CLI reference."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

# Allawi/SantaLucia 1997 DNA/DNA NN parameters (the published DNA_NN3 table).
# Each key and its reverse complement denote the same base-pair stack.
STACKS = {"AA": (-7.9, -22.2), "AT": (-7.2, -20.4), "TA": (-7.2, -21.3),
          "CA": (-8.5, -22.7), "GT": (-8.4, -22.4), "CT": (-7.8, -21.0),
          "GA": (-8.2, -22.2), "CG": (-10.6, -27.2), "GC": (-9.8, -24.4), "GG": (-8.0, -19.9)}


def hand_tm(sequence):
    enthalpy, entropy = 0.0, 0.0
    counts = {}
    for end in (sequence[0], sequence[-1]):
        dh, ds = (2.3, 4.1) if end in "AT" else (0.1, -2.8)
        enthalpy += dh
        entropy += ds
    for index in range(len(sequence) - 1):
        pair = sequence[index:index + 2]
        key = pair if pair in STACKS else pair.translate(str.maketrans("ACGT", "TGCA"))[::-1]
        dh, ds = STACKS[key]
        counts[key] = counts.get(key, 0) + 1
        enthalpy += dh
        entropy += ds
    corrected_entropy = entropy + 0.368 * (len(sequence) - 1) * math.log(0.05)
    tm = 1000 * enthalpy / (corrected_entropy + 1.987 * math.log(250e-9)) - 273.15
    return {"stack_counts": counts, "enthalpy_kcal_per_mol": format(enthalpy, ".8f"),
            "entropy_cal_per_K_mol": format(entropy, ".8f"), "tm_degC": format(tm, ".8f")}


def run_reference(primer_document, executable, output):
    output.mkdir(parents=True, exist_ok=True)
    primers = json.loads(primer_document.read_text(encoding="utf-8"))["primers"]
    about = subprocess.run([str(executable), "--about"], capture_output=True, text=True, timeout=15)
    assert about.returncode == 0, about.stderr
    version_text = about.stdout + about.stderr
    version = re.search(r"release\s+(\d+\.\d+\.\d+)", version_text)
    assert version, version_text
    rows = []
    for primer in primers:
        core, name = primer["binding_core"], primer["id"]
        arithmetic = hand_tm(core)
        tags = {"SEQUENCE_ID": "synthetic_B2_" + name, "SEQUENCE_PRIMER": core, "PRIMER_TASK": "check_primers",
                "PRIMER_PICK_ANYWAY": "1", "PRIMER_PICK_LEFT_PRIMER": "1", "PRIMER_PICK_RIGHT_PRIMER": "0",
                "PRIMER_MIN_SIZE": "2", "PRIMER_OPT_SIZE": str(len(core)), "PRIMER_MAX_SIZE": "36",
                "PRIMER_TM_FORMULA": "1", "PRIMER_SALT_CORRECTIONS": "1", "PRIMER_SALT_MONOVALENT": "50",
                "PRIMER_SALT_DIVALENT": "0", "PRIMER_DNTP_CONC": "0", "PRIMER_DNA_CONC": "1000",
                "PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT": "0"}
        request = "\n".join(key + "=" + value for key, value in tags.items()) + "\n=\n"
        process = subprocess.run([str(executable), "--strict_tags"], input=request, text=True, capture_output=True, timeout=30)
        (output / (name + ".request.txt")).write_text(request, encoding="utf-8", newline="\n")
        (output / (name + ".stdout.txt")).write_text(process.stdout, encoding="utf-8", newline="\n")
        (output / (name + ".stderr.txt")).write_text(process.stderr, encoding="utf-8", newline="\n")
        values = dict(line.split("=", 1) for line in process.stdout.splitlines() if "=" in line)
        assert process.returncode == 0 and "PRIMER_ERROR" not in values and "PRIMER_LEFT_0_TM" in values, values
        production, manual, reference = float(primer["tm_degC"]), float(arithmetic["tm_degC"]), float(values["PRIMER_LEFT_0_TM"])
        # Set before running: eight-decimal NN output, three-decimal Primer3 output.
        manual_pass = abs(production - manual) <= 0.00000001
        backend_pass = abs(production - reference) <= 0.0006
        rows.append({"id": name, "core_length": len(core), "production_tm_degC": primer["tm_degC"], "independent_arithmetic": arithmetic,
                     "primer3_tm_degC": values["PRIMER_LEFT_0_TM"], "manual_agreement": manual_pass,
                     "primer3_agreement": backend_pass, "primer3_difference_degC": format(production - reference, ".8f")})
    result = {"outcome": "PASS" if all(row["manual_agreement"] and row["primer3_agreement"] for row in rows) else "FAIL",
              "backend": {"version": version.group(1), "sha256": hashlib.sha256(executable.read_bytes()).hexdigest(), "about": version_text.strip()},
              "parameters": {"effective_strand_concentration_nM": "250", "primer3_total_oligo_nM": "1000", "sodium_mM": "50"},
              "predeclared_tolerances_degC": {"manual": "0.00000001", "primer3": "0.0006"}, "cases": rows}
    (output / "reference.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primers", type=Path, required=True)
    parser.add_argument("--primer3", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    result = run_reference(arguments.primers, arguments.primer3, arguments.out)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["outcome"] == "PASS" else 1)
