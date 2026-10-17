# S1c Core completion checkpoint

Cut Plasmid、Construct（PCR/Gibson）、Genome Identity 均能封存并在复制封存目录后离线复验；Revival Evidence 五案例亦通过。

按授权更新过时结构断言、离线补齐锁定构建依赖后，两轮完整套件均为零失败；未配置 Primer3 的一轮有一项登记跳过，未计为通过。

此前失败记录完整保留。S1c 是否通过仍由规格负责人复核关闭；这里没有湿实验结论。

## Work and contract boundary

Branch: integ-2. Baseline: c3e7c6a. No Kit implementation, template, threshold,
protected vocabulary/profile/contract or main branch was changed. No push or
merge was performed. 官方 GitLab CI 未执行. GitHub CI 未运行.

Only authorized exception: owner SPEC patch 945d702 was synced as d95f086,
limited to spec/SPEC.md and spec/OPEN-ITEMS.md. One protected event schema was
changed under the user's explicit permission, detailed below.

## Changes, reasons and generalization

### 1. Byte-preserving artifact delivery

Before: artifact output bindings raised PLAN_OUTPUT_INVALID at the JSON-only
staging path, contradicting D8 SEAL-2 and D11. Now raw files enter the existing
content store and delivery manifest by byte SHA-256. Readback, store checks and
offline verification cover those bytes. Existing JSON output naming is unchanged.
C1 records the provisional raw-store layout and suffix-preserving binding name.

Two public-API tests and an eight-command public-CLI exercise seal and verify;
only the seal is copied, the original run is unavailable, and verification still
passes. One-byte changes to either delivered or retained raw bytes are detected
as STORE_CORRUPT. Oracles are literal constructed bytes, including binary/UTF-8.
Evidence: dist/s1c-baseline/01-artifact-{red,green,cli}.txt,
dist/s1c-artifact-cli/{commands,SUMMARY}.json.

### 2. Configured external-tool fingerprint

Before: run.created always had external_tools=[], even with Primer3 configured,
contradicting D6/D17. Now a local metadata-only probe at the engine process
boundary records name, version and executable byte hash. It accepts no sequence
and records no executable path. No configuration means an empty list.
Unreadable executable/version behavior is explicitly provisional C2, not an
invented tool hash. No executable was downloaded or bundled.

Three focused controls pass. An actual CLI run records Primer3 2.6.1; an
independent PowerShell file-hash calculation agrees. The initial broad process
mock also counted Windows version detection; the test boundary was corrected,
with failed attempts retained. Evidence: dist/s1c-baseline/02-environment-*,
dist/s1c-environment-real/journal.ndjson.

### 3. Required content and preparation checks

Each CHECK has a generated declaration, construction/hand-defined positive and
negative controls, real engine/API runs and a caught deliberate comparison
mutation. No sample identity, material name or reference hash is a runtime rule.

| CHECK | Before | What now determines the verdict | Independent answer and limit |
| --- | --- | --- | --- |
| annotation_integrity | Unavailable, blocking material delivery | Bounds, parts/envelope, valid strand, compound operator and qualifier shape; per-finding input correspondence | Literal coordinates and invalid strand 2. Does not infer transcription/function from labels. |
| cds_validity | Unavailable | Annotated coding frame, start, terminal/internal stops; transl_table/codon_start, partial/pseudogene handling | Literal ATG/TAA codons and manually rotated coordinates. No expression, phenotype, recoding or strain-genotype claim. |
| biological_sanity | Unavailable | Nonempty IUPAC DNA, declared topology/strands and physical-end consistency | Constructed empty/invalid alphabet and circular-with-linear-ends contradictions. No empirical GC/repeat/host/toxicity threshold; C6 assigns these to a team owner. |
| reaction_chain | Unavailable; older assembly check missed nested calls | Recompute supported direct/nested PCR, digest, ligation, Gibson and inverse PCR from original templates, full oligos and actual recorded parameters, before reading candidate | Literal 15 nt PCR answer, changed one-base candidate, actual Cut Plasmid/Construct independent oracles, and a simulator/read-order spy. Unsupported or missing chains remain UNKNOWN. Shared simulation is not an independent scientific oracle or laboratory evidence. |
| order_table | Unavailable | Every complete planned oligo, including 5-prime tail, against recorded complete PCR/inverse-PCR inputs | Change only a 5-prime tail. Uses existing primer-set-v1 shape under C7; does not assert a vendor order or synthesis. |

