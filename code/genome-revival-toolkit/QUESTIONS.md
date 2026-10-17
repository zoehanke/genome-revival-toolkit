# S0 decisions and remaining questions

## S1c provisional integration details


C10 (night addendum 1; RESOLVED by S1d, 2026-10-17): historical behavior below
is retained as failure evidence, not current operating instructions.
The bundled Identity from_handoff template
uses FASTA readers; Construct's hash-bound reference exports are GenBank. The
host's public pipeline selects format.read_genbank for those two inputs, keeping
the handoff bytes unchanged. This is a documented host plan adaptation, not an
unchanged-template routing success or a Kit source change.
S1d now delivers both byte-identical reference files and reads their actual
format; primer ids resolve from D11. Three unmodified templates seal and copied
packages verify. No D11 shape change was needed; see S1D-REPORT.md, section A.

C11 (night addendum 1, PROVISIONAL): the stock run card projects one run and has
no public cross-run loading operation. The example's independent standard-library
script composes a clearly labeled demonstration card from three immutable sealed
records, using only existing hash_equal/declared link semantics. Individual
sealed cards remain intact. Do not advertise built-in multi-run visualization.

C12 (night addendum 1): format.write_genbank artifacts have output_role=null;
they cannot be relabeled analysis by a host binding. The initial new fixture's
three extra analysis targets correctly failed target_role_met. Remove those
unrequested targets, retaining the four requested Construct goals, and read the
actual archived format outputs under sealed work/ (manifest-bound bytes). No
Core role rule or required goal is weakened; donor/primer/assay/handoff remain.
S1d disposition: the role restriction remains unchanged. The Kit's existing
handoff exporter now declares and delivers analysis reference-file copies;
consumers use present_files rather than searching sealed work/. The historical
host workaround is superseded, without host relabeling or weakened obligations.

C13 (night addendum 1, observed lifecycle gap): changing one imported source
byte before execution is rejected with SOURCE_CHANGED and prevents sealing,
but a resolver failure before step.started can leave persisted state RUNNING.
D6 orders resolution before step.started. Do not invent new events/fields to
change this during the example. PROVISIONAL: the example's rejection control
requires the actual integrity error, nonzero exit and refused seal, without
inventing a HALTED requirement. S1/spec owner should define/fix this lifecycle
transition; its raw record is retained, not passed off as HALTED.

C14 (night addendum 1, input context): synthetic count rows without explicit
unit are retained as UNKNOWN difference by the existing Evidence contract. The
first independent oracle expected -22 without supplying unit; that fixture error
is retained. The final case states unit=colony explicitly, keeping counts 8/30
and expected difference -22 fixed. It also constructs a 120 nt model ORF after
seeded reference generation; marker 96 nt and both 50 nt arms stay explicit.
Neither modeled sequence is claimed to have experimental biological function.

Night checkpoint disposition: C8/C9 changes were left unapplied while their
explicit prohibitions remained. Subsequent user authorization on 2026-10-17
permits only the narrow structural-assertion update and offline build dependency
copy described below; no new permission question is needed.


C8 (S1c acceptance prerequisites, authorized 2026-10-17): existing Construct tests asserted
artifact staging must reject files and that check.cds_validity is absent;
Genome Identity expected the three missing content checks. These assertions were
true on the integration baseline but directly contradict tasks 1/3/4. Original
full-suite failures remain retained. User authorized: "允许更新过时结构断言，科学预期不动".
Only six obsolete assertion nodes are replaced; 68 other assertion nodes are
retained, as are all scientific sequences, sizes, analysis statuses and error
negatives. CDS now checks the same literal valid/internal-stop controls rather
than absence of the checker. Artifact output must seal and verify. Existing
missing-runtime controls still require UNKNOWN/no seal. No rejection is mocked
to keep an obsolete artifact assertion green. Evidence and final reruns are
recorded in S1C-REPORT.md's authorized-follow-up section.

C9 (S1c environment, authorized 2026-10-17): pyproject.toml already locks the release
build backend to setuptools==83.0.0. The task-provisioned isolated runtime initially had
only jsonschema/rfc8785/Biopython and closure, so the merged S4a metadata test
failed with ModuleNotFoundError. An installed local copy of the pinned backend
was available. User authorized: "允许离线补齐锁定构建依赖". Copied only the
setuptools 83.0.0 distribution's 761 RECORD-listed files (four package/metadata
components), with source RECORD hashes checked. No installer, download, system
site-package access or runtime-lock change. The actual metadata backend test
passes after copying; its original missing-package failure is retained. This
is an explicitly authorized build-environment addition, not a runtime dependency.


C7 (D7/D11 order shape, PROVISIONAL per S1c task): use the existing marked
primer-set-v1 document as the planned order, with primers[{id,sequence,core_length}].
Compare complete DNA sequences, including 5-prime tails, against actual recorded
PCR/inverse-PCR oligo materials from the same producer. This does not assert a
vendor order was placed. Unknown document shape or absent recorded use is
UNKNOWN; no marked primer output is NOT_APPLICABLE with basis. A future vendor
format needs an explicit separate input contract; no format guessing is added.
Selection follows D7's actual bound construct/primer_set producer roles; an
unbound diagnostic proposal inside an analysis output is not a preparation
order. Its own assay check and unverified-thermal statements remain unchanged.

C6 (D7/D12, team-owned future scientific criteria): biological_sanity contains
only the existing DNA alphabet, nonempty-value and physical-declaration
consistency contracts. No GC, repeat-length, host-suitability, toxicity,
efficiency or other empirical threshold is supplied by this task. A team owner
must provide a sourced rule and applicability before adding any such criterion;
there is no default numeric allowance or passing stub for them.

C4 (D7 INV-A10, provisional correspondence): an exact per-feature copy means
unchanged feature metadata/coordinates and every covered source-base span,
following only the producing step's explicit source ancestry. Other sequence
regions may differ. A uniquely determined whole-circle rotation is the other
recognized case. Multiple/missing witnesses are UNDETERMINED and fail; no
general inherited exemption exists. If the owner requires whole-material
identity for copying, change only this correspondence helper; unchanged CDSs
outside an edit would then block replacement delivery.

