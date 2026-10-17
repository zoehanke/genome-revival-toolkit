# Run card

Through event 34

Journal head: fc14545d1f746e2905774a0c26d29a8988f39e7aa0804e1288057c2910e41217

## Data chain

Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.

- s1 · evidence.parse_observations → s1.document[0] (structure)
- s2 · evidence.assess_observations → s2.assessment[0] (structure)
- Host-reported goal and reasons → s1 · evidence.parse_observations (dashed)
- Host-reported goal and reasons → s2 · evidence.assess_observations (dashed)
- observations (user_file) → s1 · evidence.parse_observations (structure)
- predictions (user_file) → s1 · evidence.parse_observations (structure)
- s1.document[0] → s2 · evidence.assess_observations (solid)

## Checked by the program

- Pipeline admitted after static validation.
- check.readback [file]: PASS · Exported content comparison.
- check.manifest [file]: PASS · File list and byte hashes checked.
- check.journal_chain [file]: PASS · Recorded event chain checked.
- check.store_hashes [file]: PASS · Stored content identities checked.
- check.inputs_unchanged [file]: PASS · Registered input copies checked.
- check.goal.nonempty [user_goal]: PASS · Active goal constraints counted.
- check.goal.target_role_met [user_goal]: PASS · Producer roles compared with target roles.
- check.goal.output_present [user_goal]: PASS · Bound output presence checked.
- evidence.check_record_consistency [content_model]: PASS · Recorded observations, sourced conclusion rules and exported content compared.

## Declared only

- Host-reported original request: Synthetic computational chain; laboratory steps PLANNED / NOT_PERFORMED.
- plan_declared: Parse submitted observation records and retain missingness and source identity.
- plan_declared: Apply sourced evidence boundaries and report tests that were not performed.
- present [host_derived]: report result

## Not done

- Authenticity of submitted observations (观察本身真实).
- Biological replication and comparability of reported conditions were not established.
- Experimental performance or correctness of a scientific conclusion.
- Experimental success (实验已成功).
- Functional revival (功能已复活).
- Functional validation: NOT_PERFORMED; functional observations were not supplied.
- Observation authenticity and experimental conditions were not independently measured.
- Revisions recorded: 0
- Rules are AI drafted and have no human review; source verification remains unverified.
- This development-tree package is not release evidence.
- Wet-laboratory performance or biological function.
- Whole-genome origin, elimination and causal dependencies were not tested.
- reviewed 0 / stale 0 / none 5

## Technical details

- Event 1: run.created; program; d985434821845a09a26fa0fe66a89aca1aa48580859456bf9ca785cfb699a201
- Event 2: input.registered; program; a283bb764bc65f96b7f05d0929db32c03a65328890e166ea7883b0c60825fefa
- Event 3: input.registered; program; 723a9a6b0f9e4521a0ade86e6ac415d6c5c12b13ff2e5dc7095fb2efa7d4bdba
- Event 4: goal.declared; ai_host; 4d27efc10bb4ef24f618b0318ee131c0b111d50b658928fd6c9619cb81b3f602
- Event 5: pipeline.declared; ai_host; 0c301be8b17aba9e9b1150170de0bd1dc99c272d0220f5f672a072db6c0cb3f8
- Event 6: declaration.recorded; ai_host; 47ff3e385bade2f3788c95752612d78949ef1e76d8d1ec61ea82065552d1f0a6
- Event 7: declaration.recorded; ai_host; 999b06d4d21a8be6c1532854415855a59f91f72ad58230523728aaa78deb5f35
- Event 8: step.started; program; b304e44449c03d7e0ac49c658683ac2a54c6d835c884169064832bede545ea23
- Event 9: step.completed; program; 354cf996b91ed222025ff2ad9dbef855e10816ed131758872e54bb23b10d09a2
- Event 10: step.started; program; 98beac376aab41a398e802e24d71285a4571fc6520479317399759216146abbf
- Event 11: step.completed; program; 3e1306417cfb84480967f0bef1283601858c5639f57d62679338ac19cd7452ba
- Event 12: run.completed; program; b85477866afa06a5d544be6d88ff4002e653f6402f4d00a5ffcad3dc7b86e0e2
- Event 13: call.recorded; program; 5139f67598d9151c1f8b3819c80be751749780cccd1d1b5f28a746fd20535eca
- Event 14: verdict.issued; program; 51741c8af746ce90aa61eeb456907f2300a5dabb58d0aeac8d8d716bfce82dec
- Event 15: verdict.issued; program; b4eebdcb40f230f2469d1c305d664931ce90716aea529342a26a91479b09a04e
- Event 16: verdict.issued; program; b1fa3f1e754ba0fa6b82a1d2356338abd018a610f3c9a53f02ec335b9f710bba
- Event 17: verdict.issued; program; 5b6dae8c7a3a163f9c63f587c886671cbd75e20e359a6ad21d28a4685ac49538
- Event 18: verdict.issued; program; 949537ba8d987297e9517f6f555683a6c9d23466619aeba56d4b19be7801cbef
- Event 19: verdict.issued; program; a1135a759251fd1b61adeb8f22d75bd99a2568fb79548d4beab6d75af905f902
- Event 20: verdict.issued; program; 058e2e808e6bfeccc96e81b18a8b2acff04f58930f0d2660bc0f8d7cce0c94bc
- Event 21: verdict.issued; program; 6d722ee29fc3e1a0ef9bfcfa9481a46d5b22936315915762f512105f6697e3b1
- Event 22: verdict.issued; program; b026a319308d848f15063093d1b825f0a6b8ecdd626d54b9096f949e04ca28f6
- Event 23: judge.finished; program; b566cd3ae0fb1aaf99b7e750a412fd0488cd0d5465a2d5186de62668c0d39748
- Event 24: call.recorded; program; 07b338177dd4f558dbc07a8f8e2a963c66271bce1ca8658b91d153c710c7a38d
- Event 25: verdict.issued; program; e166b20bb3bd47b5ba4775c3842a251424b74a5ddd5d19c9c9e0f9027a4adb8a
- Event 26: verdict.issued; program; a8729b7371801ef35ad7229e5af3dc8b3683f264f473caa1f66f462d850810cc
- Event 27: verdict.issued; program; 4fb42475f7f46653b8624c75f7b10713e401d5f72eefd7299d8bcb7513fd8ff6
- Event 28: verdict.issued; program; 8c4e884a5db3dd38273d22e8420343c43028741d2f54b6c99d2d90a9b8924cba
- Event 29: verdict.issued; program; 2eaeff11bb6f6e59bafcbaeb4f86da9a3939ffabc0a1dbd3bf8e9eb58c5f2049
- Event 30: verdict.issued; program; a157bc0f64486f7917ef43c4fc60896705703e37a05b078d263c219f7cdb7e2d
- Event 31: verdict.issued; program; ace54a11c47950031935dad02cdd9f0887be0b802eeca29ee15405e3e97d81b0
- Event 32: verdict.issued; program; 2081e81a7018913d755a4ada0d4c140b068173d347f96655bf1ecbfbc51412dd
- Event 33: verdict.issued; program; 71549a80ad91df80ee2935032932dc0ff44eb762a8f1965a476f8866f449df1d
- Event 34: judge.finished; program; fc14545d1f746e2905774a0c26d29a8988f39e7aa0804e1288057c2910e41217

This record shows what ran and what was checked. It does not prove that a conclusion is true.
