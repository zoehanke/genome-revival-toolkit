# Evaluator guide, draft

This source package prepares reproducible inspection of DNA Design Core. Begin
with the root README for purpose, audience, installation, the synthetic result,
AI disclosure, license and CI status. The current build is incomplete while
user-supplied disclosure or Kit-specific documentation is outstanding.

1. Read [installation and running](installation.md).
2. Run the fixed synthetic example and inspect [validation and limits](validation.md).
3. Review [architecture](architecture.md) and [Kit contribution rules](adding-a-kit.md).
4. Follow [source build and fresh-environment verification](build.md).

## Minimal observation workflow

This source-tree example imports synthetic colony observations, runs Revival
Evidence, and seals a bounded analysis report. It does not perform an experiment.
Use the project's existing development environment; no installation is required.
From the product root, prepare a new working directory:

```powershell
$python = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:PYTHONPATH = (Resolve-Path .\src).Path
New-Item -ItemType Directory -Path dist\minimal-goal-new -ErrorAction Stop | Out-Null
Set-Location dist\minimal-goal-new
```

Save these two files here as UTF-8. Choose a new working directory on a repeated
run; keep earlier receipts. Save the synthetic records as `observations.json`:

```json
{
  "observations": [
    {"id": "fusion1", "group": "fusion", "colonies": 9, "unit": "colony"},
    {"id": "control1", "group": "control", "colonies": 31, "unit": "colony"}
  ]
}
```

Save the complete request as `goal-request.json`:

```json
{
  "schema": "goal-v1",
  "version": 1,
  "parent_digest": null,
  "original_request": "Compare synthetic colony counts without inferring experimental function.",
  "sources": [
    {
      "source_id": "observations",
      "from": "observations.json",
      "as": "artifact",
      "input_origin": "researcher_observation",
      "declared": {}
    }
  ],
  "declared_context": [],
  "targets": [{"id": "t1", "role": "analysis", "required": true}],
  "constraints": [
    {
      "id": "present",
      "check": "check.goal.output_present@0.0.0",
      "params": {},
      "target": "t1",
      "source_quote": "Compare synthetic colony counts without inferring experimental function.",
      "status": "active"
    }
  ],
  "intents": []
}
```

Run this complete PowerShell 7 sequence. `template instantiate` returns a receipt;
the pipeline is only its `result.draft` object. `ConvertTo-Json -Depth 100`
preserves nested references when saving that object; `pipeline submit` rejects
the whole receipt.

```powershell
& $python -X utf8 -B -m dna_design_core.application.cli run create demo-run
$declared = & $python -X utf8 -B -m dna_design_core.application.cli goal declare --run demo-run --request goal-request.json | ConvertFrom-Json
@{
  goal_digest = $declared.result.goal_digest
  source_id = 'observations'
  observation_origin = 'SYNTHETIC_NOT_EXPERIMENTAL'
  comparisons = @(@{ experiment_group = 'fusion'; control_group = 'control' })
} | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath template-request.json -Encoding utf8
$receipt = & $python -X utf8 -B -m dna_design_core.application.cli template instantiate revival-evidence.assess_observations --run demo-run --request template-request.json | ConvertFrom-Json
$receipt | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath template-receipt.json -Encoding utf8
$receipt.result.draft | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath pipeline.json -Encoding utf8
& $python -X utf8 -B -m dna_design_core.application.cli pipeline submit --run demo-run --request pipeline.json
& $python -X utf8 -B -m dna_design_core.application.cli run execute --run demo-run
& $python -X utf8 -B -m dna_design_core.application.cli judge --run demo-run
$sealed = & $python -X utf8 -B -m dna_design_core.application.cli seal --run demo-run | ConvertFrom-Json
$sealed.result.present_files
& $python -X utf8 -B -m dna_design_core.application.cli verify demo-run
```

Goal declaration returns `goal_digest`, which the template request reuses.
`assessment.json` reports the count difference `-22` and functional revival as
`INSUFFICIENT`; no PCR, genotype or functional observation was supplied.
Use the exact files returned in `present_files`. `from` is consumed during import: stored sources contain
a run-relative copy path and a calculated file hash. Keep `declared: {}` when no
additional source properties are declared. Version `0.0.0` is this source-tree
Core version, not a claim of a published release.

Bind every template output to an existing goal target of the producer's role.
[Validation and limits](validation.md) explains
what execution and sealing establish.

No wet experiment, human trial or release approval is asserted by this draft.
Official GitLab CI 未执行. GitHub CI 未运行 for S1e.
