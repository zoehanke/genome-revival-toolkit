"""Developer-only declaration/data export and construction of synthetic S2 fixtures."""
import argparse
from copy import deepcopy
import importlib
import inspect
import json
from pathlib import Path
from random import Random
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "kits/cut-plasmid"
LEGACY_COMMIT = "bf90910e5b0e67985aa37db4e0b8507cbc24f2b4"
LEGACY_PATH = "genome-revival-toolkit/kits/crispr/rules/selection.json"
GUIDE = "GACATCGTACGATCGTACAT"
OLD = "CGACATCGTACGATCGTACA"
TARGET = "TACATATCCATACGACATCGTACGATCGTACATAGGTTACATATACCA"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def material(sequence, topology="circular", features=None):
    return {"sequence": sequence, "topology": topology, "strandedness": "double", "ends": None, "features": features or []}


def synthetic_b2():
    rng = Random(2026101602)
    random_bases = "".join(rng.choice("ACGT") for _ in range(360))
    vector = random_bases[:130] + OLD + "GTT" + random_bases[153:]
    assert TARGET[13:33] == GUIDE and TARGET[33:36] == "AGG"
    return {"oracle": {"kind": "construction", "method": "SPEC B2 fixed random seed, then explicit slices; expected edit defined before implementation."},
            "vector": material(vector), "target": material(TARGET, "linear"),
            "params": {"promoter_end": 130, "transcription_strand": 1, "scaffold_sequence": vector[150:173]},
            "spacer": GUIDE, "expected_product": vector[:130] + GUIDE + vector[150:],
            "expected_linear_product": vector[150:] + vector[:130] + GUIDE,
            "expected_forward": "GTTGCTGTGATCACTTGAGTAC",
            "expected_reverse": "ATGTACGATCGTACGATGTCGTTTTTTCGGAAATATGATTTCCAGAG"}


def export_declarations():
    namespace = "cut_plasmid_export"
    package = types.ModuleType(namespace)
    package.__path__ = [str(KIT)]
    sys.modules[namespace] = package
    functions = []
    for module in ("guide", "preparation", "selection", "model", "checks"):
        loaded = importlib.import_module(namespace + ".capabilities." + module)
        for function in vars(loaded).values():
            if callable(function) and getattr(function, "__module__", None) == loaded.__name__ and hasattr(function, "declaration"):
                write(KIT / "capabilities" / (function.declaration["id"].split(".")[-1] + ".json"), function.declaration)
                functions.append(function)
    skill = KIT / "SKILL.md"
    if "<!-- GENERATED:START -->" in skill.read_text(encoding="utf-8"):
        before, tail = skill.read_text(encoding="utf-8").split("<!-- GENERATED:START -->", 1)
        _, after = tail.split("<!-- GENERATED:END -->", 1)
        lines = ["", "Generated from decorated capability contracts and signatures.", "",
                 "| Capability | Inputs | Parameters | Outputs |", "| --- | --- | --- | --- |"]
        for function in sorted(functions, key=lambda value: value.declaration["id"]):
            row = function.declaration
            parameters = inspect.signature(function).parameters
            settings = []
            for name in row["params"]["properties"]:
                default = parameters[name].default
                settings.append(name + (" (required)" if default is inspect.Parameter.empty else "=" + json.dumps(default)))
            inputs = ", ".join(port["name"] + ":" + port["type"] for port in row["inputs"]) or "none"
            outputs = ", ".join(port["name"] + ":" + str(port["output_role"]) for port in row["outputs"]) or "verdicts only"
            lines.append("| " + row["id"] + "@" + row["version"] + " | " + inputs + " | " + (", ".join(settings) or "none") + " | " + outputs + " |")
        skill.write_text(before + "<!-- GENERATED:START -->" + "\n".join(lines) + "\n<!-- GENERATED:END -->" + after, encoding="utf-8", newline="\n")


