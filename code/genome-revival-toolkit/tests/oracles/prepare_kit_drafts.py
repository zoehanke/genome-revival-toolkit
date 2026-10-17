"""Generate source-backed Kit rehearsal documents, never Kit implementation code."""
from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parents[1]
LEGACY = Path("<WORK>/github")
KIT_COMMIT = "bf90910e5b0e67985aa37db4e0b8507cbc24f2b4"
CORE_COMMIT = "750bf4849b818be00f28684513ef19c01d901bcb"
DEST = ROOT / "docs/kit-prep"
KIT_NAMES = {"cut-plasmid": "crispr", "revival-evidence": "evidence", "construct": "construct", "genome-identity": "identity"}
VERSIONS = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def old(path, commit=KIT_COMMIT):
    return subprocess.check_output(["git", "-C", str(LEGACY), "show", commit + ":" + path]).decode("utf-8")


def source_inventory():
    tree = subprocess.check_output(["git", "-C", str(LEGACY), "ls-tree", "-r", "--name-only", KIT_COMMIT], text=True).splitlines()
    rows = []
    for name, legacy_name in KIT_NAMES.items():
        prefix = "genome-revival-toolkit/kits/" + legacy_name + "/"
        selected = [path for path in tree if path.startswith(prefix) and path.endswith(".py") and "/scripts/" in path]
        for path in selected:
            text = old(path)
            parsed = ast.parse(text)
            functions = [{"name": node.name, "start": node.lineno, "end": node.end_lineno, "lines": node.end_lineno - node.lineno + 1}
                         for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef)]
            script = Path(path).stem
            disposition = "discard_framework" if script in ("entry", "hooks", "presentation", "output") else "extract_domain_only_discard_orchestration"
            rows.append({"kit": name, "path": path, "commit": KIT_COMMIT, "file_lines": len(text.splitlines()),
                         "functions": functions, "disposition": disposition})
    common = [
        ("cut-plasmid", "snapgene-dna-design/core/tools/grna.py", KIT_COMMIT),
        ("cut-plasmid", "snapgene-dna-design/core/tools/grna_evaluation.py", KIT_COMMIT),
        ("cut-plasmid", "snapgene-dna-design/core/tools/grna_preparation.py", KIT_COMMIT),
        ("construct", "snapgene-dna-design/core/handlers/integration_donor.py", CORE_COMMIT),
        ("construct", "snapgene-dna-design/core/recipes/gibson.py", CORE_COMMIT),
        ("construct", "snapgene-dna-design/core/recipes/verification.py", CORE_COMMIT),
        ("genome-identity", "snapgene-dna-design/core/tools/comparison.py", CORE_COMMIT),
    ]
    for kit, path, commit in common:
        text = old(path, commit)
        parsed = ast.parse(text)
        functions = [{"name": node.name, "start": node.lineno, "end": node.end_lineno, "lines": node.end_lineno - node.lineno + 1}
                     for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef)]
        rows.append({"kit": kit, "path": path, "commit": commit, "file_lines": len(text.splitlines()),
                     "functions": functions, "disposition": "retain_domain_algorithms_only"})
    return rows


def function_decision(name):
    if name in ("evaluate_candidates", "design_crispr_grna"):
        return "首版丢弃候选 gRNA 枚举/排序；只检查或替换用户选定 guide"
    if name in ("_discrimination", "conclusion_rows", "_count", "marker_ids", "selection_report", "_assessment", "compare_expected", "expectation_table"):
        return "保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology"
    if name in ("read_expected_results", "read_construct_handoff", "write_handoff", "read_bound_observations"):
        return "保留显式文件/参考绑定原则；按新交接形状重写，丢弃旧 Trace 与旧 schema_version 协议"
    if name in ("check_grna", "replace_grna_spacer", "check_grna_vector", "_locate", "_target_matches"):
        return "科学判据留给 S2；本轮不移植 CRISPR 代码"
    if name in ("_interval", "validate_options", "mapping_rows", "_mapping_rows", "mapping_sources"):
        return "丢弃旧加载/字段手验/缓存外壳，使用接纳契约、来源数据和共享坐标函数"
    if name.startswith("run_") or name in ("call", "failure", "main", "context_for_result", "summary", "fact_text", "outputs", "_primer_outputs", "_save", "write_selection"):
        return "丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接"
    return "只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移"


def inp(name, kind="material", schema=None, required=True):
    result = {"name": name, "type": kind, "required": required, "constraints": {}, "description": name.replace("_", " ")}
    if schema:
        result["schema_ref"] = schema
    return result


def out(name, kind="document", role="analysis", schema=None):
    result = {"name": name, "type": kind, "output_role": role}
    if schema:
        result["schema_ref"] = schema
    return result


def cap(kit, identity, inputs, outputs, properties=None, required=(), *, check_scope=None, effects=("pure",), composite=False, final_checks=(), model=None):
    module = "grt_kit_" + kit.replace("-", "_") + ".capabilities.operations:"
    result = {"schema": "capability-v1", "id": identity, "version": VERSIONS["kits"][kit],
              "role": "CHECK" if check_scope else "ACTION", "summary": "Draft contract for " + identity + "; no Kit implementation exists.",
              "effects": list(effects), "deterministic": True, "requires_runtime": [], "inputs": inputs,
              "params": {"type": "object", "properties": properties or {}, "required": list(required), "additionalProperties": False},
              "outputs": outputs, "step_checks": [], "final_checks": [{"check": item} for item in final_checks],
              "does_not_establish": ["Experimental success, authentic genotype, functional revival or genome-wide safety."],
              "source": {"algorithm_refs": ["spec/MIGRATION-MAP.md section 6"], "implemented_in": module + identity.rsplit(".", 1)[1]},
              "owner": "kit:" + kit, "granularity": "composite" if composite else "atomic"}
    if model:
        result["model"] = model
    if check_scope:
        name = identity.rsplit(".", 1)[1]
        result.update(scope=check_scope, evaluates_constraint=False, offline=True,
                      fixtures={variant: "capabilities/fixtures/" + name + "." + variant + ".json" for variant in ("pass", "fail")})
    return result


