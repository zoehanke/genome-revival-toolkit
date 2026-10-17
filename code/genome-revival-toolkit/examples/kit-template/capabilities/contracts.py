"""Exportable declarations; no engine, renderer or separate Kit entry point."""
from dna_design_core.kernel.public import core_version

PREFIX = "word_count"
OWNER = "kit:word-count"
VERSION = core_version()
LIMITS = ["This is a tutorial example, not any experimental or scientific claim."]
REPORT = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "word_count": {"type": "integer", "minimum": 0},
        "minimum_words": {"type": "integer", "minimum": 0},
        "meets_minimum": {"type": "boolean"},
        "rule_id": {"type": "string"},
    },
    "required": ["text", "word_count", "minimum_words", "meets_minimum", "rule_id"],
    "additionalProperties": False,
}


def declaration(name, role, module, summary):
    return {
        "schema": "capability-v1", "id": PREFIX + "." + name,
        "version": VERSION, "role": role, "summary": summary,
        "effects": ["reads_files"], "deterministic": True, "requires_runtime": [],
        "inputs": [], "params": {"type": "object", "properties": {}, "additionalProperties": False},
        "outputs": [], "step_checks": [], "final_checks": [],
        "does_not_establish": LIMITS,
        "source": {"algorithm_refs": ["README.md: Counting contract; knowledge/minimum_words.json"],
                   "implemented_in": "grt_kit_" + PREFIX + ".capabilities." + module + ":" + name},
        "owner": OWNER, "granularity": "atomic",
        "authorship": {"kind": "ai", "tool_or_model": "Codex", "date": "2026-10-17"},
    }


ACTION = declaration("count_words", "ACTION", "count", "Count whitespace-separated words and apply a sourced tutorial threshold.")
ACTION["params"] = {"type": "object", "properties": {"text": {"type": "string"}},
                    "required": ["text"], "additionalProperties": False}
ACTION["outputs"] = [{"name": "report", "type": "document", "schema": REPORT, "output_role": "analysis"}]
ACTION["step_checks"] = [PREFIX + ".check_count"]
ACTION["final_checks"] = [{"check": PREFIX + ".check_count"}]

CHECK = declaration("check_count", "CHECK", "check", "Independently check retained counts and decisions against recorded text and the frozen rule.")
CHECK.update(scope="content_model", evaluates_constraint=False, offline=True,
             fixtures={"pass": "capabilities/fixtures/count.pass.json", "fail": "capabilities/fixtures/count.fail.json"})
