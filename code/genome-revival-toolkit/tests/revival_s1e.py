"""Synthetic Evidence fixtures and a public-CLI test driver, outside the Kit.

Reference geometry is literal: one forward site and zero, one or two reverse
sites. The 80/131 bp expectations are fixed before any Toolkit invocation.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORWARD = "ACGTCGATGCTAGTACCGTA"
REVERSE_SITE = "TGATCCTGTACGCTAGGTCA"


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def fixture(folder, *, count=1, result="negative", band=None, controls=None, tolerance=5):
    if count == 0:
        reference = "C" * 80
    else:
        reference = FORWARD + "C" * 40 + REVERSE_SITE
        if count == 2:
            reference += "C" * 31 + REVERSE_SITE
    assert len(FORWARD) == len(REVERSE_SITE) == 20
    # Independent exact windows, used only to check the predetermined geometry.
    sites = [i + 20 for i in range(len(reference) - 19) if reference[i:i+20] == REVERSE_SITE]
    assert sites == {0: [], 1: [80], 2: [80, 131]}[count]
    assert [i for i in range(len(reference) - 19) if reference[i:i+20] == FORWARD] == ([] if count == 0 else [0])
    file = folder / "synthetic-reference.fasta"
    file.write_text(">synthetic_reference\n" + reference + "\n", encoding="utf-8", newline="\n")
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    predictions = {"schema": "identity-expected-results-v1", "assay_id": "local_assay", "backgrounds": [
        {"id": "reference", "reference_sha256": digest, "primer_pair": ["forward", "reverse"],
         "expected": {"product_count": count, "product_bp": 80 if count == 1 else None,
                      "status": "UNDETERMINED" if count == 2 else "DISTINGUISHABLE"}}]}
    row = {"sample_id": "synthetic_sample", "assay_id": "local_assay", "background_id": "reference",
           "reference_sha256": digest, "result": result, "band_tolerance_bp": tolerance}
    if band != "omitted":
        row["observed_band_bp"] = band
    if controls is not None:
        row["control_status"] = controls
    observations = {"observations": [], "genotype_results": [row],
                    "observation_origin": "SYNTHETIC_NOT_EXPERIMENTAL"}
    return write(folder / "observations.json", observations), write(folder / "predictions.json", predictions)


class EvidenceRun:
    def __init__(self, folder):
        self.folder = Path(folder).resolve()
        self.folder.mkdir(parents=True, exist_ok=False)
        self.root = self.folder / "run"
        self.receipts = []

    def command(self, *arguments, request=None, expected=0):
        index = len(self.receipts)
        if request is not None:
            arguments = (*arguments, "--request", write(self.folder / f"request-{index}.json", request))
        audit = self.folder / f"network-{index}.json"
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tests/e2e/network_guard.py"),
            str(audit), str(ROOT / "src/dna_design_core/application/cli.py"), *map(str, arguments)],
            cwd=self.folder, capture_output=True, text=True, encoding="utf-8", check=False)
        (self.folder / f"command-{index}.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (self.folder / f"command-{index}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        value = json.loads(result.stdout)
        row = {"arguments": list(map(str, arguments)), "exit_code": result.returncode, "receipt": value,
               "network": json.loads(audit.read_text(encoding="utf-8"))}
        self.receipts.append(row)
        write(self.folder / "receipts.json", self.receipts)
        assert row["network"]["attempts"] == 0, row
        assert result.returncode == expected, row
        return value

    def prepare(self, *, submit=True, **options):
        observations, predictions = fixture(self.folder, **options)
        self.command("run", "create", self.root)
        version = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))["core"]
        request = {"schema": "goal-v1", "version": 1, "parent_digest": None,
            "original_request": "Compare synthetic reported PCR with a constructed local prediction, not an experiment.",
            "sources": [{"source_id": name, "from": str(path), "as": "artifact",
                         "input_origin": "researcher_observation" if name == "observations" else "user_file", "declared": {}}
                        for name, path in (("observations", observations), ("predictions", predictions))],
            "declared_context": [], "targets": [{"id": "t1", "role": "analysis", "required": True}],
            "constraints": [{"id": "present", "check": "check.goal.output_present@" + version, "params": {},
                             "target": "t1", "source_quote": "Compare the submitted records.", "status": "active"}], "intents": []}
        declared = self.command("goal", "declare", "--run", self.root, request=request)
        template = {"goal_digest": declared["result"]["goal_digest"], "source_id": "observations",
            "predictions_source": "predictions", "observation_origin": "SYNTHETIC_NOT_EXPERIMENTAL", "comparisons": []}
        self.template_receipt = self.command("template", "instantiate", "revival-evidence.assess_predictions",
                                            "--run", self.root, request=template)
        self.draft = self.template_receipt["result"]["draft"]
        if submit:
            self.command("pipeline", "submit", "--run", self.root, request=self.draft)

    def complete(self):
        self.command("run", "execute", "--run", self.root)
        self.command("judge", "--run", self.root)
        sealed = self.command("seal", "--run", self.root)
        assert sealed["result"]["sealed"], sealed
        package = Path(sealed["result"]["manifest"]).parent
        copied = self.folder / "portable" / package.name
        shutil.copytree(package, copied)
        retained = self.folder / "original-run-retained"
        assert self.root.resolve().is_relative_to(self.folder) and retained.resolve().is_relative_to(self.folder)
        self.root.rename(retained)
        verified = self.command("verify", copied)
        assert verified["result"]["verified"], verified
        report = json.loads((copied / "assessment.json").read_text(encoding="utf-8"))
        local = next(row for row in report["conclusions"] if row["claim"] == "local_prediction_agreement"
                     and row["subject"].get("sample_id") == "synthetic_sample")
        result = {"status": local["status"], "reason": local["reason"], "sealed": True, "portable_verified": True,
                  "package": copied.relative_to(self.folder).as_posix(), "commands": len(self.receipts),
                  "connection_attempts": sum(row["network"]["attempts"] for row in self.receipts)}
        write(self.folder / "RESULT.json", result)
        return result

    def oracle(self):
        package = self.folder / json.loads((self.folder / "RESULT.json").read_text(encoding="utf-8"))["package"]
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(ROOT / "tests/oracles/revival_evidence.py"),
            "--observations", str(self.folder / "observations.json"), "--predictions", str(self.folder / "predictions.json"),
            "--rules-dir", str(ROOT / "kits/revival-evidence/knowledge"), "--assessment", str(package / "assessment.json")],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
        (self.folder / "oracle.stdout.txt").write_text(result.stdout, encoding="utf-8")
        (self.folder / "oracle.stderr.txt").write_text(result.stderr, encoding="utf-8")
        assert result.returncode == 0, result.stdout + result.stderr
        return json.loads(result.stdout)


def decision_cases():
    """Expected states are literals from the user's 2026-10-17 table."""
    cases = []
    def add(row, name, expected, **parameters):
        cases.append({"row": row, "name": name, "expected": expected, "parameters": parameters})
    for label, status in (("omitted", None), ("unknown", "unknown"), ("failed", "failed"), ("passed", "passed")):
        add(1, "no-product-positive-" + label, "CONTRADICTED", count=0, result="positive", band=85, controls=status)
        add(2, "wrong-size-positive-" + label, "CONTRADICTED", count=1, result="positive", band=86, controls=status)
    for label, status in (("omitted", None), ("unknown", "unknown"), ("failed", "failed")):
        add(3, "predicted-band-negative-" + label, "INSUFFICIENT", count=1, result="negative", controls=status)
    add(4, "predicted-band-negative-passed", "CONTRADICTED", count=1, result="negative", controls="passed")
    for label, status in (("omitted", None), ("unknown", "unknown")):
        add(5, "no-product-negative-" + label, "INSUFFICIENT", count=0, result="negative", controls=status)
        add(7, "matching-positive-" + label, "INSUFFICIENT", count=1, result="positive", band=85, controls=status)
    add(6, "no-product-negative-passed", "SUPPORTED", count=0, result="negative", controls="passed")
    add(8, "matching-positive-tolerance-edge-passed", "SUPPORTED", count=1, result="positive", band=85, controls="passed")
    add(9, "positive-size-omitted", "INSUFFICIENT", count=1, result="positive", band="omitted", controls="unknown")
    add(9, "positive-size-null", "INSUFFICIENT", count=0, result="positive", band=None, controls="passed")
    add(10, "multiple-products-positive", "INSUFFICIENT", count=2, result="positive", band=85, controls="passed")
    add(10, "multiple-products-negative", "INSUFFICIENT", count=2, result="negative", controls="unknown")
    return sorted(cases, key=lambda row: (row["row"], row["name"]))