C5 (D7 primer-quality scope, resolved by user): Construct's current primer-set-v1 has complete
sequences and core_length and the producer records primer_length=20, but it has
no Tm window or salt/concentration parameters. User decided: "只验明确长度，热学验收列为未做".
The automatic check may pass only the producer's explicit length constraints;
it must state thermal acceptance was not assessed. No invented thermal threshold
is introduced. Cut Plasmid's declared NN parameters and length/Tm windows remain
fully checked. Existing explicit-limits API behavior is retained.

C3 (D3/D6/D7, resolved by owner 945d702):
Originally call.recorded contained input_ids and outputs but no parameter values or digest.
For example the same complete primers with different forward_core_length may
describe a different PCR. A route document can declare these values but cannot
establish that they were the recorded invocation. Recommendation: owner adds
optional params and params_digest to call.recorded in SPEC/Appendix E and its
protected payload schema; new calls always emit them. Legacy missing records
remain UNKNOWN when the reaction cannot be reconstructed independently. Nested
material values also need immutable retention in the existing store; that needs
no schema change. User authorized syncing only that commit's spec changes and
updating call.recorded-payload-v1, the only protected schema touched by S1c.
The engine now emits both fields, enforces the existing short-literal policy,
and retains nested input/output values for replay. Fresh records require the
fields; missing-record negatives remain UNKNOWN through copied legacy views.
No event field was invented by this task.
Owner follow-up: the D3 model paragraph still says nested call records lack
parameters. Appendix E and the user's 945d702 follow-up now supply them. S1c
uses those actual records for the requested reconstruction, including model
comparison; the owner should align that old prose. No additional spec edit was
made locally, and zero field-lint findings are not a claim of prose consistency.

C2 (D6/D17): environment.external_tools requires a string version and byte hash;
there is no unavailable-executable shape. PROVISIONAL: when configured and
readable, record name/version/hash (UNKNOWN version if --about cannot identify
it). When unreadable, do not fabricate a hash; keep the list empty for that tool
and return an explicit existing notices entry. The tool's own capability still
reports unavailable normally. No paths or new environment fields are stored.
The metadata probe stays at engine's external-process boundary and accepts no
sequence argument. If rejected, the owner must specify unavailable-tool records
or decide to reject run creation. No protected schema was changed.

C1 (D6/D8 SEAL-2): raw artifact storage and destination-name convention are not
listed in the minimal JSON-only S1 layout. PROVISIONAL: use store/artifacts/<file
sha256> for unchanged bytes; use the output binding name, appending the source
suffix only when the binding has none. Existing document/material/value JSON
filenames stay unchanged. Source/artifact event schemas and the manifest file
shape are unchanged. If rejected, only Store's raw-file path and stage naming
need adjustment. Byte hash verification remains mandatory in either layout.

## S5a Construct (integration-1, 2026-10-17)

### Structural blockers

- S5A-Q1, D7/D8: Catalog on fc04e41 has no check.annotation_integrity,
  check.cds_validity, check.biological_sanity, check.reaction_chain or
  check.order_table. check.primer_quality requires explicit limits/material_ids,
  whereas the base profile invokes it without parameters. Thus a construct
  cannot seal, and D7 inherited/introduced CDS verdicts cannot be exercised.
  Recommendation: S1/S2 owners implement these core obligations and their
  recorded-input binding; retain UNKNOWN until then. Construct does not replace
  core checks, reduce profiles, or claim D7 acceptance.
- S5A-Q2, D8 SEAL-2/D11: assurance.stage.outputs raises PLAN_OUTPUT_INVALID
  for artifact bindings ("S1 stage exports JSON document or value outputs only").
  A real identity-handoff.json artifact therefore cannot be sealed. Recommendation:
  S1 owner support recorded artifact staging/readback, then rerun the full
  Construct template and copied-package verification. This task stops at that
  acceptance item, retaining the generated file and its engine-recorded hash.
- S5A-Q3, D6/D17: RunService.create records external_tools=[] even with configured
  Primer3. Construct needs no Primer3 backend for exact sequence geometry; the
  explicit backend fingerprint probe is retained as test evidence. Recommendation:
  S1 owner bind configured tools into run.created; no Kit environment reader added.
- S5A-Q4, D11/D18: the complete local suite reports an error in
  tests/unit/test_assurance.py:test_all_check_controls_are_readonly. Its source
  opens ROOT/declaration['fixtures']['pass'] for every registered CHECK, including
  bundled Kits. Kit fixture paths are relative to their own Kit root, as already
  honored by tests/unit/test_capabilities.py. Recommendation: the S1 test owner
  resolve each fixture against its catalog entry root (or ROOT for core), instead
  of duplicating Kit fixtures outside the Kit or weakening Kit isolation.
- S5A-Q5, D11/D13: the handwritten core skill/SKILL.md still says this development
  build has no real scientific Kit. The isolated routing preview observed that
  stale statement after Construct was added. Recommendation: the core documentation
  owner refresh the shared index when integrating the Kits. This task changes only
  Construct's own Skill and records the remaining old wording.

### Kit-local provisional details

- S5A-P1, D11: retain draft names for primer-set-v1/route-plan-v1, with strict
  inline schemas. Explicit primer_length chooses geometry, not a validated
  laboratory threshold. All lengths/overlaps are supplied parameters. Equal cargo
  bounds mean deletion; PCR requires explicit actual donor-template bounds.
  If rejected, change capabilities/contracts.py, templates and corresponding tests.
- S5A-P2, D11: two external-to-cargo junction pairs use complete 5-prime-to-3-prime
  sequences. For deletion without cargo, use one external flanking pair and compare
  original/edited lengths. Supplied primer documents are assessed unchanged so
  donor carry-over and repeated sites remain visible. If rejected, change assay.py.
- S5A-P3, D1/D11: donor geometry, reaction-record replay, junction selection and
  handoff serialization stay in this Kit, as requested by parallel-common.
  Possible shared-algorithm promotion is left to the specification owner.


