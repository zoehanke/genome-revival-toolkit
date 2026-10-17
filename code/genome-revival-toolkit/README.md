# Genome Revival Toolkit

## Purpose

Genome Revival Toolkit provides local DNA sequence calculations, explicit goals,
recorded execution, read-only checks and portable computational result records.
This development tree contains DNA Design Core and shared biology capabilities.
The scientific Kits are being developed separately; this package does not certify
an experimental DNA construction or a biological revival.

## Audience

Laboratory researchers and iGEM evaluators can run the synthetic example and
inspect its retained result. Developers can inspect capability declarations and
implement a Kit against the same execution and checking interfaces.

## Installation and running

Use Python 3.12.4 for the currently measured Windows environment. Package metadata
permits Python 3.11 and later; other interpreters and Ubuntu remain to be tested.
The following commands describe a fresh installation. Dependency downloads and
the fresh-environment verification step require separate authorization in this task.

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-release.lock
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps .
.\.venv\Scripts\python.exe -m dna_design_core.application.cli doctor
```

For the already provisioned developer environment, run commands from this folder
with `PYTHONPATH=src`. [Installation details](docs/judges/installation.md) distinguish
source-tree checks from an installed-package test. No executable, extension module
or third-party binary is included in the source ZIP. Optional Primer3 remains an
external installation, configured by the operator; it is never downloaded by Core.

## Reproduce the main results

The independent hand answer to the synthetic eight-base reverse complement is
`AGTCAGAA` to `TTCTGACT`. After installation:

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -X utf8 -B examples/run_example.py --out dist/example-installed
```

The runner clears child `PYTHONPATH`, executes the public command line, checks the
literal answer, seals the result, makes the original run unavailable and verifies
a portable copy. It refuses to overwrite an earlier result. To deliberately test
the source tree in the provisioned environment, add `--source-tree`; that result
is labelled as source execution, not fresh-installation evidence.

`examples/sealed/b1/` contains a retained synthetic development example. Its
`release_id` is `dev-tree`; it is a computational-record example, not release
identity evidence. An installed wheel now checks its bundled release manifest
against the wheel's RECORD and checks every listed payload file once per process
when creating or verifying a run. New installed runs record that manifest's
SHA-256. A changed or missing manifest is an error, never a fallback to dev-tree.
Verification with an installed release requires the sealed release_id to match;
use a source checkout to inspect retained dev-tree examples. A source wheel can
test installation while disclosure remains incomplete; it does not approve or
replace the gated release ZIP.
[Validation and limits](docs/judges/validation.md) gives the measured scope.

## AI use disclosure

Repository development reports record AI-assisted code and test preparation.
The inspected Core declares local Python calculations and an optional local
Primer3 process. These source records do not establish the team's full AI use.

