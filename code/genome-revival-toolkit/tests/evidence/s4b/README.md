# S4b retained evidence

This directory records source-wheel installation, not a release ZIP approval.
Source runtime/build commit: `49dd32b37bbdf55ef5c4f6c33af497bb649e3658`.
The source manifest records that commit and all selected file bytes.
Official GitLab CI was not executed. GitHub CI was not run.

## Final-run evidence

| Directory | Meaning |
|---|---|
| `install-final/` | Second newly created venv, exact package pins, pip source hashes, dependency check |
| `install-final-runtime/` | Offline wheel build/install, isolated module location, installed console commands, four-Kit driver |
| `payload-final/` | Every selected source-commit/checkout/wheel/installed file compared; raw canonical manifest |
| `development-metadata-green/` | 24 identity, cold-build and original release checks after the source-metadata fix |
| `static-final/` | Structure, schemas, generated documentation and specification alignment |
| `source-mutants/final-three/` | Three deliberate code changes detected, including removal of the source-layout fix |
| `full-final/` | Full local suite rerun; consult its actual outcome, not an earlier count |
| `wsl/` | Read-only availability check; Windows reports WSL is not installed |

Installed-case receipts, artifact inventories and the physical one-byte manifest
negative are in `example-logs-final/` and `installed-manifest-final/`.
The first environment and all failed attempts remain available too.

## Earlier attempts are not silently counted as passing

- `identity-red/`: package-shaped run incorrectly recorded dev-tree.
- `wheel-build-01/`: isolated build could not locate its build module.
- `full/`: first full suite failed after source .egg-info was misclassified as
  installed metadata. Original stderr/stdout, including cascaded failures, remain.
- `development-metadata-red/`: independently constructed source .egg-info input
  reproduces that same source/installation distinction before its fix.
- `zip-gate/`: ad-hoc driver assumed three total placeholders; actual checker
  output identified four and three existing personal-path findings. Its mistaken
  driver assertion is retained. `zip-gate-confirmed/` records the actual refusal.
- `source-mutants/attempt-01*`: mutation-driver setup matched two substrings;
  no code mutant ran. Later actual mutant failures are separately recorded.
- `legacy-bundle-negative/`, `legacy-source-check/`: an old bundled B1 seal is
  rejected before release-id comparison. Independent hashes match, but events 9
  and 22 omit parameters required by the current event schema. This real
  historical-format failure is not a passing ZIP test; no old record was edited.
- `install-01/`, `wheel-install/`, `installed-cases-01/`, `example-logs/`,
  `payload/`, `installed-manifest-negative/`: first successful installation
  before the subsequently discovered development-layout correction. They do not
  replace the final-code rerun.

## Reading and reproduction

Each `commands.json` points to UTF-8 stdout/stderr and records exit codes.
The exact public arguments are retained. Expected negative inputs remain
nonzero, including the initial wrong guide, wrong source hash, changed manifest
and deliberately broken source copies. Source mutators only change private
copies; the one-byte negative restores the new test installation exactly.

The checked-in orchestration entry points are:

- `tests/e2e/run_s4b_install.py`: creates a NEW work directory and venv, installs
  only the two locks with `--no-deps`, records pip provenance and checks packages.
- `tests/e2e/run_s4b_installed.py`: launch with the new environment's Python and
  `-I`, outside the checkout; uses installed synthetic examples and public CLI.
- `tests/e2e/run_s4b_full.py`: retains a full local suite in a NEW evidence
  directory and preserves old committed evidence rewritten by legacy tests.
- Scripts in this directory: per-file independent SHA-256 comparison, code
  mutations, actual installed-manifest mutation, log retention and WSL query.

Use new output directories on repetition. Never overwrite old failed runs.
All paths in the text copies are normalized to `<SOURCE>`, `<WORK>`, `<USER>`,
`<TEMP>` or the more specific label named by that command. JSON/repr path escaping
is normalized too. Raw private artifact inventories are hashed before that text
normalization; sealed records and binaries themselves are not rewritten or
committed here. The canonical release manifest is retained byte-for-byte.
The local .gitattributes uses the existing chain-story line-ending policy.
Raw .txt stdout/stderr keep their intentional trailing spaces and carriage
returns, and are excluded from SOURCE whitespace formatting only. Python and
Markdown formatting, science gates and release checks remain enabled and
unchanged; archive-format-before retains Git's earlier rejection of raw output.

The package hash table comes from pip, not a newly invented checksum authority.
The original locks pin versions only. Pip 24.0 was bootstrapped offline from
Python's own ensurepip wheel; ten exact dependencies were installed from PyPI.
Later source-wheel building/installing used `--no-index` and no dependency
resolution. No Primer3, dataset, sequence service or official GitLab access was
performed by these installation commands.

All DNA/observations are existing synthetic regression fixtures. Their scientific
answers and independent checkers were not changed. These are developer-run
computational checks, not heldout evaluation, human user trials, real genotypes
or laboratory experiments. Construction routes remain PLANNED/NOT_PERFORMED.
The real project release ZIP was blocked and clean_env_verify --execute was not
executed. Full conclusions and pending specification issues are in S4B-REPORT.md
and QUESTIONS.md E1-E4.
