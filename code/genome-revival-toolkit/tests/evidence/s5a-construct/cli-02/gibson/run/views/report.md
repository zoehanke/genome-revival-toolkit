# Run card

Through event 38

Journal head: cbc8cad0300a4f7e4126e06bc5a05346bb255f9fa8e6d16ee230afdf86e88092

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

- Event 1: run.created; program; 141b29b8554faebd73c63b74a37f84c1ddaf6fc746db42c71140621738f3408d
- Event 2: input.registered; program; 818cdb04d9696c9d6d2eacd877ab972324fd047f625272bb19811b7a1a128eee
- Event 3: input.registered; program; e29a5d6950b0ce1dd0aa5f1afc61eea387e0a92f22635944a7837c2e0c4ae009
- Event 4: goal.declared; ai_host; 14010c03f76b1b1fb307cdfcbef8f674ff22a4fb410901785efb2d5b90ab8445
- Event 5: pipeline.declared; ai_host; 3ff9a95e1ebb43d5512fa5aa968de638d190d61a6d1be9ac43e7423ef62be21a
- Event 6: declaration.recorded; ai_host; 896e3d9cd4a19518707748be3ffe35959360de1977eec2560805a956a846e391
- Event 7: declaration.recorded; ai_host; c81d1c8e9a00ac3b5e230e64bf30957f3150b293b0480a1488f90660fc67f16f
- Event 8: declaration.recorded; ai_host; cd2bd8fb3081e5db9b8f79795ef5925894b45dcbee945db41af800fac7a437f1
- Event 9: declaration.recorded; ai_host; d58b546afe83c3a9eabe353589cfb4788c9e5ab8a3110583d8f03df448500241
- Event 10: declaration.recorded; ai_host; b2e580aa366662468217f1d1f9cc62e76ee8d9472239658791d12d6ef6d4a137
- Event 11: declaration.recorded; ai_host; 6b631c678bd3ca4a8285e121719181882136f321b0cccfd8b4b30e4a2da2b755
- Event 12: declaration.recorded; ai_host; e3d9ca0c17b3a344443d1aea506f06d347cb7179356f0dbf0023045fb3d255ea
- Event 13: declaration.recorded; ai_host; 5fb382c08d52c93724f5b03be96ba90777b960423694425e00734340ecc6c58a
- Event 14: declaration.recorded; ai_host; 9c3b90f9ba815f6f2d4b2603861e4d6472ed1e4a6eda17c1441d8c92eeeef1da
- Event 15: step.started; program; 113addb8a6bd7cd5be9e72d0838e402315d1ab1bde8293bffbbd5f646b9f3d6e
- Event 16: step.completed; program; 82dfbd1c8896edc4ce81ad57ddd69a68bb99220e2469a321392f92b20579b853
- Event 17: step.started; program; 80206ab12ca33bf2bb2a4c7bf1363924bece4d9dcecbea72d0384e93fe4fa14b
- Event 18: step.completed; program; add555f9a39c9662ea7443160a3f8b6c4bb751dfc79cf4f932b40168d8b25365
- Event 19: step.started; program; 2f6090b34449d79d23e2d00788862a98c862a1a1b3d56ba9e0278083623e5f1b
- Event 20: step.completed; program; b6d293780be98f4f49bb5ec8e90229a2daa08be541572f6bf0be8d940b5ab3a5
- Event 21: step.started; program; 44226ef5f36973b10a29008b81bcbf98ca5ad79b52ac434129449724838cd594
- Event 22: call.recorded; program; 0104c18421387bf160397be9487591e720b6cad3cf932c083b3f618170b86d2f
- Event 23: call.recorded; program; 8825a9c5d213fa8e688a87a0985d35215ad7f43f8ad43855efbc374ca67f3960
- Event 24: call.recorded; program; 9b7098b13a4cc4844bb570b961dedd9c8d41085d2447621321a80aa6dd2122d9
- Event 25: call.recorded; program; 485f1d5a4bef2b6dc23833df79bfda48bc8d66acc645f5002fa486fba71faf99
- Event 26: call.recorded; program; eb9256d127783a2b50d04aa68b970709b8cce16256f4c478ee2ea81292147a3b
- Event 27: step.completed; program; bc6c65253a7e00c11f3f94e4793d63c8b21bf13eeaae5b4c71de36217b58ff9c
- Event 28: step.started; program; 90c68b1b6b716cf4dc1bbfcfea9b684e81b1bfa5df860036d957eb9844639bfb
- Event 29: step.completed; program; 448757d1c6769ac17128d6ae32eaa74dbfc7207868a2be794a40807f42cedb52
- Event 30: step.started; program; 225cae294e3454efa79cccb8d5b9d9a45780ababd51e984e1554c83eec3347e1
- Event 31: step.completed; program; 58ba3e79738e963f3bddda3e77e081c627dd7d4a24a2de9ff1cc0698ab38c768
- Event 32: step.started; program; 377437e1ec9faa65f4ee795f0160aa779cdfbb6f43ee6fdec6904e1403102133
- Event 33: step.completed; program; 5a1120549e468e3619e7fa18718438edb15938d46633b1a021fc6a53bac94d4a
- Event 34: step.started; program; da99db176736813038d03c1bee0e0ea3a6739860ea41f610130ce18e1197da06
- Event 35: step.completed; program; 66b31f6c934fad11b6dcadba00756cf8184df076066506f8f1f83f1c83048fe4
- Event 36: step.started; program; d9990a0c3e068b98ac33f8010d98ce6ab5035935e33ed1a4bdcde78c5a3c3a36
- Event 37: step.completed; program; 864a4310ef743440c5c81ccf48c6f44eeb98d13caa2d49df4086d8503bddae4f
- Event 38: run.completed; program; cbc8cad0300a4f7e4126e06bc5a05346bb255f9fa8e6d16ee230afdf86e88092

This record shows what ran and what was checked. It does not prove that a conclusion is true.
