# Architecture overview, draft

DNA Design Core separates goal declaration, pipeline admission, execution,
checking, sealing, offline verification and rendering. A capability contributes
a declaration and a callable; an ACTION produces content, while a CHECK returns
a read-only verdict. The recorded producer decides output roles. Goal constraints
and the frozen catalog determine required checks.

Source map:

- kernel: canonical identities, materials, schemas and public capability interfaces.
- biology: shared pure sequence and reaction calculations.
- storage: retained content and ordered execution records.
- catalog: capability, knowledge and Kit discovery.
- engine: admitted execution and explicit input/output bindings.
- assurance: required checks, sealing and offline verification.
- record: projections and offline result cards.
- application: public CLI/API and configuration.

## Scientific Kits

Four Kits contribute capability declarations and callables, linear pipeline
templates, English text and, where needed, sourced knowledge through the same
`kit-v1` contract. Core discovers these contributions through its catalog;
execution, required checks, sealing and report rendering remain Core services.
Kit-specific checks cannot replace mandatory Core checks. These are bounded
computational workflows, not evidence of successful laboratory work.

| Kit | Explicit inputs | Retained outputs and scope | Does not establish |
| --- | --- | --- | --- |
| [Cut Plasmid](../../kits/cut-plasmid/README.md) | Supplied vector and target materials/files; a user-selected 20-base spacer; explicit cassette coordinates and transcription direction; optional recipient genotype | Sequence-derived direction, NGG and supplied-vector self-target checks; replacement material, complete primers and simulated inverse-PCR/circularization route; conditional selection interpretation. No candidate enumeration. | Cleavage activity, editing efficiency or genome-wide off-target safety. |
| [Construct](../../kits/construct/README.md) | Reference and cargo materials; edit/cargo intervals, homology-arm and primer lengths; overlap for Gibson or an existing donor template for PCR | Donor material and primers; junction-PCR predictions on edited, original and residual donor sequences; original/edited reference files and a hash-bound Identity handoff. Primer length alone does not establish thermal quality. | Successful laboratory donor preparation, transformation efficiency, authentic integration locus or functional revival. |
| [Genome Identity](../../kits/genome-identity/README.md) | Original/edited references and reference files; explicit primer pair or Construct handoff with named primers | `identity-expected-results-v1` document: per-background reference-file hash, primer pair and predicted product count/size; optional explicit-region comparison. Predictions cover supplied references. | Primer specificity in an actual strain, observed experimental products, authentic genotype or whole-genome discrimination outside supplied references. |
| [Revival Evidence](../../kits/revival-evidence/README.md) | Submitted CSV/JSON observations; optional Identity predictions and reported assay/control records | Analysis document with bounded conclusions, reasons, rule sources and unperformed checks. Colony counts alone remain insufficient for functional revival; reported observations are not authenticated experiments. | Experimental success, functional revival or authenticity of submitted observations. |

Each boundary is also declared in the corresponding
[Cut Plasmid manifest](../../kits/cut-plasmid/kit.json),
[Construct manifest](../../kits/construct/kit.json),
[Genome Identity manifest](../../kits/genome-identity/kit.json) and
[Revival Evidence manifest](../../kits/revival-evidence/kit.json).
Input/output contracts are the capability JSON documents listed by those manifests.
Preparation and experimental steps remain `PLANNED` / `NOT_PERFORMED`.

The S4b installation exercise ran all four Kits from a newly installed source
wheel: nine synthetic cases, public CLI receipts, independent file checks and
copy-only sealed-directory checks. Retained repository evidence is
`tests/evidence/s4b/example-logs-final/` and
`tests/evidence/s4b/install-final-runtime/`, described in `S4B-REPORT.md`.
That exercise concerns supplied synthetic examples, not arbitrary Kit compatibility,
real genotypes, wet-laboratory performance or release ZIP approval.

## Release identity

Development runs record `dev-tree`; their cards explicitly say they are not
release evidence. An installed build reads and checks its release manifest.
Offline verification accepts an intact development seal in either environment;
a release-bound seal must match the current installed release identity.
File integrity, journal, replay and required scientific checks still apply.
See `kernel/release.py`, `application/run_service.py` and
`tests/integration/test_release_identity.py` under the product source tree.

Official GitLab CI 未执行；GitHub CI 未运行。
