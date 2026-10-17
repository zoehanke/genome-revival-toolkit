# S0 follow-up disposition

## S1d usability fixes, 2026-10-17

No specification or protected-resource change. C10's host GenBank-reader
workaround is superseded by direct D11 delivery/consumption; C12's producer-role
restriction is retained. Current instructions and executed evidence are in
S1D-REPORT.md. Older sections below record their original branch/checkpoint,
not current availability. Existing scientific expectations and independent
oracles remain unchanged. C11's single-run viewer and C13's pre-step resolution
state gap were not expanded by this task.

## S5a Construct, 2026-10-17

No intentional specification deviation or reduction of required checks.
Work is limited to kits/construct, its tests/evidence and this task's reporting
sections. The worktree remains s5a-construct on integration-1; no merge or push.

Unfinished acceptance: the core cannot stage an artifact output; five required
checks are missing; primer quality has no profile-level argument binding.
Therefore complete seal/verify, copying a sealed package for verification, and
D7 inherited/introduced/undetermined CDS verdicts are not completed. Generated
handoff bytes and their actual executor-recorded hashes are retained. Construct
to real Genome Identity consumption is not executed on this branch, whose
Genome Identity Kit has no implementation. These are not replaced by toy success.

The separate diagnostic run omits the artifact target only to expose every
construct-role obligation; it is explicitly not the accepted delivery route.
The full templates retain the handoff artifact and preserve their actual failure.

Kit-local provisional fields and primer geometry are S5A-P1/P2 in QUESTIONS.md,
with matching PROVISIONAL comments. All primer lengths and overlaps are explicit
inputs; no unstated laboratory threshold is used. General Kit-local algorithms
are registered under S5A-P3 for the specification owner's later placement decision.

Actual input source has 205 lines at the recorded old commit, rather than the
prompt's earlier inventory count. The measured source and new lines are retained
in MIGRATION-LOG.md. Initial development failures remain in focused-01.txt and
execution-01/02/03 evidence (the first file is named first-execution.txt); the
CLI import-path failure remains in cli-01-summary.txt.

The complete local suite ran 243 tests: 242 passed, one error, no skips. The
remaining error is the shared readonly-check test resolving Kit fixture paths
against the Core root (S5A-Q4), confirmed by the actual FileNotFoundError and
fixture-resolution.json. No Kit fixture was duplicated into a global directory
and no S1-owned test was edited to hide the error.

The full-suite goal-constraint test automatically rewrote the historical S1b-C2
check-fixtures.json event-basis hashes. Initial worktree was clean; all non-basis
data was confirmed unchanged. This run's output is preserved under this task's
full-generated-s1b-c2-check-fixtures.json, and the old evidence file is restored
to its original tracked contents. No other task's evidence is committed here.

Known not defended: arbitrary multi-locus/circular donor editing, inferred strain
loci and laboratory-specific gel resolution are outside this explicit linear
single-edit model. Laboratory work is PLANNED / NOT_PERFORMED.
Official GitLab CI 未执行；GitHub CI 未运行。


## S1.2 scope and retained development failures

SPEC 96db7d0 and prompts/s1-followup2.md authorize only the capability-v1
protected schema change. No other schema, errors, profiles, vocabulary, spec,
Kit or biology file was changed. The user's follow-up explicitly authorized a
minimal builtin exception: one material-reference call site plus its public
helper import, sharing kernel.references with execution. Verdict conditions
and all existing expected values are unchanged. The complete two-line diff is
included in S1-FOLLOWUP-REPORT.md. No S1b conflict resolution was attempted.

The first model probe's input declarations accidentally shared one Python dict;
renaming a model input also renamed the original input. The fixture constructor
now copies the two explicitly constructed declarations. A new diagnostic
assertion incorrectly counted normal format-export call records as model replay;
it now checks the original/model identities specifically. The first CLI loader
probe inspected result rather than the existing result.description envelope;
its request/receipt remains retained. These were new test-authoring defects,
not changes to production acceptance criteria or old test expectations.

Q13 remains a specification question about nested model invocation arguments.
No invented event field, missing-check exemption or successful verdict replaces
the absent evidence. The implementation reports UNKNOWN for that case.

