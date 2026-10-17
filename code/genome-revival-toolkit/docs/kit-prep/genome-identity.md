# Genome Identity 迁移盘点与规格演练

草稿，未实现 Kit 代码，未经人工审核。Kit 工作区和 kits/ 目录未修改。
旧工作区 HEAD 无 kits/；下面的 Kit 源码只读自 Git 对象 bf90910e5b0e67985aa37db4e0b8507cbc24f2b4。
通用 Core 源码分别固定提交，不执行或 import 旧程序。模板/声明仅作规格演练，不能据此称为可运行 Kit。

## 旧代码清单

| 文件 | 提交 | 文件行数 | 逐函数行数 | 迁移处理 |
|---|---|---:|---|---|
| `genome-revival-toolkit/kits/identity/scripts/__init__.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 1 | 无函数 | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/identity/scripts/entry.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 35 | run 18..21 (4): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; assess 24..35 (12): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/identity/scripts/handoff.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 38 | read_construct_handoff 7..21 (15): 保留显式文件/参考绑定原则；按新交接形状重写，丢弃旧 Trace 与旧 schema_version 协议; expectation_table 24..38 (15): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/identity/scripts/hooks.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 3 | references 2..3 (2): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/identity/scripts/output.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 35 | _primer_outputs 9..23 (15): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; outputs 26..35 (10): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/identity/scripts/presentation.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 17 | format_comparison 6..8 (3): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; summary 10..11 (2): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; fact_text 13..17 (5): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/identity/scripts/workflow.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 161 | _discrimination 14..32 (19): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology; run_identity 35..161 (127): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接 | extract_domain_only_discard_orchestration |
| `snapgene-dna-design/core/tools/comparison.py` | `750bf4849b818be00f28684513ef19c01d901bcb` | 142 | _region 12..46 (35): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; compare_sequences 49..142 (94): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移 | retain_domain_algorithms_only |

依据：spec/MIGRATION-MAP.md §6、§7、§8。entry/hooks/presentation/旧运行器与手工埋点丢弃；
workflow 文件只拆取科学判据、局部计算与交接绑定，绝不复制流程外壳。旧源码行数不是规则记录数。

## 新能力表

声明文件是完整 capability-v1 草稿。source.implemented_in 是未来目标模块，不存在实现，不作已导出/已运行声明。

| id / role / granularity | inputs | params | outputs / output_role | effects | step_checks / final_checks / model | biology 与剩余工作 |
|---|---|---|---|---|---|---|
| `identity.compare_regions` / ACTION / atomic | `[{"name":"references","type":"materials","required":true,"constraints":{},"description":"references"}]` | `{"type":"object","properties":{"regions":{"type":"array","items":{"type":"object"}}},"required":["regions"],"additionalProperties":false}` | `[{"name":"comparison","type":"document","output_role":"analysis","schema_ref":"region-comparison-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[],"model":null}` | slice_material; 仍缺：Regional alignment, assay discrimination and identity handoff parsing/output, only this Kit requires their domain decisions. |
| `identity.analyze_assay` / ACTION / atomic | `[{"name":"references","type":"materials","required":true,"constraints":{},"description":"references"},{"name":"forward","type":"material","required":true,"constraints":{},"description":"forward"},{"name":"reverse","type":"material","required":true,"constraints":{},"description":"reverse"},{"name":"handoff","type":"document","required":false,"constraints":{},"description":"handoff","schema_ref":"identity-handoff-v1"}]` | `{"type":"object","properties":{"assay_id":{"type":"string"},"size_resolution_bp":{"type":["integer","null"],"minimum":1}},"required":["assay_id"],"additionalProperties":false}` | `[{"name":"expected_results","type":"document","output_role":"analysis","schema_ref":"identity-expected-results-v1"}]` | `["pure"]` | `{"step_checks":[],"final_checks":[],"model":null}` | predict_pcr_products, find_binding_sites, enumerate_primer_candidates; 仍缺：Regional alignment, assay discrimination and identity handoff parsing/output, only this Kit requires their domain decisions. |
| `identity.read_handoff` / ACTION / atomic | `[{"name":"file","type":"artifact","required":true,"constraints":{},"description":"file"}]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[{"name":"handoff","type":"document","output_role":"analysis","schema_ref":"identity-handoff-v1"}]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[{"check":"identity.check_handoff"}],"model":null}` | record_from_material; 仍缺：Regional alignment, assay discrimination and identity handoff parsing/output, only this Kit requires their domain decisions. |
| `identity.check_handoff` / CHECK / atomic | `[]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | record_from_material; 仍缺：Regional alignment, assay discrimination and identity handoff parsing/output, only this Kit requires their domain decisions. |

### 每个能力的 does_not_establish

- `identity.compare_regions`: Primer specificity in an actual strain; Observed experimental products; Authentic genotype; Whole-genome discrimination.
- `identity.analyze_assay`: Primer specificity in an actual strain; Observed experimental products; Authentic genotype; Whole-genome discrimination.
- `identity.read_handoff`: Primer specificity in an actual strain; Observed experimental products; Authentic genotype; Whole-genome discrimination.
- `identity.check_handoff`: Primer specificity in an actual strain; Observed experimental products; Authentic genotype; Whole-genome discrimination.

## 知识与来源

旧 JSON 规则 3 条；有来源标记 3；缺失 0。缺失清单：无。
新 rule-v1 草稿 3 条，均为 draft/unverified。旧 verified 标记不继承，没有填写审核人或核验回执。
有来源表示旧数据含可追溯来源，不表示此轮联网核实或科学结论成立。来源分类规范化见 source-audit.json。

| 旧规则文件 / 提交 | 文件物理行数 | 规则记录数 | 有来源 / 缺来源 |
|---|---:|---:|---|
| `genome-revival-toolkit/kits/identity/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 8 | 3 | 3 / 0 |

| 新规则 | source_class | citation / locator | supports / does_not_support |
|---|---|---|---|
| `identity.supplied-region-scope` | project_contract | scripts/workflow.py:run_identity checked_scope; original given-region workflow contract / genome-revival-toolkit/kits/identity/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Alignment and PCR conclusions cover only supplied selected records/regions."],"does_not_support":["Experimental success or biological function."]} |
| `identity.prediction-not-experiment` | project_contract | scripts/workflow.py:run_identity unverified; existing Toolkit scientific contract / genome-revival-toolkit/kits/identity/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Exact PCR predictions do not certify observed bands, genotype or genomic specificity."],"does_not_support":["Experimental success or biological function."]} |
| `identity.full-quality-and-resolution` | project_contract | scripts/workflow.py:run_identity and _discrimination; retained independent primer/region regression tests / genome-revival-toolkit/kits/identity/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Full oligo quality and an explicit size-resolution condition remain separate from predicted product presence."],"does_not_support":["Experimental success or biological function."]} |

## 模板与构造答案

模板：`from_references.json`, `from_handoff.json`。
Goal 先登记真实输入文件；模板参数绑定已登记的 source ID、goal_digest 和 target ID，不把文件路径或 DNA 字符串伪装成材料来源。
以下输入与答案在实现前由构造/手算确定，不能用旧版或待测代码生成答案。

## 要写的负例及正对照

| 负例 | 输入构造 | 预期来源与结果 |
|---|---|---|
| different_sizes | Generate common unique primer flanks with interiors fixing lengths 1000 and 1300. | Predicted lengths are exactly 1000/1300; resolution is explicit before a discrimination statement. |
| same_sizes | Two different backgrounds have the same predicted band state and length. | NOT_DISTINGUISHABLE for this assay; sequence differences alone do not imply different bands. |
| multiple_sites | Duplicate a complete primer site in one background only. | Ambiguity stays distinct from a negative product; cannot encode a single certain product length. |
| circular_origin | Place a complete core across the last and first bases of a constructed circle. | Coordinates wrap and exact product is computed from the same declared circle. |
| handoff_hash | Change one byte of a reference file after preparing its handoff hash. | Reference/file binding fails before biological discrimination. |

合成构造路线：先指定唯一 forward 20 nt 与 reverse-reference 20 nt；中间分别构造 960/1260 nt，使总产物为 1000/1300 bp。序列生成器独立检查仅一个完整结合位点；相同长度控制和重复位点控制在调用 Kit 前决定。
from_handoff 模板把实际读取的交接文档传入分析能力作绑定核对；不只读取后丢弃。预期结果 document 最终由统一封存导出 JSON，交给 Evidence 作为 artifact 登记。

## 共用函数与 Kit 自有缺口

S1b 已有并可用：biology.public.enumerate_primer_candidates, biology.public.predict_pcr_products, biology.public.find_binding_sites, biology.public.slice_material。
本轮新增的四个共享函数均有至少两个 Kit 的明确需求；使用矩阵见 shared-needs.json。
- 仍交该 Kit 实现：Regional alignment, assay discrimination and identity handoff parsing/output, only this Kit requires their domain decisions.

## 规格演练发现

完整原始校验结果由 tools/validate_kit_drafts.py 填入下方；语法通过不等于合同可执行。
<!-- VALIDATION-BEGIN -->
实际校验 10 份草稿；Schema 失败 2，A14 失败 0。
未解析 document schema_ref 等语义问题不冒充 JSON Schema 原生错误。Schema 失败原文如下：
```json
[
  {
    "kit": "genome-identity",
    "file": "drafts/genome-identity/templates/from_handoff.json",
    "schema": "pipeline-template-v1",
    "valid": false,
    "expected_invalid_probe": false,
    "schema_errors": [
      {
        "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not valid under any of the given schemas",
        "instance_path": [
          "steps",
          5,
          "inputs",
          "references"
        ],
        "schema_path": [
          "properties",
          "steps",
          "items",
          "properties",
          "inputs",
          "patternProperties",
          "^.*$",
          "oneOf"
        ],
        "validator": "oneOf",
        "context": [
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              5,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              0,
              "type"
            ],
            "validator": "type",
            "context": []
          },
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              5,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              1,
              "type"
            ],
            "validator": "type",
            "context": []
          },
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              5,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              2,
              "type"
            ],
            "validator": "type",
            "context": []
          },
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              5,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              3,
              "type"
            ],
            "validator": "type",
            "context": []
          }
        ]
      }
    ],
    "a14_errors": []
  },
  {
    "kit": "genome-identity",
    "file": "drafts/genome-identity/templates/from_references.json",
    "schema": "pipeline-template-v1",
    "valid": false,
    "expected_invalid_probe": false,
    "schema_errors": [
      {
        "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not valid under any of the given schemas",
        "instance_path": [
          "steps",
          4,
          "inputs",
          "references"
        ],
        "schema_path": [
          "properties",
          "steps",
          "items",
          "properties",
          "inputs",
          "patternProperties",
          "^.*$",
          "oneOf"
        ],
        "validator": "oneOf",
        "context": [
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              4,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              0,
              "type"
            ],
            "validator": "type",
            "context": []
          },
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              4,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              1,
              "type"
            ],
            "validator": "type",
            "context": []
          },
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              4,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              2,
              "type"
            ],
            "validator": "type",
            "context": []
          },
          {
            "message": "[{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not of type 'object'",
            "instance_path": [
              "steps",
              4,
              "inputs",
              "references"
            ],
            "schema_path": [
              "properties",
              "steps",
              "items",
              "properties",
              "inputs",
              "patternProperties",
              "^.*$",
              "oneOf",
              3,
              "type"
            ],
            "validator": "type",
            "context": []
          }
        ]
      }
    ],
    "a14_errors": []
  }
]
```

合同/运行语义发现：
```json
[
  {
    "kit": "genome-identity",
    "issue": "K1",
    "file": "drafts/genome-identity/capabilities/analyze_assay.json",
    "message": "schema_ref is not in the existing local schema registry: identity-handoff-v1"
  },
  {
    "kit": "genome-identity",
    "issue": "K1",
    "file": "drafts/genome-identity/capabilities/analyze_assay.json",
    "message": "schema_ref is not in the existing local schema registry: identity-expected-results-v1"
  },
  {
    "kit": "genome-identity",
    "issue": "K1",
    "file": "drafts/genome-identity/capabilities/compare_regions.json",
    "message": "schema_ref is not in the existing local schema registry: region-comparison-v1"
  },
  {
    "kit": "genome-identity",
    "issue": "K1",
    "file": "drafts/genome-identity/capabilities/read_handoff.json",
    "message": "schema_ref is not in the existing local schema registry: identity-handoff-v1"
  },
  {
    "kit": "genome-identity",
    "issue": "K3",
    "file": "drafts/genome-identity/templates/from_handoff.json",
    "message": "A3 permits one source/step/artifact/literal reference, not an ordered array of material references: assay.references"
  },
  {
    "kit": "genome-identity",
    "issue": "K3",
    "file": "drafts/genome-identity/templates/from_references.json",
    "message": "A3 permits one source/step/artifact/literal reference, not an ordered array of material references: assay.references"
  },
  {
    "kit": "genome-identity",
    "issue": "K5",
    "file": "prompts/s5b-genome-identity.md",
    "message": "The new handoff describes primer_pair without its internal type and does not distinguish no product from unresolved multiple products when product_bp is null. Old schema_version/references-dict/rows files are a different protocol."
  }
]
```
<!-- VALIDATION-END -->

已验证：只读源文件/行数与实际草稿校验范围。模拟：合成负例计划与本轮共享纯函数。
未做：Kit 代码、Kit 端到端、封存/verify、湿实验、观察真实性验证。官方 GitLab CI 未执行；GitHub CI 未运行。
