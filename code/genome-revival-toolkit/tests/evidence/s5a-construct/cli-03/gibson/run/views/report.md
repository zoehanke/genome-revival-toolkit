# Run card

Through event 38

Journal head: 29d4d1e50359ad596f59463b0ab9da8e5fe637f0d2cd042ccddfbbc642ed8105

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

## Declared only

- Host-reported original request: Replace the selected gene with the supplied cassette and retain both 50 bp homology arms.
- plan_declared: Read the supplied synthetic linear reference.
- plan_declared: Read the actual selected cargo source.
- plan_declared: Compute the independent source-bound expectation before preparation.
- plan_declared: Prepare through actual template PCR and the requested assembly method.
- plan_declared: Test external junction primers on edited, original and residual donor DNA.
- plan_declared: Export the exact original assay background.
- plan_declared: Export the exact edited assay background.
- plan_declared: Export the actual PCR/assembly product for independent recomputation.
- plan_declared: Bind actual reference-file hashes and junction primers into the D11 file protocol.
- exact [host_derived]: 

## Not done

- Authentic integration locus
- Exact primer binding geometry is simulated; thermodynamic acceptance remains a separate obligation.
- Functional revival
- Genome-wide safety or thermodynamic structure quality unless explicitly measured.
- PLANNED donor PCR/assembly; NOT_PERFORMED in the laboratory.
- PLANNED junction PCR; NOT_PERFORMED in the laboratory.
- Predictions cover only supplied references and residual donor DNA.
- Revisions recorded: 0
- Successful laboratory donor preparation
- Transformation efficiency
- Unsealed
- Wet-laboratory success, biological function or reaction efficiency.
- reviewed 0 / stale 0 / none 0

## Technical details

- Event 1: run.created; program; e1d902d9e68f77b870e5d6e8d60cad62daef8ba065e75c5edc3c977dba5732c4
- Event 2: input.registered; program; f621d6cc8bb0f12018eafc6f0b28d8101a6ebcc07a64c292e4c7028b8734911b
- Event 3: input.registered; program; 4cff82575aa2b86f670d7f73b181a76d049907ee7297df19f1329ffa3fdcea4b
- Event 4: goal.declared; ai_host; 09b563600e1e6e02bc39cb3525d64bda0318e107dd177f8ab93d574b9e9fe581
- Event 5: pipeline.declared; ai_host; f12df9c6249d06c5ea844934d1b08c2d65925d6bc2c605406eb97b9291eaeef4
- Event 6: declaration.recorded; ai_host; e420676d8d90babed068b8075f5a34dbbe5e800a9bf776837ede75955529bdc9
- Event 7: declaration.recorded; ai_host; c76c1fc0a3387f81747ec09a60b0a54b6a7ffef013615fe0df54b6eb5ca2bf80
- Event 8: declaration.recorded; ai_host; 5a6d20986a65df0a7c0e37950379f669d6c201fd8ddb02b711b4f1235103ad49
- Event 9: declaration.recorded; ai_host; 6a91854199ecca13b8121bbed72c6172544f551df5588fdf74dec78e4287e8f5
- Event 10: declaration.recorded; ai_host; 9ae05f915dd14653035089af6d302541e86d68dc2ebec58fd6a43ca60d99e01b
- Event 11: declaration.recorded; ai_host; ac08499dd38c4dafb9d9b954cb5b019b5ab37376a83c871f89739a1378435c6b
- Event 12: declaration.recorded; ai_host; 3c2fbec9f74819d4cd5bf40cbc37117a7f692b92124097e2c1ea1c012f342289
- Event 13: declaration.recorded; ai_host; 998720eea14e6743339742083165ed9dc1ac42cdf174c4d169a2cf80c7b0c71f
- Event 14: declaration.recorded; ai_host; 2e34b36f6eed6b5454190601afd97d595c8be15c8491eebadad4fff49c354929
- Event 15: step.started; program; cea1f2097574baf4fd4644276b4c1f1c6448d693336d5606a5a1827ecabd3e50
- Event 16: step.completed; program; c56cb127ba38c6c2b791b66e9b6585f26ee8efa04472da5e481b0286ab42af03
- Event 17: step.started; program; bc47b12e4b7f7e0d6e1222803df73797fdc5ebd50724fd1a70f0c0f7b630773d
- Event 18: step.completed; program; 799da77b23d4cd599361acbe8907437f098a7e949e81316164c2d79f4ab9f1cb
- Event 19: step.started; program; a2b103057bdc7126dd6b5e0fe41029247f25a6c6cc9ba17fadd7f53e4e58974a
- Event 20: step.completed; program; f8deacae6c628648c1a0d287ea79fc589567d6706c174f6bb48edcb78ae364da
- Event 21: step.started; program; 1fa42ff3f20c55e14a6aeadb17ac9bf3707d0972c7d45432e283989c70380fa3
- Event 22: call.recorded; program; 410017bde4b9e4dd55ede59abe7ad6491cde4940fe3091b0a89544bc7482de52
- Event 23: call.recorded; program; cf74b9578dfc0a0864e3d87c94b0b7eed76f2556a96168b07d562c08de3537bd
- Event 24: call.recorded; program; f019e46d72ef07a5096b3e43ed97786004fe5d52946bf5f571b92cd02414d200
- Event 25: call.recorded; program; cabeab478219ab8b6addc4c7decc60a76d1a94d75faef54ad59e5fe866b61857
- Event 26: call.recorded; program; 61658ff061b2b4980ccf7552987e78a4522c63da9cb21f0b2b71cea64a612048
- Event 27: step.completed; program; 03c0d1ff21bd9b9abef71b44b8ddfed796f7922d1727cfa194f51caa735e67d9
- Event 28: step.started; program; 38041b4e90f25f2643d30ff764f486a4dfe4836611553f19022ae69d0f60cb7a
- Event 29: step.completed; program; 24a6ea2b471d2a966c9b0ac503c1ee92ad0a4698d51b0915b185d8ce6f16916f
- Event 30: step.started; program; f5d36ebc0b3e157a50a4fcf906cf76033ff98d3ffd80e31db7bb1e6550eebc8c
- Event 31: step.completed; program; 116926f994b9a4cdda5e0758a484eb7d90a5bf7f33ee7239f9de8428bc37c1a9
- Event 32: step.started; program; a2a2b2f9caf27f056c368206759e6219e5f7a284c60f1ac4ef99d52ca2a9947f
- Event 33: step.completed; program; edfc36fecc9488c2bc761a61b8c60fcaf1ca3b6926a4d354703c498eecd9f338
- Event 34: step.started; program; bae35fbb859659060a691985dc550e46d943c7a7289932ed172b5006c68ed103
- Event 35: step.completed; program; 2828cadfbf57a32b7966abc0c80bd18bcc30851a70b3c72487a4890631c42462
- Event 36: step.started; program; a58577da7ae2203864409f9beb1cba8a8f8784a396775992e03eba28d3df9907
- Event 37: step.completed; program; 91db483cb042d2e95a9a362e90e09d425aa701a03dfa933cdc5b6822efdf3369
- Event 38: run.completed; program; 29d4d1e50359ad596f59463b0ab9da8e5fe637f0d2cd042ccddfbbc642ed8105

This record shows what ran and what was checked. It does not prove that a conclusion is true.