Direct runtime dependencies remain rfc8785 and jsonschema at the pinned versions.
No download, package installation, network service, push or merge was used.

## S1 implementation notes

The S1 source-import contract follows the owner's D2 changes 4daa3cd and
9e170f9: request-only from, actual-byte hashing, relative copied paths, no
persisted original path, and INVALID_INPUT for changed content under one id.
No specification file was changed.

Direct third-party imports in S1 runtime and validation tools are restricted to
the two entries in requirements.lock. The earlier development checker directly
imported referencing; it now uses jsonschema's local resolver with remote
resolution rejected. The existing S0-only spikes still import Bio in
sequence_sample.py and tm_sample.py. These historical probes are outside the
S1 runtime and were not run for S1; they are not covered by the S1 dependency lock.

The static vocabulary scanner previously rejected literal state=None. A14 and
receipt-v1 explicitly permit null before a run or plan exists. The scanner now
accepts that one documented case; no state word or test expectation was changed.

The uninstalled development command executes application/cli.py directly. It
uses the same main function registered as grt in pyproject.toml and requires no
installation, PYTHONPATH setting, network access or lookup of an old product.
Human review signing remains unavailable in S1; no review was fabricated.

Integration exposed a loader defect: multiple functions in one implementation
module reused the first cached function. The loader now caches the module and
looks up the declared function for each call. The failing multi-check judgement
and all positive/negative check controls are retained.

Official GitLab CI 未执行. GitHub CI 未运行. No real Kit scientific validation.

Current authority: SPEC 8ad9c44 and corrected A14 in 12c4274. No spec files were
edited. The earlier five field discrepancies and all 16 x-s0-gap occurrences
are resolved by those spec changes; field differences and gap markers are now 0.
Required granularity and optional authorship follow A2/A9. JSON Patch belongs to
goal.amended; actor declared_by belongs to input.registered. No new event fields.

The no_authorship fixture changes expectation solely because the spec now makes
it optional. Existing literals, profile and diff fixtures were updated to A14
null/object/array forms. New constructed negatives remain in the fixture set.
53 structural/contract tests and 8 migration tests pass, with no skipped tests.
Current invariant inventory is 119: 32 static, 87 pending, including INV-F10.

The user changed S0 review to a conversation reply after reading only sections
1 and 2. No signatures, dates or review responses were filled. LICENSE remains
unchanged and pending. User's copy/rotation and selected-guide decisions are
recorded as decisions, not unimplemented product behavior.

Claude's authorized isolated P3 execution is attributed to the user's report:
3 Windows vectors passed; Linux untested; Codex did not reproduce it. Original
Codex probe records are preserved. No downloads, push or merge were performed.

## Original fb8e911 record (historical, superseded where noted above)


No protected spec, decision, prompt or review file was changed. No product
algorithm or Kit was implemented. No push or merge was attempted.

* User explicitly authorized D3/D20 to govern CHECK.offline, document input
  schema_ref and authorship on capabilities/rules/templates. Five appendix field
  differences remain visible in SCHEMA-DIFFERENCES.json. They are pending review,
  not developer edits to the spec.
* Unspecified inner field shapes remain x-s0-gap/Q07, not invented structures.
  Atomic/composite representation and first-event prev remain questions.
* D1 table/TOML and D3/D11 duplicate-id wording differences are Q08. S0 does not
  settle future runtime behavior. INV-L5/INV-C5 remain pending.
* The spec's historical prose says 120 invariants; the current C tables define
  118. Inventory uses the current 118 definitions: 32 static, 86 pending.
* P3 cannot execute under current dependency/network restrictions; 0 vectors were
  run. P1 uses only an explicitly restricted serialization subset, never offered
  as a general JCS substitute. No package was downloaded/installed.
* Migration samples intentionally cover less than the old full functions. Their
  boundaries and line counts are in MIGRATION-LOG; no old-code acceptance claim.
* A newly authored literal-origin fixture was corrected from `sequence` to an
  empty ref using D6 as independent authority. Two Tm oracle transcription values
  were corrected from hand arithmetic before implementation execution. No old
  product test expectation was weakened.