def migrate_rules(legacy_repo):
    current_path = KIT / "knowledge/selection_markers.json"
    current_rows = json.loads(current_path.read_text(encoding="utf-8"))["parameters"]["rows"] if current_path.exists() else []
    original = subprocess.check_output(["git", "-C", str(legacy_repo), "show", LEGACY_COMMIT + ":" + LEGACY_PATH])
    legacy = json.loads(original)
    classes = {"manufacturer": "official_method", "peer_reviewed_paper": "literature", "curated_database": "database_record"}
    rows, quarantined = [], []
    for old in legacy["rules"]:
        mapping = old["action"]["value"]
        for host, (plate, source_key) in mapping["hosts"].items():
            source = mapping["sources"].get(source_key, {})
            complete = source.get("source_type") in classes and all(source.get(key) for key in ("name", "url", "retrieved_at"))
            row = {"schema": "rule-v1", "id": "selection." + mapping["marker_id"] + "." + host,
                   "name": old["name"] + " in " + host, "version": old["version"],
                   "status": old["status"] if complete else "draft", "purpose": "interpretation",
                   "evaluator": "cut_plasmid.assess_selection",
                   "parameters": {"marker_id": mapping["marker_id"], "pattern": mapping["pattern"], "host": host,
                                  "plate": plate, "auxotrophy": mapping["auxotrophy"],
                                  "legacy_rule_id": old["id"], "legacy_commit": LEGACY_COMMIT},
                   "applies_when": [{"field": "marker_id", "op": "eq", "value": mapping["marker_id"]}],
                   "source": {"source_class": classes.get(source.get("source_type")), "citation": source.get("name"),
                              "locator": source.get("url"), "retrieved_at": source.get("retrieved_at"),
                              "content_ref": None, "archive_note": "Migrated citation only; no archived page or new human verification receipt.",
                              "supports": [host + " selection mapping for " + mapping["marker_id"]],
                              "does_not_support": ["Expression, resistance or selection measured in the user's strain."],
                              "verification_status": "unverified"},
                   "limits": ["Requires explicitly declared strain genotype; missing genotype yields UNKNOWN."],
                   "review": "knowledge/review/selection." + mapping["marker_id"] + "." + host + ".review.json",
                   "authorship": {"kind": "ai", "tool_or_model": "Codex; legacy authorship unknown", "date": "2026-10-17"}}
            (rows if complete else quarantined).append(row)
    migrated_count = len(rows)
    rows.extend(row for row in current_rows if "legacy_rule_id" not in row["parameters"])
    container = {"schema": "rule-v1", "id": "cut_plasmid.selection_markers", "name": "Source-labelled selection marker collection",
                 "version": 1, "status": "active", "purpose": "interpretation", "evaluator": "cut_plasmid.assess_selection",
                 "parameters": {"rows": rows}, "applies_when": [],
                 "source": {"source_class": "project_contract", "citation": "SPEC D11/D12 and MIGRATION-MAP section 6",
                            "locator": "spec/MIGRATION-MAP.md#6", "retrieved_at": "2026-10-17", "content_ref": None,
                            "archive_note": "Local project contract; biological source citations reside on each row.",
                            "supports": ["Collection format and conditional interpretation policy."],
                            "does_not_support": ["Biological truth of the nested mappings or measured selectable phenotype."],
                            "verification_status": "unverified"},
                 "limits": ["AI migrated, without human review or source verification."],
                 "review": "knowledge/review/selection_markers.review.json",
                 "authorship": {"kind": "ai", "tool_or_model": "Codex", "date": "2026-10-17"}}
    write(KIT / "knowledge/selection_markers.json", container)
    for row in quarantined:
        write(KIT / "knowledge/drafts" / (row["id"] + ".json"), row)
    write(ROOT / "tests/evidence/s2/selection-migration.json", {
        "legacy_commit": LEGACY_COMMIT, "legacy_path": LEGACY_PATH,
        "legacy_file_lines": len(original.decode("utf-8").splitlines()), "legacy_rule_count": len(legacy["rules"]),
        "migrated_host_rule_count": migrated_count, "source_incomplete_rows": [row["id"] for row in quarantined],
        "new_human_verification_receipts": 0})
    write_sources()


def write_sources():
    rows = json.loads((KIT / "knowledge/selection_markers.json").read_text(encoding="utf-8"))["parameters"]["rows"]
    sources = ["# Selection source references", "", "Generated from selection_markers.json. Sources were not fetched or independently verified; no human review is recorded.", "",
               "Host-specific rows: " + str(len(rows)) + ".", ""]
    for row in rows:
        primary = row["source"]
        sources.append("* " + row["id"] + ": " + primary["citation"] + ". " + primary["locator"])
        for source in [primary, *row["parameters"].get("supplementary_sources", [])]:
            if source is not primary:
                sources.append("  * Supplementary citation: " + source["citation"] + ". " + source["locator"])
            sources.append("  * Source class: " + source["source_class"] + "; retrieved_at: " + source["retrieved_at"] + "; verification_status: " + source["verification_status"] + ".")
            sources.append("  * Supports: " + " ".join(source["supports"]))
            sources.append("  * Does not support: " + " ".join(source["does_not_support"]))
            if source is not primary:
                sources.append("  * Archive note: " + source["archive_note"])
    (KIT / "knowledge/SOURCES.md").write_text("\n".join(sources) + "\n", encoding="utf-8", newline="\n")


