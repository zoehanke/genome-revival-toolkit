# Construct 迁移盘点与规格演练

草稿，未实现 Kit 代码，未经人工审核。Kit 工作区和 kits/ 目录未修改。
旧工作区 HEAD 无 kits/；下面的 Kit 源码只读自 Git 对象 bf90910e5b0e67985aa37db4e0b8507cbc24f2b4。
通用 Core 源码分别固定提交，不执行或 import 旧程序。模板/声明仅作规格演练，不能据此称为可运行 Kit。

## 旧代码清单

| 文件 | 提交 | 文件行数 | 逐函数行数 | 迁移处理 |
|---|---|---:|---|---|
| `genome-revival-toolkit/kits/construct/scripts/__init__.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 1 | 无函数 | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/construct/scripts/entry.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 11 | run 9..11 (3): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/construct/scripts/handoff.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 46 | validate_options 7..16 (10): 丢弃旧加载/字段手验/缓存外壳，使用接纳契约、来源数据和共享坐标函数; write_handoff 19..46 (28): 保留显式文件/参考绑定原则；按新交接形状重写，丢弃旧 Trace 与旧 schema_version 协议 | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/construct/scripts/hooks.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 6 | references 2..6 (5): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/construct/scripts/presentation.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 47 | summary 6..7 (2): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; fact_text 9..47 (39): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/construct/scripts/workflow.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 223 | _interval 20..26 (7): 丢弃旧加载/字段手验/缓存外壳，使用接纳契约、来源数据和共享坐标函数; _save 29..30 (2): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接; run_construct 33..223 (191): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接; call 137..145 (9): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接; failure 147..155 (9): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接 | extract_domain_only_discard_orchestration |
| `snapgene-dna-design/core/handlers/integration_donor.py` | `750bf4849b818be00f28684513ef19c01d901bcb` | 245 | validate_contract 24..42 (19): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; clarify 44..54 (11): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _arm_sequences 56..87 (32): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; plan 89..213 (125): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; recompute 216..229 (14): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; validate_goal 231..245 (15): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移 | retain_domain_algorithms_only |
| `snapgene-dna-design/core/recipes/gibson.py` | `750bf4849b818be00f28684513ef19c01d901bcb` | 597 | _prepare_gibson_fragments 37..90 (54): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _preparation_template 116..121 (6): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _primer_delivery 124..145 (22): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _pcr_product_record 148..150 (3): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _restore_unique_source_features 153..321 (169): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; recipe_gibson_assembly 324..597 (274): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; candidate 48..64 (17): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; all_positions 184..199 (16): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; matched_location 201..218 (18): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; actual_parts 256..278 (23): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; has_machine_clip_marker 280..285 (6): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; same_identity 287..288 (2): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; parts_are_contained 290..300 (11): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移 | retain_domain_algorithms_only |
| `snapgene-dna-design/core/recipes/verification.py` | `750bf4849b818be00f28684513ef19c01d901bcb` | 556 | _verification_candidates 54..123 (70): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _optimize_verification_primer 126..131 (6): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _search_verification_pair 134..167 (34): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _parental_pcr 170..193 (24): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _sequencing_checks 196..222 (27): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; sequencing_coverage 225..256 (32): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; recipe_cloning_verification 259..556 (298): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; individually_valid 139..143 (5): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; gaps 245..251 (7): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移 | retain_domain_algorithms_only |

依据：spec/MIGRATION-MAP.md §6、§7、§8。entry/hooks/presentation/旧运行器与手工埋点丢弃；
workflow 文件只拆取科学判据、局部计算与交接绑定，绝不复制流程外壳。旧源码行数不是规则记录数。

## 新能力表

声明文件是完整 capability-v1 草稿。source.implemented_in 是未来目标模块，不存在实现，不作已导出/已运行声明。

| id / role / granularity | inputs | params | outputs / output_role | effects | step_checks / final_checks / model | biology 与剩余工作 |
|---|---|---|---|---|---|---|
| `construct.model_donor` / ACTION / atomic | `[{"name":"reference","type":"material","required":true,"constraints":{},"description":"reference"},{"name":"cargo","type":"material","required":true,"constraints":{},"description":"cargo"}]` | `{"type":"object","properties":{"start":{"type":"integer","minimum":0},"end":{"type":"integer","minimum":0},"arm_length":{"type":"integer","minimum":1},"cargo_start":{"type":"integer","minimum":0},"cargo_end":{"type":"integer","minimum":1}},"required":["start","end","arm_length","cargo_start","cargo_end"],"additionalProperties":false}` | `[{"name":"product","type":"material","output_role":"construct"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[],"model":null}` | slice_sequence; 仍缺：Independent donor model, homology-arm selection and cargo layout.；Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization. |
| `construct.design_donor` / ACTION / composite | `[{"name":"reference","type":"material","required":true,"constraints":{},"description":"reference"},{"name":"cargo","type":"material","required":true,"constraints":{},"description":"cargo"},{"name":"donor_template","type":"material","required":false,"constraints":{},"description":"donor template"}]` | `{"type":"object","properties":{"start":{"type":"integer","minimum":0},"end":{"type":"integer","minimum":0},"arm_length":{"type":"integer","minimum":1},"cargo_start":{"type":"integer","minimum":0},"cargo_end":{"type":"integer","minimum":1},"preparation_method":{"enum":["gibson","pcr"]},"overlap":{"type":"integer","minimum":1}},"required":["start","end","arm_length","cargo_start","cargo_end","preparation_method"],"additionalProperties":false}` | `[{"name":"product","type":"material","output_role":"construct"},{"name":"primers","type":"document","output_role":"primer_set","schema_ref":"primer-set-v1"},{"name":"route","type":"document","output_role":"analysis","schema_ref":"route-plan-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[{"check":"construct.check_junction_assay"}],"model":"construct.model_donor"}` | slice_material, replace_material_region, enumerate_primer_candidates, pcr_material, gibson_material; 仍缺：Independent donor model, homology-arm selection and cargo layout.；Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization. |
| `construct.design_junction_assay` / ACTION / composite | `[{"name":"original","type":"material","required":true,"constraints":{},"description":"original"},{"name":"edited","type":"material","required":true,"constraints":{},"description":"edited"},{"name":"donor","type":"material","required":true,"constraints":{},"description":"donor"}]` | `{"type":"object","properties":{"left_arm":{"type":"array","items":{"type":"integer","minimum":0},"minItems":2,"maxItems":2},"right_arm":{"type":"array","items":{"type":"integer","minimum":0},"minItems":2,"maxItems":2}},"required":["left_arm","right_arm"],"additionalProperties":false}` | `[{"name":"primers","type":"document","output_role":"primer_set","schema_ref":"primer-set-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[{"check":"construct.check_junction_assay"}],"model":null}` | enumerate_primer_candidates, predict_pcr_products, sequencing_read_coverage; 仍缺：Independent donor model, homology-arm selection and cargo layout.；Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization. |
| `construct.check_junction_assay` / CHECK / atomic | `[]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | predict_pcr_products, find_binding_sites; 仍缺：Independent donor model, homology-arm selection and cargo layout.；Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization. |
| `construct.export_handoff` / ACTION / atomic | `[{"name":"original_file","type":"artifact","required":true,"constraints":{},"description":"original file"},{"name":"edited_file","type":"artifact","required":true,"constraints":{},"description":"edited file"},{"name":"primers","type":"document","required":true,"constraints":{},"description":"primers","schema_ref":"primer-set-v1"}]` | `{"type":"object","properties":{"name":{"type":"string"}},"required":["name"],"additionalProperties":false}` | `[{"name":"handoff","type":"artifact","output_role":"analysis"}]` | `["reads_files","writes_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | record_from_material; 仍缺：Independent donor model, homology-arm selection and cargo layout.；Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization. |

### 每个能力的 does_not_establish

- `construct.model_donor`: Successful laboratory donor preparation; Transformation efficiency; Authentic integration locus; Functional revival.
- `construct.design_donor`: Successful laboratory donor preparation; Transformation efficiency; Authentic integration locus; Functional revival.
- `construct.design_junction_assay`: Successful laboratory donor preparation; Transformation efficiency; Authentic integration locus; Functional revival.
- `construct.check_junction_assay`: Successful laboratory donor preparation; Transformation efficiency; Authentic integration locus; Functional revival.
- `construct.export_handoff`: Successful laboratory donor preparation; Transformation efficiency; Authentic integration locus; Functional revival.

## 知识与来源

旧 JSON 规则 3 条；有来源标记 3；缺失 0。缺失清单：无。
新 rule-v1 草稿 3 条，均为 draft/unverified。旧 verified 标记不继承，没有填写审核人或核验回执。
有来源表示旧数据含可追溯来源，不表示此轮联网核实或科学结论成立。来源分类规范化见 source-audit.json。

| 旧规则文件 / 提交 | 文件物理行数 | 规则记录数 | 有来源 / 缺来源 |
|---|---:|---:|---|
| `genome-revival-toolkit/kits/construct/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 5 | 3 | 3 / 0 |

| 新规则 | source_class | citation / locator | supports / does_not_support |
|---|---|---|---|
| `construct.explicit-source-bounds` | project_contract | scripts/workflow.py:run_construct input guards and source-derived model / genome-revival-toolkit/kits/construct/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Use supplied target/cargo intervals and explicit arm length; do not infer a locus."],"does_not_support":["Experimental success or biological function."]} |
| `construct.physical-route` | project_contract | scripts/workflow.py:run_construct; same-version Core workflow_delivery.py / genome-revival-toolkit/kits/construct/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Actual computational preparation and complete oligos are required for a construct handoff."],"does_not_support":["Experimental success or biological function."]} |
| `construct.donor-not-integration` | project_contract | scripts/workflow.py:run_construct checked_scope/not_checked / genome-revival-toolkit/kits/construct/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Donor interface checks do not establish genomic integration or revival."],"does_not_support":["Experimental success or biological function."]} |

## 模板与构造答案

模板：`prepare_gibson.json`, `prepare_pcr.json`。
Goal 先登记真实输入文件；模板参数绑定已登记的 source ID、goal_digest 和 target ID，不把文件路径或 DNA 字符串伪装成材料来源。
以下输入与答案在实现前由构造/手算确定，不能用旧版或待测代码生成答案。

## 要写的负例及正对照

| 负例 | 输入构造 | 预期来源与结果 |
|---|---|---|
| linear_gibson_import | Three labelled linear fragments with explicit overlaps and known final concatenation. | Typed linear product or retained original failure; never missing feature_to_dict followed by checked_scope KeyError. |
| donor_carryover | Place both junction primers wholly inside retained donor homology arms. | PCR predicts a residual-donor band and report warns that the assay cannot establish genomic integration. |
| invalid_marker_orf | Replace ATG AAA TAA with ATG TAA TAA, keeping the same marker label. | Internal stop is detected; apply D7 separately to inherited versus introduced annotation. |
| donor_bounds | Reference edit [100,160), 50 bp arms, cargo length 90; then move edit start to 30. | Valid donor is 190 bp from [50,100)+cargo+[160,210); out-of-range 50 bp arm is refused. |
| repeated_binding | Insert a second exact copy of one primer core in a supplied reference. | Retain all matches and ambiguity, never choose the shortest amplicon as unique. |

合成构造路线：固定种子生成参考，再指定 [100,160) 替换为 90 bp cargo，两侧各 50 bp；供体必须为参考 [50,100)+cargo+参考 [160,210)，长 190 bp。模型与实际 PCR/Gibson 制备路径分开；接口 QC 必须另测残留供体背景。
模板已显式连接模型、制备、编辑后参考、接口 QC 和交接导出。当前 S1 stage 仅导出 JSON 文档/值，artifact 最终输出尚待 S1；这是实现依赖，不是 schema 表达失败。

## 共用函数与 Kit 自有缺口

S1b 已有并可用：biology.public.replace_material_region, biology.public.inspect_cds, biology.public.enumerate_primer_candidates, biology.public.sequencing_read_coverage, biology.public.slice_material, biology.public.pcr_material, biology.public.gibson_material, biology.public.predict_pcr_products。
本轮新增的四个共享函数均有至少两个 Kit 的明确需求；使用矩阵见 shared-needs.json。
- 仍交该 Kit 实现：Independent donor model, homology-arm selection and cargo layout.
- 仍交该 Kit 实现：Junction-assay selection outside homology arms and donor carry-over warning; Construct-to-Identity serialization.

## 规格演练发现

完整原始校验结果由 tools/validate_kit_drafts.py 填入下方；语法通过不等于合同可执行。
<!-- VALIDATION-BEGIN -->
实际校验 11 份草稿；Schema 失败 0，A14 失败 0。
未解析 document schema_ref 等语义问题不冒充 JSON Schema 原生错误。Schema 失败原文如下：
本 Kit 草稿无原生 Schema/A14 失败；这不说明其领域文档或实现可加载。

合同/运行语义发现：
```json
[
  {
    "kit": "construct",
    "issue": "K1",
    "file": "drafts/construct/capabilities/design_donor.json",
    "message": "schema_ref is not in the existing local schema registry: primer-set-v1"
  },
  {
    "kit": "construct",
    "issue": "K1",
    "file": "drafts/construct/capabilities/design_donor.json",
    "message": "schema_ref is not in the existing local schema registry: route-plan-v1"
  },
  {
    "kit": "construct",
    "issue": "K1",
    "file": "drafts/construct/capabilities/design_junction_assay.json",
    "message": "schema_ref is not in the existing local schema registry: primer-set-v1"
  },
  {
    "kit": "construct",
    "issue": "K1",
    "file": "drafts/construct/capabilities/export_handoff.json",
    "message": "schema_ref is not in the existing local schema registry: primer-set-v1"
  },
  {
    "kit": "construct",
    "issue": "K4",
    "file": "drafts/construct/capabilities/design_donor.json",
    "message": "D3 supplies a model capability id but no target-output/argument binding contract. Producer and model differ: {\"producer_inputs\": [\"reference\", \"cargo\", \"donor_template\"], \"model_inputs\": [\"reference\", \"cargo\"], \"producer_outputs\": [\"product\", \"primers\", \"route\"], \"model_outputs\": [\"product\"]}"
  },
  {
    "kit": "construct",
    "issue": "K5",
    "file": "prompts/s5b-genome-identity.md",
    "message": "The new handoff describes primer_pair without its internal type and does not distinguish no product from unresolved multiple products when product_bp is null. Old schema_version/references-dict/rows files are a different protocol."
  }
]
```
<!-- VALIDATION-END -->

已验证：只读源文件/行数与实际草稿校验范围。模拟：合成负例计划与本轮共享纯函数。
未做：Kit 代码、Kit 端到端、封存/verify、湿实验、观察真实性验证。官方 GitLab CI 未执行；GitHub CI 未运行。