INT = {"type": "integer", "minimum": 0}
POS = {"type": "integer", "minimum": 1}
TEXT = {"type": "string"}
DNA20 = {"type": "string", "pattern": "^[ACGT]{20}$"}


def capabilities():
    cp = "cut-plasmid"
    guide_inputs = [inp("vector"), inp("target")]
    selectors = {"promoter_end": INT, "transcription_strand": {"enum": [-1, 1]}, "scaffold_sequence": TEXT}
    guide_checks = ("cut_plasmid.check_direction", "cut_plasmid.check_pam", "cut_plasmid.check_vector_self_target")
    cut = [
        cap(cp, "cut_plasmid.inspect_guide", guide_inputs, [out("guide", schema="guide-inspection-v1")], selectors, ("promoter_end", "transcription_strand", "scaffold_sequence"), final_checks=guide_checks),
        cap(cp, "cut_plasmid.replace_spacer", guide_inputs, [out("product", "material", "construct"), out("primers", role="primer_set", schema="primer-set-v1"), out("route", schema="route-plan-v1")],
            {**selectors, "spacer": DNA20, "target_tm": {"type": "string"}}, ("promoter_end", "transcription_strand", "scaffold_sequence", "spacer", "target_tm"),
            composite=True, final_checks=guide_checks, model="cut_plasmid.model_replace"),
        cap(cp, "cut_plasmid.assess_selection", [inp("vector"), inp("declared_genotype", "value", required=False)], [out("selection", schema="selection-assessment-v1")]),
        cap(cp, "cut_plasmid.model_replace", guide_inputs, [out("product", "material", "construct")], {**selectors, "spacer": DNA20}, ("promoter_end", "transcription_strand", "scaffold_sequence", "spacer")),
    ]
    for identity in guide_checks:
        cut.append(cap(cp, identity, [], [], check_scope="content_model", effects=("reads_files",)))
    for value in cut:
        value["does_not_establish"] = ["Cleavage activity", "Editing efficiency", "Genome-wide off-target safety", "Wet-laboratory PCR, DpnI, KLD or transformation."]
    ev = "revival-evidence"
    evidence = [
        cap(ev, "evidence.parse_observations", [inp("file", "artifact")], [out("observations", schema="observation-table-v1")], {"id_prefix": TEXT}, effects=("reads_files",)),
        cap(ev, "evidence.assess_observations", [inp("observations", "document", "observation-table-v1"), inp("expected_results", "artifact", required=False)], [out("assessment", schema="revival-assessment-v1")], effects=("reads_files",), final_checks=("evidence.check_record_consistency",)),
        cap(ev, "evidence.check_record_consistency", [], [], check_scope="content_model", effects=("reads_files",)),
    ]
    for value in evidence:
        value["does_not_establish"] = ["Experimental success", "Functional revival", "Authenticity of submitted observations", "Whole-genome identity or elimination."]
    con = "construct"
    donor_inputs = [inp("reference"), inp("cargo"), inp("donor_template", required=False)]
    donor_params = {"start": INT, "end": INT, "arm_length": POS, "cargo_start": INT, "cargo_end": POS,
                    "preparation_method": {"enum": ["gibson", "pcr"]}, "overlap": POS}
    donor_required = ("start", "end", "arm_length", "cargo_start", "cargo_end", "preparation_method")
    construct = [
        cap(con, "construct.model_donor", [inp("reference"), inp("cargo")], [out("product", "material", "construct")],
            {key: value for key, value in donor_params.items() if key not in ("preparation_method", "overlap")}, ("start", "end", "arm_length", "cargo_start", "cargo_end")),
        cap(con, "construct.design_donor", donor_inputs, [out("product", "material", "construct"), out("primers", role="primer_set", schema="primer-set-v1"), out("route", schema="route-plan-v1")],
            donor_params, donor_required, composite=True, final_checks=("construct.check_junction_assay",), model="construct.model_donor"),
        cap(con, "construct.design_junction_assay", [inp("original"), inp("edited"), inp("donor")], [out("primers", role="primer_set", schema="primer-set-v1")],
            {"left_arm": {"type": "array", "items": INT, "minItems": 2, "maxItems": 2}, "right_arm": {"type": "array", "items": INT, "minItems": 2, "maxItems": 2}},
            ("left_arm", "right_arm"), composite=True, final_checks=("construct.check_junction_assay",)),
        cap(con, "construct.check_junction_assay", [], [], check_scope="preparation_model", effects=("reads_files",)),
        cap(con, "construct.export_handoff", [inp("original_file", "artifact"), inp("edited_file", "artifact"), inp("primers", "document", "primer-set-v1")],
            [out("handoff", "artifact", "analysis")], {"name": TEXT}, ("name",), effects=("reads_files", "writes_files")),
    ]
    for value in construct:
        value["does_not_establish"] = ["Successful laboratory donor preparation", "Transformation efficiency", "Authentic integration locus", "Functional revival."]
    ident = "genome-identity"
    identity = [
        cap(ident, "identity.compare_regions", [inp("references", "materials")], [out("comparison", schema="region-comparison-v1")],
            {"regions": {"type": "array", "items": {"type": "object"}}}, ("regions",)),
        cap(ident, "identity.analyze_assay", [inp("references", "materials"), inp("forward"), inp("reverse"), inp("handoff", "document", "identity-handoff-v1", required=False)], [out("expected_results", schema="identity-expected-results-v1")],
            {"assay_id": TEXT, "size_resolution_bp": {"type": ["integer", "null"], "minimum": 1}}, ("assay_id",)),
        cap(ident, "identity.read_handoff", [inp("file", "artifact")], [out("handoff", schema="identity-handoff-v1")], effects=("reads_files",), final_checks=("identity.check_handoff",)),
        cap(ident, "identity.check_handoff", [], [], check_scope="file", effects=("reads_files",)),
    ]
    for value in identity:
        value["does_not_establish"] = ["Primer specificity in an actual strain", "Observed experimental products", "Authentic genotype", "Whole-genome discrimination."]
    return {cp: cut, ev: evidence, con: construct, ident: identity}


