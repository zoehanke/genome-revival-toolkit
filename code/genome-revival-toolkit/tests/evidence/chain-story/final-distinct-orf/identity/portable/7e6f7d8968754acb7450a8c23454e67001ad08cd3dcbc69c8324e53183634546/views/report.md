# Run card

Through event 60

Journal head: e1b4ef0576f558cf2e4ed57b50e5e42e7a60ae14747a23a3d08e776b8e08c748

## Data chain

Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.

- read_original · format.read_genbank → read_original.material[0] (structure)
- read_edited · format.read_genbank → read_edited.material[0] (structure)
- read_forward · format.read_fasta → read_forward.material[0] (structure)
- read_reverse · format.read_fasta → read_reverse.material[0] (structure)
- read_handoff · identity.read_handoff → read_handoff.handoff[0] (structure)
- regions · identity.compare_regions → regions.comparison[0] (structure)
- assay · identity.analyze_assay → assay.expected_results[0] (structure)
- Host-reported goal and reasons → read_original · format.read_genbank (dashed)
- Host-reported goal and reasons → read_edited · format.read_genbank (dashed)
- Host-reported goal and reasons → read_forward · format.read_fasta (dashed)
- Host-reported goal and reasons → read_reverse · format.read_fasta (dashed)
- Host-reported goal and reasons → read_handoff · identity.read_handoff (dashed)
- Host-reported goal and reasons → regions · identity.compare_regions (dashed)
- Host-reported goal and reasons → assay · identity.analyze_assay (dashed)
- original (user_file) → read_original · format.read_genbank (structure)
- edited (user_file) → read_edited · format.read_genbank (structure)
- forward (user_file) → read_forward · format.read_fasta (structure)
- reverse (user_file) → read_reverse · format.read_fasta (structure)
- handoff (user_file) → read_handoff · identity.read_handoff (structure)
- read_edited.material[0] → regions · identity.compare_regions (solid)
- read_original.material[0] → regions · identity.compare_regions (solid)
- read_forward.material[0] → assay · identity.analyze_assay (solid)
- read_handoff.handoff[0] → assay · identity.analyze_assay (solid)
- read_edited.material[0] → assay · identity.analyze_assay (solid)
- edited (user_file) → assay · identity.analyze_assay (structure)
- read_original.material[0] → assay · identity.analyze_assay (solid)
- original (user_file) → assay · identity.analyze_assay (structure)
- read_reverse.material[0] → assay · identity.analyze_assay (solid)

## Checked by the program

- Pipeline admitted after static validation.
- check.readback [file]: PASS · Exported content comparison.
- check.manifest [file]: PASS · File list and byte hashes checked.
- check.journal_chain [file]: PASS · Recorded event chain checked.
- check.store_hashes [file]: PASS · Stored content identities checked.
- check.inputs_unchanged [file]: PASS · Registered input copies checked.
- check.goal.nonempty [user_goal]: PASS · Active goal constraints counted.
- check.goal.target_role_met [user_goal]: PASS · Producer roles compared with target roles.
- check.replay [content_model]: PASS · Deterministic output identities compared.
- check.lineage [content_model]: PASS · Input bindings and identities compared.
- check.annotation_integrity [content_model]: PASS · Output findings compared with explicitly bound input features.
- check.biological_sanity [content_model]: PASS · Nonempty DNA and physical declarations checked without empirical thresholds.
- check.goal.output_present [user_goal]: PASS · Bound output presence checked.

## Declared only

- Host-reported original request: Synthetic computational chain; laboratory steps PLANNED / NOT_PERFORMED.
- plan_declared: Read the registered synthetic original FASTA with explicit physical properties.
- plan_declared: Read the registered synthetic edited FASTA with explicit physical properties.
- plan_declared: Read the registered synthetic forward FASTA with explicit physical properties.
- plan_declared: Read the registered synthetic reverse FASTA with explicit physical properties.
- plan_declared: Read the Construct handoff without guessing a legacy format.
- plan_declared: Compare the two complete supplied reference intervals.
- plan_declared: Bind reference file bytes to materials and predict exact products in both backgrounds.
- present [host_derived]: report result

## Not done

