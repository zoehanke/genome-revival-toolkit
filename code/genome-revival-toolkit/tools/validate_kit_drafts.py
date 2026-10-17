"""Validate isolated Kit contract drafts without importing or installing any Kit."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from dna_design_core.kernel import schemas
from tools.check_schemas import template_errors
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def error_data(error):
    """Preserve jsonschema messages without truncation or paraphrase."""
    return {"message": error.message, "instance_path": list(error.absolute_path),
            "schema_path": list(error.absolute_schema_path), "validator": error.validator if isinstance(error.validator, str) else None,
            "context": [error_data(child) for child in error.context]}


def validate_tree(base: Path) -> dict:
    base = base.resolve()
    index = json.loads((base / "rehearsal-index.json").read_text(encoding="utf-8"))
    records, semantic, capability_map = [], [], {}
    documents = {value["$id"] for value in (schemas.document(name) for name in (
        "kit-v1", "capability-v1", "rule-v1", "pipeline-template-v1"))}
    # Resolve against the actual complete, read-only schema inventory.
    schema_names = {"urn:grt:schema:" + path.stem for path in (ROOT / "src/dna_design_core/resources/schemas").rglob("*.json")}
    for kit_dir in sorted((base / "drafts").iterdir()):
        if not kit_dir.is_dir():
            continue
        files = [(kit_dir / "kit.json", "kit-v1")]
        files.extend((path, "capability-v1") for path in sorted((kit_dir / "capabilities").glob("*.json")))
        files.extend((path, "rule-v1") for path in sorted((kit_dir / "knowledge").glob("*.json")))
        files.extend((path, "pipeline-template-v1") for path in sorted((kit_dir / "templates").glob("*.json")))
        for relative, schema_name in index["expected_invalid_probes"].items():
            path = base / relative
            if path.is_relative_to(kit_dir):
                files.append((path, schema_name))
        for path, schema_name in files:
            value = json.loads(path.read_text(encoding="utf-8"))
            errors = list(schemas.validator(schemas.document(schema_name)).iter_errors(value))
            a14 = list(template_errors(value)) if schema_name == "pipeline-template-v1" else []
            if schema_name in ("capability-v1", "pipeline-template-v1"):
                key = "params" if schema_name == "capability-v1" else "params_schema"
                try:
                    Draft202012Validator.check_schema(value[key])
                except SchemaError as error:
                    errors.append(error)
            relative = path.relative_to(base).as_posix()
            record = {"kit": kit_dir.name, "file": relative, "schema": schema_name, "valid": not errors and not a14,
                      "expected_invalid_probe": relative in index["expected_invalid_probes"],
                      "schema_errors": [error_data(error) for error in errors], "a14_errors": [error_data(error) for error in a14]}
            records.append(record)
            if schema_name == "kit-v1":
                for paths in value.get("contributes", {}).values():
                    for relative_path in paths:
                        if not (kit_dir / relative_path).is_file():
                            semantic.append({"kit": kit_dir.name, "issue": "missing_contribution", "file": relative, "message": "Declared contribution is absent: " + relative_path})
            if schema_name == "capability-v1":
                capability_map[value["id"]] = (kit_dir.name, relative, value)
                for port in value["inputs"] + value["outputs"]:
                    reference = port.get("schema_ref")
                    if reference and reference.split("#", 1)[0].removeprefix("urn:grt:schema:") not in {name.removeprefix("urn:grt:schema:") for name in schema_names}:
                        semantic.append({"kit": kit_dir.name, "issue": "K1", "file": relative,
                            "message": "schema_ref is not in the existing local schema registry: " + reference})
            if schema_name == "pipeline-template-v1":
                for row in value.get("steps", []):
                    for port, reference in row.get("inputs", {}).items():
                        if isinstance(reference, list):
                            semantic.append({"kit": kit_dir.name, "issue": "K3", "file": relative,
                                "message": "A3 permits one source/step/artifact/literal reference, not an ordered array of material references: " + row["step_id"] + "." + port})
    for identity, (kit, relative, value) in capability_map.items():
        if value.get("model"):
            _, _, model = capability_map[value["model"]]
            semantic.append({"kit": kit, "issue": "K4", "file": relative,
                "message": "D3 supplies a model capability id but no target-output/argument binding contract. Producer and model differ: " +
                    json.dumps({"producer_inputs": [port["name"] for port in value["inputs"]], "model_inputs": [port["name"] for port in model["inputs"]],
                                "producer_outputs": [port["name"] for port in value["outputs"]], "model_outputs": [port["name"] for port in model["outputs"]]}, ensure_ascii=False)})
        if identity in index["knowledge_consumers"]:
            semantic.append({"kit": kit, "issue": "K6", "file": relative,
                "message": "D12 permits an ACTION evaluator to consume frozen knowledge, but D3 exposes knowledge(pack) only on CHECK ctx.view; no ACTION frozen-knowledge access contract is specified."})
    semantic.append({"kit": "revival-evidence", "issue": "K2", "file": "drafts/revival-evidence/probes/source-missing.json",
        "message": "Draft/unverified does not waive mandatory source fields. Missing-source rows need an explicitly quarantined delivery policy, not invented citations or a loadable knowledge claim."})
    for kit in ("construct", "genome-identity", "revival-evidence"):
        semantic.append({"kit": kit, "issue": "K5", "file": "prompts/s5b-genome-identity.md",
            "message": "The new handoff describes primer_pair without its internal type and does not distinguish no product from unresolved multiple products when product_bp is null. Old schema_version/references-dict/rows files are a different protocol."})
    counts = Counter(record["schema"] for record in records)
    return {"draft_documents": len(records), "by_schema": dict(counts), "schema_invalid_documents": sum(bool(record["schema_errors"]) for record in records),
            "a14_invalid_documents": sum(bool(record["a14_errors"]) for record in records),
            "expected_invalid_probe_documents": sum(record["expected_invalid_probe"] for record in records),
            "question_ids": sorted({row["issue"] for row in semantic if row["issue"].startswith("K")}),
            "records": records, "semantic_findings": semantic,
            "scope": "Schema/A14 and explicit contract rehearsal only. No Kit code imported, no draft is loadable or scientifically accepted."}


def render_markdown(base: Path, result: dict) -> None:
    for path in sorted(base.glob("*.md")):
        kit = path.stem
        if not (base / "drafts" / kit).is_dir():
            continue
        rows = [row for row in result["records"] if row["kit"] == kit]
        findings = [row for row in result["semantic_findings"] if row["kit"] == kit]
        lines = [f"实际校验 {len(rows)} 份草稿；Schema 失败 {sum(bool(row['schema_errors']) for row in rows)}，A14 失败 {sum(bool(row['a14_errors']) for row in rows)}。",
                 "未解析 document schema_ref 等语义问题不冒充 JSON Schema 原生错误。Schema 失败原文如下："]
        failures = [row for row in rows if row["schema_errors"] or row["a14_errors"]]
        if failures:
            lines.extend(["```json", json.dumps(failures, ensure_ascii=False, indent=2), "```"])
        else:
            lines.append("本 Kit 草稿无原生 Schema/A14 失败；这不说明其领域文档或实现可加载。")
        lines.extend(["", "合同/运行语义发现：", "```json", json.dumps(findings, ensure_ascii=False, indent=2), "```"])
        text = path.read_text(encoding="utf-8")
        before, separator, rest = text.partition("<!-- VALIDATION-BEGIN -->")
        if separator:
            _, end, after = rest.partition("<!-- VALIDATION-END -->")
            path.write_text(before + separator + "\n" + "\n".join(lines) + "\n" + end + after, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft-root", type=Path, default=ROOT / "docs/kit-prep")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--write-markdown", action="store_true")
    args = parser.parse_args()
    result = validate_tree(args.draft_root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.write_markdown:
        render_markdown(args.draft_root, result)
    print(json.dumps({key: value for key, value in result.items() if key not in ("records", "semantic_findings")}, ensure_ascii=False, indent=2))
    for row in result["records"]:
        for error in row["schema_errors"] + row["a14_errors"]:
            print(row["file"] + " " + str(error["instance_path"]) + ": " + error["message"])
    return 1 if result["schema_invalid_documents"] or result["a14_invalid_documents"] or result["semantic_findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