SHARED = {
    "cut-plasmid": ["replace_material_region", "inspect_cds", "enumerate_primer_candidates", "sequencing_read_coverage", "find_binding_sites", "pcr_material", "inverse_pcr_material", "calculate_tm"],
    "construct": ["replace_material_region", "inspect_cds", "enumerate_primer_candidates", "sequencing_read_coverage", "slice_material", "pcr_material", "gibson_material", "predict_pcr_products"],
    "genome-identity": ["enumerate_primer_candidates", "predict_pcr_products", "find_binding_sites", "slice_material"],
    "revival-evidence": [],
}
KIT_ONLY = {
    "cut-plasmid": ["Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).", "Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration."],
    "construct": ["Independent donor model, homology-arm selection and cargo layout.", "Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization."],
    "genome-identity": ["Regional alignment, assay discrimination and identity handoff parsing/output, only this Kit requires their domain decisions."],
    "revival-evidence": ["CSV ID completion, unknown counts, finite rule evaluation, observation/prediction matching and bounded conclusions; no biology calculations."],
}


NEGATIVES = {
    "cut-plasmid": [
        ("reverse_insert", "Use a nonpalindromic 20 nt spacer, its reverse complement in vector, one correctly oriented target + NGG; keep annotations falsely forward.", "FAIL direction from actual transcribed sequence; annotation does not override bases."),
        ("one_base_pam", "Change the last G of target NGG to A with protospacer unchanged.", "FAIL with domain finding INVALID_PAM, paired original NGG control passes."),
        ("annotation_contradiction", "Keep valid bases but flip annotated chain; separately label the spacer as CDS.", "Keep contradiction visible; do not infer a selectable marker from that annotation."),
        ("inherited_cds", "Carry one known-invalid CDS unchanged through copy/rotation; compare with a newly introduced invalid CDS.", "D7 source-bound inherited finding is listed; introduced or unbound finding fails. Shared CDS metrics alone never grant inheritance."),
        ("tm_parameters", "Same primer with Na 50 mM/Mg 0 versus explicitly changed Mg/salt method.", "Output parameters and method differ; no silent comparison against a single generic 60 C number."),
        ("sequencing_off_by_one", "Primer [0,4), trim=1, read_length=4 on a labelled sequence.", "Covered bases are [5,8), excluding primer and the first trimmed base."),
    ],
    "construct": [
        ("linear_gibson_import", "Three labelled linear fragments with explicit overlaps and known final concatenation.", "Typed linear product or retained original failure; never missing feature_to_dict followed by checked_scope KeyError."),
        ("donor_carryover", "Place both junction primers wholly inside retained donor homology arms.", "PCR predicts a residual-donor band and report warns that the assay cannot establish genomic integration."),
        ("invalid_marker_orf", "Replace ATG AAA TAA with ATG TAA TAA, keeping the same marker label.", "Internal stop is detected; apply D7 separately to inherited versus introduced annotation."),
        ("donor_bounds", "Reference edit [100,160), 50 bp arms, cargo length 90; then move edit start to 30.", "Valid donor is 190 bp from [50,100)+cargo+[160,210); out-of-range 50 bp arm is refused."),
        ("repeated_binding", "Insert a second exact copy of one primer core in a supplied reference.", "Retain all matches and ambiguity, never choose the shortest amplicon as unique."),
    ],
    "genome-identity": [
        ("different_sizes", "Generate common unique primer flanks with interiors fixing lengths 1000 and 1300.", "Predicted lengths are exactly 1000/1300; resolution is explicit before a discrimination statement."),
        ("same_sizes", "Two different backgrounds have the same predicted band state and length.", "NOT_DISTINGUISHABLE for this assay; sequence differences alone do not imply different bands."),
        ("multiple_sites", "Duplicate a complete primer site in one background only.", "Ambiguity stays distinct from a negative product; cannot encode a single certain product length."),
        ("circular_origin", "Place a complete core across the last and first bases of a constructed circle.", "Coordinates wrap and exact product is computed from the same declared circle."),
        ("handoff_hash", "Change one byte of a reference file after preparing its handoff hash.", "Reference/file binding fails before biological discrimination."),
    ],
    "revival-evidence": [
        ("csv_missing_id", "CSV has group,colonies but no id; two rows have the same group.", "Assign distinct stable IDs and record that IDs were program-supplied; do not claim they were measured."),
        ("missing_not_zero", "One group count is blank and another explicit count is zero.", "Blank remains unknown and is not equal to zero; no invented total or negative experiment."),
        ("control_outgrowth", "Fusion group reports 9 colonies, inactivated donor control reports 31.", "Control contradiction remains visible; functional revival stays INSUFFICIENT."),
        ("counts_only", "Provide colonies but no PCR or genetic evidence.", "Functional revival is INSUFFICIENT and unperformed tests remain listed."),
        ("source_missing", "Remove source metadata from an otherwise well-formed draft rule.", "Keep draft/unverified outside loadable knowledge; actual rule-v1 validation fails rather than fabricate source."),
    ],
}


