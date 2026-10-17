# S0 algorithm migration sample

## S5a Construct: source-bounded rewrite, 2026-10-17

Read-only source: genome-revival-toolkit/revival/construct.py at
750bf4849b818be00f28684513ef19c01d901bcb. The actual file has 205 lines;
its normalized working text matches that Git commit. The prompt's older
223/46/47 inventory is not reused as a measurement of this file.

| New file under kits/construct/capabilities | Lines | Retained idea / rewrite |
|---|---:|---|
| model.py | 25 | Independent donor expectation from explicit reference/cargo intervals; no preparation algorithm import |
| design.py | 98 | Actual donor-template PCR or three PCR fragments and two Gibson joins; complete oligos and intermediates retained |
| assay.py | 108 | Junction primers outside arms; explicit original/edited/residual-donor backgrounds; every match retained |
| handoff.py | 30 | D11 file-byte hashes and exact handoff shape, without old handoff protocol |
| checks.py | 75 | New read-only preparation and junction checks using actual retained inputs |
| contracts.py | 79 | New declarations and strict inline domain schemas; not a second registry |

New Kit Python: 415 lines, including 79 declaration/schema lines. Shared biology
is reused and unchanged; it is not counted as newly ported Kit code. The four
source-derived files carry ported-from headers. This is a rewrite of the stated
domain behavior, not a claim of literal copying or acceptance of old outputs.

Removed coupling: nine old project import statements, comprising six Core,
two revival and one Evidence Trace imports. ProjectContext and old material /
ToolResult interfaces become typed material/document/artifact ports and Outcome.
The old runner, delivery wrapper and manual observe calls are not imported.
Workflow becomes two pipeline-template-v1 data files. The three legacy scope
policies are consolidated into explicit parameters, preparation checks and
does_not_establish; no scientific threshold or unsourced rule pack is loaded.

The old Gibson feature_to_dict / checked_scope failure motivated real labelled
linear-fragment controls. The first new test found cargo CDS annotations lost
when native cargo overlap was clipped. Moving overlaps to cargo PCR tails keeps
the full source CDS. Genuine invalid preparation still returns a registered
input failure, without the old secondary exception. Old code was not executed.

Evidence: tests/evidence/s5a-construct/migration-measurement.json and focused logs.
Full seal/verify, copied-package verification and formal D7 finding-origin
classification remain blocked by the integration-1 core; see QUESTIONS.md.


Read-only source snapshot: `750bf4849b818be00f28684513ef19c01d901bcb`.
Selected working files matched the committed contents after line-ending
normalization. Old repository was not edited or executed. No old module was
imported. These samples stay under `spikes/`, outside runtime and packaging.

| Sample | Old relative source / selected functions | Old selected / whole-file lines | New file / function lines | Result |
|---|---|---:|---:|---|
| Reverse complement plus linear PAM scan | `snapgene-dna-design/scripts/design_guides.py`: `_iupac_compatible`, `pam_matches`, `scan_guides` | 132 / 390 | 28 / 19 (`sequence_sample.py`) | 5 construction/hand tests pass |
| NN Tm | `snapgene-dna-design/scripts/validation_crosscheck.py`: `bio_tm_nn` | 18 / 231 | 13 / 8 (`tm_sample.py`) | 3 hand-arithmetic/boundary tests pass |

Line counts include docstrings and blank lines inside AST function spans; file
counts include imports/header. New scan is a deliberately bounded subset, so
these numbers are **not** a full-port reduction or effort estimate.

## Coupling encountered

Sequence source: 1 caller-facing record protocol (`record.seq` plus topology
metadata), 0 imported project model classes. Module imports 12 bindings from 7
modules: standard library argparse/json/pathlib/sys; external Bio.Seq.Seq;
project sg_common.{jprint,load_seq,topology} and
provenance.{source,source_id,now_iso,read_version}. The scan also calls registry,
coordinate, circular-slice, context and id-assignment helpers. It reads package
version and builds provenance while calculating hits. Those are removed from the
pure sample. Source input becomes a string; pattern/length are explicit values.
New sample imports 1 external binding, 0 project bindings, 0 old types.

Tm source: 0 old types, 0 old project imports. Whole module imports 3 external
bindings (Seq, MeltingTemp, gc_fraction); selected function uses MeltingTemp only.
New sample keeps 1 external binding, makes concentrations explicit and returns a
calculation instead of a legacy result/provenance dictionary. It does not swallow
exceptions into an apparently valid scientific result.

