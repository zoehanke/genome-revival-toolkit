# S0 official-source checks

Initial Codex check, 2026-10-16: read-only official project/distribution pages. No binary,
package, source archive or user sequence was downloaded. Reading a license or
upstream claim is not local functional verification or human review.

## Native .dna writers (R7)

| Candidate | License / evidence | Round-trip status |
|---|---|---|
| sgffp | MIT; retain copyright and permission notice. Official code documents SgffWriter.to_file/to_bytes. [License](https://github.com/merv1n34k/sgffp/blob/master/LICENSE), [project](https://github.com/merv1n34k/sgffp) | Upstream claims substantial format support. Local write/read and desktop round trips: **not performed**. |
| AutoSnapGene | MIT. Official overview describes binary-file editing and construction utilities. [License](https://github.com/kalekundert/autosnapgene/blob/master/LICENSE.txt), [overview](https://autosnapgene.readthedocs.io/en/latest/) | Exact writer coverage and fidelity guarantee: **not found in opened overview**; not tested locally. Secondary candidate only. |

sgffp's reading/writing guide identifies limits: recompressed LZMA bytes can differ,
attachment XML whitespace can differ, and new traces cannot reproduce an absent
original encoding. Therefore byte identity is not a universal promise. The guide
shows version 0.22.1; no runtime version is selected here.
[Reading/writing and fidelity](https://merv1n34k.github.io/sgffp/guide/reading-writing.html).

Upstream README distinguishes newer regenerated cache blocks from retained legacy
caches, while the guide gives a simpler omission statement. Pin a version and test
actual supported block classes before adopting it. S0 does not certify native
format fidelity or native application compatibility.
[Version-aware description](https://github.com/merv1n34k/sgffp).

## Primer3 executable (R8)

Primer3's manual states GPL version 2 or later. Its authors distinguish embedding
source/linking libraries from calling a separate executable and interpreting its
output; the latter can use a separate caller license. This is the authors'
published explanation, not a determination about a future distribution.
[Official manual, license explanation](https://primer3.org/manual.html#licenseExplain).

Executable redistribution still requires license/notices and the applicable
corresponding-source provision of GPL section 3, such as accompanying complete
source or a qualifying written offer. Merely shipping an executable does not
remove that obligation. No Primer3 executable is bundled in S0.
[Repository license](https://github.com/primer3-org/primer3/blob/main/LICENSE).

Official v2.6.1 release assets include **primer3-2.6.1_exe_for_windows.zip**
(32 MB), plus source archives. Asset existence was read from GitHub's expanded
assets page; contents, architecture and execution were **not tested**.
[Official release asset list](https://github.com/primer3-org/primer3/releases/expanded_assets/v2.6.1).
The official manual also documents a MinGW build route. No compiler or program
was installed. [Windows build instructions](https://github.com/primer3-org/primer3/blob/main/src/primer3_manual.htm).

Do not assign one license to every program in the release archive: release notes
identify Amplicon3 as GPL-3. A future redistribution needs an exact file inventory
and corresponding notices/source. [Release notes](https://github.com/primer3-org/primer3/releases/tag/v2.6.1).

## JCS candidate (R6 / P3)

Selected implementation for the probe: **rfc8785 0.1.4**, Trail of Bits;
Apache-2.0. Official metadata describes a pure Python implementation with no
dependencies and UTF-8 byte output. [Project](https://github.com/trailofbits/rfc8785.py),
[release metadata](https://pypi.org/project/rfc8785/0.1.4/).

Redistribution conditions include the license, retained notices, notices of
modification, and applicable NOTICE attribution. Some implementation portions
derive from an Apache-2.0 reference implementation.
[License](https://github.com/trailofbits/rfc8785.py/blob/main/LICENSE).

At the initial Codex check, no implementation was installed and 0 vectors ran.
The follow-up user report attributes a separate authorized installation of
rfc8785==0.1.4 and 3 passing Windows vectors to Claude in an isolated environment.
Codex did not reproduce it; Linux remains untested. See probes/RESULTS.md.
The source lookup verifies licensing; no product canonicalizer was written.

## Disposition

Published facts above are verified by source reading. Native round trips and
Primer3 executable behavior remain unverified here. JCS Windows results are
attributed to Claude; Codex reproduction and Linux comparison remain unperformed.
Product LICENSE selection remains Q06. Official GitLab CI 未执行.

## S1b local dependency facts, 2026-10-16

Worktree `.venv`: Python package metadata reports jsonschema 4.26.0,
rfc8785 0.1.4, Biopython 1.88 and sgffp 0.21.0. No package was installed and
no network request was made. Only the first three packages are selected in
`requirements-biology.lock`. sgffp is not imported: S1B-Q3 records the dependency
boundary before potential use. Its license statements above are earlier source
checks, not a new license assessment.

The installed `Bio.SeqIO.SnapGeneIO` parser accepts in-memory binary `.dna`
packets and extracts sequence, topology and supported feature/primer packets.
Unsupported native blocks are not an assertion of complete format fidelity.
S1b uses only constructed binary fixtures and does not read user DNA files.
No native writer, binary redistribution or desktop round trip is included.


## S1b integration measurements after c8cc70a

Local measured versions: Python 3.12.4, jsonschema 4.26.0, rfc8785 0.1.4,
Biopython 1.88. User explicitly excluded sgffp; no import/install was added.
S1 kernel interface files are populated, as recorded in dependency-seam.json.
No external source lookup or network request was made for this continuation.

Actual runtime Primer3 execution through Context.run_external produced version
2.6.1 and executable SHA-256
19a546a0166fd979c41317e45696de1b383ab5fa21ec362bcc5053b2068b6e5f.
Version probe and computation are observed separately by an integration spy;
thermodynamic-file hashes are in integration/primer3-runtime.json. The separate
independent CLI oracle was rerun on all seven synthetic cases. Maximum absolute
Tm difference remains 0.00041349 C, inside three-decimal printing precision.
No binary, system package or user DNA was copied into the repository.

## S1b round2 local measurements, 2026-10-16

The specification owner's existing s1b-closed tag resolves to a6905eb. This round
adds preparation inventories and data drafts only; no Kit implementation runs.
The legacy current worktree no longer contains the four Kit script directories.
Read-only git show at bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 supplied those
files; selected shared Core sources remain fixed at 750bf4849b818be00f28684513ef19c01d901bcb.
Source/function spans are measured in docs/kit-prep/source-inventory.json.

Legacy JSON rules contain 24 records: 13 Cut Plasmid, 5 Revival Evidence,
3 Construct and 3 Genome Identity. All 24 have source labels; missing-source
records: 0. Source labels are not independently verified claims. The selection
file has 519 physical lines and 9 marker records, not 519 rules. Splitting kan
by host yields 10 selection rules. Retiring no-template-exemption and retaining
an explicit old-code control-outgrowth policy yields 25 new rule drafts total.
All are draft/unverified without a human receipt. The unsourced rehearsal rule
is a deliberately invalid probe, not an invented legacy missing-source row.

The existing 35 schemas and 227 schema fixtures pass unchanged. Rehearsing
58 draft documents yields 3 Schema-invalid and 1 A14-invalid documents:
2 actual ordered-material template blockers and 2 deliberate negative probes.
Six contract questions remain recorded; syntactically accepted schema_ref
strings do not establish that those domain schemas are registered.

Local unittest discovery without GRT_PRIMER3_CORE ran 163 tests: 162 passed,
1 registered NOT_PERFORMED skip, zero failures/errors. The same optional test
ran separately with the configured real Primer3 executable and passed without
skipping. The configured wrong-fingerprint guard uses a mock and proves the
original assertion still fails; it is not numerical verification. Four new
source mutations were caught by independent assertions. Raw logs and counts:
tests/evidence/s1b-round2/validation.json. All commands set PYTHONPATH=src.

No network lookup, new dependency, binary, Kit execution or user DNA was used.
Scientific source verification and all laboratory actions remain NOT_PERFORMED.
Official GitLab CI 未执行；GitHub CI 未运行。

## C2 measured local facts

Owner tag s1-closed resolves to acc5aed. The requested s1-minimal-slice head
dabe464 was merged as e47e17e. Four conflicts were resolved by retaining both
scientific/public exports and metadata modules. The S1 reverse-complement
function body was preserved; its independent hand answers and the five existing
S1b pure-layer contracts passed after merging. Shared AGENTS.md was added by
commit 4cdb59f while this task was running; it was read and preserved.

The Catalog now lists all seven D2 core goal-constraint kinds with no catalog
problem: the preexisting output_present and six new CHECKs. Each new CHECK has
an exported parameter schema and two independent construction fixtures. All 12
fixtures were run through actual admitted producers and the S1 Invoker/read view,
yielding the specified six PASS and six FAIL results without changing run bytes.
Six source mutations in temporary copies were each caught by test assertions.

The public application API created a run, declared six constraints, executed a
literal interval replacement and a sequence report, and judged them. The five
DNA constraints passed and claim_reported failed because the report lacks a
structured claim/status. Independent missing annotation/CDS/biological-sanity
checks remain unsatisfied; no full scientific seal acceptance is claimed.
The report and check data are retained in tests/evidence/s1b-c2. Only synthetic
DNA and literal JSON were used. No source lookup, dependency installation, native
binary, real Kit implementation, laboratory action or new gate closure.
Official GitLab CI 未执行；GitHub CI 未运行。

C2 complete discovery: 200 tests, 199 passes and one registered NOT_PERFORMED
skip, zero failures/errors. The same configured real-Primer3 test then passed
separately. One newly added public-API test ran separately and passed. These
cover 201 distinct methods across the two discoveries; the backend rerun is not
an additional distinct method. Structural/schema/generated-document checks pass;
spec_lint reports zero hard findings and 17 soft findings. Raw logs are in
tests/evidence/s1b-c2. All commands use PYTHONPATH=src.

## S4a offline local facts, 2026-10-17

The provided worktree now uses s4a-release from integration-1/fc04e41. Python is
3.12.4; the existing environment reports setuptools 83.0.0, jsonschema 4.26.0,
rfc8785 0.1.4 and Biopython 1.88. requirements-release.lock additionally pins the
observed dependency closure: attrs, jsonschema-specifications, referencing,
rpds-py, NumPy and typing-extensions. This is local distribution metadata, not
a fresh installation or cross-platform availability test. No network lookup or
installation was performed. THIRD_PARTY.md is generated from those local records.

The existing complete Apache-2.0 LICENSE has 11,358 bytes and SHA-256
cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30.
The checker pins that baseline full-text hash and rejects a one-byte mutation.
It reads actual tracked-file sizes, enforces the 50,000,000-byte ceiling, checks
selected and tracked prohibited extensions, verifies the README's seven required
sections and pinned dependency/version declarations, and counts pending markers.
Current project source yields five markers and no F10/hygiene finding; its state
is INCOMPLETE. This is not evidence that a release candidate has been assembled.

An offline build-backend test changed only a temporary copy's VERSIONS toolkit
value to 0.0.7. Actual generated package metadata reported 0.0.7. No environment
was created or installed by that test. Two builds of one independent source
fixture produced identical ZIP bytes and release ids with fixed timestamps.
Six deliberately broken release-tool variants were caught by assertions.

The new B1 source-mode example produced the independent answer TTCTGACT from
AGTCAGAA and verified its portable seal after the original run location was
unavailable. Its sealed example has release_id=dev-tree, reflecting actual Core
behavior. The fresh-environment script's plan is NOT_PERFORMED and creates no
environment. Product/Kit scientific functionality and external acceptance were
not tested by S4a. Official GitLab CI 未执行；GitHub CI 未运行。

S4a final complete discovery ran 246 methods: 245 passed, one registered Primer3
test was unperformed, zero failures/errors. With the actual executable configured,
that same optional method passed separately. These are not 247 distinct methods.
The suite includes 16 new release unit methods and two new release integrations.
Structural/schema/generated-doc scans have no findings; spec_lint has zero hard
findings and 17 soft findings. First partial discovery was interrupted to freeze
THIRD_PARTY as source input; its partial log is retained and not counted as a
completed run. The final source checker reports five pending markers, exit 2.
An actual project build refused to create an archive, as required for incomplete
source. A separate constructed missing-GitLab-statement probe also returned FAIL.