def parameter(name, kind="string"):
    return {"type": kind, "description": "Explicit caller-provided " + name.replace("_", " ") + "; no inferred source or scientific threshold."}


def step(name, use, inputs, params=None):
    return {"step_id": name, "use": use, "inputs": inputs, "params": params or {}, "why": "Apply the declared operation to explicitly registered synthetic inputs."}


def template(steps, output_step, output_port, params):
    definitions = {"goal_digest": {**parameter("goal_digest"), "pattern": "^[0-9a-f]{64}$"}, "target_id": parameter("target_id"), **params}
    return {"schema": "pipeline-template-v1", "version": 1, "goal_digest": "{{goal_digest}}", "steps": steps,
            "outputs": [{"name": "result", "from": {"step": output_step, "port": output_port}, "target": "{{target_id}}"}],
            "params_schema": {"type": "object", "properties": definitions, "required": list(definitions), "additionalProperties": False}}


def templates():
    result = {name: {} for name in KIT_NAMES}
    loaders = [step("vector", "format.read_genbank", {"file": {"source": "{{vector_source}}"}}, {"strandedness": "double"}),
               step("target", "format.read_fasta", {"file": {"source": "{{target_source}}"}}, {"topology": "linear", "strandedness": "double"})]
    common = {"vector_source": parameter("vector_source"), "target_source": parameter("target_source"),
              "promoter_end": parameter("promoter_end", "integer"), "transcription_strand": parameter("transcription_strand", "integer"), "scaffold_sequence": parameter("scaffold_sequence")}
    selectors = {key: "{{" + key + "}}" for key in ("promoter_end", "transcription_strand", "scaffold_sequence")}
    guide_inputs = {"vector": {"step": "vector", "port": "material"}, "target": {"step": "target", "port": "material"}}
    result["cut-plasmid"]["inspect_only"] = template(loaders + [step("inspect", "cut_plasmid.inspect_guide", guide_inputs, selectors)], "inspect", "guide", common)
    result["cut-plasmid"]["replace_spacer"] = template(loaders + [step("replace", "cut_plasmid.replace_spacer", guide_inputs,
        {**selectors, "spacer": "{{spacer}}", "target_tm": "{{target_tm}}"})], "replace", "product", {**common, "spacer": parameter("spacer"), "target_tm": parameter("target_tm")})
    parse = step("parse", "evidence.parse_observations", {"file": {"source": "{{observations_source}}"}}, {"id_prefix": "obs"})
    for mode in ("observations_only", "compare_predictions"):
        inputs = {"observations": {"step": "parse", "port": "observations"}}
        params = {"observations_source": parameter("observations_source")}
        if mode == "compare_predictions":
            inputs["expected_results"] = {"source": "{{expected_source}}"}
            params["expected_source"] = parameter("expected_source")
        result["revival-evidence"][mode] = template([parse, step("assess", "evidence.assess_observations", inputs)], "assess", "assessment", params)
    for mode in ("gibson", "pcr"):
        loads = [step("reference", "format.read_fasta", {"file": {"source": "{{reference_source}}"}}, {"topology": "linear", "strandedness": "double"}),
                 step("cargo", "format.read_genbank", {"file": {"source": "{{cargo_source}}"}}, {"strandedness": "double"})]
        inputs = {"reference": {"step": "reference", "port": "material"}, "cargo": {"step": "cargo", "port": "material"}}
        params = {"reference_source": parameter("reference_source"), "cargo_source": parameter("cargo_source")}
        coordinates = {key: "{{" + key + "}}" for key in ("start", "end", "arm_length", "cargo_start", "cargo_end")}
        params.update({key: parameter(key, "integer") for key in coordinates})
        loads.append(step("model", "construct.model_donor", inputs, coordinates))
        build_inputs = dict(inputs)
        build_params = {**coordinates, "preparation_method": mode}
        if mode == "pcr":
            loads.append(step("donor", "format.read_genbank", {"file": {"source": "{{donor_source}}"}}, {"strandedness": "double"}))
            build_inputs["donor_template"] = {"step": "donor", "port": "material"}
            params["donor_source"] = parameter("donor_source")
        else:
            build_params["overlap"] = "{{overlap}}"
            params["overlap"] = parameter("overlap", "integer")
        loads.append(step("build", "construct.design_donor", build_inputs, build_params))
        loads.extend([
            step("cargo_region", "seq.slice", {"material": {"step": "cargo", "port": "material"}}, {"start": "{{cargo_start}}", "end": "{{cargo_end}}"}),
            step("edited", "seq.replace_region", {"material": {"step": "reference", "port": "material"}, "insert": {"step": "cargo_region", "port": "material"}}, {"start": "{{start}}", "end": "{{end}}"}),
            step("qc", "construct.design_junction_assay", {"original": {"step": "reference", "port": "material"}, "edited": {"step": "edited", "port": "product"}, "donor": {"step": "build", "port": "product"}},
                 {"left_arm": "{{left_arm}}", "right_arm": "{{right_arm}}"}),
            step("edited_file", "format.write_genbank", {"material": {"step": "edited", "port": "product"}}, {"name": "edited-reference.gb"}),
            step("handoff", "construct.export_handoff", {"original_file": {"source": "{{reference_source}}"}, "edited_file": {"step": "edited_file", "port": "file"},
                "primers": {"step": "qc", "port": "primers"}}, {"name": "identity-handoff.json"}),
        ])
        for key in ("left_arm", "right_arm"):
            params[key] = {**parameter(key, "array"), "items": INT, "minItems": 2, "maxItems": 2}
        params.update(primers_target=parameter("primers_target"), handoff_target=parameter("handoff_target"))
        prepared = template(loads, "build", "product", params)
        prepared["outputs"].extend([
            {"name": "junction_primers", "from": {"step": "qc", "port": "primers"}, "target": "{{primers_target}}"},
            {"name": "identity_handoff", "from": {"step": "handoff", "port": "handoff"}, "target": "{{handoff_target}}"},
        ])
        result["construct"]["prepare_" + mode] = prepared
    for mode in ("from_references", "from_handoff"):
        loads = [step("original", "format.read_fasta", {"file": {"source": "{{original_source}}"}}, {"topology": "linear", "strandedness": "double"}),
                 step("edited", "format.read_fasta", {"file": {"source": "{{edited_source}}"}}, {"topology": "linear", "strandedness": "double"}),
                 step("forward", "seq.make_material", {"sequence": {"literal": "{{forward_sequence}}"}}, {"strandedness": "single"}),
                 step("reverse", "seq.make_material", {"sequence": {"literal": "{{reverse_sequence}}"}}, {"strandedness": "single"})]
        params = {key: parameter(key) for key in ("original_source", "edited_source", "forward_sequence", "reverse_sequence", "assay_id")}
        if mode == "from_handoff":
            loads.insert(0, step("handoff", "identity.read_handoff", {"file": {"source": "{{handoff_source}}"}}))
            params["handoff_source"] = parameter("handoff_source")
        # Intended typed material collection. Preserve the failure instead of
        # smuggling materials through an untracked JSON value port.
        assay_inputs = {"references": [{"step": "original", "port": "material"}, {"step": "edited", "port": "material"}],
            "forward": {"step": "forward", "port": "material"}, "reverse": {"step": "reverse", "port": "material"}}
        if mode == "from_handoff":
            assay_inputs["handoff"] = {"step": "handoff", "port": "handoff"}
        loads.append(step("assay", "identity.analyze_assay", assay_inputs, {"assay_id": "{{assay_id}}"}))
        result["genome-identity"][mode] = template(loads, "assay", "expected_results", params)
    return result