## Must be designed again before real migration

* Sequence sample does not transfer features, strand ends or lineage. It excludes
  circular wrapping, 5-prime PAMs, ambiguous sequence interpretation and regions.
  Full support needs new material/coordinate contracts and independent cases.
* Registry lookup, version/provenance decoration and context-window generation
  belong at declared boundaries, not hidden inside the scan.
* Tm-to-verdict conversion, bounds, method applicability and independent reaction
  checks remain unimplemented. No quality verdict or laboratory claim is made.

Independent expected values and public development commands are in
`spikes/README.md`. `spikes/runs/samples.json` was generated and read back: forward
guide [0,20), PAM [20,23), reverse complement TTCTGACT; both Tm results agree with
the independent arithmetic within 1e-8 C. The 8 tests use only synthetic inputs.
No heldout evaluation, human experimental assistance or wet experiment occurred.

Task item 9 explicitly selects this log instead of protected
`spec/MIGRATION-MAP.md`; that file remains untouched. Official GitLab CI 未执行.

## S3 Revival Evidence migration (2026-10-16)

Source repository was read-only. Current old checkout is commit
750bf4849b818be00f28684513ef19c01d901bcb. Historical Kit files removed from that
checkout were read with git show, never imported or executed.

| Old source | Exact revision | Measured old lines | New destination / measured lines |
|---|---|---:|---|
| genome-revival-toolkit/revival/evidence.py | 750bf4849b818be00f28684513ef19c01d901bcb | 131; read_observations 7, _count 13, run_evidence 95 | kits/revival-evidence/capabilities/records.py, 155 |
| genome-revival-toolkit/kits/evidence/scripts/workflow.py | e8534135adb98f5a294eb17134a4c22a65def7ac | 137; conclusion_rows 5 | context for splitting workflow from interpretation; no runner port |
| genome-revival-toolkit/kits/evidence/scripts/predictions.py | bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | 104; _assessment 16, compare_expected 30 | kits/revival-evidence/capabilities/assessment.py, 153 |
| genome-revival-toolkit/kits/evidence/rules/conclusions.json | e8534135adb98f5a294eb17134a4c22a65def7ac | 2 rules x 4 presence states | functional_revival.json and genome_elimination.json; all 8 old truth-table cells retained |
| New capability wrappers, declarations and recorded-consistency checking | New implementation | n/a | kits/revival-evidence/capabilities/evidence.py, 152 |

Counts include blank/docstring lines. Runtime total is 460 Python lines; this is
not a full-port compression or productivity measurement. The task prompt's old
workflow 158-line description differs from the actual 131/137-line revisions read.

Old coupling removed: evidence_trace.models.file_digest, evidence_trace.runtime
observe/observe_source, revival.__version__, context.references/reference_info,
legacy record-version/reference bindings, inline hash calculations and workflow
request/output formatting. No old Molecule class was imported, and the new Kit
has no material ports. Core owns registration, pipeline execution, event writing,
export, card rendering, sealing and verify. The Kit only imports kernel.public
and its own capability modules.

Preserved boundaries: missing counts stay unknown; an inactivated-donor
no-outgrowth control with colonies contradicts that local absence claim; local
assays do not establish functional revival or whole-genome elimination; missing
predicted assays are NOT_TESTED. The B3 difference is raw 9-31=-22. Legacy yield
normalization was not ported or relabelled as efficiency. Conflicting duplicate
sample/assay/background records now produce an explicit input error instead of
silently choosing a reported result.

Four declared project-contract rule-v1 files contain 14 sourced table rows.
Their verification remains unverified; row source_ref identifies the parent
source. Two embedded old policies without attributable sources remain excluded
as draft/unverified candidates: legacy.unmodelled_genotype_support and
legacy.primer_quality_prerequisite. Team must source or discard them. No human
review file, verification receipt, or biological sufficiency rule was fabricated.

The S5b output interface was adapted to its current prompt, not to the historical
rows/references format. Actual cross-Kit integration is still untested. See
QS3-01 through QS3-05 for provisional defaults and two Core blockers.
Official GitLab CI 未执行；GitHub CI 未运行.

## S1b batches 1 to 4 (2026-10-16)