## S1.2 questions

Q12 (D3/D7, resolved by user): a complete materials-port collection now
executes correctly, but the existing check.lineage/check.replay resolver in
capabilities/builtin/checks.py always reads only the first material when index
is absent. The retained public-API reproduction is
dist/s1-followup2-validation/04-materials-after-bind.txt. The new S1.2 prompt
forbids editing capabilities/builtin/. Recommendation: permit only a mechanical
extraction of its input-reference/argument helpers to a shared capability helper,
and teach that single helper to resolve a whole materials port. Keep all verdict
conditions and prior expectations unchanged. User authorized only the existing
material read call site plus the shared resolver. Implemented in kernel.references
and exposed through kernel.public; engine and that check call site share it.
Positive two-material flow and missing/reordered failure controls are required.

Q13 (D3/Appendix E, resolved by S1c C3 / owner SPEC 945d702; historical question): the model convention works
for recorded step.started inputs and params. Nested call.recorded events contain
input_ids and outputs but no params, so they cannot reconstruct the named model
arguments for a nested invocation. Recommendation: clarify whether model-bearing
nested calls are out of scope for v1 or define their recorded-parameter carrier
through the specification-owner process. Until resolved, check.model_agreement
reports UNKNOWN for such calls, never PASS. No event/schema field was added.

## S1 checkpoint questions and resolved patches

Q10 (D7/D19, resolved by user and SPEC c4cf727): S1 deliverable 8 permits only reverse complement as a
production scientific algorithm, while its exit gate asks for all INV-A tests,
including INV-A10's annotation/CDS finding classification. The minimum S1
document/value examples do not invoke those material checks. They remain
unavailable and block a material-output seal with UNKNOWN. The user moved
INV-A10 to S2 and excluded it from the S1 gate. No other S1 invariant requires
real plasmids, annotation or CDS analysis: material-role union, material identity
and lineage can be tested with constructed structural values. They remain in S1.
The developer has not changed the specification or closed the S1 gate.

Q11 (D4/A3/D16, resolved by user and SPEC 77ad3a0): pipeline-template-v1 has integer version for the
plan revision, but an instantiated pipeline's library_ref.version requires
semantic version text. The template has no separate semantic-version field.
The owner confirmed the contributing Kit's manifest version, retaining integer
version for the draft pipeline; a Core template uses the Core version. Exact
template identity is template_digest. No field or independent template version
was added. The synthetic CLI example exercises this provenance.

Resolved by owner: e621b5c permits dev-tree release ids and optional git_commit;
2c9c0c9 removes original input paths; 4daa3cd/9e170f9 define request-only from,
relative input copies and engine-computed hashes. Implementation follows these
patches. S1 uses the user-provided environment and the two pinned direct
dependencies. S0 was closed by the team and Apache-2.0 confirmed before S1;
the older pending statements below describe the historical S0 handoff.

Current basis: SPEC 8ad9c44, correction 12c4274, and user's S0 follow-up decisions.
Original questions and failed examples remain in fb8e911 history. No spec file
was edited by this follow-up. No human review response has been supplied here.

| Item | Original question | Current disposition |
|---|---|---|
| Q01 | CHECK.offline absent from appendix | Resolved by A2; required for CHECK |
| Q02 | Document schema_ref, atomic/composite carrier, authorship | Resolved by A2/A9: document schema_ref, required granularity, optional authorship on three declarations |
| Q03 | Which inherited findings correspond to input findings? | User agreed first version recognizes only unchanged bytewise copying and circular rotation; all other cases UNDETERMINED→FAIL. Implementation and independent mapping tests remain future work |
| Q04 | Enumerate candidate guides in first release? | User decided no; first release only checks/replaces a user-selected guide |
| Q05 | Missing local JCS dependency | User reports Claude installed rfc8785==0.1.4 in an isolated, authorized probe environment and passed 3 Windows vectors. Codex did not reproduce it; Linux untested |
| Q06 | Product license | Spec owner provisionally selected Apache-2.0, pending user confirmation. LICENSE remains pending; no license text added |
| Q07 | Unspecified inner shapes | A14 resolves all previous x-s0-gap fields. Remaining markers: 0. Corrected locations in 12c4274 are goal.amended.diff (RFC 6902) and input.registered.declared_by; no pipeline.revised.diff added |
| Q08 | D1 table/TOML and D3/D11 duplicate-id wording | Resolved by 8ad9c44. Static contract follows agreed table; runtime import/call sufficiency and catalog deduplication still require implementation |
| Q09 | Initial event prev | Resolved by D9: exactly 64 zeroes; S1 golden-vector/runtime work remains pending |

Q03 still requires unique source/feature correspondence and evidence that affected
sequence/annotation was unchanged. Copy/rotation labels alone do not prove
inheritance. Suggested later constructed controls: unchanged copy; unique rotation;
duplicate features; ambiguous multiple inputs; absent mapping evidence.
No inheritance algorithm or general exemption was implemented here.

No internal schema field remains undefined after corrected A14. Cross-document
truth, JSON Patch execution, placeholder instantiation and runtime verification
remain implementation work, not excuses to add fields. See SCHEMA-GAPS.md.

Remaining human actions: confirm product license; reviewers read REVIEW-SHEET
sections 1 and 2 and reply in the conversation. Other sections are explanatory.
Codex does not fill anyone's reply or declare S0 passed. Linux JCS comparison and
Codex reproduction remain unperformed, not failed or skipped tests.

## S3 Revival Evidence (2026-10-16)

### Structure and Core integration

QS3-01 (D2/D7/B3, PROVISIONAL; user-authorized fallback): this worktree has no
check.goal.claim_reported. Its output_present declaration also has no fields
parameter. Use output_present(params={}) and retain a PROVISIONAL unbound intent;
the Kit consistency check recomputes and compares all claim rows. Owner should
replace this constraint with claim_reported after S1b integration. No Core file changed.

