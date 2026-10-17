"""Retain command output and artifact hashes; omit bulky duplicate sealed bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--evidence", type=Path, required=True)
args = parser.parse_args()
source, work = args.source.resolve(), args.work.resolve()
sys.path.insert(0, str(source))
from tests.s4b_support import Commands

log = Commands(args.evidence, [(source, "<SOURCE>"), (work, "<WORK>")])
files, retained = [], []
for name in ("cases-01", "b1"):
    for path in sorted((work / name).rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(work)
        data = path.read_bytes()
        files.append({"path": relative.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        # Original-run and sealed internals remain in the private artifact directory.
        if any(part in {"run", "retained-run", "original-run-retained", "run-retained", "portable"} for part in relative.parts):
            continue
        if path.suffix not in {".json", ".txt"}:
            continue
        destination = args.evidence / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(log.safe(data.decode("utf-8")), encoding="utf-8", newline="\n")
        retained.append(relative.as_posix())
(args.evidence / "artifacts.json").write_text(json.dumps({"path_base": "<PRIVATE_NEW_ENVIRONMENT_WORKDIR>",
    "full_artifacts_retained": True, "files": files, "command_and_summary_files_copied": retained}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"artifacts_hashed": len(files), "command_and_summary_files_copied": len(retained)}))