- Annealing temperature was not set; exact binding does not establish PCR performance.
- Authentic genotype.
- Biological correctness of feature names or strand/function claims.
- Complete-CDS start/stop validation of explicitly partial or pseudogene annotations.
- Empirical thresholds not supplied by sourced rule data.
- Experimental function or correct transcription.
- Experimental performance or correctness of a scientific conclusion.
- Experimental viability, function, efficiency or host-specific performance.
- Gene expression, protein activity, selectable phenotype or wet-laboratory function.
- Genome-wide safety or thermodynamic structure quality unless explicitly measured.
- Global unit-cost sequence comparison of selected intervals only; genomic placement and genotype are unverified.
- Laboratory PCR and genotype confirmation: NOT_PERFORMED; laboratory steps remain PLANNED.
- No CDS feature was present in recorded material outputs.
- Observed experimental products.
- Primer specificity in an actual strain.
- Primer thermodynamic quality and experimental band separation were not measured.
- Programmed frameshifts, recoding or unannotated strain-specific genetic code differences.
- Revisions recorded: 0
- This development-tree package is not release evidence.
- Unknown physical properties or ambiguous base identities.
- Wet-laboratory performance or biological function.
- Wet-laboratory success, biological function or reaction efficiency.
- Whole-genome discrimination outside supplied references.
- Whole-genome specificity alignment was not performed; only supplied reference sequences were searched.
- check.cds_validity [content_model]: NOT_APPLICABLE · No CDS feature was present in recorded material outputs.
- reviewed 0 / stale 0 / none 5

## Technical details