def source_metadata(source, path, *, supports):
    if isinstance(source, str):
        return {"source_class": "project_contract", "citation": source, "locator": path + "@" + KIT_COMMIT,
                "retrieved_at": "2026-10-16", "content_ref": None, "archive_note": "Local legacy source inspected; this is an implemented scope contract, not biological validation.",
                "supports": [supports], "does_not_support": ["Experimental success or biological function."], "verification_status": "unverified"}
    if source.get("type") == "project_contract":
        citation = source.get("reference", "")
        return {"source_class": "project_contract", "citation": citation, "locator": citation + "@" + KIT_COMMIT,
                "retrieved_at": "2026-10-16", "content_ref": None, "archive_note": "Legacy project-policy citation retained; no current human verification is asserted.",
                "supports": [supports], "does_not_support": ["Sufficient evidence of functional revival or genome-wide elimination."], "verification_status": "unverified"}
    classes = {"manufacturer": "official_method", "peer_reviewed_paper": "literature", "curated_database": "database_record"}
    return {"source_class": classes[source["source_type"]], "citation": source["name"], "locator": source["url"],
            "retrieved_at": source["retrieved_at"], "content_ref": None, "archive_note": "Copied legacy citation, not fetched online. Old verified flags/receipts are not inherited.",
            "supports": [supports], "does_not_support": ["Resistance, expression or compatible selection measured in the user's strain."], "verification_status": "unverified"}


def rule(identity, name, evaluator, parameters, source):
    return {"schema": "rule-v1", "id": identity, "name": name, "version": 1, "status": "draft", "purpose": "interpretation",
            "evaluator": evaluator, "parameters": parameters, "applies_when": [], "source": source,
            "limits": ["Draft with retained provenance; no human review or experimental verification is asserted."], "review": "knowledge/review/" + identity + ".json"}


