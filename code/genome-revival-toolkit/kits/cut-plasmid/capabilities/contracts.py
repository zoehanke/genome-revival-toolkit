"""Kit-owned inline contracts; declarations are exported from decorated functions."""
import json
from pathlib import Path

VERSION = json.loads((Path(__file__).resolve().parents[1] / "kit.json").read_text(encoding="utf-8"))["version"]
LIMITATIONS = ["Cleavage activity", "Editing efficiency", "Genome-wide off-target safety"]


def obj(properties, required=None):
    return {"type": "object", "properties": properties, "required": list(properties) if required is None else required,
            "additionalProperties": False}


def array(items):
    return {"type": "array", "items": items}


TEXT = {"type": "string"}
INT = {"type": "integer"}
BOOL = {"type": "boolean"}
DNA = {"type": "string", "pattern": "^[ACGT]+$"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
CASSETTE_PARAMS = {
    "promoter_end": {"type": "integer", "minimum": 0},
    "transcription_strand": {"type": "integer", "enum": [-1, 1]},
    "scaffold_sequence": {"type": "string", "pattern": "^[ACGT]{3,200}$"},
}
VECTOR_SEARCH = {"vector_max_mismatches": {"type": "integer", "minimum": 0, "maximum": 3}}
SPACER = {"type": "string", "pattern": "^[ACGT]{20}$"}
# PROVISIONAL(S2-Q2): explicit B2 concentrations, not a new shared Tm contract.
TM_INPUT = obj({"dnac1_nM": TEXT, "dnac2_nM": TEXT, "Na_mM": TEXT, "K_mM": TEXT,
                "Tris_mM": TEXT, "Mg_mM": TEXT, "dNTPs_mM": TEXT,
                "nn_table": {"const": "DNA_NN3"}, "saltcorr": {"const": 5}, "selfcomp": BOOL})
DESIGN_PARAMS = {
    "length_min": {"type": "integer", "minimum": 2},
    "length_max": {"type": "integer", "minimum": 2},
    "tm_min": TEXT, "tm_max": TEXT, "tm_parameters": TM_INPUT,
}
DEFAULT_TM = {"dnac1_nM": "250", "dnac2_nM": "0", "Na_mM": "50", "K_mM": "0",
              "Tris_mM": "0", "Mg_mM": "0", "dNTPs_mM": "0",
              "nn_table": "DNA_NN3", "saltcorr": 5, "selfcomp": False}
PART = array({"type": "integer", "minimum": 0})
FINDING = obj({"code": TEXT, "feature_index": INT, "annotation_strand": {"type": ["integer", "null"]},
               "sequence_transcription_strand": INT})
HIT = obj({"strand": INT, "rna_binding_strand": INT, "start": INT,
           "parts": array(PART), "pam": TEXT, "pam_valid": BOOL, "locus": TEXT})
SELF_HIT = obj({**HIT["properties"], "mismatches": INT})
GUIDE = obj({"schema": {"const": "guide-inspection-v1"}, "vector_id": HASH, "target_id": HASH,
             "promoter_end": INT, "transcription_strand": INT, "spacer": SPACER,
             "spacer_parts": array(PART), "scaffold_sequence": DNA,
             "pam_valid": BOOL, "direction_status": TEXT,
             "direction_correct": {"type": ["boolean", "null"]},
             "orientation_distinguishable": BOOL, "target_matches": array(HIT),
             "reverse_insert_hypotheses": array(HIT), "valid_target_locus_count": INT,
             "vector_self_targets": array(SELF_HIT), "vector_max_mismatches": INT, "vector_search_complete": BOOL,
             "annotation_findings": array(FINDING),
             "warnings": array(TEXT)})
PRIMER = obj({"id": TEXT, "sequence": DNA, "binding_core": DNA, "tail_5prime": TEXT,
              "core_length": INT, "length": INT, "strand": INT,
              "reference_start": INT, "reference_end_unwrapped": INT,
              "binding_site_count": INT, "tm_degC": TEXT})
PRIMERS = obj({"schema": {"const": "primer-set-v1"}, "template_id": HASH,
               "primers": array(PRIMER), "length_min": INT, "length_max": INT,
               "tm_min": TEXT, "tm_max": TEXT, "tm_parameters": TM_INPUT,
               "quality_notes": array(TEXT)})
ROUTE = obj({"schema": {"const": "route-plan-v1"}, "method": {"const": "inverse_pcr"},
             "template_id": HASH, "product_id": HASH, "spacer_parts": array(PART),
             "transcription_strand": INT, "reference_insert": SPACER,
             "forward_primer_id": TEXT, "reverse_primer_id": TEXT,
             "closing_overlap": {"const": 0}, "rotation_to_template_origin": INT,
             "simulation": obj({"status": {"const": "PASS"}, "linear_sequence": DNA,
                                "product_length": INT, "circular_sequence_matches": BOOL}),
             "annotation_changes": array(obj({"index": INT, "type": TEXT, "reason": TEXT})),
             "laboratory_steps": array(obj({"step": TEXT, "status": {"const": "PLANNED"},
                                             "performed": {"const": "NOT_PERFORMED"}}))})
GENOTYPE = obj({"description": TEXT, "organism": TEXT, "existing_markers": array(TEXT),
                "auxotrophies": array(TEXT)}, [])
GENOTYPE["type"] = ["object", "null"]
OPTION = obj({"host": TEXT, "plate": TEXT, "rule_id": TEXT, "rule_digest": HASH,
              "source_locator": TEXT, "compatibility": TEXT, "reason": TEXT})
MARKER = obj({"feature_index": INT, "name": TEXT, "marker_id": TEXT,
              "compatibility": TEXT, "reason": TEXT, "plate_options": array(OPTION)})
SELECTION = obj({"schema": {"const": "selection-assessment-v1"}, "claim": {"const": "selection"}, "status": TEXT,
                 "markers": array(MARKER), "annotation_conflicts": array(INT),
                 "unmapped_markers": array(INT), "genotype_source": TEXT,
                 "recipient_host": {"type": ["string", "null"]}, "message": TEXT,
                 "knowledge_digest": HASH, "draft_rows_loaded": {"const": 0}})


def material_port(name, required=True):
    return {"name": name, "type": "material", "required": required, "constraints": {}, "description": name}


def output(name, kind, role=None, schema=None):
    result = {"name": name, "type": kind, "output_role": role}
    if schema is not None:
        result["schema"] = schema
    return result


def declaration(name, module, function, inputs, outputs, parameters, *, required=None, composite=False,
                scope=None, model=None, final_checks=(), step_checks=()):
    identity = "cut_plasmid." + name
    value = {"schema": "capability-v1", "id": identity, "version": VERSION,
             "role": "CHECK" if scope else "ACTION", "summary": function.replace("_", " ").capitalize() + ".",
             "effects": ["reads_files"] if scope or name == "assess_selection" else ["pure"],
             "deterministic": True, "requires_runtime": [{"kind": "python_package", "name": "biopython", "probe": None}],
             "inputs": inputs, "outputs": outputs, "params": obj(parameters, required),
             "step_checks": list(step_checks), "final_checks": [{"check": check} for check in final_checks],
             "does_not_establish": LIMITATIONS + ["Experimental PCR, transformation or phenotype."],
             "source": {"algorithm_refs": ["spec/SPEC.md D3 D7 D11 B2", "MIGRATION-LOG.md S2"],
                        "implemented_in": "grt_kit_cut_plasmid.capabilities." + module + ":" + function},
             "owner": "kit:cut-plasmid", "granularity": "composite" if composite else "atomic",
             "authorship": {"kind": "ai", "tool_or_model": "Codex", "date": "2026-10-17"}}
    if model:
        value["model"] = model
    if scope:
        value.update(scope=scope, evaluates_constraint=False, offline=True,
                     fixtures={"pass": "capabilities/fixtures/" + name + ".pass.json",
                               "fail": "capabilities/fixtures/" + name + ".fail.json"})
    return value


FINAL_CHECKS = ["cut_plasmid.check_direction", "cut_plasmid.check_pam", "cut_plasmid.check_vector_self_target"]
