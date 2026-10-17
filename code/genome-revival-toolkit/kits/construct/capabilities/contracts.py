"""Strict Kit-local declarations and document shapes; no registry or execution."""
from copy import deepcopy

from dna_design_core.kernel.public import core_version

LIMITS = ["Successful laboratory donor preparation", "Transformation efficiency",
          "Authentic integration locus", "Functional revival"]
DNA = {"type": "string", "pattern": "^[ACGT]+$"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
INTEGER = {"type": "integer", "minimum": 0}
BOUNDS = {"start": INTEGER, "end": INTEGER, "arm_length": {"type": "integer", "minimum": 1},
          "cargo_start": INTEGER, "cargo_end": INTEGER}


def obj(properties: dict, required: list | None = None) -> dict:
    return {"type": "object", "properties": deepcopy(properties),
            "required": list(properties) if required is None else required, "additionalProperties": False}


def array(items: dict, minimum: int = 0) -> dict:
    return {"type": "array", "items": deepcopy(items), "minItems": minimum}


# PROVISIONAL(S5A-P1): Kit-owned document fields, frozen inline with declarations.
PRIMER_ROW = obj({"id": {"type": "string"}, "sequence": DNA,
                  "core_length": {"type": "integer", "minimum": 1}, "purpose": {"type": "string"}})
PAIR = obj({"id": {"type": "string"}, "forward": {"type": "string"}, "reverse": {"type": "string"}})
PRIMERS = obj({"schema": {"const": "primer-set-v1"}, "primers": array(PRIMER_ROW, 2), "pairs": array(PAIR, 1)})
REACTION = obj({"id": {"type": "string"}, "method": {"enum": ["pcr", "gibson"]},
                "inputs": array(HASH, 2), "params": {"type": "object"}, "product_id": HASH})
ROUTE = obj({"schema": {"const": "route-plan-v1"}, "method": {"enum": ["gibson", "pcr"]},
             "laboratory_status": {"const": "NOT_PERFORMED"}, "parameters": obj(BOUNDS),
             "reference_id": HASH, "cargo_id": HASH, "reactions": array(REACTION, 1)})
REGION = obj({"id": {"type": "string"}, "reference_id": {"type": "string"}, "start": INTEGER, "end": INTEGER})
PREDICTION = obj({"pair_id": {"type": "string"}, "product_count": INTEGER,
                  "product_bp": {"type": ["integer", "null"], "minimum": 1},
                  "forward_sites": INTEGER, "reverse_sites": INTEGER})
ASSAY = obj({"schema": {"const": "junction-assay-v1"}, "original_id": HASH, "edited_id": HASH, "donor_id": HASH,
             "primers": PRIMERS, "regions": array(REGION, 1),
             "backgrounds": array(obj({"id": {"enum": ["original", "edited", "donor"]},
                                       "predictions": array(PREDICTION, 1)}), 3),
             "warnings": array({"type": "string"})})
HANDOFF = obj({"schema": {"const": "identity-handoff-v1"},
               "references": array(obj({"id": {"type": "string"}, "sha256": HASH,
                                         "role": {"enum": ["original", "edited"]}}), 2),
               "regions": array(REGION, 1),
               "primers": array(obj({"id": {"type": "string"}, "sequence": DNA}), 2)})


def port(name: str, kind: str = "material", *, schema: dict | None = None,
         required: bool = True, output_role: str | None = None, output: bool = False) -> dict:
    value = {"name": name, "type": kind}
    if output:
        value["output_role"] = output_role
    else:
        value.update(required=required, constraints={}, description=name.replace("_", " "))
    if schema is not None:
        value["schema"] = deepcopy(schema)
    return value


def declaration(identity: str, module: str, function: str, summary: str, inputs: list,
                outputs: list, properties: dict, required: list | None = None, *,
                effects: tuple = ("pure",), composite: bool = False, model: str | None = None,
                checks: tuple = (), scope: str | None = None) -> dict:
    value = {"schema": "capability-v1", "id": identity, "version": core_version(),
             "role": "CHECK" if scope else "ACTION", "summary": summary, "effects": list(effects),
             "deterministic": True, "requires_runtime": [{"kind": "python_package", "name": "biopython", "probe": None}],
             "inputs": inputs, "params": obj(properties, required), "outputs": outputs,
             "step_checks": [], "final_checks": [{"check": name} for name in checks],
             "does_not_establish": LIMITS, "source": {"algorithm_refs": ["spec/SPEC.md D3 D7 D11", "MIGRATION-LOG.md: S5a"],
             "implemented_in": module + ":" + function}, "owner": "kit:construct",
             "granularity": "composite" if composite else "atomic"}
    if model:
        value["model"] = model
    if scope:
        value.update(scope=scope, evaluates_constraint=False, offline=True,
                     fixtures={kind: "capabilities/fixtures/" + identity + "." + kind + ".json" for kind in ("pass", "fail")})
    return value
