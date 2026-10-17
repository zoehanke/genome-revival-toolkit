"""S2 synthetic material construction and actual Core runtime, never a fake ctx."""
from copy import deepcopy
import json
from pathlib import Path
import sys

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqFeature import CompoundLocation, SeqFeature, SimpleLocation
from Bio.SeqRecord import SeqRecord

from dna_design_core.application.run_service import RunService
from dna_design_core.engine.executor import execute

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "kits/cut-plasmid"


def b2():
    return json.loads((KIT / "examples/b2.json").read_text(encoding="utf-8"))


def write_material(path, value):
    """Independent Biopython input construction, not a production adapter."""
    record = SeqRecord(Seq(value["sequence"]), id=path.stem, name=path.stem, description="Synthetic S2 test input")
    record.annotations.update(molecule_type="DNA", topology=value["topology"])
    for feature in value["features"]:
        parts = feature.get("parts") or [{"start": feature["start"], "end": feature["end"], "strand": feature.get("strand", 1)}]
        locations = [SimpleLocation(part["start"], part["end"], strand=part.get("strand")) for part in parts]
        qualifiers = deepcopy(feature.get("qualifiers", {}))
        qualifiers.setdefault("label", [feature["label"]])
        record.features.append(SeqFeature(locations[0] if len(locations) == 1 else CompoundLocation(locations),
                                          type=feature["type"], qualifiers=qualifiers))
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        SeqIO.write(record, stream, "genbank")


def run_case(directory, *, case=None, operation="inspect_guide", parameters=None):
    case = deepcopy(b2() if case is None else case)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    write_material(directory / "vector.gb", case["vector"])
    write_material(directory / "target.gb", case["target"])
    service = RunService()
    assert service.catalog.problems == [], service.catalog.problems
    service.create(directory / "run")
    role = "construct" if operation in ("replace_spacer", "model_replace") else "analysis"
    goal = {"schema": "goal-v1", "version": 1, "parent_digest": None, "original_request": "Compute a synthetic Cut Plasmid case.",
            "sources": [{"source_id": name, "from": str(directory / (name + ".gb")), "input_origin": "user_file", "as": "artifact", "declared": {}}
                        for name in ("vector", "target")], "declared_context": [],
            "targets": [{"id": "t1", "role": role, "required": True}],
            "constraints": [{"id": "c1", "check": "check.goal.output_present@" + service.catalog.declaration("check.goal.output_present")["version"], "params": {}, "target": "t1",
                             "status": "active", "source_quote": "Compute a synthetic Cut Plasmid case."}], "intents": []}
    declared = service.session.set_goal(goal)
    declaration = service.catalog.declaration("cut_plasmid." + operation)
    inputs = {port["name"]: {"step": "read_" + port["name"], "port": "material"} for port in declaration["inputs"]}
    readers = [{"step_id": "read_" + name, "use": "format.read_genbank", "inputs": {"file": {"source": name}},
                "params": {"strandedness": "double"}, "why": "Read a synthetic GenBank source through the public format capability."}
               for name in ("vector", "target")]
    if parameters is None:
        parameters = deepcopy(case.get("setup_params", case["params"])) if operation in ("replace_spacer", "inspect_guide", "model_replace") else {}
        if operation in ("replace_spacer", "model_replace"):
            parameters["spacer"] = case["spacer"]
        if operation == "model_replace":
            parameters.pop("scaffold_sequence")
    service.session.submit({"schema": "pipeline-v1", "version": 1, "goal_digest": declared["goal_digest"],
        "steps": readers + [{"step_id": "test", "use": "cut_plasmid." + operation, "inputs": inputs, "params": parameters,
                   "why": "Use independently constructed synthetic input and expected answer."}],
        "outputs": [{"name": "result", "from": {"step": "test", "port": declaration["outputs"][0]["name"]}, "target": "t1"}]})
    result = execute(service.session, service.invoker)
    return service, result


def retained(service):
    row = service.session.steps()["test"]
    event = row["completed"] or row["failure"]
    payload = event["payload"] if row["completed"] else event["payload"]["retained_outputs"]
    return {"products": {port: service.session.store.get("materials", ids[0]) for port, ids in payload["outputs"]["materials"].items()},
            "documents": {port: service.session.store.get("documents", ids[0]) for port, ids in payload["outputs"]["documents"].items()}}


def run_check(service, name):
    return service.invoker.invoke(name, {}, {}, parent="judge", view=service.view({"moment": "final", "issuer": "check_capability", "outputs": [],
                                  "catalog": service.session.snapshot()})).verdicts[0]
