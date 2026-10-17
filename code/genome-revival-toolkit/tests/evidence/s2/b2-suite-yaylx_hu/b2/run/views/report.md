# Run card

Through event 95

Journal head: 8e30264ba8c12f28684edd18d49de8c3476509ef0e1304544d746bf491f6baf7

## Data chain

Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.

- read_vector · format.read_genbank → read_vector.material[0] (structure)
- read_target · format.read_genbank → read_target.material[0] (structure)
- s2 · cut_plasmid.replace_spacer → s2.primers[0] (structure)
- s2 · cut_plasmid.replace_spacer → s2.route[0] (structure)
- s2 · cut_plasmid.replace_spacer → s2.product[0] (structure)
- s3 · cut_plasmid.inspect_guide → s3.guide[0] (structure)
- s4 · cut_plasmid.assess_selection → s4.selection[0] (structure)
- export · format.write_genbank → export.file[0] (structure)
- readback · format.read_genbank → readback.material[0] (structure)
- Host-reported goal and reasons → read_vector · format.read_genbank (dashed)
- Host-reported goal and reasons → read_target · format.read_genbank (dashed)
- Host-reported goal and reasons → s1 · cut_plasmid.inspect_guide (dashed)
- vector (user_file) → read_vector · format.read_genbank (structure)
- target (user_file) → read_target · format.read_genbank (structure)
- read_target.material[0] → s1 · cut_plasmid.inspect_guide (solid)
- read_vector.material[0] → s1 · cut_plasmid.inspect_guide (solid)
- read_target.material[0] → s2 · cut_plasmid.replace_spacer (solid)
- read_vector.material[0] → s2 · cut_plasmid.replace_spacer (solid)
- read_target.material[0] → s3 · cut_plasmid.inspect_guide (solid)
- s2.product[0] → s3 · cut_plasmid.inspect_guide (solid)
- s2.product[0] → s4 · cut_plasmid.assess_selection (solid)
- s2.product[0] → export · format.write_genbank (solid)
- export.file[0] → readback · format.read_genbank (solid)

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
- check.goal.components_present [user_goal]: PASS · Components checked against sequence on the explicit strand; labels do not establish presence or absence.
- check.goal.regions_unchanged [user_goal]: PASS · Explicit reference/target intervals compared; annotation inheritance is outside this check.
- check.goal.claim_reported [user_goal]: PASS · Claim reporting checked; its status need not assert success and its truth is not evaluated.
- cut_plasmid.check_direction [content_model]: PASS · Recomputed supplied-sequence direction.
- cut_plasmid.check_pam [content_model]: PASS · Recomputed supplied-sequence pam.
- cut_plasmid.check_vector_self_target [content_model]: PASS · Recomputed supplied-sequence vector self target.
- check.model_agreement [content_model]: PASS · Recorded and model products compared without annotations.
- check.format_roundtrip [file]: PASS · Exported material identities compared.

## Declared only

- Host-reported original request: Replace only the spacer; return complete primers and report selection status.
- plan_declared: Read the registered synthetic GenBank source.
- plan_declared: Read the registered synthetic GenBank source.
- plan_declared: Inspect the user-supplied spacer before any replacement.
- plan_declared: The initial spacer was shifted by one base; use target [13,33) followed by AGG.
- plan_declared: The initial spacer was shifted by one base; use target [13,33) followed by AGG.
- k1 [user_quoted]: Replace only the spacer
- k2 [user_quoted]: Replace only the spacer
- k3 [user_quoted]: report selection status
- host_expectation: check.goal.output_present [user_goal]: FAIL · Host expectation failed.
- tool_self_report: check.primer_quality [preparation_model]: PASS · Selected unique binding cores meet the explicit length and NN Tm windows.
- tool_self_report: check.primer_quality [preparation_model]: UNKNOWN · Explicit primer-quality limits are required.
- host_expectation: check.goal.output_present [user_goal]: PASS · Host expectation satisfied.

## Not done

