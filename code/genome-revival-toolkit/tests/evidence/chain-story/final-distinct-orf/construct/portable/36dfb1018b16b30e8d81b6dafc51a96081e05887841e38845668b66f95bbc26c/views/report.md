# Run card

Through event 92

Journal head: 8f4f89e9834a92d8e5b895a5d36dc39e0f7d0539642d88303a2678bf697f49c7

## Data chain

Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.

- reference · format.read_fasta → reference.material[0] (structure)
- cargo · format.read_fasta → cargo.material[0] (structure)
- model · construct.model_donor → model.product[0] (structure)
- design · construct.design_donor → design.primers[0] (structure)
- design · construct.design_donor → design.route[0] (structure)
- design · construct.design_donor → design.edited[0] (structure)
- design · construct.design_donor → design.intermediates[0] (structure)
- design · construct.design_donor → design.intermediates[1] (structure)
- design · construct.design_donor → design.intermediates[2] (structure)
- design · construct.design_donor → design.intermediates[3] (structure)
- design · construct.design_donor → design.intermediates[4] (structure)
- design · construct.design_donor → design.oligos[0] (structure)
- design · construct.design_donor → design.oligos[1] (structure)
- design · construct.design_donor → design.oligos[2] (structure)
- design · construct.design_donor → design.oligos[3] (structure)
- design · construct.design_donor → design.oligos[4] (structure)
- design · construct.design_donor → design.oligos[5] (structure)
- design · construct.design_donor → design.product[0] (structure)
- assay · construct.design_junction_assay → assay.assay[0] (structure)
- assay · construct.design_junction_assay → assay.primers[0] (structure)
- original_file · format.write_genbank → original_file.file[0] (structure)
- edited_file · format.write_genbank → edited_file.file[0] (structure)
- donor_file · format.write_genbank → donor_file.file[0] (structure)
- handoff · construct.export_handoff → handoff.handoff_data[0] (structure)
- handoff · construct.export_handoff → handoff.handoff[0] (structure)
- Host-reported goal and reasons → reference · format.read_fasta (dashed)
- Host-reported goal and reasons → cargo · format.read_fasta (dashed)
- Host-reported goal and reasons → model · construct.model_donor (dashed)
- Host-reported goal and reasons → design · construct.design_donor (dashed)
- Host-reported goal and reasons → assay · construct.design_junction_assay (dashed)
- Host-reported goal and reasons → original_file · format.write_genbank (dashed)
- Host-reported goal and reasons → edited_file · format.write_genbank (dashed)
- Host-reported goal and reasons → donor_file · format.write_genbank (dashed)
- Host-reported goal and reasons → handoff · construct.export_handoff (dashed)
- input_reference (user_file) → reference · format.read_fasta (structure)
- input_cargo (user_file) → cargo · format.read_fasta (structure)
- cargo.material[0] → model · construct.model_donor (solid)
- reference.material[0] → model · construct.model_donor (solid)
- cargo.material[0] → design · construct.design_donor (solid)
- reference.material[0] → design · construct.design_donor (solid)
- design.product[0] → assay · construct.design_junction_assay (solid)
- design.edited[0] → assay · construct.design_junction_assay (solid)
- reference.material[0] → assay · construct.design_junction_assay (solid)
- reference.material[0] → original_file · format.write_genbank (solid)
- design.edited[0] → edited_file · format.write_genbank (solid)
- design.product[0] → donor_file · format.write_genbank (solid)
- assay.assay[0] → handoff · construct.export_handoff (solid)
- edited_file.file[0] → handoff · construct.export_handoff (solid)
- original_file.file[0] → handoff · construct.export_handoff (solid)

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
- check.reaction_chain [preparation_model]: PASS · Recorded sequence reactions recomputed before candidate comparison.
- check.primer_quality [preparation_model]: PASS · Marked preparation primers assessed against explicit criteria only.
- check.order_table [preparation_model]: PASS · Full planned-order sequences compared with actual recorded oligos.
- check.goal.exact_sequence [user_goal]: PASS · Complete uppercase sequences compared without rotation or reverse-complement equivalence.
- check.assembly_product [preparation_model]: PASS · Recorded sequence reactions recomputed before candidate comparison.
- construct.check_preparation [preparation_model]: PASS · Source-derived PCR and Gibson products compared.
- check.model_agreement [content_model]: PASS · Recorded and model products compared without annotations.
- construct.check_junction_assay [preparation_model]: PASS · Edited, original and residual donor backgrounds compared.
- check.format_roundtrip [file]: PASS · Exported material identities compared.
- check.pcr_product [preparation_model]: PASS · Recorded sequence reactions recomputed before candidate comparison.

