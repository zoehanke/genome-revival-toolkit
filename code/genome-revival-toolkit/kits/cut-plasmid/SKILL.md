---
name: cut-plasmid
description: Inspect a user-selected SpCas9 spacer in a supplied vector, replace that spacer, simulate inverse-PCR preparation, or interpret source-labelled selection markers. Use explicit promoter boundary, transcription strand and scaffold anchor. Candidate-guide discovery, genome-wide off-target analysis and efficiency prediction require another method.
---

Inspect sequence before changing the cassette. Preserve the user's target and the failed inspection when revision is needed.

1. Register supplied vector and target GenBank files as artifact sources in the goal. Use `cut-plasmid.inspect_only` to read those files and inspect the directed 20-base cassette. `pam_valid=false` identifies an invalid supplied guide/PAM combination; it does not authorize choosing a replacement guide.
2. When the user has selected a replacement spacer, instantiate `cut-plasmid.replace_spacer` or revise the original pipeline before execution. Keep the original goal and supersede its failed inspection. `replace_spacer` must be a direct pipeline step because its independent expected model is checked at that level.
3. Read complete primer sequences, binding-core lengths, explicit Tm inputs and retained linear intermediate. Sequence simulation does not establish physical PCR, DpnI treatment or KLD. These and transformation, sequencing and guide activity remain `PLANNED` / `NOT_PERFORMED`.
4. Read selection status from `assess_selection`. Missing recipient genotype means `UNKNOWN`; report it in Not done. With explicit organism, existing markers and auxotrophies, mapped media remain conditional on that declaration. Review migrated citations in [knowledge/SOURCES.md](knowledge/SOURCES.md).
5. Run the Core `judge`, `seal`, `record render` and `verify` commands. Present only files returned by a successful seal as formal delivery. A missing required Core check leaves an unsealed candidate with its diagnostic.

The scaffold anchor and directed promoter boundary are user declarations. The synthetic example in [examples/b2.json](examples/b2.json) has no validated promoter, replication origin or selectable function.

Coordinates are 0-based boundaries on the supplied positive reference. For `transcription_strand=1`, the spacer starts at `promoter_end`; for -1, its first transcribed base is at `promoter_end-1`, read toward decreasing coordinates. Circular coordinates wrap explicitly. `scaffold_sequence` follows the 20 spacer bases in transcription orientation.

Tm is for the annealing core, with the full tailed oligo retained separately. The example's length/Tm settings and concentrations are in [README.md](README.md). The bounded vector search gives FAIL for an exact self-target, UNKNOWN for a near match or an incomplete ambiguous-base search. It does not evaluate a recipient genome.

<!-- GENERATED:START -->
Generated from decorated capability contracts and signatures.

| Capability | Inputs | Parameters | Outputs |
| --- | --- | --- | --- |
| cut_plasmid.assess_selection@0.1.0 | vector:material | strain_genotype=null | selection:analysis |
| cut_plasmid.check_direction@0.1.0 | none | none | verdicts only |
| cut_plasmid.check_pam@0.1.0 | none | none | verdicts only |
| cut_plasmid.check_vector_self_target@0.1.0 | none | none | verdicts only |
| cut_plasmid.inspect_guide@0.1.0 | vector:material, target:material | promoter_end (required), transcription_strand (required), scaffold_sequence (required), vector_max_mismatches=3 | guide:analysis |
| cut_plasmid.model_replace@0.1.0 | vector:material | promoter_end (required), transcription_strand (required), spacer (required) | product:None |
| cut_plasmid.replace_spacer@0.1.0 | vector:material, target:material | promoter_end (required), transcription_strand (required), scaffold_sequence (required), spacer (required), length_min=18, length_max=36, tm_min="55", tm_max="62", tm_parameters=null, vector_max_mismatches=3 | product:construct, primers:primer_set, route:None |
<!-- GENERATED:END -->

AI drafted, without human review. Does not establish cleavage activity, editing efficiency or genome-wide off-target safety.
