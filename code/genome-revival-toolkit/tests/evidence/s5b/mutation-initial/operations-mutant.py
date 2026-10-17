# ported-from: genome-revival-toolkit/kits/identity/scripts/workflow.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
# ported-from: genome-revival-toolkit/kits/identity/scripts/handoff.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
"""Supplied-reference comparisons and exact PCR expectations, without orchestration."""
from copy import deepcopy
from pathlib import Path

from dna_design_core.kernel.public import (
    Outcome, ToolkitError, capability, core_version, file_sha256, loads,
    material_id, normalize_material, require_schema,
)
from dna_design_core.biology.public import (
    material_from_genbank, material_from_record, predict_pcr_products,
    read_dna, read_fasta,
)


LIMITS = [
    "Primer specificity in an actual strain.",
    "Observed experimental products.",
    "Authentic genotype.",
    "Whole-genome discrimination outside supplied references.",
]
UNVERIFIED = [
    "Annealing temperature was not set; exact binding does not establish PCR performance.",
    "Whole-genome specificity alignment was not performed; only supplied reference sequences were searched.",
    "Primer thermodynamic quality and experimental band separation were not measured.",
    "Laboratory PCR and genotype confirmation: NOT_PERFORMED; laboratory steps remain PLANNED.",
]


def _object(properties: dict, required: list | None = None) -> dict:
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


IDENTIFIER = {"type": "string", "minLength": 1}
SHA256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
COORDINATE = {"type": "integer", "minimum": 0}
REGION = _object({"id": IDENTIFIER, "reference_id": IDENTIFIER,
                  "start": COORDINATE, "end": COORDINATE})
HANDOFF_SCHEMA = _object({
    "schema": {"const": "identity-handoff-v1"},
    "references": {"type": "array", "minItems": 2, "maxItems": 2, "items": _object({
        "id": IDENTIFIER, "sha256": SHA256, "role": {"enum": ["original", "edited"]}})},
    "regions": {"type": "array", "items": REGION},
    "primers": {"type": "array", "minItems": 2, "items": _object({
        "id": IDENTIFIER, "sequence": {"type": "string", "pattern": "^[ACGTacgt]+$"}})},
})
EXPECTED = _object({
    "status": {"enum": ["DISTINGUISHABLE", "NOT_DISTINGUISHABLE", "UNDETERMINED"]},
    "product_count": {"type": "integer", "minimum": 0},
    "product_bp": {"type": ["integer", "null"], "minimum": 1},
})
EXPECTED["allOf"] = [{
    "if": {"properties": {"product_count": {"const": 1}}},
    "then": {"properties": {"product_bp": {"type": "integer", "minimum": 1}}},
    "else": {"properties": {"product_bp": {"type": "null"}}},
}]
EXPECTED_SCHEMA = _object({
    "schema": {"const": "identity-expected-results-v1"}, "assay_id": IDENTIFIER,
    "backgrounds": {"type": "array", "minItems": 2, "maxItems": 2, "items": _object({
        "id": IDENTIFIER, "reference_sha256": SHA256,
        "primer_pair": {"type": "array", "minItems": 2, "maxItems": 2, "items": IDENTIFIER},
        "expected": EXPECTED,
    })},
})
# PROVISIONAL(S5B-Q1): explicit intervals and unit-cost global edit distance.
INTERVAL = _object({"material_id": SHA256, "start": COORDINATE, "end": COORDINATE})
COMPARISON_SCHEMA = _object({
    "schema": {"const": "region-comparison-v1"},
    "original": INTERVAL, "edited": INTERVAL,
    "identical": {"type": "boolean"}, "edit_distance": COORDINATE,
})


def _input(name: str, kind: str = "material", *, schema: dict | None = None,
           required: bool = True) -> dict:
    port = {"name": name, "type": kind, "required": required,
            "constraints": {}, "description": name.replace("_", " ")}
    if schema is not None:
        port["schema"] = schema
    return port


def _output(name: str, schema: dict, role: str | None = "analysis") -> dict:
    return {"name": name, "type": "document", "schema": schema, "output_role": role}


def _declaration(name: str, summary: str, inputs: list, outputs: list,
                 properties: dict | None = None, required: list | None = None,
                 *, reads_files: bool = False) -> dict:
    return {
        "schema": "capability-v1", "id": "identity." + name, "version": core_version(),
        "role": "ACTION", "summary": summary,
        "effects": ["reads_files" if reads_files else "pure"],
        "deterministic": True,
        "requires_runtime": [{"kind": "python_package", "name": "biopython", "probe": None}],
        "inputs": inputs, "outputs": outputs,
        "params": _object(properties or {}, required),
        "step_checks": [], "final_checks": [], "does_not_establish": LIMITS,
        "source": {"algorithm_refs": ["spec/SPEC.md D11", "MIGRATION-LOG.md S5b"],
                   "implemented_in": "grt_kit_genome_identity.capabilities.operations:" + name},
        "owner": "kit:genome-identity", "granularity": "atomic",
    }


