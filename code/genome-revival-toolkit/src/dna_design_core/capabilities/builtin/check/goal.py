"""D2 constraints over retained, explicitly target-bound content, never annotations as sequence."""
from pathlib import Path

from dna_design_core.biology.public import reverse_complement
from dna_design_core.kernel.public import (
    Outcome, ToolkitError, capability, core_version, file_sha256, loads, make,
)
from ...declaration import check

MODULE = __name__ + ":"
DNA = {"type": "string", "minLength": 1, "pattern": "^[ACGTRYSWKMBDHVNacgtryswkmbdhvn]+$"}
TEXT = {"type": "string", "minLength": 1, "pattern": "\\S"}
COMPONENTS = {"type": "array", "minItems": 1, "items": {
    "type": "object", "properties": {"name": TEXT,
        "sequence": {"type": "string", "minLength": 1, "pattern": "^[ACGTacgt]+$"},
        "strand": {"enum": [1, -1]}}, "required": ["name", "sequence"], "additionalProperties": False}}
REGIONS = {"type": "array", "minItems": 1, "items": {
    "type": "object", "properties": {
        **{name: {"type": "integer", "minimum": 0} for name in ("source_start", "source_end", "target_start", "target_end")},
        "strand": {"enum": [1, -1]}},
    "required": ["source_start", "source_end", "target_start", "target_end"], "additionalProperties": False}}
ERRORS = (ToolkitError, OSError, ValueError, KeyError, TypeError, IndexError)


def _declaration(name, function, summary, properties, required):
    value = check("check.goal." + name, "user_goal", MODULE + function, summary, constraint=True)
    value["params"] = {"type": "object", "properties": properties, "required": required, "additionalProperties": False}
    value["fixtures"] = {variant: "tests/fixtures/goal_checks/" + name + "." + variant + ".json" for variant in ("pass", "fail")}
    value["source"]["algorithm_refs"] = ["SPEC D2 GOL-4/GOL-6", "SPEC D9 retained content identities"]
    value["does_not_establish"] = ["Experimental performance, functional identity or truth of a reported claim.",
                                   "Constraint meaning beyond the explicit sequences, coordinates and report topic."]
    return value


def _result(ctx, name, outcome, summary, evidence=None):
    candidate, events = ctx.view.candidate, ctx.view.events()
    return Outcome(verdicts=[make(check={"id": "check.goal." + name, "version": core_version()}, scope="user_goal",
        moment=candidate.get("moment", "final"), issuer=candidate.get("issuer", "check_capability"),
        subject={"kind": "run", "id": events[0]["run_id"]}, constraint_id=candidate.get("constraint", {}).get("id"),
        outcome=outcome, summary=summary, evidence=evidence or {}, basis=[event["hash"] for event in events],
        does_not_establish=["Experimental success, biological function or truth of a reported claim."])])


def _targets(ctx, name, kinds):
    target = ctx.view.candidate.get("constraint", {}).get("target")
    if target is None:
        return [], _result(ctx, name, "UNKNOWN", "No explicit goal-constraint target was supplied.")
    rows = [row for row in ctx.view.candidate.get("outputs", []) if row.get("target") == target]
    if not rows:
        return [], _result(ctx, name, "FAIL", "The constrained target has no retained output.", {"target": target})
    if any(row.get("kind") not in kinds for row in rows):
        return [], _result(ctx, name, "UNKNOWN", "The target output kind cannot establish this constraint.", {"target": target})
    return rows, None


@capability(_declaration("topology", "topology", "Compare every target material's known topology with the requested topology.",
    {"topology": {"enum": ["linear", "circular"]}}, ["topology"]))
def topology(ctx: object, topology: str) -> Outcome:
    rows, error = _targets(ctx, "topology", {"material"})
    if error is not None:
        return error
    try:
        actual = [ctx.view.material(row["id"])["topology"] for row in rows]
    except ERRORS:
        return _result(ctx, "topology", "UNKNOWN", "Target material content is unavailable.")
    outcome = "FAIL" if any(value is not None and value != topology for value in actual) else "UNKNOWN" if None in actual else "PASS"
    return _result(ctx, "topology", outcome, "Retained topology compared; unknown topology is not inferred.", {"expected": topology, "actual": actual})


@capability(_declaration("exact_sequence", "exact_sequence", "Compare complete target sequences literally at their declared origin and orientation.",
    {"sequence": DNA}, ["sequence"]))
def exact_sequence(ctx: object, sequence: str) -> Outcome:
    rows, error = _targets(ctx, "exact_sequence", {"material"})
    if error is not None:
        return error
    try:
        matches = [{"material_id": row["id"], "matches": ctx.view.material(row["id"])["sequence"] == sequence.upper()} for row in rows]
    except ERRORS:
        return _result(ctx, "exact_sequence", "UNKNOWN", "Target sequence content is unavailable.")
    return _result(ctx, "exact_sequence", "PASS" if all(row["matches"] for row in matches) else "FAIL",
                   "Complete uppercase sequences compared without rotation or reverse-complement equivalence.", {"targets": matches})


