"""Four actual source mutations in disposable copies; never modify worktree code."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tests/evidence/s1b/mutations"
MUTATIONS = (
    ("pcr_ambiguity", "pcr/prediction.py", "if len(products) != 1:", "if not products:",
     "test_biology_primer_pcr.PCRTests.test_repeated_sites_enumerated_and_unique_simulator_rejects"),
    ("overhang_labels", "assembly/simulation.py",
     'first["overhang"] == str(Seq(second["overhang"]).reverse_complement())',
     'first["overhang"] == second["overhang"]',
     "test_biology_restriction_assembly.AssemblyTests.test_actual_extensions_must_be_reverse_complements"),
    ("nn_salt_term", "primer/thermodynamics.py", "saltcorr=5,", "saltcorr=0,",
     "test_biology_primer_pcr.PrimerTests.test_tm_hand_sum_non_self_complementary"),
    ("feature_start", "sequence/operations.py", "lo - seg_left + offset, hi - seg_left + offset",
     "lo - seg_left + offset + 1, hi - seg_left + offset",
     "test_biology_sequence_formats.SequenceTests.test_feature_mapping_hand_forward_reverse_and_partial_cds"),
)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, module, original, replacement, test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="s1b_mutation_") as temporary:
            root = Path(temporary).resolve()
            package = root / "dna_design_core"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            target = package / "biology"
            shutil.copytree(ROOT / "src/dna_design_core/biology", target, ignore=shutil.ignore_patterns("__pycache__"))
            for dependency in ("kernel", "resources"):
                shutil.copytree(ROOT / "src/dna_design_core" / dependency, package / dependency,
                                ignore=shutil.ignore_patterns("__pycache__"))
            source = target / module
            text = source.read_text(encoding="utf-8")
            if text.count(original) != 1:
                raise AssertionError("mutation must replace exactly one expression: " + name)
            source.write_text(text.replace(original, replacement, 1), encoding="utf-8", newline="\n")
            environment = dict(os.environ)
            environment["PYTHONPATH"] = os.pathsep.join((str(root), str(ROOT / "tests/unit")))
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-m", "unittest", test],
                                     env=environment, cwd=root, text=True, capture_output=True,
                                     encoding="utf-8", timeout=30)
            output = process.stdout + process.stderr
            (OUTPUT / (name + ".txt")).write_text(output, encoding="utf-8", newline="\n")
            caught = process.returncode != 0 and "FAIL: " + test.rsplit(".", 1)[1] in output
            results.append({"id": name, "module": module, "before": original, "after": replacement,
                            "test": test, "exit_code": process.returncode, "caught_by_assertion": caught,
                            "output": name + ".txt"})
    (OUTPUT / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mutations": len(results), "caught": sum(result["caught_by_assertion"] for result in results)}))
    raise SystemExit(0 if all(result["caught_by_assertion"] for result in results) else 1)
