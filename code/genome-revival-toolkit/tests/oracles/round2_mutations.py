"""Four source mutations of the new common functions in disposable copies."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tests/evidence/s1b-round2/mutations"
MUTATIONS = (
    ("region_suffix", "sequence/preparation.py", 'value["sequence"][end:]', 'value["sequence"][end + 1:]',
     "test_region_edit_sequence_and_annotation_retirement"),
    ("cds_always_consistent", "sequence/preparation.py", '"complete_cds_consistent": None if partial or ambiguous else consistent',
     '"complete_cds_consistent": True', "test_cds_hand_translation_frame_and_partial_unknown"),
    ("primer_loses_tail", "primer/preparation.py", "full = tail + core", "full = core", "test_primer_candidates_core_tail_and_reverse_anchor"),
    ("read_off_by_one", "primer/preparation.py", 'site["end_unwrapped"] + trim,', 'site["end_unwrapped"] + trim - 1,',
     "test_coverage_first_usable_base_is_after_primer_plus_trim"),
)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for name, module, original, replacement, method in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="s1b_round2_mutation_") as temporary:
            root = Path(temporary)
            package = root / "dna_design_core"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            for dependency in ("biology", "kernel", "resources"):
                shutil.copytree(ROOT / "src/dna_design_core" / dependency, package / dependency,
                                ignore=shutil.ignore_patterns("__pycache__"))
            path = package / "biology" / module
            text = path.read_text(encoding="utf-8")
            if text.count(original) != 1:
                raise AssertionError("mutation target must be unique: " + name)
            path.write_text(text.replace(original, replacement, 1), encoding="utf-8", newline="\n")
            environment = dict(os.environ, PYTHONPATH=os.pathsep.join((str(root), str(ROOT / "tests/unit"))))
            test = "test_biology_round2_common.Round2CommonTests." + method
            process = subprocess.run([sys.executable, "-X", "utf8", "-B", "-m", "unittest", test], cwd=root,
                env=environment, capture_output=True, text=True, encoding="utf-8", timeout=30)
            output = process.stdout + process.stderr
            (OUTPUT / (name + ".txt")).write_text(output, encoding="utf-8", newline="\n")
            caught = process.returncode != 0 and "FAIL: " + method in output
            results.append({"id": name, "before": original, "after": replacement, "test": test,
                            "exit_code": process.returncode, "caught_by_assertion": caught, "output": name + ".txt"})
    (OUTPUT / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"mutations": len(results), "caught": sum(row["caught_by_assertion"] for row in results)}))
    raise SystemExit(0 if all(row["caught_by_assertion"] for row in results) else 1)
