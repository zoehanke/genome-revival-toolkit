"""Read-only check; counting algorithm is independent of the ACTION's split."""
from dna_design_core.kernel.public import Outcome, ToolkitError, capability, document_id, make
from .contracts import CHECK, LIMITS, OWNER, PREFIX, VERSION


@capability(CHECK)
def check_count(ctx: object) -> Outcome:
    candidate = ctx.view.candidate
    matches = []
    try:
        rule = ctx.knowledge(OWNER + "/knowledge/minimum_words.json")
        minimum = rule["parameters"]["minimum_words"]
        for step in ctx.view.steps():
            if step["definition"]["use"].split("@")[0] != PREFIX + ".count_words" or step["superseded"]:
                continue
            if candidate.get("moment") == "step":
                if step["definition"]["step_id"] != candidate["step_id"]:
                    continue
                retained = candidate["step_outputs"]
            elif step["completed"]:
                retained = step["completed"]["payload"]
            else:
                continue
            text = step["started"]["payload"]["params"]["text"]
            count, in_word = 0, False
            for character in text:
                if character.isspace():
                    in_word = False
                elif not in_word:
                    count += 1
                    in_word = True
            expected = {"text": text, "word_count": count, "minimum_words": minimum,
                        "meets_minimum": count >= minimum, "rule_id": rule["id"]}
            identity, = retained["outputs"]["documents"]["report"]
            report = ctx.view.document(identity)
            matches.append(report == expected)
        outcome = ("PASS" if all(matches) else "FAIL") if matches else "UNKNOWN"
    except (ToolkitError, KeyError, TypeError, ValueError):
        outcome = "UNKNOWN"
    return Outcome(verdicts=[make(
        check={"id": PREFIX + ".check_count", "version": VERSION}, scope="content_model",
        moment=candidate.get("moment", "final"), issuer=candidate.get("issuer", "check_capability"),
        subject={"kind": "run", "id": ctx.view.events()[0]["run_id"]}, outcome=outcome,
        summary="Retained word counts and threshold decisions checked against recorded text.",
        evidence={"matches": matches}, rule_refs=[document_id(rule)] if matches else [],
        does_not_establish=LIMITS,
    )])