* User's pre-existing root README, decision, OPEN-ITEMS and untracked prompt
  changes were preserved and excluded from S0 commits.

Official GitLab CI 未执行. GitHub CI was not run: branch is local-only with no remote.

## S3 Revival Evidence (2026-10-16)

* D2/A1 compatibility deviation QS3-03: this baseline runtime requires request
  constraints[].origin although current SPEC forbids it. S3's CLI reproduction
  retains the spec-shaped rejection and then supplies origin for the existing
  baseline interface. Owner integration remains required; Core was not edited.
* D2/B3 PROVISIONAL QS3-01: user explicitly authorized output_present while
  claim_reported is absent. Current Core also lacks fields, so params={} is used;
  Kit consistency enforces the report shape and claim contents. This does not
  implement claim_reported in Core.
* D11 structure validation is blocked in two existing S1 runtime probes by their
  direct import of a package outside src (QS3-04). No shim, skip, or weakening was
  introduced. Static scanner and S3-specific structure checks run separately.
* S5b handoff was tested using constructed interface fixtures, not a real S5b
  output. Its provisional details are QS3-02. Kit-local payload defaults are QS3-05.

No edits to spec/, decisions/, prompts/, reviews/, protected contracts/resources,
Core modules or other Kits. No import or execution of old code; no user DNA read.
No human review/verification record was created. Official GitLab CI 未执行；
GitHub CI 未运行. These deviations do not close the S3 gate.

S3 regression follow-up: the same package import assumption also fails the
existing unit declaration-export probe. Current full layer totals and raw log
paths are in S3-REPORT.md. This is a third error event sharing QS3-04's cause,
not an additional Kit failure or a passing structural gate.

## S1b execution disposition, 2026-10-16

S1b is incomplete and its gate is not closed. The current branch has no S1
runtime: material.py, public.py, ports.py, ids.py and verdict.py are empty.
Following parallel-common section 4, S1B-Q1 stops kernel-material construction,
executable capability wrappers, decorator-generated JSON export, CHECK fixtures
execution and ctx.run_external integration at their structural dependency.
No alternate material model, Outcome/verdict factory, hash implementation,
decorator, callable registry or product entry was invented. Pure calculations
and their independent answers continue. Developer scripts under tools/tests
collect evidence only and do not implement the product backend.

S1B-Q2: material/sequence identity after rotation is not tested or claimed.
D9 hashes sequence and feature coordinates at the chosen origin; S1b acceptance
also asks rotation to preserve identity. Inverse rotation, cyclic k-mers and
extracted feature sequences are tested; no new hash/canonicalization is added.

S1B-Q3: installed sgffp 0.21.0 is not in the dependency allow-list. It was
recorded in FACTS/QUESTIONS before potential use and was not used. The native
reader uses allowed Biopython 1.88 and supports only its parsed fields; full
native fidelity is not claimed. No native writer, binary or user DNA is added.

S1B-Q4: baseline spec_lint has one hard finding: run.created.git_commit missing
from its protected payload schema. No spec, protected resource, S1-owned layer,
review, Kit or reverse-complement capability implementation was changed.

Scientific boundaries: sequences only; no wet experiment, efficiency prediction,
phosphorylation/methylation inference or functional validation. No network
request or dependency installation. Official GitLab CI 未执行；GitHub CI 未运行。


## S1b integration after c8cc70a

This section supersedes the earlier S1b blocked disposition. User merged S1,
resolved origin-dependent D9 identity, excluded sgffp, and resolved the old
spec/schema baseline. The kernel public interfaces are now consumed directly.
22 thin capabilities and generated declarations, kernel material adapters,
four CHECKs with executed PASS/FAIL fixtures, and ctx.run_external integration
are implemented. No S1-owned/protected file or reverse-complement implementation
was modified. README commands explicitly set PYTHONPATH=src.

No new structural deviation is introduced. Current implementation bounds are
explicit: exact local feature coordinates, representable GenBank orientation,
strict FASTA metadata refusal, optional Primer3 complete oligos of 2..36 nt,
and explicit one/two-material assembly ports with larger assemblies chained.
There is no opaque materials-list shortcut, hidden environment reader, separate
verdict constructor, native writer, installed dependency or external binary.