def knowledge():
    packs, audit = {name: [] for name in KIT_NAMES}, []
    for kit, legacy_name in KIT_NAMES.items():
        kinds = ["scope"] + (["selection"] if kit == "cut-plasmid" else ["conclusions"] if kit == "revival-evidence" else [])
        for kind in kinds:
            path = "genome-revival-toolkit/kits/" + legacy_name + "/rules/" + kind + ".json"
            document = json.loads(old(path))
            for item in document["rules"]:
                audit.append({"kit": kit, "file": path, "commit": KIT_COMMIT, "id": item["id"], "source_present": bool(item.get("source")),
                              "raw_source": deepcopy(item.get("source")), "original": deepcopy(item),
                              "disposition": "retire_conflicts_D7" if item["id"] == "no-template-exemption" else "draft_unverified"})
                if item["id"] == "no-template-exemption":
                    continue
                evaluator = {"cut-plasmid": "cut_plasmid.assess_selection", "revival-evidence": "evidence.assess_observations",
                             "construct": "construct.design_donor", "genome-identity": "identity.analyze_assay"}[kit]
                if kind == "selection":
                    mapping = item["action"]["value"]
                    for host, (plate, source_key) in mapping["hosts"].items():
                        metadata = mapping["sources"][source_key]
                        identity = "selection." + mapping["marker_id"] + "." + host
                        source = source_metadata(metadata, path, supports=host + " selection mapping for " + mapping["marker_id"])
                        value = rule(identity, item["name"] + " / " + host, evaluator,
                                     {"marker_id": mapping["marker_id"], "pattern": mapping["pattern"], "host": host, "plate": plate, "auxotrophy": mapping["auxotrophy"]}, source)
                        value["applies_when"] = [{"field": "marker_id", "op": "eq", "value": mapping["marker_id"]}, {"field": "host", "op": "eq", "value": host}]
                        packs[kit].append(value)
                else:
                    parameters = {key: deepcopy(value) for key, value in item.items() if key not in ("source", "id")}
                    if kind == "conclusions":
                        parameters["state_index"] = deepcopy(document["state_index"])
                    source = source_metadata(item["source"], path, supports=item.get("statement", item.get("reason", "Project scope constraint.")))
                    packs[kit].append(rule(legacy_name + "." + item["id"], item.get("claim", item.get("statement", item["id"])), evaluator, parameters, source))
    path = "genome-revival-toolkit/kits/evidence/scripts/workflow.py"
    packs["revival-evidence"].append(rule("evidence.control-outgrowth", "Retain inactivated-donor control outgrowth contradiction", "evidence.assess_observations",
        {"role": "inactivated_donor_control", "colonies_greater_than": 0, "conclusion": "CONTRADICTED"},
        source_metadata("scripts/workflow.py:run_evidence control-colony branch", path, supports="The legacy assessment policy flags a reported positive inactivated-donor control.")))
    return packs, audit


def shared_for_cap(identity, kit):
    specific = {
        "cut_plasmid.inspect_guide": ["record_from_material", "find_binding_sites"],
        "cut_plasmid.replace_spacer": ["replace_material_region", "enumerate_primer_candidates", "inverse_pcr_material", "sequencing_read_coverage"],
        "cut_plasmid.assess_selection": ["inspect_cds", "record_from_material"],
        "cut_plasmid.model_replace": [],
        "construct.model_donor": ["slice_sequence"],
        "construct.design_donor": ["slice_material", "replace_material_region", "enumerate_primer_candidates", "pcr_material", "gibson_material"],
        "construct.design_junction_assay": ["enumerate_primer_candidates", "predict_pcr_products", "sequencing_read_coverage"],
        "construct.check_junction_assay": ["predict_pcr_products", "find_binding_sites"],
        "identity.compare_regions": ["slice_material"],
        "identity.analyze_assay": ["predict_pcr_products", "find_binding_sites", "enumerate_primer_candidates"],
    }
    return specific.get(identity, [] if kit == "revival-evidence" else ["record_from_material"])