## Declared only

- Host-reported original request: Synthetic computational chain; laboratory steps PLANNED / NOT_PERFORMED.
- plan_declared: Read the supplied synthetic linear reference.
- plan_declared: Read the actual selected cargo source.
- plan_declared: Compute the independent source-bound expectation before preparation.
- plan_declared: Prepare through actual template PCR and the requested assembly method.
- plan_declared: Test external junction primers on edited, original and residual donor DNA.
- plan_declared: Export the exact original assay background.
- plan_declared: Export the exact edited assay background.
- plan_declared: Export the actual PCR/assembly product for independent recomputation.
- plan_declared: Bind actual reference-file hashes and junction primers into the D11 file protocol.
- exact [host_derived]: constructed donor with two 50 bp arms

## Not done

- Authentic integration locus
- Biological correctness of feature names or strand/function claims.
- Complete-CDS start/stop validation of explicitly partial or pseudogene annotations.
- Constraint meaning beyond the explicit sequences, coordinates and report topic.
- DpnI removal, phosphorylation, ligation yield, transformation or biological function.
- Empirical thresholds not supplied by sourced rule data.
- Exact primer binding geometry is simulated; thermodynamic acceptance remains a separate obligation.
- Experimental function or correct transcription.
- Experimental performance or correctness of a scientific conclusion.
- Experimental performance, functional identity or truth of a reported claim.
- Experimental success or biological function.
- Experimental success, biological function or truth of a reported claim.
- Experimental viability, function, efficiency or host-specific performance.
- Functional revival
- Gene expression, protein activity, selectable phenotype or wet-laboratory function.
- Genome-wide safety or thermodynamic structure quality unless explicitly measured.
- Independence of the shared calculation implementation.
- Independence or correctness of the shared simulation algorithms.
- Laboratory reactions actually occurred.
- No CDS feature was present in recorded material outputs.
- PLANNED donor PCR/assembly; NOT_PERFORMED in the laboratory.
- PLANNED junction PCR; NOT_PERFORMED in the laboratory.
- Predictions cover only supplied references and residual donor DNA.
- Primers were ordered, synthesized, purified or delivered by a supplier.
- Programmed frameshifts, recoding or unannotated strain-specific genetic code differences.
- Revisions recorded: 0
- Successful laboratory donor preparation
- Thermal acceptance was not assessed: no temperature window and concentrations were supplied.
- Thermodynamic suitability, efficiency or actual laboratory PCR.
- This development-tree package is not release evidence.
- Transformation efficiency
- Unknown physical properties or ambiguous base identities.
- Wet-laboratory performance or biological function.
- Wet-laboratory success, biological function or reaction efficiency.
- check.cds_validity [content_model]: NOT_APPLICABLE · No CDS feature was present in recorded material outputs.
- reviewed 0 / stale 0 / none 5

## Technical details

