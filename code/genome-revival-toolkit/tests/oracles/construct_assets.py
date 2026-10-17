"""Development-only declaration/template export and independent synthetic inputs."""
import importlib
import json
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "kits/construct"
MODULES = ("model", "design", "assay", "checks", "handoff")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def template(method):
    properties = {name: {"type": "string", "description": name.replace("_", " ")} for name in (
        "goal_digest", "reference_source", "cargo_source", "donor_target", "primers_target", "assay_target", "handoff_target")}
    for name in ("start", "end", "arm_length", "cargo_start", "cargo_end", "primer_length"):
        properties[name] = {"type": "integer", "minimum": 0, "description": "Explicit " + name.replace("_", " ")}
    extra = ("overlap",) if method == "gibson" else ("donor_template_source", "donor_start", "donor_end")
    for name in extra:
        properties[name] = {"type": "string" if name.endswith("source") else "integer", "description": name.replace("_", " ")}
    def ref(step, port):
        return {"step": step, "port": port}
    def step(name, use, inputs, params, why):
        return {"step_id": name, "use": use, "inputs": inputs, "params": params, "why": why}
    steps = [step("reference", "format.read_fasta", {"file": {"source": "{{reference_source}}"}},
                  {"topology": "linear", "strandedness": "double"}, "Read the supplied synthetic linear reference."),
             step("cargo", "format.read_fasta", {"file": {"source": "{{cargo_source}}"}},
                  {"topology": "linear", "strandedness": "double"}, "Read the actual selected cargo source.")]
    if method == "pcr":
        steps.append(step("donor_template", "format.read_fasta", {"file": {"source": "{{donor_template_source}}"}},
                          {"topology": "linear", "strandedness": "double"}, "Read the actual complete donor template; do not create it from the model."))
    bounds = {name: "{{" + name + "}}" for name in ("start", "end", "arm_length", "cargo_start", "cargo_end")}
    inputs = {"reference": ref("reference", "material"), "cargo": ref("cargo", "material")}
    steps.append(step("model", "construct.model_donor", inputs.copy(), bounds.copy(), "Compute the independent source-bound expectation before preparation."))
    design_params = {**bounds, "preparation_method": method, "primer_length": "{{primer_length}}"}
    if method == "pcr":
        inputs["donor_template"] = ref("donor_template", "material")
        design_params.update(donor_start="{{donor_start}}", donor_end="{{donor_end}}")
    else:
        design_params["overlap"] = "{{overlap}}"
    steps.extend([
        step("design", "construct.design_donor", inputs, design_params, "Prepare through actual template PCR and the requested assembly method."),
        step("assay", "construct.design_junction_assay", {"original": ref("reference", "material"),
             "edited": ref("design", "edited"), "donor": ref("design", "product")},
             {name: "{{" + name + "}}" for name in ("start", "end", "arm_length", "primer_length")},
             "Test external junction primers on edited, original and residual donor DNA."),
        step("original_file", "format.write_genbank", {"material": ref("reference", "material")}, {"name": "original.gb"}, "Export the exact original assay background."),
        step("edited_file", "format.write_genbank", {"material": ref("design", "edited")}, {"name": "edited.gb"}, "Export the exact edited assay background."),
        step("donor_file", "format.write_genbank", {"material": ref("design", "product")}, {"name": "donor.gb"}, "Export the actual PCR/assembly product for independent recomputation."),
        step("handoff", "construct.export_handoff", {"original_file": ref("original_file", "file"),
             "edited_file": ref("edited_file", "file"), "assay": ref("assay", "assay")}, {},
             "Bind actual reference-file hashes and junction primers into the D11 file protocol.")])
    return {"schema": "pipeline-template-v1", "version": 1, "goal_digest": "{{goal_digest}}", "steps": steps,
            "outputs": [{"name": name, "from": ref(producer, port), "target": "{{" + target + "}}"} for name, producer, port, target in (
                ("donor", "design", "product", "donor_target"), ("primers", "design", "primers", "primers_target"),
                ("assay", "assay", "assay", "assay_target"), ("identity_handoff", "handoff", "handoff", "handoff_target"))],
            "params_schema": {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}}