def document(kit, declarations, inventory, rules, audit, template_names):
    title = {"cut-plasmid": "Cut Plasmid", "revival-evidence": "Revival Evidence", "construct": "Construct", "genome-identity": "Genome Identity"}[kit]
    rows = [row for row in inventory if row["kit"] == kit]
    legacy_rules = [row for row in audit if row["kit"] == kit]
    missing = [row["id"] for row in legacy_rules if not row["source_present"]]
    lines = ["# " + title + " 迁移盘点与规格演练", "", "草稿，未实现 Kit 代码，未经人工审核。Kit 工作区和 kits/ 目录未修改。",
             "旧工作区 HEAD 无 kits/；下面的 Kit 源码只读自 Git 对象 " + KIT_COMMIT + "。",
             "通用 Core 源码分别固定提交，不执行或 import 旧程序。模板/声明仅作规格演练，不能据此称为可运行 Kit。", "", "## 旧代码清单", "",
             "| 文件 | 提交 | 文件行数 | 逐函数行数 | 迁移处理 |", "|---|---|---:|---|---|"]
    for row in rows:
        functions = "; ".join(f"{fn['name']} {fn['start']}..{fn['end']} ({fn['lines']}): " +
                              ("丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接" if row["disposition"] == "discard_framework" else function_decision(fn["name"]))
                              for fn in row["functions"]) or "无函数"
        lines.append(f"| `{row['path']}` | `{row['commit']}` | {row['file_lines']} | {functions} | {row['disposition']} |")
    lines += ["", "依据：spec/MIGRATION-MAP.md §6、§7、§8。entry/hooks/presentation/旧运行器与手工埋点丢弃；",
              "workflow 文件只拆取科学判据、局部计算与交接绑定，绝不复制流程外壳。旧源码行数不是规则记录数。", "", "## 新能力表", "",
              "声明文件是完整 capability-v1 草稿。source.implemented_in 是未来目标模块，不存在实现，不作已导出/已运行声明。", "",
              "| id / role / granularity | inputs | params | outputs / output_role | effects | step_checks / final_checks / model | biology 与剩余工作 |",
              "|---|---|---|---|---|---|---|"]
    compact = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    for value in declarations:
        existing = ", ".join(shared_for_cap(value["id"], kit)) or "无共享生物函数；保留领域计算独立性"
        remaining = "；".join(KIT_ONLY[kit])
        lines.append("| `" + value["id"] + "` / " + value["role"] + " / " + value["granularity"] + " | `" + compact(value["inputs"]) + "` | `" + compact(value["params"]) + "` | `" + compact(value["outputs"]) + "` | `" + compact(value["effects"]) + "` | `" + compact({key: value.get(key) for key in ("step_checks", "final_checks", "model")}) + "` | " + existing + "; 仍缺：" + remaining + " |")
    lines += ["", "### 每个能力的 does_not_establish", ""]
    for value in declarations:
        lines.append("- `" + value["id"] + "`: " + "; ".join(value["does_not_establish"]))
    lines += ["", "## 知识与来源", "", f"旧 JSON 规则 {len(legacy_rules)} 条；有来源标记 {len(legacy_rules)-len(missing)}；缺失 {len(missing)}。缺失清单：" + (", ".join(missing) if missing else "无") + "。",
              f"新 rule-v1 草稿 {len(rules)} 条，均为 draft/unverified。旧 verified 标记不继承，没有填写审核人或核验回执。",
              "有来源表示旧数据含可追溯来源，不表示此轮联网核实或科学结论成立。来源分类规范化见 source-audit.json。"]
    lines += ["", "| 旧规则文件 / 提交 | 文件物理行数 | 规则记录数 | 有来源 / 缺来源 |", "|---|---:|---:|---|"]
    for path in sorted({row["file"] for row in legacy_rules}):
        group = [row for row in legacy_rules if row["file"] == path]
        present = sum(row["source_present"] for row in group)
        lines.append(f"| `{path}@{KIT_COMMIT}` | {len(old(path).splitlines())} | {len(group)} | {present} / {len(group)-present} |")
    if kit == "cut-plasmid":
        lines += ["selection.json 是 519 行、9 条 marker 映射；kan 按 ecoli/yeast 两种来源拆分，成为 10 条 marker-host 规则。",
                  "旧 no-template-exemption 与 D7 冲突，保留原记录并退役，不把旧拒绝逻辑原样迁移。"]
    if kit == "revival-evidence":
        lines += ["两条功能/全基因组结论真值表来自旧项目契约；仅支持项目输出边界，不是生物学充分证据。",
                  "另有一条控制组出菌落策略从实际旧代码分支数据化；缺来源探针是新增演练负例，不计入旧规则缺失数。"]
    lines += ["", "| 新规则 | source_class | citation / locator | supports / does_not_support |", "|---|---|---|---|"]
    for value in rules:
        source = value["source"]
        lines.append("| `" + value["id"] + "` | " + source["source_class"] + " | " + source["citation"] + " / " + source["locator"] + " | " + compact({key: source[key] for key in ("supports", "does_not_support")}) + " |")
    lines += ["", "## 模板与构造答案", "", "模板：" + ", ".join("`" + name + ".json`" for name in template_names) + "。",
              "Goal 先登记真实输入文件；模板参数绑定已登记的 source ID、goal_digest 和 target ID，不把文件路径或 DNA 字符串伪装成材料来源。",
              "以下输入与答案在实现前由构造/手算确定，不能用旧版或待测代码生成答案。", "", "## 要写的负例及正对照", "",
              "| 负例 | 输入构造 | 预期来源与结果 |", "|---|---|---|"]
    for name, construction, answer in NEGATIVES[kit]:
        lines.append("| " + name + " | " + construction + " | " + answer + " |")
    constructions = {
        "cut-plasmid": "固定非回文 20 nt spacer；先确定启动子边界、链和后接 scaffold，再构造目标 protospacer+TGG。插反、单碱基 PAM 改动及标注矛盾分别从此控制构造。首版不枚举候选 gRNA，旧排序无区分度问题不带入首版。",
        "construct": "固定种子生成参考，再指定 [100,160) 替换为 90 bp cargo，两侧各 50 bp；供体必须为参考 [50,100)+cargo+参考 [160,210)，长 190 bp。模型与实际 PCR/Gibson 制备路径分开；接口 QC 必须另测残留供体背景。",
        "genome-identity": "先指定唯一 forward 20 nt 与 reverse-reference 20 nt；中间分别构造 960/1260 nt，使总产物为 1000/1300 bp。序列生成器独立检查仅一个完整结合位点；相同长度控制和重复位点控制在调用 Kit 前决定。",
        "revival-evidence": "手写融合组 9、对照组 31 的 CSV；另写空计数与显式 0 两行，并删除 id 表头。结论来自有限真值表与构造的控制状态，不从菌落计数推导功能复活。",
    }
    lines += ["", "合成构造路线：" + constructions[kit]]
    if kit == "construct":
        lines += ["模板已显式连接模型、制备、编辑后参考、接口 QC 和交接导出。当前 S1 stage 仅导出 JSON 文档/值，artifact 最终输出尚待 S1；这是实现依赖，不是 schema 表达失败。"]
    if kit == "genome-identity":
        lines += ["from_handoff 模板把实际读取的交接文档传入分析能力作绑定核对；不只读取后丢弃。预期结果 document 最终由统一封存导出 JSON，交给 Evidence 作为 artifact 登记。"]
    lines += ["", "## 共用函数与 Kit 自有缺口", "", "S1b 已有并可用：" + (", ".join("biology.public." + item for item in SHARED[kit]) if SHARED[kit] else "无 DNA 算法依赖") + "。",
              "本轮新增的四个共享函数均有至少两个 Kit 的明确需求；使用矩阵见 shared-needs.json。",
              *["- 仍交该 Kit 实现：" + item for item in KIT_ONLY[kit]],
              "", "## 规格演练发现", "", "完整原始校验结果由 tools/validate_kit_drafts.py 填入下方；语法通过不等于合同可执行。",
              "<!-- VALIDATION-BEGIN -->", "尚未运行。", "<!-- VALIDATION-END -->", "", "已验证：只读源文件/行数与实际草稿校验范围。模拟：合成负例计划与本轮共享纯函数。",
              "未做：Kit 代码、Kit 端到端、封存/verify、湿实验、观察真实性验证。官方 GitLab CI 未执行；GitHub CI 未运行。", ""]
    return "\n".join(lines)


