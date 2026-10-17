# S4d retained evidence

Source/runtime freeze: `9fe5fb0f4b7814c227ce94dbe2ae7ac62b1e0115`.
Specification-owner patch: `f7f5886`, synchronized as `db3e165`; only spec/ and
archive/ were imported. The final report is `S4D-REPORT.md` at the product root.
Official GitLab CI 未执行；GitHub CI 未运行。

| Record | Meaning |
| --- | --- |
| `red/` | Real public-CLI failure before the new development-seal rule |
| `green/`, `preflight/` | Focused identity cases; schema, structure, generated-doc and spec checks; real ZIP refusal |
| `mutants/` | Two private source mutations are caught: rejecting dev-tree again, ignoring a different release |
| `legacy-b1/`, `legacy-byte-comparison.json` | All thirteen historical B1 files, unchanged from s4b; incompatible old format remains a negative |
| `rebuild/` | Current public CLI creates B1 and checks the literal hand answer, then moves away its original run |
| `independent-record-check.json` | Independent file/event hashes; old events 9 and 22 lack actual call parameters, current events retain them |
| `paths/`, `path-reference-check.json` | 37 generated authoring files match byte-for-byte; historical inventories and source-commit bytes remain intact |
| `doc-links.json` | Eight architecture links resolve to the declared Kit sources |
| `dependencies/` | A newly created venv, exact pins, pip provenance and package checks |
| `installed/` | Offline wheel build/install; 13 public verify cases, including five intended refusals |
| `payload/` | 836 source-commit, checkout, wheel and installed files compared using independent SHA-256 calculations |
| `example-logs/` | Normalized source/new-installation example requests and all seven CLI receipts per run; original-byte hashes retained |
| `full/` | One final complete suite with the existing local Primer3; consult its actual RESULTS.json |

The commands and UTF-8 stdout/stderr are retained, including nonzero expected
refusals. Logs normalize only local paths using SOURCE/WORK/USER/TEMP labels.
Sealed records are not normalized. Evidence-local `-text` attributes preserve
their original bytes and raw command-output whitespace.

The old B1 fails before release-id comparison. Independent hashes still match;
its call-record payloads lack params and params_digest required by the current
schema. No unrecorded parameter was inserted into the historical seal.
The new B1 is a calculation of the reverse complement of AGTCAGAA. Reverse first
to AAGACTGA, then complement to the hand answer TTCTGACT. Its cards explicitly
say the development-tree package is not release evidence.

Reproduction entry points in this directory:

- `run-preflight.py NEW_WORK`: actual source checks and expected release refusals.
- `check-record-bytes.py`: independently recompute the current/old record hashes
  and check the known historical omissions; never overwrite a differing result.
- `run-mutants.py NEW_WORK`: mutate only private source copies; two failing tests
  are expected evidence that those changes are detected.
- `run-path-comparison.py --legacy-repo LOCAL_SOURCE --work NEW_WORK`: compare the
  pinned historical authoring helper with the explicit-repository version in
  disposable copies; never regenerate the live Kit. The legacy repository must
  already contain the pinned rule commit; this script does not fetch anything.
- `check-installation.py NEW_INSTALL_WORK`: use an already provisioned fresh venv,
  build/install its source wheel with no index/dependency downloads, and run B1
  and identity boundaries. Provision only with the separately authorized locked
  dependency helper `tests/e2e/run_s4b_install.py` and new evidence/work paths.
- `preserve-and-rebuild.py NEW_WORK` documents the one-time s4b-to-s4d archival
  transition; it deliberately refuses existing backup/output directories.

The complete suite uses `tests/e2e/run_s4b_full.py` with a new work/evidence path
and explicit existing Primer3 executable. It preserves older tracked evidence
that legacy tests regenerate. No failed attempt is replaced with a passing one.

This is developer-run known-case and synthetic-input evidence. It is not heldout
evaluation, human user testing, laboratory work or approval of a release ZIP.
No README disclosure was completed, checker changed, protected schema changed,
remote CI invoked, push performed or main merged.
