"""Compare source commit, checkout, wheel and installation with standard-library SHA-256."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", type=Path, required=True)
parser.add_argument("--work", type=Path, required=True)
parser.add_argument("--evidence", type=Path, required=True)
args = parser.parse_args()
root, work = args.source.resolve(), args.work.resolve()
package = work / "venv/Lib/site-packages/dna_design_core"
wheel = next((work / "wheels-02").glob("*.whl"))
data = (package / "release-manifest.json").read_bytes()
manifest = json.loads(data)
origins = ["VERSIONS.json" if row["path"] == "src/dna_design_core/resources/VERSIONS.json" else row["path"] for row in manifest["files"]]
requests = "".join(manifest["build_id"] + ":code/genome-revival-toolkit/" + name + "\n" for name in origins)
raw = subprocess.run(["git", "cat-file", "--batch"], cwd=root, input=requests.encode("utf-8"), capture_output=True, check=True).stdout
position, blobs = 0, []
for name in origins:
    end = raw.index(b"\n", position)
    header = raw[position:end].split()
    if len(header) != 3 or header[1] != b"blob":
        raise AssertionError("Source commit lacks " + name)
    size = int(header[2])
    blobs.append(raw[end + 1:end + 1 + size])
    position = end + size + 2
rows = []
sha = lambda content: hashlib.sha256(content).hexdigest()
with zipfile.ZipFile(wheel) as archive:
    if archive.read("dna_design_core/release-manifest.json") != data:
        raise AssertionError("Installed manifest differs from wheel.")
    for row, origin, blob in zip(manifest["files"], origins, blobs):
        name = row["path"].removeprefix("src/dna_design_core/")
        item = {**row, "source": origin, "source_commit_sha256": sha(blob),
                "commit_matches": sha(blob) == row["sha256"],
                "checkout_matches": sha((root / origin).read_bytes()) == row["sha256"],
                "wheel_matches": sha(archive.read("dna_design_core/" + name)) == row["sha256"],
                "installed_matches": sha((package / name).read_bytes()) == row["sha256"]}
        rows.append(item)
        if not all(item[key] for key in ("commit_matches", "checkout_matches", "wheel_matches", "installed_matches")):
            raise AssertionError(item)
result = {"build_id": manifest["build_id"], "manifest_sha256": sha(data),
          "wheel_sha256": sha(wheel.read_bytes()), "files_checked": len(rows),
          "all_match": True, "generated_resource_comes_from": "VERSIONS.json", "files": rows}
args.evidence.mkdir(parents=True, exist_ok=True)
(args.evidence / "source-wheel-manifest.json").write_bytes(data)
(args.evidence / "source-installed-comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "files"}))
