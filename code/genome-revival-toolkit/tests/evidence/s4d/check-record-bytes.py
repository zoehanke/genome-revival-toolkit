"""Independent D9 hashes and the known historical payload omissions; no Core imports."""
import hashlib
import json
from pathlib import Path
import rfc8785

ROOT = Path(__file__).resolve().parents[3]
rows = []
for label, base in (("current", "examples/sealed/b1"), ("legacy", "tests/evidence/s4d/legacy-b1")):
    package = next(p for p in (ROOT / base).iterdir() if p.is_dir())
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        assert hashlib.sha256((package / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    previous, missing, count = "0" * 64, [], 0
    for event in map(json.loads, (package / "journal-until-seal.ndjson").read_text(encoding="utf-8").splitlines()):
        assert event["prev"] == previous
        body = {key: value for key, value in event.items() if key != "hash"}
        calculated = hashlib.sha256(rfc8785.dumps(body) + event["prev"].encode("ascii")).hexdigest()
        assert event["hash"] == calculated, event["seq"]
        previous = calculated
        count += 1
        if event["type"] == "call.recorded":
            absent = [name for name in ("params", "params_digest") if name not in event["payload"]]
            if absent:
                missing.append({"seq": event["seq"], "missing": absent})
    assert previous == manifest["journal_head"]
    if label == "current":
        assert not missing
    else:
        assert missing == [{"seq": 9, "missing": ["params", "params_digest"]},
                           {"seq": 22, "missing": ["params", "params_digest"]}]
    rows.append({"case": label, "files_with_matching_hashes": len(manifest["files"]),
                 "events_with_matching_hashes": count, "missing_call_parameters": missing,
                 "method": "stdlib hashlib and public rfc8785; no Core or Kit imports"})
output = json.dumps(rows, indent=2) + "\n"
prior = Path(__file__).with_name("independent-record-check.json")
if prior.exists():
    assert prior.read_text(encoding="utf-8") == output, "Prior independent check differs; retain it and investigate."
else:
    prior.write_text(output, encoding="utf-8")
print(output)