QS3-03 (D2/A1, blocked on Core): latest SPEC acc5aed requires request origin to be
program-derived and rejects supplied origin. Current session.set_goal instead
validates against a stored schema requiring constraints[].origin. A spec-shaped
request fails PLAN_SCHEMA_INVALID at /constraints/0 (required). S3 retains that
failure in its CLI evidence, then exercises the existing S1 interface with an
explicit origin=user_quoted. This is provisional baseline compatibility, not
compliance with the corrected goal contract. Owner must integrate the S1 fix;
S3 does not patch kernel/engine/schema or declare the structural item resolved.

QS3-04 (D11/INV-K1/K2, blocked on S1 test harness): with the first bundled Kit,
test_runtime_contracts.test_atomic_capabilities_do_not_call_other_capabilities and
test_verdict_constructor_and_exception_boundary raise ModuleNotFoundError for
grt_kit_revival_evidence. They use importlib.import_module(entry['module']) rather
than the package mapping in Invoker. Catalog discovery, actual action/check calls,
static structure scanning, and portable verify load the Kit successfully. Owner
should make these probes use the Kit loading seam; no test shim or Core edit was added.

### Kit-internal defaults and source decisions

QS3-02 (D11/B3/S5b handoff, PROVISIONAL): use schema token
identity-expected-results-v1; primer_pair is opaque JSON string/list/object because
S5b prompt defines no inner shape. A determinate null product means no predicted
product; UNDETERMINED is never interpretable. An observation must name the same
reference hash to support/contradict local model agreement. Size tolerance defaults
to exact equality, with explicit observation band_tolerance_bp honored. S5b has no
primer-quality field, so no quality outcome is invented. Change records.py,
assessment.py, handoff fixtures and oracle if owner rejects these defaults.

QS3-05 (D11/D12, PROVISIONAL internal data): normalized observation document,
row_<data-row> ID naming with collision suffix, and rule.parameters.{claim,context,
truth_table} are Kit-local. Each truth row has D12 conditions and a source_ref to
its rule-v1 parent. Generic JSON document ports reuse the S1 toy's local
JSON-value schema because Kit schema registration has no public hook. No protected
schema was added. Rejecting this layout affects Kit capabilities/data/tests only.

Source decisions: 4 declared project-contract rule-v1 rows contain 14 finite
truth-table rows; all source verification remains unverified and no review receipt
was written. Two historical embedded policies lack an attributable source:
legacy.unmodelled_genotype_support and legacy.primer_quality_prerequisite. They
remain draft/unverified under knowledge/drafts and cannot load. Team must identify
an actual project_contract/lab_protocol or discard them. No biological sufficiency
claim or human verification was attributed to the team.

QS3-04 follow-up: broader regression also reproduces the same ModuleNotFoundError
in unit.test_capabilities.test_generated_declarations_match_decorator_exports.
That test additionally resolves every CHECK fixture as ROOT/path; Kit fixture
paths belong to the Kit root. The fixture-path issue is source-observed, not a
second executed failure, because import fails first. S3's own declaration and
fixture tests use the Kit root and actual implementations.

## S1b structural dependencies (2026-10-16)

| Item | Evidence / question | Disposition |
|---|---|---|
| S1B-Q1 | D1/D3/D9: the five S1 interface files were empty on base 54bace6. | Resolved by user merging S1 at c8cc70a. Material/Outcome/decorator/verdict/hash/ctx interfaces now consumed directly. No substitute runtime or S1-owned edit. Historical empty-file evidence is retained under tests/evidence/s1b/before-c8cc70a. |
| S1B-Q2 | Original S1b prompt asked rotation to preserve material identity, conflicting with D9. | Resolved by user: prompt was wrong; origin-dependent sequence/annotation changes can change identity. Retain cyclic k-mer property as a sequence property. Test a nonperiodic rotated material has a different D9 identity; zero rotation stays unchanged. |
| S1B-Q3 | Installed sgffp is outside the dependency allow-list. | Resolved by user: exclude sgffp; `.dna` reading uses Biopython 1.88 only. Supported native fields only; no native writer. |
| S1B-Q4 | Old baseline lacked run.created.git_commit in its schema. | Resolved by owner/S1 merge c8cc70a. Re-run spec_lint and all tests against the merged baseline; no S1b edit to protected schema/spec. |

## S1b integration boundaries

- `Context.run_external(argv)` has no stdin parameter. The Primer3 ACTION writes
  a Boulder request under ctx.workdir and passes its filename in argv; both
  --about and actual computation use that one external-call interface.
- Backend version/executable hash/thermodynamic-file hashes are retained in its
  report document. S1 owns application configuration and run.created environment
  construction; S1b does not add an environment reader or mutate those layers.
- S1 material feature envelopes support exact zero-based coordinates. Compound
  parts and qualifiers are retained as feature content. Fuzzy/remote transforms
  and GenBank-ambiguous feature orientation are explicitly refused.
- Explicit two-material assembly ports fit current admission/input binding;
  larger assemblies use successive material steps and explicit digest indices.
  No unbound JSON-list shortcut replaces material provenance.

## Round2 Kit rehearsal questions (K1 to K6)

Four Kit reports and data-only drafts are under docs/kit-prep. Existing schemas
remain unchanged. Raw Schema/A14 failures are in schema-report.json; a valid
declaration is not evidence that its planned implementation or domain schema exists.

### Structural interfaces

