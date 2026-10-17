# Cut Plasmid 迁移盘点与规格演练

草稿，未实现 Kit 代码，未经人工审核。Kit 工作区和 kits/ 目录未修改。
旧工作区 HEAD 无 kits/；下面的 Kit 源码只读自 Git 对象 bf90910e5b0e67985aa37db4e0b8507cbc24f2b4。
通用 Core 源码分别固定提交，不执行或 import 旧程序。模板/声明仅作规格演练，不能据此称为可运行 Kit。

## 旧代码清单

| 文件 | 提交 | 文件行数 | 逐函数行数 | 迁移处理 |
|---|---|---:|---|---|
| `genome-revival-toolkit/kits/crispr/scripts/__init__.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 1 | 无函数 | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/crispr/scripts/entry.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 11 | run 9..11 (3): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/crispr/scripts/gates.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 23 | evaluate 9..19 (11): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; context_for_result 22..23 (2): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接 | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/crispr/scripts/hooks.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 3 | references 2..3 (2): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/crispr/scripts/presentation.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 39 | summary 6..24 (19): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; fact_text 26..39 (14): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/crispr/scripts/selection.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 124 | mapping_rows 20..23 (4): 丢弃旧加载/字段手验/缓存外壳，使用接纳契约、来源数据和共享坐标函数; _mapping_rows 27..37 (11): 丢弃旧加载/字段手验/缓存外壳，使用接纳契约、来源数据和共享坐标函数; marker_mappings 40..41 (2): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; mapping_sources 44..45 (2): 丢弃旧加载/字段手验/缓存外壳，使用接纳契约、来源数据和共享坐标函数; marker_ids 48..50 (3): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology; selection_report 53..124 (72): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/crispr/scripts/workflow.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 113 | write_selection 17..27 (11): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接; run_crispr 30..113 (84): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接 | extract_domain_only_discard_orchestration |
| `snapgene-dna-design/core/tools/grna.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 293 | _label 19..24 (6): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _location 27..37 (11): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _parts 40..41 (2): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _overlaps 44..47 (4): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _locate 50..117 (68): 科学判据留给 S2；本轮不移植 CRISPR 代码; _annotation_warnings 120..129 (10): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; replace_grna_spacer 132..207 (76): 科学判据留给 S2；本轮不移植 CRISPR 代码; _target_matches 210..231 (22): 科学判据留给 S2；本轮不移植 CRISPR 代码; check_grna 234..293 (60): 科学判据留给 S2；本轮不移植 CRISPR 代码 | retain_domain_algorithms_only |
| `snapgene-dna-design/core/tools/grna_evaluation.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 209 | validate_mismatch_limit 30..32 (3): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _parts 35..39 (5): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; pam_sites 42..66 (25): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; matching_sites 69..77 (9): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; vector_report 80..97 (18): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; check_grna_vector 100..118 (19): 科学判据留给 S2；本轮不移植 CRISPR 代码; exact_loci 121..134 (14): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; evaluate_candidates 137..209 (73): 首版丢弃候选 gRNA 枚举/排序；只检查或替换用户选定 guide | retain_domain_algorithms_only |
| `snapgene-dna-design/core/tools/grna_preparation.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 152 | _hits 21..24 (4): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; preparation_warnings 27..47 (21): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; plan_and_simulate 50..138 (89): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; protocol_steps 141..152 (12): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移 | retain_domain_algorithms_only |

依据：spec/MIGRATION-MAP.md §6、§7、§8。entry/hooks/presentation/旧运行器与手工埋点丢弃；
workflow 文件只拆取科学判据、局部计算与交接绑定，绝不复制流程外壳。旧源码行数不是规则记录数。

## 新能力表

声明文件是完整 capability-v1 草稿。source.implemented_in 是未来目标模块，不存在实现，不作已导出/已运行声明。

