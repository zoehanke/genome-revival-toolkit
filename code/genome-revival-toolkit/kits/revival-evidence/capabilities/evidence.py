"""Kit capabilities: parse, assess, and independently bind recorded inputs to reports."""
from pathlib import Path

from dna_design_core.kernel.public import Outcome, ToolkitError, capability, document_id, file_sha256, loads, make
from .records import read_records
from .assessment import assess, read_rules
from .contract import OBSERVATIONS_DOCUMENT, ASSESSMENT_DOCUMENT


ROOT = Path(__file__).resolve().parents[1]
LIMITS = ["Experimental success (实验已成功).", "Functional revival (功能已复活).",
          "Authenticity of submitted observations (观察本身真实)."]
COMPARISONS = {"type": "array", "items": {"type": "object", "additionalProperties": False,
    "required": ["experiment_group", "control_group"], "properties": {
        "experiment_group": {"type": "string", "minLength": 1},
        "control_group": {"type": "string", "minLength": 1}}}}


def declaration(name, inputs, outputs, properties=None, summary=""):
    check = name.startswith("check_")
    result = {
        "schema": "capability-v1", "id": "evidence." + name,
        "version": loads((ROOT / "kit.json").read_bytes())["version"],
        "role": "CHECK" if check else "ACTION", "summary": summary,
        "effects": ["reads_files"], "deterministic": True, "requires_runtime": [],
        "inputs": inputs, "params": {"type": "object", "properties": properties or {}, "additionalProperties": False},
        "outputs": outputs, "step_checks": [],
        "final_checks": [] if check else [{"check": "evidence.check_record_consistency"}],
        "does_not_establish": LIMITS,
        "source": {"algorithm_refs": ["SPEC D11, D12, B3; prompts/s3-revival-evidence.md"],
                   "implemented_in": "grt_kit_revival_evidence.capabilities.evidence:" + name},
        "owner": "kit:revival-evidence", "granularity": "atomic",
        "authorship": {"kind": "ai", "tool_or_model": "Codex", "date": "2026-10-16"}}
    if check:
        result.update(scope="content_model", evaluates_constraint=False, offline=True,
                      fixtures={"pass": "capabilities/fixtures/consistency.pass.json",
                                "fail": "capabilities/fixtures/consistency.fail.json"})
    return result


@capability(declaration("parse_observations", [
    {"name": "observations", "type": "artifact", "required": True, "constraints": {},
     "description": "UTF-8 CSV counts or JSON observations, genotype_results and functional_results."},
    {"name": "predictions", "type": "artifact", "required": False, "constraints": {},
     "description": "S5b identity-expected-results.json; predictions remain separate from observations."}],
    [{"name": "document", "type": "document", "schema": OBSERVATIONS_DOCUMENT, "output_role": None}],
    {"observation_origin": {"type": "string", "minLength": 1}},
    "Parse supplied observations; retain missing counts and record generated IDs."))
def parse_observations(ctx, observations, predictions=None,
                       observation_origin="Submitted observation; authenticity unverified.") -> Outcome:
    document = read_records(observations, predictions, observation_origin)
    verdicts = []
    if document["generated_ids"]:
        verdicts.append(make(check={"id": "evidence.check_record_consistency",
                                   "version": parse_observations.declaration["version"]},
            scope="content_model", moment="step", issuer="tool_self_report",
            subject={"kind": "document", "id": document_id(document)}, outcome="PASS",
            summary="Missing observation IDs generated and recorded; tool self report only.",
            evidence={"generated_ids": len(document["generated_ids"])}, does_not_establish=LIMITS))
    return Outcome(documents={"document": document}, unverified=document["unverified"], verdicts=verdicts)


@capability(declaration("assess_observations", [
    {"name": "document", "type": "document", "schema": OBSERVATIONS_DOCUMENT, "required": True,
     "constraints": {}, "description": "Normalized parse_observations document."}],
    [{"name": "assessment", "type": "document", "schema": ASSESSMENT_DOCUMENT, "output_role": "analysis"}],
    {"comparisons": COMPARISONS},
    "Apply sourced claim evidence tables; report bounded conclusions and unperformed tests."))
def assess_observations(ctx, document, comparisons=()) -> Outcome:
    result = assess(document, read_rules(ctx), comparisons)
    return Outcome(documents={"assessment": result}, unverified=result["unverified"])