Only annotation/CDS handle inherited findings. C4 permits exact per-feature
metadata/coordinates and covered bases, or a unique whole-circle rotation,
following explicit root-input ancestry. An inherited finding stays visible with
PASS and INHERITED_FINDINGS; introduced/unresolved findings fail. Unsupported
coordinate shifts with matching bad CDS bases are UNDETERMINED, not a claim
that the pipeline introduced the old finding. This last label correction was
reproduced against the preceding classifier in a disposable source copy; both
versions block delivery. No broader inherited exemption was added.

The existing GenBank default translation table is standard code 1, as specified
by [NCBI Genetic Codes](https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi#SG1).
Explicit partial/pseudogene metadata and unassessable CDSs retain stated limits.

A real Cut Plasmid acceptance run exposed an over-broad reaction selector: it
also tried to replay an independent editing branch's coordinate rotation. Its
input was not a physical predecessor, so the valid inverse-PCR chain incorrectly
returned UNKNOWN. The original failed run remains in dist/s1c-final/cut-plasmid.
Only transforms connected by recorded material IDs to physical reaction inputs
or products now belong to preparation replay. A separate constructed workflow
reproduces this old failure and proves both valid-product PASS and changed-product
FAIL after the fix. No missing physical predecessor is supplied from a candidate.

Primer/order scope follows D7 bound construct/primer_set producers. An unbound
diagnostic-primer proposal in an analysis output is not silently promoted to a
preparation order; its own assay checks and limitations remain unchanged.

Evidence: dist/s1c-baseline/03a-*, 03b-*, 03c-*, 03d-*, 03e-*,
final-reaction-branch-{red,and-inheritance}.txt,
final-inheritance-previous-behavior.txt; dist/s1c-mutations/*/RESULTS.json.
Tests: tests/integration/test_s1c_{content,cds,sanity,reactions,orders}.py.

### 4. Automatic primer-quality scope, user decision C5

Before: the profile called without IDs/limits, so an explicit-only API always
returned UNKNOWN. Now automatic calls find marked preparation primer documents,
validate core lengths against actual PCR/inverse-PCR parameters, and assess only
explicit criteria. No object is NOT_APPLICABLE with fact basis; missing/invalid
criteria remain UNKNOWN. The explicit material_ids/limits API is retained.

User decision: "只验明确长度，热学验收列为未做". Length-only acceptance records this
exact limitation in the verdict, seal manifest and report:

> Thermal acceptance was not assessed: no temperature window and concentrations were supplied.

Declared NN temperature windows remain mandatory. Core recomputes annealing-core
DNA_NN3/method-5 Tm with both supplied strand concentrations and every supplied
salt concentration; it does not substitute the older total-strand convention.
Actual verdict does_not_establish statements now enter the existing not_verified
aggregation. No new failure threshold or thermal recommendation is invented.

Real API controls cover correct/wrong core length, no object, Construct sealing,
and an explicit NN window pass/fail with independent stack/entropy arithmetic.
Turning off mismatch failure is caught. The new pure 8 nt hand oracle initially
mixed NN4 initiation constants into NN3; this new-test error was corrected from
the published NN3 table and existing hand calculation, not from production
results. Both transcripts remain. No old expected result was relaxed.
Evidence: dist/s1c-baseline/04-primer-*, final-thermal-window.txt,
final-pure-oracles{,-corrected}.txt; tests/unit/test_s1c_analyzers.py.

### 5. Existing fixture-path repair

The already-merged f7cd8d6 rule is retained: Core fixtures resolve at product
root; Kit fixtures at contributing Kit root. Its focused read-only/control and
declaration tests pass. No duplicate fixture or alternate path mechanism added.

## Authorized actual-call parameter schema

File: src/dna_design_core/resources/schemas/events/call.recorded-payload-v1.json.
Before required: parent, capability, input_ids, duration_ms.
After required: those four plus params and params_digest. params uses the same
object/short-literal contract as step.started; params_digest is 64 lowercase hex
characters holding SHA-256 of its JCS bytes. Existing success/failure alternatives
remain unchanged. No other protected schema was touched.

Sample params: {"forward_core_length":4,"reverse_core_length":4}; its fixture digest
is independently hashed from that literal canonical JSON. One valid and four
invalid new examples cover missing params/digest, non-object params and short
digest. Existing payload fixtures retain their original validity expectations.

Invoker always emits actual parameters/digest and retains nested input/output
values. With identical complete primers, a constructed 4 nt core yields one
15 nt product; a 2 nt core yields two possible products and is refused. A changed
recorded parameter fails digest/model/reaction checking. This does not assert
that changing core length always changes a unique product's sequence.
Evidence: dist/s1c-baseline/03-call-*; tests/unit/test_s1c_calls.py. The owner
should align D3's old prose saying nested parameters are absent with the new
Appendix E/user-directed behavior. This task synced only the authorized spec
patch; zero field-lint findings do not establish narrative consistency.

## Existing-test prerequisites, unchanged expected outcomes

- Fresh call records now require parameters by owner decision. The prior missing-
  parameter negative constructs a copied legacy view missing those fields and
  still expects UNKNOWN.
- The old missing-primer-limits negative explicitly selects its retained primer;
  a no-argument call with no marked output is now N/A under task 4. Its original
  UNKNOWN expectation for a selected primer without limits is unchanged.
- The old unavailable-material-check test assumed the two checks did not exist.
  It now deliberately makes their runtime availability false while retaining
  frozen obligations. It still requires UNKNOWN, no seal and no present_files.
  Initial stale-prerequisite failure and corrected run are retained.
- Construct's old acceptance script leaves a stale diagnostic saying portable
  verification was not performed even after sealing becomes possible. It is
  unchanged. run_s1c_kits.py performs the missing copy/verify independently and
  retains that old text alongside actual portable verification results.

## Public-entry acceptance and persistent boundary evidence

Developer-assisted synthetic regression, not an unseen benchmark or human/agent
routing evaluation. Existing Kit scripts, algorithms and expected scientific
values are unchanged. tests/e2e/run_s1c_kits.py enforces successful seal,
verification, copied-seal verification and existing independent oracles.

| Workflow | Verified scope | Local evidence |
| --- | --- | --- |
| Cut Plasmid | Initial failure, recorded revision without goal change, inverse-PCR sequence, GenBank readback, UNKNOWN selection without genotype, seal and portable verify | dist/s1c-final-r2/cut-plasmid/SUMMARY.json |
| Construct PCR/Gibson | Actual preparation, both junction assays, handoff file, independent standard-library oracle, seal/verify and copied-package verify with original path unavailable | dist/s1c-final/construct/SUMMARY.json |
| Genome Identity | Predicted band table, independent oracle, seal/portable verify; changed handoff hash refuses execution/seal | dist/s1c-final/genome-identity/SUMMARY.json |
| Revival Evidence | Five existing observation/prediction cases, independent assessment oracle and portable verification | dist/s1c-final/revival-evidence/SUMMARY.json |

Offline re-execution is not the same as initial final checking: Cut Plasmid
reruns 23 of 24 checks; Construct reruns 21/22 (Gibson) and 20/21 (PCR).
Their unchanged check.format_roundtrip declaration has offline=false, so verify
explicitly lists it in not_rerun. Initial readback ran and byte hashes are still
recomputed. Genome Identity reruns all 13 checks; each Evidence case reruns all
9. No not_rerun entry is counted as an executed or passing check.

The existing Construct marker-cassette fixture was additionally exercised via
public Judge with literal valid versus internal-stop cargo. cds_validity gives
PASS versus FAIL. This selected-check control does not claim whole-workflow
acceptance: its custom cargo differs from the original fixture goal. Evidence:
dist/s1c-construct-cds/SUMMARY.json and final-construct-cds.txt.

The five new material/preparation checks are not required for Revival Evidence:
its runs produce no DNA material or preparation output. They are not silently
counted as passing checks. Its evidence/goal/file obligations still run.

Eight persisted real API workflows in dist/s1c-negative-runs/SUMMARY.json show:
invalid annotation, introduced internal stop, physical-end contradiction, wrong
candidate (reaction and model FAIL), wrong 5-prime tail, wrong core length,
unsupported route UNKNOWN, and unchanged inherited CDS PASS with visible label,
seal and offline verify. Original inputs, receipts and generated files remain.

Reproduce with provisioned local Python and PYTHONPATH=src:

```powershell
python -X utf8 -B tests/e2e/run_s1c_kits.py --case cut-plasmid --out dist/new-cut
python -X utf8 -B tests/e2e/run_s1c_kits.py --case construct --out dist/new-construct
python -X utf8 -B tests/e2e/run_s1c_kits.py --case genome-identity --out dist/new-identity
python -X utf8 -B tests/e2e/run_s1c_kits.py --case revival-evidence --out dist/new-evidence
python -X utf8 -B tests/e2e/run_s1c_negatives.py --out dist/new-negatives
```

## Historical matrix before C8/C9 authorization

Both complete commands ran, with their failures retained. Counts below are
unique test methods; a Construct method has two failed subtests.

| Full run | Methods | Passed | Failed/errored methods | Skipped | Seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Primer3 unset, initial contract-registration state | 375 | 363 | 11 | 1 | 1141.045 |
| Primer3 configured, own contract corrections applied | 380 | 372 | 8 | 0 | 1150.727 |

Raw runner totals: initial 11 failure records + one error; configured 8 failure
records + one error. The extra five methods in the latter run are four new pure
hand/construction oracles and one explicit NN-window integration test. No skip
is counted as passed. The sole initial skip is S1B-PRIMER3-OPTIONAL: no configured
executable, so actual external-program numerical checking was not performed.
With configuration, that actual Primer3 integration/fingerprint check passed.

Three initial own omissions (typing, oracle registration, generated reference)
were corrected; 12 focused contract/structure methods passed in 2.952 seconds,
and those checks passed in the configured full run. Earlier full-run outcomes
are not relabeled after correction. At the main checkpoint the unconfigured
full command had not been rerun; the final overnight results below supersede
that execution timing. Both modes must run again after any C8/C9 changes.

All eight remaining distinct failing methods are preserved unchanged:

- Construct artifact test still expects PLAN_OUTPUT_INVALID instead of a seal.
- Construct diagnostic test still expects all six implemented checks UNKNOWN.
- Construct labelled-cargo test still asserts the CDS capability is absent
  (two subcases, one method); its independent literal stop-count assertions are
  unchanged. A separate public Judge control confirms CDS PASS/FAIL correctly.
- Four Genome Identity integration methods still expect three missing checks.
- Release metadata test cannot import the pinned build backend setuptools.

The first seven methods require decision C8 before obsolete structural
assertions change. Their scientific sequence/size/status/error oracles must
remain. The last requires C9 before an offline build-dependency copy. No test
was deleted, weakened or converted to a skip. No dependency was copied while
permission was pending. These failures block complete regression acceptance.
AI stops dependent work here and does not declare S1c passed.

Raw logs, unique-method count summaries and exit records:
dist/s1c-baseline/full-{without,with}-primer3.{txt,summary.json,exit.json}.
Test-generated historical evidence files were copied into
dist/s1c-generated-test-evidence/tracked before restoring their tracked
contents; both generated S2 run folders were moved under that same ignored
archive after resolved-path checks. The original failures remain available;
generated outputs are not committed. No unrelated working-tree change was
restored or removed.

Static checks currently report zero structure findings; 35 schemas/242 fixtures
with no findings; spec_lint zero hard findings, 17 soft legacy-context notices,
zero appendix field differences. INV-A10 runtime evidence is now registered;
this is coverage evidence, not owner acceptance of the stage.

| 已验证 / Verified | 仅模拟 / Simulation | 未做 / Not done | 不确定 / Open |
| --- | --- | --- | --- |
| Listed public workflows, file hashes, portable seals, constructed failures and mutation detection | PCR, inverse-PCR/closure, Gibson and predicted assays; all synthetic inputs | Wet laboratory work, strain/genome-wide specificity, human review, Linux, push/merge, hosted CI | C8 obsolete assertions and C9 build dependency await user decisions; C1/C2/C4/C7 provisional conventions await owner review |

User/team: answer the two pending C8/C9 choices and review the provisional
conventions/scientific limitations. Recommended: allow only obsolete structural
assertion updates plus genuine missing-runtime controls, with all scientific
oracles retained; allow the existing pinned build backend's offline copy.
AI: after permission, apply those narrow changes, run focused controls and both
complete suites again. Estimate about one hour, based on the measured roughly
19 minutes per full run. Laboratory work remains
PLANNED / NOT_PERFORMED. No user DNA was read, no host routing evaluation run,
and no external sequence service invoked. 官方 GitLab CI 未执行. GitHub CI 未运行.

## 追加任务 / Historical overnight addendum before authorization

Night instruction: continue with registered provisional defaults; ask no further
questions. Explicit no-test-expectation/no-unlisted-dependency limits still leave
the main C8/C9 gate blocked. Independent additional work is authorized by the
addendum's blocked-main exception. No Kit, spec or protected file is changed.

### 1. Three-Kit sealed chain

Started 05:04, completed about 05:28 on 2026-10-17 (local time), within the two-hour
timebox. The final case ran 42 public CLI commands, zero connection attempts.
Three positive runs plus a bounded foreign-background assessment seal and pass
portable verification. Independent standard-library recomputation confirms donor
196 bp, 50 bp arms, two 260/236 bp PCR products, local SUPPORTED, foreign-reference
INSUFFICIENT and no functional-revival support. Exactly two demonstrated links
have equal output/input byte hashes. Two requested failure controls and a further
shared-primer negative were actually run. No scientific expected value or gate
was weakened; setup and input-design failures are retained and explained in C10
through C15. The combined card is a clearly labeled example projection, not a
new built-in multi-run feature. See docs/chain-story.md and
 tests/evidence/chain-story/final-distinct-orf/independent.json.

Verified: CLI, file interfaces, portable records, independent recomputation,
failure controls and zero socket attempts. Simulated: construction and PCR, all
synthetic. Not done: wet experiments, human readers, routing assessment, hosted
CI or main-stage acceptance. Open: C13 resolver lifecycle, C8/C9 main gate and
owner review of documented provisional choices. 官方 GitLab CI 未执行.

Evidence transport follow-up: immutable CRLF bytes are retained with local Git
attributes; per-command Windows longpaths is used. All 122 manifest-listed
portable files match Git-index bytes. No package member was rewritten to satisfy
a whitespace check. Initial staging/inspection failures remain in local logs.

### 2. Read-only specification/ownership census

Started about 05:28 and completed about 05:42 local time, within two hours.
`docs/spec-coverage.md` accounts for all 119 invariants (95 registered, 24 pending)
and 33 mandatory-keyword sentences from 32 D1-D20 lines; historical text/table
headers are not turned into new requirements. Source inspection plus issued
scope/deferral checks identify 11 invariant requirements with no concrete
follow-up implementation assignment, the additional runtime release-id handoff,
and three partial review features. This is an explicit-task ownership criterion,
not a claim no person ever mentioned the subject. No code/Kit/spec/test or
PENDING registry was changed. Estimates in hours are marked as estimates.

The most consequential gaps are exact-commit Windows/Ubuntu CI, runtime loading
of an actual release identity, and truthful human-review state processing.
Additional real checks: release inspection reports four selected-file local
path findings and five disclosure placeholders; 14,246,181 tracked bytes is
below the limit. A synthetic public-CLI probe confirms a 320 nt DNA run in
original prose can enter the goal journal. These are preserved observations,
not repaired in this item. C17/C18 record interpretation/ownership limits.

Verified: current files, symbols, 119/33 census completeness, release-check
output and synthetic CLI probe. Simulated: only new probe data. Not done:
implementing audit gaps, changing ownership assignments, human approvals,
network/install/push/merge. Uncertain: owner treatment of broad/conditional task
scope and the long-prose privacy exception. 官方 GitLab CI 未执行.

### 3. Post-call file-effect detection

Started about 05:42 and completed about 06:50 local time on 2026-10-17, within
the two-hour timebox. Original behavior only compared the authorized
work directory and existing protected files after a normal return. It missed
new out-of-scope files, write/delete cycles and writes followed by exceptions;
a parent could also catch a nested violation. Those are the same file-effect
contract failures regardless of capability identity, contrary to D3/INV-C4
and the bounded post-call requirement in D6/INV-E3.

The Invoker now observes synchronous Python write operations during loading,
execution and result copying, then decides after the call; known input/store/
artifact/candidate files are rehashed even on exceptions. Legitimate nested
engine storage/journal writes use a trusted bookkeeping boundary; child
violations propagate to the parent. No capability write is prevented or rolled back.
No new runtime field, event, registered error, check, dependency or Kit change.
Direct undeclared function/module writes also have an AST heuristic.

Initial eight-control run: two passed and six genuinely failed; the separate
module-loading control also failed before correction. A default-bytecode probe
then found an actual false positive: interpreter cache generation was counted
as a capability write. Both initial loading and a later lazy-helper import
reproduce it. The observed call now suppresses interpreter cache generation
and restores the previous process flag; module/body writes remain observed.
No .pyc-name exemption exists. Earlier complete-suite attempts were deliberately
interrupted while correcting these failures, retained as incomplete, and do not
count as final validation.

Current focused result: 15 methods pass (13 actual API controls and two AST
controls). These cover allowed reads/writes, changed inputs, outside/new-store
files, transient writes, exception paths, import-time writes, nested writes,
swallowed child errors and normal interpreter-cache behavior. A deliberate
mutation disabling the post-call decision is detected by a real failing test.
Six persisted public CLI cases use 24 commands and zero connection attempts;
the retained bad bytes confirm detection after writing, not a sandbox claim.

Evidence: tests/integration/test_postcall_io.py,
tests/e2e/run_postcall_io.py; raw failed/fixed attempts under
dist/s1c-baseline/addendum-3-*; final CLI files under dist/s1c-postcall-cli-final-v2/;
mutant baseline/results under dist/s1c-mutations/postcall-final-v2/.
Reproduce with PYTHONPATH=src and the provisioned Python:

```powershell
python -X utf8 -B -m unittest tests.integration.test_postcall_io -v
python -X utf8 -B tests/e2e/run_postcall_io.py --out dist/new-postcall-cli
python -X utf8 -B tools/run_s1c_mutations.py --case postcall --out dist/new-postcall-mutant
```

Coverage registration: INV-C4 is implemented within the stated v1 AST/Python
write/readback boundary. INV-E3 remains partial/pending: arbitrary reads and
native/child-process I/O outside known paths are not globally monitored. C19
records that limit and the untested concurrent-thread cache-flag policy.
INV-I2 (Linux/multiple Python versions) was not done, as instructed.
The frozen-source configured full run completed 395 methods: 387 passed, eight
distinct methods failed, no skips, 1267.346 seconds. Raw unittest totals are
eight failure records and one error, because one method has two failed subtests.
The failed-method set is exactly the same seven C8 legacy feature-absence
assertions and the C9 missing build-backend method; no new failed method.
No test expectation, threshold, skip condition or dependency was changed.
The unconfigured full run completed 395 methods: 386 passed, the same eight
distinct methods failed, one registered skip, 1236.467 seconds. The sole skip
is S1B-PRIMER3-OPTIONAL: no configured executable, so the actual external-tool
numerical/fingerprint integration was not performed. It passed with configuration.
No skip is counted as passed. Both raw runs report eight failure records plus
one error, with one method containing two failed subtests.

| Final frozen runtime | Methods | Passed | Failed methods | Skipped | Seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Primer3 configured | 395 | 387 | 8 | 0 | 1267.346 |
| Primer3 unset | 395 | 386 | 8 | 1 | 1236.467 |

These are two executions of the suite, not 790 unique tests. The eight failed
method identities match both prior main-checkpoint failures and each other.
Complete regression acceptance remains blocked by C8/C9. Raw logs, exit times,
and method-level summaries are retained at
dist/s1c-baseline/addendum-3-final-v2-{with,without}-primer3.*.

All four public-Kit acceptance scripts passed again on the final runtime:
Cut Plasmid (87.216 seconds), Construct PCR/Gibson (189.058), Genome Identity
(34.543), Revival Evidence's five cases (99.455). Each script enforces seal,
portable verification and independent file oracles. Evidence is under
dist/s1c-postcall-final-kits/RESULTS.json with the full per-Kit subdirectories.
These are developer-assisted synthetic regressions, not independent host
evaluation or wet-laboratory results. No incomplete run or registered skip
is counted as passed.

Final static checks: zero structure findings; unchanged 35 schemas/242 fixtures
have zero findings; generated references are fresh; spec_lint has zero hard
findings, 17 legacy-context notices and zero appendix field differences.
Coverage partition is now 96 registered and 23 pending, total 119; this inventory
is not stage acceptance. C4 has the new bounded write-detection evidence; E3
and I2 remain pending with explicit reasons.

Generated test outputs were preserved before restoring only three known tracked
output JSON files. Four untracked first-round directories and one second-round
directory were archived under dist/s1c-generated-test-evidence/addendum-3-*.
One historical tracked directory was accidentally included in the first move,
then moved back unchanged; Git shows no historical evidence change or deletion.
An initial summary helper duplicated method suffixes; its original summary was
retained and corrected against raw unittest identifiers. No runner outcome changed.

| 已验证 / Verified | 仅模拟 / Simulation | 未做 / Not done | 不确定 / Open |
| --- | --- | --- | --- |
| Fifteen focused methods, six actual CLI cases/24 commands/zero connections, detected decision mutant; both complete-suite results above; four Kit public regressions | DNA preparation, PCR and assembly on constructed inputs; laboratory steps PLANNED / NOT_PERFORMED | Wet experiments, Construct thermal acceptance, Linux/multiple Python versions, unrestricted I/O certification, human review, push/merge and hosted CI | C19 broader I/O/concurrent-thread policy; owner review of provisional conventions; C8/C9 still block the main gate |

The specification owner reviews the eight retained main failures and C19 scope;
AI may update the obsolete structural assertions or add the missing build
dependency only after the required authorization. No test expectation or rule
was relaxed overnight. 官方 GitLab CI 未执行. GitHub CI 未运行.

## Authorized C8/C9 follow-up, 2026-10-17

User authorization: "允许更新过时结构断言，科学预期不动" and
"允许离线补齐锁定构建依赖". This section supersedes the earlier pending-permission
and eight-failure status. Earlier logs and checkpoint totals remain historical
evidence; none is deleted or relabeled as passed. S1c acceptance remains with
the specification owner.

### Scope and independent basis

No product/Kit code, profile, schema, scientific input, fixture generator,
independent oracle or runtime dependency lock changes. Only two integration
test files and this follow-up documentation change.

| Old assertion | Authorized replacement | Basis independent of returned results |
| --- | --- | --- |
| Construct file outputs must be rejected | Seal succeeds, manifest exists, public verification succeeds | D8 SEAL-2 and S1c task 1 explicitly require byte-preserving artifact delivery |
| CDS checker must be absent | Checker exists; the same valid CDS is PASS, the same internal-stop CDS is FAIL | Literal ATG/start, terminal stop and one deliberately inserted internal stop; previous sequence/feature/codon-count assertions retained |
| Six Construct obligations must be UNKNOWN | Valid unannotated input satisfies annotation/sanity/preparation/order/explicit-length checks; CDS is NOT_APPLICABLE | D7 required checks, constructed valid references and actual declared routes/primers; C5 still excludes thermal acceptance |
| Identity must lack three Core checks | No unsatisfied obligation; annotation/sanity PASS and CDS NOT_APPLICABLE | Supplied synthetic references have valid DNA and no CDS features; D7 |

The Identity table still must exactly equal the constructed expected table,
including NOT_DISTINGUISHABLE, UNDETERMINED, product counts and band sizes.
The independently computed assay conclusion comparison is unchanged. All
registered-error negative assertions remain. Missing-check/runtime controls in
tests/unit/test_assurance.py still require UNKNOWN, no seal and no present files.
One adjacent table read is now explicit UTF-8; its expected value is unchanged.

Source-level comparison accounts for six replaced obsolete assertion nodes
(four Construct, two Identity) and retains all 68 other assertion nodes
(62 Construct, six Identity). Only the explicit read encoding is normalized
for this source comparison. The two test method names that described obsolete
absence/blocking were renamed; no test was removed. Audit evidence:
dist/s1c-authorized-followup/assertion-preservation.json.

### Offline build dependency

The missing-backend test was rerun before copying and really failed with
ModuleNotFoundError. Then only the installed setuptools==83.0.0 distribution's
761 RECORD-listed files were copied to this worktree's ignored environment.
The four components are setuptools, _distutils_hack, distutils-precedence.pth
and setuptools-83.0.0.dist-info. Source RECORD hashes were checked before copying.
No package installer/download, system-site inheritance, extra dependency or
runtime-lock change. Distribution/version import and actual metadata creation
now succeed, retaining the literal expected metadata version 0.0.7.
Evidence: dist/s1c-authorized-followup/build-dependency.json and
dist/s1c-authorized-followup/build-dependency-red.txt.
No dependency files are committed or added to the product runtime requirements.

### Actual validation

Focused public-API/actual-backend regressions: 20 methods passed in 186.519
seconds, including all formerly failing Construct/Identity cases. Static
checks report zero structure findings; 35 schemas/242 fixtures have no findings;
generated references are fresh; spec_lint reports zero hard findings, 17
legacy-context notices and zero field differences.

Both complete modes finished with exit code zero on the same fixed test content:

| Configuration | Methods | Passed | Failed/errors | Registered skips | Seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Primer3 configured | 395 | 395 | 0 | 0 | 1409.228 |
| Primer3 unset | 395 | 394 | 0 | 1 | 1905.621 |

The sole skip is S1B-PRIMER3-OPTIONAL: actual external-program numerical and
fingerprint checking was NOT_PERFORMED when no executable was configured.
That exact integration passed in the configured run. The skip is not a pass;
these are two executions of the same suite, not 790 unique tests. The runs
cover normal software delivery and deliberate error rejection; they do not
establish wet-laboratory performance or general success rates.

Original eight-failure checkpoints remain under dist/s1c-baseline/. The new
logs, summaries and exit records are under dist/s1c-authorized-followup/.
Generated result JSON files from each mode are preserved in separate
generated-with-primer3/ and generated-without-primer3/ directories. Two new
untracked run directories were archived to generated-runs/ after absolute-path
checks; the already tracked historical run was left untouched. Only three known
test-generated output JSON files were restored after saving their new contents.
No original failure, scientific input or historical record was removed.

These are known-case regressions plus existing independent constructed controls.
No heldout/independent-host evaluation was run; the human-authorized test
maintenance is not counted as independent task success. No production code,
Kit, scientific oracle, protected contract or runtime lock changed.

| 已验证 / Verified | 仅模拟 / Simulation | 未做 / Not done | 不确定 / Open |
| --- | --- | --- | --- |
| 20 focused methods; both complete-suite results above; six obsolete assertion nodes corrected with 68 others retained; actual locked metadata backend | Existing synthetic DNA preparation, PCR and assembly; laboratory routes PLANNED / NOT_PERFORMED | Wet experiments, Construct thermal acceptance, Linux/multiple Python versions, hosted CI, push/merge or release approval | Broader I/O coverage and existing provisional conventions remain unchanged; specification-owner review is still required |

C8/C9 are resolved by explicit user authorization and the actual runs above.
The local main-task regression blockers are cleared. The specification owner
must review S1C-REPORT.md and the provisional conventions before closing S1c;
this developer report does not supply that approval. 官方 GitLab CI 未执行.
GitHub CI 未运行. No push or main-branch change.