Read-only source commit: `750bf4849b818be00f28684513ef19c01d901bcb`.
All 12 selected source files match that commit after newline normalization,
verified with `git show`. No old module was imported/executed or file changed.

Every row below identifies the old function and rewritten function/class.
Numbers are AST spans including docstrings/blank lines. Whole-file line counts,
source import modules and line ranges are in
`tests/evidence/s1b/migration-inventory.json`; regenerate with
`tests/oracles/migration_inventory.py --legacy-root <old-source-directory>`.
Repeated old functions indicate splitting a large routine, so summing the old
rows double-counts code. These counts do not measure a complete tool migration.
New type/validation/protocol portions were rewritten rather than copied intact.

| New module / symbol | Old source / symbol | Old function lines | New function/class lines |
|---|---|---:|---:|
| `biology/sequence/operations.py:normalize_dna` | `snapgene-dna-design/core/tools/snapgene_io.py:_normalise_dna` | 11 | 9 |
| `biology/sequence/operations.py:interval_segments` | `snapgene-dna-design/core/interval.py:validate_interval` | 107 | 19 |
| `biology/sequence/operations.py:slice_sequence` | `snapgene-dna-design/core/interval.py:extract_interval` | 27 | 11 |
| `biology/sequence/operations.py:map_feature` | `snapgene-dna-design/core/tools/sequence_ops.py:_clip_feature_to_intervals` | 112 | 76 |
| `biology/sequence/operations.py:slice_record` | `snapgene-dna-design/core/tools/sequence_ops.py:slice_record_interval` | 47 | 25 |
| `biology/sequence/operations.py:rotate_record` | `snapgene-dna-design/core/tools/sequence_ops.py:rotate_sequence` | 9 | 15 |
| `biology/formats/records.py:record_projection` | `snapgene-dna-design/core/io/molecule_codec.py:visible_fingerprint` | 10 | 11 |
| `biology/formats/records.py:read_genbank` | `snapgene-dna-design/core/io/input_resolution.py:_read_record_from_file` | 26 | 11 |
| `biology/formats/records.py:write_genbank` | `snapgene-dna-design/core/io/molecule_codec.py:genbank_record` | 26 | 15 |
| `biology/formats/records.py:read_fasta` | `snapgene-dna-design/core/io/input_resolution.py:_read_record_from_file` | 26 | 11 |
| `biology/formats/records.py:write_fasta` | `snapgene-dna-design/core/tools/snapgene_io.py:export_snapgene` | 59 | 16 |
| `biology/formats/records.py:read_dna` | `snapgene-dna-design/core/tools/snapgene_io.py:_read_native_data` | 17 | 11 |
| `biology/primer/thermodynamics.py:TmParameters` | `snapgene-dna-design/core/tools/amplification.py:calc_primer_tm` | 69 | 27 |
| `biology/primer/thermodynamics.py:calculate_tm` | `snapgene-dna-design/core/tools/amplification.py:calc_primer_tm` | 69 | 28 |
| `biology/primer/quality.py:dimer_metrics` | `snapgene-dna-design/core/tools/amplification.py:check_primer_dimers` | 68 | 22 |
| `biology/primer/quality.py:hairpin_metrics` | `snapgene-dna-design/scripts/primer_qc.py:score_hairpin` | 25 | 18 |
| `biology/primer/quality.py:primer_quality` | `snapgene-dna-design/core/tools/amplification.py:calc_primer_tm` | 69 | 15 |
| `biology/primer/quality.py:evaluate_primer_quality` | `snapgene-dna-design/scripts/primer_qc.py:flag_risks` | 15 | 36 |
| `biology/primer/primer3.py:encode_boulder` | `snapgene-dna-design/core/tools/primer3_backend.py:encode_boulder` | 13 | 12 |
| `biology/primer/primer3.py:parse_boulder` | `snapgene-dna-design/core/tools/primer3_backend.py:parse_boulder` | 12 | 26 |
| `biology/primer/primer3.py:primer3_check_request` | `snapgene-dna-design/core/tools/primer3_backend.py:check_complete_oligo_pair` | 66 | 36 |
| `biology/pcr/prediction.py:find_binding_sites` | `snapgene-dna-design/core/tools/amplification.py:_find_primer_binding` | 93 | 34 |
| `biology/pcr/prediction.py:predict_pcr_products` | `snapgene-dna-design/core/tools/amplification.py:simulate_pcr` | 205 | 28 |
| `biology/pcr/prediction.py:simulate_pcr` | `snapgene-dna-design/core/tools/amplification.py:simulate_pcr` | 205 | 12 |
| `biology/pcr/prediction.py:simulate_pcr_record` | `snapgene-dna-design/core/tools/amplification.py:simulate_pcr` | 205 | 30 |
| `biology/restriction/digestion.py:enzyme_definition` | `snapgene-dna-design/core/tools/restriction.py:get_enzyme` | 19 | 14 |
| `biology/restriction/digestion.py:scan_restriction_sites` | `snapgene-dna-design/core/tools/restriction.py:restriction_hits` | 83 | 42 |
| `biology/restriction/digestion.py:digest_sequence` | `snapgene-dna-design/core/tools/restriction.py:digest_sequence` | 45 | 70 |
| `biology/assembly/simulation.py:compatible_ends` | `snapgene-dna-design/core/models/assembly_model.py:compatible_sticky` | 14 | 15 |
| `biology/assembly/simulation.py:validate_duplex` | `snapgene-dna-design/core/models/assembly_model.py:_validate` | 8 | 33 |
| `biology/assembly/simulation.py:ligate_fragments` | `snapgene-dna-design/core/tools/assembly.py:ligate_fragments` | 49 | 28 |
| `biology/assembly/simulation.py:gibson_assemble` | `snapgene-dna-design/core/models/assembly_model.py:join_by_homology` | 14 | 30 |
| `biology/assembly/simulation.py:inverse_pcr_circularize` | `snapgene-dna-design/core/recipes/mutagenesis.py:recipe_site_directed_mutagenesis` | 351 | 23 |

