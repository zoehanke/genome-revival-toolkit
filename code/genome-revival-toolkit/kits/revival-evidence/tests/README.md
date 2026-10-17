# Development tests

Tests live in repository test layers; this Kit contains no separate runtime entry.

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -X utf8 -B tools\check_structure.py
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests\structure -p test_revival_evidence_structure.py
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests\contract -p test_revival_evidence_contracts.py
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests\unit -p test_revival_evidence.py
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests\integration -p test_revival_evidence_mutations.py
```

The check's declared PASS/FAIL fixtures use constructed counts 9 and 31. The FAIL
fixture reverses the difference sign. It is actually executed, rather than checked
for shape alone. Manual mutations disable source-parse comparison, assessment
comparison and failure aggregation on disposable Kit copies. Each mutation causes
a false PASS on a retained negative case and is detected by the expected FAIL.

The independent oracle is `tests/oracles/revival_evidence.py`. The public-CLI runner
is `tests/e2e/run_revival_evidence.py`; instructions are in the Kit README.

Round 2 also checks count/size consistency in the shared prediction handoff,
zero versus multiple predicted products, inline document schemas, the actual
claim_reported constraint and rejection of a missing requested theme. A real
Invoker test changes live rule data after run creation and confirms that action,
check and offline verify still use the frozen data through ctx.knowledge.

S3b adds `tests/unit/test_revival_evidence_scoped.py` and
`tests/e2e/test_revival_evidence_scoped.py`. The unit layer covers the five-row
construction, both "any control" rows over missing/zero/positive controls,
explicit group selection, partial-count missingness, omitted comparisons,
computed global progress and the perfect reported input that still cannot support
functional revival. It checks both existing HTML/Markdown views and source status.
The positive-control row is manually changed to `SUPPORTED`; the fixed expectation
rejects it. The independent oracle also rejects it when given that mutated rule
file, since its S3b states follow the user's construction rather than table output.

The CLI layer runs the original five cases and six S3b cases. Each of the eleven
cases creates a run, declares a goal, instantiates a template, submits, executes,
judges, seals, verifies, then verifies only a copied seal with the run moved away.
The omission case removes `comparisons` from the assessment step's parameters.
Set `GRT_S3B_EVIDENCE` to a fresh directory to retain requests, command receipts,
portable seals and independent-oracle results from the full suite.