def source_file(view, step, port):
    entry = step["started"]["payload"]["inputs"][port]
    origin = entry["origin"]
    if origin["kind"] == "source":
        source = next(row for row in view.goal["sources"] if row["source_id"] == origin["ref"])
        path = view.root / source["path"]
    elif origin["kind"] == "artifact":
        path = view.root / origin["ref"]
    else:
        raise ToolkitError("PLAN_REF_UNRESOLVED", "Observation files must have a registered source or artifact binding.")
    if file_sha256(path.read_bytes()) != entry["id"]:
        raise ToolkitError("SOURCE_CHANGED")
    return path


@capability(declaration("check_record_consistency", [], [], summary=
    "Check recorded source parsing, truth-table conclusions and exported report against fixed rule snapshots."))
def check_record_consistency(ctx) -> Outcome:
    view = ctx.view
    failures, basis, rule_refs, supported = [], [], [], []
    outcome = "PASS"
    try:
        rules = read_rules(ctx)
        if not rules:
            raise ToolkitError("KNOWLEDGE_SOURCE_INVALID", "No evidence rule snapshot is available.")
        rule_refs = [document_id(row) for row in rules]
    except ToolkitError:
        rules = []
        outcome = "UNKNOWN"
    if rules:
        parsed = {}
        steps = [row for row in view.steps() if row["completed"] and not row["superseded"]]
        assessed = []
        try:
            for step in steps:
                identity = step["definition"]["step_id"]
                use = step["definition"]["use"].split("@")[0]
                output = step["completed"]["payload"]["outputs"]["documents"]
                if use == "evidence.parse_observations":
                    started = step["started"]["payload"]
                    prediction = source_file(view, step, "predictions") if "predictions" in started["inputs"] else None
                    expected = read_records(source_file(view, step, "observations"), prediction, **started["params"])
                    actual = view.document(output["document"][0])
                    if actual != expected:
                        failures.append(identity)
                    parsed[identity] = output["document"][0]
                elif use == "evidence.assess_observations":
                    started = step["started"]["payload"]
                    entry = started["inputs"]["document"]
                    origin = entry["origin"]
                    if origin["kind"] != "step" or parsed.get(origin["ref"]["step_id"]) != entry["id"]:
                        failures.append(identity)
                    expected = assess(view.document(entry["id"]), rules, **started["params"])
                    actual = view.document(output["assessment"][0])
                    if actual != expected:
                        failures.append(identity)
                    assessed.append((identity, output["assessment"][0]))
                    supported.extend(row for row in expected["conclusions"]
                                     if row["subject"] and row["status"] == "SUPPORTED")
                else:
                    continue
                basis.extend([step["started"]["hash"], step["completed"]["hash"]])
            if not assessed:
                outcome = "UNKNOWN"
            for output in view.candidate["outputs"]:
                if output["step_id"] not in {row[0] for row in assessed}:
                    continue
                exported = loads((Path(view.candidate["root"]) / output["path"]).read_bytes())
                if exported != view.document(output["id"]):
                    failures.append(output["step_id"])
            if failures:
                outcome = "FAIL"
        except (ToolkitError, OSError, KeyError, TypeError, ValueError, StopIteration):
            outcome = "FAIL"
    summary = "Recorded observations, sourced conclusion rules and exported content compared."
    if outcome == "PASS":
        entries = [row["claim"] + " (" + ", ".join(key + "=" + str(value)
                   for key, value in sorted(row["subject"].items())) + "): " + row["reason"] for row in supported]
        summary = (("Supported scoped conclusions (submitted records only): " + "; ".join(entries) + ". " if entries
                    else "No scoped conclusion is supported. ") +
                   "Does not support: " + "; ".join(LIMITS) + " " + summary)
    return Outcome(verdicts=[make(check={"id": "evidence.check_record_consistency",
        "version": check_record_consistency.declaration["version"]}, scope="content_model", moment="final",
        issuer="check_capability", subject={"kind": "run", "id": view.events()[0]["run_id"]},
        outcome=outcome, summary=summary,
        evidence={"different_steps": sorted(set(failures)), "rule_count": len(rules)},
        basis=basis, rule_refs=rule_refs, does_not_establish=LIMITS)])
