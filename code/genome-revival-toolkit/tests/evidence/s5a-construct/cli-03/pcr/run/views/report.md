# Run card

Through event 38

Journal head: c3e2bd440db4860104864c3d0e448a2c1ce666d1d9b23174119de1aec4118bd7

## Data chain

Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.

- reference · format.read_fasta → reference.material[0] (structure)
- cargo · format.read_fasta → cargo.material[0] (structure)
- donor_template · format.read_fasta → donor_template.material[0] (structure)
- model · construct.model_donor → model.product[0] (structure)
- design · construct.design_donor → design.primers[0] (structure)
- design · construct.design_donor → design.route[0] (structure)
- design · construct.design_donor → design.edited[0] (structure)
- design · construct.design_donor → design.intermediates[0] (structure)
- design · construct.design_donor → design.oligos[0] (structure)
- design · construct.design_donor → design.oligos[1] (structure)
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
- Host-reported goal and reasons → donor_template · format.read_fasta (dashed)
- Host-reported goal and reasons → model · construct.model_donor (dashed)
- Host-reported goal and reasons → design · construct.design_donor (dashed)
- Host-reported goal and reasons → assay · construct.design_junction_assay (dashed)
- Host-reported goal and reasons → original_file · format.write_genbank (dashed)
- Host-reported goal and reasons → edited_file · format.write_genbank (dashed)
- Host-reported goal and reasons → donor_file · format.write_genbank (dashed)
- Host-reported goal and reasons → handoff · construct.export_handoff (dashed)
- input_reference (user_file) → reference · format.read_fasta (structure)
- input_cargo (user_file) → cargo · format.read_fasta (structure)
- input_donor_template (user_file) → donor_template · format.read_fasta (structure)
- cargo.material[0] → model · construct.model_donor (solid)
- reference.material[0] → model · construct.model_donor (solid)
- cargo.material[0] → design · construct.design_donor (solid)
- donor_template.material[0] → design · construct.design_donor (solid)
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
- plan_declared: Read the actual complete donor template; do not create it from the model.
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

- Event 1: run.created; program; d8f703d33a386d91fef1d46afc50316c51f457d23c202472b6777ecaac43ed1d
- Event 2: input.registered; program; bfdc4d9ac068e2897be4c5d8f60d3de9d569a721b6a1ec99fd1987869e485e26
- Event 3: input.registered; program; 854e27a5189453b3089701f40be2766d1b73dfc0d4d60b572bd51da0095e36d5
- Event 4: input.registered; program; 8388ed3814836a37cce6147090275427cdf70e232df61610ceea3b0e28895a04
- Event 5: goal.declared; ai_host; c8e9a91be83161ed173b196948be54528d5d74f4ac60d79da11e9dd536afb2c3
- Event 6: pipeline.declared; ai_host; 4d59e638c4684528c320e284e04d8b09ab4d60beef09b4fc5dbc18a2e1045263
- Event 7: declaration.recorded; ai_host; 7a0125fca2d238ea53b2cd10827bf161a3c4a6a4f83fcbba1043cca5e7769e85
- Event 8: declaration.recorded; ai_host; 55189778a8ac1d2cc5be999b6f94076b0361ad04347442e2e402d0df996b2208
- Event 9: declaration.recorded; ai_host; a47aa629d775702839c3db6740482ae4affbdff365995d947f27a74de9b3bf23
- Event 10: declaration.recorded; ai_host; cbfe63a28667c230aa2fe579ff7264286e83b2661d562f7d579c2a622d73fbaf
- Event 11: declaration.recorded; ai_host; 69163d3ec7d5587a52c17fd817ca593e2c494a9cca36ce8fa944adcbfd8ae92b
- Event 12: declaration.recorded; ai_host; 5b1ef90d24acfea52de096f0fbec9bb324249d0e3f464d390938ab2a6b30c37e
- Event 13: declaration.recorded; ai_host; b6ef1643210c8c44506bfa7ce20863eb48008a9e613ea509ead71767a8da7cd9
- Event 14: declaration.recorded; ai_host; 66bfa79a9cdc5e33efba516a9886409520645366eed764626d38461061b0866e
- Event 15: declaration.recorded; ai_host; 5f821b34cf979628053e5228faa103064b39cc6f833d8acf67da62ea0409405c
- Event 16: declaration.recorded; ai_host; 7b100767223673816b4603742ec478f99ecf357be4ebf6c486fae0f7643c4e59
- Event 17: step.started; program; ba814d49fc7d23e4d79fcbc5092d2573106d1544ef2eff1a2f24d36f56fc4e46
- Event 18: step.completed; program; 980c688542e583b2f135d91a0492a5886ab9c65693362b691c2985545bd572f5
- Event 19: step.started; program; ff87b34c02fdaaff32c7ccb32163cceeebfcee7edf1cd6812c41c9c05fc49770
- Event 20: step.completed; program; fe69a37018ea15c798f7ccb8c75de98a2189b684b57479e1e57a0f3b92f16e38
- Event 21: step.started; program; 81ccbe427e9cf8843fc2ef76451cad24f0d807d2995a1737b73244afafa4018c
- Event 22: step.completed; program; 89ab7db2af71b95899d4ba33f5500cd46286ae891e35b220a58348b1898b8ef3
- Event 23: step.started; program; f1f28a3219a34a6ca0c39cb97ecf7852ee2173ef865fa4515311755e3c006dc6
- Event 24: step.completed; program; 480977560b40558c3d6daa8f4659c7d802502350941a25b4b84ef6877e954ac6
- Event 25: step.started; program; 8ead6400ce1d878b34cb56a4d0c4d00294c9d4d5ecc3da3319483f024cefc8dd
- Event 26: call.recorded; program; 8d733d8a519f5bbadeba1394251a8caef32b6000eaec70177179888cdb56ca71
- Event 27: step.completed; program; aa55cd67f8d5fbc65303ce58186b303afa501187bac42458353aa15ec89d01f6
- Event 28: step.started; program; ba9708005375229c822a9b6cad1389998caf433c70518df969ef284c848593d8
- Event 29: step.completed; program; 1ffa73397585c8d81877e10da606400e9d2b9603f0cea48710f79d8352be0e17
- Event 30: step.started; program; e7e108872d09e7dabc044d41a859788abf9d439ddb6f4c02cea6b8d72d20693d
- Event 31: step.completed; program; b8ca8045c3be3625a35235216d2327b59b89867ae7b4eb762f40b73735eead1d
- Event 32: step.started; program; 4e7d15f372595e75d00db671e06d711258d6bc8d68a0a380fa0f51498c4a6591
- Event 33: step.completed; program; 46bb3d3ec6e2b1770084bc7e7d1f9d40c34a232eb385ee215c2cbba03c20592c
- Event 34: step.started; program; a52c5e561471618aa18a33ffe10486984b30c8ba97775b70675111452a55292d
- Event 35: step.completed; program; 067ba8c83fb1250912060d522f275bffec5a5034c3d80cb6fdda38688453708b
- Event 36: step.started; program; fd1c9071740d2e4367aba6ef0c32c32a0662ef9d8b7388e7d04ab66d3cd68d70
- Event 37: step.completed; program; c0af4e2e555686cf8d9f8a06789f2d65daf101c89d19c2e5afb25fd62857f34a
- Event 38: run.completed; program; c3e2bd440db4860104864c3d0e448a2c1ce666d1d9b23174119de1aec4118bd7

This record shows what ran and what was checked. It does not prove that a conclusion is true.
