"""Execute every marked tutorial command verbatim, retaining successes and failures."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs/developers/add-a-kit.md"
BLOCK = re.compile(r"<!-- copyable: ([a-z0-9-]+) -->\s*```powershell\n(.*?)\n```", re.DOTALL)
ORDER = ["01-copy", "02-manifest", "03-action", "04-rule", "05-template",
         "06-check", "07-describe", "08-lifecycle", "09-checks", "10-review"]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def inventory(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob("*") if path.is_file()}


def run_tutorial(output, tours=False):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    guide = GUIDE.read_text(encoding="utf-8")
    blocks = BLOCK.findall(guide)
    assert [name for name, _ in blocks] == ORDER, "Tutorial command order changed."
    assert len(re.findall(r"```powershell\n", guide)) == len(blocks), "Unmarked PowerShell command."
    write(output / "commands.json", [{"step": name, "powershell": code} for name, code in blocks])
    script = ["try {"]
    for name, code in blocks:
        script.extend(["Write-Output 'STEP_BEGIN=" + name + "'", code,
                       "Write-Output 'STEP_END=" + name + "'"])
    script.extend(["} catch {", "    Write-Error $_ -ErrorAction Continue", "    exit 1", "}"])
    script_path = output / "tutorial.ps1"
    script_path.write_text("\n".join(script) + "\n", encoding="utf-8", newline="\n")
    shell = shutil.which("pwsh")
    if shell is None:
        raise RuntimeError("PowerShell 7 is required; no download or installation is attempted.")
    print("Executing the ten tutorial blocks; evidence: " + str(output), flush=True)
    process = subprocess.run([shell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(script_path)],
                             cwd=ROOT, text=True, capture_output=True, encoding="utf-8", timeout=240)
    (output / "powershell.stdout.txt").write_text(process.stdout, encoding="utf-8", newline="\n")
    (output / "powershell.stderr.txt").write_text(process.stderr, encoding="utf-8", newline="\n")
    workspace_match = re.search(r"^WORK_DIRECTORY=(.+)$", process.stdout, re.MULTILINE)
    workspace = Path(workspace_match.group(1).strip()) if workspace_match else None
    write(output / "execution.json", {"exit_code": process.returncode,
                                      "workspace": str(workspace) if workspace else None})
    assert process.returncode == 0, "Tutorial failed; inspect retained powershell.stderr.txt and workspace receipts."
    assert re.findall(r"^STEP_END=(.+)$", process.stdout, re.MULTILINE) == ORDER
    result = read(workspace / "walkthrough-result.json")
    receipts = read(workspace / "receipts.json")
    write(output / "receipts.json", receipts)
    write(output / "default-discovery.json", read(workspace / "default-discovery.json"))
    assert result["count"] == 4 and result["minimum"] == 3 and result["verified"]
    assert result["not_rerun"] == []
    kit, portable, tampered, retained = (Path(result[key]) for key in ("kit", "portable", "tampered", "retained_run"))
    assert not (workspace / "run").exists(), "Original run remained available."
    assert not kit.is_relative_to(ROOT / "kits")
    assert read(kit / "kit.json")["name"] == "phrase-counter"
    assert read(kit / "capabilities/count_words.json")["owner"] == "kit:phrase-counter"
    for module in ("count.py", "check.py"):
        assert (kit / "capabilities" / module).read_text(encoding="utf-8").strip() == (
            ROOT / "examples/kit-template/capabilities" / module).read_text(encoding="utf-8").strip()
    assert read(portable / "phrase-counter.json") == {
        "text": "red green blue gold", "word_count": 4, "minimum_words": 3,
        "meets_minimum": True, "rule_id": "phrase_counter.minimum_words"}
    original_package = retained / "sealed" / portable.name
    good, bad = inventory(portable), inventory(tampered)
    assert good == inventory(original_package), "Portable verify modified its package."
    assert good.keys() == bad.keys()
    assert [key for key in good if good[key] != bad[key]] == ["phrase-counter.json"]
    assert len(good["phrase-counter.json"]) == len(bad["phrase-counter.json"])
    assert sum(a != b for a, b in zip(good["phrase-counter.json"], bad["phrase-counter.json"])) == 1
    assert not any(path.parent.name == "review" for path in kit.rglob("*.json"))
    events = [json.loads(line) for line in (retained / "journal.ndjson").read_text(encoding="utf-8").splitlines()]
    verdicts = [event["payload"]["verdict"] for event in events if event["type"] == "verdict.issued"]
    own = [v for v in verdicts if v["check"]["id"] == "phrase_counter.check_count"]
    assert {(v["moment"], v["issuer"], v["outcome"]) for v in own} == {
        ("step", "tool_self_report", "PASS"), ("final", "check_capability", "PASS")}
    manifest = read(portable / "manifest.json")
    assert "phrase_counter.check_count" in {row["check"] for row in manifest["verdicts"]}
    failures = [row for row in receipts if row["exit_code"]]
    assert len(failures) == 2
    assert failures[0]["arguments"] == ["verify", str(tampered)]
    assert failures[0]["receipt"]["result"].get("verified") is not True
    assert failures[0]["receipt"]["problems"][0]["code"] == "STORE_CORRUPT"
    assert failures[1]["arguments"][:2] == ["review", "sign"]
    assert failures[1]["receipt"]["problems"][0]["code"] == "CHECK_UNAVAILABLE"
    portable_receipt = next(row for row in receipts if row["arguments"] == ["verify", str(portable)])
    assert portable_receipt["receipt"]["result"]["not_rerun"] == []
    summary = {"copyable_blocks_executed": ORDER, "cli_commands": len(receipts),
               "constructed_answer": {"word_count": 4, "minimum_words": 3, "meets_minimum": True},
               "portable_verified": True, "portable_unchanged": True, "not_rerun": [],
               "tamper_bytes_changed": 1, "tamper_detected": True,
               "check_moments": ["step", "final"], "human_review": "NOT_PERFORMED",
               "workspace": str(workspace), "portable_package": str(portable),
               "scope": "Source-tree tutorial and synthetic non-DNA example; no new-developer timing trial.",
               "official_gitlab_ci": "not executed", "github_ci": "not run"}
    write(output / "SUMMARY.json", summary)
    if tours:
        environment = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
        summary["tours"] = {}
        for name, runner in [("cut-plasmid", "run_cut_plasmid.py"), ("revival-evidence", "run_revival_evidence.py")]:
            destination = output / "tours" / name
            destination.parent.mkdir(exist_ok=True)
            tour = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tests/e2e" / runner),
                                   "--out", str(destination)], cwd=ROOT, env=environment,
                                  text=True, capture_output=True, encoding="utf-8", timeout=900)
            (output / (name + ".stdout.txt")).write_text(tour.stdout, encoding="utf-8", newline="\n")
            (output / (name + ".stderr.txt")).write_text(tour.stderr, encoding="utf-8", newline="\n")
            assert tour.returncode == 0, "Real-Kit tour failed; see retained " + name + " output."
            summary["tours"][name] = read(destination / "SUMMARY.json")
    write(output / "SUMMARY.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tours", action="store_true", help="Also run both existing synthetic real-Kit CLI runners.")
    arguments = parser.parse_args()
    print(json.dumps(run_tutorial(arguments.out, arguments.tours), ensure_ascii=False, indent=2))
