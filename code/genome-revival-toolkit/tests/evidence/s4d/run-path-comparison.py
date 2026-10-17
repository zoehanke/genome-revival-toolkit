"""Compare legacy authoring output in disposable copies; never regenerate live Kits."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tests.s4b_support import Commands, isolated_env

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--legacy-repo", type=Path, required=True)
parser.add_argument("--work", type=Path, required=True)
args = parser.parse_args()
work = args.work.resolve()
work.mkdir(parents=True, exist_ok=False)
evidence = ROOT / "tests/evidence/s4d/paths"
log = Commands(evidence, [(ROOT, "<SOURCE>"), (work, "<WORK>"), (args.legacy_repo.resolve(), "<LEGACY_SOURCE>")])
env = isolated_env()
env["PYTHONPATH"] = str(ROOT / "src")
for label in ("before", "after"):
    target = work / label
    shutil.copytree(ROOT / "kits/cut-plasmid", target / "kits/cut-plasmid")
    program = target / "tests/oracles/prepare_cut_plasmid.py"
    program.parent.mkdir(parents=True)
    if label == "before":
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", "e5e153a:code/genome-revival-toolkit/tests/oracles/prepare_cut_plasmid.py"])
        program.write_bytes(old)
        arguments = []
    else:
        shutil.copyfile(ROOT / "tests/oracles/prepare_cut_plasmid.py", program)
        arguments = ["--legacy-repo", str(args.legacy_repo)]
    result = log.run([sys.executable, "-X", "utf8", "-B", str(program), *arguments], cwd=target, env=env)
    if result.returncode:
        raise AssertionError("Historical authoring comparison failed; retained the output.")
def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and p.relative_to(root).as_posix() != "tests/oracles/prepare_cut_plasmid.py"}
before, after = inventory(work / "before"), inventory(work / "after")
assert set(before) == set(after)
rows = [{"path": name, "before_sha256": before[name], "after_sha256": after[name], "same": before[name] == after[name]}
        for name in sorted(before)]
(evidence / "file-comparison.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
assert all(row["same"] for row in rows)

# Historical software inventories identify earlier commits, not the S4d tree.
# Prove those referenced bytes and their actual inventory records remain intact.
path_file = ROOT / "tests/evidence/s4d/path-reference-check.json"
references = json.loads(path_file.read_text(encoding="utf-8"))
for row in references:
    checks = []
    for name in row["hash_references"]:
        data = (ROOT / name).read_bytes()
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", "e5e153a:code/genome-revival-toolkit/" + name])
        value = json.loads(data)
        content = subprocess.check_output(["git", "-C", str(ROOT), "show", value["build_id"] + ":code/genome-revival-toolkit/" + row["path"]])
        checks.append({"inventory": name, "source_commit": value["build_id"],
                       "inventory_unchanged": data == old,
                       "referenced_commit_bytes_unchanged": hashlib.sha256(content).hexdigest() == row["old_file_sha256"]})
    assert all(item["inventory_unchanged"] and item["referenced_commit_bytes_unchanged"] for item in checks)
    row["reference_checks"] = checks
path_file.write_text(json.dumps(references, indent=2) + "\n", encoding="utf-8")
summary = {"authoring_files_compared": len(rows), "all_byte_identical": True,
           "live_kit_generated_files_changed": False, "historical_inventory_bytes_and_commits_preserved": True}
(evidence / "RESULTS.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
