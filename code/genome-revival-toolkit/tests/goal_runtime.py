"""Actual admitted producers, explicit goal constraints, retained candidate bindings."""
from copy import deepcopy
from pathlib import Path

from biology_runtime import run_steps
from dna_design_core.engine.view import ReadView
from dna_design_core.kernel.public import core_version, file_sha256


def fixture_case(directory, fixture):
    fixture = deepcopy(fixture)
    steps = []
    def material_step(identity, value):
        return {"step_id": identity, "use": "seq.make_material", "inputs": {"sequence": {"literal": value["sequence"]}},
                "params": {name: item for name, item in value.items() if name != "sequence"}, "why": "Construct an independently specified synthetic material."}
    if "reference" in fixture:
        steps.append(material_step("reference", fixture["reference"]))
    if fixture["kind"] == "material":
        steps.append(material_step("target", fixture["value"]))
    else:
        steps.append({"step_id": "target", "use": "format.write_json", "inputs": {"data": {"literal": fixture["value"]}},
                      "params": {"name": "assessment.json"}, "why": "Export a synthetically constructed JSON claim report."})
    constraint = {"id": "c2", "check": fixture["check"] + "@" + core_version(), "params": fixture["params"], "target": "t1",
                  "source_quote": "synthetic case", "status": "active"}
    session, invoker = run_steps(directory, steps, goal_constraints=[constraint],
                                 target_role="component" if fixture["kind"] == "material" else "analysis")
    payload = session.steps()["target"]["completed"]["payload"]["outputs"]
    if fixture["kind"] == "material":
        identity = payload["materials"]["material"][0]
        output = {"id": identity, "kind": "material", "target": "t1",
                  "path": session.store.path("materials", identity).relative_to(session.root).as_posix()}
    else:
        artifact = payload["artifacts"][0]
        output = {"id": artifact["sha256"], "kind": "artifact", "target": "t1", "path": artifact["run_path"]}
    files = [{"path": output["path"], "sha256": file_sha256((session.root / output["path"]).read_bytes()),
              "role": "component" if fixture["kind"] == "material" else "analysis", "labels": []}]
    candidate = {"root": str(session.root), "outputs": [output], "files": files, "constraint": session.current_goal()["constraints"][0],
                 "catalog": session.snapshot(), "moment": "final", "issuer": "check_capability"}
    return session, invoker, candidate


def invoke(session, invoker, candidate, identity, params):
    view = ReadView(session.root, session.events(), session.snapshot(), candidate)
    return invoker.invoke(identity, {}, params, parent="final", view=view).verdicts[0]


def bytes_in(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in Path(root).rglob("*") if path.is_file()}
