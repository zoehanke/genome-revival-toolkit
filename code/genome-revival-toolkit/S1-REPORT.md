# S1 implementation checkpoint

The local minimal chain and D2 source import are implemented.
The S1 inventory has 50 covered and 3 pending invariants after moving INV-A10 to S2.
The human reviewer decides whether S1 closes; this report does not close it.

## Authority and scope

Source branch: s1-minimal-slice. Developer changes are confined to code/ and
development tools. No push, merge, installation, old-runtime import, or real
scientific Kit implementation was performed.

Owner patches followed: e621b5c (dev-tree and optional Git commit), 2c9c0c9
(no original input paths), 4daa3cd/9e170f9 (request-only from), c4cf727
(INV-A10 belongs to S2), and 77ad3a0 (template library version comes from
contributing Kit, or Core for a Core template).

The single callable declaration, single Invoker, single verdict constructor,
append-only journal and single seal publisher are used by both examples.
The only production scientific algorithm implemented is reverse complement.
The external counting Kit is generated only in test output directories.

## Actual validation

| Scope | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Structural/contract unittest cases | 60 | 0 | 0 |
| Unit cases | 44 | 0 | 0 |
| Integration cases | 4 | 0 | 0 |
| Public CLI end-to-end cases | 2 | 0 | 0 |
| Complete discover run | 110 | 0 | 0 |

The complete discover run took 337.569 seconds in the supplied Windows Python
environment. Subsequent focused checks covered the strengthened goal-digest
ownership assertion, copied-tree source exclusions, and an actual public API
material-output rejection. Their assertions did not weaken previous expectations.

- check_schemas: 35 schemas, 227 fixtures, 0 findings.
- check_structure: 0 findings.
- spec_lint: 0 hard findings, 17 soft findings in negative/historical terminology
  contexts; 35 schemas compared, 0 field differences, 0 unresolved fields.
- docgen --check: 0 differences.
- Three deliberate mutations were detected: removing replay output comparison,
  removing always-required profile checks, and disabling event hash comparison.
  Each targeted test failed with its expected assertion. These are detected
  mutations, not three additional passing unittest cases.
- Public examples: 41 CLI commands, 0 attempted network connections. A separate
  deliberate connection control records 1 attempt and fails.
- Registered Core CHECKs and the toy CHECK have constructed passing and failing
  fixtures. The failing controls were actually executed. A wrong counting
  algorithm can replay consistently, but fails its independent additive identity.
- Source import was exercised through the CLI using relative and non-ASCII
  filenames. Copied bytes, actual SHA-256, input.registered, immutable run.json,
  path omission, duplicate ids, and changed-content rejection were inspected.
- A killed subprocess left an incomplete journal tail. The public run execute
  command recovered that tail, retained the started step, recorded STEP_INTERRUPTED
  and returned HALTED instead of silently repeating it.

No heldout evaluation or success-rate claim is made. B1 is a known spec example;
the non-DNA counts and malformed cases are developer-constructed independent
inputs, with answers fixed by construction. Human assistance supplied contract
decisions, not corrected runtime outputs. No reader or isolated-host evaluation
was run.

## Retained failures and general fixes

| Original behavior | Requirement | General correction and control |
|---|---|---|
| A request source was validated as a stored source before import | D2 uses from only in requests | Normalize after reading actual bytes; preserve a relative copy and computed hash; same id with changed bytes is INVALID_INPUT |
| Functions sharing one implementation module reused the first cached function | D3 requires the declared function to run | Cache the module, then select each declared function; combined judgement retains the original failing case |
| Revision validation rejected compact references accepted on initial submit | D4/D5 require normalization before admission | Normalize added steps and output bindings before revision validation; original failed CLI run retained |
| API pre-read rejected a torn tail before execution could recover it | D6/D9 recovery belongs to storage | Read the intact prefix for receipt accounting, then recover under the execution lock; real killed-process CLI test |
| Earlier inputs could cease being checked after source declarations were amended | D9 retains registered input facts | Check every registered input copy, including an input absent from the current goal |
| Static scanner rejected state=null | A14 explicitly allows null before a run/plan | Accept only this documented null case; no new state word |
| Copied-tree static tests copied local environments and generated results | Development artifacts are outside source contracts | Exclude .venv, dist and build from copies; retain all source, tests and fixtures |