- Cleavage activity
- Complete oligo contains a homopolymer run of at least six bases; retained as evidence, not a v1 failure.
- Constraint meaning beyond the explicit sequences, coordinates and report topic.
- DpnI template removal: PLANNED / NOT_PERFORMED
- Editing efficiency
- Experimental PCR, transformation or phenotype.
- Experimental performance, functional identity or truth of a reported claim.
- Genome-wide off-target safety
- Genome-wide safety or thermodynamic structure quality unless explicitly measured.
- Hairpins, dimers and purification were not assessed.
- KLD circularization: PLANNED / NOT_PERFORMED
- Marker expression, resistance, growth and plating: PLANNED / NOT_PERFORMED.
- No matching sequence reaction was recorded.
- Revisions recorded: 1
- Selection UNKNOWN: strain genotype was not provided.
- Selection mapping sources are migrated references; source verification and team review remain unperformed.
- Supplied scaffold anchor and directed boundary are declarations; promoter and full scaffold activity NOT_PERFORMED.
- Unsealed
- Wet-laboratory performance or biological function.
- Wet-laboratory success, biological function or reaction efficiency.
- check.annotation_integrity [content_model]: UNKNOWN · Required check could not be completed.
- check.assembly_product [preparation_model]: NOT_APPLICABLE · No matching sequence reaction was recorded.
- check.biological_sanity [content_model]: UNKNOWN · Required check could not be completed.
- check.cds_validity [content_model]: UNKNOWN · Required check could not be completed.
- check.order_table [content_model]: UNKNOWN · Required check could not be completed.
- check.primer_quality [preparation_model]: UNKNOWN · Explicit primer-quality limits are required.
- check.reaction_chain [content_model]: UNKNOWN · Required check could not be completed.
- gRNA activity: PLANNED / NOT_PERFORMED
- inverse PCR: PLANNED / NOT_PERFORMED
- reviewed 0 / stale 0 / none 1
- s1 failed: STEP_EXPECTATION_FAILED (retained in history).
- sequencing: PLANNED / NOT_PERFORMED
- transformation: PLANNED / NOT_PERFORMED

## Technical details

