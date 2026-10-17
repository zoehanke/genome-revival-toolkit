# ported-from: genome-revival-toolkit/revival/evidence.py@750bf4849b818be00f28684513ef19c01d901bcb
"""Normalize submitted counts and local assay records without authenticating them."""
import csv
from decimal import Decimal, InvalidOperation
from io import StringIO
from pathlib import Path

from dna_design_core.kernel.public import ToolkitError, file_sha256, loads, require_schema
from .contract import ASSAY, RECORDS, PREDICTIONS


def count(value, field):
    """Omission remains None; Decimal avoids float rounding of submitted counts."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ToolkitError("PLAN_PARAM_INVALID", field + " must be a nonnegative integer or omitted.")
    try:
        number = Decimal(str(value))
        valid = number.is_finite() and number >= 0 and number == number.to_integral_value()
    except InvalidOperation:
        valid = False
    if not valid:
        raise ToolkitError("PLAN_PARAM_INVALID", field + " must be a nonnegative integer or omitted.")
    return int(number)


def normalize_rows(rows):
    present = [row.get("id") for row in rows if row.get("id")]
    if any(not isinstance(value, str) or not value.strip() for value in present) or len(set(present)) != len(present):
        raise ToolkitError("PLAN_PARAM_INVALID", "Observation IDs must be nonempty and unique when supplied.")
    used = set(present)
    normalized, generated = [], []
    for index, row in enumerate(rows, 1):
        if not isinstance(row.get("group"), str) or not row["group"].strip():
            raise ToolkitError("PLAN_PARAM_INVALID", "Each count observation needs a group.")
        identity = row.get("id")
        if not identity:
            identity = "row_" + str(index)
            while identity in used:
                identity += "_auto"
            used.add(identity)
            generated.append({"row": index, "id": identity})
        if "colonies" not in row and row.get("measure") != "colony_count":
            raise ToolkitError("PLAN_PARAM_INVALID", "Use colonies, or measure=colony_count and value.")
        raw = row.get("colonies") if "colonies" in row else row.get("value")
        if "colonies" in row and "value" in row and count(raw, "colonies") != count(row["value"], "value"):
            raise ToolkitError("PLAN_PARAM_INVALID", "Count columns disagree.")
        volume = row.get("plated_volume_uL")
        if volume not in (None, ""):
            try:
                decimal = Decimal(str(volume))
                if not decimal.is_finite() or decimal <= 0:
                    raise InvalidOperation
                volume = format(decimal.normalize(), "f")
            except InvalidOperation as error:
                raise ToolkitError("PLAN_PARAM_INVALID", "plated_volume_uL must be positive or omitted.") from error
        else:
            volume = None
        normalized.append({"id": identity, "group": row["group"], "colonies": count(raw, "colonies"),
                           "plated_cells": count(row.get("plated_cells"), "plated_cells"),
                           "plated_volume_uL": volume, "unit": row.get("unit") or None,
                           "role": row.get("role") or None})
    return normalized, generated


def read_records(path, predictions=None, observation_origin="Submitted observation; authenticity unverified."):
    raw = Path(path).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
        if text.lstrip().startswith("{"):
            value = loads(text.encode("utf-8"))
        else:
            reader = csv.DictReader(StringIO(text))
            if not reader.fieldnames or "group" not in reader.fieldnames or not (
                    "colonies" in reader.fieldnames or {"measure", "value"} <= set(reader.fieldnames)):
                raise ToolkitError("PLAN_PARAM_INVALID", "Observation CSV needs group and colonies, or group,measure,value.")
            value = {"observations": list(reader)}
        try:
            require_schema(RECORDS, value, "PLAN_PARAM_INVALID")
        except ToolkitError as error:
            if any(finding.get("rule") == "enum"
                   and finding.get("location", "").startswith("/genotype_results/")
                   and finding.get("location", "").endswith("/control_status")
                   for finding in error.problem.details.get("findings", [])):
                choices = ", ".join(ASSAY["properties"]["control_status"]["enum"])
                raise ToolkitError(error.problem.code, "control_status must be one of: " + choices + ".",
                                   error.problem.details) from error
            raise
        observations, generated = normalize_rows(value["observations"])
    except (UnicodeError, csv.Error) as error:
        raise ToolkitError("PLAN_PARAM_INVALID", "Read observations as UTF-8 CSV or JSON.") from error
    genotypes = []
    seen = set()
    for row in value.get("genotype_results", []):
        key = (row["sample_id"], row["assay_id"], row["background_id"])
        if key in seen:
            raise ToolkitError("PLAN_PARAM_INVALID", "Keep one result per sample, assay and background; reconcile conflicting reports explicitly.")
        seen.add(key)
        band = row.get("observed_band_bp")
        if row["result"] != "positive" and band is not None or band == 0:
            raise ToolkitError("PLAN_PARAM_INVALID", "Only a positive band can have a positive observed_band_bp.")
        genotypes.append({**row, "control_status": row.get("control_status", "unknown"),
                          "observed_band_bp": band, "band_tolerance_bp": row.get("band_tolerance_bp", 0)})
    model, model_hash = None, None
    if predictions is not None:
        data = Path(predictions).read_bytes()
        model = loads(data)
        require_schema(PREDICTIONS, model, "PLAN_PARAM_INVALID")
        names = [row["id"] for row in model["backgrounds"]]
        if len(set(names)) != len(names):
            raise ToolkitError("PLAN_PARAM_INVALID", "Expected-result background IDs must be unique.")
        model_hash = file_sha256(data)
    unverified = ["Observation authenticity and experimental conditions were not independently measured."]
    unverified.extend("Generated observation ID " + item["id"] + " for data row " + str(item["row"]) + "." for item in generated)
    if any(row["unit"] is None for row in observations):
        unverified.append("Count unit was omitted; affected count comparisons are UNKNOWN.")
    return {"observations": observations, "genotype_results": genotypes,
            "functional_results": value.get("functional_results", []),
            "observation_origin": value.get("observation_origin", observation_origin),
            "predictions": model, "generated_ids": generated,
            "input_files": {"observations_sha256": file_sha256(raw), "predictions_sha256": model_hash},
            "unverified": unverified}
