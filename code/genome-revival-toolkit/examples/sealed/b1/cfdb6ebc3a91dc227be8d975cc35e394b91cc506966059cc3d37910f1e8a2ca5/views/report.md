# Run card

Through event 34

Journal head: 70cdff47d42a016cfc83e235b9be3130eef0936076e0f765a7d956653e57631a

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
- Experimental performance or correctness of a scientific conclusion.
- Revisions recorded: 0
- This development-tree package is not release evidence.
- Wet-laboratory performance or biological function.
- reviewed 0 / stale 0 / none 5

## Technical details

- Event 1: run.created; program; 7fd5f8fa50ac24b5fba5e9b110d9102dbdb0f9cbfe4903b9ca35c3bb70954e10
- Event 2: goal.declared; ai_host; 28f6468143b9060899b58ff87b94a12c47daea9f63bd14089e4e02a6f89f3e25
- Event 3: pipeline.declared; ai_host; 6ceb7b1b153744580eed73f47384630f3fa6027798413cf84fa9515ed68c10e6
- Event 4: declaration.recorded; ai_host; 76d6a5cfab361b9da2582dccc7a52d58a168cf60a29be8d27c1ea8de64d96aa2
- Event 5: step.started; program; 37c6246e61bef331688a11ecdeec8f114c6f32db7400657f570f06ddb32d5486
- Event 6: verdict.issued; program; c56988a13ddefd8838ce7babfc6bcbe2649e0ad6df6a9155e960b59cce0e47be
- Event 7: step.completed; program; d506bc6e2f1c0acadd602222c823613cfeb4c3f8730d9e1cefa18b63dde020b9
- Event 8: run.completed; program; dfbe5d7a7506eff0aad40ef6cc94de0fd888b6e589146b772e9320e7b4e52e56
- Event 9: call.recorded; program; 1657ad85daa74cb69f3ca9350d9dc4758a768420831d106afe0f3c92e3f21098
- Event 10: verdict.issued; program; e007db64c5440fe5b750fa35b0d98e8819a619303690e01143081271a0c8625a
- Event 11: verdict.issued; program; 845c50c150016cc5a9169de515622ff86722a46a9181f496894001014fe16797
- Event 12: verdict.issued; program; cc862ecbbfad3ba3674236dce408199c70958dbeaa75b2c2be56400b514db4e6
- Event 13: verdict.issued; program; 5b0d26d773765f5f5082aa5d957f50246e3c000c1c33206488cb01601ea867f2
- Event 14: verdict.issued; program; e9f6de9385f1bc196bfd5d855e600f61bddc1d056c34ea185fcc8db7358e35c9
- Event 15: verdict.issued; program; 03f6b950152b4983a0b1c1364c7d1282dd696f128568ee2a1ffbf82614526916
- Event 16: verdict.issued; program; 455b040fcb6ca1217c63f8bf96f0547ed6e9628466de7ff1fb68ae21eb765e1a
- Event 17: verdict.issued; program; fb4eca9fb7007e0ac0a901a573dc3068dfe8678b104411eea995768732a24595
- Event 18: verdict.issued; program; f5e6025b819e0559cae3c0021ea0ba579626bda72ad731d1aea4c36c23b52b37
- Event 19: verdict.issued; program; a9840158ad260a11b8d30840700d1e7b50c8c61f103f94c78c23ad3e4df386e2
- Event 20: verdict.issued; program; d552f20a063ab064b5493aeab93eea5c826f6f7f62070709bc6e9203260163c9
- Event 21: judge.finished; program; 36ac5ed4258c3049e806658a7e943746a5c52aa9f8e0e590843975ae3bfe4c02
- Event 22: call.recorded; program; 0a6094ea352daf6108b5a8146d0b628962d6810447506ab541c8042b5bf314d7
- Event 23: verdict.issued; program; 3e2624a478e61e32edb46279a7c0216bccda31c2ea66556f0f368d2519064b0a
- Event 24: verdict.issued; program; 7364bf57208927f5afeae3bf7cf59e7ce0108535b00ac5ffec12754350ec6101
- Event 25: verdict.issued; program; f4aa182f429605264ad1242b2f2ad8371e55627a7c384e58f130c4757f7a455a
- Event 26: verdict.issued; program; cafd662fb29243fc37b9ec689d71d60a235c313157ad1a52d8d613fc01552f29
- Event 27: verdict.issued; program; 0b5691861ef8abc510e3a5dfe0e49c29504f22c1959959a1c23f0d9cceb338d7
- Event 28: verdict.issued; program; 168724f2121d9767602cb35dd28eaeab293203360f063ad0b5bcc9f05ded9d33
- Event 29: verdict.issued; program; f3d4f8db0f4359f412ae82931fe62e281c0c825f6aa62f7103a53422c4ac0dd8
- Event 30: verdict.issued; program; 98256f158f262fed769679cf071a7bb88dfbcc703d2913451828b077948d13ca
- Event 31: verdict.issued; program; 317fb013ccfe5a274be8db1c8c12f0fd5d8d26c32e13377a2b236959be1a6dfb
- Event 32: verdict.issued; program; df5614a414c1628ff044c42a5aa169dee5e36516cd4f1278b079f58d4b08773c
- Event 33: verdict.issued; program; e135d6f5888db72a92c95ff2aea714eb74820d546af02db7308c3d2ff37da92d
- Event 34: judge.finished; program; 70cdff47d42a016cfc83e235b9be3130eef0936076e0f765a7d956653e57631a

This record shows what ran and what was checked. It does not prove that a conclusion is true.
