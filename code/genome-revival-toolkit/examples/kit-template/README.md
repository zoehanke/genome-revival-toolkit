# Tutorial Word Count

Copyable teaching Kit, explicitly loaded from outside `kits/`. Requires the same
Core development version and contracts as this checkout; its version follows
`core_version()` in this minimal example. It is excluded from the release Kit
directory and is never discovered by default.

## Counting contract

A word is one nonempty run of characters separated by Python whitespace.
Punctuation stays within a word. Empty or whitespace-only text has zero words.
`knowledge/minimum_words.json` is one rule-table row: minimum three words,
source class `project_contract`, citation "Tutorial example, not a scientific
claim". The decision is `word_count >= minimum_words`.

`red green blue gold` has four words and meets the minimum. `red green` has two
and does not. This is a tutorial example, not any experimental or scientific
claim. Source verification remains `unverified`; human review is absent.

## Files and interfaces

| Contribution | Files | Purpose |
| --- | --- | --- |
| Capabilities | `capabilities/count.py`, `check.py`, `contracts.py`, two JSON declarations | ACTION counts; CHECK independently scans character transitions. Both import only `kernel.public` and their own declarations. |
| Rules | `knowledge/minimum_words.json` | Frozen threshold and source read with `ctx.knowledge`. Incomplete sources belong in `knowledge/drafts/`, outside the manifest. |
| Template | `templates/count.json` | One declared step and an analysis output bound to goal target `t1`. |
| Text | `text/en.json` | Declared text file; current Core checks its existence but does not consume Kit translations in its renderer. |

`kit.json` declares all four contributions. JSON declarations must match the
decorated Python functions. `SKILL.md` gives host instructions, not another
runtime entry point. `examples/goal.json` and `template-request.json` are requests;
replace the request's digest with `goal declare`'s `result.goal_digest`.

The CHECK tests accuracy, including an accurately reported `false` decision.
It runs after the step through `step_checks` and again through `final_checks`
before sealing. It returns `UNKNOWN` when required records are unavailable.
The negative fixture deliberately reports five words for a four-word phrase;
tests really invoke the CHECK and require `FAIL`. Answers come from literal
token construction, not from the ACTION. Tests also change ACTION counting,
invert its threshold decision and disable the CHECK comparison.

## Walkthrough and checks

From the project folder, follow `docs/developers/add-a-kit.md`. Its marked
PowerShell commands are executed verbatim by `tests/e2e/run_add_a_kit.py`.
`tests/unit/test_kit_template.py` checks schemas, declarations, scope, controls,
independent answers and source mutations. No Kit-local CLI or installer exists.

Portable verification copies only the sealed data directory, preserving its
name. Re-running checks still requires Python, the matching Core and this Kit's
unchanged code. No original run directory is needed.

Responsible people review the source, meaning and scope. `review sign` currently
returns `CHECK_UNAVAILABLE`; this tutorial supplies no review receipt and creates
no file under `review/`. Laboratory work: `NOT_PERFORMED`.