Coupling removed and mandatory rewrites:

| Batch | Old coupling | Rewritten boundary |
|---|---|---|
| 1 formats | Path guessing; Molecule/MoleculeInput; metadata supplements and fingerprints; sgffp/reader fallback; desktop executable lookup | Strict text/bytes input; SeqRecord is a format carrier. No file access or hashes. GenBank equivalence covers sequence/topology/features. FASTA rejects unrepresentable annotations. Native reading uses allowed Biopython with bounded fidelity; no native writer. |
| 2 sequence | PlanningError/TaskValidationError, task-kind flags, ConstructModel, derived_molecule, primer-coordinate synchronizer | Strict integer half-open segments, explicit topology, copied feature positions/qualifiers, partial CDS/primer handling. Exact local positions only. Material construction and circular identity acceptance await S1B-Q1/Q2. |
| 3 primer/PCR | MoleculeInput, FragmentEnd, ToolResult, heuristic core selection, hidden QC thresholds, subprocess/discovery/cache/installation | Explicit core/tail lengths, every exact binding pair, unique-PCR refusal. Raw structural metrics, caller-supplied thresholds. Tm emits concentration/model/table/symmetry parameters. Boulder codec only; runtime invocation and missing-backend CHECK await S1B-Q1. |
| 4 restriction/assembly | AssemblyFragment/FragmentEnd/derived_molecule, reaction checks, record loaders, hashes; mutation-design and protocol logic | Both cut strands and actual extensions, unknown natural ends retained, actual duplex validation before joining. Explicit overlap lengths. Sequence-only inverse-PCR closure retains intermediate. No mutation-design or laboratory protocol port. |

All module-level old project imports are counted/listed in the inventory JSON.
New biology imports zero old modules/types. TmParameters holds thermodynamic
parameters, not materials. Digest/PCR dictionaries describe sequence
calculations without material IDs, storage or lineage contracts.

Generation comparison: scripts/design_primers.py and
scripts/primer_design_engine.py retain old ranking/consent/provenance paths.
Core amplification.py and primer3_backend.py supply the modern library seams.
The unique pure hairpin fallback from scripts/primer_qc.py was rewritten with
explicit loop minimum and without heuristic score/threshold constants.

Independent answers: tests/fixtures/biology/oracles.json maps all 33 public
symbols to constructed/hand-answer tests. The Primer3 comparison additionally
retains independent requests/stdout and executable/data-file version/hashes.
No runtime adapter or generated capability declaration is claimed: S1-owned
kernel interfaces are empty. See QUESTIONS.md and S1B-REPORT.md.


