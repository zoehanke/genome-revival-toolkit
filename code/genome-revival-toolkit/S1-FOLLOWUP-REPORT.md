# S1.2 follow-up checkpoint

Implemented the requested D3/D11 contracts on s1-minimal-slice, starting at
96db7d0. Runtime/test source commit: 36d28121909e61a5f675481f61c9b0de0bbd21da.
Final local suite: 137 passed, 0 failed, 0 skipped; spec_lint hard findings: 0.
Nested model-call parameter recording remains Q13, with UNKNOWN blocking sealing.
This is evidence for owner review, not a declaration that S1.2 has passed.

## Changes and general basis

| Original behavior | Requirement and general correction |
|---|---|
| Document ports required schema_ref and rejected a Kit's inline schema | D3/A2: input/output document ports require exactly one schema_ref or inline schema. Freeze the complete declaration; validate input binding and output before persistence. Invalid input uses PLAN_INPUT_UNBOUND; invalid output uses CAPABILITY_OUTPUT_INVALID; no error code added |
| ACTION had no knowledge accessor; CHECK's view accessor did not enforce owner | D3: one ctx.knowledge(pack) path for both roles. Match the frozen catalog owner/pack, then read the content store, which rehashes bytes and returns a fresh object. Cross-owner reads are denied; changed frozen bytes yield STORE_CORRUPT, category INTEGRITY. Live rule edits do not replace frozen rules. Remove view.knowledge from implementation and protocol |
| Bad model input/parameter names and missing product ports loaded; model agreement was unavailable | D3: validate names and shared material product at metadata discovery, isolating the invalid Kit. Compare a completed step's recorded product against a model invoked with named inputs and recorded parameters. Compare sequence, topology and ends; annotations remain subject to their separate checks |
| A materials reference always needed an index and could only provide one material | D3: an unindexed earlier materials port can feed a materials input; indexed item references retain material semantics. Reject concatenated lists of sources/steps and literal material lists during zero-call admission, with INVALID_INPUT and an explicit materials explanation |
| Three probes directly imported external module names and failed for real Kit | D1/D3: extract Invoker's existing implementation loader into engine.loading.Loader; runtime and the three probes use that exact implementation. No import shim, skip or weakened assertion; Kit fixture paths are resolved from the owning Kit root |
| SPEC and schema differed at inputs[].schema and outputs[].schema | Regenerate field comparison, add 10 manually constructed schema fixtures and rerun full validation. No new state, event or CLI verb; no Kit or biology edits |

Embedded schemas are checked as Draft 2020-12. Metadata discovery still imports
no implementation. Frozen knowledge names use the existing catalog pack ids,
for example kit:<owner>/knowledge/<file>.json; no extra registry was added.

## Final validation of the source commit

| Run | Actual result | What it establishes |
|---|---|---|
| unittest discover -s tests -v | 137 passed, 0 failed, 0 skipped; 358.868 seconds | 60 structure, 61 unit, 4 integration, 12 public-CLI end-to-end tests; existing S1/S1.1 expectations remain unchanged |
| check_schemas | 35 schemas; 237 fixtures: 77 valid and 160 invalid; 0 findings | Four new valid alternatives and six new malformed/both/neither document-port fixtures follow hand-specified D3 expectations |
| check_structure | 0 findings | Import, vocabulary, contribution, fixture and invariant-inventory checks |
| spec_lint | 0 hard findings, 17 soft legacy-context notices; 0 field differences | Both missing schema fields are now represented. SCHEMA-DIFFERENCES.json was regenerated; its zero-difference contents remain unchanged |
| docgen --check | 0 differences | Check directory and Skill generated listing match declarations |
| Real S3 Kit contract probe | 3 passed, 0 failed, 0 skipped | Atomic-call rule, verdict/exception boundary, decorator/export agreement all load through the shared seam |
| New manual mutations on disposable copies | Four distinct mutations detected by assertion failures | Bypassing inline output validation, owner restriction, model comparison, or whole-collection resolution breaks constructed regressions |

The real Kit probe used the clean S3 branch at
eb7d11d9a3a0f5bb21dc9b18cba3d219ea4e31db. It exercised metadata loading and
source assertions only, not the Kit's scientific workflow. Its existing
view.knowledge consumer must be changed to ctx.knowledge by S3's owner when
integrating; this task did not edit kits/ or the S3 checkout.

The first complete run before adding Q13's boundary test was 136/136 in
413.856 seconds, retained in tests-01.txt. The final complete run above includes
that boundary test. Counts are unique test cases, not sums of repeated runs.

