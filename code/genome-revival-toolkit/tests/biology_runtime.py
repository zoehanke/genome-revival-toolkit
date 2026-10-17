"""Constructed S1 sessions for genuine Invoker/executor tests, never a fake ctx."""
import copy
from pathlib import Path

from dna_design_core.catalog.registry import Catalog
from dna_design_core.engine.executor import execute
from dna_design_core.engine.invoker import Invoker
from dna_design_core.engine.session import Session
from dna_design_core.engine.view import ReadView
from dna_design_core.kernel import canonical, ids
from dna_design_core.storage.journal import Journal
from dna_design_core.storage.store import Store


def material(sequence, topology=None, strandedness=None, ends=None, features=None):
    return {"sequence": sequence, "topology": topology, "strandedness": strandedness,
            "ends": ends, "features": copy.deepcopy(features or [])}


def material_steps(values):
    steps, references = [], {}
    for index, (name, value) in enumerate(values.items(), 1):
        step_id = "m" + str(index)
        steps.append({"step_id": step_id, "use": "seq.make_material", "inputs": {"sequence": {"literal": value["sequence"]}},
                      "params": {key: copy.deepcopy(item) for key, item in value.items() if key != "sequence"},
                      "why": "Construct an explicitly specified synthetic material."})
        references[name] = {"step": step_id, "port": "material"}
    return steps, references


def action_case(directory, identity, inputs=None, parameters=None, *, config=None, artifact_sources=None):
    steps, references = material_steps(inputs or {})
    sources = []
    for name, path in (artifact_sources or {}).items():
        sources.append({"source_id": name, "from": str(path), "input_origin": "user_file", "as": "artifact", "declared": {}})
        references[name] = {"source": name}
    steps.append({"step_id": "target", "use": identity, "inputs": references, "params": parameters or {},
                  "why": "Run a synthetic case with an independently written answer."})
    return run_steps(directory, steps, sources=sources, config=config)


def run_steps(directory, steps, *, sources=(), config=None, goal_constraints=(), target_role="analysis"):
    root = Path(directory) / "run"
    root.mkdir()
    catalog = Catalog()
    if catalog.problems:
        raise AssertionError(catalog.problems)
    (root / "run.json").write_bytes(canonical.dumps({"run_id": "a" * 16, "created_at": "2026-10-16T00:00:00Z", "release_id": "dev-tree"}))
    snapshot = catalog.snapshot("dev-tree")
    snapshot_id = Store(root).put("documents", snapshot)
    Journal(root, "a" * 16).append("run.created", {
        "release_id": "dev-tree", "schema_versions": {"event": 1}, "created_by": {"kind": "ai_host", "name": "synthetic test"},
        "environment": {"python": "test", "platform": "test", "packages": {}, "external_tools": [],
                        "config_digest": ids.document_id(config or {})},
        "catalog_id": snapshot_id, "catalog_ref": "store/documents/" + snapshot_id + ".json", "kits": []}, writer="application")
    session = Session(root, catalog, config=config)
    declared = session.set_goal({"schema": "goal-v1", "version": 1, "parent_digest": None,
        "original_request": "Compute the synthetic case.", "sources": list(sources), "declared_context": [],
        "targets": [{"id": "t1", "role": target_role, "required": True}], "constraints": list(goal_constraints), "intents": []})
    last = steps[-1]
    port = catalog.declaration(last["use"])["outputs"][0]
    reference = {"step": last["step_id"], "port": port["name"]}
    if port["type"] == "materials":
        reference["index"] = 0
    session.submit({"schema": "pipeline-v1", "version": 1, "goal_digest": declared["goal_digest"], "steps": steps,
                    "outputs": [{"name": "result", "from": reference, "target": "t1"}]})
    invoker = Invoker(session)
    result = execute(session, invoker)
    if result["state"] != "COMPLETED":
        raise AssertionError(result)
    return session, invoker


def retained(session, step_id="target"):
    payload = session.steps()[step_id]["completed"]["payload"]
    return {
        "products": {key: [session.store.get("materials", identity) for identity in values]
                     for key, values in payload["outputs"]["materials"].items()},
        "documents": {key: session.store.get("documents", values[0]) for key, values in payload["outputs"]["documents"].items()},
        "artifacts": [session.root / row["run_path"] for row in payload["outputs"]["artifacts"]],
    }


def check_view(session, events=None, outputs=None):
    return ReadView(session.root, session.events() if events is None else events, session.snapshot(),
                    {"moment": "final", "issuer": "check_capability", "outputs": outputs or []})
