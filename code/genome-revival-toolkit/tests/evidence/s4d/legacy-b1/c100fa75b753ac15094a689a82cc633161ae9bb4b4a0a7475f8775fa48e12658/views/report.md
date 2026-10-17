# Run card

Through event 34

Journal head: 12b220014a0516f5e657ebaf731e04feb96b8eb0a23bed5967e85119803f057e

## Data chain

Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.

- reverse · seq.reverse_complement → reverse.result[0] (structure)
- Host-reported goal and reasons → reverse · seq.reverse_complement (dashed)

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
- check.replay [content_model]: PASS · Deterministic output identities compared.
- check.lineage [content_model]: PASS · Input bindings and identities compared.
- check.dna_value_valid [content_model]: PASS · DNA-valued document alphabet checked.

## Declared only

- Host-reported original request: Report the reverse complement of [sequence omitted].
- plan_declared: Reverse and complement a synthetic eight-base literal.
- c1 [user_quoted]: Report the reverse complement
- host_expectation: check.goal.output_present [user_goal]: PASS · Host expectation satisfied.

## Not done

- Computed sequence only; no physical molecule was prepared.
- Revisions recorded: 0
- This development-tree package is not release evidence.
- Wet-laboratory performance or biological function.
- reviewed 0 / stale 0 / none 0

## Technical details

- Event 1: run.created; program; 27526ee37f02dc7cb8efd121083fc48e294a1a64a455905ce2e3e5b49764dce8
- Event 2: goal.declared; ai_host; 92475a54ac6e1bb023c1b83d213f3316be9d14fea49d8f2a6cd076ef7a2051a8
- Event 3: pipeline.declared; ai_host; 027c5b28ee009f54415ba63bcb147926945946a29b8af6d18eba06901087fb57
- Event 4: declaration.recorded; ai_host; c038e48e244f2d66cd540f79953a1eec2c316df3876e9a3efed88e6a0751f179
- Event 5: step.started; program; a8da3cd43c90b74204801aa14c6d1d34e39e23700695f27a3409998ee0c9c29f
- Event 6: verdict.issued; program; 9913010b7164c0837c9fd12776c8474be40a32a5245e22e0c2e75151d9ab202b
- Event 7: step.completed; program; f900cf632c6f0bc9a4f17e88f0dd60b46e7b216e03d3917052995e430cdb9113
- Event 8: run.completed; program; 6001e1e00061ed0b287e1126ea4bb9c4c360a5e4241abd4f8c2d66c53dee4e3a
- Event 9: call.recorded; program; f0ad4897eda1a913a28057b1e1e7ed49909f56acff09df18c3babe6bc88a514b
- Event 10: verdict.issued; program; acdaf2820e4a219ae15133d8df0d46587e67565703e97d2867a39cc2c6dfadd1
- Event 11: verdict.issued; program; e6eb570be9a6f6d103641f6834f4045e8dc6e2a708869ae476adb1f112081fe4
- Event 12: verdict.issued; program; 7bd46a6757ed4e641da31c60e5e40a455e85e21e28c72b3033f1ba6ccd06ca5e
- Event 13: verdict.issued; program; b3b4b10849abcbb55a35d815b7f693173630f7b6ee93b25e6c3c3a7f2768f505
- Event 14: verdict.issued; program; 7a5a6486505197f1a50e889d77298287a7586fa7226668a4ea1330dbef851ef3
- Event 15: verdict.issued; program; d747b067a1f8ba09a7d5f8c92f9a0432dac8f6bc65853ac391ffc6ad34300bbb
- Event 16: verdict.issued; program; 3a88d871bb8cd21eda85b9be9bf6a71c511f6ab8890cca33eac0ebcc75518001
- Event 17: verdict.issued; program; aba3115037648c1c7d5ff5b014fc89def0f5fa7ab977e9e01f3f2a18e8ff306f
- Event 18: verdict.issued; program; 74fd4e2ff2e0690dc6be1f7383aa073db457dfd2fb61ae95c6355cf053d32093
- Event 19: verdict.issued; program; 31ec8ca5c4c52e2d5de6f7b4884d28a5c45bc41e7f30909e417c1ca9f6f35079
- Event 20: verdict.issued; program; 7ba898daf5dd6f13144faf7584eb8f5d4d13987534ef1c13be121307b0aba8d8
- Event 21: judge.finished; program; 8324bbc99250d57fe479ca67105ac40e508907113457df0bd2f7074d62a744d1
- Event 22: call.recorded; program; 01624a56cd0e17d8de70167fdbc37051ff8a7c689bea5660e529eb673d2dad77
- Event 23: verdict.issued; program; 7a207b571dbafd1505b87041a79f26b58e11c685e8e36baffbf45cfbebe0da75
- Event 24: verdict.issued; program; ef7554326411c620746002f43cd9d843407769ca8dce973e54eae3638026da0f
- Event 25: verdict.issued; program; fea89b6ae122ff8a89448a067d9678343286d8346c272220b234dcf2eab24365
- Event 26: verdict.issued; program; 811db67e4c65ea2e15d43c125da53d278798bb9e0a03da8f443d06c61aabcd01
- Event 27: verdict.issued; program; 3c9a8411358c2ec4246c0d32c7a6036377b25287f1d6dc7369d442464cbc4b1b
- Event 28: verdict.issued; program; eaa2b40b7b750a37baa90659ca7fc1665f15aaac90b97c155f964fcb21e9c006
- Event 29: verdict.issued; program; 9f027958fd7929564ece78b321e04b8259a14b422026f931322e15f114c71f7c
- Event 30: verdict.issued; program; 7d071e7ad0786d644d0ba0c6a3746b4a1bf6fd957c0879f722c97954c4508fac
- Event 31: verdict.issued; program; 4f074a670fabcde63dae16e19dc1a0b8bbd72ad08ae5efba34e97d49e14859c1
- Event 32: verdict.issued; program; 819c42811d514eb6a719a739178a914ce033765c9f15c27cd65d9ebac68e9902
- Event 33: verdict.issued; program; 86c5a3b9337a11e32443756fff1e3d1e907371d092a77a46f6911916c67d3998
- Event 34: judge.finished; program; 12b220014a0516f5e657ebaf731e04feb96b8eb0a23bed5967e85119803f057e

This record shows what ran and what was checked. It does not prove that a conclusion is true.
