"""One-byte corruption of the new test installation, followed by exact restoration."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import dna_design_core
from dna_design_core.tests.s4b_support import Commands, isolated_env

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--evidence", type=Path, required=True)
args = parser.parse_args()
work = args.work.resolve()
package = Path(dna_design_core.__file__).resolve().parent
if not package.is_relative_to(Path(sys.prefix).resolve()) or sys.prefix == sys.base_prefix:
    raise AssertionError("Only the newly installed test environment may be changed.")
log = Commands(args.evidence, [(work, "<WORK>"), (package, "<INSTALLED>")])
manifest = package / "release-manifest.json"
data = manifest.read_bytes()
offset = data.index(b'"build_id":"') + len(b'"build_id":"')
corrupt = data[:offset] + (b"0" if data[offset:offset + 1] != b"0" else b"1") + data[offset + 1:]
assert sum(a != b for a, b in zip(data, corrupt)) == 1 and len(data) == len(corrupt)
portable = next((work / "cases-01/cut-plasmid/portable").glob("*/manifest.json")).parent
cli = [sys.executable, "-X", "utf8", "-B", "-m", "dna_design_core.application.cli"]
before = {p.relative_to(portable).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in portable.rglob("*") if p.is_file()}
try:
    manifest.write_bytes(corrupt)
    for command in ([*cli, "run", "create", str(work / "manifest-corrupt-run")], [*cli, "verify", str(portable)]):
        process = log.run(command, cwd=work, env=isolated_env())
        receipt = json.loads(process.stdout)
        assert process.returncode == 1 and receipt["problems"][0]["code"] == "SOURCE_CHANGED", receipt
        assert "manifest" in receipt["problems"][0]["message"].lower()
    assert not (work / "manifest-corrupt-run/run.json").exists()
finally:
    manifest.write_bytes(data)
assert manifest.read_bytes() == data
process = log.run([*cli, "verify", str(portable)], cwd=work, env=isolated_env())
receipt = json.loads(process.stdout)
assert process.returncode == 0 and receipt["result"]["verified"], receipt
after = {p.relative_to(portable).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in portable.rglob("*") if p.is_file()}
assert after == before
result = {"changed_bytes": 1, "byte_offset": offset, "create_refused": True, "verify_refused": True,
          "original_manifest_sha256": hashlib.sha256(data).hexdigest(),
          "modified_manifest_sha256": hashlib.sha256(corrupt).hexdigest(),
          "manifest_restored_exactly": True, "verify_after_restoration": True,
          "sealed_files_unchanged": len(before), "development_fallback": False}
(args.evidence / "RESULTS.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
