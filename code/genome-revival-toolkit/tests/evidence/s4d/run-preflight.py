"""S4d focused public checks; expected refusals remain nonzero in retained logs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env

work = Path(sys.argv[1]).resolve()
work.mkdir(parents=True, exist_ok=False)
repository = ROOT.parents[1]
evidence = ROOT / "tests/evidence/s4d/preflight"
log = Commands(evidence, [(ROOT, "<SOURCE>"), (repository, "<REPOSITORY>"), (work, "<WORK>")])
env = isolated_env()
env["PYTHONPATH"] = str(ROOT / "src")
commands = [
    (0, ["tools/check_structure.py"]),
    (0, ["tools/check_schemas.py"]),
    (0, ["tools/docgen.py", "--check"]),
    (0, [str(ROOT / "tools/spec_lint.py"), str(repository / "spec/SPEC.md"), "--fields-report", str(evidence / "spec-fields.json")]),
    (0, ["-m", "unittest", "tests.integration.test_release_identity", "-v"]),
    (2, ["tools/check_release.py", "--report", str(evidence / "release-check.json")]),
    (1, ["tools/build_release.py", "--out", str(work / "must-not-exist")]),
    (0, ["tests/oracles/prepare_cut_plasmid.py", "--help"]),
    (2, ["tests/oracles/prepare_cut_plasmid.py"]),
]
for expected, command in commands:
    result = log.run([sys.executable, "-X", "utf8", "-B", *command], cwd=ROOT, env=env)
    print(log.safe(result.stdout + result.stderr), flush=True)
    if result.returncode != expected:
        raise AssertionError("Unexpected exit code; preserve the failure and investigate.")
report = json.loads((evidence / "release-check.json").read_text(encoding="utf-8"))
assert report["findings"] == [] and report["placeholder_files"] == {"README.md": 3}, report
assert not (work / "must-not-exist").exists()
(evidence / "RESULTS.json").write_text(json.dumps({"release_status": report["status"],
    "findings": report["findings"], "readme_human_markers": 3, "zip_created": False,
    "focused_tests": 7, "developer_helper_requires_explicit_local_repository": True}, indent=2) + "\n", encoding="utf-8")
