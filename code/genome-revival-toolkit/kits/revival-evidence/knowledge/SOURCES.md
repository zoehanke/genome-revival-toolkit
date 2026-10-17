# Rule sources

Generated from declared rule-v1 files. All sources remain unverified; no human review receipt exists.

## evidence.functional_revival

- Class: project_contract
- Citation: Genome Revival Toolkit SPEC D12 and Appendix B3 (2026-10-16)
- Locator: spec/SPEC.md D12; B3; prompts/s3-revival-evidence.md
- Supports: Adopt a bounded conclusion; observations alone cannot certify functional revival.
- Does not support: Biological proof of revival, elimination, causality or record authenticity.
- Table rows: 2
- Every table row uses source_ref=evidence.functional_revival and inherits this rule source.

## evidence.genome_elimination

- Class: project_contract
- Citation: Genome Revival Toolkit SPEC D12 and Appendix B3 (2026-10-16)
- Locator: spec/SPEC.md D12; B3
- Supports: Local assays cannot support a whole-genome elimination conclusion.
- Does not support: Biological proof of revival, elimination, causality or record authenticity.
- Table rows: 2
- Every table row uses source_ref=evidence.genome_elimination and inherits this rule source.

## evidence.control_absence

- Class: project_contract
- Citation: Genome Revival Toolkit SPEC D12 and Appendix B3 (2026-10-16)
- Locator: prompts/s3-revival-evidence.md Sources and negative cases; spec/SPEC.md B3
- Supports: Preserve the requested contradiction for an inactivated-donor no-outgrowth control and missing-count handling.
- Does not support: Biological proof of revival, elimination, causality or record authenticity.
- Table rows: 3
- Every table row uses source_ref=evidence.control_absence and inherits this rule source.

## evidence.local_prediction

- Class: project_contract
- Citation: Genome Revival Toolkit SPEC D12 and Appendix B3 (2026-10-16); user decision 2026-10-17
- Locator: spec/SPEC.md B3 boundary; prompts/s5b-genome-identity.md output handoff; prompts/s3-revival-evidence.md goal; prompts/s1d-usability-fixes.md B4; prompts/s1d-usability-fixes.md B5; prompts/s1e-evidence-rule-and-docs.md section 1
- Supports: Compare supplied, hash-bound local predictions with reported results; support or contradict only that local agreement. A complete reported positive band may contradict a local prediction without confirmed passing controls; a negative mismatch requires reported passed controls. User decision 2026-10-17; project interpretation only.
- Does not support: Biological proof of revival, elimination, causality or record authenticity.
- Table rows: 10
- Every table row uses source_ref=evidence.local_prediction and inherits this rule source.

The positive/negative distinction follows the user's 2026-10-17 decision. This
records a project interpretation choice, not a source-verification receipt or
a team review. Verification remains `unverified`; no human review is asserted.

## evidence.fusion_plate_outgrowth

- Class: project_contract
- Citation: Genome Revival Toolkit SPEC D12 与附录 B3；用户 2026-10-17 的决定（方案 B）
- Locator: spec/SPEC.md D12; B3; prompts/s3b-scoped-supported-conclusion.md
- Supports: 融合平板有菌落而指定的无生长对照没有；这不证明功能复活，也不证明对照细胞已死
- Does not support: 功能复活、遗传学恢复、供体来源、对照细胞死亡、记录的真实性
- Table rows: 5
- Every table row uses source_ref=evidence.fusion_plate_outgrowth and inherits this rule source.
- Source verification: unverified. No human review receipt exists. Team declaration remains required.
