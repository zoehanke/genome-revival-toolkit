# Revival Evidence 迁移盘点与规格演练

草稿，未实现 Kit 代码，未经人工审核。Kit 工作区和 kits/ 目录未修改。
旧工作区 HEAD 无 kits/；下面的 Kit 源码只读自 Git 对象 bf90910e5b0e67985aa37db4e0b8507cbc24f2b4。
通用 Core 源码分别固定提交，不执行或 import 旧程序。模板/声明仅作规格演练，不能据此称为可运行 Kit。

## 旧代码清单

| 文件 | 提交 | 文件行数 | 逐函数行数 | 迁移处理 |
|---|---|---:|---|---|
| `genome-revival-toolkit/kits/evidence/scripts/__init__.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 1 | 无函数 | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/evidence/scripts/entry.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 11 | run 9..11 (3): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/evidence/scripts/hooks.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 4 | references 2..4 (3): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/evidence/scripts/predictions.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 104 | read_expected_results 9..36 (28): 保留显式文件/参考绑定原则；按新交接形状重写，丢弃旧 Trace 与旧 schema_version 协议; read_bound_observations 39..46 (8): 保留显式文件/参考绑定原则；按新交接形状重写，丢弃旧 Trace 与旧 schema_version 协议; observe_reported_bands 49..54 (6): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _assessment 57..72 (16): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology; compare_expected 75..104 (30): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology | extract_domain_only_discard_orchestration |
| `genome-revival-toolkit/kits/evidence/scripts/presentation.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 17 | format_comparison 6..7 (2): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; summary 9..10 (2): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接; fact_text 12..17 (6): 丢弃旧入口/钩子/呈现/输出外壳；新模板与公共导出承接 | discard_framework |
| `genome-revival-toolkit/kits/evidence/scripts/workflow.py` | `bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 158 | conclusion_rows 16..20 (5): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology; read_observations 23..29 (7): 只保留必要领域片段；旧类型、运行器、血统和 I/O 外壳不迁移; _count 32..44 (13): 保留领域算法/有限决策，重写输入输出；只服务一个 Kit 的判断不搬入 biology; run_evidence 47..158 (112): 丢弃流程/呈现/手工埋点；需要的科学分支由新能力表逐项承接 | extract_domain_only_discard_orchestration |

依据：spec/MIGRATION-MAP.md §6、§7、§8。entry/hooks/presentation/旧运行器与手工埋点丢弃；
workflow 文件只拆取科学判据、局部计算与交接绑定，绝不复制流程外壳。旧源码行数不是规则记录数。

## 新能力表

声明文件是完整 capability-v1 草稿。source.implemented_in 是未来目标模块，不存在实现，不作已导出/已运行声明。

| id / role / granularity | inputs | params | outputs / output_role | effects | step_checks / final_checks / model | biology 与剩余工作 |
|---|---|---|---|---|---|---|
| `evidence.parse_observations` / ACTION / atomic | `[{"name":"file","type":"artifact","required":true,"constraints":{},"description":"file"}]` | `{"type":"object","properties":{"id_prefix":{"type":"string"}},"required":[],"additionalProperties":false}` | `[{"name":"observations","type":"document","output_role":"analysis","schema_ref":"observation-table-v1"}]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | 无共享生物函数；保留领域计算独立性; 仍缺：CSV ID completion, unknown counts, finite rule evaluation, observation/prediction matching and bounded conclusions; no biology calculations. |
| `evidence.assess_observations` / ACTION / atomic | `[{"name":"observations","type":"document","required":true,"constraints":{},"description":"observations","schema_ref":"observation-table-v1"},{"name":"expected_results","type":"artifact","required":false,"constraints":{},"description":"expected results"}]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[{"name":"assessment","type":"document","output_role":"analysis","schema_ref":"revival-assessment-v1"}]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[{"check":"evidence.check_record_consistency"}],"model":null}` | 无共享生物函数；保留领域计算独立性; 仍缺：CSV ID completion, unknown counts, finite rule evaluation, observation/prediction matching and bounded conclusions; no biology calculations. |
| `evidence.check_record_consistency` / CHECK / atomic | `[]` | `{"type":"object","properties":{},"required":[],"additionalProperties":false}` | `[]` | `["reads_files"]` | `{"step_checks":[],"final_checks":[],"model":null}` | 无共享生物函数；保留领域计算独立性; 仍缺：CSV ID completion, unknown counts, finite rule evaluation, observation/prediction matching and bounded conclusions; no biology calculations. |