| ID | Exact authority and concrete rehearsal | Proposal for the specification owner |
|---|---|---|
| K1 | D3: `document` inputs are "带 schema_ref". D11: "Kit 能贡献的只有四样：能力（含检查能力）、知识、模板、文案". The drafts require observation-table-v1, primer-set-v1, route-plan-v1, identity-handoff-v1 and other domain schemas; none is in the local registry, and kit-v1 has no schema contribution. capability-v1 itself accepts the schema_ref string, so only checking that schema would miss this. | Specify a single permitted way to register/freeze Kit document schemas, or prescribe core-owned shared schemas. Do not switch the drafts to unconstrained values merely to obtain green validation. |
| K3 | A2 permits input type materials; A3 says a reference is "{literal}、{source}、{step,port,index?}、{artifact} 之一". Genome Identity needs an ordered collection of original/edited backgrounds. Both drafted templates fail existing A3 oneOf when binding an array of material references; current admission also indexes materials output to one material. | Define tracked ordered material-collection binding, or explicitly limit the first Kit contract to fixed individual material ports. No opaque JSON list of DNA is used as a workaround in this rehearsal. |
| K4 | D3: model "指向一个独立实现的预期产物能力" and check.model_agreement "逐位比较两条路径的结果". construct.design_donor has optional preparation inputs and product/primers/route outputs; model_donor has reference/cargo and only product. cut_plasmid.replace_spacer also has more parameters/outputs than its model. The model field carries only an id. | Specify which recorded inputs/params are passed and which output is compared, including whether annotations/ends or only sequence are compared. Prefer a fixed product-port convention if adequate; this task adds no unapproved model-binding field. |
| K6 | D12: evaluator "可以是 ACTION 或 CHECK" and consumes rule parameters. D3 ctx exposes call/workdir/run_external/config; only CHECK has ctx.view including knowledge(pack). D11 restricts Kits to kernel.public/biology.public and their own package. ACTION assess_selection/assess_observations need frozen run knowledge, not mutable current package files. | Define read-only frozen-knowledge access for ACTION evaluators, or a typed, provenance-preserving injection contract. No new ctx field or S1 implementation is added here. |

### Data and delivery details

| ID | Exact authority and concrete rehearsal | Proposal |
|---|---|---|
| K2 | D12: "没有来源的规则无法装载"; rule-v1 requires source_class/citation/locator/retrieved_at/content_ref/archive_note/supports/does_not_support. Task instructions also retain missing-source rows as draft/unverified. The deliberately missing-source probe fails all eight required fields. Actual legacy inventory has 24/24 source-labelled rows, not 24 verified scientific claims. | Keep unsourced rows in an explicitly quarantined preparation artifact outside loadable knowledge until the team supplies a real source. Do not fabricate metadata or weaken rule-v1. Clarify the eventual Kit handoff location relative to KIT-7 contribution membership. |
| K5 | S5b shared shape gives references/regions/primers and `expected: {product_bp|null, status}`, but does not type primer_pair or distinguish absent product from unresolved multiple products when product_bp is null. Its new schema field/arrays differ from legacy schema_version/references-dict/rows. A14 says "未列出的内部字段不得加入" for the governed shapes. | Set the precise shared handoff schema literals, primer-pair reference type and per-background ambiguous/no-product semantics before S5a/S5b/S3 implement them. Keep the old reader strict; do not silently reinterpret it as the new protocol. |

The partial-placeholder probe is an expected A14 rejection, not a request to
relax A14: a full filename parameter already expresses that case. K1/K3/K4/K6
are structural decisions; K2/K5 are explicit data/handoff decisions. All Kit
Python implementation remains deferred to its owner.

## C2 integration boundary after merging S1

Merged s1-minimal-slice at dabe464 (contains s1-closed at acc5aed), merge commit
e47e17e. The six remaining D2 core constraint CHECKs are implemented with explicit
parameter schemas; their bounded meanings are in docs/goal-constraints.md.
regions_unchanged compares a specifically selected retained material id and
explicit coordinate mappings. It does not infer original-source identity or
annotation inheritance. claim_reported checks a structured claim/status at an
explicit JSON Pointer, including an insufficient/unknown status, without
certifying that claim. These choices add no protected schema fields.

S1.1's existing prompt owns three remaining seams: program-derived request
origin, goal-declaration-time validation of constraint params, and optional
output_present.fields. The merged runtime still expects stored-form origin on
the request and validates the new CHECK params at invocation. C2 tests record
this existing interface explicitly; C2 makes no S1-layer changes or premature
goal-rejection claim. No additional D2 CHECK is left unimplemented in C2.

## S3 integration update, 2026-10-17

This section supersedes the S3 provisional integration entries from 2026-10-16.
User explicitly authorized merging main including 7b1ca09 / integration-1b.
Merge 33a99e0 keeps both sets of development records; only append conflicts in
QUESTIONS, DEVIATIONS and MIGRATION-LOG required resolution. No side was discarded.

QS3-01 resolved by S1b integration: goals use check.goal.claim_reported with
params={claim:functional_revival,pointer:/conclusions}; the old output_present
fallback and unbound provisional intent are removed.
QS3-03 resolved by S1.1: goal requests omit constraint origin. The existing Core
computes it from source_quote. S3 no longer sends the compatibility origin field.
QS3-04 resolved by S1.2's Loader and Kit-root fixture resolution. Runtime checking
results are recorded in the updated S3 report; no local loading shim was added to
production or the Core probes.
QS3-02 resolved by current SPEC D11: identity-expected-results-v1 has exactly two
primer IDs, required product_count, and product_bp only for count=1. Count=0 and
count>1 both have null size but distinct meaning. Multiple products are not
interpreted as predicted absence. The reader and independent oracle follow this.
QS3-05: observation and assessment document types are now explicit inline schemas,
frozen in declarations. Their existing Kit-local record fields and row ID naming
are the published Kit contract, not a substitute Core schema registry. Both action
and check use ctx.knowledge(pack); no view.knowledge or live rule-file read remains.
The corresponding PROVISIONAL markers and current workaround documentation are removed.

Two source decisions remain for human team members: legacy.unmodelled_genotype_support
and legacy.primer_quality_prerequisite. Both stay draft/unverified with source=null,
inside knowledge/drafts and outside kit.json. Updated S3-REPORT contains a separate
plain-language team checklist stating the rule, attribution need and exact material
to supply. Integration does not supply a missing source or authorize activation.

