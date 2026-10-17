# Run card

Through event 34

Journal head: f40f5b142c84e5556856a0520bf84bdf69806df7ddeea0f2c33d380ac1aae305

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

- Event 1: run.created; program; d9492f87d99e2b2cdc921917fd3814536f01c534ea95b409764be7a3b1a44d83
- Event 2: input.registered; program; e7f481db156dbd81e3ccf847ab613d1c47124344352281d63c0df4ca4e6bb41e
- Event 3: input.registered; program; bcc374491fec7f8f05428f676fde056a0bd96a8f9675ba981f1a03f828f3088f
- Event 4: goal.declared; ai_host; 1aa06061a298115149cc4959cfa81ec5df41dde61314435a2aad58da49aa531d
- Event 5: pipeline.declared; ai_host; 3bd9e760d20db28c0e2b6b827d3b5f628b5b06d2c5c79704adada6421591af13
- Event 6: declaration.recorded; ai_host; fef7c8924db822eb2cf909058dea0607e7932fd72c22b781267d6160ef5b4e82
- Event 7: declaration.recorded; ai_host; e6869c3d9cd6178b1076e622a10d5500fdfbc9e5692d62bbd225902c049702b0
- Event 8: step.started; program; 4becefb0762ef615685dfc3b2e611a8a80a38576e011cf7da28013b6c926a80f
- Event 9: step.completed; program; ccfb5238a2d6d2caadcee20829e973503669533282e81250d3091aecb176a847
- Event 10: step.started; program; ebca35c728ba57e385eb04e2094ce5e545f2ea77cdf36b49d0adcb4ecf2db98b
- Event 11: step.completed; program; de7fb82cf0b694f23986d1d7fea987564f6ada0785a98a137c6aa6cd49b6760f
- Event 12: run.completed; program; 8ad4da374bd9c06001a2cf030d5895bd3efa634020987a327985385c43d0c752
- Event 13: call.recorded; program; 238c7477cbbb09598f534c4e28657344a0bf56158bc42f4871565d9fb8b6ca17
- Event 14: verdict.issued; program; 06dde431b6660f80bc7fd526a850ce863ceab52158e4ffa97b0df7bcba4f48c8
- Event 15: verdict.issued; program; c8d02ce981bce1c3424dc77d049bccd5df8a1462db4b99fb87e1a47c1d0a2446
- Event 16: verdict.issued; program; 151230dd3ae465bf228b561c3e162d0fb64dec1ab6e5cb0bfdfbe49fdc2ec121
- Event 17: verdict.issued; program; 71775f88f78cb21c4cd6ff18c7ff34e9e41a2226e93e0ece89dd496a227db994
- Event 18: verdict.issued; program; dd8eb54b2f6a32d43045032c7289408fa6bbec4f989f51ecd8e67a7e8e939789
- Event 19: verdict.issued; program; c3138fab3b2652101043fb83ace09520cc3995192bd941f8fbae1d5f62c92e3e
- Event 20: verdict.issued; program; 5c48cac042fbc95bb6d142454284d580ead21035aa33a2a598d6145f9480fbeb
- Event 21: verdict.issued; program; fc8916fe54cb7d3ef609c113be9e3c05bfbfc2ce7f057eb38b5e3efcf08c9977
- Event 22: verdict.issued; program; 276a4e1e3ec338fdc3825babef09bd3e2eed02ab0a75636cdec69289461e8c87
- Event 23: judge.finished; program; ef940e4e4e7a9ba06ce6e11e26aefec7e6f9ee15c7eaa741bce597936be7e452
- Event 24: call.recorded; program; f7545e4751abce883df4ab59e7b1cdf8e325a9988e677b99d7879338f61b2b8e
- Event 25: verdict.issued; program; 29f4b56bc9bb1a124edcc4f5bcf04760480e2ba248406f91f2209c98ddd7fc45
- Event 26: verdict.issued; program; 057d0adbc1ca048e874ec67e3c8ae2b30180a2063da6188c12062302205001ac
- Event 27: verdict.issued; program; c449e5b28296addef40e3a1eab7e7747bda0e7b32d7ec99d4b5800293db38002
- Event 28: verdict.issued; program; 1fbe4ebc3dc31a3ac91332a38da58f31cf2cafee4227b62bfa2ee12c232dcf35
- Event 29: verdict.issued; program; 6130fdf98615ec39b23879f9f261aae6321adf4ab7328bbcb08785840c3e4ae5
- Event 30: verdict.issued; program; 87caa8e3767c1433c452f287b1935e04791f72a250603de58810c9277220357e
- Event 31: verdict.issued; program; c3715c95643858652c14b94b62a3e8e0e9309d387a39ee9520beae9ce12ddacd
- Event 32: verdict.issued; program; 711509dd2ab7281c2d00f1bfac611ea9ee050df5478455d33540e977bc3d66c4
- Event 33: verdict.issued; program; ee8fece593e8f89b758d320b2f3518e2ba1fae7148428ca25a8346b2b867c3c2
- Event 34: judge.finished; program; f40f5b142c84e5556856a0520bf84bdf69806df7ddeea0f2c33d380ac1aae305

This record shows what ran and what was checked. It does not prove that a conclusion is true.