def export():
    sys.path.insert(0, str(ROOT / "kits"))
    declarations = []
    for name in MODULES:
        module = importlib.import_module("construct.capabilities." + name)
        for item in vars(module).values():
            declaration = getattr(item, "declaration", None)
            if not declaration:
                continue
            path = "capabilities/" + declaration["id"].split(".", 1)[1] + ".json"
            write(KIT / path, declaration)
            declarations.append((path, declaration))
    versions = json.loads((ROOT / "VERSIONS.json").read_text(encoding="utf-8"))
    write(KIT / "kit.json", {"schema": "kit-v1", "name": "construct", "version": versions["kits"]["construct"], "title": "Construct",
        "requires_core": {"minimum": versions["core"], "maximum_exclusive": str(int(versions["core"].split(".")[0]) + 1) + ".0.0"},
        "contributes": {"capabilities": sorted(path for path, _ in declarations), "knowledge": [],
                        "templates": ["templates/prepare_gibson.json", "templates/prepare_pcr.json"], "text": ["text/en.json"]},
        "does_not_establish": declarations[0][1]["does_not_establish"], "review": "knowledge/review/"})
    for method in ("gibson", "pcr"):
        write(KIT / "templates" / ("prepare_" + method + ".json"), template(method))
    for identity in ("construct.check_preparation", "construct.check_junction_assay"):
        for kind in ("pass", "fail"):
            write(KIT / "capabilities/fixtures" / (identity + "." + kind + ".json"), {
                "check": identity, "expected": "PASS" if kind == "pass" else "FAIL", "params": {},
                "scenario": "valid_gibson" if kind == "pass" else "mutated_preparation_product" if identity.endswith("preparation") else "donor_carryover",
                "oracle": {"kind": "construction", "reason": "Predetermined template edit or both QC primers inside retained donor arms."}})
    lines = ["<!-- GENERATED:START -->", "## Input contracts", "", "Strict field shapes are in the linked exported declarations.", "",
             "| Capability | Inputs (? optional) | Required parameters | Outputs | Extra final checks |",
             "|---|---|---|---|---|"]
    for _, declaration in sorted(declarations):
        lines.append("| [" + declaration["id"] + "](capabilities/" + declaration["id"].split(".", 1)[1] + ".json) | " +
                     ", ".join(p["name"] + ":" + p["type"] + ("" if p["required"] else "?") for p in declaration["inputs"]) + " | " +
                     ", ".join(declaration["params"].get("required", [])) + " | " +
                     ", ".join(p["name"] + ":" + p["type"] for p in declaration["outputs"]) + " | " +
                     ", ".join(row["check"] for row in declaration["final_checks"]) + " |")
    lines.extend(["", "Model: construct.design_donor declares construct.model_donor; check.model_agreement is automatically required.", "",
                  "Does not establish: " + "; ".join(declarations[0][1]["does_not_establish"]) + ".", ""])
    lines.append("<!-- GENERATED:END -->")
    path = KIT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    prefix = text.split("<!-- GENERATED:START -->")[0]
    path.write_text(prefix + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def example():
    # Construction oracle: standard-library random source, intervals then answer.
    generator = Random(20261017)
    reference = "".join(generator.choice("ACGT") for _ in range(300))
    cargo = "".join(generator.choice("ACGT") for _ in range(90))
    left, right = reference[50:100], reference[160:210]
    donor = left + cargo + right
    template_sequence = "".join(generator.choice("ACGT") for _ in range(30)) + donor + "".join(generator.choice("ACGT") for _ in range(30))
    for name, sequence in (("reference", reference), ("cargo", cargo), ("donor-template", template_sequence)):
        (KIT / "examples" / (name + ".fasta")).write_text(">synthetic_" + name + "\n" + sequence + "\n", encoding="utf-8", newline="\n")
    write(KIT / "examples/case.json", {"oracle": {"kind": "construction", "seed": 20261017, "generator": "tests/oracles/construct_assets.py:example"},
        "parameters": {"start": 100, "end": 160, "arm_length": 50, "cargo_start": 0, "cargo_end": 90, "primer_length": 20},
        "gibson": {"overlap": 20}, "pcr": {"donor_start": 30, "donor_end": 220},
        "expected_donor": donor, "expected_length": 190, "expected_edited": reference[:100] + cargo + reference[160:],
        "expected_junction_bp": {"left": 90, "right": 90}})


if __name__ == "__main__":
    (KIT / "examples").mkdir(exist_ok=True)
    export()
    example()