- Event 1: run.created; program; b59f1d82dfdf8de289cb556416292afd55b4e02528cb7833c2d2eb4737897058
- Event 2: input.registered; program; 776071800f82bcaf4e5995ccfcce24511d091dca8fe1ac3b80614eabd1f71756
- Event 3: input.registered; program; 233a0ff2cd87f9699d23abb1ccf7d0da082da4e5e98b5cd978ccd06697b1dfa7
- Event 4: goal.declared; ai_host; f4a35078abacffec97686e97efde360e1a66291fcb0628482de83507af12072d
- Event 5: pipeline.declared; ai_host; 8f6cbb913197928e8f4141871efe449b5ca64cbe3a8a280d6a512d49d70c1977
- Event 6: declaration.recorded; ai_host; 3a54678d1227371c58eface2af9fe53cfc3f3ccd57e5c4b5b05608d5223dc8d8
- Event 7: declaration.recorded; ai_host; d7e3c28b4dbe8c3f5ff9bb4d280ef27b020b2a84f7190cb5ede27b2a930591f1
- Event 8: declaration.recorded; ai_host; ed1b4c62504dd4a659e478b62172342ccc8954bffa9b8b3af6e0697058394b0b
- Event 9: step.started; program; 8c96aa758cc7c96b09ab3324ed5806ca036bfd0f79bcea17413989f1708fb70b
- Event 10: step.completed; program; ba2356c9c375e9c48d8a74c2da30fa1dde6c3e9fd724db74bbeb11dfb3a1edc8
- Event 11: step.started; program; 4c8c1f40991689ae1ad7ad88759aaa01d1d8204dcc15fa6f1530e2eff9f73c40
- Event 12: step.completed; program; 3e9b62c7d3134acc3d6788104a1c3e8746b27d18f98b6489f2c86c1ad1136bea
- Event 13: step.started; program; 7d59b386064d641625b7d57ce9706ff9c2170a349bfaebc407b924f5d1a9437f
- Event 14: verdict.issued; program; e27cb50fb8815c18bda1d72d39c1667cb023551b35430d9ee244537624be32b3
- Event 15: step.failed; program; 88bf6dd4e9d9e5bb5f79b7bdfcdc08f175ed16aa3f4ed54f0f22b4d8f28e2759
- Event 16: run.halted; program; c7633888e7d916a2180d9c8615d5003a20217790b189aa1d1717ddcf7ed7e360
- Event 17: declaration.recorded; ai_host; 73a3aa84b474ac341613329748a488cf09c39dd9f4bc17ed3a72dc08287280db
- Event 18: declaration.recorded; ai_host; 18fe553b01aa508b2bd7ba63a370bc97df5510d086155dacee592dd41dbcc537
- Event 19: pipeline.revised; ai_host; 17878392a6e5d64d7b3d73857802eda9b15db65fc0da1f7fc558c924087b6485
- Event 20: step.started; program; 29e1e2fc9580d73e3737b5f8a95bb2ba37f26b13fc07c49dc1018349457228ca
- Event 21: call.recorded; program; caeeb26d8cfc3debd7e9fa4383e56624e65bb5dee333f8c803f78c08a3bca423
- Event 22: call.recorded; program; 9351a186fa428488bc3fad535dca0e5feef12006a00b5dff83e548656fd5d87e
- Event 23: call.recorded; program; cce6422ef6d7ab652cc605e751c69acc889d47e5546390b2a13bd06340d08e71
- Event 24: call.recorded; program; b4ae31f06f6021acd74e4c2858b059ffbf1ef82b292abf45b0bc8182f911e792
- Event 25: call.recorded; program; 6846314bf42ae34e973cf0f67373f9d44c0d22237ee3614559ad8dda68d4e1fa
- Event 26: verdict.issued; program; 6353f8dd65d8f87a73b3c9a81336fc74b6f767fef979da24ce0602018129f00d
- Event 27: verdict.issued; program; eb914560353445b8392e63a6042c4fc3710379b0b7fe51bdae7a2e8467db8af7
- Event 28: step.completed; program; 828ae71da838d32ecd368d038be15bb36c7633933ae6593842a5219dfc6fa8ec
- Event 29: step.started; program; 821c4b5e38bb370bb8d5525d713cca8ce3c8e95b41345959a240521069cf2d4b
- Event 30: verdict.issued; program; 77914e39e43f6226760f985ef3f689463dbd5bbca1ade00535d45604570c54b1
- Event 31: step.completed; program; f975e31bf9096d2b80e243c453a74cfddc9c03ef338d77b8e2b19930339dcce1
- Event 32: step.started; program; 27782fc529341acc88dbfab1c26ce4c5c785331a8e27429f16eee6c597f79526
- Event 33: step.completed; program; 92a9744e8cd5a790ea8ddabd42ffe2d2c74b621abd916a738f165b6e41d6f57e
- Event 34: step.started; program; 44a112bcdfb85a80180f88f23a813e046309918f81f7adcf1a946183064a0084
- Event 35: step.completed; program; dc867ecb20f33ce07d5458b863448d9422b074209f4d447fccda9d3787a4ad6d
- Event 36: step.started; program; 15b70521d49f921c9a33c7f5be8d5624c93ce07547b273c054de29a2dfc89c64
- Event 37: step.completed; program; 894a26ad02f30e5caf77d4caa8118f0ee078b9d528696f7063e479fb96420230
- Event 38: run.completed; program; f8a3567d38022cbf426aab242a749d9248104ebd4ddab4cc9bf72eae7e03c245
- Event 39: call.recorded; program; 1a15ada7a82d00ac8860a2951b48c54de8b89036b412ca2f8627f18a8280b0f2
- Event 40: call.recorded; program; 8608ced065c5bd0d4dd2134dd4a0b76a514cad8005f1592dc9d2491769529e75
- Event 41: call.recorded; program; 55a1665584ba693decf611af0358f736a1efb3747345501fbadd58ae544d2e1d
- Event 42: verdict.issued; program; 1e4dcbfc8ffee64ce90324443bd7d98f2bc1ee7b59714b695e54819e9c6cf2f8
- Event 43: verdict.issued; program; ea1c0397f54475ada663021f2695af30ceae0a367c994f50d960c7a27722c184
- Event 44: verdict.issued; program; bb67a918aada5cb7e50e895b6b5127fb68fc34607f5ee4b52424337a59300a25
- Event 45: verdict.issued; program; 3eb91230330b8c4bf899dbd608459d7819a7422cc6d933543dd5ed436e0df04f
- Event 46: verdict.issued; program; 63042c9639918a57572c3ba6bc3530fa9cf0af5fb5c5f261f6c329e344ace1ca
- Event 47: verdict.issued; program; 024b04edbcbca514ee4c2110bf74a935c25eb63367715befc5c787b8226609e9
- Event 48: verdict.issued; program; aac35933f76811ac08d63d71291ba1d38af92e89dcd28aafa90b49a9d7a5f1a9
- Event 49: verdict.issued; program; 11d06f102b2a7c7747f6381b211854ae4b13c4e90b92a95acfb9d3391565682c
- Event 50: verdict.issued; program; 6db4e3e90d3010517882a9a0c5a32094232f600dcaa28e66e4420bd78a67343b
- Event 51: verdict.issued; program; 8fdba6c3c6382f2c0952fa3ab8470922183e1c79814b3e84b7384942093224cb
- Event 52: verdict.issued; program; 52b26ad4a8fad463b8e7f03cfa77984365487c26cc9e4e19736b06513864ce61
- Event 53: verdict.issued; program; b523cb17ed9fa7f6d3fcafd64e4e2da34779a5acc9cbc04b8ece733773c4a7d5
- Event 54: verdict.issued; program; 2aa93663b1f9990e73ffd3e9f171dd363a6f757095afc29f145876f31be6dcd1
- Event 55: verdict.issued; program; 006862769b8868826bf472316fdb513b4470507fbdbdf67175c1a4d2937f7742
- Event 56: verdict.issued; program; 36d9154c381f12ffaf0f8555ab98051ac7853810a80268389070832d8ce67afb
- Event 57: verdict.issued; program; 057c210bbc01ca378c189560a9bd19fc04de966e6238688c4a8f4b0aee15d751
- Event 58: verdict.issued; program; 4cfc1b82c5728b744729c69ea6147e9bbd4d5ad2a6afd70c76076aadcc921183
- Event 59: verdict.issued; program; 3e19eab3b8049a55455c02de2492d2e365417f9180b0ad181f26e4d600be37f1
- Event 60: verdict.issued; program; ad8428eddba17c9702c93e21970bd1040a7fdb4f3451c0b0685c6ee0b6c78769
- Event 61: verdict.issued; program; 612be92ae67f11e6c267cdd5c885cecc43947ac778470ab0fa95ce07d78ad70d
- Event 62: verdict.issued; program; 7b4f10fd04742b0e8f1d7afc909c2ce134b3c579b0acb0b53f42239e91efed9e
- Event 63: verdict.issued; program; fe35d401d7e1e474110462ffd44c710a182acb6e6ed3813b6c3578fcdad827f3
- Event 64: verdict.issued; program; 02a5805e97aa2bc3749891088dfaa2b6ee161d20618f2bd0533da754734530fc
- Event 65: verdict.issued; program; 9c01470ab7a72c039b685f9bf138520a342d0bf1d31ed1abedbf8efbcefa8794
- Event 66: judge.finished; program; 80ca6a8738672ffb0fc236156c5e4f855751dab49fc7a5d810a3fc0a25ea5542
- Event 67: call.recorded; program; d3b69233a9b44f17d247ca54808bbecd81e7fe83fa3f0a1b74f51a75f311c793
- Event 68: call.recorded; program; 07ccdc1b194ed4ce092da7f3890b4a87277fa12dea9d26bd833688b6a739dddd
- Event 69: call.recorded; program; 78f777583b4e7a32eef308b597f2ca73a5b05c3a57d06acef7e9d0896b86b0ed
- Event 70: verdict.issued; program; 7168dffb427103de3193a55b3128f085c9eee58cbef9e2d56ce736a22fb7ec01
- Event 71: verdict.issued; program; 302653f476f0fae4d89b69aeb43eb7532353314223b944c9ce79116c21683b7c
- Event 72: verdict.issued; program; 14044b89fd62c8f0593dcecd282d08e1829c6d44b50d2c654d1cd4f052d3b48c
- Event 73: verdict.issued; program; 51f6daa4d74cf87d1b9399532f53e2c332641f1262303866455369edc68809cf
- Event 74: verdict.issued; program; 85f7444fe364a943ff2e39ad0354fd4c2417974ab63476900f120419fa93c923
- Event 75: verdict.issued; program; b21a0dbeccc8ec071714d8d34e86759f3a54899d030c917f1f2f9861b518940d
- Event 76: verdict.issued; program; 9e1fe913f4e94ee7b5e28c47ea47b61161f25b9b342bba46cb1d7612adafed3b
- Event 77: verdict.issued; program; d6d154e6706019cd879ba7c4bf7c63b4ee59d0f7161e5e72dcb778360f12d290
- Event 78: verdict.issued; program; 5c3094e1be7101432966c0f80ae2ed3d1059cfe565f08341560d6aa10545bf69
- Event 79: verdict.issued; program; 1ded245405fef9dc66072a9bde907e103253d8a6b4dc71f86f14a8dd3bb31365
- Event 80: verdict.issued; program; 27cc554f9a7a7cb500002fe6e783f40e996d764ef57a3e164f637b2dcb8be432
- Event 81: verdict.issued; program; 93dc6f7d544d002c32f6c588573d8b1a59b6434c2c21345e8fb95c452f4cb0d7
- Event 82: verdict.issued; program; ee5630bc7f1061533b71a370dbddf5c0540debe025b7dbc92e5676ea16f217ad
- Event 83: verdict.issued; program; a2953ff232925db8d3b62b68e627c5192c20ec0ee3e36f77687766ca884268c1
- Event 84: verdict.issued; program; aa405047c3f7fa426142613bcc33d6b586f5550ade3d434c435faa0f2c65212d
- Event 85: verdict.issued; program; f210ff5da34974e5bb5ffbf95e78b3753099fbda709c6eae42f68b3a8a5500d7
- Event 86: verdict.issued; program; eac9be2c9fc0f3963b758381926f9a776a2f4cc57c1f54194c3c0d8d3ce93141
- Event 87: verdict.issued; program; ba3dee9b3b400ed6afd7fe5381da84aeea26fd9f5e5d9d99732bb4f4c18c0577
- Event 88: verdict.issued; program; aa9da5525b959e33b5de928c3bb111e708235028fcdca034f65490bb63de0ef2
- Event 89: verdict.issued; program; f11d8493aed5f9657e8ec4387c760c5c7681a9a54fe3302d272c97a3003d9d79
- Event 90: verdict.issued; program; cee813f7be00179b817bdae72fe65bda5f1313416fc5ac7c4ec55880b9d7d439
- Event 91: verdict.issued; program; b626f5b4c1f29f64afd1ceab9923f3c869d1e626318cd1a5ac665fd587607b78
- Event 92: verdict.issued; program; d57061c7c45c86082f826ce507237bbead84ae4b9b32b38bf30174f6369d66f0
- Event 93: verdict.issued; program; 6e5c856e95c5a03f71c4e0307ed8cc5455b5acd2e3165189d825695915deaa44
- Event 94: judge.finished; program; ecbf249014d59d0ca0ba1d718ed483fc12902fb4c38e0f661dc3662e5b8d0f80
- Event 95: seal.rejected; program; 8e30264ba8c12f28684edd18d49de8c3476509ef0e1304544d746bf491f6baf7

This record shows what ran and what was checked. It does not prove that a conclusion is true.
