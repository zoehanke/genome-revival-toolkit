"""Retain the historical B1 bytes and rebuild its replacement through public CLI."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env


def run(work):
    work = Path(work).resolve()
    work.mkdir(parents=True, exist_ok=False)
    evidence = ROOT / "tests/evidence/s4d"
    log = Commands(evidence / "rebuild", [(ROOT, "<SOURCE>"), (work, "<WORK>")])
    env = isolated_env()
    env["PYTHONPATH"] = str(ROOT / "src")
    old_root = ROOT / "examples/sealed/b1"
    old = next(path for path in old_root.iterdir() if path.is_dir())
    target = evidence / "legacy-b1" / old.name
    shutil.copytree(old, target)
    rows = []
    for path in sorted(old.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        committed = subprocess.check_output(["git", "-C", str(ROOT), "show", "e5e153a:code/genome-revival-toolkit/" + relative])
        copied = (target / path.relative_to(old)).read_bytes()
        if path.read_bytes() != committed or copied != committed:
            raise AssertionError("Historical bytes differ: " + relative)
        rows.append({"path": path.relative_to(old).as_posix(), "sha256": hashlib.sha256(committed).hexdigest(),
                     "bytes": len(committed), "same_as_s4b": True})
    (evidence / "legacy-byte-comparison.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    before = log.run([sys.executable, "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", "verify", str(target)],
                     cwd=work, env=env)
    receipt = json.loads(before.stdout)
    if before.returncode != 1 or receipt["problems"][0]["code"] != "JOURNAL_CHAIN_BROKEN":
        raise AssertionError("Expected old-format incompatibility was not reproduced.")
    result = log.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "examples/run_example.py"),
                      "--source-tree", "--out", str(work / "current")], cwd=work, env=env)
    if result.returncode:
        raise AssertionError("Current source example failed; retained original package and command evidence.")
    summary = json.loads((work / "current/SUMMARY.json").read_text(encoding="utf-8"))
    current = work / "current" / summary["portable_package"]
    manifest = json.loads((current / "manifest.json").read_text(encoding="utf-8"))
    if manifest["release_id"] != "dev-tree" or json.loads((current / "result.json").read_text(encoding="utf-8")) != {"sequence": "TTCTGACT"}:
        raise AssertionError("The hand-calculated example answer or development identity differs.")
    # Remove only the original package after its byte-for-byte backup is checked.
    if old.resolve().parent != old_root.resolve() or not target.resolve().is_relative_to(evidence.resolve()):
        raise ValueError("Historical example move would leave its intended folders.")
    shutil.rmtree(old)
    shutil.copytree(current, old_root / current.name)
    (old_root / ".gitattributes").write_text("# Sealed records retain their original bytes.\n* -text whitespace=cr-at-eol\n", encoding="utf-8")
    (evidence / "rebuild/RESULTS.json").write_text(json.dumps({
        "historical_files_unchanged": len(rows), "historical_negative": "JOURNAL_CHAIN_BROKEN",
        "current_package": "examples/sealed/b1/" + current.name,
        "release_id": manifest["release_id"], "expected": {"sequence": "TTCTGACT"},
        "source_verified": True, "original_run_moved_away": True}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run(sys.argv[1])