## S1b integration after S1 merge c8cc70a

User resolved the origin/identity and dependency questions, and merged the S1
interfaces. New adapters call kernel.material.normalize and kernel.ids, with no
new material class, hash implementation, verdict factory or environment reader.
Native reading stays on Biopython 1.88; sgffp remains excluded.

The table below records the additional material adapters. Old routines provide
source invariants/codec ideas; these adapters are substantial rewrites, not
line-for-line ports. In particular, reconstructing and validating both strands
from top sequence plus actual extensions is newly written. Full counts for all
48 public symbols / 13 source files are in migration-inventory.json.
The earlier 33-row table remains the pre-integration snapshot; use the current
inventory JSON for present function spans and counts after parameter fixes.

| New symbol | Old source / selected function | Old span lines | New span lines |
|---|---|---:|---:|
| `biology/materials.py:make_material` | `snapgene-dna-design/core/models/molecule.py:__init__` | 47 | 30 |
| `biology/materials.py:record_from_material` | `snapgene-dna-design/core/models/molecule.py:as_molecule` | 25 | 30 |
| `biology/materials.py:material_from_record` | `snapgene-dna-design/core/models/molecule.py:to_dict` | 17 | 17 |
| `biology/materials.py:material_to_duplex` | `snapgene-dna-design/core/models/molecule.py:__init__` | 47 | 26 |
| `biology/materials.py:material_from_duplex` | `snapgene-dna-design/core/models/molecule.py:as_molecule` | 25 | 5 |
| `biology/materials.py:material_to_genbank` | `snapgene-dna-design/core/io/molecule_codec.py:genbank_record` | 26 | 12 |
| `biology/materials.py:material_from_genbank` | `snapgene-dna-design/core/io/molecule_codec.py:restore_file_metadata` | 45 | 13 |
| `biology/materials.py:material_to_fasta` | `snapgene-dna-design/core/tools/snapgene_io.py:export_snapgene` | 59 | 6 |
| `biology/material_operations.py:slice_material` | `snapgene-dna-design/core/tools/sequence_ops.py:extract_subsequence` | 47 | 3 |
| `biology/material_operations.py:rotate_material` | `snapgene-dna-design/core/tools/sequence_ops.py:rotate_sequence` | 9 | 5 |
| `biology/material_operations.py:pcr_material` | `snapgene-dna-design/core/tools/amplification.py:simulate_pcr` | 205 | 7 |
| `biology/material_operations.py:digest_material` | `snapgene-dna-design/core/tools/restriction.py:digest_sequence` | 45 | 24 |
| `biology/material_operations.py:ligate_material` | `snapgene-dna-design/core/tools/assembly.py:ligate_fragments` | 49 | 13 |
| `biology/material_operations.py:gibson_material` | `snapgene-dna-design/core/tools/assembly.py:simulate_overlap_assembly` | 120 | 16 |
| `biology/material_operations.py:inverse_pcr_material` | `snapgene-dna-design/core/recipes/mutagenesis.py:recipe_site_directed_mutagenesis` | 351 | 14 |

Removed coupling: old SeqRecord subclass/lineage/version fields, MoleculeInput
unions, shape guessing, FragmentEnd class, in-function hashing, file loaders,
protocol construction and automatic Primer3 installation. New kernel material
content stays in its five fields; exact feature parts/qualifiers remain feature
content. GenBank supplement is bound to its visible projection through kernel
hashes and cannot restore a different visible sequence or feature record.
FASTA explicitly refuses unrepresentable metadata.

22 thin capabilities are exported from @capability metadata, with 18 ACTIONs
and 4 CHECKs. Capabilities use only kernel.public and biology.public, plus their
own declaration helpers. Formal inputs are material/artifact/value ports;
ordered two-material assembly uses explicit references, not opaque JSON lists.
Every new capability maps to an independent answer in capability-oracles.json.
The four CHECKs use kernel.verdict.make and declared positive/negative fixtures.

Primer3 remains a separate executable. Both version probe and numerical request
use ctx.run_external(argv); Boulder input is passed as a workdir file. Version,
executable/data hashes and raw measurements remain in a stored report. No new
configuration reader, subprocess launch outside ctx, external binary, native
writer, Kit implementation or reverse-complement capability is introduced.


## Round2 shared preparation functions