- Development and workflow-host models and roles (stated by the team; the software itself bundles no model): OpenAI Codex (GPT family) wrote most of the code and tests; Anthropic Claude (Claude Code) wrote and maintained the specification, ran independent verification and isolated trial runs; Google Gemini was used during a mid-project refactoring and development phase; DeepSeek was used in early testing; a model inside the Trae AI coding environment was used with an earlier version to design knockout plasmids. Kimi and Doubao were not used for development. Model versions as recorded by the team (dates were not recorded): Codex models 5.6 Sol, 6 Astra and 6.1 Sol (the order in which they replaced one another was not recorded); Claude Sonnet 5.5, in a single Claude Code session; Gemini 3.7 Flash; DeepSeek V4 Flash and V4 Pro; inside Trae, DeepSeek V4 Flash and Kimi K3 were used, with an earlier version of the software, to design knockout plasmids (Kimi was not used to develop the software).
- Training or fine-tuning: none. The team did not train or fine-tune any model, and the software contains no machine-learning model and no model client; it performs deterministic local calculations and can call a locally installed Primer3.
- Evaluation procedure, independent results and retained evidence: All evaluation uses synthetic data only. Expected answers are fixed before running, either by construction (random sequences are generated first, then the edit is decided, so the answer follows from the construction) or by hand calculation; they are never generated by the software under test. Independent standard-library scripts recompute donors, primer binding sites, PCR product lengths and evidence conclusions from the delivered files and compare them with the software's output. The complete local test suite passes on Windows. In addition, an isolated AI agent that received only the user documentation and a natural-language task completed the Construct, Genome Identity and Revival Evidence workflow on new synthetic materials (two rounds); its results were checked against pre-computed answers, and failures and workarounds were kept. Every sealed example can be verified offline, including after copying only the sealed directory. Retained evidence is in `tests/evidence/` and in the example packages. Not done: wet-laboratory validation, trials by human users, evaluation on AI hosts other than Claude and Codex, tests on Linux, and a run of the official GitLab CI (no runner is available there).
- Known model limitations and human responsibilities: AI-written code and specifications can look plausible and still be wrong, so every scientific result is recomputed by independent scripts on synthetic data, and the specification, tests and evidence are kept in the repository for review. The software only computes and plans: laboratory steps are always reported as PLANNED / NOT_PERFORMED, and nothing here claims that a construct, assay or revival works in the laboratory. Thermal parameters such as primer melting temperature have not been validated against experiments, and Construct does not claim its primers are thermally suitable. The Revival Evidence rule tables were drafted by AI and their sources are recorded but not yet verified by a human. A host AI that chooses among the Kits can route a task wrongly or bypass the software's checks; only results sealed through the public route with a passing `verify` should be treated as checked output. Human responsibility: this disclosure was reviewed by the iGEM Tianjin 2026 team on 2026-10-17.

The release checker counts these markers. Any remaining marker means the
release is incomplete. No human review or team agreement is asserted here.

## License

Source code is distributed under [Apache-2.0](LICENSE). The release checker uses
the pinned SHA-256 of the complete Apache-2.0 text. [THIRD_PARTY.md](THIRD_PARTY.md)
is generated from exact dependency pins and locally available distribution
metadata. Dependency binaries and Primer3 are not redistributed in this ZIP.

## CI status

Official iGEM GitLab CI has not been executed. 官方 GitLab CI 未执行。
GitHub CI has not been run for this release-engineering branch. Local tests do
not replace Windows and Ubuntu CI on an exact release commit.

## Build a source package

Run from this source folder with the provisioned environment:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -X utf8 -B tools/build_release.py --third-party-only
.\.venv\Scripts\python.exe -X utf8 -B tools/check_release.py --report dist/release-check.json
.\.venv\Scripts\python.exe -X utf8 -B tools/build_release.py --out dist/release
```

The checker must pass before a ZIP is created. Missing disclosure or architecture
information remains incomplete; the build does not silently replace it. Files
are selected by `ship.json`, sorted and stored with fixed timestamps. The ZIP,
its SHA-256 and a canonical release manifest are emitted together. The manifest
contains versions, build identity, exact file hashes and locked dependencies;
its SHA-256 is the release identity. The manifest excludes its own file entry.

[Build and fresh-environment procedure](docs/judges/build.md) gives the complete
sequence and the separate authorization point for installation. Human approval,
CI evidence, scientific Kit acceptance and upload are later release steps.

## Developer verification

In the complete development checkout, before freezing a candidate:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -X utf8 -B tools/check_structure.py
.\.venv\Scripts\python.exe -X utf8 -B tools/check_schemas.py
.\.venv\Scripts\python.exe -X utf8 -B tools/docgen.py --check
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 -B tests/oracles/release_mutations.py
```

Full repository tests also read internal specification/evidence files; those are
not all shipped in the evaluator ZIP. The evaluator's installed example is a
separate check. An unset Primer3 configuration is a registered unperformed test,
excluded from pass counts. Set GRT_PRIMER3_CORE to an authorized local executable
when deliberately running that optional integration test.

## Further reading

- [Evaluator guide](docs/judges/README.md)
- [Architecture and pending Kit overview](docs/judges/architecture.md)
- [Adding a Kit](docs/judges/adding-a-kit.md)
- [Runnable add-a-Kit tutorial and minimal template](docs/developers/add-a-kit.md)
- [Developer source-map notes](docs/developers/README.md)
- [Capability protocol](skill/SKILL.md)