S1 owns application configuration and run.created environment construction;
S1b stores actual Primer3 executable/data fingerprints in its retained report.
Current tests exercise the real provided Invoker/context API. They do not close
S1/S1b gates, prove wet-lab success or replace Kit/sealing acceptance.
Original failures and the pre-merge report are retained. Official GitLab CI
未执行；GitHub CI 未运行。

## S1b round2 preparation disposition

The round2 task explicitly supersedes the older common-rule wording for the
optional actual-Primer3 test: missing configuration is registered skip
S1B-PRIMER3-OPTIONAL, reported NOT_PERFORMED and excluded from passes. Configured
incorrect results remain failures. The product's missing-backend UNKNOWN
behavior remains as previously implemented. No default-CI numerical pass is
claimed when the external integration test did not run.

K1/K3/K4/K6 stop the corresponding Kit structural work: domain document schema
registration, ordered material references, independent model argument/output
binding, and frozen knowledge access for ACTION. K2/K5 retain explicit source
quarantine and handoff-shape decisions. Protected schemas and S1 layers were not
modified. The two actually invalid Genome Identity templates remain invalid;
the unsourced-rule and partial-placeholder probes intentionally remain rejected.

No Kit code was written. Draft modules, fixtures and review paths are future
contracts/strings, not implemented packages or completed tests/review. Legacy
verified flags are not transferred, and no human signature or verification
receipt is supplied. The 24 legacy source-labelled records have no missing-source
rows; the isolated missing-source probe must not be reported as a discovered row.

Task C's four corresponding ACTIONs use the existing declaration exporter and
generate four resources/capabilities JSON files. This necessary deliverable does
not alter resources/schemas, vocabularies, profiles, versions or contracts.toml.
No exporter/runtime/legacy framework changes or additional dependencies are made.

Shared-function tests pass within their explicit constructed scope. Scientific
and Kit acceptance remain unperformed, and K1 to K6 remain unresolved. First
development structure failures and the initial mutation result are retained.
The original S1b gate closure at a6905eb is attributed to the specification
owner; this round does not add a closing tag. No merge or push.
Official GitLab CI 未执行；GitHub CI 未运行。

## S5b Genome Identity (2026-10-17)

No specification, protected resource, shared implementation or other Kit was edited.
The addendum was found under the existing integ worktree, not at the user-named
main-worktree path. Its integration-1 baseline and decisions match this checkout.

S5B-Q1 to Q4 in QUESTIONS.md record Kit-internal defaults and local algorithms.
D11 replaces the legacy discrimination states and gel-resolution workflow;
the new three-state count/size contract is used without inventing public words.
The three historical scope rules are not loaded: the implementation has no
external scientific threshold table and does not inherit historical verified flags.
No source citation or human review was fabricated.

Acceptance deviation: public-CLI computation reaches the correct candidate,
but sealing is rejected by three unavailable mandatory shared checks (S5B-Q5).
No successful seal, portable verify, wet-lab result or stage closure is claimed.
The failing acceptance test and earlier development failures are retained.
## S2 Cut Plasmid, integration-1

- B2 cannot satisfy final acceptance on this base: required annotation integrity,
  CDS validity, biological sanity, reaction-chain and order-table Core checks are
  absent; Core primer-quality requires a different interface. The real public CLI
  retains these six UNKNOWN obligations and rejects sealing with exit 10.
  QUESTIONS.md S2-Q1 requests the owner fix. Profiles are not relaxed and no
  alternative Core checks are installed by the Kit.
- D7 inherited CDS PASS/introduced FAIL classification and isolated-sealed-copy
  verify remain unperformed. S2 tests retain untouched input annotations, but do
  not label that retention as inheritance acceptance.
- The runtime requires explicit GenBank reading actions before material use.
  Templates and B2 use existing public format.read_genbank actions. A real
  GenBank export is read back; the current stage contract exports bound material
  and document candidates as JSON. See S2-Q5; no Kit stage/renderer is added.