def main():
    inventory = source_inventory()
    for row in inventory:
        for function in row["functions"]:
            function["decision"] = function_decision(function["name"])
    drafts = capabilities()
    flow = templates()
    rules, audit = knowledge()
    write(DEST / "source-inventory.json", {"source_mode": "read_only_git_objects", "sources": inventory})
    file_stats = []
    for path in sorted({row["file"] for row in audit}):
        group = [row for row in audit if row["file"] == path]
        present = sum(row["source_present"] for row in group)
        file_stats.append({"file": path, "commit": KIT_COMMIT, "physical_lines": len(old(path).splitlines()), "rule_records": len(group),
                           "source_present": present, "source_missing": len(group)-present})
    write(DEST / "source-audit.json", {"files": file_stats, "legacy_rows": audit, "legacy_total": len(audit), "legacy_source_present": sum(row["source_present"] for row in audit),
                                       "legacy_source_missing": [row["id"] for row in audit if not row["source_present"]]})
    needs = {"replace_material_region": ["cut-plasmid", "construct"], "inspect_cds": ["cut-plasmid", "construct"],
             "enumerate_primer_candidates": ["cut-plasmid", "construct", "genome-identity"], "sequencing_read_coverage": ["cut-plasmid", "construct"]}
    write(DEST / "shared-needs.json", {"implemented_shared": needs, "kit_only": KIT_ONLY})
    for kit, values in drafts.items():
        folder = DEST / "drafts" / kit
        contributions = {"capabilities": [], "knowledge": [], "templates": [], "text": ["text/en.json"]}
        for value in values:
            name = value["id"].rsplit(".", 1)[1]
            path = "capabilities/" + name + ".json"
            contributions["capabilities"].append(path)
            write(folder / path, value)
            if value["role"] == "CHECK":
                constructions = {
                    "cut_plasmid.check_direction": ("Actual spacer matches the unique target followed by TGG, with the declared transcription strand.", "Use the nonpalindromic spacer reverse complement in the vector while leaving forward annotation."),
                    "cut_plasmid.check_pam": ("Exact selected protospacer is followed by TGG.", "Same protospacer is followed by TGA, one PAM base changed."),
                    "cut_plasmid.check_vector_self_target": ("Selected cassette is followed by GTT scaffold and contains no extra spacer+NGG copy.", "Append an extra exact spacer+TGG copy to the same supplied vector."),
                    "evidence.check_record_consistency": ("Unique sample ids, known count 9 and explicit control zero, no contradictory genotype rows.", "Submit both positive and negative results for one sample/reference under reported passing controls."),
                    "construct.check_junction_assay": ("One primer lies outside the donor's retained homology arm, giving no residual-donor product.", "Both primers lie inside retained donor arms, so the residual donor gives the same band."),
                    "identity.check_handoff": ("Reference file bytes are unchanged after computing the handoff binding.", "Append one byte after computing the original handoff binding; recomputed hash differs."),
                }
                for variant, path in value["fixtures"].items():
                    write(folder / path, {"check": value["id"], "variant": variant, "expected": "PASS" if variant == "pass" else "FAIL",
                        "oracle": {"kind": "construction", "reason": "Future Kit fixture: select a paired synthetic construction from the migration report; not executed in this rehearsal."},
                        "data": {"construction": constructions[value["id"]][0 if variant == "pass" else 1]}})
        for value in rules[kit]:
            path = "knowledge/" + value["id"] + ".json"
            contributions["knowledge"].append(path)
            write(folder / path, value)
        for name, value in flow[kit].items():
            path = "templates/" + name + ".json"
            contributions["templates"].append(path)
            write(folder / path, value)
        write(folder / "text/en.json", {"draft_notice": "Schema rehearsal only. No Kit implementation, experimental result or human review."})
        manifest = {"schema": "kit-v1", "name": kit, "version": VERSIONS["kits"][kit], "title": kit.replace("-", " ").title(),
                    "requires_core": {"minimum": VERSIONS["core"], "maximum_exclusive": "1.0.0"}, "contributes": contributions,
                    "does_not_establish": values[0]["does_not_establish"], "review": "knowledge/review/"}
        write(folder / "kit.json", manifest)
        write(DEST / (kit + ".md"), document(kit, values, inventory, rules[kit], audit, flow[kit]))
    missing = rule("probe.missing-source", "Constructed rule with intentionally missing source", "evidence.assess_observations", {}, {"verification_status": "unverified"})
    write(DEST / "drafts/revival-evidence/probes/source-missing.json", missing)
    partial = deepcopy(flow["revival-evidence"]["observations_only"])
    partial["outputs"][0]["name"] = "assessment-{{target_id}}"
    write(DEST / "drafts/revival-evidence/probes/partial-placeholder.json", partial)
    write(DEST / "rehearsal-index.json", {"expected_invalid_probes": {
        "drafts/revival-evidence/probes/source-missing.json": "rule-v1", "drafts/revival-evidence/probes/partial-placeholder.json": "pipeline-template-v1"},
        "issue_map": {"document_schema": "K1", "source_quarantine": "K2", "material_collection": "K3", "model_binding": "K4", "handoff_shape": "K5", "action_knowledge_access": "K6"},
        "knowledge_consumers": ["cut_plasmid.assess_selection", "evidence.assess_observations"],
        "handoff_authority": "prompts/s5b-genome-identity.md; old schema_version/references-dict/rows protocol is not the new contract"})
    print(json.dumps({"kit_reports": len(drafts), "capability_drafts": sum(map(len, drafts.values())), "rule_drafts": sum(map(len, rules.values())),
                      "templates": sum(map(len, flow.values())), "legacy_rule_rows": len(audit), "legacy_missing_source_rows": sum(not row["source_present"] for row in audit)}))


if __name__ == "__main__":
    main()
