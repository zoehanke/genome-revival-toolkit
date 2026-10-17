---
name: revival-evidence
description: Compare submitted colony observations with control claims or supplied local PCR predictions. Use for evidence limits and unperformed tests. For DNA construction or assay design, use the corresponding design Kit.
---

Register observation files as researcher_observation artifacts in a goal. Read [README.md](README.md) for accepted records and current Core contracts.
For observations alone, instantiate `revival-evidence.assess_observations`.
For an Identity output file, instantiate `revival-evidence.assess_predictions`
with `predictions_source` naming that registered file. The command returns a
receipt: extract `result.draft`, save that object as a UTF-8 pipeline JSON file,
then pass that file to `pipeline submit --request`. The entire receipt is not a
pipeline. Execute, judge, seal and verify through Core. A complete copyable
command sequence is in [the evaluator guide](../../docs/judges/README.md).
Present only files returned by seal. Report each claim with its local subject and its stated evidence limit. Keep predicted results separate from submitted observations.
A positive record missing `observed_band_bp` must be presented as explicitly
incomplete (`INSUFFICIENT`); report that reason even when controls are missing.
`control_status` accepts exactly `passed`, `failed`, or `unknown`; omit the field
to retain the default `unknown`. Other values are input errors.
Report a complete, hash-bound positive-band mismatch as `CONTRADICTED`, even
without confirmed passing controls. A negative mismatch needs reported
`passed` controls; otherwise report `INSUFFICIENT` because PCR may have failed.
Present unconfirmed controls separately from that local mismatch, using the
report's `unverified` entries. Neither statement authenticates an experiment.

<!-- GENERATED:START -->
### evidence.assess_observations

Apply sourced claim evidence tables; report bounded conclusions and unperformed tests.

Inputs: document (document, required).
Parameters: `{"additionalProperties": false, "properties": {"comparisons": {"items": {"additionalProperties": false, "properties": {"control_group": {"minLength": 1, "type": "string"}, "experiment_group": {"minLength": 1, "type": "string"}}, "required": ["experiment_group", "control_group"], "type": "object"}, "type": "array"}}, "type": "object"}`.
Outputs: assessment (analysis).
Final checks: evidence.check_record_consistency.
Does not establish: Experimental success (实验已成功).; Functional revival (功能已复活).; Authenticity of submitted observations (观察本身真实).

### evidence.check_record_consistency

Check recorded source parsing, truth-table conclusions and exported report against fixed rule snapshots.

Inputs: none.
Parameters: `{"additionalProperties": false, "properties": {}, "type": "object"}`.
Outputs: verdicts.
Final checks: none.
Does not establish: Experimental success (实验已成功).; Functional revival (功能已复活).; Authenticity of submitted observations (观察本身真实).

### evidence.parse_observations

Parse supplied observations; retain missing counts and record generated IDs.

Inputs: observations (artifact, required), predictions (artifact, optional).
Parameters: `{"additionalProperties": false, "properties": {"observation_origin": {"minLength": 1, "type": "string"}}, "type": "object"}`.
Outputs: document (intermediate).
Final checks: evidence.check_record_consistency.
Does not establish: Experimental success (实验已成功).; Functional revival (功能已复活).; Authenticity of submitted observations (观察本身真实).

### Template parameters

- goal_digest (string): Current declared goal digest.
- source_id (string): Registered observations artifact source.
- observation_origin (string): Submitted source declaration, e.g. SYNTHETIC_EXAMPLE.
- comparisons (array): Explicit experiment_group and control_group comparisons.
<!-- GENERATED:END -->