def _components(ctx, components, absent):
    name = "components_absent" if absent else "components_present"
    rows, error = _targets(ctx, name, {"material"})
    if error is not None:
        return error
    evidence, failed, unresolved = [], False, False
    try:
        for row in rows:
            material = ctx.view.material(row["id"])
            sequence, topology = material["sequence"], material["topology"]
            for component in components:
                query = component["sequence"].upper()
                if component.get("strand", 1) == -1:
                    query = reverse_complement(query)
                searchable = sequence + sequence[:len(query) - 1] if topology == "circular" else sequence
                positions = [start for start in range(len(sequence)) if len(query) <= len(sequence) and searchable.startswith(query, start)]
                uncertain = not positions and (topology is None or bool(set(sequence) - set("ACGT")))
                failed |= bool(positions) if absent else not positions and not uncertain
                unresolved |= uncertain
                evidence.append({"material_id": row["id"], "name": component["name"], "strand": component.get("strand", 1),
                                 "positions": positions, "unresolved": uncertain})
    except ERRORS:
        return _result(ctx, name, "UNKNOWN", "Component or target content is unavailable.")
    return _result(ctx, name, "FAIL" if failed else "UNKNOWN" if unresolved else "PASS",
        "Components checked against sequence on the explicit strand; labels do not establish presence or absence.", {"components": evidence})


@capability(_declaration("components_present", "components_present", "Require every explicit component sequence in every target material.",
    {"components": COMPONENTS}, ["components"]))
def components_present(ctx: object, components: list[dict]) -> Outcome:
    return _components(ctx, components, False)


@capability(_declaration("components_absent", "components_absent", "Require every explicit component sequence to be absent from every target material.",
    {"components": COMPONENTS}, ["components"]))
def components_absent(ctx: object, components: list[dict]) -> Outcome:
    return _components(ctx, components, True)


@capability(_declaration("regions_unchanged", "regions_unchanged", "Compare explicit nonwrapping reference/target intervals in retained materials.",
    {"reference_material_id": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "regions": REGIONS},
    ["reference_material_id", "regions"]))
def regions_unchanged(ctx: object, reference_material_id: str, regions: list[dict]) -> Outcome:
    rows, error = _targets(ctx, "regions_unchanged", {"material"})
    if error is not None:
        return error
    comparisons = []
    try:
        source = ctx.view.material(reference_material_id)["sequence"]
        for row in rows:
            target = ctx.view.material(row["id"])["sequence"]
            for region in regions:
                a, b, c, d = (region[key] for key in ("source_start", "source_end", "target_start", "target_end"))
                if not 0 <= a < b <= len(source) or not 0 <= c < d <= len(target):
                    return _result(ctx, "regions_unchanged", "UNKNOWN", "Regions must be nonempty, nonwrapping and within both retained sequences.")
                expected = source[a:b]
                if region.get("strand", 1) == -1:
                    expected = reverse_complement(expected)
                comparisons.append({"material_id": row["id"], "region": region, "matches": expected == target[c:d]})
    except ERRORS:
        return _result(ctx, "regions_unchanged", "UNKNOWN", "The explicit retained reference or target is unavailable.")
    return _result(ctx, "regions_unchanged", "PASS" if all(row["matches"] for row in comparisons) else "FAIL",
        "Explicit reference/target intervals compared; annotation inheritance is outside this check.",
        {"reference_material_id": reference_material_id, "comparisons": comparisons})


def _document(ctx, row):
    if row["kind"] == "document":
        return ctx.view.document(row["id"])
    root = Path(ctx.view.candidate["root"]).resolve()
    path = (root / row["path"]).resolve()
    if not path.is_relative_to(root):
        raise ValueError("target report is outside the candidate")
    data = path.read_bytes()
    if file_sha256(data) != row["id"]:
        raise ValueError("target report bytes differ from the bound artifact identity")
    return loads(data)


def _pointer(value, pointer):
    if pointer:
        for token in pointer.split("/")[1:]:
            token = token.replace("~1", "/").replace("~0", "~")
            if isinstance(value, list) and (not token.isdigit() or (len(token) > 1 and token[0] == "0")):
                raise KeyError(token)
            value = value[int(token)] if isinstance(value, list) else value[token]
    return value


@capability(_declaration("claim_reported", "claim_reported", "Require a unique explicitly named claim with a nonempty status in target JSON reports.",
    {"claim": TEXT, "pointer": {"type": "string", "pattern": "^(?:/(?:[^~/]|~[01])*)*$"}}, ["claim"]))
def claim_reported(ctx: object, claim: str, pointer: str = "/claims") -> Outcome:
    rows, error = _targets(ctx, "claim_reported", {"document", "artifact"})
    if error is not None:
        return error
    matches = []
    try:
        for row in rows:
            try:
                selected = _pointer(_document(ctx, row), pointer)
            except (KeyError, IndexError, TypeError):
                continue
            values = selected if isinstance(selected, list) else [selected]
            matches.extend(value for value in values if isinstance(value, dict) and value.get("claim") == claim)
    except ERRORS:
        return _result(ctx, "claim_reported", "UNKNOWN", "Target JSON report content is unavailable or corrupt.")
    passed = len(matches) == 1 and isinstance(matches[0].get("status"), str) and bool(matches[0]["status"].strip())
    return _result(ctx, "claim_reported", "PASS" if passed else "FAIL", "Claim reporting checked; its status need not assert success and its truth is not evaluated.",
                   {"claim": claim, "pointer": pointer, "matches": len(matches), "reported_status": matches[0].get("status") if len(matches) == 1 else None})