Invariant inventory remains 94 covered / 25 pending, totaling 119 with no overlap.
Only evidence references were updated. No pending item was promoted. The three
S1 pending items remain undeclared-write coverage, external I/O detection
coverage, and the cross-platform matrix; all original reasons are preserved.
SKIPS.json is empty. S0 migration spikes were not run or counted as passes/skips.

## Six groups of raw positive/negative evidence

All paths below are local ignored artifacts, not source commits. The five CLI
groups retain request-N.json, raw stdout/stderr, exit codes, receipts.json, the
run directory and SUMMARY.json. They contain 18 scenario summaries and 80 CLI
calls; their run.created records identify the source commit above.

| Group | Retained raw output | Constructed success/failure boundaries |
|---|---|---|
| 1. Inline document ports | [summary](dist/s1-followup2-final/inline/SUMMARY.json); [valid receipts](dist/s1-followup2-final/inline/valid/receipts.json); bad_input/receipts.json and bad_output/receipts.json in the same group | Integer count 7 reaches the consumer; string output is rejected without persistence; a consumer maximum of 5 rejects 7 before calling consumer. Both/neither and malformed schemas are separate metadata negatives |
| 2. Frozen knowledge | [summary](dist/s1-followup2-final/knowledge/SUMMARY.json); [frozen receipts](dist/s1-followup2-final/knowledge/frozen/receipts.json); corrupt/receipts.json and foreign/receipts.json | Live value 42 still reads frozen 7 for ACTION/CHECK; mutating a returned copy does not persist. Frozen-store edit to 9 fails INTEGRITY. Unit tests also load a real second synthetic package and deny access, and exercise Core-only reads |
| 3. Model convention | [summary](dist/s1-followup2-final/model/SUMMARY.json); [one-base receipts](dist/s1-followup2-final/model/one_base/cli/receipts.json); [nested boundary](dist/s1-followup2-validation/03-model-nested.txt) | Equal paths and annotation-only differences PASS. ACGT versus ACGA, changed topology, or changed ends FAIL. Missing input/parameter names and missing/non-material product ports are isolated. Named offset=2 is passed, unrelated unused=13 is not passed to model |
| 4. materials ports | [summary](dist/s1-followup2-final/materials/SUMMARY.json); [collection receipts](dist/s1-followup2-final/materials/collection/receipts.json); [rejection receipts](dist/s1-followup2-final/materials/lists_rejected/receipts.json); [missing/order controls](dist/s1-followup2-validation/04-materials-green.txt) | Ordered 4+4 nt materials produce 8; explicit second item produces 4. Source/step list concatenation is rejected with no new journal facts. Whole-collection lineage/replay PASS; missing one or reversing order yields FAIL using existing comparisons |
| 5. Shared loading seam | [temporary-Kit receipts](dist/s1-followup2-final/loader/external/receipts.json); [real Kit probe](dist/s1-followup2-validation/05-loader-real-kit-final.txt) | External Kit is visible, executes and disappears when no longer supplied. All three original assertions pass for real S3 Kit; changed implementation bytes are still rejected |
| 6. Whole-suite/schema alignment | [complete suite](dist/s1-followup2-validation/tests-final.txt); [schemas](dist/s1-followup2-validation/check_schemas-final.txt); [structure](dist/s1-followup2-validation/check_structure-final.txt); [spec_lint](dist/s1-followup2-validation/spec_lint-final.txt); [field differences before fix](dist/s1-followup2-validation/fields-before.json) | Original 2 missing fields become 0; positive and deliberately invalid fixture expectations remain independently specified. Existing scanner mutations still detect violations |

Direct file inspection of ten generated cases is recorded in
[INSPECTED-FILES.json](dist/s1-followup2-final/INSPECTED-FILES.json). It checks
the stored count document, ordered material sequences, exported scalar files and
original model-path product JSON. Model recomputation does not persist its
alternative products into the run store. These are computational checks, not
qualified material deliveries: missing mandatory annotation/CDS checks still
return UNKNOWN and prevent material sealing.

Original red evidence remains in dist/s1-followup2-validation/:
01-inline-red.txt, 02-knowledge-red.txt, 03-model-red.txt,
04-materials-red.txt, 04-materials-after-bind.txt,
05-loader-real-kit-red.txt and 06-spec-before.txt. The original real-Kit probe
fails all three tests with ModuleNotFoundError. New test-authoring corrections
are disclosed in DEVIATIONS.md; their failing records were not deleted.