- The named addendum was absent at the user-specified main path and this
  worktree. It was read from the integration worktree's identical-named prompt.
  Base HEAD remains integration-1/fc04e41; no integration branch was merged.
- Kit internal PROVISIONAL decisions are S2-Q2 (inline preparation document and
  exact B2 Tm convention), S2-Q3 (one frozen collection with individually sourced
  rule-v1 rows), and S2-Q4 (bounded vector near-match risk gives UNKNOWN).
- Selection sources were migrated offline and not independently verified. No
  new human review/verification receipt or team declaration was created. All
  physical experiments are PLANNED / NOT_PERFORMED. No new dependency was installed.

Official GitLab CI 未执行；GitHub CI 未运行。

## C2 follow-up after the user-authorized S1 merge

The user explicitly authorized merging s1-minimal-slice. Merge e47e17e contains
the owner's S1 closure tag at acc5aed and preserves both S1 reverse complement
and the existing S1b biology/metadata exports. The later shared AGENTS.md commit
4cdb59f is retained. No C2 change to protected resources or S1-owned layers is
made after that merge. No push or new gate-closing tag.

All six requested D2 CHECK capabilities are implemented. Parameter choices and
bounded meanings are documented in docs/goal-constraints.md. Checks operate on
actual target-bound content; reported claims do not become scientific facts.
Unknown topology, unreadable content, ambiguous absence and unavailable explicit
references do not produce PASS. No independent-region mapping or original-source
identity is guessed from annotation labels. Component sequence presence is not
evidence of component activity.

The merged S1 tests now read declared fixture params for read-only checks, since
the new checks have required parameters. Core dependencies remain exactly their
existing lock; only biology may import Bio, already pinned by the separate
Biopython 1.88 biology lock. No dependency lock is loosened or package installed.
Generated capability docs and the generated Skill index are synchronized using
the existing exporter/doc generator; handwritten workflow instructions remain.

Initial targeted testing exposed a missing files list in the new Judge test
candidate, not a production verdict error. The observed failure summary is kept
in tests/evidence/s1b-c2/development-history.json. Twelve literal positive/negative
fixtures and six source mutations actually run; the public API chain separately
confirms that a missing structured claim fails, even when the five DNA constraints
pass. Annotation/CDS/biological-sanity obligations still block complete scientific
acceptance. S1.1 owns goal-origin/request validation and output_present.fields.
Official GitLab CI 未执行；GitHub CI 未运行。

## S3 round 2 after integration-1b, 2026-10-17

User authorized merging main containing 7b1ca09; merge 33a99e0 preserves both
histories. The old S3 origin compatibility request, output_present fallback,
view.knowledge use and generic JSON document port are removed. Production uses
the specified claim constraint, inline schemas and ctx.knowledge. The S5b handoff
now follows SPEC D11, including product_count and exactly two primer IDs. Earlier
S3 deviations above describe the old baseline and are superseded by this section.

No new structural workaround, Core edit, protected-resource edit, other-Kit change,
review record or source attribution was introduced by S3's post-merge edits.
Two unsourced legacy policies remain quarantined and need human source material.
Actual cross-Kit producer execution and wet experiments remain unperformed.
Official GitLab CI 未执行；GitHub CI 未运行. Gate closure belongs to the reviewer.

S3 validation scope clarification: one necessary shared-test edit is outside the
S3-named test files. tests/unit/test_assurance.py now resolves fixture paths from
the contributing Kit root, with Core root as fallback, exactly as the integrated
S1.2 declaration test already does. This fixes the observed FileNotFoundError;
it does not alter production assurance, simplify scientific checks or skip tests.
The first failed complete-layer run is retained and reported separately.
## S2 full-suite test dependency

The complete local suite ran 247 cases: 246 passed, one error, no skips. The
error is the shared Core read-only fixture test resolving a Kit-relative fixture
against project ROOT (test_assurance.py:86), not the Kit directory. See S2-Q6 and
tests/evidence/s2/full-suite.log. The shared test is unchanged; no duplicate
fixture was added under an incorrect project-root capabilities directory. S2's
six check controls execute against the real Kit through Invoker.
## S4a release preparation