| id / role / granularity | inputs | params | outputs / output_role | effects | step_checks / final_checks / model | biology 与剩余工作 |
|---|---|---|---|---|---|---|
| `cut_plasmid.inspect_guide` / ACTION / atomic | `[{"name":"vector","type":"material","required":true,"constraints":{},"description":"vector"},{"name":"target","type":"material","required":true,"constraints":{},"description":"target"}]` | `{"type":"object","properties":{"promoter_end":{"type":"integer","minimum":0},"transcription_strand":{"enum":[-1,1]},"scaffold_sequence":{"type":"string"}},"required":["promoter_end","transcription_strand","scaffold_sequence"],"additionalProperties":false}` | `[{"name":"guide","type":"document","output_role":"analysis","schema_ref":"guide-inspection-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[{"check":"cut_plasmid.check_direction"},{"check":"cut_plasmid.check_pam"},{"check":"cut_plasmid.check_vector_self_target"}],"model":null}` | record_from_material, find_binding_sites; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |
| `cut_plasmid.replace_spacer` / ACTION / composite | `[{"name":"vector","type":"material","required":true,"constraints":{},"description":"vector"},{"name":"target","type":"material","required":true,"constraints":{},"description":"target"}]` | `{"type":"object","properties":{"promoter_end":{"type":"integer","minimum":0},"transcription_strand":{"enum":[-1,1]},"scaffold_sequence":{"type":"string"},"spacer":{"type":"string","pattern":"^[ACGT]{20}$"},"target_tm":{"type":"string"}},"required":["promoter_end","transcription_strand","scaffold_sequence","spacer","target_tm"],"additionalProperties":false}` | `[{"name":"product","type":"material","output_role":"construct"},{"name":"primers","type":"document","output_role":"primer_set","schema_ref":"primer-set-v1"},{"name":"route","type":"document","output_role":"analysis","schema_ref":"route-plan-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[{"check":"cut_plasmid.check_direction"},{"check":"cut_plasmid.check_pam"},{"check":"cut_plasmid.check_vector_self_target"}],"model":"cut_plasmid.model_replace"}` | replace_material_region, enumerate_primer_candidates, inverse_pcr_material, sequencing_read_coverage; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |
| `cut_plasmid.assess_selection` / ACTION / atomic | `[{"name":"vector","type":"material","required":true,"constraints":{},"description":"vector"},{"name":"declared_genotype","type":"value","required":false,"constraints":{},"description":"declared genotype"}]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[{"name":"selection","type":"document","output_role":"analysis","schema_ref":"selection-assessment-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[],"model":null}` | inspect_cds, record_from_material; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |
| `cut_plasmid.model_replace` / ACTION / atomic | `[{"name":"vector","type":"material","required":true,"constraints":{},"description":"vector"},{"name":"target","type":"material","required":true,"constraints":{},"description":"target"}]` | `{"type":"object","properties":{"promoter_end":{"type":"integer","minimum":0},"transcription_strand":{"enum":[-1,1]},"scaffold_sequence":{"type":"string"},"spacer":{"type":"string","pattern":"^[ACGT]{20}$"}},"required":["promoter_end","transcription_strand","scaffold_sequence","spacer"],"additionalProperties":false}` | `[{"name":"product","type":"material","output_role":"construct"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[],"model":null}` | 无共享生物函数；保留领域计算独立性; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |
| `cut_plasmid.check_direction` / CHECK / atomic | `[]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | record_from_material; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |
| `cut_plasmid.check_pam` / CHECK / atomic | `[]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | record_from_material; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |
| `cut_plasmid.check_vector_self_target` / CHECK / atomic | `[]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | record_from_material; 仍缺：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).；Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration. |

### 每个能力的 does_not_establish

- `cut_plasmid.inspect_guide`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.
- `cut_plasmid.replace_spacer`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.
- `cut_plasmid.assess_selection`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.
- `cut_plasmid.model_replace`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.
- `cut_plasmid.check_direction`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.
- `cut_plasmid.check_pam`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.
- `cut_plasmid.check_vector_self_target`: Cleavage activity; Editing efficiency; Genome-wide off-target safety; Wet-laboratory PCR, DpnI, KLD or transformation.

## 知识与来源

旧 JSON 规则 13 条；有来源标记 13；缺失 0。缺失清单：无。
新 rule-v1 草稿 13 条，均为 draft/unverified。旧 verified 标记不继承，没有填写审核人或核验回执。
有来源表示旧数据含可追溯来源，不表示此轮联网核实或科学结论成立。来源分类规范化见 source-audit.json。

| 旧规则文件 / 提交 | 文件物理行数 | 规则记录数 | 有来源 / 缺来源 |
|---|---:|---:|---|
| `genome-revival-toolkit/kits/crispr/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 6 | 4 | 4 / 0 |
| `genome-revival-toolkit/kits/crispr/rules/selection.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 519 | 9 | 9 / 0 |
selection.json 是 519 行、9 条 marker 映射；kan 按 ecoli/yeast 两种来源拆分，成为 10 条 marker-host 规则。
旧 no-template-exemption 与 D7 冲突，保留原记录并退役，不把旧拒绝逻辑原样迁移。

| 新规则 | source_class | citation / locator | supports / does_not_support |
|---|---|---|---|
| `crispr.sequence-direction` | project_contract | scripts/workflow.py:run_crispr; Core tools/grna.py:check_grna / genome-revival-toolkit/kits/crispr/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Sequence downstream of the promoter determines guide orientation and PAM; annotation conflicts remain warnings."],"does_not_support":["Experimental success or biological function."]} |
| `crispr.supplied-vector` | project_contract | scripts/workflow.py:run_crispr; Core tools/grna_evaluation.py:check_grna_vector / genome-revival-toolkit/kits/crispr/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Search the caller's actual supplied vector, with declared mismatch limit and PAM."],"does_not_support":["Experimental success or biological function."]} |
| `crispr.planned-not-performed` | project_contract | scripts/workflow.py:run_crispr laboratory_status/wet_lab / genome-revival-toolkit/kits/crispr/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Independent sequence simulation is not physical PCR, DpnI or KLD."],"does_not_support":["Experimental success or biological function."]} |
| `selection.amp.ecoli` | official_method | NEB Turbo competent E. coli: antibiotics for plasmid selection / https://www.neb.com/en-us/products/c2986-neb-turbo-electrocompetent-e-coli | {"supports":["ecoli selection mapping for amp"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.kan.ecoli` | official_method | NEB Turbo competent E. coli: antibiotics for plasmid selection / https://www.neb.com/en-us/products/c2986-neb-turbo-electrocompetent-e-coli | {"supports":["ecoli selection mapping for kan"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.kan.yeast` | literature | Chee and Haase, G3 2012, redesigned pRS vectors / https://pmc.ncbi.nlm.nih.gov/articles/PMC3362935/ | {"supports":["yeast selection mapping for kan"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.cat.ecoli` | official_method | NEB Turbo competent E. coli: antibiotics for plasmid selection / https://www.neb.com/en-us/products/c2986-neb-turbo-electrocompetent-e-coli | {"supports":["ecoli selection mapping for cat"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.hph.yeast` | literature | Chee and Haase, G3 2012, redesigned pRS vectors / https://pmc.ncbi.nlm.nih.gov/articles/PMC3362935/ | {"supports":["yeast selection mapping for hph"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.nat.yeast` | literature | Chee and Haase, G3 2012, redesigned pRS vectors / https://pmc.ncbi.nlm.nih.gov/articles/PMC3362935/ | {"supports":["yeast selection mapping for nat"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.ura3.yeast` | literature | Chee and Haase, G3 2012, redesigned pRS vectors / https://pmc.ncbi.nlm.nih.gov/articles/PMC3362935/ | {"supports":["yeast selection mapping for ura3"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.his3.yeast` | database_record | SGD commonly used auxotrophic markers / https://wiki.yeastgenome.org/index.php/Commonly_used_auxotrophic_markers | {"supports":["yeast selection mapping for his3"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.leu2.yeast` | database_record | SGD commonly used auxotrophic markers / https://wiki.yeastgenome.org/index.php/Commonly_used_auxotrophic_markers | {"supports":["yeast selection mapping for leu2"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |
| `selection.trp1.yeast` | database_record | SGD commonly used auxotrophic markers / https://wiki.yeastgenome.org/index.php/Commonly_used_auxotrophic_markers | {"supports":["yeast selection mapping for trp1"],"does_not_support":["Resistance, expression or compatible selection measured in the user's strain."]} |