S3 validation follow-up (2026-10-17): the first complete layer run passed structure
and contract, then exposed a remaining Kit-root fixture-path assumption in
unit.test_assurance.test_all_check_controls_are_readonly. Unlike the already-fixed
declaration probe, this test still read ROOT/fixture for every owner. The single
shared-test locator now uses session.catalog.entries[name]['root'] or ROOT,
matching tests/unit/test_capabilities.py and the existing Kit fixture contract.
No fixture, assertion, CHECK invocation or production module was removed/changed.
The actual failed log is dist/s3-round2-full-01/unit.log. The corrected read-only
probe ran successfully in dist/s3-round2-readonly-path-fix.log. Unit, integration
and e2e are rerun after the fix; earlier successful structure/contract results
remain attributed to their original execution rather than claimed as rerun.
## S5b Genome Identity (2026-10-17)

Authority: SPEC D3, D7, D11; parallel-addendum-20261017.md read from
`<SEPARATE_WORKTREE>` because the
user-named main-worktree path did not contain that file. No prompt/spec was copied or edited.

| ID | Question and authority | Provisional choice / recommendation | If rejected |
|---|---|---|---|
| S5B-Q1 | D11 names `identity.compare_regions` but does not define its interval/comparison document or alignment scoring. | Kit-local default: fixed original/edited material ports, explicit nonwrapping half-open intervals, exact equality and unit-cost global Levenshtein distance. No alignment-derived genotype claim or homology threshold. Schema frozen inline in declaration. | Change only compare_regions declaration/function/template and corresponding tests. |
| S5B-Q2 | D11 says distinct `(product_count, product_bp)` signatures are necessary for DISTINGUISHABLE, and multiple unresolved products give UNDETERMINED. The scalar size is null for multiple products; their size distribution is unavailable. | Conservatively mark any background with multiple predicted physical products UNDETERMINED. Otherwise follow exact D11 count/size comparison. Gel resolution remains unverified, not an extra threshold. | Owner must define how multiple-product size distributions can be resolved within D11; change local discrimination and tests. |
| S5B-Q3 | D11 requires background ids and file SHA-256; direct reference analysis has no imported handoff ids. | Use fixed material-port names reference_original/reference_edited as ids without a handoff. Always hash actual registered reference-file bytes and decode them with shared readers to match their materials. With a handoff retain its ids and require its hashes/primer ids/sequences to agree. | Change local default id assignment and from_references example expectations. |
| S5B-Q4 | D1/common: new reusable algorithms stay in the Kit pending owner decision. Existing predict_pcr_products enumerates the submitted forward primer on the reference plus strand only. | Kit-local wrapper runs the shared predictor for both primer orders and deduplicates physical reference intervals. This preserves predictions after reversing reference orientation and counts equal-size products at distinct loci separately. New region-distance implementation also stays local. No biology/shared capability edit. | Owner can move these helpers into biology later; no cross-Kit import is added now. |

### S5B-Q5: structural blocker, sealing and portable verification not achieved

SPEC D7 derives on_material_output checks whenever any completed step returns a
material. The two templates use the existing format.read_fasta actions for the
two references and primers. At integration-1 (`fc04e41`) the frozen profiles
require `check.annotation_integrity`, `check.cds_validity` and
`check.biological_sanity`, but none is registered in Catalog. A real public-CLI
seal returned exit 10 and UNKNOWN for all three, after the prediction had already
completed with independently confirmed 1000/1300 bp outputs.

Evidence: tests/evidence/s5b/e2e-run03.txt and e2e-blocked.txt, with original
receipts retained in the external run directories named in REPORT.md.
No schema, profile, CHECK declaration or other owner's implementation was changed.
The positive end-to-end acceptance test remains a real failure until the shared
capabilities exist. Portable verification is NOT_EXECUTED, not a pass or a skip.

Recommendation for the shared-capability owner: implement the three required
checks with honest applicability, independent positive/negative examples and
offline support, then integrate them and rerun the unchanged positive acceptance
criterion. S5b stops at this structural dependency and continues independent
algorithm, binding, schema, negative-fixture, mutation and pipeline/Judge work.
## S2 Cut Plasmid (integration-1, 2026-10-17)

### Structural dependency, stop only at final acceptance

**S2-Q1, D7/D8/B2.** The frozen base profiles require
`check.annotation_integrity`, `check.cds_validity`, `check.biological_sanity`,
`check.reaction_chain` and `check.order_table`, but integration-1 has no
declarations or implementations for them. `check.primer_quality` requires explicit
single-stranded material IDs and exact-complementarity limits; a default call
returns UNKNOWN, whereas B2 specifies a retained primer document and length/Tm
limits. These are Core-owned paths. Recommendation: the mainline owner completes
the existing checks and specifies their route/primer document consumption contract.
S2 implements its Kit and retains a public-CLI run up to the real rejected seal;
it does not replace Core checks, weaken profiles, or claim seal/portable verify.
Example: even a correct 360-base B2 construct is blocked by these missing checks.
AI action here: retain the exact rejection and independent sequence/PCR evidence.
Specification owner action: supply the Core checks, then rerun the same B2 case.

### Kit internal provisional details

**S2-Q2, D3/D11/B2, PROVISIONAL.** Kit inline document fields describe cassette
coordinates, primer binding-core lengths, explicit DNA_NN3 Tm inputs, and an
inverse-PCR/circularization route. No shared document schema or new public state
is introduced. B2's dnac1=250 nM/dnac2=0 convention is not expressible by the
shared TmParameters (which derives equal strand concentrations). S2 uses the
already allowed Biopython Tm_NN directly with all B2 parameters explicit, inside
its own capabilities directory. It calls existing shared capabilities through
ctx.call for material editing and inverse-PCR sequence simulation. If rejected,
adjust Kit contracts and preparation implementation; no Core file needs changing.
CHECK fixture params are reserved for the CHECK call; setup_params contains the
prerequisite inspection's parameters. This is test data only, not a new runtime port.

**S2-Q3, D11/D12, PROVISIONAL.** One rule-v1 selection_markers.json contains
host-specific rule-v1 rows under parameters.rows. Each row retains its own source;
the container cites the project migration contract only for the collection format.
Legacy source labels are not new verification receipts. New source verification
is unverified, review remains absent. Source-incomplete rows belong in
knowledge/drafts and are excluded from the manifest. If rejected, split the rows
into individual rule files and update only Kit knowledge loading and manifest.

