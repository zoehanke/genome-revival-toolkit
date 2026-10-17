# Revival Evidence

Compare submitted colony counts, controls and local assay observations with sourced
claim boundaries. Output role is `analysis`; no DNA material is created or read.
Predictions, submitted observations and program checks retain separate meanings.

## Reproduce

Run from `code/genome-revival-toolkit/` in this worktree:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -X utf8 -B tests\e2e\run_revival_evidence.py --out dist\s3-example
```

Choose a new output directory on another run. The runner uses only public Core CLI
verbs. It saves requests and receipts, submits the two-step template, executes,
judges, seals and verifies each case, then copies each sealed directory and verifies
it with the original run moved away. It also invokes the independent oracle.
Results are under the selected output's `*/portable/<seal_id>/assessment.json`.
`SUMMARY.json`, `receipts.json` and `oracle-receipts.json` retain the checks.

For an existing report, the independent checker needs only standard library:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -X utf8 -B tests\oracles\revival_evidence.py --observations kits\revival-evidence\examples\b3.csv --rules-dir kits\revival-evidence\knowledge --assessment PATH_TO_ASSESSMENT_JSON
```

Add `--predictions PATH` when comparing an expected-results handoff. This checker
does not import Core or Kit code. Source observations and rule files determine its
answers; it recomputes each conclusion, group total and count difference.
Add `--comparisons PATH` with the submitted JSON array of comparison pairs to
check that selection too. Otherwise the report's declared comparison pairs select
the groups; their counts and conclusions are still recomputed from source records.

For the five original cases plus all S3b cases, use:

```powershell
.\.venv\Scripts\python.exe -X utf8 -B tests\e2e\run_revival_evidence.py --scoped --out dist\s3b-example
```

## Records

CSV requires `group,colonies`, or `group,measure,value` with
`measure=colony_count`. Optional columns: `id`, `unit`, `role`, `plated_cells`,
`plated_volume_uL`. UTF-8 BOM is accepted. Missing or blank IDs receive deterministic
`row_<data-row>` IDs, with collision suffixes; each generated ID enters `unverified`
and a tool self report. Missing counts remain `null` through aggregation and
comparison. Counts must be nonnegative integers.

Explicit `unit=colony` is needed for count differences. Without a unit the
comparison is `UNKNOWN`. A raw count difference is not normalized efficiency.
Equal reported plating volumes are recorded, without certifying comparability.
`role=inactivated_donor_control` declares a no-outgrowth control: reported colonies
contradict that local absence claim. Ordinary growth controls need not be negative.

### Scoped fusion-plate outgrowth

`fusion_plate_outgrowth` concerns only the reported counts in the explicit
`comparisons` pair (`experiment_group`, `control_group`). It uses the same
known/positive count facts as `control_no_outgrowth`; no comparison is inferred
from group names or observation roles. Omitting the assessment action's
`comparisons` parameter, or supplying `[]`, produces no new outgrowth conclusion.
The templates still take an explicit `comparisons` array.

| Experiment count | Control count | Scoped state |
|---|---|---|
| Missing | Any | `NOT_TESTED` |
| 0 | Any | `CONTRADICTED` |
| Positive | Missing | `INSUFFICIENT` |
| Positive | Positive | `INSUFFICIENT` |
| Positive | 0 | `SUPPORTED` |

For groups containing several records, the existing comparison totals apply:
any missing count keeps that group's total missing. No known subset substitutes
for the group total. This reports growth and absence in the selected groups;
it establishes no mechanism, donor origin, control-cell death or authentic record.

Supported local conclusions appear first in `assessment.json`. Both global
claims keep their original states and explain which local claims are supported
and what remains unestablished. The existing consistency-check summary lists each
supported local claim, its subject and its scoped reason before the original
"Does not support" limits in both `views/runcard.html` and `views/report.md`.
This uses the existing Core views and merges the presentation into the existing
check summary, without a new renderer, presentation field or check.

This rule comes from the user's 2026-10-17 decision, option B. Its project-contract
source remains `unverified`; the team must declare the source and review it.
No verification receipt or human approval is asserted. Even with reported growth,
zero control colonies, matching PCR with passing controls and a positive functional
test, `functional_revival` and `whole_genome_elimination` remain `INSUFFICIENT`
or `NOT_TESTED` under their existing rules.

JSON accepts `observations`, optional `genotype_results`, `functional_results`, and
`observation_origin`; see [local observations](examples/local_observations.json).
A minimal synthetic colony-count JSON uses the same fields as CSV:

```json
{
  "observations": [
    {"id": "fusion1", "group": "fusion", "colonies": 9, "unit": "colony"},
    {"id": "control1", "group": "control", "colonies": 31, "unit": "colony"}
  ]
}
```

Save it as `observations.json`. The [complete command sequence](../../docs/judges/README.md)
imports this file and reports the difference `9 - 31 = -22`; colony counts alone
remain insufficient for functional revival. These are synthetic observations.

