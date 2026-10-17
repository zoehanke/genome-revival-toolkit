"""Kit-owned document schemas, embedded in exported capability declarations."""


def object_schema(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required, "additionalProperties": False}


TEXT = {"type": "string", "minLength": 1}
STRINGS = {"type": "array", "items": {"type": "string"}}
COUNT = {"type": ["integer", "null"], "minimum": 0}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
NULLABLE_HASH = {"type": ["string", "null"], "pattern": "^[0-9a-f]{64}$"}
NULLABLE_TEXT = {"type": ["string", "null"]}
STATES = {"enum": ["SUPPORTED", "INSUFFICIENT", "CONTRADICTED", "NOT_TESTED"]}

ASSAY = object_schema({
    "sample_id": TEXT, "assay_id": TEXT, "background_id": TEXT, "reference_sha256": HASH,
    "result": {"enum": ["positive", "negative", "indeterminate", "not_tested"]},
    "control_status": {"enum": ["passed", "failed", "unknown"]},
    "observed_band_bp": COUNT, "band_tolerance_bp": {"type": "integer", "minimum": 0}},
    ["sample_id", "assay_id", "background_id", "result"])
FUNCTION = object_schema({"sample_id": TEXT, "result": ASSAY["properties"]["result"]})
RECORDS = object_schema({
    "observations": {"type": "array", "items": {"type": "object"}},
    "genotype_results": {"type": "array", "items": ASSAY},
    "functional_results": {"type": "array", "items": FUNCTION}, "observation_origin": TEXT}, ["observations"])

EXPECTED = object_schema({
    "status": {"enum": ["DISTINGUISHABLE", "NOT_DISTINGUISHABLE", "UNDETERMINED"]},
    "product_count": {"type": "integer", "minimum": 0},
    "product_bp": {"type": ["integer", "null"], "minimum": 1}})
EXPECTED["allOf"] = [{
    "if": {"properties": {"product_count": {"const": 1}}, "required": ["product_count"]},
    "then": {"properties": {"product_bp": {"type": "integer", "minimum": 1}}},
    "else": {"properties": {"product_bp": {"type": "null"}}}}]
PREDICTIONS = object_schema({
    "schema": {"const": "identity-expected-results-v1"}, "assay_id": TEXT,
    "backgrounds": {"type": "array", "minItems": 1, "items": object_schema({
        "id": TEXT, "reference_sha256": HASH,
        "primer_pair": {"type": "array", "minItems": 2, "maxItems": 2, "items": TEXT},
        "expected": EXPECTED})}})

GENERATED_IDS = {"type": "array", "items": object_schema({
    "row": {"type": "integer", "minimum": 1}, "id": TEXT})}
INPUT_FILES = object_schema({"observations_sha256": HASH, "predictions_sha256": NULLABLE_HASH})
NORMALIZED_ASSAY = {**ASSAY, "required": [name for name in ASSAY["properties"] if name != "reference_sha256"]}
OBSERVATIONS_DOCUMENT = object_schema({
    "observations": {"type": "array", "items": object_schema({
        "id": TEXT, "group": TEXT, "colonies": COUNT, "plated_cells": COUNT,
        "plated_volume_uL": NULLABLE_TEXT, "unit": NULLABLE_TEXT, "role": NULLABLE_TEXT})},
    "genotype_results": {"type": "array", "items": NORMALIZED_ASSAY},
    "functional_results": {"type": "array", "items": FUNCTION}, "observation_origin": TEXT,
    "predictions": {"anyOf": [{"type": "null"}, PREDICTIONS]},
    "generated_ids": GENERATED_IDS, "input_files": INPUT_FILES, "unverified": STRINGS})

CONCLUSION = object_schema({
    "claim": TEXT, "subject": object_schema({"sample_id": NULLABLE_TEXT,
        "assay_id": TEXT, "background_id": TEXT,
        "experiment_group": TEXT, "control_group": TEXT}, []), "status": STATES,
    "applicability": {"enum": ["PASS", "UNKNOWN"]}, "reason": TEXT, "rule_ref": HASH})
ASSESSMENT_DOCUMENT = object_schema({
    "conclusions": {"type": "array", "minItems": 1, "items": CONCLUSION},
    "groups": {"type": "array", "items": object_schema({
        "group": TEXT, "sample_ids": STRINGS, "colonies": COUNT,
        "record_count": {"type": "integer", "minimum": 1}, "units": STRINGS})},
    "comparisons": {"type": "array", "items": object_schema({
        "experiment_group": TEXT, "control_group": TEXT,
        "experiment_colonies": COUNT, "control_colonies": COUNT,
        "difference": {"type": ["integer", "null"]}, "outcome": {"enum": ["PASS", "UNKNOWN"]},
        "equal_reported_plated_volumes": {"type": "boolean"}, "limits": STRINGS})},
    "genotype_tests": STATES, "functional_tests": STATES, "observation_origin": TEXT,
    "rule_refs": {"type": "array", "items": HASH}, "input_files": INPUT_FILES,
    "generated_ids": GENERATED_IDS, "unverified": STRINGS, "limits": STRINGS})