**S2-Q4, D7/B2, PROVISIONAL.** Retain the legacy supplied-vector-only NGG,
both-strand, Hamming-distance search, with explicit vector_max_mismatches 0..3
(legacy default 3). An exact match gives FAIL; a near match or an incomplete
ambiguous-base search gives UNKNOWN rather than PASS or a claim of measured
cleavage. This is not a genome scan. If rejected, adjust the Kit parameter and
check policy; no Core state, check ID or error code needs changing.

**S2-Q5, D3/D8/B2, integration limitation.** integration-1 resolves an artifact
source to its registered file path; only as:material JSON is resolved directly
to a material. Existing format.read_genbank actions already supply the explicit,
logged conversion. S2's templates and B2 case therefore prepend these actions.
The stager exports bound materials/documents as JSON and refuses artifact plan
outputs. S2 records a GenBank export/readback as ordinary plan steps, retaining
that file in work/export; it does not add a Kit-owned stage or promote it as a
sealed file. Recommendation: Core owner settles the final export contract along
with S2-Q1. The retained inline route/primer shapes are in capabilities/contracts.py.

### Additional structural test dependency

**S2-Q6, D11/D18.** Full-suite test_all_check_controls_are_readonly opens every
CHECK fixture under the Core project ROOT (tests/unit/test_assurance.py:86).
Bundled Cut Plasmid declarations, like the existing external toy Kit, use paths
relative to their Kit directory. The full suite actually raises FileNotFoundError
for project-root capabilities/fixtures/check_direction.pass.json. The correct
file is kits/cut-plasmid/capabilities/fixtures/check_direction.pass.json.
Recommendation: the Core test owner resolves Kit fixtures against the catalog
entry's Kit root, Core fixtures against project ROOT. S2 does not modify that
shared test or duplicate fixtures into the wrong project-root directory. Its own
six pass/fail fixtures execute through the actual Invoker. Core test owner action:
fix that one path-resolution assumption and rerun the complete suite.
## S4a release-engineering handoff

### Structural integration, S4A-01

D16 says release_id is the canonical release-manifest digest, loaded and checked
once, with development trees explicitly labelled dev-tree. Current
application/run_service.py:create assigns dev-tree unconditionally; kernel/release
reads versions but does not consume the release manifest. S4a builds and checks
the manifest without changing those S1-owned layers. The bundled B1 example
therefore truthfully retains dev-tree. Proposal: the S1 owner implements the
specified manifest load/identity check before release verification is claimed.
No passing runtime release receipt is fabricated by the builder.
The owner must also agree how the manifest is carried into an installed package;
the current pyproject data rules do not install the source-root manifest. The
prepared fresh verifier compares the new run's identity with the archive and
keeps a dev-tree mismatch INCOMPLETE rather than treating it as release success.

### Shipping policy and pending material

Task S4a explicitly requires ship.json; no such file existed at integration-1.
The new include/exclude policy is delivered for the specification owner's
review and protected-hash registration under D15/DEV-3. No existing protected
resource, version source or decision record was edited. The engineering checker
implements F10, not a claim that the protected-file review gate F7 is closed.

The user/team supplies the four AI-disclosure entries in README. The Kit owners
supply the pending accepted architecture overview. The five literal markers
remain counted, make the source status INCOMPLETE and prevent a real release ZIP.
The new release lock pins locally observed transitive dependencies in addition
to the existing runtime roots/backend; nothing was installed or downloaded.
The fresh-environment script was prepared and its no-install plan tested. Actual
fresh-environment installation remains a separate authorization step under task
item 4, after a real candidate exists. S4 is not declared complete.

C15 (night addendum 1, independently confirmed scientific negative): an initial
120 nt synthetic target ORF and 96 nt marker both used AAA internal codons.
Their selected junction primer cores therefore matched both backgrounds. The
standard-library checker calculates two 90 bp junction bands in both original
and edited references; construct.check_junction_assay correctly fails. This
failure is retained. A separate positive construction uses GCT target codons
and AAA marker codons; no expected donor length/arms/band sizes or gate is
relaxed. This is a new explicitly discriminating synthetic input, not a repair
of the refused input or a sequence-identity exception in runtime code.

C16 (night addendum 1, Windows evidence transport): Git initially rejected deep
record paths and warned about line-ending normalization. Per-command longpaths
and an evidence-local -text/CRLF whitespace attribute preserve immutable bytes;
122 manifest-listed files match their Git-index bytes. This is local archive
transport, not a relaxed runtime integrity or scientific check.

C17 (night addendum 2, PROVISIONAL audit ownership criterion): a stage label or
an instruction to read a chapter is not a concrete follow-up implementation
assignment after a recorded deferral. On that explicit-task criterion the audit
finds 11 unassigned invariant requirements plus the S4A-01 runtime release-id
handoff, and three partially implemented review requirements lacking closure.
S0 empty-tree conditional scope is not silently extended to later data. The
owner should confirm task ownership in daylight. No missing feature was
implemented, no inventory row reclassified by this read-only audit.

C18 (night addendum 2, observed D17 ambiguity): public goal declare accepts a
natural-language original_request containing a 320 nt synthetic DNA string and
the original goal event retains it. Current long-literal enforcement covers
parameters; it does not clearly cover prose. No external connection occurred.
Owner should define whether original prose must reject >200 nt sequence runs
or whether this is an additional explicit privacy exception. Do not infer
anonymity or claim all sequence text is stripped. Only synthetic data was used;
probe outputs remain ignored under dist/spec-coverage-probes.

