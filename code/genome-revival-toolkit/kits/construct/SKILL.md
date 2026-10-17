---
name: construct
description: Design an integration donor for one explicit replacement or deletion on a supplied linear reference, prepare by PCR or Gibson, and assess junction PCR. Use Genome Identity for interpreting existing assay discrimination and Revival Evidence for observations. Circular edits are outside this Kit.
---

Submit a goal with actual reference/cargo files, explicit edit/cargo intervals and
homology-arm length. PCR also needs an existing complete donor-template file and
its interval. Choose an explicit primer length and, for Gibson, an overlap.

Instantiate `construct.prepare_gibson` or `construct.prepare_pcr` through the
standard grt interface. The template computes the model first, prepares from
actual templates, predicts both external junctions, exports references and writes
identity-handoff.json. Keep design_donor as a direct plan step so model comparison
has its recorded inputs and parameters. Read warnings for residual donor bands.
The seal receipt includes the handoff plus `identity_original.gb` and
`identity_edited.gb`, byte-identical to the references hashed in that handoff.
Register those three delivered files for `genome-identity.from_handoff`; select
the primer ids from the handoff. Additional primer FASTA files are unnecessary.

Run judge, seal and verify through grt. Present only the files returned by seal.
A failed or unavailable mandatory check blocks sealing.
Laboratory preparation and junction PCR are PLANNED / NOT_PERFORMED.

<!-- GENERATED:START -->
## Input contracts

Strict field shapes are in the linked exported declarations.

| Capability | Inputs (? optional) | Required parameters | Outputs | Extra final checks |
|---|---|---|---|---|
| [construct.check_junction_assay](capabilities/check_junction_assay.json) |  |  |  |  |
| [construct.check_preparation](capabilities/check_preparation.json) |  |  |  |  |
| [construct.design_donor](capabilities/design_donor.json) | reference:material, cargo:material, donor_template:material? | start, end, arm_length, cargo_start, cargo_end, preparation_method, primer_length | product:material, edited:material, oligos:materials, intermediates:materials, primers:document, route:document | construct.check_preparation |
| [construct.design_junction_assay](capabilities/design_junction_assay.json) | original:material, edited:material, donor:material, primer_file:artifact? | start, end, arm_length, primer_length | primers:document, assay:document | construct.check_junction_assay |
| [construct.export_handoff](capabilities/export_handoff.json) | original_file:artifact, edited_file:artifact, assay:document |  | handoff:artifact, reference_original:artifact, reference_edited:artifact, handoff_data:document |  |
| [construct.model_donor](capabilities/model_donor.json) | reference:material, cargo:material | start, end, arm_length, cargo_start, cargo_end | product:material |  |

Model: construct.design_donor declares construct.model_donor; check.model_agreement is automatically required.

Does not establish: Successful laboratory donor preparation; Transformation efficiency; Authentic integration locus; Functional revival.

<!-- GENERATED:END -->