def templates_and_fixtures():
    case = synthetic_b2()
    write(KIT / "examples/b2.json", case)
    for check in ("check_direction", "check_pam", "check_vector_self_target"):
        for kind in ("pass", "fail"):
            fixture = deepcopy(case)
            fixture["vector"]["sequence"] = case["expected_product"]
            fixture["check"] = "cut_plasmid." + check
            fixture["expected"] = "FAIL" if kind == "fail" else "PASS"
            # PROVISIONAL(S2-Q2): CHECK params and inspection setup are distinct fixture inputs.
            fixture["setup_params"] = fixture.pop("params")
            fixture["params"] = {}
            if kind == "fail":
                if check == "check_direction":
                    complement = str.maketrans("ACGT", "TGCA")
                    fixture["vector"]["sequence"] = case["vector"]["sequence"][:130] + GUIDE.translate(complement)[::-1] + case["vector"]["sequence"][150:]
                elif check == "check_pam":
                    fixture["target"]["sequence"] = TARGET[:35] + "A" + TARGET[36:]
                else:
                    sequence = fixture["vector"]["sequence"]
                    fixture["vector"]["sequence"] = sequence[:20] + GUIDE + "TGG" + sequence[43:]
            write(KIT / "capabilities/fixtures" / (check + "." + kind + ".json"), fixture)
    text = {"selection_unknown": "Selection UNKNOWN: strain genotype was not provided.",
            "scope": "Exact supplied-sequence checks and preparation models only.",
            "laboratory": "PLANNED / NOT_PERFORMED", "review": "AI drafted, without human review."}
    write(KIT / "text/en.json", text)
    common = {"goal_digest": {"type": "string"}, "vector_source": {"type": "string"}, "target_source": {"type": "string"},
              "promoter_end": {"type": "integer"}, "transcription_strand": {"type": "integer", "enum": [-1, 1]},
              "scaffold_sequence": {"type": "string"}, "analysis_target": {"type": "string"}}
    for name in ("inspect_only", "replace_spacer"):
        properties = deepcopy(common)
        if name == "replace_spacer":
            properties.update(spacer={"type": "string"}, construct_target={"type": "string"}, primer_target={"type": "string"})
        parameters = {key: "{{" + key + "}}" for key in ("promoter_end", "transcription_strand", "scaffold_sequence")}
        steps = [{"step_id": "inspect", "use": "cut_plasmid.inspect_guide", "inputs": {"vector": {"source": "{{vector_source}}"}, "target": {"source": "{{target_source}}"}},
                  "params": parameters, "why": "Inspect the supplied directed guide against the supplied target."}]
        outputs = [{"name": "inspection", "from": {"step": "inspect", "port": "guide"}, "target": "{{analysis_target}}"}]
        if name == "replace_spacer":
            steps = [{"step_id": "replace", "use": "cut_plasmid.replace_spacer", "inputs": deepcopy(steps[0]["inputs"]),
                      "params": {**parameters, "spacer": "{{spacer}}"}, "why": "Replace the user-selected spacer and independently simulate the preparation."},
                     {"step_id": "inspect", "use": "cut_plasmid.inspect_guide", "inputs": {"vector": {"step": "replace", "port": "product"}, "target": {"source": "{{target_source}}"}},
                      "params": parameters, "why": "Inspect the replaced cassette from its sequence."},
                     {"step_id": "selection", "use": "cut_plasmid.assess_selection", "inputs": {"vector": {"step": "replace", "port": "product"}},
                      "params": {}, "why": "Retain selection UNKNOWN without an explicitly supplied genotype."}]
            outputs = [{"name": "construct", "from": {"step": "replace", "port": "product"}, "target": "{{construct_target}}"},
                       {"name": "primers", "from": {"step": "replace", "port": "primers"}, "target": "{{primer_target}}"},
                       {"name": "selection", "from": {"step": "selection", "port": "selection"}, "target": "{{analysis_target}}"}]
        for step in steps:
            for key, reference in list(step["inputs"].items()):
                if reference == {"source": "{{vector_source}}"}:
                    step["inputs"][key] = {"step": "read_vector", "port": "material"}
                elif reference == {"source": "{{target_source}}"}:
                    step["inputs"][key] = {"step": "read_target", "port": "material"}
        readers = [{"step_id": "read_" + key, "use": "format.read_genbank",
                    "inputs": {"file": {"source": "{{" + key + "_source}}"}}, "params": {"strandedness": "double"},
                    "why": "Read the registered synthetic GenBank source with explicit duplex status."} for key in ("vector", "target")]
        write(KIT / "templates" / (name + ".json"), {"schema": "pipeline-template-v1", "version": 1,
            "goal_digest": "{{goal_digest}}", "params_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False},
            "steps": readers + steps, "outputs": outputs,
            "authorship": {"kind": "ai", "tool_or_model": "Codex", "date": "2026-10-17"}})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-repo", type=Path, default=None,
                        help="Local source repository containing the pinned legacy rule commit; no network access. Required unless --sources-only.")
    parser.add_argument("--sources-only", action="store_true", help="Regenerate only the source summary from current knowledge.")
    args = parser.parse_args()
    if args.sources_only:
        write_sources()
    else:
        if args.legacy_repo is None:
            parser.error("--legacy-repo is required unless --sources-only")
        export_declarations()
        migrate_rules(args.legacy_repo)
        templates_and_fixtures()
