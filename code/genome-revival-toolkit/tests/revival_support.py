"""S3 synthetic test setup. No expected scientific answer is obtained here."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "kits/revival-evidence"
sys.path.insert(0, str(ROOT / "src"))
from dna_design_core.application.run_service import RunService
from dna_design_core.engine.executor import execute
from dna_design_core.kernel.public import ToolkitError


def load_kit(root=KIT, namespace="revival_test_kit"):
    for name, path in [(namespace, root), (namespace + ".capabilities", root / "capabilities")]:
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        sys.modules[name] = package
    name = namespace + ".capabilities.evidence"
    spec = importlib.util.spec_from_file_location(name, root / "capabilities/evidence.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def json_file(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def skill_contract():
    lines = []
    for path in sorted((KIT / "capabilities").glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        lines.extend(["### " + row["id"], "", row["summary"], "",
            "Inputs: " + (", ".join(port["name"] + " (" + port["type"] + ", " + ("required" if port["required"] else "optional") + ")" for port in row["inputs"]) or "none") + ".",
            "Parameters: `" + json.dumps(row["params"], sort_keys=True) + "`.",
            "Outputs: " + (", ".join(port["name"] + " (" + (port["output_role"] or "intermediate") + ")" for port in row["outputs"]) or "verdicts") + ".",
            "Final checks: " + (", ".join(check["check"] for check in row["final_checks"]) or "none") + ".",
            "Does not establish: " + "; ".join(row["does_not_establish"]), ""])
    template = json.loads((KIT / "templates/assess_observations.json").read_text(encoding="utf-8"))
    lines.extend(["### Template parameters", ""])
    lines.extend("- " + name + " (" + value["type"] + "): " + value["description"] for name, value in template["params_schema"]["properties"].items())
    return "\n".join(lines) + "\n"


def context_for(view=None):
    """Unit-test context; integration cases obtain the real Context from Invoker."""
    if view is None:
        manifest = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
        packages = {"kit:revival-evidence/" + name: json.loads((KIT / name).read_text(encoding="utf-8"))
                    for name in manifest["contributes"]["knowledge"]}
    else:
        packages = {row["pack"]: view.document(row["digest"]) for row in view.candidate["catalog"]["knowledge"]
                    if row["pack"].startswith("kit:revival-evidence/")}
    def knowledge(pack):
        if pack not in packages:
            raise ToolkitError("KNOWLEDGE_SOURCE_INVALID")
        return deepcopy(packages[pack])
    return types.SimpleNamespace(view=view, knowledge=knowledge)


def run_case(folder, observation=KIT / "examples/b3.csv", predictions=None, comparisons=None,
             *, kit_dirs=(), before_execute=None, claim="functional_revival"):
    root = folder / "run"
    service = RunService(kit_dirs=kit_dirs)
    service.create(root)
    goal = json.loads((KIT / "examples/goal.json").read_text(encoding="utf-8"))
    goal["sources"][0]["from"] = str(observation.resolve())
    if predictions:
        goal["sources"].append({"source_id": "predictions", "from": str(predictions.resolve()),
                                "as": "artifact", "input_origin": "user_file", "declared": {}})
    goal["constraints"][0]["check"] = "check.goal.claim_reported@" + service.catalog.declaration("check.goal.claim_reported")["version"]
    goal["constraints"][0]["params"]["claim"] = claim
    declared = service.session.set_goal(goal)
    draft = service.instantiate("revival-evidence.assess_observations", {
        "goal_digest": declared["goal_digest"], "source_id": "observations", "observation_origin": "SYNTHETIC_EXAMPLE",
        "comparisons": comparisons if comparisons is not None else [{"experiment_group": "fusion", "control_group": "control"}]})["draft"]
    if predictions:
        draft["steps"][0]["inputs"]["predictions"] = {"source": "predictions"}
    before = service.invoker.calls
    service.session.submit(draft)
    assert service.invoker.calls == before == 0
    if before_execute is not None:
        before_execute(service)
    execution = execute(service.session, service.invoker)
    assert execution.get("failure") is None, execution
    assessment_step = next(row for row in service.view().steps() if row["definition"]["step_id"] == "s2")
    identity = assessment_step["completed"]["payload"]["outputs"]["documents"]["assessment"][0]
    return service, service.view().document(identity)


class AlteredView:
    """Read-only test overlay representing an inconsistent recorded report."""
    def __init__(self, view, documents):
        self.original = view
        self.documents = deepcopy(documents)
        self.root, self.goal, self.pipeline, self.candidate = view.root, view.goal, view.pipeline, view.candidate

    def document(self, identity):
        return deepcopy(self.documents[identity]) if identity in self.documents else self.original.document(identity)

    def steps(self):
        return self.original.steps()

    def events(self, filter=None):
        return self.original.events(filter)