Started s4a-release at fc04e41 as requested. The single prior uncommitted C2
fixture had only regenerated basis hashes; its verdicts/oracles were unchanged,
so it was restored as explicitly instructed. The old s1b-biology branch is not
used for new work. Task/addendum text was read from main because the supplied
primary checkout was still on an older branch without those files.

Release tools, an explicit first shipping policy, a generated third-party
inventory, a full local dependency pin list and English evaluator documents are
implemented. Fixed-order/fixed-timestamp source ZIPs and their SHA-256/canonical
manifest were actually built twice on labelled synthetic fixture trees. This
proves those engineering cases, not that the current project is ready to ship.
The actual project has five pending disclosure/Kit markers and correctly refuses
to create a release ZIP. Both F10 and W3 remain in the pending release-acceptance
inventory, with their implemented controls and exact remaining scope recorded.

The ordinary source example was run in the existing environment, compared with
its hand answer and verified after the original run path was moved. Only its
portable B1 sealed record is added as a bundled example; no Kit code is changed.
It retains dev-tree because Core release-manifest consumption is still missing.
That integration issue is assigned to the S1 owner in QUESTIONS.md. Build staging
only generates the VERSIONS resource copy supported by the existing reader;
no source resource or S1-owned implementation is edited.

The new ship.json is an explicitly requested artifact and awaits the owner's
protected-hash registration; no review response or team approval is filled.
New-environment installation, external-user acceptance, official upload, new
freezing decisions and S4 closure were not performed. Official GitLab CI 未执行；
GitHub CI 未运行。 No existing dependency lock or product runtime was changed.

## S1c Core completion, integ-2

No empirical threshold, scientific-model expectation, required check or Kit
implementation is weakened. User decision C5 permits explicit-length-only
acceptance with thermal assessment visibly not performed; existing explicit
thermal constraints remain mandatory. C1/C2/C4/C7 are recorded provisional
integration conventions, not silent defaults claiming laboratory correctness.

Owner 945d702 and the user's explicit follow-up authorize only the spec patch
and call.recorded-payload-v1 schema exception. Fresh records require actual
params and their JCS digest. Existing missing-parameter negatives construct a
legacy view instead of pretending that new records still lack these fields.

Old function-absence assertions conflict with S1c's implementation requirements.
On 2026-10-17 the user authorized only their structural update (C8), with
scientific expectations unchanged. Six obsolete assertion nodes are replaced;
68 other nodes, the input/oracle files and the runtime remain unchanged.
Missing-runtime controls retain UNKNOWN/no-seal expectations.
The user also authorized the local offline setuptools==83.0.0 copy (C9).
Only its 761 RECORD-listed distribution files were copied into the ignored
worktree environment; RECORD hashes were checked. No installer/download,
system site-package inheritance or runtime dependency-lock change. Original
failed runs remain retained. These two approved exceptions are resolved;
S1C-REPORT.md records the actual post-authorization test results.

The new hand Tm fixture initially mixed NN4 initiation constants into NN3; its
own arithmetic was corrected from the NN3 table and existing hand reference,
not fitted to production output. Initial and corrected transcripts remain under
dist/s1c-baseline. Historical branch reports above are not current S1c status;
S1C-REPORT.md owns the current result and outstanding review items.

No user DNA was read, external sequence service invoked, Kit routing evaluation
performed, dependency downloaded, main branch changed, push or merge executed.
All modeled laboratory routes remain PLANNED / NOT_PERFORMED.
官方 GitLab CI 未执行. GitHub CI 未运行.

Night addendum 3 uses the registered C19 provisional boundary: synchronous
Python write observation plus known-file hash readback. It detects writes after
they occur, including import-time, transient and exceptional writes; it cannot
prevent or undo them. Arbitrary reads and unobserved native/child-process I/O
remain outside tested coverage, so INV-E3 remains pending. Interpreter cache
creation is disabled only during the observed call, with the previous flag restored;
module-body writes are still observed. No file-extension exemption, new
dependency, runtime vocabulary or protected-contract change is used.