- Event 1: run.created; program; 04594f579d12995f745b972051d9ffa792e359358ca8b73d9315de18041236e9
- Event 2: input.registered; program; 29c1ef77b3a13d1415ac47b74761caff5a34e3588d9668a5f83560088983e849
- Event 3: input.registered; program; 61cd5ae95ed3729a4a35ccd71a2199fe8e16d402c21642ff16007c96c837b0c0
- Event 4: input.registered; program; 58d332f55df3ec8442b79ee6018d44f5e694f3e34d4c84ecde89d96bf16dd788
- Event 5: input.registered; program; 1a671893c82838626962987d7afeb55e1ffd66cfedc41f1e1515c6bb4194186f
- Event 6: input.registered; program; c9e62ff1a11c2ab646ad5edcccdcf5754a0e4cd5c9f58dcdf107e637d20082e4
- Event 7: goal.declared; ai_host; 1042c2680b3d59b02b87e47b1d5e11d46131bd2a335cc5da6061746071a7c6c8
- Event 8: pipeline.declared; ai_host; 493050f64a34c0f3b79944d66ba3d1fe8c2465a9161a69c110f3c23d92449562
- Event 9: declaration.recorded; ai_host; 30eec7f398bb01a79b462e9b1d2275a92c79273352afe7525e9a7253e1fb8461
- Event 10: declaration.recorded; ai_host; e4f46f0dd5d09a5ce353e278b4a3582d721cb4b01fef5c6874bca504e284be75
- Event 11: declaration.recorded; ai_host; fb6840fa18eb078bf0231a21719395a12b80d0f3e304c31dee0b7b230545613f
- Event 12: declaration.recorded; ai_host; 12dc30527bd8dbf0f95402f9da182b58c930873b89cd407c96ec83dd08d4b2c7
- Event 13: declaration.recorded; ai_host; 4da2f1538f4094bfe3fe7caff2a967a5a87364d718ecf66baa85a83512fc642f
- Event 14: declaration.recorded; ai_host; 6cc95b7971f27a25e2af662641e816bc3c6c6c6a2f5b217e2f8eadc8373d0e14
- Event 15: declaration.recorded; ai_host; 90d10c8cd20976fa6a6d4afa925193ce45666784cb7789b3f9ab552e8a627ed6
- Event 16: step.started; program; da6060abb67a40c89af1429fff4b454b545c425e03c38d9e7d22bce21e381f4e
- Event 17: step.completed; program; 9ead4068eff98267d464c2bdfd15ef231ee6722a15b559e02b587c6372a00a16
- Event 18: step.started; program; 741911da17c7859cd446001ccb90b40b38033b66531e0ca872f92884da52d1a6
- Event 19: step.completed; program; e86a089ff3335d08428f7fc70202f6fda4c12605166b562801f2727ac7c8f098
- Event 20: step.started; program; cdffd79c960cfda57042f05d10d98072df1f9a8bffdd4754141879a35ccf1655
- Event 21: step.completed; program; d1a63676b748707d965571ce5bc211601701f3e8bae49a4fb2138de2ae66f7f7
- Event 22: step.started; program; 561899910e920426b2c005238437c164a92c038fdc7f07eef2e9fdfc54e3e7ea
- Event 23: step.completed; program; c374faaa01d53a4a414b825548c78ca216670ba6fa5f33555a0ba39dfd416f2a
- Event 24: step.started; program; 268a1e8b646f9de0900ac8500ca554141d1b0c08d905c2bc275fa4d1397870dc
- Event 25: step.completed; program; 0c7b9d33bacb481e3a3cf9cee9765cc57e1ea0a119e63a2f07c01c3984616a67
- Event 26: step.started; program; c6df13c7a99fbea71ae77102db8714b6eb6fbe9598a364b3f2cd5fd809ad8b61
- Event 27: step.completed; program; 3a17e196a0f1b2c88d5e727d3271194f2c4b6370df302843dc26b9a562d4e7b6
- Event 28: step.started; program; d03d26a3f5bd4240d9b74816f5148d8bc8b1ed93bef71ecffebfd62aee85c45b
- Event 29: step.completed; program; 96baf93b3368c02246da6110d669304bdd50cf12b28926eb8fff0622ed0fdf29
- Event 30: run.completed; program; b08f5cfcaf524bf8876cacbe35320a5db1f62b91eef100d9f9cb3249fdc8ebfb
- Event 31: call.recorded; program; 1922241bd38239ffe3b54db611ce1a97f36acb0b565e6fb2b5817df93f4f710c
- Event 32: verdict.issued; program; 6be2c7e4f6769e302bdca98dfcb4e989d74947134a0b778f3d4aa77f4a5b72d8
- Event 33: verdict.issued; program; 4515f41d8feec3a7d2c71b03f561a552778045583db536807af8af49d310ef23
- Event 34: verdict.issued; program; 970cb688d3fa5e0ef6336285900ecd85dffbcc8e9a1fd2ed4b9b54ced6bafbec
- Event 35: verdict.issued; program; bf1c38966710c799d7fe67e07277f497210893172905da5f917859be1c50da21
- Event 36: verdict.issued; program; e46b2429fc0c088b67c5bf56bc89e6c7613cf44ed201057896412ed97559eba7
- Event 37: verdict.issued; program; f11a1db1f41a6ef042658daab94a6f0fd3ee1705a77f5e3e953f0d5e2a916422
- Event 38: verdict.issued; program; d378539c6e286548aa11a5ada5044067c28f7ce35287f469955b7eedaad301e3
- Event 39: verdict.issued; program; d01e256fc3168815e7b216f3334a661c2a75c5d7d9bff3051c5478d4ee9bb649
- Event 40: verdict.issued; program; e3c9b61757abbf218a22bc96374d5deb1c303e71e429c120996b7e2da7c3ee97
- Event 41: verdict.issued; program; bd574c08da785ea106947f53220babd4c39715f69df1f08d86d89b01a1774f05
- Event 42: verdict.issued; program; d6c53092257bf215d805f9c4702362fdce082c019c0c184ed75f9fe84a4a763b
- Event 43: verdict.issued; program; 25c3e51ea5d9b658f016c94b34410df9c9ddf5efa11fcc8d8ef1262e02d119cb
- Event 44: verdict.issued; program; 3dbeca56159c4b5037d10a0e919cbf214a5a28bc9b7cf7d9673953a9303f14ef
- Event 45: judge.finished; program; 9823ad327b98feaf886829abdac11935e5481bfd7e3d9dc85fc9e96187c393e3
- Event 46: call.recorded; program; 8d7d27bba3c3d81583901a8803f5af26a4b7336d42a53a9b92abadc861e20230
- Event 47: verdict.issued; program; 74d7cdfdf13d39cb583a2fc09c39390c0d555f38527801e75a0637ada6d0639d
- Event 48: verdict.issued; program; 552be5bb802e643a3d55e914d75a62da5885223e0c9bc658221b015ae7eb9fb8
- Event 49: verdict.issued; program; 82538deab3c38c519ad0176fcefc98533075101f355185b38f87b5ff280bdeef
- Event 50: verdict.issued; program; dd8c18a1a625ef8267a8212b1d18ecaf62654631e7349f91943d2f8dcf67868d
- Event 51: verdict.issued; program; 748b3a437543e48252a23382f22687aab5c35f101de759695edc1435ad69dfdc
- Event 52: verdict.issued; program; 0f0d13bc51336238e7a800519b5f92e692dd62d4fe8c71bc3fd8c6f8854ab1ae
- Event 53: verdict.issued; program; c9b763ddaa531202ca6821dbe1c0db99aa11bdd46e12939bf60d953bc1dcdfa3
- Event 54: verdict.issued; program; c29856a39feb8dd78412511575bc39837a334d1fc4db470f13d04fe52bcec5be
- Event 55: verdict.issued; program; 39f8b35049d027d2f534610076976cafd682e8354e5fdadfc568a0769e942372
- Event 56: verdict.issued; program; 2a22982fe1c9af1e7abe70ae538a4f468059478f1a2ed177e75ad604f48d6efd
- Event 57: verdict.issued; program; dfefbb4824066afa2dda2895372e520abb1530d2c8ba7180c8008687440c0c1a
- Event 58: verdict.issued; program; fab0bcbf9819798fb559b9b1937f2e4078ef39769a71cb93e60f75b27a2fca69
- Event 59: verdict.issued; program; cc38cf0f6b38ea10489adbb06036fe2086f9822fb08337c70219400bc119a8f6
- Event 60: judge.finished; program; e1b4ef0576f558cf2e4ed57b50e5e42e7a60ae14747a23a3d08e776b8e08c748

This record shows what ran and what was checked. It does not prove that a conclusion is true.