- Event 1: run.created; program; 83e769af080b3ed81e75cdf38b926c61c87084fb473f1d30e44cb186680c6adc
- Event 2: input.registered; program; 90d528811b04cfa7f7835890394570a98219f414c9e1566422db081469fa40a9
- Event 3: input.registered; program; 26bed823fa4fcf660cb9d96b73c64b295756e33a2fbd3d5747c8b62be4d7dc0f
- Event 4: goal.declared; ai_host; d5384fd2ff2ecca1a1ca83a1cf762be8835004b04629296d80fbaa0ce44a55d4
- Event 5: pipeline.declared; ai_host; 7b15fc5202f43a6d46fe5ce2ab9f91dd30f7f6c03bc6ca2fe55c7adc1cff772c
- Event 6: declaration.recorded; ai_host; 204a12568c2caa701784d12b28e4ea8231bdc897d2ca7a45636b11bccee54efe
- Event 7: declaration.recorded; ai_host; 3f2333db8e40051758c37a771da1fa7113077ce3489b52017d5219c84b0231ad
- Event 8: declaration.recorded; ai_host; a8ae97f7d9da4a6d3f61c24d2a0ce56b358018006210872df63129dfa7ba4033
- Event 9: declaration.recorded; ai_host; f422d2a23c8a3f89ebdb5c41eb1418f09baef68de92c35963305677c0d5e6f38
- Event 10: declaration.recorded; ai_host; 6e24eaa7a6c0ce4faa4eba2ae5a4b90b3498af5bfa2c162f169c3eb012e3d142
- Event 11: declaration.recorded; ai_host; 75cb11d23a59c8ad4d436e44ad0b989d7cbc76a0c869106059c03d7c68014624
- Event 12: declaration.recorded; ai_host; 8ea4b157d31d0921835097a795fddc31f93ff9913174a9e6a185e7ccafb7b2ac
- Event 13: declaration.recorded; ai_host; 136d901566bb509c44aa161140c2d955ff29077341b9ddfbcb8e034d592c14aa
- Event 14: declaration.recorded; ai_host; c9a02ffca304113b6e60512e61d9fe554e78f3dd7bdecb7799d5af9b502c6b28
- Event 15: step.started; program; 7c45d25aed7f67c2f906079e03c5d12c661d323375a9f7d97ae34712108c31ab
- Event 16: step.completed; program; 89104ffc997d2bd9f09cb2f12601ccfb36ef24547d47d290665bbb8c52f8b1a7
- Event 17: step.started; program; ee08f7926a2165a8988af2046d167aaa86d711d246e9767ff485f871cce8022b
- Event 18: step.completed; program; d7d22d53a5c558d323437228e3ce7b3cff5027a5aeaaccc6815bd9acca94593e
- Event 19: step.started; program; 3dc5cc0e52ff776eb52f540d8d95face2263cf78af49c75fb898b4d847e0c57a
- Event 20: step.completed; program; 02e4259780e9432a7a9de510393c8222c281773dae0adda6f4630bf118152d65
- Event 21: step.started; program; fa2c1696b2b2814122614128ac2155294aa6e99980a09415ff732a6049c10d08
- Event 22: call.recorded; program; bd5ce4f7f3b9569ff896d27946f3bcea9ff228eea781985a93a4fd8250def839
- Event 23: call.recorded; program; 3abde427c5bf790e335701579668ede9f2c98779098bc072901e7a1f2c95cc88
- Event 24: call.recorded; program; e8da74335b9045cf8cf6604cc2428b3aba5c270d887341a4487bbeb563785036
- Event 25: call.recorded; program; f39025025a099cc9461310e16dba268746634dab0f771787ff69d40f378fbff7
- Event 26: call.recorded; program; 83f14520a2ba3a27f7e2d16b1509ed05313795b6950c5e0adf7ab387a9ebf733
- Event 27: step.completed; program; bc833a71e702c92e0a5aae1d21b655706dccfd784c440c9474e816173fb70fb3
- Event 28: step.started; program; 881078b06ddb7054a2ad40b0df150a3bf3dccea6d6d0b1891d11c2e7722cdbdc
- Event 29: step.completed; program; 00716be05d2b68ba1e1011b56d544fab95cc276389aafcc030433cb833e34977
- Event 30: step.started; program; 1db1b6d6306e9ac7eef6764a664dd65d289fbeb47c0442afdc982c59e39f7914
- Event 31: step.completed; program; 447707ebe679a9c0421013c4ac7a8ca0a12babdcdd6deb4fda843e63dfd42682
- Event 32: step.started; program; 8d794248863d40a535ceccd3aafdef692022740fa52a6d7e7d6a48403a6d2a0b
- Event 33: step.completed; program; f1facb219b64fd5c4ca08509e9b6a110026fcac2a8422c8f5eaa5235eb5f179a
- Event 34: step.started; program; 38fba8d323e674daa043f7c59308528201e8e59512d06b893b33973ef1c94a1f
- Event 35: step.completed; program; 3be2e2bb2230f1fb65ca9014ea165c624ae9e31ac79712a3b0a1e794f7255749
- Event 36: step.started; program; d81ff1d08264533145c4810ed88080129c0362b5b7a10e2afdbe9835fbc946ff
- Event 37: step.completed; program; 7c702ed9fb9fd09f8fa935822612086dd822189922123b65f950a67cfaddb8e6
- Event 38: run.completed; program; 2440a3f795e473fbdf40b10fd0d4786e1f166e7949b4d3f3b27266848b859d3d
- Event 39: call.recorded; program; 1597f1fa3be162566373381782682becd8293688ff6d066578215c3fbe32bb92
- Event 40: call.recorded; program; 195a000057254f50862037e8de5c039fa58196f94d50e7f1c5833cc88efdde07
- Event 41: call.recorded; program; 58f3e609065509c62f1d87d0b0513e33d8998f842e163293301d72f92c2dd9dc
- Event 42: call.recorded; program; 8e95a9c564f056c28d977880f2b6c819373660eb0196a6813b980dadce327911
- Event 43: verdict.issued; program; 234d0928341b348eb5753d156658d7da70de624b1b02e884285daeffa50ba87e
- Event 44: verdict.issued; program; 6f2888a2ad0a01a4570923bed3e8d1f78a58cd64ccff3b9f409a921a01c3a5ff
- Event 45: verdict.issued; program; db1b7fdd16210eb4a47ca18b50cac8e8f16fa78274da11fb146e89e646c963b8
- Event 46: verdict.issued; program; 5d09cb37339bf7add7ade1ea843e700aae1bdf50b26ccc8e38218aa0ad9f643c
- Event 47: verdict.issued; program; f253cb28a90815b8a2d613b9cdf9e14227e8e03b05ec57fe57826c3a895bf744
- Event 48: verdict.issued; program; 94bdcd92d9adf74a52c497149f486e76e180f1cfd63d9ec8960101bbae4a41db
- Event 49: verdict.issued; program; 12e8da88377a16724bdae27450a187688d802258aaf34b8bf78b16ed03cd8845
- Event 50: verdict.issued; program; 344bd8bd5ff7ec2ec665d684341ecda027d2160236b7a99fef9848f979926313
- Event 51: verdict.issued; program; 479c9ae2ac9ddbeeff709ade907752514d16e5391e547d8635225f64a23a7621
- Event 52: verdict.issued; program; d49acd07783b37b26d7b88df404920d19863dc565a852eaf9e1d131a8236cecd
- Event 53: verdict.issued; program; 024053ec2c2db09309cf53b2a07273fbe433347901970ab3799c55190ee7ab15
- Event 54: verdict.issued; program; 0f45dc9ec297300f52f0c2c87be34917cd4cc6d5f33dd95e9bffc141165de3e8
- Event 55: verdict.issued; program; ab4e5f6691a1b5fb8495a9906017cca021ed348f4ae756561515dda3d6bc7a38
- Event 56: verdict.issued; program; d4adfba391fe1d5e6bba92fc3bf0afcaa14d4bb7fbbe0c19b178d76edb399250
- Event 57: verdict.issued; program; c146ac57959d810bf147a19d0a37e1a90903d3972d72dbe676e2e1e8deba1a2d
- Event 58: verdict.issued; program; c856d830e6fb0424cacf28fe86f4953e43f34ead5be75e1e407572cd1929ff1e
- Event 59: verdict.issued; program; 7c32ad4c621c0c5483869d6b7d10c1c0c23820ae140d5defcefc23fb9325e1bf
- Event 60: verdict.issued; program; 58da0afd17c6d9847ac3f0e41a09445f3e9509552ee48f2b740a9a4114ec14ec
- Event 61: verdict.issued; program; 54de8abcd3b74808568e63ff3b6aaa207d0d91fd18903398587c10deef3797bc
- Event 62: verdict.issued; program; 7071a62452d0b41124b29e61a3d4b122d0301502c096442fe0b4b44a1512586e
- Event 63: verdict.issued; program; 69a79539bd4217c08214c07808236fd4f34ac9b9fb1e773cd779690736e01d57
- Event 64: verdict.issued; program; 8cc8ab94cfb2359243693c106bcbd341a84745e724c0a6f2a54f5b8ab5f29c04
- Event 65: judge.finished; program; 253ac439cc2f0b8c662d2a75d5355be64c64b89b9f4c00c3c3ba1ccf9459ba78
- Event 66: call.recorded; program; 39554703291792029cc79a0e56a14c19318837c79e7c539732e4f524a579b15c
- Event 67: call.recorded; program; eafc9e24e74891bbe434514cd85caf4881844599a00aa4800441c20cf36aa6ab
- Event 68: call.recorded; program; 844fb41a3e6c6a5a25f674bd076cc6cea333b12e0b00eacc48b601fbf5db2d15
- Event 69: call.recorded; program; 1364276af2ccde6dc3721057732dcfca49a4a28ce12f535932bbcad90a6ced6e
- Event 70: verdict.issued; program; b92aa8d8c12b1d5d982c2969863c2821503ed7a87a9cdfe9fc29496c019b4ed7
- Event 71: verdict.issued; program; c38b374f4b67ddc334e6f00cfe7a318128e625d4f503c0bc8250fe85b0781cb4
- Event 72: verdict.issued; program; 0ed2dc435c8015fe732dd032450d4029576460cfdfc665b0519e02472d4d81d0
- Event 73: verdict.issued; program; 2407cf5bf8951468b5bef9532cfabb7c1a050710e88769e8c7c0954479c0aba6
- Event 74: verdict.issued; program; e0058a5495becffa96ee8708166e7d74f04230aab45b26910cd7f460bee0c734
- Event 75: verdict.issued; program; 2604eac37d8c1c6916cf4d7ae76020c0a05365f6f6cf5d248932c06559ce15eb
- Event 76: verdict.issued; program; 8325f3193a75bcd5b866e2d627a8d0b264547363b91c2c3118a31cd9f005ddae
- Event 77: verdict.issued; program; e98b3a5c3df86782308b7014f26c62dbd0a4780028a4873a892fea99a45668c0
- Event 78: verdict.issued; program; fb11de59f6f43fca2998df8666f3f12e114342eda6e5262b8b206911eda048be
- Event 79: verdict.issued; program; c7f479f8d9d251253aca6adb9b27eeced290b3eda160a94c6cdfbb5cc206bcdd
- Event 80: verdict.issued; program; 9957e0c9a5d6b3b103e3c691f7289890f319f8fb4ac667fc72c3c3d6e387fa87
- Event 81: verdict.issued; program; 10a7bfc535d00ceabee1457fcbb784b0add5dae8a5dc7941c29580dfc3ea796e
- Event 82: verdict.issued; program; 7b59c8c5fed5617cc3233dfa7185ae07412b6c6946e6f617517c171efefd21f3
- Event 83: verdict.issued; program; fc01ab0a454e9524f725c4aca3d8a03c1b39d657fe55b380d415808616c11ad6
- Event 84: verdict.issued; program; 59257ad8cc6b6a04ce85501b9829da3bb749580b5ab49d08792f114ebdf9ef53
- Event 85: verdict.issued; program; d1395f7047299e3f3dace19354f0d348d5526a265aa28e2c9499f30733e66693
- Event 86: verdict.issued; program; e8bcf08e79af1e69897ebee4dbef5f7951857a92df7fb7b6dbfbb69c55956569
- Event 87: verdict.issued; program; 9c9cd8e5a5cdbc6420097813e2e0476d15849ea4ee174f555d64acb6aaa62324
- Event 88: verdict.issued; program; 861b56ed5aafb590ec214495e71abf564c5349e1a06d9e46799f7211f29621fa
- Event 89: verdict.issued; program; 83ad325b413b09cb43d0e523637213763331fdd3def164f696d43906bac6ca63
- Event 90: verdict.issued; program; aef67b5fb0f852b477d42515806d5187bdf11fb3e4ed2a829c2a1ac578cb6831
- Event 91: verdict.issued; program; a971233617c1ed4c6ca0048a2bde4aeb1e8bf30361a55930c2bbf99e93a0f0fa
- Event 92: judge.finished; program; 8f4f89e9834a92d8e5b895a5d36dc39e0f7d0539642d88303a2678bf697f49c7

This record shows what ran and what was checked. It does not prove that a conclusion is true.