Mutation evidence: dist/s1-followup2-mutations/RESULTS.json and transcripts;
dist/s1-followup2-mutations-owner-02/RESULTS.json completes the owner control.
The first owner mutation caused an indexing error in the new test, so it was
not counted as detected. An explicit HALTED assertion now exposes it as a real
assertion failure; both records remain. Repetitions are not independent success
evaluations. The new fixtures are developer-constructed regressions with
independent oracles, not heldout or blind agent assessments. No human-corrected
scientific result was counted as independent success.

## Authorized builtin exception: complete diff

The user permitted exactly this material read call site plus its helper import.
kernel.references holds the extracted resolver; execution and that call site
share it. Existing lineage/replay verdict conditions are unchanged.

```diff
--- a/code/genome-revival-toolkit/src/dna_design_core/capabilities/builtin/checks.py
+++ b/code/genome-revival-toolkit/src/dna_design_core/capabilities/builtin/checks.py
@@ -4,3 +4,3 @@ from pathlib import Path
 from dna_design_core.kernel.public import (Outcome, capability, make, core_version, document_id,
-    material_id, file_sha256, event_hash, GENESIS, loads, require_schema, ToolkitError)
+    material_id, file_sha256, event_hash, GENESIS, loads, require_schema, ToolkitError, resolve_reference)
 from ..declaration import check
@@ -124,3 +124,3 @@ def _resolve(view, ref):
     if port in outputs['documents']:return view.document(outputs['documents'][port][index])
-    if port in outputs['materials']:return view.material(outputs['materials'][port][index])
+    if port in outputs['materials']:return resolve_reference(view,ref,view.candidate['catalog'])
     if port in payload['values']:return deepcopy(payload['values'][port])
```

## Reproduce and remaining boundary

From this product directory using the supplied interpreter:

```powershell
& './.venv/Scripts/python.exe' -X utf8 -B -m unittest discover -s tests -v
& './.venv/Scripts/python.exe' -X utf8 -B tools/check_schemas.py
& './.venv/Scripts/python.exe' -X utf8 -B tools/check_structure.py
& './.venv/Scripts/python.exe' -X utf8 -B tools/docgen.py --check
& './.venv/Scripts/python.exe' -X utf8 -B tests/e2e/run_s1_followup2.py --case model --out dist/new-s12-model
& './.venv/Scripts/python.exe' -X utf8 -B tools/run_s12_mutations.py --out dist/new-s12-mutations
```

Use fresh output directories. The CLI case choices are inline, knowledge, model,
materials and loader. tools/probe_capability_contracts.py --kit-dir accepts the
owner's external Kit directory for all three original assertions.

| Status | Scope |
|---|---|
| Verified | Local public CLI/API contracts, frozen data access, modeled product comparison, collection bindings, loader seam, generated files, validation tools and specified failure controls |
| Simulation only | Constructed short materials and constant independent model answers. No physical construction or laboratory experiment |
| Not done | Real Kit scientific workflows, blind/heldout evaluation, routing evaluation, Linux matrix, downloads, installation, push, merge, release/frozen-candidate integration. 官方 GitLab CI 未执行; GitHub CI 未运行 |
| Uncertain / owner decision | Q13: nested call.recorded lacks parameter values. It remains UNKNOWN and blocks sealing until a specification decision. Code independence of real scientific models requires scientific review; this test suite does not certify it |

Only code/ changed, including the explicitly authorized capability-v1 schema
and minimal builtin exception. No user DNA, private paths, extra dependency,
event/state/verb, human approval or external-service request was introduced.
S1.2 closure belongs to the specification owner.

# S1.1 follow-up checkpoint (historical)

The specification owner closed S1.1 at tag s1.1-closed, commit 9a7fd36.
The original implementation/evidence record is retained below.

Implemented the goal-constraint corrections from prompts/s1-followup.md.
Runtime commit: a8a48c5844b497595419cd7f8a4642ae0fc77c64.
Final complete suite: 115 passed, 0 failed, 0 skipped.
At this historical checkpoint S1.1 was awaiting the specification owner's review.

## Changes and general basis

| Previous behavior | Required behavior and correction |
|---|---|
| Stored goal schema required origin before the program filled it; supplied origin was accepted | D2: requests omit origin and any supplied value is INVALID_INPUT. The program derives user_quoted or host_derived before validating the stored shape |
| Constraint parameters and references failed only during judgement, becoming CHECK_UNAVAILABLE | D2: goal declaration and amendment validate the recorded CHECK identity, exact version, evaluates_constraint and parameter schema before writing goal facts. Parameter errors point to their JSON Pointer, including unknown keys |
| output_present only checked output-file presence | D7: optional fields lists required document keys. Existing keys pass; missing keys produce FAIL rather than UNKNOWN. No fields retains the previous presence-only behavior |
| Goal schema errors suggested pipeline-v1 | Contextual recovery names goal-v1 in both the receipt and nested failure, including non-object requests. Existing error codes are reused; errors.json was not changed |
| Pending C4/E3 reasons assumed OS enforcement | Reasons now follow SPEC acc5aed: AST and post-call detection, no v1 sandbox, external I/O cannot be prevented. INV-I2 remains unchanged and cross-platform validation is left to S4 |

