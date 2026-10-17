"""Retained manual code mutations. Only private copies are changed, never the checkout."""
import argparse
import json
from pathlib import Path
import shutil
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--evidence", type=Path, required=True)
args = parser.parse_args()
source, work = args.source.resolve(), args.work.resolve()
sys.path.insert(0, str(source))
from tests.s4b_support import Commands, isolated_env

work.mkdir(parents=True, exist_ok=False)
log = Commands(args.evidence, [(source, "<SOURCE>"), (work, "<MUTANTS>")])
results = []
mutations = [
    ("create_reverts_to_dev_tree", "application/run_service.py", "        release=release_id()", "        release='dev-tree'",
     "test_package_records_manifest_digest_and_detects_one_byte_change"),
    ("verify_ignores_different_release", "application/run_service.py", "if installed_release!='dev-tree' and manifest['release_id']!=installed_release:", "if False:",
     "test_installed_seal_verifies_portably_but_different_release_is_rejected"),
    ("source_metadata_is_mistaken_for_installation", "kernel/release.py",
     "    if (source / 'pyproject.toml').is_file() and (source / 'src/dna_design_core').resolve() == package:", "    if False:",
     "test_source_build_metadata_is_not_an_installed_release"),
]
for name, module, before, after, test in mutations:
    root = work / name
    shutil.copytree(source / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(source / "VERSIONS.json", root / "VERSIONS.json")
    path = root / "src/dna_design_core" / module
    data = path.read_text(encoding="utf-8")
    assert data.count(before) == 1
    path.write_text(data.replace(before, after, 1), encoding="utf-8")
    program = ("import sys,unittest; sys.path.insert(0,sys.argv[1]); "
               "from tests.integration import test_release_identity as t; from pathlib import Path; "
               "t.ROOT=Path(sys.argv[2]); "
               "r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.ReleaseIdentityTests(sys.argv[3])])); "
               "sys.exit(not r.wasSuccessful())")
    process = log.run([sys.executable, "-X", "utf8", "-B", "-c", program, str(source), str(root), test],
                      cwd=work, env=isolated_env(), timeout=120)
    killed = process.returncode != 0 and "AssertionError" in process.stderr and "FAILED (failures=1)" in process.stderr
    results.append({"mutation": name, "changed_from": before, "changed_to": after,
                    "test": test, "exit_code": process.returncode, "mutation_detected": killed})
    if not killed:
        raise AssertionError("Mutation was not demonstrably detected. Retained output for diagnosis.")
(log.directory / "RESULTS.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2))