The original failed example remains in dist/s1-evidence-01. Later successful
development reruns remain in dist/s1-evidence-02 and dist/s1-evidence-03. They
are not independent unfamiliar-task successes.

## Invariant inventory

[IMPLEMENTED_INV.json](tests/IMPLEMENTED_INV.json) records 94 covered invariants
across stages, including the 32 original S0 static controls. Evidence paths are
listed per new invariant. [PENDING_INV.json](tests/PENDING_INV.json) retains 25.

Only INV-A10 moved from S1 to S2. It needs actual annotation/CDS finding and
inheritance comparison, outside the sole scientific algorithm allowed in S1.
No other S1 invariant requires real plasmids or CDS logic: material identity,
role-derived obligations and lineage are testable with constructed values.
The public API material control confirms that labeling a material as analysis
still requires content checks; missing annotation/CDS checks are UNKNOWN and
the seal is refused.

| Still pending in S1 | Reason |
|---|---|
| INV-C4 | Normal built-ins and post-call effect detection were exercised, but OS-enforced read-only execution for arbitrary external capabilities is not implemented or verified |
| INV-E3 | External Kit I/O is not confined by an OS mechanism; external-process fingerprint capture is not exercised in this slice |
| INV-I2 | Golden vectors were run only on Windows/Python 3.12.4; Linux and other Python versions were not run |

These pending items remain pending, not skipped or passed. The current S1
INV-L, INV-P and INV-A entries are covered, with the human-authorized INV-A10
exclusion. V1 explicitly has no code sandbox.

## Evidence artifacts and reproduction

Run the commands in [README](README.md). The example script uses the public CLI,
retains receipts and generated files, and verifies a copied sealed directory
after renaming the original run out of the way. Every stored input path is
relative. The copied package contains input copies, content store, journal,
catalog, goals, plans, verdicts and offline views needed for those checks.
Verification requires matching Core and external Kit code; it does not require
the original run directory.

Final evidence regenerated from committed runtime dfa4faf7c5aae80bf12d2d99bc48b4282be2fae8:
- [Example summary](dist/s1-evidence-final/SUMMARY.json) and [raw receipts](dist/s1-evidence-final/receipts.json)
- [B1 offline card](dist/s1-evidence-final/b1/portable/c38938a5313a828fe6183f7ba8989dc44db5a002ae55d90802698a76937c9586/views/runcard.html)
- [B3 offline card](dist/s1-evidence-final/b3/portable/4fc86809f490057634c8036c35ca2c7323c151498735a9a1fddb7a792b8f4d93/views/runcard.html)
- [Mutation results](dist/s1-mutations-final/RESULTS.json) and sanitized assertion transcripts
- dist/s1-full-tests.txt and dist/s1-fields.json

Both final run.created records name that same Git commit. B1's copied package
contains 12 manifest-listed files; B3's contains 15. Both were verified after
the original run directory was renamed. The final rerun again executed 41
public CLI commands with 0 connection attempts, and all three mutations were
detected. Generated evidence remains under ignored dist/ and is not committed.

Source commits for kernel through fixtures: e875ea8, f1606cd, ebc3e4e, 26e13f6,
f444b6b, 0a6ab82, 5284382, a28e3b0; end-to-end closure is dfa4faf. Each example records its own Git commit and
exact declaration/code digests in run.created and the catalog snapshot.
Development reruns before the final commit contain working-tree code and are
not release evidence.

## Verified / simulated / not performed / uncertain

| Verified | Simulated | Not performed | Uncertain |
|---|---|---|---|
| Public commands, byte checks, immutable records, replay controls, copied-seal verification, zero-connection controls | Reverse complement of constructed DNA; synthetic count calculation; deliberate failure and revision | Real scientific Kits, real plasmids, wet experiments, installation/release assembly, human review signing, hosted CI, independent reader evaluation | Arbitrary external Kit side effects, cross-platform equivalence, future jsonschema resolver compatibility |

The owned runtime directly imports only rfc8785 and jsonschema outside the
standard library. The S0 migration spikes still import Bio and were not run as
part of S1; this is recorded in DEVIATIONS.md. jsonschema emits a RefResolver
deprecation warning; the pinned version passes the local checks.

Official GitLab CI 未执行. GitHub CI 未运行. No real Kit scientific validation.