## 模板与构造答案

模板：`inspect_only.json`, `replace_spacer.json`。
Goal 先登记真实输入文件；模板参数绑定已登记的 source ID、goal_digest 和 target ID，不把文件路径或 DNA 字符串伪装成材料来源。
以下输入与答案在实现前由构造/手算确定，不能用旧版或待测代码生成答案。

## 要写的负例及正对照

| 负例 | 输入构造 | 预期来源与结果 |
|---|---|---|
| reverse_insert | Use a nonpalindromic 20 nt spacer, its reverse complement in vector, one correctly oriented target + NGG; keep annotations falsely forward. | FAIL direction from actual transcribed sequence; annotation does not override bases. |
| one_base_pam | Change the last G of target NGG to A with protospacer unchanged. | FAIL with domain finding INVALID_PAM, paired original NGG control passes. |
| annotation_contradiction | Keep valid bases but flip annotated chain; separately label the spacer as CDS. | Keep contradiction visible; do not infer a selectable marker from that annotation. |
| inherited_cds | Carry one known-invalid CDS unchanged through copy/rotation; compare with a newly introduced invalid CDS. | D7 source-bound inherited finding is listed; introduced or unbound finding fails. Shared CDS metrics alone never grant inheritance. |
| tm_parameters | Same primer with Na 50 mM/Mg 0 versus explicitly changed Mg/salt method. | Output parameters and method differ; no silent comparison against a single generic 60 C number. |
| sequencing_off_by_one | Primer [0,4), trim=1, read_length=4 on a labelled sequence. | Covered bases are [5,8), excluding primer and the first trimmed base. |

