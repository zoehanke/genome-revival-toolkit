"""Retain one full developer suite without overwriting earlier committed evidence."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env


def run(work, primer3, evidence):
    work = Path(work).resolve()
    work.mkdir(parents=True, exist_ok=False)
    evidence = Path(evidence)
    if evidence.exists():
        raise ValueError("Use a new evidence directory; earlier suite failures are retained.")
    log = Commands(evidence, [(ROOT, "<SOURCE>"), (work, "<FULL_WORK>"), (primer3.parent, "<PRIMER3>")])
    original = {name: (ROOT / name).read_bytes() for name in (
        "tests/evidence/s1b-c2/check-fixtures.json", "tests/evidence/s1b-c2/public-api.json",
        "tests/evidence/s4a/public-commands.json", "tests/evidence/s1b/integration/primer3-runtime.json")}
    old = set((ROOT / "tests/evidence/s2").glob("b2-suite-*"))
    env = isolated_env()
    env["PYTHONPATH"] = str(ROOT / "src")
    env["GRT_PRIMER3_CORE"] = str(primer3)
    try:
        result = log.run([sys.executable, "-X", "utf8", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                         cwd=ROOT, env=env, timeout=7200)
        text = result.stdout + result.stderr
        count = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", text)
        summary = {"exit_code": result.returncode, "tests": int(count[1]) if count else None,
                   "seconds": float(count[2]) if count else None,
                   "registered_skips": re.findall(r"^(.+?) \.\.\. skipped (.+)$", text, re.M),
                   "primer3": "existing local executable; not downloaded"}
        (evidence / "RESULTS.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary), flush=True)
        return result.returncode
    finally:
        for name, data in original.items():
            path = ROOT / name
            if path.read_bytes() != data:
                archive = evidence / "generated" / name.removeprefix("tests/evidence/")
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_text(log.safe(path.read_text(encoding="utf-8")), encoding="utf-8")
                path.write_bytes(data)
        for path in set((ROOT / "tests/evidence/s2").glob("b2-suite-*")) - old:
            destination = work / path.name
            if not path.resolve().is_relative_to(ROOT / "tests/evidence/s2") or not destination.resolve().is_relative_to(work):
                raise ValueError("Generated evidence move would leave the selected folders.")
            shutil.move(str(path), str(destination))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--primer3", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, default=ROOT / "tests/evidence/s4b/full")
    args = parser.parse_args()
    raise SystemExit(run(args.work, args.primer3, args.evidence))
