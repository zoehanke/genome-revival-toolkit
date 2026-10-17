# Constructed schema fixtures

Each JSON file wraps `data` with an independently assigned `expected_valid` and
`oracle`. These are not product documents and are not generated from schemas.
Valid examples were transcribed from D/A/E field tables using synthetic values.
Each schema has one missing-required-field (or wrong-type for optional config)
negative and one unknown-field negative. Additional boundary examples cover
CHECK fields, document contracts and NOT_APPLICABLE.

A14 follow-up: 28 groups in `tests/contract/a14-coverage.json` add 91 constructed
cases. Each group includes at least one positive and two negatives, covering
minimal internal shapes and their propagated event locations. JSON Patch cases
test syntax only; no patch is applied. Template checks cover whole-value spelling,
declared type/description and value-only placement, not instantiation.

SPEC 8ad9c44 A2/A9 makes authorship optional, so the retained no_authorship case
now expects acceptance. SPEC 12c4274 A14 sets literal origin.ref to null. These
are requirement changes, not relaxed checks to accommodate implementation.

All short sequences are synthetic. Digests are constructed syntax examples, not
hashes of user material or evidence of execution. Review names and dates are
blank. No fixture is a review record; none is stored under a `review/` directory.

Run: `python -X utf8 -B tools/check_schemas.py` from the S0 code directory.
The validator uses an explicit local registry with no network retrieval callback.