def _invalid(message: str) -> None:
    raise ToolkitError("PLAN_PARAM_INVALID", message)


def _concrete(material: dict, *, primer: bool = False) -> dict:
    material = normalize_material(material)
    if not material["sequence"] or set(material["sequence"]) - set("ACGT"):
        _invalid("Exact identity analysis requires nonempty, unambiguous A/C/G/T sequences.")
    if material["topology"] not in ("linear", "circular"):
        _invalid("Declare reference topology explicitly; unknown topology cannot imply no product.")
    if primer and material["topology"] != "linear":
        _invalid("Primers must be linear single-stranded materials.")
    if material["strandedness"] != ("single" if primer else "double"):
        _invalid("Declare double-stranded references and single-stranded primers explicitly.")
    return material


def _handoff_links(handoff: dict) -> None:
    references = handoff["references"]
    if {row["role"] for row in references} != {"original", "edited"}:
        _invalid("Handoff needs one original reference and one edited reference.")
    for rows in (references, handoff["primers"], handoff["regions"]):
        if len({row["id"] for row in rows}) != len(rows):
            _invalid("Handoff reference, primer and region identifiers must be unique within each collection.")
    identifiers = {row["id"] for row in references}
    if any(row["reference_id"] not in identifiers or row["start"] >= row["end"]
           for row in handoff["regions"]):
        _invalid("Handoff regions need existing reference ids and nonempty zero-based half-open intervals.")


@capability(_declaration(
    "read_handoff", "Parse the D11 Construct handoff; file and material binding is checked by analyze_assay.",
    [_input("file", "artifact")], [_output("handoff", HANDOFF_SCHEMA, None)], reads_files=True,
))
def read_handoff(ctx: object, file: Path) -> Outcome:
    try:
        value = loads(Path(file).read_bytes())
    except OSError as error:
        raise ToolkitError("PLAN_INPUT_UNBOUND", "Cannot read the registered handoff file.") from error
    require_schema(HANDOFF_SCHEMA, value)
    _handoff_links(value)
    return Outcome(documents={"handoff": value})


def _bound_file(file: Path, material: dict) -> str:
    """Bind a declared material to actual source bytes using shared format readers."""
    path = Path(file)
    try:
        content = path.read_bytes()
        if path.suffix.lower() in (".gb", ".gbk", ".genbank"):
            source = material_from_genbank(content.decode("utf-8"))
        elif path.suffix.lower() in (".fa", ".fasta", ".fna"):
            source = material_from_record(read_fasta(content.decode("utf-8")))
        elif path.suffix.lower() == ".dna":
            source = material_from_record(read_dna(content))
        else:
            _invalid("Reference files must use a supported FASTA, GenBank or native DNA extension.")
    except (OSError, UnicodeError, ValueError) as error:
        raise ToolkitError("PLAN_INPUT_UNBOUND", "Cannot decode the supplied reference file.") from error
    for field in ("topology", "strandedness"):
        if source[field] is None:
            source[field] = material[field]
    if material_id(source) != material_id(material):
        raise ToolkitError("SOURCE_CHANGED", "Reference material does not match the supplied reference file.")
    return file_sha256(content)


def _edit_distance(left: str, right: str) -> int:
    """Unit-cost global Levenshtein distance; no score-derived biological identity."""
    if len(right) > len(left):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for row, base in enumerate(left, 1):
        current = [row]
        for column, other in enumerate(right, 1):
            current.append(min(previous[column] + 1, current[-1] + 1,
                               previous[column - 1] + (base != other)))
        previous = current
    return previous[-1]


@capability(_declaration(
    "compare_regions", "Compare explicit supplied intervals by exact equality and unit-cost global edit distance.",
    [_input("reference_original"), _input("reference_edited")],
    [_output("comparison", COMPARISON_SCHEMA)],
    {"original_start": COORDINATE, "original_end": {"type": ["integer", "null"], "minimum": 1},
     "edited_start": COORDINATE, "edited_end": {"type": ["integer", "null"], "minimum": 1}}, [],
))
def compare_regions(ctx: object, reference_original: dict, reference_edited: dict,
                    original_start: int = 0, original_end: int | None = None,
                    edited_start: int = 0, edited_end: int | None = None) -> Outcome:
    materials = [_concrete(reference_original), _concrete(reference_edited)]
    intervals, sequences = [], []
    for material, start, end in zip(materials, (original_start, edited_start), (original_end, edited_end)):
        end = len(material["sequence"]) if end is None else end
        if not 0 <= start < end <= len(material["sequence"]):
            _invalid("Comparison intervals must be nonempty, in range, and not wrap the circular origin.")
        intervals.append({"material_id": material_id(material), "start": start, "end": end})
        sequences.append(material["sequence"][start:end])
    value = {"schema": "region-comparison-v1", "original": intervals[0], "edited": intervals[1],
             "identical": sequences[0] == sequences[1], "edit_distance": _edit_distance(*sequences)}
    return Outcome(documents={"comparison": value}, unverified=[
        "Global unit-cost sequence comparison of selected intervals only; genomic placement and genotype are unverified."])