Source commit 750bf4849b818be00f28684513ef19c01d901bcb, working source compared
with Git objects before measurement. No old module was imported or executed.
All four functions have at least two explicit Kit consumers in shared-needs.json.
The old Core has reused algorithms but also legacy types/results/IO; no bridge
or Kit workflow is carried over.

| New function | Old selected source | Old selected / file lines | New selected / file lines | Consumers |
|---|---|---:|---:|---|
| `biology/sequence/preparation.py:replace_material_region` | `snapgene-dna-design/core/models/construct_model.py:replace` | 4 / 362 | 47 / 88 | Cut Plasmid, Construct |
| `biology/sequence/preparation.py:inspect_cds` | `snapgene-dna-design/core/tools/sequence_ops.py:validate_cds_feature` | 179 / 724 | 25 / 88 | Cut Plasmid, Construct |
| `biology/primer/preparation.py:enumerate_primer_candidates` | `snapgene-dna-design/core/recipes/verification.py:_verification_candidates` | 70 / 556 | 31 / 81 | Cut Plasmid, Construct, Genome Identity |
| `biology/primer/preparation.py:sequencing_read_coverage` | `snapgene-dna-design/core/recipes/verification.py:sequencing_coverage` | 32 / 556 | 36 / 81 | Cut Plasmid, Construct |

Rewrite/coupling: region editing drops the ConstructModel wrapper and retires
intersecting annotations rather than assert their original function. The old
three-line replace delegates to delete/insert; its small span is not the entire
old algorithm or a reduction claim. CDS inspection returns bounded frame/code
metrics, not legacy verdicts or resistance. Primer enumeration uses explicit
lengths/anchor/NN parameters and retains all sites; complete-tail QC and core Tm
stay separate. Read coverage projects stated distances from unique 3-prime ends,
not old Trace/RecipeResult records or actual sequencing quality.

Four ACTION adapters use the existing metadata exporter via the existing
seq/primer modules. Their four generated capability-v1 resources are a necessary
consequence of Task C's corresponding-capability deliverable and D3; no protected
schema/vocabulary is changed. All functions have hand/construction tests, actual
Invoker cases and four recorded source mutations. No CRISPR or Kit algorithm was
implemented. Single-Kit donor/discrimination/observation policy remains with its
Kit owner.

## C2 six core goal checks

New implementation from SPEC D2/GOL-4/GOL-6 and D9, not an old-code port:
capabilities/builtin/check/goal.py implements topology, exact_sequence,
components_present, components_absent, regions_unchanged and claim_reported.
Old function path/line counts: not applicable. No legacy framework, types,
results, Kit policy, material class, hash algorithm or verdict constructor is
introduced. It consumes the existing kernel.public identity/verdict interfaces,
read-only view and biology.public.reverse_complement from merged S1.

Each exports CHECK/user_goal/evaluates_constraint=true/offline=true with exact
params and a pass/fail construction pair. Six source mutations are independently
caught. Components inspect sequence, regions compare explicit stored identities
and coordinate pairs, reported claims inspect actual bound JSON content.
Generated Core resources/docs/index are updated through existing tools.

## S3 round 2, integration-1b (2026-10-17)

The S3 source migration above remains historical evidence. User-authorized merge
33a99e0 includes main 7b1ca09 and preserves S1b's separate migration records.
Post-merge S3 code adopts the existing frozen-knowledge interface and inline
schema support, rather than adding a new registry or importing legacy code.
The handoff reader and independent oracle now use product_count, retaining the
logical distinction between zero and multiple products. No new legacy source
was executed or imported, and no previously unattributed policy was activated.
The original truth tables and 2 draft candidates retain their provenance state.
## S5b Genome Identity (2026-10-17)

Read-only legacy source: `<WORK>/github`, Git object
`bf90910e5b0e67985aa37db4e0b8507cbc24f2b4`, paths
`genome-revival-toolkit/kits/identity/scripts/workflow.py` and `handoff.py`.
The requested old `revival/identity.py` path is superseded by this source layout,
as already inventoried in docs/kit-prep/genome-identity.md. No legacy code was
executed or imported, no DNA input was read, and the old checkout was untouched.

