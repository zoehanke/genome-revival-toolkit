"""Metadata and safe argument adapters shared by the S1b thin capabilities."""
from functools import wraps

from dna_design_core.kernel.public import ToolkitError
from ..declaration import action, check


JSON_VALUE = "urn:grt:schema:goal-v1#/$defs/value"


def port(name: str, kind: str = "material", *, required: bool = True) -> dict:
    value = {"name": name, "type": kind, "required": required, "constraints": {}, "description": name.replace("_", " ")}
    if kind == "document":
        value["schema_ref"] = JSON_VALUE
    return value


def output(name: str, kind: str = "material", role: str | None = "component") -> dict:
    value = {"name": name, "type": kind, "output_role": role}
    if kind == "document":
        value["schema_ref"] = JSON_VALUE
    return value


def declaration(identity: str, summary: str, module: str, function: str, inputs: list, outputs: list,
                properties: dict | None = None, required: tuple = (), *, effects: tuple = ("pure",),
                final_checks: tuple = (), scope: str | None = None, offline: bool = True) -> dict:
    implementation = module + ":" + function
    if scope is None:
        value = action(identity, summary, implementation, inputs, outputs, effects=effects, final_checks=final_checks)
    else:
        value = check(identity, scope, implementation, summary)
        value.update(inputs=inputs, effects=list(effects), offline=offline,
                     fixtures={kind: f"tests/fixtures/biology/checks/{identity}.{kind}.json" for kind in ("pass", "fail")})
    value["params"] = {"type": "object", "properties": properties or {}, "required": list(required), "additionalProperties": False}
    value["requires_runtime"] = [{"kind": "python_package", "name": "biopython", "probe": None}]
    value["does_not_establish"] = ["Wet-laboratory success, biological function or reaction efficiency.",
                                    "Genome-wide safety or thermodynamic structure quality unless explicitly measured."]
    value["source"]["algorithm_refs"] = ["spec/MIGRATION-MAP.md: batches 1-4", "MIGRATION-LOG.md"]
    return value


def input_errors(function):
    """Normalize ordinary invalid biological parameters at the capability boundary."""
    @wraps(function)
    def invoke(*arguments, **parameters):
        try:
            return function(*arguments, **parameters)
        except (ValueError, TypeError, KeyError, IndexError) as error:
            raise ToolkitError("PLAN_PARAM_INVALID", "Biological input or parameter is invalid.",
                               {"reason": str(error)}) from error
    return invoke


def optional_integer() -> dict:
    return {"type": ["integer", "null"], "minimum": 1}


def concentration_properties() -> dict:
    return {name: {"type": "string", "pattern": r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$"}
            for name in ("sodium_mM", "magnesium_mM", "dntp_mM", "total_oligo_nM")}