Reference and parameter validation uses the run's frozen catalog metadata.
It does not invoke a CHECK during goal declaration. Stored goal-v1 still
requires origin; the protected schema was not weakened. Existing valid request
builders now omit the derived field; previous result assertions remain intact.
The original supplied-origin case is retained as an explicit rejection test.

## Validation

| Scope | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Structural/contract tests | 60 | 0 | 0 |
| Unit tests | 44 | 0 | 0 |
| Integration tests | 4 | 0 | 0 |
| End-to-end tests | 7 | 0 | 0 |
| Complete discovery | 115 | 0 | 0 |

The final full run took 315.012 seconds using the provisioned project Python.
An earlier full run also passed 115 tests; its log remains separate.

- check_structure: 0 findings.
- check_schemas: 35 schemas, 227 fixtures, 0 findings.
- spec_lint: 0 hard findings, 17 soft findings in historical/negative contexts;
  35 schema alignments, 0 field differences, 0 unresolved fields.
- docgen --check: 0 differences.
- The three required regressions plus two boundary cases were rerun from
  committed runtime a8a48c5. Their run.created events record that exact commit.
- Positive and negative fields fixtures use the hand-constructed SPEC B1 answer.
  No expected scientific value was generated by the tested implementation.
- Boundary controls include supplied origin values user_quoted, host_derived
  and null; wrong parameter spelling/type/item type; missing checks, ACTION
  references, CHECKs not marked evaluates_constraint, version mismatch;
  invalid amendment parameters; malformed goal objects; and absent output fields.

All new cases use the public CLI and inspect generated files.
Only synthetic data was used. Old S0 migration spikes are outside this S1 suite
and were not run; they are not counted as skipped or passed here.

## Retained raw regression outputs

Each directory contains immutable request-N.json inputs, receipts.json with
raw stdout/stderr and exit codes, SUMMARY.json, and the run directory.

| Required regression | Raw output | Result |
|---|---|---|
| Request includes origin | [origin receipts](dist/s1-followup-final/origin/receipts.json) | 4 commands; all supplied origin values rejected as INVALID_INPUT |
| Invalid constraint parameters | [parameter receipts](dist/s1-followup-final/invalid_params/receipts.json) | 10 commands; bad declarations/amendments rejected before new goal facts |
| fields includes sequence for B1 | [B1 receipts](dist/s1-followup-final/fields/receipts.json) | 7 commands; field checks PASS, sealed JSON matches the constructed answer, verify succeeds |

Additional controls:
- [Missing-field receipts](dist/s1-followup-final/fields_missing/receipts.json):
  6 commands; both goal-field verdicts FAIL, sealing returns exit code 10.
- [Goal-schema recovery receipts](dist/s1-followup-final/schema_recovery/receipts.json):
  4 commands; recovery names goal-v1, never pipeline-v1.
- [Full test log](dist/s1-followup-validation/tests-final.txt),
  [structure log](dist/s1-followup-validation/check_structure.txt),
  [schema log](dist/s1-followup-validation/check_schemas.txt), and
  [field alignment](dist/s1-followup-fields.json).

Original red development cases remain in dist/s1-followup-red-01-origin,
dist/s1-followup-red-02-invalid-params, dist/s1-followup-red-03-fields and
dist/s1-followup-red-04-schema. They belong to different development states;
they are retained failures, not independent success-rate evidence.
Generated outputs are ignored and were not committed.

Reproduce a case with the project interpreter:

```powershell
& './.venv/Scripts/python.exe' -X utf8 -B tests/e2e/run_s1_followup.py --case origin --out dist/new-origin-case
& './.venv/Scripts/python.exe' -X utf8 -B tests/e2e/run_s1_followup.py --case invalid_params --out dist/new-parameter-case
& './.venv/Scripts/python.exe' -X utf8 -B tests/e2e/run_s1_followup.py --case fields --out dist/new-fields-case
```

Choose new output directories to preserve prior evidence.

## Boundaries

Only code/ changed. No spec, protected schema, registry error file, Kit,
biology module or S1b implementation was changed. No error code was added.
No download, installation, push, merge, real scientific Kit evaluation or wet
experiment was performed. Human review has not been filled or implied.

Official GitLab CI 未执行. GitHub CI 未运行.