| Old source | Old physical lines | Retained responsibility | New implementation |
|---|---:|---|---|
| workflow.py | 161 | Supplied-background discrimination; old `_discrimination` is 19 lines | New D11 three-state count/size comparison is 6 lines; full two-primer orientation wrapper is 11 lines. Legacy states/gel-resolution workflow are replaced by D11; no claim of semantic equivalence to old output. |
| handoff.py | 38 | Strict handoff file/reference binding and machine-readable expectations | New parser is 8 lines, actual-file/material binding helper is 21 lines and analyze_assay is 39 lines; shared format readers and kernel hash functions are reused. |
| comparison.py (inventory only) | 142 | Explicit given-region comparison | Fresh 12-line unit-cost global edit-distance helper and 15-line interval action; no old alignment API imported/copied, not an old scoring-equivalence claim. |

New runtime file `kits/genome-identity/capabilities/operations.py`: 281 physical
lines including inline schemas, declarations, limitations and helpers. Exact
function spans and installed dependency versions are in tests/evidence/s5b/inventory.json.
These differently scoped numbers are an inventory, not a code-reduction percentage.

The two old scripts reference seven distinct external project modules
(`core.tools.comparison`, `core.tools.amplification`, `core.tools.primer3_backend`,
`core.tools.result`, `evidence_trace.runtime`, `evidence_trace.models`, `revival`),
plus their own handoff module. Discarded couplings include context.materials /
reference_info, material.record_version, result.only_product, to_wire, manual
observe/observe_files, old schema_version/rows and formatted summaries. The
new code imports only standard library, kernel.public and biology.public.

Kit contributions: three typed ACTIONs, strict generated inline-schema
declarations, two data-only templates, English text and a generated-input
SKILL contract. Shared PCR/format algorithms are reused rather than copied;
the new Kit-local helpers are registered in QUESTIONS.md S5B-Q1/Q4. No new
CHECK/profile/public vocabulary or rule lifecycle is added. Historical rules
are not loaded and verified flags/human review are not inherited.

Construct/Revival Evidence working-copy declarations were read as JSON only:
S5b's synthetic handoff validates against Construct's output schema and the
expectation table validates against Revival Evidence's prediction-input schema.
Raw shape-validation results are in tests/evidence/s5b/interop.json. This is
schema interoperability evidence, not an executed multi-Kit workflow or approval.

Acceptance remains blocked at shared mandatory checks; positive sealing and
portable verification were not achieved. See QUESTIONS.md S5B-Q5 and the
retained real CLI rejection. Official GitLab CI 未执行；GitHub CI 未运行。
## S2 Cut Plasmid

Read-only source commit: bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 in
<WORK>/github. Four reference files contain 778 lines in total:
grna.py 293, grna_evaluation.py 209, grna_preparation.py 152, and the legacy
crispr/scripts/selection.py 124. Source function-by-function counts and the new
file counts are retained in tests/evidence/s2/migration-stats.json. These are
reference-file counts, not an assertion that every line was copied.

The seven new Kit Python files total 585 lines, including the independent model,
inline contracts and check declarations. Header ported-from markers identify each
reference. No old module is imported or executed. The old Molecule/ToolResult
interfaces, KitCatalog and rule caches, derived_molecule lineage, check_result,
old runners, workflow, gates, entry and rendering are removed. The Kit consumes
kernel.public Outcome/material identities/verdicts and biology.public primitives;
all nested actions use ctx.call.

The production edit path rotates the template, calls seq.replace_region, rotates
back, designs complete unique primers and calls assembly.inverse_pcr. Its
model_replace uses separate per-base assignment with no edit/PCR/locator imports.
The external standard-library oracle independently extends the actual primers and
closes the resulting circle. A separate table-based NN calculation and Primer3
2.6.1 invocation cross-check B2 binding-core Tm with explicit concentrations.

The legacy selection.json is 519 lines containing nine marker rules, not 519
biological records. Migration yields ten host-specific rule-v1 rows with the
original citation/locator and bounded supports/does_not_support. Manufacturer,
peer-reviewed-paper and curated-database source categories map respectively to
official_method, literature and database_record. Legacy verification labels do
not become new verification receipts: all sources are unverified and review is
absent. Source-incomplete row list is empty. No scientific table is team-approved
by this migration.

S2-Q1 records the missing/incompatible Core final checks. B2 reaches an actual
rejected seal; inherited finding classification, successful seal and portable
verify are not claimed. No Core implementation, schema, profile or specification
was modified.
