# Construct

Design a donor for one explicit replacement or deletion on a supplied linear
reference. Preparation uses actual template PCR, either as one complete donor
amplicon or as fragments joined by two linear Gibson operations. The independent
model runs first and shares no preparation algorithm with design_donor.

Required inputs: original reference, cargo source, edit/cargo intervals,
homology-arm length and primer length. Gibson also needs overlap length. PCR
needs an existing complete donor-template file and its selected interval.
All coordinates are zero-based and half-open. Equal cargo bounds mean deletion.
No locus, arm length or laboratory acceptance threshold is inferred.

## Use

Use the existing `grt` goal, template, pipeline, execute, judge, seal and verify
verbs. The templates are `construct.prepare_gibson` and `construct.prepare_pcr`.
Their params_schema describes exact inputs; keep source IDs different from step
IDs. Keep model-bearing design_donor as a direct pipeline step in these templates.

The standard templates export original.gb, edited.gb, donor.gb and
identity-handoff.json under the corresponding run work directories. Seal also
returns `identity_handoff.json`, `identity_original.gb` and `identity_edited.gb`
as delivery files. Both delivered references retain the exact GenBank bytes
whose hashes appear in the handoff. The handoff
contains exactly the D11 schema, reference-file byte hashes, regions and primers.
It contains no embedded reference sequences. Reference files must travel with
the handoff. Register those three delivered files for
`genome-identity.from_handoff`, with explicit topologies and selected primer ids.
Its primers come directly from D11; no primer FASTA or edited draft is needed.
The executor records file hashes without Kit logging code.

Junction primers use sequence outside each homology arm and sequence inside the
cargo. Both pairs are simulated on edited, original and residual donor DNA.
For deletion, one external flanking pair distinguishes original/edited sizes.
An optional primer_file artifact accepts a strict primer-set-v1 JSON document;
supplied primers are assessed unchanged. A residual donor product produces an
explicit warning and a failing junction check, even if edited DNA also has a band.
Every binding site is retained; a single amplicon does not hide repeated sites.

Exact binding cores and full tailed oligos are retained as materials and documents.
Primer length is an explicit geometry parameter. Thermodynamic acceptance remains
a separate core obligation. No wet-lab preparation is performed.

## Reproduce developer evidence

From code/genome-revival-toolkit with the existing .venv:

```powershell
$env:PYTHONPATH = "src"
$env:GRT_PRIMER3_CORE = "<path-to-installed-primer3_core.exe>"
.\.venv\Scripts\python.exe -X utf8 -B tools/check_structure.py
.\.venv\Scripts\python.exe -X utf8 -B -m unittest tests.integration.test_construct -v
.\.venv\Scripts\python.exe -X utf8 -B tests/e2e/run_construct.py tests/evidence/s5a-construct/new-cli-run
.\.venv\Scripts\python.exe -X utf8 -B tests/oracles/construct_verify.py tests/evidence/s5a-construct/new-cli-run/gibson/run
```

The e2e script is a test harness outside this Kit. It invokes public CLI verbs,
retains each request, exit code, stdout/stderr and failed seal, and refuses to
overwrite previous evidence. It is not a product entry point. The independent
oracle uses only Python standard library and reads actual saved output files.
Dependencies remain pinned by requirements-biology.lock; no installation added.
Historical construction expectations use seed 20261017 and source intervals,
never Kit outputs. `tests/oracles/construct_assets.py` is retained unchanged;
its historical template exporter must not overwrite current handoff templates.
Current capability decorators and their exported declarations define the interface.

## Delivery boundary

S1c added shared checks and artifact staging. Original failed runs and questions
remain historical evidence; they do not describe current availability.
An unavailable or failing mandatory check still prevents sealing. Explicit
primer-length acceptance does not establish thermal quality: no undeclared Tm
window or salt condition is inferred. Read `not_verified` in the actual manifest.

Laboratory preparation and PCR: PLANNED / NOT_PERFORMED.
Does not establish: 实验室制备成功、转化效率、整合位点的真实性、功能复活。
Official GitLab CI 未执行；GitHub CI 未运行。
