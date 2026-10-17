# Genome Identity

Predict whether one supplied primer pair can distinguish an original reference
from an edited reference. Output is the exact D11 expectation document for
Revival Evidence. It is a computational prediction, not observed PCR or genotype.

S1c supplies the shared checks missing on the historical integration-1 baseline.
Current checks still decide whether a particular result can seal. Original
failed evidence remains in REPORT.md; current S1d validation is in S1D-REPORT.md
at the product root.

## Inputs and output

`analyze_assay` takes fixed material ports `reference_original`,
`reference_edited`; optional `forward`, `reverse` material ports; reference-file artifact ports
`reference_original_file`, `reference_edited_file`; optional inline-schema
`handoff` document; and `assay_id`, `forward_id`, `reverse_id` parameters.
Reference files can be FASTA, GenBank or native DNA supported by existing Core
readers. `from_handoff` reads each actual format through `identity.read_reference`
and selects both explicitly named primers from the handoff. Register only the
delivered handoff and references; primer files are not needed. Supplying one
primer without the other fails. Explicit conflicting primers still fail.
`from_references` retains four FASTA inputs. Declare reference topology and double strands;
primers must be linear, single stranded and concrete A/C/G/T.

`read_handoff` parses `identity-handoff-v1` from an artifact. Its output alone
does not prove file binding. `analyze_assay` checks binding before predicting.
`compare_regions` reports exact equality and unit-cost global edit distance on
explicit nonwrapping intervals. This is sequence comparison, not genomic mapping.

Output document:

```json
{
  "schema": "identity-expected-results-v1",
  "assay_id": "synthetic_identity",
  "backgrounds": [
    {
      "id": "original",
      "reference_sha256": "<actual reference-file SHA-256>",
      "primer_pair": ["forward", "reverse"],
      "expected": {"status": "DISTINGUISHABLE", "product_count": 1, "product_bp": 1000}
    }
  ]
}
```

The abridged example shows one row; actual output has original and edited rows.
Schema and strict document shapes are embedded in exported declarations.
Sequence files are hash-referenced by the handoff. Their DNA is not embedded.
No new core schema, public state word, entry point or profile was added.

Count/size signatures equal: NOT_DISTINGUISHABLE. Different signatures with at
most one product per background: DISTINGUISHABLE. Any multiple-product background:
UNDETERMINED. Both reference orientations are searched; identical physical
intervals are deduplicated, equal sizes at separate sites remain multiple products.
PCR is searched over the complete supplied references; handoff regions are
validated metadata, not an instruction to ignore other sites in those references.

## Reproduce synthetic results

From `code/genome-revival-toolkit` in this worktree, use its existing virtual
environment. No installation or download is needed; Biopython is locked at 1.88
in the existing requirements-biology.lock.

```powershell
$env:PYTHONPATH='src'
& '.\.venv\Scripts\python.exe' -X utf8 -B -m unittest tests.unit.test_genome_identity tests.integration.test_genome_identity -v
```

The standalone public-CLI run keeps original receipts, rejected seal and failed
handoff-hash run. Choose a new output folder; existing evidence is never replaced.
Exit 2 means the positive seal/verify criterion was not met.

```powershell
$env:PYTHONPATH='src'
& '.\.venv\Scripts\python.exe' -X utf8 -B tests\e2e\run_genome_identity.py --out "$env:TEMP\grt-identity-demo-new"
```

Independently check the supplied synthetic expected table using standard library
window enumeration, with no Kit/Core import:

```powershell
$env:PYTHONPATH='src'
& '.\.venv\Scripts\python.exe' -X utf8 -B tests\oracles\genome_identity.py --original kits\genome-identity\examples\original.fasta --edited kits\genome-identity\examples\edited.fasta --forward kits\genome-identity\examples\forward.fasta --reverse kits\genome-identity\examples\reverse.fasta --handoff kits\genome-identity\examples\identity-handoff.json --expected kits\genome-identity\examples\identity-expected-results.json
```

The literal construction places two 20-base primer sites around 960 interior
bases, then inserts 300 bases in the edited interior. This determines 1000 and
1300 bp before implementation runs. Additional tests cover equal sizes, absent
products, duplicate sites, reversed references, circular-origin sites and hash
mismatches. An independent oracle rejects a deliberately false 1299 bp table.

## Interpretation and review

`unverified` carries unset annealing temperature, untested primer thermodynamics,
unmeasured gel separation, absent whole-genome specificity alignment and absent
laboratory/genotype confirmation. Three historical project-scope rules are not
loaded or presented as verified science. No scientific rule table needs a
fabricated source. Source/genotype authenticity, mismatched-primer amplification,
single-oligo self-amplification and reaction efficiency are outside this exact
two-primer reference model.

Kit-local defaults are listed in QUESTIONS.md S5B-Q1 to Q4. S5B-Q5 records the
historical shared-check blocker. Gate closure belongs to the specification owner after rerunning
the actual acceptance checks. Official GitLab CI 未执行；GitHub CI 未运行。