def _discrimination(predictions: list) -> str:
    # PROVISIONAL(S5B-Q2): multiple products cannot be resolved by the D11 scalar size field.
    if any(row["product_count"] > 1 for row in predictions):
        return "UNDETERMINED"
    signatures = {(row["product_count"], row["product_bp"]) for row in predictions}
    return "DISTINGUISHABLE" if len(signatures) != len(predictions) else "NOT_DISTINGUISHABLE"


def _product_spans(material: dict, primers: list) -> set:
    # Both reference orientations are valid for the same physical primer pair.
    # PROVISIONAL(S5B-Q4): merge by physical reference interval, not by size.
    spans = set()
    for first, last in (primers, primers[::-1]):
        for product in predict_pcr_products(
            material["sequence"], first["sequence"], last["sequence"],
            circular=material["topology"] == "circular",
        ):
            spans.add((product["template_start"], product["template_span"]))
    return spans


@capability(_declaration(
    "analyze_assay", "Predict exact PCR products on two file-bound references and export D11 expectations.",
    [_input("reference_original"), _input("reference_edited"), _input("forward"), _input("reverse"),
     _input("reference_original_file", "artifact"), _input("reference_edited_file", "artifact"),
     _input("handoff", "document", schema=HANDOFF_SCHEMA, required=False)],
    [_output("expected_results", EXPECTED_SCHEMA)],
    {"assay_id": IDENTIFIER, "forward_id": IDENTIFIER, "reverse_id": IDENTIFIER},
    ["assay_id", "forward_id", "reverse_id"], reads_files=True,
))
def analyze_assay(ctx: object, reference_original: dict, reference_edited: dict,
                  forward: dict, reverse: dict, reference_original_file: Path,
                  reference_edited_file: Path, assay_id: str, forward_id: str,
                  reverse_id: str, handoff: dict | None = None) -> Outcome:
    references = {"original": _concrete(reference_original), "edited": _concrete(reference_edited)}
    primers = [_concrete(forward, primer=True), _concrete(reverse, primer=True)]
    if forward_id == reverse_id:
        _invalid("Forward and reverse primers need distinct identifiers.")
    hashes = {role: _bound_file(file, references[role]) for role, file in (
        ("original", reference_original_file), ("edited", reference_edited_file))}
    # PROVISIONAL(S5B-Q3): without a handoff, use the fixed material-port names as background ids.
    identifiers = {role: "reference_" + role for role in references}
    if handoff is not None:
        require_schema(HANDOFF_SCHEMA, handoff)
        _handoff_links(handoff)
        for row in handoff["references"]:
            role = row["role"]
            if hashes[role] != row["sha256"]:
                raise ToolkitError("SOURCE_CHANGED", "Reference file hash differs from the Construct handoff.")
            identifiers[role] = row["id"]
        supplied = {row["id"]: row["sequence"].upper() for row in handoff["primers"]}
        if any(supplied.get(name) != primer["sequence"]
               for name, primer in zip((forward_id, reverse_id), primers)):
            _invalid("Selected primer ids and sequences must match the Construct handoff.")
        lengths = {identifiers[role]: len(value["sequence"]) for role, value in references.items()}
        if any(row["end"] > lengths[row["reference_id"]] for row in handoff["regions"]):
            _invalid("A handoff region extends outside its bound reference sequence.")
    backgrounds = []
    for role, material in references.items():
        products = _product_spans(material, primers)
        backgrounds.append({"id": identifiers[role], "reference_sha256": hashes[role],
                            "primer_pair": [forward_id, reverse_id],
                            "expected": {"product_count": len(products),
                                         "product_bp": next(iter(products))[1] if len(products) == 1 else None}})
    status = _discrimination([row["expected"] for row in backgrounds])
    for row in backgrounds:
        row["expected"]["status"] = status
    value = {"schema": "identity-expected-results-v1", "assay_id": assay_id, "backgrounds": backgrounds}
    return Outcome(documents={"expected_results": value}, unverified=deepcopy(UNVERIFIED))
