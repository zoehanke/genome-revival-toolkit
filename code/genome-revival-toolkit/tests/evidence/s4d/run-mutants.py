"""Two deliberate identity-rule mutations, only in new private source copies."""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env

work = Path(sys.argv[1]).resolve()
work.mkdir(parents=True, exist_ok=False)
log = Commands(ROOT / "tests/evidence/s4d/mutants", [(ROOT, "<SOURCE>"), (work, "<MUTANTS>")])
condition = "if manifest['release_id']!='dev-tree' and installed_release!='dev-tree' and manifest['release_id']!=installed_release:"
mutations = [
    ("rejects_development_seal", "if installed_release!='dev-tree' and manifest['release_id']!=installed_release:",
     "test_development_seal_verifies_in_an_installed_release"),
    ("ignores_release_mismatch", "if False:",
     "test_installed_seal_verifies_portably_but_different_release_is_rejected"),
]
rows = []
for name, replacement, test in mutations:
    root = work / name
    shutil.copytree(ROOT / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (root / "examples").mkdir()
    shutil.copyfile(ROOT / "examples/run_example.py", root / "examples/run_example.py")
    for filename in ("VERSIONS.json", "pyproject.toml"):
        shutil.copyfile(ROOT / filename, root / filename)
    module = root / "src/dna_design_core/application/run_service.py"
    text = module.read_text(encoding="utf-8")
    assert text.count(condition) == 1
    module.write_text(text.replace(condition, replacement, 1), encoding="utf-8")
    program = ("import sys,unittest; sys.path.insert(0,sys.argv[1]); "
               "from tests.integration import test_release_identity as t; from pathlib import Path; "
               "t.ROOT=Path(sys.argv[2]); "
               "r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([t.ReleaseIdentityTests(sys.argv[3])])); "
               "sys.exit(not r.wasSuccessful())")
    result = log.run([sys.executable, "-X", "utf8", "-B", "-c", program, str(ROOT), str(root), test],
                     cwd=work, env=isolated_env(), timeout=180)
    caught = result.returncode == 1 and "FAILED (failures=1)" in result.stderr and "AssertionError" in result.stderr
    rows.append({"mutation": name, "from": condition, "to": replacement, "test": test,
                 "exit_code": result.returncode, "mutation_detected": caught})
    if not caught:
        raise AssertionError("Mutation was not detected; retained output for investigation.")
(log.directory / "RESULTS.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
print(json.dumps(rows, indent=2))
