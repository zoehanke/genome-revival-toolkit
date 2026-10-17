"""Normalize actual machine paths in retained text; leave canonical manifests unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--private-work", type=Path, required=True)
parser.add_argument("--primer3-dir", type=Path, required=True)
args = parser.parse_args()
source = args.source.resolve()
sys.path.insert(0, str(source))
from tests.s4b_support import Commands

folder = source / "tests/evidence/s4b"
mask = Commands(folder / "path-normalization", [(source, "<SOURCE>"), (source.parents[1], "<REPOSITORY>"),
    (args.private_work.resolve(), "<PRIVATE_WORK>"), (args.primer3_dir.resolve(), "<PRIMER3>")])
manifests = {path: path.read_bytes() for path in folder.glob("**/source-wheel-manifest.json")}
changed, findings = [], []
pattern = re.compile(r"(?i)[A-Z]:[\\/]+(?:Users|codex_project)[\\/]+")
for path in sorted(folder.rglob("*")):
    if not path.is_file() or path.suffix not in {".json", ".txt", ".md", ".py"}:
        continue
    text = path.read_text(encoding="utf-8")
    normalized = mask.safe(text)
    if normalized != text:
        path.write_text(normalized, encoding="utf-8", newline="\n")
        changed.append(path.relative_to(folder).as_posix())
    if pattern.search(normalized):
        findings.append(path.relative_to(folder).as_posix())
for path, data in manifests.items():
    if path.read_bytes() != data:
        raise AssertionError("Canonical manifest bytes must not be changed.")
result = {"changed_text_files": changed, "remaining_machine_path_candidates": findings,
          "canonical_manifests_unchanged": {p.relative_to(folder).as_posix(): hashlib.sha256(data).hexdigest()
                                            for p, data in manifests.items()},
          "normalization": "Path spelling only, including repeated JSON/repr escapes; outcomes are not rewritten."}
(folder / "path-normalization/RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"text_files_normalized": len(changed), "remaining_candidates": findings}))
if findings:
    raise SystemExit(1)
