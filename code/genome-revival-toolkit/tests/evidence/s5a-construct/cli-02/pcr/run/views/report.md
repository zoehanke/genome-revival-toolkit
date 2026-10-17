# Run card

Through event 38

Journal head: 4ec232ef1261f62737b1809d0181c0c1edf815e4238114535322c931fb5b5901

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

- Event 1: run.created; program; a0c75b9a8cf549cc7cb8d19a26858b35713674d9d7466acbe95d55eb25d45187
- Event 2: input.registered; program; 480527e789415ad6f45218ca7624369183a1e431f9baa16e3da851cb1cf95b67
- Event 3: input.registered; program; 1b8b4d9b95ebacf7a3972046209740bf356ecc31db347bafb1947e4ef225451d
- Event 4: input.registered; program; 8447d07e2a709a2b0341dbd3946fb0b1401bea7f60385004dca473f5ec25593d
- Event 5: goal.declared; ai_host; 25aed409092d5f6b4a564dba2d25b32b4abae0ec3b694ab58648e356a757ab0a
- Event 6: pipeline.declared; ai_host; 22e3c791057db26914ca909d3efcfe4daf844d67ba3838de2753437fd1378ac4
- Event 7: declaration.recorded; ai_host; 49dcf13f80243785e1e2f96e769fdc0f51df96baf658432b906b3ff97dc1d3a4
- Event 8: declaration.recorded; ai_host; 6689d3f778c50dfefb19e04d99e4ab558239318a4c72af8b4e03b425eb624419
- Event 9: declaration.recorded; ai_host; 954e48332d8c14b12f4243bc0a7ff85379351dc3aca5d98635ddbcfda9692b52
- Event 10: declaration.recorded; ai_host; 78e7bf86ade69d76a3be64e5ff6a45f390c458b95f7813a0abdc0c7884a804d8
- Event 11: declaration.recorded; ai_host; f405291fe0bd9c1f9ed247b37fa36759ef7146754513216d483685a16818b1c9
- Event 12: declaration.recorded; ai_host; 7130b49785dc208bae9b4dd62cb94f7846be0b1f4ea983a97d0575cd527a27c7
- Event 13: declaration.recorded; ai_host; d1d44b7c336e0332cb0bff5782689ed6e3049958a682c6abcef6222a02fc1c39
- Event 14: declaration.recorded; ai_host; 743047ce8b4e033673cb974c499b187e0f3ef38dfcb9ad71b12f0495f311950b
- Event 15: declaration.recorded; ai_host; 3bf27d13690cd44535a0bf5f7d658e4d357642b9f7cbd7f533bfd8225599efb4
- Event 16: declaration.recorded; ai_host; 911eb6f57682e1733164ddc91eb9a1d6496d6d45e3e7b092872a16bc55d4e6e2
- Event 17: step.started; program; 206038d680ad5f618d9171266f1dd8093355563e626d517dd28c83ad21188217
- Event 18: step.completed; program; c98a2a9c45a0b6db0d255cec13fd52d29be1b89f211fb222afaab9e9b4de389a
- Event 19: step.started; program; 4cc88b5f7c51db8d7e7164f232a5acd50b4ffbba124ea3209c7b3c1b7e8a5bdd
- Event 20: step.completed; program; 7e4b87c5053c60e20561eb7db52d3d2a20ce534a9a5d84e3b094713bef64a6e3
- Event 21: step.started; program; c71271d04dcf9228eed347a325890364b087ae928999fb3b3026fbaaed8e0562
- Event 22: step.completed; program; 053c396899f735e36cc12be7663715dcb9e0223ec264c8874bcfb1350f59325d
- Event 23: step.started; program; e4204bd8b74d6d3d280c5fc5d9ba61aded19ef9fa7c9c5f5ee9393ddfeff52c8
- Event 24: step.completed; program; 51cc723a5e9e7ac25957600f8cba49adf82dd3a9f435a52b4195b505c1e6eefa
- Event 25: step.started; program; c93eb7fb5231412c5c0e51bc0a09b68fe1f181ad069120f6e5cee04bd099a4b4
- Event 26: call.recorded; program; ee2547e149f46134de6a441140a854301e1ed8c60b1983ac44725e864c74badb
- Event 27: step.completed; program; a296b7c67a9a929cb1f256f8f72a36674fb1aa610f42cce700c4882452c3a764
- Event 28: step.started; program; d3d899e39b8e2920dcab29a83d207cac21b428356102f5f26677f296cba57f17
- Event 29: step.completed; program; 10e39b48622b5a9c96ccc2a2f703cf42f438fa899396201409ed40f35db39b56
- Event 30: step.started; program; c8f5801d4848fcec62eea22384aae3e3541998b520811876ce59891f76b0be30
- Event 31: step.completed; program; e0607e20a6d9d8bf08b528a757e9cbcd42d83d7e3212364ba3b652f55108ccb0
- Event 32: step.started; program; 72aebfe00b52810505a95d1e481b762f67502c74fd3fa227d52db9a642b60675
- Event 33: step.completed; program; ae622b0f44a783bd75b48b01926ab6ee01a4536a9a1391d8883702c5ccffc236
- Event 34: step.started; program; 160afd746392cae6bddc59a098a85e31bce84e55984648b20aac4cb0bb96a40c
- Event 35: step.completed; program; 9591056bbdfc7f3158fa36c10f0f90165cd04a40a38596cc59214f0eb6f5f471
- Event 36: step.started; program; f5b29bbee88454a62e5cf16fcbd0b2f9889edf853551ba994a3a547eff6b5798
- Event 37: step.completed; program; 77db047207677c04a848fac7d5f84106356ccee2b1d6bca02f111f356436edfb
- Event 38: run.completed; program; 4ec232ef1261f62737b1809d0181c0c1edf815e4238114535322c931fb5b5901

This record shows what ran and what was checked. It does not prove that a conclusion is true.
