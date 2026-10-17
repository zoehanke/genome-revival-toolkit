"""One operation, one typed analysis document."""
from dna_design_core.kernel.public import Outcome, capability
from .contracts import ACTION, OWNER


@capability(ACTION)
def count_words(ctx: object, text: str) -> Outcome:
    rule = ctx.knowledge(OWNER + "/knowledge/minimum_words.json")
    minimum = rule["parameters"]["minimum_words"]
    count = len(text.split())
    return Outcome(documents={"report": {
        "text": text, "word_count": count, "minimum_words": minimum,
        "meets_minimum": count >= minimum, "rule_id": rule["id"],
    }})
