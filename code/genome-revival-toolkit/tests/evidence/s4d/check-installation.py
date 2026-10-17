"""Build offline, then exercise actual newly installed B1 and identity boundaries."""
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env

work = Path(sys.argv[1]).resolve()
python = work / "venv/Scripts/python.exe"
evidence = ROOT / "tests/evidence/s4d/installed"
log = Commands(evidence, [(ROOT, "<SOURCE>"), (work, "<WORK>")])
env = isolated_env()


def checked(arguments, *, code=0, environment=env):
    result = log.run(arguments, cwd=work, env=environment)
    if result.returncode != code:
        raise AssertionError(log.safe(result.stdout + result.stderr))
    return result


checked([str(python), "-X", "utf8", "-B", "-m", "pip", "--isolated", "wheel", "--disable-pip-version-check",
         "--no-deps", "--no-build-isolation", "--no-index", "--wheel-dir", str(work / "wheels-02"), str(ROOT)])
wheel = next((work / "wheels-02").glob("*.whl"))
checked([str(python), "-X", "utf8", "-B", "-m", "pip", "--isolated", "install", "--disable-pip-version-check",
         "--no-deps", "--no-index", "--report", str(work / "product-install.json"), str(wheel)])
program = ("import json,sys,pathlib,dna_design_core; from dna_design_core.kernel.release import release_id; "
           "p=pathlib.Path(dna_design_core.__file__).resolve().parent; "
           "assert p.is_relative_to(pathlib.Path(sys.prefix).resolve()); assert sys.prefix!=sys.base_prefix; "
           "print(json.dumps({'package':str(p),'prefix':sys.prefix,'release_id':release_id()}))")
identity = json.loads(checked([str(python), "-I", "-X", "utf8", "-B", "-c", program]).stdout)
package = Path(identity["package"])
log.roots.append((package, "<INSTALLED>"))
assert len(identity["release_id"]) == 64
summary = {"module_inside_new_venv": True, "system_site_packages": False,
           "installed_release_id": identity["release_id"], "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
           "cases": []}
source_env = isolated_env()
source_env["PYTHONPATH"] = str(ROOT / "src")


def verify(path, *, installed=True, expected=None):
    executable = python if installed else Path(sys.executable)
    flags = ["-I"] if installed else []
    command = [str(executable), *flags, "-X", "utf8", "-B", "-m", "dna_design_core.application.cli", "verify", str(path)]
    result = checked(command, code=1 if expected else 0, environment=env if installed else source_env)
    receipt = json.loads(result.stdout)
    if expected:
        assert receipt["problems"][0]["code"] == expected, receipt
    else:
        assert receipt["result"]["verified"], receipt
    summary["cases"].append({"path": log.safe(str(path)), "environment": "new installation" if installed else "source",
                             "expected_error": expected, "exit_code": result.returncode,
                             "verified": receipt["result"].get("verified", False)})


bundled = next(p for p in (package / "examples/sealed/b1").iterdir() if p.is_dir())
source_bundled = ROOT / "examples/sealed/b1" / bundled.name
assert json.loads((bundled / "result.json").read_text(encoding="utf-8")) == {"sequence": "TTCTGACT"}
manifest = json.loads((bundled / "manifest.json").read_text(encoding="utf-8"))
assert manifest["release_id"] == "dev-tree"
label = "This development-tree package is not release evidence."
assert label in manifest["not_verified"]
for name in ("views/runcard.html", "views/report.md"):
    assert label in (bundled / name).read_text(encoding="utf-8")
verify(bundled)
verify(source_bundled, installed=False)
portable = work / "portable-b1" / bundled.name
shutil.copytree(bundled, portable)
verify(portable)
verify(portable, installed=False)

corrupt = work / "one-byte-corruption" / bundled.name
shutil.copytree(bundled, corrupt)
result_file = corrupt / "result.json"
data = result_file.read_bytes()
changed = data.replace(b"TTCTGACT", b"ATCTGACT", 1)
assert len(data) == len(changed) and sum(a != b for a, b in zip(data, changed)) == 1
result_file.write_bytes(changed)
verify(corrupt, expected="STORE_CORRUPT")
verify(corrupt, installed=False, expected="STORE_CORRUPT")
legacy = next(p for p in (ROOT / "tests/evidence/s4d/legacy-b1").iterdir() if p.is_dir())
verify(legacy, expected="JOURNAL_CHAIN_BROKEN")
verify(legacy, installed=False, expected="JOURNAL_CHAIN_BROKEN")

# A new release-bound example comes from this actual installation, not a forged seal.
checked([str(python), "-I", "-X", "utf8", "-B", str(package / "examples/run_example.py"),
         "--python", str(python), "--out", str(work / "release-bound-example")])
example_summary = json.loads((work / "release-bound-example/SUMMARY.json").read_text(encoding="utf-8"))
bound = work / "release-bound-example" / example_summary["portable_package"]
assert example_summary["release_id"] == identity["release_id"]
verify(bound)
verify(bound, installed=False)

# Change only the build identifier of an otherwise intact private installation,
# with its RECORD checksum updated: a second valid, different release manifest.
# Restore both original files exactly, even on failure.
release_manifest = package / "release-manifest.json"
record = next(package.parent.glob("genome_revival_toolkit-*.dist-info/RECORD"))
original_manifest, original_record = release_manifest.read_bytes(), record.read_bytes()
value = json.loads(original_manifest)
old_build = value["build_id"].encode("ascii")
new_build = ("0" * len(value["build_id"])).encode("ascii")
assert old_build != new_build and original_manifest.count(old_build) == 1
other_manifest = original_manifest.replace(old_build, new_build, 1)
try:
    release_manifest.write_bytes(other_manifest)
    rows = list(csv.reader(io.StringIO(original_record.decode("utf-8"))))
    updated = 0
    for row in rows:
        if row[0] == "dna_design_core/release-manifest.json":
            row[1] = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(other_manifest).digest()).decode().rstrip("=")
            row[2] = str(len(other_manifest))
            updated += 1
    assert updated == 1
    stream = io.StringIO(newline="")
    csv.writer(stream).writerows(rows)
    record.write_bytes(stream.getvalue().encode("utf-8"))
    other = json.loads(checked([str(python), "-I", "-X", "utf8", "-B", "-c", program]).stdout)
    assert other["release_id"] == hashlib.sha256(other_manifest).hexdigest() != identity["release_id"]
    verify(bound, expected="SOURCE_CHANGED")
    verify(portable)
    summary["different_valid_release_id"] = other["release_id"]
finally:
    release_manifest.write_bytes(original_manifest)
    record.write_bytes(original_record)
verify(bound)
assert release_manifest.read_bytes() == original_manifest and record.read_bytes() == original_record
summary.update({"installation_restored_byte_for_byte": True, "hand_answer": {"sequence": "TTCTGACT"},
                "builtin_release_id": manifest["release_id"], "card_and_markdown_disclose_non_release_evidence": True,
                "no_wet_lab_work": True, "official_gitlab_ci": "NOT_RUN", "github_ci": "NOT_RUN"})
(evidence / "RESULTS.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