C19 (night addendum 3, PROVISIONAL v1 observation boundary): D3/INV-C4 and
D6/INV-E3 require post-call detection, not operating-system confinement. The
minimal implementation observes synchronous Python write operations during
module loading and capability execution, and rehashes known inputs, store
objects, explicit artifact inputs and CHECK candidates on both return and
exception. Trusted nested Invoker storage/journal bookkeeping is excluded;
child violations still propagate if capability code catches the exception.
No capability write is prevented or rolled back. Arbitrary reads, detached work and
native/child-process writes outside known protected paths are not globally
observed. INV-C4 has AST/runtime/mutant evidence within this stated boundary;
complete ctx-only interaction (INV-E3) remains pending rather than certified.

A real default-bytecode probe initially produced an interpreter .pyc write and
incorrectly halted an otherwise pure capability. A second constructed failure
shows the same problem during a lazy helper import. The observed call now
temporarily disables interpreter bytecode-cache creation, restores the prior
process flag, and still observes module/body writes. Both regressions reproduce
the earlier false positives; no extension-based file exemption was added.
The flag is process-wide during the call; concurrent-thread policy is not
established here. Write intents are recorded for the later verdict, including
an out-of-scope attempt whose actual filesystem operation subsequently fails.
Owner should confirm this limited v1 boundary and assign remaining read/native
I/O coverage before claiming arbitrary external Kit confinement. No new runtime
field, event, error, check, dependency or protected contract is introduced.

## S4b release identity and installation handoff

E1 (D16, protected environment shape): D16 mentions recording
release_verified:false for an invalid release manifest. The existing protected
run.created environment schema has no such property; this task forbids new
fields/events and protected edits. That recording item remains NOT_IMPLEMENTED.
The installed runtime instead returns the existing SOURCE_CHANGED error before
creating a run, as explicitly required by S4b, with no dev-tree fallback.
Development execution without an installed manifest remains dev-tree. Proposal
for the specification owner: confirm this error-only installed-package behavior,
or separately authorize the environment-field contract and its validation.

E2 (D15/D16, observed release ZIP blockers): the actual S4b source check returns
FAIL, not just INCOMPLETE. README retains the three human disclosure markers;
docs/judges/architecture.md retains one further marker. The existing checker
also identifies absolute machine paths in kits/cut-plasmid/README.md,
kits/genome-identity/REPORT.md and tests/oracles/prepare_cut_plasmid.py. No path
values are reproduced here. S4b does not alter these other owners' historical
content, fill markers, change ship.json or weaken the release check. The
maintainers should normalize the documentation paths, decide whether the legacy
authoring helper belongs in the release selection, and finish the pending
architecture/disclosure content. Source-wheel installation is separate evidence;
no real project ZIP was built and clean_env_verify --execute remains unperformed.

E3 (D16, future bundled-example verification): strict installed-release matching
correctly refuses a retained dev-tree seal. The existing bundled B1 seal is
dev-tree, so it cannot satisfy clean_env_verify's matching installed-release
verification. Also, directly including a new seal that already names the final
release-manifest digest inside that manifest's hashed payload is self-referential.
No mismatch exemption, rewritten historical seal or invented release evidence
was added. Before the real ZIP path can pass, the specification owner must decide
how retained development examples are verified alongside release-bound new runs.
S4b leaves this item unimplemented and continues only independent source-wheel
tests, whose new sealed runs are outside the installed release payload.

E4 (D16/D9, observed retained-example format mismatch): the existing bundled B1
seal fails public verify in BOTH the current source checkout and the installed
wheel, at journal event 9. An independent hashlib+rfc8785 calculation finds all
event hashes and prev links intact. Public jsonschema validation instead finds
that call.recorded events 9 and 22 omit params and params_digest, now required
by the current protected payload schema. The current chain reader reports this
as JOURNAL_CHAIN_BROKEN; it has not reached the E3 release-id comparison.
This is an old-format incompatibility, not evidence that wheel copying damaged
the journal. No old journal, seal or protected schema was rewritten. The
specification owner should decide historical-example/version support; maintainers
can generate a separately identified current-format example after that decision.
Do not backfill unrecorded historical call parameters or relax verification.
The real ZIP verifier remains NOT_PERFORMED, and this independent legacy-example
probe is a retained failure, not a successful ZIP execution.

## S4d dispositions of the S4b handoff

The specification owner's f7f5886 patch resolves E1/E3 without a new environment
field. Only spec/ and archive/ from that commit were synchronized into s4d.
An intact dev-tree seal is permitted alongside an installed release; a different
64-character release identity still returns SOURCE_CHANGED. Development seals
continue to say they are not release evidence. The original refusal and two
deliberate code mutations are retained in tests/evidence/s4d/.

E4: the thirteen original B1 files are preserved byte-for-byte under
tests/evidence/s4d/legacy-b1/ and still fail current public verification as an
old-format negative. A newly executed B1, with the hand answer TTCTGACT, replaces
the shipped example. No old event or protected schema was edited.

E2: the real unchanged release check now has zero findings and three README
human-disclosure markers; the real ZIP builder still refuses publication.
The two documentation path locations use existing USER/WORK/TEMP placeholders.
The legacy authoring helper now requires an explicit local --legacy-repo input;
its pinned commit, rule conversion and 37 compared generated files are unchanged.
Historical software inventories refer to their own source commits: all six
referenced inventories and the old file bytes at those commits remain intact,
as checked in tests/evidence/s4d/path-reference-check.json. No sealed record,
historical inventory or Git history was rewritten. The human README remains
unchanged; no S4 approval, release ZIP or CI success is claimed here.
## S4e: existing Core limits exposed by the tutorial (2026-10-17)

S4E-Q1, SPEC D11 contribution table: `kit.json` declares `text/en.json` and
`catalog.kits.read` checks that it exists, but the current catalog/renderer does
not consume Kit translations. The tutorial and anatomy diagram show only the
implemented file check. Suggestion for the Core owner: connect declared text
to rendering in a separately assigned change. No Core change is made here.

S4E-Q2, SPEC D20 RV-2/RV-3: public `review sign` currently returns
`CHECK_UNAVAILABLE`, explicitly deferring interactive human signing. The tutorial
executes that negative probe, leaves review pending and creates no `review/`
record. Responsible people must perform review; the Core owner must implement
the assigned signing workflow before a tutorial can demonstrate a signature.