### 每个能力的 does_not_establish

- `evidence.parse_observations`: Experimental success; Functional revival; Authenticity of submitted observations; Whole-genome identity or elimination.
- `evidence.assess_observations`: Experimental success; Functional revival; Authenticity of submitted observations; Whole-genome identity or elimination.
- `evidence.check_record_consistency`: Experimental success; Functional revival; Authenticity of submitted observations; Whole-genome identity or elimination.

## 知识与来源

旧 JSON 规则 5 条；有来源标记 5；缺失 0。缺失清单：无。
新 rule-v1 草稿 6 条，均为 draft/unverified。旧 verified 标记不继承，没有填写审核人或核验回执。
有来源表示旧数据含可追溯来源，不表示此轮联网核实或科学结论成立。来源分类规范化见 source-audit.json。

| 旧规则文件 / 提交 | 文件物理行数 | 规则记录数 | 有来源 / 缺来源 |
|---|---:|---:|---|
| `genome-revival-toolkit/kits/evidence/rules/conclusions.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 33 | 2 | 2 / 0 |
| `genome-revival-toolkit/kits/evidence/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4` | 5 | 3 | 3 / 0 |
两条功能/全基因组结论真值表来自旧项目契约；仅支持项目输出边界，不是生物学充分证据。
另有一条控制组出菌落策略从实际旧代码分支数据化；缺来源探针是新增演练负例，不计入旧规则缺失数。

| 新规则 | source_class | citation / locator | supports / does_not_support |
|---|---|---|---|
| `evidence.missing-is-unknown` | project_contract | scripts/workflow.py:_count and group normalisation / genome-revival-toolkit/kits/evidence/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Missing counts or denominators remain unknown, not zero."],"does_not_support":["Experimental success or biological function."]} |
| `evidence.controls-and-conflicts` | project_contract | scripts/workflow.py:run_evidence findings / genome-revival-toolkit/kits/evidence/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Keep submitted controls and contradictory sample/reference records explicit."],"does_not_support":["Experimental success or biological function."]} |
| `evidence.bounded-conclusions` | project_contract | scripts/workflow.py:run_evidence conclusions and checked_scope / genome-revival-toolkit/kits/evidence/rules/scope.json@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Local submitted observations do not prove whole-genome elimination or functional revival."],"does_not_support":["Experimental success or biological function."]} |
| `evidence.functional-revival-scope` | project_contract | specs/genome-revival-toolkit.md: supported scope and evidence limits / specs/genome-revival-toolkit.md: supported scope and evidence limits@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Colony growth and selected markers alone do not establish donor-dependent restoration, exclude recipient growth, or identify the causal route."],"does_not_support":["Sufficient evidence of functional revival or genome-wide elimination."]} |
| `evidence.whole-genome-elimination-scope` | project_contract | specs/genome-revival-toolkit.md: local genetic assessment boundary / specs/genome-revival-toolkit.md: local genetic assessment boundary@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["Negative selected-region tests do not cover the complete genome."],"does_not_support":["Sufficient evidence of functional revival or genome-wide elimination."]} |
| `evidence.control-outgrowth` | project_contract | scripts/workflow.py:run_evidence control-colony branch / genome-revival-toolkit/kits/evidence/scripts/workflow.py@bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 | {"supports":["The legacy assessment policy flags a reported positive inactivated-donor control."],"does_not_support":["Experimental success or biological function."]} |

## 模板与构造答案

模板：`observations_only.json`, `compare_predictions.json`。
Goal 先登记真实输入文件；模板参数绑定已登记的 source ID、goal_digest 和 target ID，不把文件路径或 DNA 字符串伪装成材料来源。
以下输入与答案在实现前由构造/手算确定，不能用旧版或待测代码生成答案。

## 要写的负例及正对照

| 负例 | 输入构造 | 预期来源与结果 |
|---|---|---|
| csv_missing_id | CSV has group,colonies but no id; two rows have the same group. | Assign distinct stable IDs and record that IDs were program-supplied; do not claim they were measured. |
| missing_not_zero | One group count is blank and another explicit count is zero. | Blank remains unknown and is not equal to zero; no invented total or negative experiment. |
| control_outgrowth | Fusion group reports 9 colonies, inactivated donor control reports 31. | Control contradiction remains visible; functional revival stays INSUFFICIENT. |
| counts_only | Provide colonies but no PCR or genetic evidence. | Functional revival is INSUFFICIENT and unperformed tests remain listed. |
| source_missing | Remove source metadata from an otherwise well-formed draft rule. | Keep draft/unverified outside loadable knowledge; actual rule-v1 validation fails rather than fabricate source. |

合成构造路线：手写融合组 9、对照组 31 的 CSV；另写空计数与显式 0 两行，并删除 id 表头。结论来自有限真值表与构造的控制状态，不从菌落计数推导功能复活。

## 共用函数与 Kit 自有缺口

S1b 已有并可用：无 DNA 算法依赖。
本轮新增的四个共享函数均有至少两个 Kit 的明确需求；使用矩阵见 shared-needs.json。
- 仍交该 Kit 实现：CSV ID completion, unknown counts, finite rule evaluation, observation/prediction matching and bounded conclusions; no biology calculations.

## 规格演练发现

完整原始校验结果由 tools/validate_kit_drafts.py 填入下方；语法通过不等于合同可执行。
<!-- VALIDATION-BEGIN -->
实际校验 14 份草稿；Schema 失败 1，A14 失败 1。
未解析 document schema_ref 等语义问题不冒充 JSON Schema 原生错误。Schema 失败原文如下：
```json
[
  {
    "kit": "revival-evidence",
    "file": "drafts/revival-evidence/probes/source-missing.json",
    "schema": "rule-v1",
    "valid": false,
    "expected_invalid_probe": true,
    "schema_errors": [
      {
        "message": "'source_class' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'citation' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'locator' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'retrieved_at' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'content_ref' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'archive_note' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'supports' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      },
      {
        "message": "'does_not_support' is a required property",
        "instance_path": [
          "source"
        ],
        "schema_path": [
          "properties",
          "source",
          "required"
        ],
        "validator": "required",
        "context": []
      }
    ],
    "a14_errors": []
  },
  {
    "kit": "revival-evidence",
    "file": "drafts/revival-evidence/probes/partial-placeholder.json",
    "schema": "pipeline-template-v1",
    "valid": false,
    "expected_invalid_probe": true,
    "schema_errors": [],
    "a14_errors": [
      {
        "message": "A14 requires a whole-string placeholder with a valid lowercase name.",
        "instance_path": [],
        "schema_path": [],
        "validator": null,
        "context": []
      }
    ]
  }
]
```

合同/运行语义发现：
```json
[
  {
    "kit": "revival-evidence",
    "issue": "K1",
    "file": "drafts/revival-evidence/capabilities/assess_observations.json",
    "message": "schema_ref is not in the existing local schema registry: observation-table-v1"
  },
  {
    "kit": "revival-evidence",
    "issue": "K1",
    "file": "drafts/revival-evidence/capabilities/assess_observations.json",
    "message": "schema_ref is not in the existing local schema registry: revival-assessment-v1"
  },
  {
    "kit": "revival-evidence",
    "issue": "K1",
    "file": "drafts/revival-evidence/capabilities/parse_observations.json",
    "message": "schema_ref is not in the existing local schema registry: observation-table-v1"
  },
  {
    "kit": "revival-evidence",
    "issue": "K6",
    "file": "drafts/revival-evidence/capabilities/assess_observations.json",
    "message": "D12 permits an ACTION evaluator to consume frozen knowledge, but D3 exposes knowledge(pack) only on CHECK ctx.view; no ACTION frozen-knowledge access contract is specified."
  },
  {
    "kit": "revival-evidence",
    "issue": "K2",
    "file": "drafts/revival-evidence/probes/source-missing.json",
    "message": "Draft/unverified does not waive mandatory source fields. Missing-source rows need an explicitly quarantined delivery policy, not invented citations or a loadable knowledge claim."
  },
  {
    "kit": "revival-evidence",
    "issue": "K5",
    "file": "prompts/s5b-genome-identity.md",
    "message": "The new handoff describes primer_pair without its internal type and does not distinguish no product from unresolved multiple products when product_bp is null. Old schema_version/references-dict/rows files are a different protocol."
  }
]
```
<!-- VALIDATION-END -->

已验证：只读源文件/行数与实际草稿校验范围。模拟：合成负例计划与本轮共享纯函数。
未做：Kit 代码、Kit 端到端、封存/verify、湿实验、观察真实性验证。官方 GitLab CI 未执行；GitHub CI 未运行。
