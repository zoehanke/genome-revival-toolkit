# Schema boundaries after S1.2

Current D3/A2 authority: SPEC 96db7d0. Input and output document ports now
require exactly one schema_ref or inline schema object. Inline schemas are
validated as Draft 2020-12, frozen in capability declarations and checked at
input binding and before output persistence. Ten construction-defined fixtures
cover both directions, both valid alternatives, both/neither and malformed
inline schemas. SCHEMA-DIFFERENCES.json is regenerated with zero differences.
S1c resolves Q13 under owner SPEC 945d702: call.recorded now requires actual
params and params_digest, copied from the step.started shapes. This is S1c's
only authorized protected schema change. Nested value retention enables replay;
missing-record negatives remain UNKNOWN. See S1C-REPORT.md for current evidence.

The S0 sections below are retained historical evidence, not current runtime
coverage. See S1-FOLLOWUP-REPORT.md and tests/IMPLEMENTED_INV.json for S1.2.

## S0 boundary record (historical)

Authority: SPEC 8ad9c44 and corrected A14 in 12c4274. Draft 2020-12 schemas
follow A2/A9/A14. `granularity` is required (`atomic|composite`); `authorship` is
optional on capability, rule and pipeline-template declarations. Supplied
authorship still requires kind, tool_or_model and date. At S0, document inputs
required schema_ref; S1.2 adds the inline alternative above. CHECK retains required offline.

The former five body/appendix field discrepancies are resolved in the spec.
SCHEMA-DIFFERENCES.json now compares those fields directly; no legacy
authorization allow-list suppresses differences. Spec files were not edited here.

## Previously opaque fields

| Shape now checked | Basis |
|---|---|
| Runtime kind, executable argv probe, null Python-package probe | A14 |
| Failure causes `{code, message}` | A14 |
| Manifest profile `{profiles_digest, obligation_ids[]}` | A14 |
| Receipt endpoint object or null; no-run null state/range | A14 |
| Package-name/version map; actor with optional version in four payload fields | A14 |
| goal.amended.diff JSON Patch operation array | Corrected A14, RFC 6902 / RFC 6901 |
| Completed and retained material/document port arrays of ids | A14; E retained-output equivalence |
| Source/step/artifact/literal origin.ref discrimination | A14; literal ref is now null |
| Both unsatisfied arrays use check/outcome/verdict_id/recovery | A14 |
| First event prev is 64 zeroes | D9 |

Remaining `x-s0-gap` markers in schemas: **0**. No currently named internal shape
remains unresolved. `pipeline.revised` has no diff; `declaration.recorded` keeps
its own actor with kind/name. Corrected locations are goal.amended.diff and
input.registered.declared_by, not new event fields.

Protocol objects are closed. Explicit maps use patternProperties for caller
keys. JSON Patch objects use fields of their defined operation under A's
closed-object rule; no patch executor is implemented.

## Validation outside JSON Schema

JSON Schema cannot compare a placeholder name against another object's property
names. The development checker checks A14 whole-string spelling, lowercase names
of 1–32 characters, value-only placement, and declared type plus description.
It does not substitute values or execute plans. Parameter declarations and
authorship metadata are not substituted. Embedded parameter schemas are checked
against the Draft 2020-12 meta-schema. CHECK/ACTION naming remains a structural
check, although it could also be expressed with JSON Schema conditionals.

Fixtures are hand-authored/construction-defined. `tests/contract/a14-coverage.json`
indexes 28 new shape groups, each with a positive and at least two independent
negative cases. No oracle is derived from schemas or validator results.
The original missing-authorship case is retained with its expected result updated
to true specifically because A2/A9 now make that field optional. Existing literal
origin fixtures use null under A14; manifest/goal-diff fixtures use the specified
objects/arrays. Historical cases remain in fb8e911.

## Runtime obligations remain pending

| Contract | Still requires runtime validation |
|---|---|
| D2/D4/D5 | Goal immutability; reference/port binding; actual JSON Patch application to previous goal; frozen steps; instantiated template validation |
| D3/D6 | Atomic/composite call behavior, installed declaration/code agreement, CHECK positive/negative execution, effects, port cardinality |
| D6/D9 | Continuous event sequence, chain computation, identity semantics, readback and recovery in actual engine |
| D7 | Obligation union and ownership; applicability, independent models and inherited-findings correspondence |
| D8/D10 | Staged bytes, immutable seals, receipt sequence-range correspondence, evidence ownership and hash-linked reporting |
| D11/D12/D20 | Version compatibility, contribution files, sources/review hashes and display; missing applicability information |
| D17 | Runtime zero-connection proof and redaction, literal sequence limits, contained file resolution |
| D16 | INV-F10 release contents, approved license and repository size; no release is assembled in S0 |

These semantic checks are not unspecified fields and are not counted as schema
gaps. The ledger has 32 static checks and 87 pending items, including new INV-F10.
This does not close S0 or authorize S1.