合成构造路线：固定非回文 20 nt spacer；先确定启动子边界、链和后接 scaffold，再构造目标 protospacer+TGG。插反、单碱基 PAM 改动及标注矛盾分别从此控制构造。首版不枚举候选 gRNA，旧排序无区分度问题不带入首版。

## 共用函数与 Kit 自有缺口

S1b 已有并可用：biology.public.replace_material_region, biology.public.inspect_cds, biology.public.enumerate_primer_candidates, biology.public.sequencing_read_coverage, biology.public.find_binding_sites, biology.public.pcr_material, biology.public.inverse_pcr_material, biology.public.calculate_tm。
本轮新增的四个共享函数均有至少两个 Kit 的明确需求；使用矩阵见 shared-needs.json。
- 仍交该 Kit 实现：Promoter/scaffold location, sequence-derived guide direction, PAM and supplied-vector self-target checks (S2 only).
- 仍交该 Kit 实现：Guide-specific inverse-PCR layout and selection interpretation; no candidate-guide enumeration.

## 规格演练发现

完整原始校验结果由 tools/validate_kit_drafts.py 填入下方；语法通过不等于合同可执行。
<!-- VALIDATION-BEGIN -->
实际校验 23 份草稿；Schema 失败 0，A14 失败 0。
未解析 document schema_ref 等语义问题不冒充 JSON Schema 原生错误。Schema 失败原文如下：
本 Kit 草稿无原生 Schema/A14 失败；这不说明其领域文档或实现可加载。

合同/运行语义发现：
```json
[
  {
    "kit": "cut-plasmid",
    "issue": "K1",
    "file": "drafts/cut-plasmid/capabilities/assess_selection.json",
    "message": "schema_ref is not in the existing local schema registry: selection-assessment-v1"
  },
  {
    "kit": "cut-plasmid",
    "issue": "K1",
    "file": "drafts/cut-plasmid/capabilities/inspect_guide.json",
    "message": "schema_ref is not in the existing local schema registry: guide-inspection-v1"
  },
  {
    "kit": "cut-plasmid",
    "issue": "K1",
    "file": "drafts/cut-plasmid/capabilities/replace_spacer.json",
    "message": "schema_ref is not in the existing local schema registry: primer-set-v1"
  },
  {
    "kit": "cut-plasmid",
    "issue": "K1",
    "file": "drafts/cut-plasmid/capabilities/replace_spacer.json",
    "message": "schema_ref is not in the existing local schema registry: route-plan-v1"
  },
  {
    "kit": "cut-plasmid",
    "issue": "K6",
    "file": "drafts/cut-plasmid/capabilities/assess_selection.json",
    "message": "D12 permits an ACTION evaluator to consume frozen knowledge, but D3 exposes knowledge(pack) only on CHECK ctx.view; no ACTION frozen-knowledge access contract is specified."
  },
  {
    "kit": "cut-plasmid",
    "issue": "K4",
    "file": "drafts/cut-plasmid/capabilities/replace_spacer.json",
    "message": "D3 supplies a model capability id but no target-output/argument binding contract. Producer and model differ: {\"producer_inputs\": [\"vector\", \"target\"], \"model_inputs\": [\"vector\", \"target\"], \"producer_outputs\": [\"product\", \"primers\", \"route\"], \"model_outputs\": [\"product\"]}"
  }
]
```
<!-- VALIDATION-END -->

已验证：只读源文件/行数与实际草稿校验范围。模拟：合成负例计划与本轮共享纯函数。
未做：Kit 代码、Kit 端到端、封存/verify、湿实验、观察真实性验证。官方 GitLab CI 未执行；GitHub CI 未运行。