Local genotype rows identify sample, assay and background, report a result and
assay-control state, and supply the reference hash for interpretable comparison.
`control_status` accepts exactly `passed`, `failed`, or `unknown`. Omission defaults
to `unknown`; strings such as `pass` or `not_reported` are not accepted aliases.
An absent or mismatched reference hash leaves the local conclusion `INSUFFICIENT`.
Unconfirmed passing controls prevent a matching report from becoming `SUPPORTED`.
A complete positive band that conflicts with the hash-bound local prediction
(unexpected presence or size outside the declared tolerance) is `CONTRADICTED`
for any reported control status. A negative result that conflicts with a predicted
band is `CONTRADICTED` only with reported `passed` controls. Without them it is
`INSUFFICIENT`: reaction failure cannot be distinguished from a prediction mismatch.
Control uncertainty is separately listed in `unverified`, with sample, assay and
background. This compares submitted records; it does not authenticate a PCR band
or establish an actual genotype or whole-genome conclusion.
Positive bands require their size. A positive record with missing or null
`observed_band_bp` is explicitly reported as an incomplete `INSUFFICIENT`
local observation, including when predictions or controls are also missing.
It is never treated as a negative band or usable complete observation.
The default size tolerance is zero; a supplied
`band_tolerance_bp` is a declared observation condition, not a calibrated threshold.

The optional `predictions` input is a registered artifact using S5b's handoff:

Use `revival-evidence.assess_predictions` and set `predictions_source` to the
registered Identity output file. The observations-only template stays unchanged.
Both templates bind files through existing Core source references; no plan edit
or rewritten prediction document is needed.
`template instantiate` returns a receipt, not a pipeline file. Save only its
`result.draft` object as UTF-8 JSON, then submit that file with
`pipeline submit --request`. Submitting the whole receipt is rejected.

```json
{"schema":"identity-expected-results-v1","assay_id":"assay1","backgrounds":[{"id":"original","reference_sha256":"1111111111111111111111111111111111111111111111111111111111111111","primer_pair":["forward","reverse"],"expected":{"product_count":1,"product_bp":1000,"status":"DISTINGUISHABLE"}}]}
```

`primer_pair` contains exactly two primer IDs. `product_count=1` requires a positive
integer `product_bp`. Zero or multiple products require `product_bp:null`;
`product_count` distinguishes these cases. Multiple products and `UNDETERMINED`
predictions cannot support a local absence conclusion. Comparisons concern reported local agreement only.
The JSON above is an interface fixture. The S1d public-CLI chain separately
checks an actual sealed Identity output and its unchanged file hash.

## Rules and checks

`kit.json` declares capabilities, rule files, a parsing-to-assessment template and
English text. Each `rule-v1` contains a claim, an observation context and a finite
truth table. Conditions use D12 operators. Each table row identifies its parent
source with `source_ref`; [SOURCES.md](knowledge/SOURCES.md) lists supports and limits.
Changing a team's claim table changes interpretation without changing the engine.
All shipped sources are project contracts with `verification_status:unverified`.
They express this project's interpretation boundary, not established biology.

Action and check both read hash-checked, frozen rules through `ctx.knowledge(pack)`.
Editing live rule files after run creation does not change that run's interpretation.
Final consistency checking reparses registered observation bytes, recomputes the
assessment with the same frozen rules and checks the exported report.
The check produces a Core verdict; `SUPPORTED`, `INSUFFICIENT`, `CONTRADICTED`,
`NOT_TESTED` are separate domain conclusions.

Two [unattributed legacy candidates](knowledge/drafts/unattributed.json) remain
`draft` and `unverified`, excluded from contributions. They concern support for
unmodelled genotype observations and a primer-quality prerequisite. A missing
source prevents loading; team attribution is still required.

## Current integration contracts

The branch includes `integration-1b` at `7b1ca09`. Example goals use
`check.goal.claim_reported` with `claim=functional_revival` and
`pointer=/conclusions`. This verifies that the topic has a reported state;
the Kit consistency check separately verifies the bounded interpretation.
Requests omit constraint `origin`; Core derives it from `source_quote`.

The normalized observation and assessment document ports carry inline JSON
schemas. Their field contracts, including the prediction handoff, freeze with
the capability declarations in the run catalog. No Kit schema registry or generic
JSON-value fallback is used. Draft rules remain outside declared contributions.

Superseded integration questions are retained as history in repository QUESTIONS
and DEVIATIONS. The original goal, loading and document-contract workarounds have
been removed. The public-CLI S1d chain also covers actual producer-to-consumer delivery.

## Evidence boundary

B3 uses synthetic fusion count 9 and control count 31: difference `-22`;
`functional_revival=INSUFFICIENT`. PCR, genetic evidence and functional validation
without supplied observations enter Not done as `NOT_PERFORMED`.
`does_not_establish` includes experimental success, functional revival and observation
authenticity. No wet experiment occurred. The specification owner closes S3;
team review of interpretation rules is separate. Official GitLab CI 未执行；
GitHub CI 未运行.
