---
name: genome-identity
description: Compare supplied original and edited DNA references, predict exact PCR products, or export Construct handoff expectations for Revival Evidence. Use only supplied references. Whole-genome identification and interpretation of observed bands need other evidence.
---

Use the existing Core goal, pipeline, execute, seal and verify commands. This Kit
contributes four actions and two pipeline templates. It has no separate runner.

1. Register synthetic or user-supplied files locally as Goal artifact sources.
   With a Construct handoff, register the delivered handoff JSON and its two
   hash-referenced files. Without one, register references and primer FASTAs.
   Declare an analysis target and an output-present
   constraint at the exact installed Core version. Omit constraint origin.
2. Instantiate `genome-identity.from_handoff` or `genome-identity.from_references`.
   Supply source ids, explicit reference topologies, goal digest, target id,
   assay id and forward/reverse primer ids. Source ids must differ from template
   step ids. Primer sequences are complete, exact 3-prime binding sequences;
   tails and degenerate binding are outside this model.
3. Submit the draft unchanged and execute it. `from_handoff` reads FASTA, GenBank
   or native DNA references through existing Core readers and selects the named
   primers from the handoff. `from_references` keeps explicit primer FASTA inputs.
   Analyze checks the actual reference-file hashes and
   decoded material identities, plus handoff ids/primer sequences/region bounds.
   A changed reference produces a failed step, not an identity conclusion.
4. Inspect `identity-expected-results.json`. Count zero means no exact predicted
   product; count above one means multiple predicted physical products. Size is
   null in both cases; the count distinguishes them. Different exact size or
   presence can distinguish supplied backgrounds; multiple products remain
   undetermined. Neither state establishes an observed genotype.
5. Run normal Core sealing and verify. An unavailable mandatory check stays
   UNKNOWN and blocks sealing. A candidate is not a sealed handoff. Only a
   successfully sealed result can be handed on as a verified delivery.

The runnable synthetic demonstration and independent oracle are documented in
README.md. Laboratory work stays PLANNED / NOT_PERFORMED.

<!-- GENERATED:START -->
### identity.analyze_assay

Predict exact PCR products on two file-bound references and export D11 expectations.

Inputs: reference_original, reference_edited, forward (optional), reverse (optional), reference_original_file, reference_edited_file, handoff (optional).

Parameters: assay_id, forward_id, reverse_id.

### identity.compare_regions

Compare explicit supplied intervals by exact equality and unit-cost global edit distance.

Inputs: reference_original, reference_edited.

Parameters: original_start (optional), original_end (optional), edited_start (optional), edited_end (optional).

### identity.read_handoff

Parse the D11 Construct handoff; file and material binding is checked by analyze_assay.

Inputs: file.

Parameters: none.

### identity.read_reference

Read a supplied FASTA, GenBank or native DNA reference without rewriting its bytes.

Inputs: file.

Parameters: topology.
<!-- GENERATED:END -->
