"""Construct tests use the public API and real Invoker/ReadView, never fake ctx."""
from copy import deepcopy
import json
from pathlib import Path

from dna_design_core.application.api import call
from dna_design_core.application.run_service import RunService
from dna_design_core.kernel.public import core_version

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "kits/construct"
CASE = json.loads((KIT / "examples/case.json").read_text(encoding="utf-8"))


def required(receipt):
    if receipt["problems"]:
        raise AssertionError(receipt)
    return receipt["result"]


def create(directory, method="gibson", *, kit_dirs=(), modify_plan=None, sequences=None, primers=None, outputs="full", execute=True, dispatch=None):
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ("reference", "cargo", "donor-template"):
        sequence = (sequences or {}).get(name)
        text = (KIT / "examples" / (name + ".fasta")).read_text(encoding="utf-8") if sequence is None else ">synthetic\n" + sequence + "\n"
        files[name] = folder / (name + ".fasta")
        files[name].write_text(text, encoding="utf-8", newline="\n")
    sources = [{"source_id": "input_" + name.replace("-", "_"), "from": str(path), "input_origin": "user_file", "as": "artifact", "declared": {}}
               for name, path in files.items() if method == "pcr" or name != "donor-template"]
    if primers is not None:
        path = folder / "supplied-primers.json"
        path.write_text(json.dumps(primers), encoding="utf-8")
        sources.append({"source_id": "supplied_primers", "from": str(path), "input_origin": "user_file", "as": "artifact", "declared": {}})
    run = folder / "run"
    receipts = []
    def invoke(verb, **options):
        value = (dispatch or call)(verb, root=run, kit_dirs=kit_dirs, **options)
        receipts.append({"verb": verb, "receipt": value})
        return value
    required(invoke("run create", directory=run))
    targets = [{"id": name, "role": role, "required": True} for name, role in (
        ("donor", "construct"), ("primers", "primer_set"), ("assay", "analysis"), ("handoff", "analysis"))]
    if outputs == "diagnostic":
        # Separate diagnostic run: keep all construct/preparation obligations.
        targets = [row for row in targets if row["id"] != "handoff"]
    goal = required(invoke("goal declare", request={"schema": "goal-v1", "version": 1, "parent_digest": None,
        "original_request": "Replace the selected gene with the supplied cassette and retain both 50 bp homology arms.",
        "sources": sources, "declared_context": [], "targets": targets,
        "constraints": [{"id": "exact", "check": "check.goal.exact_sequence@" + core_version(), "params": {"sequence": CASE["expected_donor"]},
                         "target": "donor", "source_quote": "", "status": "active"}], "intents": []}))
    parameters = {**CASE["parameters"], **CASE[method], "goal_digest": goal["goal_digest"], "reference_source": "input_reference",
        "cargo_source": "input_cargo", "donor_target": "donor", "primers_target": "primers", "assay_target": "assay", "handoff_target": "handoff"}
    if method == "pcr":
        parameters["donor_template_source"] = "input_donor_template"
    instantiated = required(invoke("template instantiate", name="construct.prepare_" + method, request=parameters))
    plan = deepcopy(instantiated["draft"])
    if primers is not None:
        next(row for row in plan["steps"] if row["step_id"] == "assay")["inputs"]["primer_file"] = {"source": "supplied_primers"}
    if outputs == "diagnostic":
        plan["outputs"] = [row for row in plan["outputs"] if row["target"] != "handoff"]
    if modify_plan:
        modify_plan(plan)
    required(invoke("pipeline submit", request=plan))
    result = invoke("run execute") if execute else None
    return RunService(run, kit_dirs=kit_dirs), receipts, result


def retained(service, step="design"):
    completed = service.session.steps()[step]["completed"]["payload"]["outputs"]
    return {"materials": {name: [service.session.store.get("materials", identity) for identity in identities]
                          for name, identities in completed["materials"].items()},
            "documents": {name: service.session.store.get("documents", identities[0]) for name, identities in completed["documents"].items()},
            "artifacts": completed["artifacts"]}


def checked(service, identity):
    candidate = {"moment": "final", "issuer": "check_capability", "catalog": service.session.snapshot(), "outputs": []}
    return service.invoker.invoke(identity, {}, {}, parent="final", view=service.view(candidate)).verdicts[0]
