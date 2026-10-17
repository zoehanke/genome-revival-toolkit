# Genome Revival Toolkit 新版构建规格：合并底稿 v0.1

- 日期：2026-10-16　状态：**讨论用底稿，未经用户审定，未实现，没有任何代码**
- 来源：`archive/proposals/claude-20261016`（下称 C）与 `archive/proposals/gpt-20261016`（下称 A，即 astra）合并而成。骨架以 A 为底（执行与检查的核心机制），并入 C 的结构护栏、事件目录、迁移表与自证封存包；已吸收用户 2026-10-16 的决定。每章末尾的「来源」说明取自哪一份、哪些是合并时新定的（M）。
- 之后只在这一份底稿上讨论。合并的取舍见 `MERGE-LEDGER.md`，待用户确认的默认值见 `OPEN-ITEMS.md`，迁移见 `MIGRATION-MAP.md`。
- 证据级别：**[已读]** 读过源码或文档；**[已量]** 脚本数过；**[推断]** 由调用关系推出；**[未核实]** 没看；**[设计]** 本稿的新决定，尚无实现验证。
- 术语约定：本稿只使用 §1 的词表。旧设计的词（如五个检查阶段、评估器目录、交付类别、`PLAN` 与 `DOMAIN` 范围）已全部退役，只在 `MERGE-LEDGER.md` 的「旧词对照」里出现。

---

## 0. 总览（先看这里）

**结论：一条主线，一本日志，其余都是主线的部分或视图。**

> 用户的话 → **目标** → **流水线**（动手前写好，执行中只追加修订）→ **执行**（每步留下不可改的事实）→ **检查与交付**（一个系统）→ **封存包**
> 以上每一步只往同一本只追加、哈希链接的**日志**里写事件。记录（Evidence Trace）、报告、运行卡片都是日志的**视图**。

| 部分 | 是什么 | 不是什么 |
|---|---|---|
| 目标 Goal | 用户要什么；哪些要求程序能检查、哪些不能（明列为未绑定） | 不是做法 |
| 流水线 Pipeline | 宿主 AI 动手前写好的步骤；执行中只能追加修订 | 不含任何检查字段 |
| 能力 Capability | 一步能做的事，只有一种声明，两种角色：**做事**（ACTION）与**检查**（CHECK） | 不自己调用别的能力（要经上下文） |
| 编排层 | 唯一指挥者：接纳计划 → 逐步执行 → 请求检查 → 封存 | 不含科学算法 |
| 调用器 | 所有能力（含检查）的唯一调用口 | 不判断对错 |
| 检查与交付 | 三个时刻的检查加封存，同一个系统 | 不被计划增删 |
| 日志 | 哈希链接的事件日志，唯一真相来源，**不能关闭** | 不是可选项 |
| 记录 | 日志的只读视图：事实与声明分层，运行卡片 | 不判断，不证明结论正确 |
| Kit | 可插拔的包：能力、知识、模板、文案 | 不带入口、流程代码、报告渲染 |
| 宿主 AI | 唯一会思考的一方 | 不被强制走正式路线；不走只会被如实标注「未封存」 |

**九个「唯一」，每个都有自动测试守着**

| 唯一的…… | 守它的测试 |
|---|---|
| 一条流（先写计划再执行，哪怕只调一个工具） | INV-P1 INV-H1 |
| 一本日志（状态、证据、封存依据同源） | INV-E1 INV-E2 |
| 一种可调用单元（能力；检查也是能力） | INV-C1 INV-C6 |
| 一种裁决形状 | INV-A1 INV-A2 |
| 一个入口（封闭动词表） | INV-H1 |
| 一张词表 | INV-V1 INV-V2 |
| 一处算哈希 | INV-I1 |
| 一处读配置 | INV-X1 |
| 一个手写的版本来源 | INV-W2 |

**威胁模型（本稿一切取舍的前提）**：要防的是**宿主 AI 或开发 AI 的疏忽、偷懒、顺手编造**；**不防蓄意攻击者**。因此：不做代码沙箱（写进展望）；人工审核按「标注」处理，不阻断，也不做密码学签名；不声称能验证「审核的人是不是真人」。结构测试与独立答案防的是「为让测试变绿而牺牲结构」。

**防御预算（与威胁模型同级）**：只防三类坏事——**科学结论错误、序列外发、检查或历史被静默改写**。其余的防护，写之前先过三问：①这个坏情况在本项目的真实使用里发生过，或经常发生吗？②发生后果是重（结论错、外发、静默改写）还是轻（这次重跑即可）？③防它的代价（代码、新概念、测试）明显小于后果吗？有一问答「否」，就**不写防护代码**，只在 `OPEN-ITEMS.md` 的「已知不防」清单里写一行。常见的使用错误（路径、编码、重复提交）只给清楚的错误提示，不做恢复机制；需要恶意或巧合才发生的情形不防。**概念预算**：新增一个词、对象、字段或检查，必须同时删掉或合并一个。**汇报框架优先**：任何文档或汇报的第一屏只写「结构是什么、这次改了哪里的结构、要决定什么」（DEV-14）。

**检查在流里出现的三个时刻**（每个时刻一个名字，全稿统一）

| 时刻 | 中文名 | 标识 | 查什么 | 谁来跑 | Kit 在能力声明里的对应项 |
|---|---|---|---|---|---|
| 提交或修订计划时 | **接纳校验** | `admission` | 这份计划写得对不对、能不能跑 | 底盘，核心规则固定，Kit 不能放宽或删除 | 接纳契约（`inputs`/`params`/`outputs`） |
| 每步完成时 | **步骤自检** | `step` | 这一步的输出合不合它自己的声明；宿主追加的断言成不成立 | 能力自己出结果，底盘核对 | `step_checks` |
| 判定与封存时 | **封存终检** | `final` | 成果能不能交付；封存时对暂存包重新检查，不信任之前的结果 | 底盘按**实际用到的能力**推出必过项，经调用器运行 | `final_checks` |

**一次任务的流**

1 建运行（记环境与目录快照）→ 2 提交目标 → 3 提交流水线（接纳校验，不执行任何能力）→ 4 逐步执行（经调用器）→ 5 步骤自检与断言，失败则暂停 → 6 追加修订（已开始的步骤冻结，理由先于新步骤入日志）→ 7 判定（封存终检的试跑，可选）→ 8 封存（暂存、重检、清单、原子重命名）→ 9 复核（封存包可离线核对）→ 10 出运行卡片（只读视图）。

**诚实边界**：日志的哈希链能发现意外损坏与局部改写，不能阻止对整台机器有完全控制权的写入者整体重写，除非把头哈希发布到机器之外；封存是「经过这些检查」，不是「科学上正确」，更不是「湿实验成功」；官方 GitLab 没有 CI 执行器，文档一律写「官方 GitLab CI 未执行」。

---

## 1. 词表（权威版本；机器可读版是 `vocab.json`，D14）

| 类别 | 取值 |
|---|---|
| 检查时刻 `moment` | `admission` `step` `final` |
| 裁决结果 `outcome` | `PASS` `FAIL` `UNKNOWN`（没能判断：证据不足、依赖缺失、检查本身失败）`NOT_APPLICABLE` |
| 裁决范围 `scope` | `content_model` `preparation_model` `file` `user_goal` |
| 裁决出具者 `issuer` | `check_capability` `tool_self_report` `host_expectation` |
| 能力角色 `role` | `ACTION` `CHECK` |
| 输出角色 `output_role` | `construct` `component` `primer_set` `analysis` |
| Run 状态 | `PLANNED` `RUNNING` `HALTED` `COMPLETED` `ABANDONED` |
| Step 状态 | `PENDING` `RUNNING` `COMPLETED` `FAILED` |
| 副作用 `effects` | `pure` `reads_files` `writes_files` `external_process` |
| 规则生命周期 `status` | `draft` `active` `retired` |
| 来源核验 `verification_status` | `unverified` `verified` |
| 审核状态 `review` | `none` `draft` `reviewed` `stale` |
| 行为者 `actor` | `program` `ai_host` `human` `unknown` |
| 理由来源 `origin` | `plan_declared` `original_statement` `organized_summary` `later_interpretation` `unknown` |
| 关系依据 | `hash_equal`（实线）`declared`（虚线） |
| 输入来源 `input_origin` | `user_file` `researcher_observation` |
| 规则来源类 `source_class` | `literature` `official_method` `project_contract` `lab_protocol` `database_record`（`AI` `internet` `latest` 一律拒绝） |
| 实验室状态标签 | `PLANNED` `NOT_PERFORMED` |
| 错误类别 | `INVALID_INPUT` `CAPABILITY_FAILURE` `ENVIRONMENT` `POLICY` `INTEGRITY` `INTERNAL` |
| 退出码 | `0` 成功；`1` 任何错误（类别写在回执信封里）；`10` 被必过项拒绝（不是错误） |

**可信度的三个问题，各用一个词，互不混用**：规则或模板还在不在用？看 `status`。来源核验过吗？看 `verification_status`。人审过吗？看 `review`。没有「成熟」这个词；方法是否验证过，靠独立答案测试，不设字段。

**Kit 的领域词不进本词表**：例如 Revival Evidence 的结论状态 `SUPPORTED` `INSUFFICIENT` `CONTRADICTED` `NOT_TESTED` 属于 Kit 的数据类型，与裁决结果是不同概念，写在该 Kit 的文案与文档里并分开。

---

## D1 总体分层与依赖方向

**结论**：十个模块，严格分层，只许向下依赖；依赖规则写成机器可读的契约，由测试自动检查。**只有编排层同时认识执行与检查**；能力与 Kit 只看得见公开的 `kernel.public` 与 `biology.public`。

**问题**：旧代码出现 `workflow ↔ composite_pipeline`、`registry ↔ workflow` 的循环引用，一个 Kit 的入口回头调用旧运行器 [已读]；旧的「计划」阶段就把整条流水线跑完（`CompositePipelineHandler.plan()` 调用 `run_pipeline_steps`，`core/handlers/composite_pipeline.py:222–229`）[已读，A 发现并经 C 核实]；两个交付入口前置条件不同（`runtime_gate.finalize` 信任一份已记录的验证结果，`deliver_result` 重新计算）[已读]。

**决定**

| 层 | 模块 | 职责（一句话） | 允许依赖 |
|---|---|---|---|
| L0 | `kernel` | 标识与哈希、规范化 JSON、词表、错误（Problem）、模式、材料值类型、裁决类型与构造函数、端口（Protocol：`Invoker`）、`kernel.public`（给能力与 Kit 的公开面） | 无（只用标准库） |
| L1 | `biology` | **共享算法层**：无状态的纯领域计算（序列操作、PCR 与连接模拟、Tm、PAM 扫描、格式读写），做事与检查共用；公开面 `biology.public` | kernel |
| L1 | `storage` | 日志（事件、追加、读取、哈希链、锁、尾部恢复）与内容存储（只写一次、读时校验） | kernel |
| L1 | `knowledge` | 规则与来源的数据模式、加载、审核状态读取 | kernel |
| L2 | `catalog` | 能力与 Kit 的声明登记、Kit 发现与清单校验、选择器解析、目录快照构建；**只读元数据，不 import 任何实现** | kernel、knowledge |
| L2 | `capabilities` | 内置能力的实现（做事的与检查的），薄壳调用 `biology` | kernel.public、biology.public、knowledge |
| L3 | `engine` | 目标、流水线模型与规范化、接纳校验、执行器、调用器实现、修订、由日志推出状态 | kernel、storage、catalog |
| L4 | `assurance` | 必过项推导、判定、暂存、封存、复验、标签、审核状态显示；**经 `kernel` 的 `Invoker` 端口运行检查，不 import engine** | kernel、storage、knowledge、catalog |
| L4 | `record` | 日志的视图：事实与关系投影、声明层、运行卡片、报告、文案资源 | kernel、storage（只读接口） |
| L5 | `application` | **编排层 `RunService`**：组合 engine、assurance、record，把调用器注入检查层；写 `run.*` 事件；同一层含 Python API、命令行、`describe`、配置 | engine、assurance、record、catalog、storage、knowledge、kernel |
| — | `kits/<name>/`（包外） | Kit 包 | 仅 `kernel.public`、`biology.public` 与它自己的包 |

*依赖契约 `contracts.toml`（节选）*

```toml
[layers]
order = ["kernel","biology|storage|knowledge","catalog|capabilities","engine","assurance|record","application"]

[allow]
"biology"      = ["kernel"]
"storage"      = ["kernel"]
"knowledge"    = ["kernel"]
"catalog"      = ["kernel","knowledge"]
"capabilities" = ["kernel.public","biology.public","knowledge"]
"engine"       = ["kernel","storage","catalog"]
"assurance"    = ["kernel","storage","knowledge","catalog"]
"record"       = ["kernel","storage.read"]
"application"  = ["kernel","storage","knowledge","catalog","engine","assurance","record"]

[kit_allow]
"*" = ["dna_design_core.kernel.public","dna_design_core.biology.public"]   # 加上 Kit 自己的包

[forbid_patterns]
"os.environ" = ["application/config.py"]
"hashlib"    = ["kernel/ids.py"]
"print("      = ["application/cli.py"]
```

*规则 DEP-1…DEP-13*
- DEP-1 `kernel` 不 import 本项目任何其他模块。DEP-2 `biology`、`storage`、`knowledge` 只 import `kernel`。DEP-3 `catalog` 只 import `kernel`、`knowledge`，**不 import 任何能力实现**。
- DEP-4 `capabilities` 只 import `kernel.public`、`biology.public`、`knowledge`；**不得 import engine、assurance、record、application**。需要「调用别的能力、写文件、跑外部程序」时经注入的 `ctx`。
- DEP-5 `engine` 经调用器按引用加载实现，**不静态 import 任何具体能力**。DEP-6 `assurance` 运行检查只经 `kernel` 里的 `Invoker` 端口，**不 import engine**。DEP-7 `record` 只读日志与内容存储，没有写入口。
- DEP-8 **只有 `application` 同时 import engine 与 assurance**。DEP-9 Kit 只许 import `kernel.public`、`biology.public` 与自己的包，不得 import 其他 Kit、引擎、检查层内部或旧版代码。
- DEP-10 `os.environ` 只在 `application/config.py`。DEP-11 `hashlib` 只在 `kernel/ids.py`。DEP-12 库代码不得 `print`，只有 `application/cli.py` 写标准输出。DEP-13 宽泛的 `except Exception` 只允许出现在两处：`engine` 的调用器边界（把能力与检查的异常规范成失败记录）和 `application` 的命令行顶层。

*谁能写日志*：只有 `engine`、`assurance`、`application` 的白名单函数，以及 `storage` 的尾部恢复例程（INV-E1，写权限矩阵见附录 E）。

**不采用**：不设依赖契约、靠评审（旧系统已证明不可靠）；把 engine 与 assurance 合成一层（执行会影响判定）；让 engine 反向 import assurance 来出裁决（旧设计的缺口）；检查与做事各一套声明与注册表（检查器够不到算法，会重写一遍，正是旧 Kit 里 `gates.py` 与流程里重复检查的病根）。

**失败时怎么办**：契约测试失败即构建失败；只能改代码，或修改规格并写决策记录（INV-F7）。

**怎么测**：`ast` 解析所有 `src/` 与 `kits/` 的 import，对照契约（INV-L1、INV-L2）；环检测（INV-L3）；动态探针：运行时给调用器与封存函数装 spy，确认所有能力调用都经调用器、只有一处能创建封存包（INV-L4）；**契约充分性测试**：规格正文要求的跨模块调用必须是契约允许的子集（INV-L5）；扫描器自测：把故意违规的模块加入副本，扫描必须报错。

**来源**：模块划分与契约 C-D1；`biology` 分层、调用器唯一、应用层（编排）、动态探针 A-D1；检查层经端口运行检查、契约充分性测试、`catalog` 与 `capabilities` 的边界 M。依据：[已读] 旧循环引用与两个交付入口；[设计] 新依赖图。

---

## D2 目标（Goal）

**结论**：目标是一份「用户要什么」的文档：逐字保存宿主报告的用户原话，列出**程序能检查的约束**（每条指出原话里的依据），声明要产出的**目标物**（用输出角色表示），并把**程序检查不了的意图明列为「未绑定」**。目标只能追加版本；执行开始后改目标会被醒目标记。

**问题**：旧系统里「用户要什么」散落在要求字典、目标条目、任务表、Kit 请求、记录的决策里，没有总对象 [已读]；好想法要保留：`source_quote` 必须逐字出现在原话里，未绑定任何可检查约束的条目被标为 `MISSED`，完成报告永远写 `original_task_verified: false` [已读]。

**决定**

由宿主在写流水线**之前**提交（可以与流水线一同提交，但先于任何执行）。

```json
{
  "schema": "goal-v1", "version": 1, "parent_digest": null,
  "original_request": "（宿主报告的用户原话，逐字）",
  "sources": [{"source_id": "vector", "path": "inputs/guide_plasmid.gb", "sha256": "…",
               "input_origin": "user_file", "declared": {"topology": "circular"}}],
  "declared_context": [{"id": "c1", "kind": "strain", "text": "宿主已整合潮霉素盒",
                        "origin": "ai_host", "basis_sources": []}],
  "targets": [{"id": "t1", "role": "construct", "required": true},
              {"id": "t2", "role": "primer_set", "required": true}],
  "constraints": [{"id": "k1", "check": "check.goal.components_present@1.0.0",
                   "params": {"components": [{"name": "spacer_new", "sequence": "…20nt…"}]},
                   "target": "t1", "source_quote": "换成这条 20 nt", "status": "active"}],
  "intents": [{"id": "i1", "text": "尽量避免和菌株已有抗性冲突", "source_quote": "…", "binds": []}]
}
```

- `goal_digest` 由程序对规范化文档计算，不由 AI 填写。
- **约束的 `origin` 与参数**：`origin` 由程序按 GOL-4 填写（原话逐字出现→`user_quoted`，否则→`host_derived`），请求里写了 `origin` 一律 `INVALID_INPUT`（防止宿主自称用户原话）；`constraints[].params` 在**提交目标时**就按该检查能力声明的 `params` 模式校验，不符 → `INVALID_INPUT`，不要拖到判定时才表现为 `UNKNOWN`。目标文档的模式错误，`recovery` 文案要指向 goal-v1，不是 pipeline-v1。
- **来源文件怎样进入运行**：`goal declare|amend --request` 的请求里，每个来源用 `from` 指向原文件（相对当前目录或绝对路径都可），代替文档里的 `path` 与 `sha256`。引擎把文件复制到 `inputs/<source_id>/<文件名>`，计算 `file_sha256`，写 `input.registered`，并把存入目标文档的 `sources[]` 补成 `path`（运行目录相对）与 `sha256`。**`from` 不写进目标文档、事件或任何文件**（不保存原绝对路径）；同一来源 id 再次提交内容不同的文件 → `INVALID_INPUT`。
- `targets[].role` 取自输出角色词表；一个目标物只能被**声明了同一输出角色**的输出满足。目标物是「要什么」，必过检查则由「实际产出什么」推导（D7），**宿主不能靠给输出贴低档标签来降低检查**。
- `constraints[].check` 指向一个**检查能力**，该能力的声明里 `evaluates_constraint: true`。初始约束种类：`topology`、`exact_sequence`、`components_present`、`components_absent`、`regions_unchanged`、`output_present`、`claim_reported`。Kit 可通过自己的检查能力新增种类，**不能改已有种类的含义**（同名即装载冲突）。
- `intents[]` 是自然语言意图；`binds` 为空即未绑定：程序不检查，只列在封存清单的 `not_verified` 与运行卡片「Not done」栏。
- `sources` 与 `declared_context` 是声明（带来源），不是事实，检查不得把它们当事实用。

*规则 GOL-1…GOL-8*
- GOL-1 修订追加新版本，旧版本留在日志。GOL-2 约束不能删除，只能标 `dropped` 并写原因，被丢弃的约束仍显示。GOL-3 第一个步骤开始后的修订置 `amended_after_start`，写进封存清单与运行卡片。
- GOL-4 `source_quote` 必须逐字出现在 `original_request` 中；否则该约束标 `origin: host_derived`，视图画虚线并注明「约束由宿主推导，非用户原话」。
- GOL-5 活动约束为 0，则 `check.goal.nonempty` 给 `UNKNOWN`，**阻止封存**。
- GOL-6 **`original_request` 是宿主报告的用户原话，系统无法证明那确是用户所说**；它列在运行卡片「Declared only」栏，文档与 Wiki 须写作「宿主转述的用户原话」。
- GOL-7 新版本目标的满足**不追溯关闭**旧版本未满足的条目，它们继续显示。GOL-8 目标物角色不可被计划降低；要换成别的角色只能走 `goal.amended`。

**不采用**：把目标塞进流水线（AI 改计划会顺手改目标）；目标用自由文本（不可检查）；允许静默删约束（最容易钻的空子）。

**失败时怎么办**：目标文档不合模式 → `INVALID_INPUT`，一次列出所有错误，run 停在 `PLANNED`，错误带 `recovery`。

**怎么测**：模式正反例；`source_quote` 逐字出现（含 Unicode、换行、全半角）；GOL-1…GOL-8 各一个属性或示例测试，尤其「约束 id 永不消失」的随机序列测试；每个约束种类的检查能力有 PASS/FAIL 夹具（D7、D18）。

**来源**：对象与 `source_quote`、模式、`dropped`、`amended_after_start` C-D2；目标物用角色表示、版本链语义、`host-reported` 的诚实表述 A-D2 与 M。依据：[已读] 旧 `requirements`、`goal_coverage`；[设计] 新对象。

---

## D3 能力（Capability）：唯一的可调用单元

**结论**：一切「一步能做的事」——原子工具、成熟方法、**检查**、格式导出、Kit 带来的任何东西——都是 `Capability`，**只有一种声明格式**。声明从代码里的装饰器导出，文档从声明生成。能力有两种**角色**：`ACTION`（做事）与 `CHECK`（检查，只读）。组合型能力只能经 `ctx.call` 调用别的能力。算法放在共享的 `biology`，做事与检查共用。

**问题**：旧系统有四套「能做的事」（工具、成熟方法、任务处理器、Kit），形状各不相同，调用靠硬编码参数名转换 [已读]；旧 Kit 里同一个判断在流程与门里各写一份 [已读]。

**决定**

*声明 `capability-v1`*（从代码中的 `@capability(...)` 与带类型注解的签名导出为 `resources/capabilities/*.json`，入库）

```json
{
  "schema": "capability-v1", "id": "cut_plasmid.replace_spacer", "version": "1.0.0",
  "role": "ACTION",
  "summary": "Replaces the 20 nt spacer, returns the new plasmid, a route plan and primers.",
  "effects": ["pure"], "deterministic": true,
  "inputs": [{"name": "vector", "type": "material", "required": true},
             {"name": "target", "type": "material", "required": true}],
  "params": {"type": "object", "additionalProperties": false, "required": ["spacer"],
             "properties": {"spacer": {"type": "string", "pattern": "^[ACGT]{20}$"}}},
  "outputs": [{"name": "product", "type": "material", "output_role": "construct"},
              {"name": "route", "type": "document", "schema_ref": "route-plan-v1", "output_role": null},
              {"name": "primers", "type": "document", "schema_ref": "primer-set-v1", "output_role": "primer_set"}],
  "step_checks": ["check.primer_quality"],
  "final_checks": [{"check": "cut_plasmid.check_direction"}, {"check": "cut_plasmid.check_pam"},
                      {"check": "cut_plasmid.check_vector_self_target"}],
  "model": "cut_plasmid.model_replace",
  "does_not_establish": ["Cleavage activity", "Editing efficiency", "Genome-wide off-target safety"],
  "source": {"algorithm_refs": [], "implemented_in": "grt_kit_cut_plasmid.capabilities:replace_spacer"},
  "owner": "kit:cut-plasmid"
}
```

*检查能力多出的字段*（`role: "CHECK"`）：`scope`（恰为四个范围之一）、`evaluates_constraint`（是否可作目标约束种类）、`offline`（只读封存包内容即可运行时为 true；`verify` 只重跑这类检查，其余在复验回执里标「未重跑」）、`fixtures`（`{"pass": 路径, "fail": 路径}`，**必填**）。检查能力的 `effects` 只能是 `pure` 或 `reads_files`。

*声明里与检查系统相连的三项，名字与检查的三个时刻一一对应*（Kit 对检查系统的**唯一入口**，详见 D11）

| Kit 在能力声明里的对应项 | 内容 | 对应哪个检查时刻 |
|---|---|---|
| **接纳契约**（对应 `admission`） | `inputs`（收什么）、`params`（设置）、`outputs`（给什么、交付哪种角色）；三项合称接纳契约，就是能力的函数签名 | 接纳校验：计划里用到它的步骤按契约查 |
| **`step_checks`**（对应 `step`） | 做完后它对自己的结果自检哪些项（结果标「工具自报」） | 步骤自检 |
| **`final_checks`**（对应 `final`） | 只要这个能力被用到，就必须通过的检查（本身也是能力） | 封存终检：并入必过项（D7） |

- **输入端口类型**：`material`、`materials`、`document`（带 `schema_ref`〔核心共享模式的 id〕**或**内联的 `schema`〔JSON Schema 对象，Kit 自己的文档类型〕，二选一）、`artifact`（文件）、`value`（标量或 JSON）。不再接受「字符串、路径、字典随便传」；文件进入系统只有两个入口：目标里的 `sources[]`（登记文件与来源；序列格式文件默认经格式加载器变成材料，其他文件用 `as: artifact` 以文件进入，由计划里的解析能力读取）或上一步输出的引用。内联 `schema` 随能力声明一起冻结进目录快照，**不需要另设模式注册表**，Kit 的贡献仍只有四样。`materials` 端口只接收上一步输出的 `materials` 端口（普通的步骤引用）；v1 的引用形式不提供「把多个来源或多个步骤的材料拼成一个列表」，需要多个材料时用多个固定的 `material` 端口。
- **输出 `Outcome`**（`kernel.public`）：`products`、`documents`、`artifacts`、`values`、`verdicts`（对自己结果的自检草稿，出具者记为 `tool_self_report`）、`unverified`（本次结果里没能核实的项，每项一句话加原因，如「筛选方案未知：基因型缺失」；记入 `step.completed`）。检查能力的 `Outcome` 只含 `verdicts`。
- **`output_role`**：输出端口声明自己交付的是哪种角色（`construct`、`component`、`primer_set`、`analysis`，或 `null` 表示仅中间产物）。**必过项由它推导，不由宿主选择**（D7）。
- **粒度**：`atomic`＝一个算法操作，不调用别的能力；`composite`＝内部有两个以上能力调用或有搜索与分支，**只能**用 `ctx.call("id", inputs=…, params=…)`。`ctx.call` 自动在日志里产生带 `parent` 的子事件，经同一个调用器，内部操作因此自动留痕（回放模式下不写事件，见 D7）。
- **独立预期模型 `model`**：可选，指向一个**独立实现**的「预期产物」能力（保留旧处理器 `recompute` 的双重计算思想）；声明了 `model` 就**自动**把 `check.model_agreement` 并入必过项（不必再写进 `final_checks`），它逐位比较两条路径的结果，两条路径在代码上必须相互独立。**约定**：模型能力从原能力那次调用的记录里**按名字**取它声明要的输入与参数（名字必须在原能力里存在，否则声明装载失败）；比较的输出端口是两者共有的名为 `product` 的 `material` 端口（原能力没有 `product` 端口就不能声明 `model`）；比较内容是序列、拓扑与末端，**不比较注释**（注释由别的检查负责）。**v1 的边界**：`model` 只对作为**计划步骤**直接调用的能力生效；被 `ctx.call` 嵌套调用的能力即使声明了 `model`，嵌套调用记录里没有参数（`call.recorded` 只有输入标识与输出），无法重建模型的输入，所以 `check.model_agreement` 对这种调用报 `UNKNOWN`（阻止封存），**绝不报 `PASS`**；Kit 作者把带 `model` 的能力只当计划步骤用。`final_checks` 只写这个能力**额外**要求的检查；基础档位已有的检查（D7）不必重复，重复也无害（必过项取并集）。
- **上下文 `ctx`**：`call`、`workdir`、`run_external`、`config`、`knowledge(pack)`；`knowledge(pack)` 所有能力可用、只读，返回的是**本次运行的目录快照里冻结的**知识包（读出后核对摘要，与快照不符则 `INTEGRITY` 失败）；能力只能读自己所在 Kit 的知识包，核心能力可读核心知识包。检查能力另有只读视图 `ctx.view`（`candidate`、`material(id)`、`document(id)`、`steps()`、`events(filter)`、`goal`、`pipeline`）。需要算法时，**检查与做事一样直接 import `biology.public`**，不再重写。
- **副作用**：`pure`、`reads_files`、`writes_files`（只许写 `ctx.workdir`）、`external_process`（只经 `ctx.run_external`，记录可执行文件版本与内容哈希、有超时）。
- **命名与版本**：`namespace.verb_noun`；核心命名空间 `format`、`seq`、`primer`、`pcr`、`restriction`、`assembly`、`mutagenesis`、`crispr`、`verify`、`check`；Kit 用自己的命名空间。同名且内容不同即装载失败，不覆盖（同 id 同内容只装载一份，见 KIT-2）。**检查角色（`CHECK`）的能力 id 以 `check` 开头**（核心用命名空间 `check.`，Kit 用 `<命名空间>.check_<名字>`）；**做事角色（`ACTION`）的 id 不以 `check` 开头**，以免混淆——例如 Kit 里读出间隔序列状况的分析叫 `inspect_guide`（做事），判定方向是否正确的叫 `check_direction`（检查）。语义化版本，存储的流水线一律记 `id@精确版本`（提交时可省略版本，由规范化补上），写了版本而不符时报 `CAPABILITY_VERSION_MISMATCH`，不静默代用。
- **可用性**：`requires_runtime`（Python 包、可执行文件）由 `catalog` 探测；不可用的能力在 `describe` 里列出原因；接纳校验在**执行前**就发现。

**不采用**：声明与代码各写一份再人工同步（旧系统已因此对不上数字）；检查另设一套声明、注册表与接口（检查够不到算法，会重写一遍）；每个 Kit 一个任意的 `run(inputs)` 入口（绕开计划与调用器）；把成熟方法继续当另一种东西。

**失败时怎么办**：能力抛 `ToolkitError`（带类别与 `recovery`），由调用器边界规范成失败记录（D14）；输出不符声明 → `CAPABILITY_OUTPUT_INVALID`；未声明的异常 → `CAPABILITY_INTERNAL` 并保留类型名；检查能力抛异常 → 该必过项算 `UNKNOWN` 并附失败记录，不是 `FAIL`。

**怎么测**：每个能力至少一个**独立答案**测试（构造出来的，或手工核算并注明方法与来源，不得用待测能力生成答案）；契约测试（声明↔签名↔输出形状）；`deterministic:true` 的能力同输入两次运行输出相同；序列操作的随机属性测试；每个检查能力的 PASS/FAIL 夹具；结构测试 INV-C1…INV-C7。

**来源**：声明导出机制、`Outcome`、`ctx.call`、`model` C-D3；一种声明含检查与导出、`biology` 分层、`required_obligations` 思想（落成 `final_checks`）A-D3；`step_checks` 标「工具自报」、三字段对应三个时刻、检查直接用 `biology` M。依据：[已读] 旧 `ToolSpec`、`_recipe_spec`、副作用类别；[设计] 检查并入能力。

---

## D4 流水线（Pipeline）与接纳校验

**结论**：计划先成为不可变记录，科学计算随后才发生。首版只支持**线性**步骤和有类型的引用。提交计划时只做**接纳校验**：整份计划一次校验，**不执行任何能力**。计划的格式里**没有**任何能表达检查、门或必需范围的字段。

**问题**：旧 `plan()` 实际把整链跑完，无法证明理由是事前声明 [已读]；字符串引用把 DNA、路径和内部字段混在一起 [已读]。

**决定**

```json
{
  "schema": "pipeline-v1", "version": 1, "goal_digest": "…",
  "steps": [
    {"step_id": "s1", "use": "cut_plasmid.inspect_guide@1.0.0",
     "inputs": {"vector": {"source": "vector"}, "target": {"source": "target"}},
     "params": {}, "why": "Check the supplied guide before changing anything.",
     "expects": {"on": {"step": "s1", "port": "report", "pointer": "/pam_valid"}, "op": "equals", "value": true}}
  ],
  "outputs": [{"name": "construct", "from": {"step": "s1", "port": "product", "index": 0}, "target": "t1"}],
  "library_ref": null
}
```

- **引用**恰有四种：`{"literal": 值}`（仅用于 `value` 类端口与参数，记为宿主声明）、`{"source": 来源id}`、`{"step": 步骤id, "port": 端口, "index": 下标?}`、`{"artifact": 文件引用}`。多产物端口取单个成员**必须显式给 `index`**，不自动取第一个。紧凑写法 `@vector`、`@s1.product[0]` 只是糖，规范化后与规范形式摘要相同，**只存一种规范形式**。不提供 JSONPath 或任意字段解引用。
- `why` **必填**（1–400 字符），记为 `plan_declared` 声明（D10）；程序不判断其质量。
- `expects` 可选，宿主**追加**的预期断言，封闭语法：`op` ∈ `equals` `gte` `lte` `between` `contains` `length_equals`。它**只增不减，不能代替系统检查**。
- `outputs[]` 把步骤端口绑定到目标物（`target`）。**没有 `deliver_as`**：输出的角色由产出它的能力声明（D3），宿主不能自选。
- 允许**局部诊断计划**：`outputs` 暂未覆盖全部目标物时，接纳回执列出未绑定的目标物，目标保持开放；封存时所有 `required` 的目标物必须有合法绑定。
- `library_ref`：由库模板实例化则记 `{name, version, template_digest}`。`name` 是模板名；`version` 是**贡献该模板的 Kit 的清单版本**（核心模板用 Core 版本）；模板自己没有独立版本号（模板文件里的 `version` 是实例化后流水线的版本整数，不是库版本），精确身份靠 `template_digest`。

*接纳校验（`admission`）：提交与每次修订时执行，一次列出所有错误*

| 错误码族 | 查什么 |
|---|---|
| `PLAN_SCHEMA_INVALID` | 符合 `pipeline-v1`；不允许未声明字段，**尤其不允许出现 `checks`、`gates`、`required_scopes` 之类** |
| `PLAN_ID_INVALID` | 步骤 id 格式 `^[a-z][a-z0-9_]{0,31}$`、唯一、不与来源重名 |
| `PLAN_REF_UNRESOLVED` | 引用可解析；只指向更早且未失败、未被取代的步骤；端口与下标合法 |
| `PLAN_CAPABILITY_UNKNOWN` | 能力存在于**固定的目录快照**，运行条件可用；`use` 可省略版本，规范化时补成目录快照里的精确版本，写了版本则必须一致；只允许 `ACTION` 角色 |
| `PLAN_INPUT_UNBOUND` | 每个必填输入端口都被绑定；类型匹配；静态可判定的约束检查 |
| `PLAN_PARAM_INVALID` | 参数符合声明的 JSON Schema；未知参数拒绝；字面量序列每个不超过 200 nt |
| `PLAN_WHY_MISSING` | 每步都有 `why` |
| `PLAN_OUTPUT_INVALID` | 输出引用存在，`target` 存在；允许暂时没有输出（局部诊断计划）；`required` 目标物必须有绑定是**封存的先决条件**（SEAL-1），不是接纳条件 |
| `PLAN_GOAL_BINDING_INVALID` | 目标里每条约束的 `target` 指向存在的目标物 |
| `PLAN_EXPECT_INVALID` | `expects` 语法合法，`on` 引用类型与 `op` 兼容 |

接纳校验的结果是**失败记录**（`INVALID_INPUT`），不是裁决：它回答「这个操作能不能被接受」，不是「某个对象好不好」。任何一项失败 → 返回错误清单，计划**不可执行**，不写日志；全部通过 → `pipeline.declared`（版本 1）。**只有 `ACTION` 角色的能力可以出现在计划里**；检查能力由检查层按必过项派生调用，宿主想要额外检查用 `--also`（D7）。

*模板*：`pipeline-template-v1` ＝ 带参数（`{{name}}` 占位，声明类型与说明）的 `pipeline-v1`。`template instantiate` 只输出草稿，可在提交前编辑；**模板不能携带检查**。库里建议放一个只有一步的 `core.single_call` 模板（待用户决定，见 `OPEN-ITEMS.md`）。

**不采用**：继续在计划阶段运行算法；把已算出的最终序列放进计划当执行权威；`if`/循环或任意表达式（会变成新语言，分支用「修订」表达）；只接受结构化引用（对弱宿主太啰嗦），所以紧凑与规范两种写法、一种存储。

**失败时怎么办**：返回完整错误清单，每条含错误码、位置（JSON Pointer）、原因、`recovery`（如「运行 `describe capability <id>` 查看端口」）；不转调旧入口，不用默认值掩盖缺失。

**怎么测**：INV-P3 接纳时调用器的调用数为 0（最后一步参数非法，第一步也不得执行）；INV-P2 塞检查字段被拒；规范化幂等与两种写法摘要相同；前向引用、环、重名、多产物无 `index`、DNA 字符串被当引用均拒绝；非 DNA 的计划可完整通过；每条错误码各有正反例。

**来源**：计划格式、`why`、`expects`、模板 C-D4；四种引用、`index` 必给、局部诊断计划、接纳零计算 A-D4；接纳校验改为失败记录而非裁决、`outputs` 取消 `deliver_as`、只允许 `ACTION` 入计划 M。依据：[已读] 旧步骤格式、引用解析、`plan()` 即执行；[设计] 其余。

---

## D5 流水线修订

**结论**：修订只追加，不覆盖。**步骤一旦开始就冻结**，其定义、相对顺序与位置永不改变；每次修订必须写触发原因和理由；修订不能改目标、不能减少检查；封存之后不能再修订。

**问题**：用户要求「动手前先写计划，执行中可因实际问题实时修改」。任意修改会出现「为通过而删步骤」「失败记录消失」；完全不能改，AI 遇到问题只能放弃整个计划。

**决定**

```json
{
  "schema": "pipeline-revision-v1", "expected_digest": "<当前流水线摘要>",
  "trigger": {"kind": "step_failed", "step_id": "s1", "failure_code": "STEP_EXPECTATION_FAILED",
              "event_refs": ["<journal event hash>"]},
  "reason": "The supplied guide has no valid PAM; replacing it with the guide at [13,33).",
  "operations": [
    {"op": "supersede_step", "step_id": "s1", "by": "s2"},
    {"op": "add_step", "after": "s1", "step": {"step_id": "s2", "use": "cut_plasmid.replace_spacer@1.0.0",
      "inputs": {"vector": {"source": "vector"}, "target": {"source": "target"}},
      "params": {"spacer": "GACATCGTACGATCGTACAT"}, "why": "Use the guide that has an NGG PAM."}},
    {"op": "set_outputs", "outputs": [{"name": "construct", "from": {"step": "s2", "port": "product", "index": 0}, "target": "t1"}]}
  ]
}
```

**操作集（封闭）**：`add_step`（插在指定步骤之后，且必须在所有已开始步骤之后）、`supersede_step`（只能对 `FAILED` 或 `PENDING` 的步骤，标记被哪一步取代；被取代的待执行步骤不再执行）、`set_outputs`。**没有**「修改已开始的步骤」「删除步骤」「修改目标」。

*规则 REV-1…REV-9*
- REV-1 修订带 `expected_digest`（并发防覆盖；同一修订重复提交时摘要已变，会被拒绝）；程序把操作应用到当前文档得到新文档，重新规范化并计算摘要，写 `pipeline.revised`。
- REV-2 **已开始的步骤冻结**：除 `supersede_step` 作用于 `FAILED` 外，任何触及它们的操作一律拒绝；失败与中断的步骤记录永不覆盖。
- REV-3 触发原因必填：`step_failed`（含预期断言失败与中断）、`check_failed`（某次判定里的 `FAIL` 或 `UNKNOWN` 裁决）、`host_observation`（宿主文字说明，**视为声明**）、`user_request`（附原话，**视为声明**）。前两类的 `event_refs` 必须存在于日志并与类别相符，由引擎核对；后两类只记录并在视图里画虚线。
- REV-4 `reason` 必填，记为 `plan_declared` 声明并绑定新版本摘要；日志里它出现在新步骤的任何执行事件**之前**，先后由哈希链证明（D9）。
- REV-5 修订后重新跑**全部接纳校验**；失败 → 返回错误清单，当前版本不变。
- REV-6 修订不能改目标，也不能减少或绕过检查（计划里本来就没有检查）；改目标走 `goal.amended`。
- REV-7 run 一旦存在 `SEALED` 的交付或已 `ABANDONED`，不再允许修订；要继续就开新 run 并记录 `derived_from_run`。
- REV-8 修订次数与触发类别写进封存清单和运行卡片。
- REV-9 **重试就是新增一个步骤并取代旧的**：因环境或内部原因（含中断）失败的步骤，与科学上失败的步骤一样，都不原样重跑，而是新增一个步骤（定义可与旧步骤相同）并 `supersede` 旧步骤。被取代步骤的输出**不可被后续步骤引用**，但永远保留。
- 一个预期断言失败的步骤记为 `FAILED`（失败码 `STEP_EXPECTATION_FAILED`，输出保留不可引用），因而可被取代；这避免了「断言永远不通过、封存永远被挡」的死结。

**不采用**：就地编辑计划（无法恢复原始选择）；失败后复用原 step_id 换参数（隐藏原失败）；完全禁止修订；引入条件步骤（新语言，分支由「AI 看到失败后修订」表达，更诚实）。

**失败时怎么办**：返回违反的规则号与位置；原计划与产物保持可查；拒绝只返回错误清单，不写日志。`run execute` 在两次调用之间发现计划被改，则暂停，不悄悄执行另一版的后续步骤。

**怎么测**：随机操作序列的属性测试（INV-R1、INV-R2）；REV-1…REV-9 各一正例一反例；触发类别与事件引用不符被拒；两个并发修订只有一个成功；重试保留原失败；端到端：失败 → 修订 → 完成 → 封存。

**来源**：封闭操作集、触发类别、规则 C-D5；冻结点＝开始、`expected_digest` A-D5；断言失败记为 `FAILED`（修掉旧稿的死结）M。依据：[已读] 任务表有 `revision` 字段；旧 Pipeline 能否中途改动 [未核实]；其余 [设计]。

---

## D6 执行层与日志

**结论**：命令行每次调用都是无状态的：从运行目录里的日志恢复状态，执行下一批待执行步骤，把一切写成事件，输出存进内容存储。**执行层只产生事实，不下判断**；记录不再依赖调用者记得埋点，而是执行器自己写。

**问题**：旧 `run_step` 每调用一次就重放此前所有步骤、遍历 `core` 与 `scripts` 下所有 `.py` 计算「实现指纹」、用大范围 `except Exception` 把一切规范成同一个失败码；Evidence Trace 靠各入口手工 `observe(...)` 包装与嗅探结果字典形状 [已读]。

**决定**

*运行目录*（每个 run 一个目录 `runs/<run_id>/`）

```
run.json                  创建时写入，之后不变：run_id、创建时间、release_id
journal.ndjson            唯一真相：哈希链接的事件日志（D9）
inputs/<source_id>/…      输入文件副本（只记录运行目录相对路径与 sha256；**不保存原文件的绝对路径**）
store/materials/<id>.json、store/documents/<id>.json    只写一次、读时校验
work/<step_id>/…  能力写出的文件（登记 sha256）
candidate/<n>/…           暂存的待交付输出
sealed/<seal_id>/…        封存包（不可变）
views/…                   渲染出的视图（可重建）
```

*创建运行时（`run create`）*：编排层只写一个 `run.created` 事件，里面带：环境指纹（Python、平台、依赖版本、外部程序的名称与版本与**可执行文件内容哈希**、配置摘要）、**目录快照**的标识（见 D11）、已装载的 Kit 回执。环境指纹**每个 run 记一次**，不逐步重算、不遍历源码哈希。

*执行算法*（`run execute [--until s3]`）
1. 取运行锁（单写者）；读日志并校验哈希链；若**尾部不完整**则按 E-尾部规则恢复（见下）；由日志推出状态。
2. 能力找不到或版本不符 → 失败 `CAPABILITY_UNKNOWN`／`CAPABILITY_VERSION_MISMATCH`（目录快照只用来记录和推导必过项，执行时不再专门比对）。
3. 取下一个未被取代的 `PENDING` 步骤。解析输入：来源（核对 `sha256`，变了则 `SOURCE_CHANGED`）、上一步输出（读时校验哈希）。
4. 追加 `step.started`：步骤 id、能力 `{id, 版本, 声明摘要, 代码摘要}`、**每个输入的标识与来源 `{kind: source|step|artifact|literal, ref}`**（`literal` 是宿主声明，`ref` 为空）、参数全文、参数摘要。
5. 经**调用器**在进程内调用能力，传入 `ctx`。能力内部的 `ctx.call` 同样经调用器，产生带 `parent` 的 `call.recorded` 事件。
6. 校验 `Outcome` 符合声明（端口、类型、材料合法）；材料与文档写入内容存储；文件登记哈希（记入 `step.completed`）。
7. **步骤自检**：能力的自检草稿写成 `verdict.issued`（出具者 `tool_self_report`）；宿主的 `expects` 逐条求值，写 `verdict.issued`（出具者 `host_expectation`，范围 `user_goal`）。
8. 无断言失败 → 追加 `step.completed`（输出标识、值、耗时）。**任一断言失败 → 追加 `step.failed`（`STEP_EXPECTATION_FAILED`，输出保留但不可引用）**。步骤失败 → `run.halted` 并停止。
9. 没有待执行步骤且每个失败步骤都已被取代 → `run.completed`。

*状态机*

| Run 状态 | 进入条件 | 可迁移到 |
|---|---|---|
| `PLANNED` | 目标与流水线 v1 已声明且通过接纳校验，尚无步骤开始 | `RUNNING`、`ABANDONED` |
| `RUNNING` | 有步骤已开始或有待执行步骤，未停止 | `HALTED`、`COMPLETED`、`ABANDONED` |
| `HALTED` | 步骤失败（含断言失败、中断），等待修订或放弃 | `RUNNING`（提交合法修订后）、`ABANDONED` |
| `COMPLETED` | 无待执行步骤，且每个失败步骤都已被取代 | `RUNNING`（提交合法修订后，且尚无封存）、`ABANDONED`（尚无封存时）；可 `judge`、`seal`、`verify` |
| `ABANDONED` | 宿主或人放弃（`run abandon`，可附原因）；已封存的 run 不能放弃 | 终态；不能再修订或封存 |

Step 状态由其事件推出：无事件为 `PENDING`；`FAILED` 的记录永久保留，可被后续步骤取代（`superseded_by` 是字段，不是状态）。

*E-尾部规则（崩溃恢复）*：追加事件为「序列化 → 一次写入 → flush → fsync」，持锁进行。打开日志时若**最后一行**不是合法 JSON 或链校验失败，且前面的链完好 → 把日志截到最后一个完好事件，追加 `journal.recovered{discarded_bytes, reason}`（该事件由 `storage` 的恢复例程写，是唯一的特例）；若损坏在非末尾 → `JOURNAL_CHAIN_BROKEN`（`INTEGRITY`），只允许只读查看与 `verify`。尾部有 `step.started` 而无完成或失败 → 追加 `step.failed{STEP_INTERRUPTED}`（可重试）；残留文件只作诊断，不据其补写完成。


*确定性*：声明 `deterministic:true` 的能力不得读时间或未播种的随机数；随机性必须来自显式 `seed` 参数。

*失败记录*（`failure-v1`，D14）：`{code, category, message, details, recovery, retryable, cause_chain}`；`details` 不含原始序列。

**不采用**：运行状态放内存或可写状态文件（不可审计、崩溃后无法恢复）；每步用子进程隔离（崩溃隔离只对 `external_process` 有意义，那里已有子进程与超时）；每步隐式重放全部历史（O(n²)；重放只在封存终检里做一次）；异步「尽力发送」事件（崩溃后无法判断完成状态）。

**失败时怎么办**：来源文件变化 → `SOURCE_CHANGED`；进程中断 → 下次打开时 `STEP_INTERRUPTED`；链断裂 → 拒绝继续；锁被占用 → 报 `RUN_LOCKED`。**不得因「重复运行都通过」宣布间歇失败已修复**：保留失败现场两侧操作数的安全摘要（输入标识、结果摘要哈希、差异字段名，不含序列）。

**怎么测**：用玩具能力（纯计算、会失败、写文件、大输出、故意非确定）测执行器：成功、失败、断言失败、中断恢复（在 `step.started` 后强杀）、**日志尾部写到一半后强杀**、来源被改、锁竞争、目录快照被换；状态机合法与非法迁移表；`Outcome` 不符声明的反例；环境指纹只出现一次；INV-E1…INV-E6。

**来源**：运行目录、环境指纹一次、无状态执行 C-D6；输入来源绑定 A-D6；尾部恢复规则、断言失败＝步骤失败、日志存储取 NDJSON 而非 SQLite（取其人可读与封存包自带副本，见 `OPEN-ITEMS.md` 的可逆默认）M。依据：[已读] 旧 `run_step`、旧 Recorder；[设计] 其余。

---

## D7 检查系统

**结论**：检查**只有一种形状（裁决）、一种载体（检查能力）**，裁决出现在**步骤自检**与**封存终检**两个时刻；第三个时刻**接纳校验**只产生失败记录，不是裁决（见下表）。哪些检查必须通过，由**底盘根据「实际产出什么」和「实际用了谁的能力」推导**，宿主和计划都不能减少。检查失败（`FAIL`）、没能判断（`UNKNOWN`）、不适用（`NOT_APPLICABLE`）三者含义不同，且检查结果永远不是异常。

**问题**：旧系统一次检查失败至少有五种形式（检查字典、异常、`"CODE: text"` 字符串、布尔 `all_applicable_pass`、目标覆盖字典）；任务路线与流程路线是两套并行的验证（`runtime_validate` 用三个布尔值，`workflow_validation` 直接算四个范围），同一个 CDS 检查在两条路线里归到不同范围；`INCOMPLETE` 一个词同时表示没跑、信息不足和目标没绑定；生物学自检在构造路线上至少运行两次；一个 Kit 的必过检查在 `gates.py` 与流程里各写一份 [已读]。**好的部分保留**：四个范围各回答一个不同的问题（规格里写明：序列模型、制备模型、文件、用户目标；要求制备时会拦下只改序列的结果）；裁决绑定被检查对象的版本与条件；封存时重新计算 [已读]。

**决定**

*三个时刻*

| 时刻 | 产生什么 | 失败时 | 谁能追加 |
|---|---|---|---|
| `admission` 接纳校验 | 失败记录（D4 的错误码族），**不是裁决** | 返回错误清单，计划不可执行 | 底盘固定；Kit 只能通过自己能力的契约影响（D11） |
| `step` 步骤自检 | 裁决，出具者 `tool_self_report`（能力自检）或 `host_expectation`（宿主断言） | 断言 `FAIL` → 步骤 `FAILED`；自检 `FAIL` 只显示，不改变步骤状态 | 能力作者（自检）、宿主（断言） |
| `final` 封存终检 | 裁决，出具者 `check_capability` | 必过项未满足 → 不能封存 | 底盘按必过项推导；Kit 经 `final_checks` 追加 |

*裁决 `verdict-v1`*（事件 `verdict.issued` 的负载；`verdict_id` ＝ 该事件哈希）

```json
{
  "schema": "verdict-v1",
  "check": {"id": "check.primer_quality", "version": "1.0.0"},
  "scope": "preparation_model", "moment": "final",
  "subject": {"kind": "document", "id": "<document_id>"}, "constraint_id": null,
  "outcome": "PASS", "issuer": "check_capability",
  "summary": "Primer pair passes complete-oligo quality limits.",
  "evidence": {"forward_tm": "59.7", "reverse_tm": "60.2", "dimer_dg": "-3.1"},
  "basis": ["<被读取的事件哈希>"],
  "applicability": null, "rule_refs": ["<rule digest>"],
  "does_not_establish": ["Actual PCR performance"]
}
```

- `outcome`：`PASS`（检查了且符合）、`FAIL`（检查了且违反）、`UNKNOWN`（没能判断：证据不足、依赖缺失、检查本身出错——出错时附一条失败记录）、`NOT_APPLICABLE`（必须给 `applicability: {reason, basis}`：`reason` 是一句话原因，`basis` 指向使它不适用的事实；不接受「调用者说跳过」）。
- `evidence` 只放哈希、长度、数值（精确量用十进制字符串）、状态，**不放原始序列**；`basis` 使每个裁决可追溯到它依据的事实。
- **继承自输入的问题**（如模板自带的 CDS 注释错误）只在两项检查里特殊处理：`check.annotation_integrity` 与 `check.cds_validity` 把输出与对应输入逐项比较（比较依据写进 `evidence`），给每个发现标 `origin: INHERITED|INTRODUCED|UNDETERMINED`。`INTRODUCED` 与 `UNDETERMINED`（无法判断来源，取保守一侧）使裁决为 `FAIL`；**只有 `INHERITED`（输入里本来就有、流水线没有触碰）不使裁决为 `FAIL`**：裁决为 `PASS`，`evidence` 逐条列出继承发现，封存包带标签 `INHERITED_FINDINGS`，运行卡片「Not done」栏显示。这不是通用豁免：只限这两项检查，其他检查不适用，宿主与计划都不能指定。

*四个范围，各回答一个不同的问题*

| 范围 | 回答什么 | 备注 |
|---|---|---|
| `content_model` | 步骤产生的东西是不是确实就是被宣称的那样？内容在计算上和领域上合理吗？ | 由旧 `sequence_model` 推广，以容纳非 DNA 的判断类输出 |
| `preparation_model` | 按流水线能否真的把它做出来（按我们的模型）？ | 反应链模拟、完整引物质量、订单表一致 |
| `file` | 文件和记录是否忠实承载了结果？ | 各格式回读等价、清单、日志哈希链、输入未被改动 |
| `user_goal` | 结果满足用户要求了吗（在可计算范围内）？ | 目标约束、目标物是否被满足 |

*核心检查目录（初始，ID 固定）*

| 范围 | 检查 | 说明 |
|---|---|---|
| `content_model` | `check.replay`、`check.lineage`、`check.model_agreement`、`check.annotation_integrity`、`check.cds_validity`、`check.biological_sanity`、`check.dna_value_valid` | `check.replay` 对 `deterministic:true` 的步骤用记录的版本与输入经调用器（回放模式：临时目录，不写事件、不入内容存储；由 `check.replay` 经调用器内部选择，宿主不能选，对所有派生的 `ctx.call` 一并生效，仍做原来的端口与输出校验）重算并比较输出标识，非确定性步骤在证据里列为「未重放」；`check.biological_sanity` 的阈值与适用条件来自规则数据（D12） |
| `preparation_model` | `check.reaction_chain`、`check.primer_quality`、`check.order_table` | 反应链模拟的输入只给模板、引物与路线，不读候选序列 |
| `file` | `check.readback`、`check.manifest`、`check.journal_chain`、`check.store_hashes`、`check.inputs_unchanged`、`check.package_hashes` | `check.package_hashes` 只对 `sealed` |
| `user_goal` | `check.goal.nonempty`、`check.goal.target_role_met`、`check.goal.<约束种类>`（D2 的七种；其中 `check.goal.output_present` 的参数是可选的 `fields`，即输出文档必须含的字段名列表；其余种类的参数由各检查能力的声明定义） | |

*必过项（obligations）的唯一推导规则*

> 必过项 ＝ **基础档位**（由输出角色决定）∪ **目标约束**（每条活动约束对应的检查）∪ **所用能力的 `final_checks`**（含声明了 `model` 的能力自动带上 `check.model_agreement`）∪ **宿主追加的 `--also`**。只取并集，**从不减少**。

基础档位（`profiles.json`，底盘数据，Kit 不能增改）：

| 条件 | 并入的检查 |
|---|---|
| 任何封存包 | `file` 范围的 `check.readback`、`check.manifest`、`check.journal_chain`、`check.store_hashes`、`check.inputs_unchanged`；再加 `check.goal.nonempty`、`check.goal.target_role_met` |
| 输出里含**材料** | `content_model` 的 `check.replay`、`check.lineage`、`check.annotation_integrity`、`check.cds_validity`、`check.biological_sanity`（**恒必过**，防止把 DNA 输出标成低档逃避序列检查） |
| 角色 `construct` | 再加 `preparation_model` 的 `check.reaction_chain`、`check.primer_quality`、`check.order_table` |
| 角色 `primer_set` | `preparation_model` 的 `check.primer_quality`、`check.order_table`、`check.reaction_chain` |
| 角色 `component`、`analysis` | 只有上面两行；非 DNA 输出（如证据评估）的内容检查由所用 Kit 能力的 `final_checks` 追加 |

输出角色**由产出它的能力声明**（D3），宿主在计划里没有地方选；目标物声明的角色与实际输出角色不符，则 `check.goal.target_role_met` 为 `FAIL`。

*封存条件*：封存时对暂存包重新运行**全部**必过项（SEAL-4），每一项的裁决为 `PASS` 或带原因与依据的 `NOT_APPLICABLE` 才算满足；`FAIL`、`UNKNOWN`、缺失（如检查能力不在目录快照里、依赖不可用）都**阻止封存**，缺失记为 `UNKNOWN` 加 `CHECK_UNAVAILABLE`，**不是跳过**。封存只看这一套判据（INV-D3）。封存的先决条件（run 已完成等）不是裁决，是先决条件失败（D8）。

*检查能力的质量保证*：每个检查能力必带「必须通过」与「必须失败」两份样例（`fixtures`），测试实际运行 FAIL 样例确认其结果非 `PASS`；检查只读（除追加自己的裁决事件外，运行目录哈希相同；重放在临时目录里进行）；三处关键逻辑（`check.replay`、必过项推导、哈希链校验）做人工变异测试。

*步骤自检的显示*：`tool_self_report` 与 `host_expectation` 的裁决**不计入必过项**，也**不放进运行卡片的「Checked by the program」栏**，而放「Declared only」栏，标明是工具自报或宿主断言（D10）。

**不采用**：把必过检查放进计划让 AI 选；类别由宿主在计划里自选；Kit 可新增交付档位；把 `UNKNOWN` 转成 `FAIL` 或 `PASS`；让能力自带的「通过」充当正式资格；检查另设一套声明与注册表；把「继承自输入」扩成通用豁免（只有上面两项检查按逐项比较处理，其余检查不适用）。

**失败时怎么办**：检查能力抛异常 → 调用器边界把它规范成失败记录，该必过项记 `UNKNOWN`，阻止封存；检查结果永不通过异常传递（INV-A1）。

**怎么测**：每个检查能力的 PASS/FAIL 样例；必过项推导的**属性测试**（对任意输出角色与能力集合，并集单调，宿主任何输入不能使其变少，INV-A4）；**角色降级反例**（给输出贴低档角色无效，INV-A6）；缺失检查记 `UNKNOWN`（INV-A5）；`NOT_APPLICABLE` 缺原因或依据被拒（INV-A8）；自检裁决不进必过项也不进「程序核对」栏（INV-A9、INV-T6）；变异测试；封存重判（INV-D7）。

**来源**：三个时刻与命名、必过项并集、`profiles` 数据、四个范围（回到用户原有四问）M；单一裁决形状、夹具、变异测试、`model_agreement`、材料输出恒查内容 C-D7；检查即能力、`UNKNOWN`、`NOT_APPLICABLE` 须有依据、`INHERITED` 标记（后改为两项检查按逐项比较处理，见 INV-A10）、义务只增不减 A-D7。依据：[已读] 旧检查的形式与散落、两套验证、`INCOMPLETE` 的多义；[设计] 其余。

---

## D8 交付：封存

**结论**：交付是检查系统的最后一步：**判定（试跑）→ 暂存 → 封存终检 → 封存**。封存包不可变、内容寻址、**自带日志副本与目录快照**，离线也能复核，并诚实列出「没有核验什么」。没封存的结果照常给，但统一加「未封存」标签。

**问题**：旧系统有三个交付入口（`deliver_result`、`finalize`、`finalize_candidate_construct`）汇到同一个提升函数 `_promote_verified_candidate`，前置检查各异；失败用 `GateRejected` 抛出（19 种码）；交付状态词多达八种 [已读/已量]。**好的部分保留**：暂存目录 → 读回 → 带 SHA-256 的清单 → 原子重命名 → 拒绝覆盖已存在目录 [已读]。

**决定**

*状态*：只有「已封存」与「未封存」两种。已封存的包不可变；其余一律是标签「未封存」，封存被拒（`seal.rejected`）时候选保留。封存之后的新事实（被新封存取代、复验失败）用事件与标签记录，不改旧包。

*命令*
- `judge [--also id]`：先把当前输出暂存到 `candidate/<n>/`（同 SEAL-2），再对它运行全部必过项，**不封存**；返回「若现在封存会缺哪些」。
- `seal [--also id]`：

*SEAL-1…SEAL-10*
- SEAL-1 **先决条件**（失败是 `INVALID_INPUT`，退出码 1，不是裁决）：run 为 `COMPLETED`；每个失败步骤都已被取代；没有内容不同的既有封存（内容相同则幂等返回）；`required` 目标物都有合法绑定。
- SEAL-2 **暂存**：按 `outputs` 经格式能力（`format.write_*`，同样走调用器）把输出导出成用户可读文件（GenBank、FASTA、原生 `.dna`（可选）、表格、报告）到 `candidate/<n>/`，并生成暂存文件清单 `files[]`（`check.manifest` 检查它与目录实际文件一致，SEAL-6 的最终清单由同一份数据生成），
- SEAL-3 推导必过项（D7），固定到本次封存运行。
- SEAL-4 对**暂存包的当前内容**重新运行全部必过项（`moment: final`），**不信任此前任何裁决**；裁决写入日志后才固定 `journal_head`（SEAL-7）。
- SEAL-5 有未满足项 → `seal.rejected`（含每项的检查、结果、`recovery`），退出码 10，候选保留并标「未封存」。
- SEAL-6 在临时目录 `.sealing-<随机>.tmp` 写入封存包：交付文件、`goal.json`、`pipeline-final.json`、`revisions/`、`journal-until-seal.ndjson`（日志副本）、`catalog-snapshots.json`、`verdicts.json`、`views/runcard.html`、`views/report.md`，最后写 `manifest.json`。
- SEAL-7 清单字段：`run_id`、`release_id`、`goal_digest`、`pipeline_digest`、`revisions`、`journal_head`（本次封存终检的全部裁决写完之后的日志头哈希；包内日志副本截止于此，`seal.created` 在原子发布之后追加，不在副本里）、`catalog_ids`、`environment_ids`、`files[{path, sha256, role, labels}]`、`verdicts[{check, scope, outcome, verdict_event}]`、`profile`、**`not_verified`**、**`labels`**、`review_states`、`kit_receipts`。**清单不含 `seal_id` 自身**。
- SEAL-8 复制后重新计算临时目录内每个文件的哈希，与暂存值比较。
- SEAL-9 **原子重命名**为 `sealed/<seal_id>/`（`seal_id` ＝ 清单规范化摘要）；目录已存在则内容相同返回已存在的封存，否则拒绝覆盖；随后追加 `seal.created`。
- SEAL-10 返回 `present_files`：**只有这些文件可以被当作「正式结果」展示**。

*`not_verified` 的组成*：所有用到的能力与运行过的检查的 `does_not_establish` 之并集 ＋ 未绑定意图 ＋ 被丢弃的约束 ＋ `PLANNED` 的实验室步骤 ＋ 带原因码的 `NOT_APPLICABLE` 说明 ＋ 各步骤 Outcome 的 `unverified`。清单里的 `not_verified` 是运行卡片「Not done」栏的子集（INV-T3）：「Not done」栏另外显示标签行，以及未封存时的 `UNKNOWN` 必过项。

*复验 `verify <运行目录或封存目录>`*：重新计算文件哈希、清单摘要等于目录名、包内日志副本的哈希链完整且头哈希等于清单所记、重跑 `offline` 的检查（D3；其余如实标「未重跑」）。**只复制封存目录到新位置，`verify` 也应通过**（INV-D6）。

*标签只有一处实现*（`assurance.labels`）：`UNSEALED`、`AMENDED_AFTER_START`、`INHERITED_FINDINGS`、审核状态汇总（`reviewed x / stale y / none z`）、`EXTERNAL_KIT`。`status`、报告、命令行输出都从这里取标签文字。

*运行卡片放进封存包，但只显示 `journal_head`，不显示 `seal_id`*，以免「清单含卡片哈希、卡片含清单摘要」的自引用。

**不采用**：交付门是独立于检查的另一套规则（旧系统的做法）；只给文件不给日志；允许覆盖旧封存；把封存拆成独立于检查系统的另一个模块；任何导出函数都能设置「authoritative」。

**失败时怎么办**：磁盘或权限失败 → 清理临时目录，返回失败记录，不留部分包；封存被拒 → 返回完整未满足清单。封存后改字节 → 新文件需要新的封存，旧包不改。

**怎么测**：全部通过 → 封存 → `verify`；逐个让一个必过项失败 → 被拒且原因正确；封存后改一个字节 → `verify` 报错；改日志副本一行 → 链断裂；同内容重复封存幂等；封存中途崩溃的清理；卡片不含 `seal_id` 且清单可由内容复算；只复制封存目录后 `verify` 通过。

**来源**：状态与标签、封存流程、自证封存包（日志副本）、`not_verified` C-D8；检查与交付同一拥有者、先决条件与裁决分开、`Reuse` 不跨运行 A-D8；封存只留三种状态、卡片只显示日志头、封存时对暂存包重判 M。依据：[已读] 旧暂存、读回、清单、原子提升模式与三个入口；[设计] 其余。旧 19 个 `GATE_*` 的去向见 `MIGRATION-MAP.md`。

---

## D9 标识、版本与来源追踪

**结论**：每一种「可被引用的东西」恰有一种标识；标识一律是 SHA-256 小写十六进制，对**规范化 JSON** 或**文件字节**计算；**只有 `kernel/ids.py` 会算哈希**。日志是哈希链，**事件的先后顺序可以证明**。材料的来历不写在材料里，由日志里「输入标识 → 步骤 → 输出标识」的事件表达，**每个输入都记录它的来源**。

**问题**：旧系统里「这是哪一版」有七八种说法（分子版本 84 处、序列哈希 61 处、来源哈希 28 处、计划哈希 20 处、验证哈希 17 处、产物哈希 17 处、清单哈希 12 处），大小写不统一；分子的版本号把来源血统和注释元数据全算进去，同一条序列经不同途径会有不同「版本」 [已量/已读]。

**决定**

| 对象 | 标识 | 计算自 | 用于 |
|---|---|---|---|
| 材料 | `material_id` | 规范化 JSON：`sequence`（大写）、`topology`、`strandedness`、`ends`、`features`（按 `(start,end,type,label)` 排序；0 起半开区间；限定词键排序）。未知的拓扑、链、末端存为 `null`，**不猜**。**不含**名称、描述、日期、注释性元数据、血统 | 内容存储、引用、检查 |
| 序列 | `sequence_id` | `sha256(大写序列 + "|" + topology)` | 快速判断是不是同一条序列 |
| 文档 | `document_id` | 规范化 JSON | 内容存储 |
| 文件 | `file_sha256` | 文件字节（不换行归一、不去 BOM） | 输入、产物、封存文件 |
| 目标、流水线 | `goal_digest`、`pipeline_digest` | 规范化文档 | 事件 |
| 事件 | `event_hash` | `sha256(规范化事件（不含 hash）+ prev)` | 日志哈希链 |
| 裁决 | `verdict_id` | 其 `verdict.issued` 事件的 `event_hash` | 引用 |
| 目录快照 | `catalog_id` | 目录快照文档摘要（D11） | `run.created` |
| 封存 | `seal_id` | 清单规范化摘要（清单不含它自己） | 目录名 |
| 环境、发行 | `env_id`、`release_id` | 环境指纹文档摘要；发行清单摘要（D16） | 事件、清单 |
| 运行 | `run_id` | `sha256(创建时间 + 随机数)` 的前 16 位 | 目录名 |

*首个事件的 `prev`* 取 64 个字符 `0`（`"0" * 64`），这是唯一的创世约定；S1 的跨平台黄金向量固定它。


- **规范化 JSON**：采用 **JCS（RFC 8785）** 的规则：UTF-8，键按 UTF-16 码元顺序排序（RFC 8785 §3.2.3），无多余空白，拒绝重复键、`NaN`、`Infinity`。**被哈希的对象里不放裸浮点数**：计数用整数，需要小数的量（如 Tm）用**十进制字符串加单位**。以带黄金向量的单一实现为准（Python 标准库的 `json` 不是 JCS，不得拿来冒充）。
- **身份是内容，来历是关系**：同一内容经不同途径得到应被认出是同一个材料；改名字不改身份；改注释**应当**改身份（旧系统被继承的 CDS 注释错误正是实例）。
- **血统不写进材料**：`step.started` 的每个输入都记 `{id, origin: {kind: source|step|artifact|literal, ref}}`，`step.completed` 记输出标识；`lineage(material_id)` 是对日志的查询。同一内容来自多个来源时靠这个**显式来源**区分，不猜「最近那个」。
- **输入来源**（`input.registered`）：`input_origin` ∈ `user_file` `researcher_observation`。由文件导入**不会**把研究者观察升级成程序核实的实验。首版只接受本地文件，不发起公共数据库请求。
- **规则来源类**（`source_class`，D12）：`literature` `official_method` `project_contract` `lab_protocol` `database_record`；`AI` `internet` `latest` 之类一律拒绝。
- **哈希链的诚实边界**：能发现意外损坏与局部改写；对整台机器有完全控制权的写入者可以连清单一起重写。要防有意篡改，需自行把头哈希发布到机器之外（如写进发布记录）；本系统不提供专门机制，也**不假装有签名级的真实性**。

**不采用**：多种哈希各管一摊；只哈希 DNA 字符串（注释与末端不同会被当同一材料）；把来源路径当版本（路径可变）；把运行时间混进科学结果的身份；对事件做数字签名（本地没有可信的密钥托管方，只会制造虚假安心）；用数据库存事件（封存包需要离线可核对的日志副本）。

**失败时怎么办**：内容存储读取时摘要不符 → `STORE_CORRUPT`（`INTEGRITY`）；日志链断裂 → `JOURNAL_CHAIN_BROKEN`，只允许只读查看与 `verify`。

**怎么测**：黄金向量跨 Windows 与 Linux、各 Python 版本一致（INV-I2）；材料规范化属性测试（特征顺序、名称、描述、日期任意变化不改 `material_id`，序列与注释变化改变它，INV-I4）；链校验的篡改测试（改一行、删一行、重排）；被哈希对象不含裸浮点（INV-I6）；每个输入都带来源（INV-I7）。

**来源**：标识表、材料内容身份、哈希链与诚实边界 C-D9；JCS 规范、十进制字符串、输入来源类型 A-D9；用「输入的显式来源」代替独立的句柄对象 M。依据：[已量/已读] 旧哈希种类与 `record_version` 构成；[设计] 其余。

---

## D10 记录层（Evidence Trace）

**结论**：记录层**没有自己的采集入口**，它是日志的**只读视图**：事实层（程序观察到的）、声明层（AI 或人说的，带理由来源）、呈现层（报告与运行卡片）。事实与声明分开；实线只表示「程序核验过的哈希相等」，虚线表示「仅声明」；它不判断，也不证明结论正确。

**问题**：旧 Evidence Trace 的**存储本身是好的**（追加式、带序号、有记录类型、有行为者与理由来源、有投影与渲染）；坏的是**生产端**：各入口手工 `observe(...)` 包装，`capture()` 靠嗅探结果字典的形状决定记什么 [已读]。旧实测：宿主的 13 个选择理由全是事后整理（`organized_summary`）[已读 CLAUDE.md]。

**决定**

1. **日志即存储**：D6 的 `journal.ndjson` 就是记录的事件库；执行层与检查层写事件时就把追踪需要的事实写进去。**没有 `observe` 包装，不嗅探结果字典。**
2. **日志是必选项**：它同时是执行状态，不能关闭。旧的 Off/Observed/Full 开关改为**视图详细程度**（简要、标准、完整），只影响渲染。
3. **事实与声明的硬分界**：事件有 `actor.kind`。`program` 只写观察；`ai_host`、`human` 只写声明；程序**不能**产生声明。**宿主提交的声明（`declare`、目标、计划的 `why`、修订的 `reason`）行为者一律记 `ai_host`；程序执行与检查产生的事件仍是 `program`；`human` 只来自交互式确认（`review sign`，D20）**，宿主转述的用户信息仍是宿主的声明。Kit 的能力在引擎内运行，其事件行为者仍是 `program`（带 Kit 名与版本）。
4. **理由来源**：`plan_declared`（流水线 `why` 与修订 `reason`，**事前声明**，其「事前」由哈希链位置证明）、`original_statement`（与日志里已记录的公开文本逐字一致）、`organized_summary`、`later_interpretation`、`unknown`。
5. **线型**：**实线**只有一种依据——某步骤的输出（文件或材料）与另一步骤的某个输入，**执行层在 `step.started` 里显式记录了这个绑定**（`origin: step|artifact`），且两侧的哈希相等；**虚线**＝宿主或人声明的关系；其余是结构性边（步骤→输出、执行→裁决），用细灰线画，图例注明「仅表示记录结构」。相同内容来自多个来源时靠显式绑定，不猜。
6. **运行卡片**：一页的视图，由日志投影生成，**默认英文**，上方是数据链图（左端外部来源节点，中间步骤，右端交付物，节点标哈希前缀），下方固定三栏，页脚固定一句「This record shows what ran and what was checked. It does not prove that a conclusion is true.」，并注明**「截至第 N 个事件」**。

| 栏 | 内容 |
|---|---|
| Checked by the program | 本次 `final` 时刻、出具者为 `check_capability` 的 `PASS`/`FAIL` 裁决（范围、检查、结果）；接纳校验通过这一事实 |
| Declared only | 目标原话（宿主转述）与约束来源、`why`、修订 `reason`、`declared_context`、人的声明；**能力自检（`tool_self_report`）与宿主断言（`host_expectation`）**——逐条标注来源 |
| Not done | ① 目录快照里所用能力与检查的 `does_not_establish`，加各步骤 Outcome 的 `unverified`；② `PLANNED`/`NOT_PERFORMED` 的实验室步骤；③ 未绑定意图；④ `UNKNOWN` 的必过项；⑤ 被丢弃的约束；⑥ 标签（`amended_after_start`、修订次数、`inherited_findings`、审核状态汇总） |

7. **「不判断」的结构保证**：`record` 模块没有任何写日志的入口，也没有产生裁决或影响封存的接口。8. **视图不重复事实**：报告、卡片、Markdown 摘要都是可随时重新生成的视图，删了不影响真相。9. 卡片所需的「不能证明什么」文字来自**目录快照文档**（已存入内容存储，并随封存包携带），记录层因此不需要 import 任何能力模块，离线也能重绘。

**不采用**：保留 `observe` 包装并收拢到一处；继续嗅探结果形状；让记录层参与判断；用语言模型补齐缺失的理由。

**失败时怎么办**：视图生成失败不影响运行与封存，错误写入 `views/ERRORS.md` 并在 `status` 里提示。日志缺口显示缺口，不编造。宿主绕路得到的成果导入后标 `external_unobserved`，不补写其原始过程。

**怎么测**：构造 run（成功、失败后修订、目标被修订、声明、哈希相等且显式绑定的文件链、哈希相等但**无绑定**的偶然匹配）→ 断言线型（INV-T2）；卡片文本快照（英文）；自检不进「程序核对」栏（INV-T6）；删除 `views/` 后重建字节一致（INV-T4）；卡片声明事件截止点（INV-T5）；**外行读者测试**：事先写好 6–8 题与标准答案，只给读者卡片（真人为准，AI 预演须标「非真人」）。

**来源**：只读视图、事实与声明分层、理由来源、线型规则、三栏卡片 C-D10；事件截止点、显式绑定才画实线、最小运行事实不可关 A-D10；自检归入「Declared only」、目录快照提供「不能证明什么」M。依据：[已读] 旧存储模型、记录类型、`observe`/`capture`；[设计] 其余。

---

## D11 Kit 与目录快照

**结论**：Kit 是一个**目录**，用 `kit.json` 声明它贡献什么，附 `SKILL.md`（写成触发条件，让宿主自己选）。**Kit 不带入口、不带流程代码、不带报告渲染。** Kit 能贡献的只有四样：**能力**（含检查能力）、**知识**、**模板**、**文案**。**Kit 对检查系统只有一个入口：能力声明里的三个字段**（契约、自检、必过检查，D3）。装载由 `catalog` 完成，每个 run 在开始时把装载结果固定成**目录快照**。

**问题**：旧每个 Kit 带 113–223 行流程代码（请求字段手工校验、材料读取、步骤执行、手工埋点、交付、交接文件、摘要整理），入口回头调用旧的共享运行器，一个 Kit 的必过检查在 `gates.py` 与流程里各写一遍 [已读]。**好的部分保留**：旧 `core/kits.py` 的清单发现不 import 代码、模式校验、版本范围、名称冲突不覆盖、坏邻居隔离、回执 [已读]。

**决定**

*Kit 目录*

```
kits/<kit-name>/
  kit.json                  清单（kit-v1）
  SKILL.md                  触发条件 + 使用说明（手写 frontmatter + 生成的输入契约）
  capabilities/             能力实现（Python，含检查能力）+ 导出的声明 JSON + fixtures/
  knowledge/                规则与来源数据（rule-v1）+ review/
  templates/                流水线模板（pipeline-template-v1）
  text/                     文案资源（键 → 英文，中文可选）
  examples/                 合成数据示例（兼作测试）
  tests/   README.md
```

*清单 `kit-v1`*

```json
{
  "schema": "kit-v1", "name": "cut-plasmid", "version": "0.1.0", "title": "Cut Plasmid",
  "requires_core": {"minimum": "1.0.0", "maximum_exclusive": "2.0.0"},
  "contributes": {
    "capabilities": ["capabilities/inspect_guide.json", "capabilities/replace_spacer.json",
                     "capabilities/check_direction.json", "capabilities/check_pam.json",
                     "capabilities/check_vector_self_target.json", "capabilities/assess_selection.json",
                     "capabilities/model_replace.json"],
    "knowledge": ["knowledge/selection_markers.json"],
    "templates": ["templates/replace_spacer.json", "templates/inspect_only.json"],
    "text": ["text/en.json"]
  },
  "does_not_establish": ["Cleavage activity", "Editing efficiency", "Genome-wide off-target safety"],
  "review": "knowledge/review/"
}
```

*装载规则 KIT-1…KIT-7*
- KIT-1 **发现不执行代码**：只读 `kit.json`，用模式校验，核对 Core 版本范围，计算清单哈希。KIT-2 **冲突**：同 id 且内容相同则去重；同 id 内容不同则**冲突双方都不装载**并给出诊断，不按安装顺序挑赢家；Core 保留名被外部项侵犯只禁用外部项。KIT-3 **隔离**：一个 Kit 的清单错误、导入错误、注册冲突只让它自己装载失败，不影响其他 Kit 与底盘。
- KIT-4 **外部 Kit（用户指定目录）会执行代码**：首次装载输出明确提示（「外部 Kit 将以你的权限运行代码；本版本没有沙箱」），记入 `run.created` 的 Kit 回执 `{name, version, manifest_sha256, code_digest, origin, source}`；内置 Kit 同样记，`origin: bundled`。KIT-5 Kit 只能通过 `catalog` 的注册接口接入，不能修改底盘行为。KIT-6 清单里没有联网相关字段，本版本的词表里也没有联网副作用；声明了不认识的副作用的能力在装载时被拒。KIT-7 **清单里没声明的贡献一律不加载**；清单声明的每个贡献都必须有对应文件，反之亦然。**`knowledge/drafts/` 是例外**：来源不全的规则放在这里，**不进清单、不被装载**；团队提供真实来源后移入 `knowledge/` 并登记。

*目录快照*：run 创建时由 `catalog` 构建，标识记入 `run.created`。快照文档（存入内容存储，随封存包携带）包含：`release_id`；每个能力的**完整声明**（含输出角色、`final_checks`、`model`、`does_not_establish`）加 `{声明摘要, 代码摘要, owner}`；每个知识包的摘要与规则审核状态；每个 Kit 的 `{名称, 版本, 清单哈希, 代码摘要, origin}`；`profiles.json` 的**完整内容**与词表的摘要。`catalog_id` 是它的摘要。**快照只记录，并作为必过项推导的依据**：之后装载情况变了，不做专门检查，能力找不到就按普通失败处理。必过项也**按快照推导**：快照里缺的检查记 `UNKNOWN`，不会因为「当前没装上」而从必过项里消失。

*Kit 之间交接的文件形状*（首版唯一一处：Construct → Genome Identity → Revival Evidence；交接的是**文件**，下一个 Kit 把它当作 `as: artifact` 的来源读入，文件内容哈希相等时在运行卡片上画实线）

- `identity-handoff-v1`（Construct 输出）：`{schema, references[{id, sha256, role(original|edited)}], regions[{id, reference_id, start, end}], primers[{id, sequence}]}`；序列文件用哈希引用，不内嵌序列；`start`、`end` 是参考序列上的 0 起半开区间。
- `identity-expected-results-v1`（Genome Identity 输出）：`{schema, assay_id, backgrounds[{id, reference_sha256, primer_pair[正向引物 id, 反向引物 id], expected{status, product_count, product_bp}}]}`。`product_count` 是这对引物在该背景上预测到的产物个数；`product_bp` 只在恰好 1 个产物时是整数，0 个或多个时为 `null`，由 `product_count` 区分「没有产物」与「多个产物」；`status` 取 Genome Identity 自己的领域词（`DISTINGUISHABLE`／`NOT_DISTINGUISHABLE`／`UNDETERMINED`，**不进公共词表**），判据：各背景的 `(product_count, product_bp)` 互不相同才是 `DISTINGUISHABLE`，任一背景 `product_count>1` 且无法区分则 `UNDETERMINED`。
- Revival Evidence 只读取上面第二份文件；两份文件的 `schema` 字符串固定为 `identity-handoff-v1`、`identity-expected-results-v1`，对应的 JSON Schema 以内联 `schema` 形式随各 Kit 的能力声明发布。三个 Kit 对形状有分歧时以本节为准。

*Kit 能改什么、不能改什么，以什么方式体现*

| Kit 能改（落在 Kit 目录的文件上） | 载体 | 影响哪一道检查 |
|---|---|---|
| 自己能力的**契约**（输入输出、参数、副作用、失败码） | `capabilities/*.json`（由代码导出） | 接纳校验 |
| 自己能力的**自检** | `capabilities/*.py` 与声明里的 `step_checks` | 步骤自检 |
| 自己能力的**必过检查**；新增检查能力（含目标约束种类） | `capabilities/*.py`（`role: CHECK`）与声明里的 `final_checks`，必带 `fixtures/` | 封存终检 |
| **知识**（规则、阈值、来源） | `knowledge/*.json`，被检查能力读取 | 封存终检（作为数据） |
| 模板；文案 | `templates/*.json`、`text/*.json` | 不属于检查 |

| Kit 不能改 | 靠什么挡住 |
|---|---|
| 计划里加检查字段 | **格式里没位置**：`pipeline-v1` 不允许多余字段，没有检查字段 |
| 放宽或删掉核心检查；改基础档位、输出角色词表 | **注册时只追加**：重名即冲突，必过项取并集；`profiles.json` 与词表是底盘数据，清单里没有对应键 |
| 写日志、自带渲染、自带入口、import 引擎或检查层 | **机器检查拒绝**：Kit 的 Python 只许 import `kernel.public`、`biology.public` 与自己的包；结构测试扫到即构建失败 |
| 改裁决形状、词表、封存步骤 | **根本没有接口**：裁决必须经 `kernel` 的构造函数且值取自词表，封存只在 `assurance` |

*Kit 的「工作流」是流水线模板*；*「领域知识」是数据*；*「报告」是文案*（摘要与卡片由底盘通用渲染器生成，Kit 不得带渲染代码）。非 DNA 的 Kit（Revival Evidence）同样适用：能力的输入是观察记录文件，输出角色 `analysis`，没有 `preparation_model` 检查；它只是 Kit 形式的另一个例子，不是另一类 Kit。Kit 的四个领域词（如 `SUPPORTED`/`INSUFFICIENT`）写在 Kit 自己的文案与数据类型里。

*路由*：宿主靠 `SKILL.md` 的 `description`（写成触发条件，含「不该用」的情形）自己选 Kit；顶层 `SKILL.md` 只是目录页。

**不采用**：Kit 带自己的入口脚本；在沙箱里运行外部 Kit（v1 不做，写进展望，以后在执行层外面加壳，不改结构）；Kit 之间共享代码（共享的东西进底盘的 `biology`）；Kit 新增交付档位或输出角色。

**失败时怎么办**：清单不合模式 → `KIT_MANIFEST_INVALID`；版本不符 → `KIT_CORE_INCOMPATIBLE`；名称冲突 → `KIT_NAME_CONFLICT`；装载期间抛异常 → 回滚其已注册的贡献。均只影响该 Kit，诊断可查。

**怎么测**：用**仅测试用的玩具 Kit**（包外临时目录）：插入后 `describe` 看得见且能运行；拔掉后注册表与装载前逐项一致；坏清单、版本不符、重名冲突、装载抛异常各一例；坏邻居不影响好 Kit；玩具 Kit 声明一个 `final_checks` 并验证它出现在必过项里；INV-K1…INV-K7；**路由测试**（每个 Kit 3–5 条自然语言请求，含模糊与不该用的，由隔离的非开发 agent 在不被告知 Kit 名时选择，保留首次失败记录）。

**来源**：目录与清单、装载规则、模板即工作流、知识即数据、路由与测试 C-D11；清单只含声明、冲突双禁用、目录快照固定 A-D11；Kit 的贡献收成四样、对检查系统唯一入口＝三字段、取消 Kit 新增档位、`text` 写入清单 M。依据：[已读] 旧 `core/kits.py` 与四个 Kit 的流程代码；[设计] 其余。

---

## D12 知识层

**结论**：领域知识分成两类，各有归宿：**数据**（规则、阈值、标记表、结论真值表）放进带来源的 `rule-v1` 文件；**算法**（扫描器、模拟器）留在代码里（`biology`），只从数据读阈值与适用条件。每条数据都有来源；审核状态只能由人写；规则的改动会改变目录快照。

**问题**：旧生物学自检（`core/guardrails/checklist.py`，857 行）把阈值与条件写在代码里；规则 JSON 三份、Kit 的规则表、成熟方法里的算法选择、说明文档，只有一部分带来源与审核 [已读/已量]。**好的部分**：规则 JSON 的字段已统一；旧系统要求来源类型并拒绝 `AI/internet/latest` [已读]。

**决定**

*规则 `rule-v1`*

```json
{
  "schema": "rule-v1", "id": "marker.selection.ble", "name": "Bleomycin/Zeocin selection for yeast",
  "version": 1, "status": "active", "purpose": "interpretation",
  "evaluator": "cut_plasmid.assess_selection",
  "parameters": {"marker_id": "ble", "selection": {"yeast": ["Zeocin/phleomycin medium"]}},
  "applies_when": [{"field": "marker_id", "op": "eq", "value": "ble"}],
  "source": {"source_class": "official_method", "citation": "…", "locator": "…", "retrieved_at": "2026-10-14",
             "content_ref": null, "archive_note": "not archived",
             "supports": ["Zeocin is used to select ble in yeast"],
             "does_not_support": ["Measured resistance in the user's strain"],
             "verification_status": "verified",
             "verification_receipt": {"by": "（姓名）", "method": "（方法）", "date": "（日期）", "scope": "（范围）"}},
  "limits": ["Requires the strain genotype; unknown genotype yields UNKNOWN"],
  "review": "knowledge/review/marker.selection.ble.review.json"
}
```

- `purpose` ∈ `mandatory_check`（硬性要求）、`interpretation`（解释）、`advisory`（建议）；三种**分开标明，不合成一个分数**。`applies_when` 的运算符封闭：`eq` `in` `gte` `lte` `between` `exists`，由注册的代码求值；**适用所需的信息缺失 → `UNKNOWN`，不是 `FAIL`**。`evaluator` 指向目录快照里已注册的能力（可以是 `ACTION` 或 `CHECK`），即消费这条规则 `parameters` 的那个能力。
- **来源逐条必填**，且写明它**支持什么、不支持什么**：「项目约束」只能支持「我们采用此边界」，不能支持「生物学已证明」。`verification_status: verified` 要有核验回执（核验人、方法、日期、范围——**由人填，AI 不得填**）。**没有来源的规则无法装载。**
- **算法与数据分离**：扫描器（自切风险、终止信号、重复序列、发夹……）是 `biology` 里的受审计分析函数，被检查能力调用；其**阈值、适用条件、严重程度**放在 `rule-v1` 数据里。分析函数在声明里写明算法来源（文献），阈值数据逐条写来源。
- **知识包**：一个文件夹，含规则文件、`review/`、`SOURCES.md`（人类可读的来源汇总，由数据生成）。内置包在 `dna_design_core/knowledge/packs/`，Kit 的包在 Kit 目录里。
- **三个可信度问题，各一个词**（§1）：`status`（还在不在用）、`verification_status`（来源核验过吗）、`review`（人审过吗）。
- **经验规则**（实验室经验的自然语言记录）：只能以 `status: draft`、来源类 `lab_protocol`、行为者 `human` 进入；**自然语言到规则的转换结果必须经人确认才变成 `active`**。
- **结论真值表**（如 Revival Evidence 的「只有菌落形成不能支持功能复活」）同样是 `rule-v1` 数据，不得扩张其科学结论范围。无数据不等于阴性；没有全基因组检查，不能从几个局部 PCR 推全基因组消除。
- 旧的三份规则 JSON 字段已统一，可迁移；旧的只被旧装配规划入口使用的 `evaluate_plan` 不迁移。

**不采用**：把所有生物学知识都改成数据（扫描、模拟无法用数据表达，硬做就是新语言）；来源写在文档里不写在数据里（会再次漂移）；让 AI 把自然语言规则直接激活；「来源 URL 非空即正式启用」。

**失败时怎么办**：来源缺失或类型非法 → 知识包装载失败（`KNOWLEDGE_SOURCE_INVALID`），依赖它的检查记 `UNKNOWN`；审核记录哈希与文件不符 → `stale`，不阻止运行，但清单与卡片显示「审核已过期」。

**怎么测**：规则模式正反例；来源缺失被拒；`AI/internet/latest` 被拒；INV-N2 的数值字面量扫描（**启发式**，含白名单机制自测）；每个数据化的生物学规则有 PASS/FAIL 样例；规则改动后旧 run 的目录快照不变；适用信息缺失产生 `UNKNOWN`（INV-N5）。

**来源**：算法与数据分离、`rule-v1`、来源与审核落点、经验规则 C-D12；规则指向已注册的评估函数、`purpose` 三分、`supports`/`does_not_support`、适用缺信息＝`UNKNOWN`、不得扩张结论范围 A-D12；可信度三词并列 M。依据：[已读/已量] 旧自检函数与三份规则 JSON；各条规则的具体内容 [未核实]，迁移时逐条核对来源。

---

## D13 宿主接口

**结论**：宿主 AI 看到的所有说明——有哪些能力、怎么填、哪些模板、有哪些检查、每个 Kit 什么时候该用——**由声明生成**；手写的只有「使用协议」与 Kit 的触发描述。命令行只有一套**封闭**动词，统一回执，错误带 `recovery`。默认英文。

**问题**：旧入口多（6 个真正的任务入口，另有收尾、核对两个支持脚本和一个示例脚本，以及宿主自写脚本）[已量]；说明文档靠手写、随分支前进而落后，没有一致性机制；上一轮三个隔离测试里输入格式门槛一再出现 [已读]。

**决定**

*唯一入口*：Python API `application.api` 与命令行 `grt`（同一份实现，命令行是薄封装）。动词登记在 `application/verbs.json`，**变更需改规格**。

| 动词 | 作用 | 写日志 |
|---|---|---|
| `describe [capabilities｜capability <id>｜templates｜template <name>｜checks｜goal-kinds｜kits｜vocab]` | 查看声明（由 JSON 生成，不 import 任何能力实现） | 否 |
| `run create <dir>` | 建运行目录，写环境指纹、目录快照、Kit 回执 | 是 |
| `goal declare｜amend` `--request FILE` | 提交或修订目标 | 是 |
| `template instantiate <name>` `--request FILE` | 由模板生成流水线草稿（只输出） | 否 |
| `pipeline submit｜revise` `--request FILE` | 提交或修订流水线（接纳校验） | 是 |
| `declare` `--request FILE` | 记录一条声明（行为者一律记为 `ai_host`，宿主不能自称 `human`） | 是 |
| `run execute [--until s3]` | 执行待执行步骤 | 是 |
| `run abandon [--reason 文字]` | 放弃 run（终态；已封存的不能放弃） | 是 |
| `status` | run 状态、各步状态、最近裁决、下一步建议 | 否 |
| `judge [--also id]` | 封存终检的试跑（对象 `candidate`），不封存 | 是 |
| `seal [--also id]` | 暂存 → 封存终检 → 封存或拒绝 | 是 |
| `verify <运行目录或封存目录>` | 复核 | 是（在运行目录内时） |
| `record render [--level --lang]` | 重新生成视图 | 否 |
| `review sign` | 创建审核记录（要交互式确认，D20） | 否（写审核文件，不写日志） |
| `doctor` | 检查环境与可选依赖，**只输出指引，不安装任何东西** | 否 |

- **请求文件**：带内容的动词用 `--request FILE`（UTF-8 JSON）；只带标识的动词用命令行参数。这避开 Windows 中文终端的引号与编码问题。
- **回执信封**（所有动词的 JSON 输出）：`{run_id, state, event_range, result, problems[], next[], labels[]}`。`problems` 里每项含 `code`、`category`、`message`、`location`、`recovery`。`--format json|text`，text 由 json 渲染。
- **退出码**：见 §1 与 D14。**退出码不是科学裁决**：`judge` 返回 0 且含 `FAIL` 裁决是正常的；`seal` 被必过项拒绝返回 10。
- **文档生成**（`tools/docgen.py`，输出入库，CI 校验「生成物与声明一致」）：顶层 `SKILL.md`＝手写「使用协议」（≤2 页）＋生成的目录；每个 Kit 的 `SKILL.md`＝手写 frontmatter（`name`、写成触发条件的 `description`）＋生成的输入契约（模板参数、必过检查、`does_not_establish`）；`docs/capabilities.md`、`docs/checks.md`、`docs/vocabulary.md` 纯生成；`examples/` 下的合成示例同时是测试。
- **语言**：能力与检查的描述、报告、卡片默认英文；中文通过 `text/` 资源按键翻译，缺翻译回退英文；程序事实（状态词、标识）不翻译。
- **宿主最低能力**：能访问用户授权的文件、运行本地命令、读写 UTF-8 JSON、保留回执。纯文本问答或浏览器聊天只能算「指导模式」，**不能计为程序独立运行成功**。
- **不走正式路线**：不拦截。`SKILL.md` 写明：只有经 `seal` 封存的文件是正式结果，其他输出带「未封存」标签；宿主自写脚本的结果不在 Toolkit 的核对范围内。

**不采用**：每个 Kit 一个入口；一个超长的 `run` 命令隐含所有操作（修订与失败恢复不可见）；说明文档手写后人工同步；`doctor` 自动安装依赖（旧系统有一个由环境变量打开的自动 `pip install`，会联网）。

**失败时怎么办**：未知动词或参数 → 退出码 1，附最接近的动词与 `describe` 提示；`describe` 对不可用能力显示原因而不是让它消失。

**怎么测**：动词登记与实际注册一致（INV-H1）；生成区块新鲜（INV-H2）；信封模式（INV-H3）；`describe` 在不能 import 任何能力模块的受限环境里可用（INV-H4）；手写区不含数量、版本、清单（INV-H5）；请求文件（INV-H6）；非 ASCII 路径与 JSON 内容；隔离 agent 的端到端真实测试（D18）。

**来源**：封闭动词、信封、文档生成、`doctor` 只给指引 C-D13；请求文件、宿主最低能力与指导模式、「退出码不是科学裁决」A-D13；`describe checks` 取代检查器目录、`review` 补入动词表、`run execute --until` M。依据：[已量/已读] 旧入口数量与自动安装；[设计] 其余。

---

## D14 状态词、错误与失败记录

**结论**：所有状态词、错误码、类别登记在两份数据文件（`vocab.json`、`errors.json`），枚举与文档由它们生成。**一种错误类型**（带类别）。**一条总规则分清三种「结果」**：

> **判断一个对象好不好 → 裁决。操作没被接受或没做成 → 失败记录（含先决条件不满足）。只是补充信息 → 标签。**

**问题**：旧异常家族十余个，还有同名的 `ExecutionError` 与重复的 `BackendUnavailable`；`PlanningError` 87 处、`ValidationError` 52 处、`GateRejected` 47 处 `raise`；规定四个状态词，代码里却另有 `NOT_CHECKED`、`UNCHECKED`、`MISSED`、`INCOMPLETE`；常按冒号前缀解析错误码 [已量/已读]。

**决定**

- **词表**见 §1，是权威版本；`vocab.json` 机器可读，每项一句定义。
- **错误模型**：只有 `ToolkitError(code, category, message, details, recovery, retryable)`；`CapabilityError` 只是固定 `category=CAPABILITY_FAILURE` 的便捷子类，**不是新家族**。类别写在回执信封里，退出码只分 0、1、10（§1）；`CAPABILITY_FAILURE` 作为失败记录返回（run 进入 `HALTED`）。
- **失败记录 `failure-v1`**：`{code, category, message, details, recovery, retryable, cause_chain}`；`details` 不含原始序列，只放长度与哈希；`cause_chain` 保留嵌套调用的子失败。
- **错误码**登记在 `errors.json`：`{code, category, meaning, recovery, introduced_in}`；命名 `AREA_THING`，如 `PLAN_REF_UNRESOLVED`、`STEP_INTERRUPTED`、`STEP_EXPECTATION_FAILED`、`CAPABILITY_UNKNOWN`、`CHECK_UNAVAILABLE`、`KIT_NAME_CONFLICT`、`SEAL_RUN_NOT_COMPLETED`。
- **抛出与捕获**：能力与规范化代码抛 `ToolkitError`，不抛裸异常。**只有两处把一切规范成失败记录**：调用器边界（含检查能力的调用）和 `application` 的命令行顶层（DEP-13）。其余位置只能捕获指名的异常类型。
- **检查结果永远不是异常**（INV-A1）：检查返回裁决；封存被拒也不是异常，而是 `seal.rejected` 事件加未满足清单加退出码 10。
- **调用成功≠通过**：`Outcome` 里没有 `ok/verified/ready` 之类的资格布尔；步骤完成与检查通过是两件事。一个检查能力技术上成功地返回了 `FAIL` 裁决，步骤仍是 `COMPLETED`。

**不采用**：全程序只用 `PASS/FAIL`；每个 Kit 自定义 `error/status`；保留 `ready/ok/all_applicable_pass` 之类多个资格布尔；按 `CODE: text` 解析决定分支；保留异常家族并加专用类。

**失败时怎么办**：词表测试失败即构建失败；新增词必须先改 `vocab.json`/`errors.json` 并附理由。

**怎么测**：字面量扫描（含自测：故意放一个不在词表里的 `outcome="PASSED"`）；错误码登记扫描；异常类定义扫描；失败记录模式测试；检查模块里没有 `raise`，除非是调用器边界的包装。

**来源**：词表、一种错误类型、失败记录、检查结果不是异常 C-D14；按对象分状态、`Outcome` 无资格布尔、调用成功≠通过 A-D14；三种「结果」的总规则 M。依据：[已量/已读] 旧异常与状态词；[设计] 其余。旧状态词与旧错误码的映射见 `MERGE-LEDGER.md`。

---

## D15 仓库、目录与发行结构

**结论**：新版是一个独立仓库，源码、Kit、测试、工具、文档各有固定位置；**面向评委的包与面向开发者的仓库由同一棵树按清单构建**，没有手工拷贝的第二套。开发专用文件放 `dev/`，不进评审包。

**问题**：旧系统有两层目录和两个远端；`snapgene-dna-design/` 里有 94 MB、33 个打包目录和多份源码快照，还有同名嵌套文件夹；测试按开发阶段命名（`test_final_*`、`test_dev2_*`、`test_historical_*`、`test_engineering_*_audit`），116 个文件、约 2.6 万行、1202 个测试函数 [已量]。

**决定**

```
genome-revival-toolkit/
├─ VERSIONS.json                 版本唯一手写来源（D16）
├─ contracts.toml                依赖契约（D1）
├─ README.md  LICENSE  THIRD_PARTY.md（生成）  pyproject.toml（动态读 VERSIONS.json）  requirements*.txt
├─ src/dna_design_core/
│  ├─ kernel/        ids.py canonical.py material.py vocab.py errors.py schemas.py verdict.py ports.py redact.py release.py public.py
│  ├─ biology/       formats/ sequence/ pcr/ primer/ restriction/ assembly/ crispr/ analyzers/ public.py
│  ├─ storage/       journal.py chain.py lock.py recovery.py store.py read.py（只读接口，供 record 使用）
│  ├─ knowledge/     schema.py loader.py review.py packs/
│  ├─ catalog/       registry.py kits.py snapshot.py selectors.py
│  ├─ capabilities/  builtin/{format,seq,primer,pcr,restriction,assembly,mutagenesis,crispr,verify,check}/
│  ├─ engine/        goal.py pipeline.py normalize.py admission.py executor.py invoker.py revision.py session.py view.py
│  ├─ assurance/     obligations.py judge.py stage.py seal.py verify.py labels.py
│  ├─ record/        projections.py declarations.py render/{report,runcard}.py i18n/
│  ├─ application/   run_service.py api.py cli.py describe.py config.py verbs.json
│  └─ resources/     schemas/*.json  capabilities/*.json（生成）  profiles.json  vocab.json  errors.json  text/
├─ kits/{construct,genome-identity,revival-evidence,cut-plasmid}/      结构见 D11
├─ skill/            SKILL.md（手写协议 + 生成目录）
├─ examples/         合成数据示例（兼作测试）
├─ tests/{structure,contract,unit,integration,e2e,fixtures,oracles}/
├─ tools/            build_release.py export_declarations.py docgen.py verify_release.py check_fixtures.py spec_lint.py
├─ docs/{judges,developers,decisions}/
├─ ship.json         发行包包含与排除清单
└─ dev/              AGENTS.md  CLAUDE.md  计划与归档（不进评审包）
```

- **命名**：仓库 `genome-revival-toolkit`；Python 包 `dna_design_core`（底盘名 DNA Design Core）；发行 Skill 目录 `genome-revival-toolkit/`；Kit 目录用连字符名（`cut-plasmid`），其 Python 模块名由装载器映射为 `grt_kit_cut_plasmid`。**产品名只在发行包名、文档、`SKILL.md` 里出现**，不是源码的目录层级。`snapgene` 字样只出现在指称文件格式或第三方库的地方（`.dna`、读取库）。
- **两类读者**：评委与外部用户读 `docs/judges/`（README、架构概览、安装与运行、如何新增 Kit、验证结果与诚实的限制）和发行包（含一个已封存、可 `verify` 的示例）；开发者（含 AI）读 `docs/developers/`（本规格定稿版、不变量清单、决策记录）与 `dev/`。
- **`ship.json`** 决定哪些进评审包与官方 GitLab：`src/`、`kits/`、`skill/`、`examples/`、`tests/`、`tools/`、`docs/judges/`、`docs/developers/`、`README.md`、`LICENSE`、`requirements*.txt`、`.gitlab-ci.yml`；排除 `dev/`、内部决策、任何含个人路径的文件。
- **平台规则**（Windows 为主要环境）：所有文本读写显式 `encoding="utf-8"`；存储文档用 LF；存储文档里的路径一律运行目录相对、POSIX 分隔符，**不保存任何绝对路径**（输入文件的原路径不记录，只记副本的相对路径与 sha256）；不用 `shell=True`；非 ASCII 路径有测试；CI 同时跑 Windows 与 Ubuntu。
- **工作区卫生**：构建产物只在 `dist/`（被忽略）；仓库里不放源码快照或打包副本；`check_fixtures.py` 检查 `tests/fixtures/` 里每个序列文件都登记在 `MANIFEST.json`（合成：生成器与种子；或第三方：许可）。

**不采用**：延续两层目录；把 Kit 放进 `dna_design_core` 包内；仓库里保留发行副本以便对比（对比由构建脚本生成，不入库）；symlink、`PYTHONPATH`、动态查找旧安装。

**失败时怎么办**：任何不变量失败即构建失败；清单与目录不一致时，构建脚本列出差异并拒绝产出包。

**怎么测**：`tests/structure/` 下的文件系统测试（INV-F1…INV-F9）；`build_release` 的「干净检出 → 构建 → 解压 → 运行示例 → `verify` 示例封存包」集成测试；清空 `PYTHONPATH` 从空目录安装运行。

**来源**：目录树骨架、两类读者、`ship.json`、平台规则、工作区卫生 C-D15；`biology` 与 `application` 层、源码到安装包的逐文件映射 A-D15；`kernel/release.py` 补入、`tools/docgen.py` 只放一处、`spec_lint.py` M。依据：[已量] 旧目录与测试规模；[设计] 其余。

---

## D16 版本权威与发布流程

**结论**：版本只在一个文件 `VERSIONS.json` 里手写；其余地方（代码、清单、文档、`pyproject`）都是生成物或读取它。发行包带 `release manifest`（含代码清单与每个文件哈希），其摘要就是 `release_id`，装载时校验一次，不逐步重算。运行的可重现靠**准确内容的固定**，不靠版本标签。

**问题**：旧系统版本分散（`VERSION` 文件、各模块 `__version__`、Kit 清单、文档里的数字），Evidence Trace 在开发树里是 0.3.3、包里是 0.3.5；实现指纹靠运行时遍历源码计算 [已量/已读]。

**决定**

```json
{ "toolkit": "0.1.0", "core": "1.0.0",
  "kits": {"construct": "0.1.0", "genome-identity": "0.1.0", "revival-evidence": "0.1.0", "cut-plasmid": "0.1.0"},
  "schemas": {"goal": 1, "pipeline": 1, "pipeline-revision": 1, "capability": 1, "verdict": 1, "event": 1,
              "failure": 1, "kit": 1, "rule": 1, "review": 1, "manifest": 1, "catalog": 1, "config": 1} }
```

- 语义化版本；**模式版本独立于软件版本**，只在模式不兼容时升。具体产品版本号由负责人在发布时定，建议新架构用独立的预发布系列，避免被误认为与旧候选兼容。
- **`release manifest`**：构建时生成，含版本、构建标识、文件列表（路径加 SHA-256）、依赖清单；`release_id` ＝ 其摘要，装载时校验一次：已安装的发行包里清单与文件不符 → 报既有错误 `SOURCE_CHANGED` 并拒绝创建运行（不记任何 `release_verified` 字段，已删除这一写法）。`verify` 一个封存包时：封存清单的 `release_id` 是 `"dev-tree"` 则在任何环境都可验证（它不是发行证据，运行卡片照实显示）；是 64 位摘要而当前环境存在发行清单时，两者必须相同，不同则拒绝。开发树里无清单时，`release_id` 记字面量 `"dev-tree"`，并在 `run.created` 里另记 `git_commit`（40 位小写十六进制；取不到就省略）。`release_id` 只有两种取值：64 位十六进制摘要，或 `"dev-tree"`；`"dev-tree"` 产生的封存包不是发行证据。
- **环境固定**：`run.created` 固定 Python 与平台、依赖锁、**外部程序的可执行文件内容哈希**（路径不是身份）、配置摘要，以及规则、检查与 Kit 代码摘要（目录快照）。环境不完整时不宣称严格重放。
- **发布流程（每步有记录）**：1 冻结：结构不变量与完整测试在**这个精确提交**上于 Windows 与 Ubuntu 的 GitHub CI 全部通过；**官方 GitLab 没有执行器，CI 未执行，所有文档必须如实写明，不得把 GitHub CI 称为 GitLab CI**。2 构建：确定性构建（文件排序、固定时间戳）→ zip ＋ SHA-256 ＋ manifest。3 干净环境验证：新虚拟环境安装，跑全部示例，对内置示例封存包跑 `verify`，保存输出。4 发布记录 `RELEASE-RECORD.md`：版本、`release_id`、包哈希、CI 链接与提交号、**未执行项**（官方 GitLab CI、真人独立试用、湿实验）、已知问题、所有审核记录及状态——**由人逐项确认签署**。5 上传：由有权限的人（或其明确授权下的 Codex）传到**新的候选分支**，不覆盖已有分支、不推 `main`（`main` 需用户当场明确说）。6 官方源码读回：逐文件读回并计算哈希，保存为清单，与 manifest 对照。
- **iGEM 硬性要求**（官方 Software Project 页的 Requirements，用户 2026-10-16 提供截图）：①源码托管在 iGEM GitLab 的队伍专属仓库，别处的代码不参评；②`README.md` 说明软件做什么、给谁用、怎么安装与运行、怎么复现主要结果；③`LICENSE` 文件，OSI 批准许可（本项目：Apache-2.0，iGEM 的默认推荐；MIT 亦可；CC-BY 不适合代码）；④可复现的构建与运行步骤，**不上传编译产物**（`.exe`、`.bin`）；⑤提交锁定依赖版本的文件；⑥Git 仓库小于 50 MB，大文件放 Zenodo 并在 README 里引用；⑦软件若使用 AI 模型（自训、微调或调用商业接口），README 须写明用了哪些模型、训练或微调数据的来源、怎么评估、已知局限。发布记录逐项列出这七条的状态。
- **切换**：新版全部通过也**不自动解除冻结**；是否替换冻结候选只由负责人明确决定（D19）。

**不采用**：各处各写版本号再用脚本同步；用 Git 标签当唯一版本（评审包不一定带历史）；运行时遍历源码算指纹；运行时安装最新依赖；通过后自动上传。

**失败时怎么办**：构建的两次摘要不一致 → 阻止发布；干净环境验证失败 → 阻止发布；清单与官方读回不一致 → 在发布记录里标红并停止宣布发布。依赖无法锁定则对应平台或后端不进入支持矩阵。

**怎么测**：构建确定性（INV-W3）；版本字面量扫描（INV-W1）；装载校验的篡改测试；CI 报告必须绑定精确提交；不存在自动上传或冻结切换动作。

**来源**：`VERSIONS.json`、manifest、发布六步 C-D16；外部程序内容哈希、不自动解冻 A-D16；`pyproject` 动态读取 `VERSIONS.json` M（待用户确认，见 `OPEN-ITEMS.md`）。依据：[已量/已读] 旧版本分散、旧指纹；[已读 CLAUDE.md] 官方 GitLab 无 CI 执行器；[设计] 其余。

---

## D17 配置、联网、隐私

**结论**：软件在任何代码路径上**都不外发序列**；v1 不提供任何网络能力，也不在软件里安装任何东西。所有配置只在一处读取。输入材料留在本机运行目录，日志与清单只记标识、长度与哈希。**v1 不做代码沙箱**：外部 Kit 以用户的权限运行代码，只提示与记录；沙箱列入展望，以后在调用器外面加壳，不改结构。

**问题**：旧系统有 11 个环境变量分散各处，一个由环境变量打开的自动 `pip install`（会联网），好几个「同意回执」相关模块（操作同意、序列上传同意、CRISPOR 适配骨架、在线来源适配器）[已量/已读]；后来决定软件任何路径不联网、不外发 [已读 CLAUDE.md]。

**决定**

*配置*：只有 `application.config` 读取环境与文件。优先级：默认值 < 配置文件（`grt.config.json`）< 环境变量 `GRT_*` < 命令行参数；有 `config-v1` 模式；摘要写进环境指纹（无密钥）；**环境变量不得暗中覆盖科学参数**。

| 键 | 环境变量 | 默认 | 作用 |
|---|---|---|---|
| `primer3_core` | `GRT_PRIMER3_CORE` | 自动探测 | 引物设计程序路径 |
| `lang` | `GRT_LANG` | `en` | 报告语言 |
| `external_timeout_s` | `GRT_EXTERNAL_TIMEOUT` | 300 | D6 |

旧变量映射：`PRIMER3_CORE→GRT_PRIMER3_CORE`；`SNAPGENE_*` 不再识别（品牌名不再出现在配置键里）；`PRIMER3_AUTO_INSTALL` 删除。

*联网*：v1 没有任何联网的能力，词表里也没有联网这种副作用。`doctor` 只输出「请你运行这条命令」的指引。外部程序只经 `ctx.run_external`，记录名称、版本、内容哈希，命令用参数列表，有超时。**CRISPOR 等外部服务**：软件不联网使用；Cut Plasmid 的「模式 A」＝生成「该粘贴什么」的说明，用户自己去网站，再把导出文件作为外部来源文件导入（`input_origin: user_file`，标注「外部服务给出，未经本 Kit 重算」，分数不与本地因素混排）。

*隐私*：裁决证据、失败记录、事件的结果字段与报告默认不放原始序列，只放标识、长度、哈希与摘要；**唯一例外**是宿主自己写进目标与计划的短字面量（如 20 nt 间隔序列，每个不超过 200 nt，超过的必须作为输入文件，事件里只记哈希），它们会出现在 `goal.*`、`pipeline.*` 事件里，因此**封存包里的日志副本含这些短序列，对外公开前自行检查**；材料本体在运行目录的内容存储里（本机）；报告默认不含序列（`--include-sequences` 显式打开）；不保存输入文件的原绝对路径（只记运行目录相对路径与 sha256）；没有遥测；**用户真实 DNA 绝不进仓库**，测试只用合成数据。哈希是身份线索，也可能暴露材料关联，**不能称作匿名化**。

*对「零连接」的措辞*（A 的区分）：我们能证明的是**正常代码路径零次连接尝试**；我们**不声称**能挡住恶意代码联网，也不控制宿主自己的联网与云同步。

**不采用**：保留可选的自动安装；「问了再发」的同意流程（程序无法验证同意是真人给的，用户的靶序列可能未发表，根本不发更干净）；把 `network:false` 当隔离证明；自动配置整台电脑的防火墙；在 v1 做 Windows 受限进程沙箱（成本高、可行性未验证，且我们的威胁模型是疏忽而非对抗，见 §0）。

**失败时怎么办**：策略违反 → `POLICY` 类错误，日志留事件；缺依赖 → 只给指引；缺后端、缺基因组不联网补救。

**怎么测**：INV-X2 默认命令集与示例运行时**零次**网络连接尝试（子进程里把 `socket` 的 `connect`、`connect_ex`、`create_connection`、`getaddrinfo` 换成「计数并失败」（Linux CI 上可选再用 `unshare -n` 跑一遍以覆盖子进程；含自测：故意加一个联网调用，测试必须失败））；INV-X3 源码里没有 `pip`、`urllib`、`requests`、`http.client`、`socket`（测试工具白名单）；INV-X4 无 `shell=True`；配置优先级参数化测试；`doctor` 不执行任何安装。

**来源**：单一读配置点、不联网、隐私规则、零连接测试 C-D17；零次尝试与「被系统拦截」分开措辞、外部 Kit 全权限的如实说明 A-D17；沙箱降为展望（用户 2026-10-16 决定）、配置键去掉 `network` M。依据：[已量/已读] 旧环境变量、自动安装、同意模块；[已读 CLAUDE.md] 不联网决定；[设计] 其余。

---

## D18 测试与验收

**结论**：测试分五层，**结构不变量先跑、先过**，结构测试不过，其他绿都不算数。科学结果的正确性只用**独立答案**验收（构造出来的、手工核算并注明方法与来源的、已发表数值的、独立程序的），**绝不用待测代码或旧系统的输出当答案**。输出正确、结构收敛、宿主会用是三种不同的证据，三个都要，任何一个不能替代另一个。

**问题**：旧测试按开发阶段命名，约 24 项长期跳过，验收主要比较输出字节，造成「输出一致、结构没变」（Kit 迁移后仍走旧流程桥）[已量/已读]。旧系统里值得保留的：隔离子代理做端到端真实测试、「答案先定、来源独立」的纪律、零连接测试、固定种子合成夹具 [已读 CLAUDE.md]。

**决定**

| 目录 | 内容 | 何时跑 |
|---|---|---|
| `tests/structure/` | 依赖契约、词表字面量、错误码登记、动词登记、生成文档新鲜度、夹具登记、文件命名、哈希／环境变量／网络／`print`／宽捕获位置、Kit 包形状、无旧版引用、无样例身份特判、**契约充分性**、**规格自洽扫描** | 每次改动，**最先跑；失败则其余结果无效** |
| `tests/contract/` | 声明↔签名、`Outcome`／裁决／事件／失败记录的模式、规范化 JSON 黄金向量、检查能力的 PASS/FAIL 样例、目录一致性、Kit 清单、能力确定性 | 每次改动 |
| `tests/unit/` | 各模块单元测试；能力的独立答案测试 | 每次改动 |
| `tests/integration/` | 执行器＋日志＋存储＋检查＋封存（玩具能力）：修订、中断恢复、**日志尾部强杀**、哈希链篡改、多进程锁、封存幂等 | 每次改动 |
| `tests/e2e/` | 在干净虚拟环境里按文档步骤经命令行跑合成数据任务，并对封存包做离线 `verify` | 发布前与 CI |

*规则 TST-1…TST-11*（编号是稳定标识，删除不重排；测试的命名与目录组织属于开发测试说明 `dev/AGENTS.md`，不进规格）
- TST-1 **独立答案**：期望值只能来自 (a) 构造（生成器预先知道答案：随机合成序列、先定编辑再算供体）；(b) 手工核算，注明方法与来源；(c) 已发表数值并引用；(d) 独立程序（如 Primer3 命令行同参数）。**不得**用待测代码生成答案，**不得**把旧系统输出当答案；容差来自方法与后端规格，不得在观察到失败后临时加宽。若被测实现与参考用同一个库函数，该数值只算**回归预期**，不算独立交叉验证。
- TST-2 **覆盖要求**：每个能力至少一个独立答案测试；每个检查能力 PASS 与 FAIL 样例各一；每个 Kit 至少一个端到端示例（运行到封存并 `verify` 通过）。
- TST-3 **反空洞**：三处关键逻辑（`check.replay`、必过项推导、哈希链校验）做**人工变异测试**（翻转比较符、吞掉异常、跳过一步），发布前运行，断言样例能抓到；每个 FAIL 样例被实际执行并确认结果非 `PASS`。**静态扫描必须配动态探针和故意破坏的反例**，不能只搜关键词。
- TST-4 **跳过登记**：跳过只能用 `@skip_with(reason_id)`，原因登记在 `tests/SKIPS.json`（`id, reason, owner, expires`）；CI 打印登记表；未登记或过期的跳过失败；**SKIPPED 不算 PASS**，缺后端的集成测试不算通过。
- TST-6 **确定性**：固定种子，不联网，不依赖墙上时钟（时钟可注入）。
- TST-7 **真实测试方法**（用户已明确要求）：用打好的包在新空目录安装；起隔离子代理当用户，只给使用说明、自然语言任务与材料；答案先定、来源独立；全程留痕，失败不删，重复运行都报告；只回答三件事——做对了没有、错在哪、有没有帮过它；帮过的算「开发者辅助」，与自主完成分开；诚实声明宿主是哪个模型（子代理是 Claude 时，结果只说明「程序配这个宿主表现如何」）。**开发者不得读 heldout 答案；改完同题重跑不算新的独立证据。**
- TST-8 **阶段门**：① 结构测试全绿 → ② 契约测试 → ③ 单元与集成 → ④（若有）纵切面端到端 → ⑤ 生成文档新鲜。①未过时后面所有绿都不算。
- TST-9 覆盖率只报告不当目标。TST-10 Windows 与 Ubuntu 的 CI 同时通过。
- TST-11 **间歇失败**：保留失败现场两侧操作数的安全摘要，登记并限期，**不得因「重复运行都通过」宣布已修复**（旧 K 分支间歇失败的教训）。

*证据清单字段*（发布时随包）：`test_id`、源码或包引用、输入来源等级、预期来源（`construction|hand|published|independent_program`）、命令、退出码、结果、输出引用、跳过原因。作者自审、代理预演、真人读者是三种不同等级，不合并统计。

*新增的结构测试*（本稿合并时补入）：**契约充分性**（正文需要的跨模块调用必须是依赖契约允许的子集，INV-L5）；**角色降级无效**（INV-A6）；**缺失检查记 `UNKNOWN`**（INV-A5）；**日志尾部强杀恢复**（INV-E5）；**规格自洽扫描**（INV-S1…S6：事件名、动词、模块路径、规则编号是否对得上，并扫退役词残留）。

*科学正确性的独立答案来源（初始）*：`tests/fixtures/gen/`（固定种子生成器）：合成基因座与标记盒、合成质粒与已知方向与 PAM 的 gRNA（含差一位 PAM、插反）、合成观察记录（已知结论）；`tests/oracles/`：独立核对脚本（不 import `dna_design_core`，只用 Biopython 和标准库），如「按引物模拟反向 PCR ＋ 环化，得到的序列应与交付质粒逐位一致」；Tm 对照 Primer3 命令行。附录 B 的案例数据可直接作为首批夹具。

**不采用**：只比输出字节；只扫关键词；追求覆盖率数字；允许 flaky 测试自动重跑（会掩盖真实的不稳定）；被测算法生成标准答案。

**失败时怎么办**：CI 红＝不合并；不能解释的差异不得靠忽略字段或更新 golden 解决；独立评测失败时由管理者决定新评测。

**怎么测**：测试框架自测（故意违规 → 结构测试必须报错）；`SKIPS.json` 过期测试；`oracle` 字段完整性检查；变异测试的执行记录。

**来源**：五层、独立答案、夹具、变异、跳过登记、真实测试方法 C-D18；证据清单字段、动态探针配静态扫描、SKIPPED 不算通过、同值不算独立交叉验证 A-D18；新增结构测试 M。依据：[已量/已读] 旧测试命名与规模、跳过；[已读 CLAUDE.md] 真实测试方法；[设计] 其余。

---

## D19 首个纵切面、阶段与保底线

**结论**：先用一个**最小结构切片**证明主干对「单个工具」和「非 DNA」都成立，再用 **Cut Plasmid** 走通失败、修订、制备、检查、封存和卡片，然后用 **Revival Evidence** 证明结构不限于 DNA。首版（MVP）＝这两个 Kit；Construct 与 Genome Identity 是目标，不是最低交付。**保底线**：2026-10-17 内部冻结继续用现有 0.2.2 候选；2026-10-19 20:00（北京时间）新版没有通过全部验收，评委看到的仍是 0.2.2。

**问题**：直接搬四个 Kit 容易把旧 runner 藏进新壳；先造完整通用平台又可能耗尽冻结前时间。

**决定**

*首版（MVP）范围*：一个可安装包、一个命令行、统一主干；**两个 Kit**：Cut Plasmid（方向／PAM／载体自切检查、间隔序列替换、可模拟的制备计划与引物、筛选信息的边界）与 Revival Evidence（有来源的观察与预测比较、有限的结论边界）；默认英文离线运行卡片；生成的宿主说明。

*明确不做*：旧接口兼容；全部旧方法覆盖；远程数据库与自动提交；第三方程序捆绑；通用条件语言；跨机服务；任意第三方 Kit 的认证；代码沙箱；密码学签名审核；全基因组结论；湿实验成功；对继承自模板的诊断设通用豁免（只有 D7 的两项内容检查按逐项比较处理）。**新名字不是扩展科学边界的理由。**
*展望（未做，不进首版）*：探索／预览模式（现在想先试试就不封存，结果照常给，标「未封存」；若将来要「检查较少的预览包」，必须把少做的检查清单写进包里，且永远不能当作正式交付）；代码沙箱（在调用器外面加壳，不改结构）；联网取序列与外部服务的自动提交；Construct 与 Genome Identity 两个 Kit。

*阶段*

| 阶段 | 入口 | 产出 | 退出验收 | AI 最易跑偏／防护 |
|---|---|---|---|---|
| **S0 契约与探针** | 用户确认本稿的待决项 | `contracts.toml`、`vocab.json`、`errors.json`、`profiles.json`、各模式（由附录 A 展开，**人审定**）；探针：日志尾部强杀与 Windows 重命名重试、JCS 黄金向量、`spec_lint` | 结构测试骨架在空树上全绿；探针通过 | 只写接口壳／先写反例探针再铺功能 |
| **S1 最小结构切片** | S0 门通过 | `kernel`、`storage`、`catalog`、`engine`、`assurance`、`application`、`record` 的最短链；两个玩具能力（单工具、非 DNA 的两步链）走完三个检查时刻、封存、复验、卡片；玩具 Kit 插入与拔掉 | 无计划不能执行；接纳零调用；无需强制 `Molecule`；无手工埋点；INV-L、INV-P、INV-A 结构测试全绿（其中 INV-A10 需要真实的 CDS／注释继承比较，随科学检查在 S2 实现，不在 S1 门内） | 建第二个非 DNA 入口／调用器 spy 与动态探针 |
| **S2 Cut Plasmid 纵切面** | S1 门通过 | 附录 B 案例 2 完整跑通：初检失败、事前修订、替换、制备模拟、检查、文件读回、封存、卡片 | 原目标保持、外部序列不变、方向／PAM／自切及制备检查、报告含失败；筛选未知如实列入「Not done」 | `replace` 结果自证或字符串环化／独立反应计算与边界输入 |
| **S3 Revival Evidence** | S2 无无法解释的差异 | 案例 3；规则表数据化且逐行带来源；实线数据链 | 仅菌落计数不得得出「功能复活」；没有 `Molecule` 也完整通过 | 把项目约束写成已证实的生物学／`supports` 与 `does_not_support` |
| **S4 发行与外部验收** | S2、S3 的技术与科学门通过 | 完整包、生成文档、卡片、隔离宿主评测与读者材料、发布记录 | 空目录安装、源码映射、精确提交的 GitHub CI、独立评测；跳过如实列出 | 开发者重复题当独立成功／冻结包与隔离管理 |
| **S5（MVP 之后）** | S4 | Construct 与 Genome Identity 迁移，其余旧方法按批 | 同主干，无旧桥，各自独立答案 | 照搬 runner／依赖门加独立构造预期 |

每阶段先过结构门、再过科学门；某阶段的门没过，不得进入下一阶段，超出范围的需求先登记，不实现。

*保底线与切换*

| 判断点 | 必须检查 | 动作 |
|---|---|---|
| 开始开发前 | 本稿待决项是否已确认；审核职责与探针 | 未确认则只做获准部分，不发布 |
| 10 月 17 日内部冻结 | 新版是否已通过 S4 | 没有则旧 0.2.2 继续冻结，新版独立分支保留 |
| 10 月 19 日 20:00 | MVP（S0–S4）是否全齐 | 任一必要项未完成即确定旧 0.2.2；无「基本通过」 |
| 新版全部通过且仍有上传时间 | 负责人是否**明确**批准冻结后切换；文件清单与证据是否匹配 | 只有明确批准才切换；通过测试不自动解除冻结 |
| 官方截止前 | 实际上传版本、说明与证据是否一致 | 不把设计、预演或 GitHub CI 称作官方 GitLab CI |

**重要的现实**：MVP 只有两个 Kit，而 0.2.2 有四个，所以**MVP 本身不能替换 0.2.2**；10 月 19 日前能做到的最好情形是新结构作为「下一版」与架构说明，除非 S5 也完成。我对在截止前以新版**完整替换**0.2.2 的概率估计为**低**（估计，非测量）；S1 完成后做一次进度实测再更新。0.2.2 是用户指定的回退候选，不是本轮重新认证的产品；Wiki 的主体不应押在新版上。

**不采用**：先搬四个 Kit 再验结构；只做一个玩具 Kit 就宣布可扩展；为赶截止保留临时旧桥；用「基本通过」模糊判断点。

**失败时怎么办**：停在首次未通过的阶段，记录缺项、可复核失败与下一最小动作；不无声缩小检查赶进度；隔离或事务类探针失败要带具体证据回到设计决定。

**怎么测**：`MVP-01` 发行清单要求两个 Kit 的支持范围都有公共入口证据；`MVP-02` 故意移除一个必过项时候选资格失败；`MVP-03` 样例包不含旧桥或玩具实现；`MVP-04` 三个案例全部经同一接口运行；`MVP-05` 正式卡片准确区分已核查设计、模拟与未做实验。日期切换是人工决策，不靠程序自动推送。

**来源**：两个纵切面、保底线时间点 C-D19；最小结构切片先行、S0 探针、阶段门与「不自动解冻」A-D19；MVP 取两个 Kit（用户 2026-10-16 决定）、去掉沙箱与签名探针、明说 MVP 不能替换 0.2.2 M。依据：[设计]；工期未实测 [未核实]。

---

## D20 人工审核

**结论**：审核是一份**独立的、由人写的记录**，绑定被审文件的**哈希**，文件一变自动变为「过期」；AI 工具不得创建。各处统一显示审核状态：`none`／`draft`／`reviewed`／`stale`。**审核是声明，不是认证**；它**标注而不阻断**：没有人审的内容照常使用，但交付清单与卡片如实写「AI 起草，未经人工审核」。

**问题**：用户要求规则、库条目、Kit 设计都有「人工审核」的落脚点，且「审核人和日期只能由人填写」；旧系统有来源与验证回执，但没有「审核」这一层，也没有「AI 起草、未经审核」的显示 [已读]。

**决定**

*审核记录 `review-v1`*（每个被审对象一份文件，放在对象旁的 `review/`）

```json
{
  "schema": "review-v1",
  "object": {"kind": "rule-pack", "id": "cut-plasmid.selection_markers",
             "path": "knowledge/selection_markers.json", "sha256": "…"},
  "reviewer": {"name": "（姓名）", "role": "（角色）"}, "date": "（审核日期）",
  "scope": "（审核了什么、没审核什么）", "decision": "approved", "notes": ""
}
```

- 可被审核的对象：`rule-pack`、`rule`（行级）、`pipeline-template`、`kit`（清单与触发描述）、`capability`（算法来源与限制，含检查能力）。
- **状态**：`none`（没有记录）、`draft`（`decision: changes_requested`）、`reviewed`（`approved` 且哈希匹配）、`stale`（哈希不匹配）。
- RV-1 审核绑定被审文件当前字节的哈希；文件改动后自动 `stale`，无需任何人记得去更新。
- RV-2 审核记录只由 `grt review sign` 创建；它要求**交互式确认**（输入姓名并键入确认语），非交互环境默认拒绝，宿主 AI 因此无法顺手生成。**诚实说明**：程序无法验证键入者是不是真人，这是「签注」不是「认证」；防止 AI 直接写文件靠的是流程规则（`AGENTS.md` 禁止 AI 创建或修改 `review/` 下的文件）与发布时的人工清点。
- RV-3 审核人与日期**只能由人填**；缺失或为空 → 按 `draft` 处理。**团队声明**：`reviewer.name` 可以是团队名（本项目：`iGEM Tianjin 2026`），`reviewer.role` 写 `team declaration`；声明由团队成员在对话中作出，程序与 AI 都无法验证团队内部是否确有共识，卡片与文档如实写「团队声明」。
- RV-4 **统一显示**：`describe kits`、封存清单的 `labels`、运行卡片都显示每个 Kit 贡献条目的 `reviewed x / stale y / none z`，以及本次 run 实际用到的规则与模板各自的状态。**未审核的内容写「AI 起草，未经人工审核」，不沉默。**
- RV-5 库里的模板显示为「已审核」当且仅当 `reviewed`；没有「成熟」一词。
- RV-6 起草者信息：规则、模板与能力带 `authorship{kind: ai|human|mixed|unknown, tool_or_model, date}`，供负责任 AI 使用页引用，**不是质量保证**。
- RV-7 发布流程（D16）第 4 步的发布记录必须列出本版包含的所有审核记录及其状态，**由人逐项确认**。

**威胁模型的说明**：本机制防的是**AI 疏忽和顺手编造**，不防蓄意伪造；不提供密码学保证，不阻断交付（用户 2026-10-16 决定，理由：首版若要求签名阻断，没人建好密钥保管就一个封存包都出不来，而且 AI 与密钥同机时签名也防不住）。

**不采用**：把审核状态做成规则文件里的一个字段（任何人改文件时顺手改一下就能「通过」，也不会随内容变化失效）；数字签名阻断；要求所有内容都已审核才能发布（会把发布卡死）。

**失败时怎么办**：`stale` 不阻止运行，但清单与卡片显示「审核已过期」；`review sign` 在对象文件不存在或哈希无法计算时拒绝。

**怎么测**：四种状态的显示；改动被审文件后自动 `stale`（INV-RV1）；非交互拒绝且不写文件（INV-RV2）；清单标签覆盖本 run 用到的每条规则与模板（INV-RV3）；代码里除 `review sign` 外没有写 `review/` 的调用（INV-RV4）。

**来源**：审核记录与哈希绑定、四种状态、统一显示、流程规则 C-D20；人审与 AI 会话分离、承认程序验不了真人 A-D20；标注不阻断、去掉「成熟」一词 M。依据：[已读] 旧来源与核验回执；[设计] 其余。

---

# 附录 A 字段表（各模式的权威草表）

> 这是各模式（schema）的字段草表，S0 阶段展开成 JSON Schema 2020-12 并**经人审定后**才进入 S1。默认 `additionalProperties:false`；时间一律 UTC、RFC 3339；路径只作受控定位，不作身份；摘要字段一律 64 位小写十六进制。**未在表中列出的字段不得加入**，需要时写 `QUESTIONS.md` 并停在该处。

**A1 `goal-v1`**：`schema`、`version`（整数，从 1 起）、`parent_digest`（首版 null）、`original_request`（字符串，宿主报告的用户原话）、`sources[]{source_id, path, sha256, input_origin, as(material|artifact，缺省按格式判断), declared{}}`（存储形式；请求里用 from 代替 path 与 sha256，见 D2）、`declared_context[]{id, kind, text, origin(actor), basis_sources[]}`、`targets[]{id, role(输出角色), required}`、`constraints[]{id, check(检查能力 id@精确版本), params{}, target, source_quote, origin(user_quoted|host_derived), status(active|dropped), drop_reason?}`、`intents[]{id, text, source_quote, binds[]}`。

**A2 `capability-v1`**：公共：`schema`、`id`、`version`、`role(ACTION|CHECK)`、`summary(≤200)`、`effects[]`、`deterministic`、`requires_runtime[]{kind,name,probe}`、`inputs[]{name,type,required,constraints,description,schema_ref?,schema?}`、`params(JSON Schema)`、`outputs[]{name,type,schema_ref?,schema?,output_role}`、`step_checks[]`(检查能力 id)、`final_checks[]{check,params?}`、`model?`(能力 id)、`does_not_establish[](非空)`、`source{algorithm_refs[],implemented_in}`、`owner(core|kit:<name>)`、`granularity(atomic|composite)`、`authorship?`（见 A9 说明）。仅 `CHECK`：`scope`、`evaluates_constraint`、`offline`、`fixtures{pass,fail}`。`CHECK` 的 `effects ⊆ {pure, reads_files}`。

**A3 `pipeline-v1`**：`schema`、`version`、`goal_digest`、`steps[]{step_id, use(id 或 id@版本；存储时一律是 id@精确版本), inputs{名→引用}, params{名→值或引用}, why(1–400), expects?{on, op, value}}`、`outputs[]{name, from(引用), target}`、`library_ref?{name,version,template_digest}`。**引用**恰为：`{literal}`、`{source}`、`{step,port,index?}`、`{artifact}` 之一；`expects.on` 是引用加可选 `pointer`（JSON Pointer，指入文档或值类输出），`op ∈ equals|gte|lte|between|contains|length_equals`。**不含任何 `checks`、`gates`、`required_scopes`、`deliver_as`、`status`、`result` 字段。** 模板 `pipeline-template-v1`＝同上加 `params_schema` 与 `{{name}}` 占位。

**A4 `pipeline-revision-v1`**：`schema`、`expected_digest`、`trigger{kind(step_failed|check_failed|host_observation|user_request), step_id?, failure_code?, event_refs[], quote?}`、`reason`、`operations[]`（`add_step|supersede_step|set_outputs` 之一，字段见 D5）。

**A5 `event-v1`（信封）**：`seq`（从 1 连续）、`time`、`run_id`、`type`、`actor{kind,name,version}`、`payload`、`refs[]`、`prev`、`hash`。事件的结果与证据字段**不得出现原始序列**；目标与计划里的短字面量除外（≤200 nt，D17）。

**A6 `verdict-v1`**：见 D7；字段 `check{id,version}`、`scope`、`moment(step|final)`、`subject{kind,id}`、`constraint_id?`、`outcome`、`issuer`、`summary`、`evidence{}`、`basis[]`、`applicability{reason,basis}?`、`rule_refs[]`、`does_not_establish[]`。**`outcome=NOT_APPLICABLE` 当且仅当 `applicability` 非空。**

**A7 `failure-v1`**：`code`、`category`、`message`、`details{}`、`recovery`、`retryable`、`cause_chain[]`。

**A8 `kit-v1`**：见 D11。**A9 `rule-v1`** 与 **`review-v1`**：见 D12、D20。可选字段 `authorship?{kind(ai|human|mixed|unknown), tool_or_model, date}` 适用于 `capability-v1`、`rule-v1`、`pipeline-template-v1`（D20 RV-6），**不是质量保证**。

**A10 `manifest-v1`（封存包清单）**：`schema`、`run_id`、`release_id`、`goal_digest`、`pipeline_digest`、`revisions[]`、`journal_head`、`catalog_ids[]`、`environment_ids[]`、`files[]{path, sha256, role, labels[]}`、`verdicts[]{check, scope, outcome, verdict_event}`、`profile`、`not_verified[]`、`labels{}`、`review_states{}`、`kit_receipts[]`。**不含 `seal_id`，不含自身摘要。**

**A11 目录快照（`run.created` 引用的文档）**：`schema`、`release_id`、`capabilities[]{declaration(完整声明), declaration_digest, code_digest, owner}`、`knowledge[]{pack, digest, review{none,draft,reviewed,stale 计数}}`、`kits[]{name, version, manifest_sha256, code_digest, origin}`、`profiles`（完整内容）、`profiles_digest`、`vocab_digest`。

**A12 回执信封**：见 D13。**`config-v1`**：见 D17。

**A13 `profiles.json`**：见 D7 的基础档位表；结构为 `{always:[检查 id…], on_material_output:[…], roles:{construct:[…], primer_set:[…], component:[], analysis:[]}}`；底盘数据，Kit 不能增改；每个角色列出的检查所属范围由检查能力自己的 `scope` 声明给出。

**A14 内部形状（最小，由 S0 审核人确认）**：以下字段在前面只有名字，没有内部结构，统一如下，**未列出的内部字段不得加入**。
- `release_id`（`run.created`、目录快照、封存清单）：64 位十六进制摘要或字面量 `"dev-tree"`；`git_commit`（仅 `run.created`，可省略）：40 位小写十六进制。
- `requires_runtime[]`：`{kind(python_package|executable), name, probe}`；`probe` 是取版本的命令行字符串数组（如 `["primer3_core","-version"]`），`python_package` 时为 `null`。
- `failure.cause_chain[]`：`{code, message}`。
- `manifest.profile`：`{profiles_digest, obligation_ids[]}`。
- 回执 `event_range`：`{from_seq, to_seq}`，没有事件时为 `null`；尚无 run 时回执的 `run_id`、`state` 为 `null`。
- `run.created` 的 `environment.packages`：`{包名: 版本字符串}`；`created_by`、`goal.amended` 与 `run.abandoned` 的 `by`、`input.registered` 的 `declared_by`：同 `actor{kind,name,version?}`（`declaration.recorded` 用它自己的 `actor{kind,name}`，见附录 E）。
- `goal.amended` 的 `diff`：从上一版目标文档到新版目标文档的 JSON Patch（RFC 6902）数组。`pipeline.revised` 没有 `diff`，它的 `operations` 已经记录了变化。
- `step.completed` 的 `outputs.materials`、`outputs.documents`：`{端口名: [id, …]}`（单值端口也是只有一个元素的数组）。
- 输入来源 `origin.ref`：`source`→来源 id 字符串；`step`→`{step_id, port, index?}`；`artifact`→运行目录相对路径字符串；`literal`→`null`。
- `judge.finished` 与 `seal.rejected` 的 `unsatisfied[]`：`{check, outcome, verdict_id, recovery}`。
- 模板占位符：`{{name}}` 只出现在字符串值里，`name` 匹配 `^[a-z][a-z0-9_]{0,31}$` 且必须在模板的参数声明里有类型与说明；实例化时整个字符串值替换，不做字符串内插。

---

# 附录 B 三个走通的案例

> 以下是**规范模拟**，**不是新版运行结果**。DNA 全是本次构造的合成序列；反向互补、区间、PAM、计数差、环化旋转用标准库内联核算，Tm 用 Biopython 公式，没有调用旧版或待实现的程序（这些数值已由 Claude 在合并前重算一致）。**Tm 与被测实现若用同一个 Biopython 函数，只算回归预期，不算独立交叉验证**（TST-1）。案例展示的是三个检查时刻与同一接口，不是科学结论。

## B1 单工具：计算一段序列的反向互补

**预期由构造得出**：`AGTCAGAA` 的反向互补是 `TTCTGACT`（8 个碱基，结果是计算值，不声称有实体材料）。

| 环节 | 内容 |
|---|---|
| 目标 | 目标物 `t1` 角色 `analysis`；约束 `k1`＝`check.goal.output_present`（`t1` 含字段 `sequence`），`source_quote`＝「反向互补」 |
| 计划 v1 | 一个步骤 `s1`：`seq.reverse_complement@1.0.0`，输入 `sequence` ＝ `{"literal": "AGTCAGAA"}`（记为宿主声明），`why`：「Compute the reverse complement of the supplied synthetic sequence.」；`outputs`：`t1 ← s1.result` |
| **接纳校验** | 通过；**调用器调用数为 0**；写 `pipeline.declared`。若把输入写成 `AGTZAGAA`，在此被 `PLAN_PARAM_INVALID` 拒绝（字母表不合），计划不可执行 |
| 执行 | `step.started`（输入来源记 `literal`）→ 结果 `TTCTGACT` → `step.completed` |
| **步骤自检** | 能力自报 `check.dna_value_valid`（长度 8、字母合法）`PASS`，出具者 `tool_self_report`，进卡片「Declared only」 |
| **封存终检** | 必过项＝基础（`file` 五项、`check.goal.nonempty`、`check.goal.target_role_met`）∪ 约束 `k1` ∪ 所用能力的 `final_checks`（`check.dna_value_valid`）；无材料输出、无制备类检查；全部 `PASS` → 封存 |
| 卡片 | Checked by the program：`file` 五项、目标检查、`check.dna_value_valid`（`final`）；Declared only：输入序列是宿主声明的合成输入、`why`、自报的自检；Not done：未做物理制备与实验验证 |

边界：含合法 IUPAC 未知碱基时按声明规则处理，不自动猜 A/C/G/T；把目标改成实际构建 8 bp 材料，不能沿用本例的基础档位（角色变成 `construct`，必过项随之增加）。

## B2 Cut Plasmid：错位的间隔序列、失败后修订、替换与制备计划

**预期位置由拼接定义，不由被测程序生成。**

- 靶序列（48 nt）：`TACATATCCATACGACATCGTACGATCGTACATAGGTTACATATACCA`。正确间隔序列在 [13,33)：`GACATCGTACGATCGTACAT`，其后 [33,36)＝`AGG`（NGG 成立）；错位的间隔序列在 [12,32)：`CGACATCGTACGATCGTACA`，其后 [32,35)＝`TAG`（不成立）。
- 载体（360 nt 圆形合成模型）：以 Python 标准库 `Random(2026101602)` 连续 360 次从 `ACGT` 取字符，再把 [130,150) 换成错位间隔序列、[150,153) 换成 `GTT`：

```
GTCCTAAAATGCATTCTAGATTGTTGGGAGCAGGCGTCGCTACCACGTCAGCTTGCCCTGTTAGAGTGGCGCGTAGGCTTAGCCTTATCTGTCCGTGCCGGTTCTCTGGAAATCATATTTCCGAAAAAACCGACATCGTACGATCGTACAGTTGCTGTGATCACTTGAGTACGATCGTGCAATCCTGAGTCCCAACCCTAAGTAGCCGGGTATGTTGCGGCCATTTAAGTGTCAGCTCTAAGGTACATCTACTGGGTAAACTATTAAGATCTCTCCCCTGAGCGTGGGGGTAGTGGTTTCCCTGAAACCAACAGTCGCGATAAGCCTGTTAAGGTGACTAGTGGATAGAACTACTTAAGT
```

- 替换预期（独立定义）：`vector[0:130] + guide + vector[150:360]`。线性预期（反向 PCR 产物）：`vector[150:360] + vector[0:130] + guide`，共 360 nt；以原模板前 30 nt 为锚，线性预期里锚的位置是 210，旋转后与替换预期逐位一致；未修改区 [0,130) 与 [150,360) 逐位相等。
- 引物：F 退火区 `GTTGCTGTGATCACTTGAGTAC`（22 nt，Tm 55.3176 °C，唯一结合 [150,172)）；R 退火区 `GTTTTTTCGGAAATATGATTTCCAGAG`（27 nt，Tm 55.1042 °C，唯一结合 [103,130) 的反向互补）；R 的 5′ 尾 `ATGTACGATCGTACGATGTC`（guide 的反向互补，20 nt）；R 完整引物 `ATGTACGATCGTACGATGTCGTTTTTTCGGAAATATGATTTCCAGAG`（47 nt）。Tm 参数：Biopython 1.88 `Tm_NN`，`DNA_NN3`，`saltcorr=5`，`dnac1=250 nM`，`dnac2=0`，Na 50 mM，其余 0，`selfcomp=false`；按 18 至 36 nt 递增选首个落入 55–62 °C 的退火段（这只是案例指定的搜索区间，不是通用实验阈值）。R 退火区含 6 个连续 T，**作为证据备注写进卡片，v1 的 `check.primer_quality` 只判长度与 Tm 窗口，不判发夹、二聚体、纯化**，这些列入 `not_verified`。
- 这个 360 nt 模型只用来验证接口、方向、区间与反应预期，不含经验证的启动子、复制起点或抗性标记，**不能称真实可用质粒**。

| 步 | 事件与处理 |
|---|---|
| 1 | `run.created`（含环境、目录快照、已装载的 `cut-plasmid`） |
| 2 | `goal.declared v1`：目标物 `t1 construct`、`t2 primer_set`、`t3 analysis`（筛选信息）；约束 `k1 components_present`（新间隔序列在 `t1`）、`k2 regions_unchanged`（[0,130) 与 [150,360)）、`k3 claim_reported`（筛选状态在 `t3`）；未提供菌株基因型 |
| 3 | **接纳校验**通过（零调用）：`s1 cut_plasmid.inspect_guide`，`expects`：`pam_valid` 等于 true；`outputs` 暂未覆盖全部目标物（局部诊断计划），接纳回执列出未绑定的 `t1 t2 t3`，目标保持开放；`why` 同时记为事前声明 |
| 4 | 执行 `s1`：报告 `pam_valid=false`（PAM＝`TAG`）→ **步骤自检**：宿主断言 `FAIL` → `step.failed(STEP_EXPECTATION_FAILED)` → `run.halted`。步骤的技术执行成功，但断言不成立 |
| 5 | 宿主先提交事前声明（`reason`：依据初检改用 [13,33) 的 guide），再提交**修订 v2**，触发 `step_failed(s1, event_refs)`：`supersede s1→s2`；新增 `s2 cut_plasmid.replace_spacer`（guide＝`GACATCGTACGATCGTACAT`）、`s3 cut_plasmid.inspect_guide`（输入 `s2.product`，断言 `pam_valid` 为 true）、`s4 cut_plasmid.assess_selection`（输入 `s2.product`，无基因型）；`set_outputs`：`t1←s2.product`、`t2←s2.primers`、`t3←s4.selection`。再次通过接纳校验 |
| 6 | 执行 `s2 s3 s4`：`s2` 的自检自报引物质量；`s3` 断言成立；`s4` 报告筛选状态 `UNKNOWN`（原因：未提供基因型）——**不猜筛选板** |
| 7 | `run.completed`；`judge`：必过项＝基础（`file` 五项、目标检查）∪ 材料输出的 `content_model` 五项 ∪ 角色 `construct` 与 `primer_set` 的 `preparation_model` 项 ∪ 约束 `k1 k2 k3` ∪ 所用能力的 `final_checks`（`cut_plasmid.check_direction`、`check_pam`、`check_vector_self_target`）∪ `check.model_agreement`（因 `replace_spacer` 声明了 `model`）。其中 `check.reaction_chain` 的输入只给原模板、引物与路线，生成模拟产物后才与候选比较；全部 `PASS` |
| 8 | `seal`：暂存、对暂存包重检、清单、原子重命名。**封存成功**；`not_verified` 含：筛选方案未知（基因型缺失）、Cleavage activity、Editing efficiency、Genome-wide off-target safety、引物发夹／二聚体／纯化未评估、`PLANNED`（反向 PCR、DpnI 去模板、KLD；`NOT_PERFORMED`）；标签：`revisions:1`、审核状态汇总 |
| 卡片 | Checked by the program：终检裁决；Declared only：用户原话（宿主转述）、`why`、修订 `reason`、自检自报、断言；Not done：如上；数据链：载体与靶序列文件（哈希）→ `s2` →交付物，仅在**显式绑定且哈希相等**处画实线；`s1` 的失败与被取代的记录**保留可查** |

*必须预先构造的负例（各配一个正对照，预期值由构造决定，不依赖被测实现）*：候选故意错一位（`check.model_agreement` 与 `check.reaction_chain` 应给 `FAIL`）；间隔序列区跨圆环原点；存在第二个引物结合位点；Tm 超出窗口；gRNA 特征标在负链但序列在正向（方向检查按序列判，不按注释）；旧 CDS 注释失真（输入里本来就有、流水线没碰：`PASS` 并列出继承发现；本次引入或来源不明：`FAIL`）；有基因型时筛选板由规则表给出而非猜测。

## B3 Revival Evidence：非 DNA 的观察与有限结论

**预期由观察构造与已声明的结论边界决定**：融合组 9 个菌落，对照组 31 个，差为 −22；**只有菌落形成，不支持功能复活，也不能推 PCR 阴性。**

合成观察文件（概念数据）：`observations: [{id:"o1", group:"fusion", measure:"colony_count", value:9, unit:"colony", plated_volume_uL:100}, {id:"o2", group:"control", measure:"colony_count", value:31, unit:"colony", plated_volume_uL:100}]`，`genotype_results: []`，`functional_results: []`，`observation_origin: "SYNTHETIC_EXAMPLE"`。

| 环节 | 内容 |
|---|---|
| 目标 | 目标物 `t1` 角色 `analysis`；约束 `claim_reported`（结论主题 `functional_revival` 必须有结论状态）；没有任何 DNA 材料 |
| 计划 | `s1 evidence.parse_observations`（输入来源＝观察文件，`input_origin: researcher_observation`）→ `s2 evidence.assess_observations`（输入 `s1.document`）；`outputs`：`t1←s2.assessment` |
| 接纳校验 | 通过（零调用）；无强制 `Molecule` |
| 步骤自检 | `s1` 自报「缺 `id` 列时自动补并记录」这一读取层行为（若发生）；两步均无断言失败 |
| 结果 | 结论 `claim=functional_revival`：`INSUFFICIENT`；`genotype_tests: NOT_TESTED`；`functional_tests: NOT_TESTED`；比较：菌落数差 −22；`limits`：无重复、观察未独立核实、仅菌落形成不构成功能复活的证据。这些结论状态是 **Kit 的领域词**，不是裁决结果 |
| 封存终检 | 基础档位对角色 `analysis` 只要求 `file` 五项与目标检查；**Kit 经 `final_checks` 追加** `evidence.check_record_consistency`（`content_model`，读取知识包里「只有菌落形成不能支持功能复活」的 `rule-v1`，来源类 `project_contract`）。全部 `PASS` → 封存一份**准确说明证据不足的报告** |
| 卡片 | Checked by the program：文件项、记录一致性检查；Declared only：研究者／合成来源的观察与条件、`why`；Not done：基因型、遗传学与功能验证未做，数据真实性未核实；数据链：观察文件（哈希）→ `s1` → `s2` → 报告，输入哈希与步骤显式绑定且相等处为实线 |

边界：schema 合法但无观察 → 结论 `INSUFFICIENT`／`NOT_TESTED`，不是空列表通过；负菌落数被拒；缺单位无法比较 → `UNKNOWN`；给出明确相反的预测与观察，只能在被覆盖的局部检测主张上给 `CONTRADICTED`，不能推全局功能复活被否定；给齐局部 PCR 也不自动升到全基因组结论。

## B4 三个案例的共同检查表

都经过：Goal、事前写好的流水线、接纳校验（零调用）、步骤自检、封存终检、同一调用器、同一种裁决形状、同一个封存流程。**它们不共用科学算法，也不强迫相同的输出类型**；主干不检查 Kit 名，只检查声明、类型与必过项。案例里所有通过条件在实现后必须**实际运行**，本文不是 golden 执行回执。

---

# 附录 C 结构不变量（可自动执行）

检查类型：AST＝语法树扫描，FS＝文件系统或清单，RT＝运行时测试，DOC＝生成物对照，SPEC＝规格自洽扫描。**扫描器自测**：每一类扫描都要有「故意违规的样本必须被报告」的用例。不变量分两档：**骨架不变量**表达本稿的结构原则（分层、一条流、检查在计划外、单一裁决形状、日志与封存不可改、不联网），共 40 条，是规格正文的一部分；**卫生检查**是保持一致性的普通测试，共 79 条，随工具维护。

## C1 骨架不变量

| ID | 不变量 | 检查 | 章 |
|---|---|---|---|
| INV-L1 | 每个 `src/` 模块的项目内 import ⊆ `contracts.toml [allow]` | AST | D1 |
| INV-L2 | 每个 `kits/*/` 的 import ⊆ `[kit_allow]` ＋ 自己的包 | AST | D1 |
| INV-L3 | 模块图没有 import 环 | AST | D1 |
| INV-L4 | 动态探针：所有能力调用都经调用器；只有一处能创建封存包 | RT | D1 |
| INV-C6 | 可调用单元只有 `capability-v1` 一种声明；不存在另一种检查声明或检查注册表 | FS+AST | D3 |
| INV-C7 | `CHECK` 能力：`effects ⊆ {pure, reads_files}`，恰有一个 `scope`，带通过与失败两份样例，失败样例实际运行结果非 `PASS` | RT | D3 |
| INV-P1 | 没有已接纳的计划与步骤，就不能经正式接口执行业务能力 | RT | D4 |
| INV-P2 | `pipeline-v1` 模式 `additionalProperties:false`，且无法表达检查、门、必需范围、`deliver_as` | FS | D4 |
| INV-P3 | **接纳校验期间调用器的调用数为 0**（最后一步非法时第一步也不执行） | RT 探针 | D4 |
| INV-P6 | 只有 `ACTION` 角色的能力可以出现在计划里 | RT | D4 |
| INV-R1 | 已开始步骤的定义在后续所有 `pipeline.*` 事件里逐字不变 | RT 属性 | D5 |
| INV-R3 | 修订的 `reason` 事件早于新步骤的执行事件 | RT | D5 |
| INV-R4 | 含 `seal.created` 的 run 拒绝任何修订 | RT | D5 |
| INV-E1 | 写日志的调用只出现在 `engine`、`assurance`、`application` 的白名单函数与 `storage` 的恢复例程 | AST | D6 |
| INV-E2 | 步骤完成或失败后其记录不再被修改（存储只写一次、读时校验） | RT | D6 |
| INV-A1 | 检查结果永远不通过异常传递 | AST | D7 |
| INV-A2 | 裁决只通过 `kernel.verdict.make` 构造；`outcome/scope/moment/issuer` 字面量来自词表 | AST | D7 |
| INV-A4 | 必过项只取并集，宿主任何输入都不能使其变少（属性测试） | RT 属性 | D7 |
| INV-A5 | 必过检查缺失或不可用 → `UNKNOWN`（`CHECK_UNAVAILABLE`），不是跳过 | RT | D7 |
| INV-A6 | 给输出贴低档角色无效；含材料输出时 `content_model` 检查恒必过 | RT 参数化 | D7 |
| INV-A9 | `tool_self_report` 与 `host_expectation` 的裁决不计入必过项 | RT | D7 |
| INV-A10 | 继承发现只在 `check.annotation_integrity`、`check.cds_validity` 里按输入输出逐项比较给 `PASS`，且必带 `INHERITED_FINDINGS` 标签；引入的或来源不明的发现给 `FAIL` | RT 夹具 | D7 |
| INV-D1 | 封存目录创建后不被任何函数修改 | RT | D8 |
| INV-D2 | `seal_id` ＝清单摘要，清单不含 `seal_id` 与自身；卡片只显示 `journal_head` | RT | D8 |
| INV-D6 | 封存包单独复制到新位置后 `verify` 通过 | RT | D8 |
| INV-D7 | 封存总是对暂存包重新运行全部必过项，不复用任何先前裁决 | RT | D8 |
| INV-I1 | `hashlib` 只在 `kernel/ids.py` | AST | D9 |
| INV-I3 | 所有测试 run 的日志哈希链有效 | RT | D9 |
| INV-T1 | `record` 包内没有任何写日志调用，也不 import 引擎、检查层内部 | AST | D10 |
| INV-T2 | 每条实线都有显式输入绑定且哈希相等（随机重算）；无绑定的偶然相等画虚线 | RT | D10 |
| INV-T6 | 自检与宿主断言的裁决不出现在「Checked by the program」栏 | RT | D10 |
| INV-K1 | Kit 包内 Python 只在 `capabilities/` 下；无 `main/argparse`；无报告渲染代码 | AST+FS | D11 |
| INV-K2 | Kit import ⊆ `[kit_allow]` ＋ 自己的包 | AST | D11 |
| INV-K7 | 清单模式没有档位、输出角色、接纳规则、交付类别之类的键 | FS | D11 |
| INV-H1 | `verbs.json` ＝实际注册的动词＝`api.__all__` | FS+AST | D13 |
| INV-V1 | `outcome/scope/moment/issuer/state` 字面量来自词表 | AST | D14 |
| INV-W2 | `VERSIONS.json` 是唯一手写版本来源 | FS | D16 |
| INV-X1 | `os.environ` 只在 `application/config.py` | AST | D17 |
| INV-X2 | 默认命令集与示例零次网络连接尝试 | RT | D17 |
| INV-Q1 | `tests/structure` 在 CI 里是独立作业，且是其他作业的前置 | FS | D18 |
| INV-Q3 | 夹具 `oracle` 字段指明来源类别 `construction|hand|published|independent_program` | FS | D18 |

## C2 卫生检查

| ID | 不变量 | 检查 | 章 |
|---|---|---|---|
| INV-L5 | 契约充分性：规格正文需要的跨模块调用 ⊆ 契约允许的调用 | SPEC+AST | D1 |
| INV-G1 | `goal_digest` 只由 `engine.goal` 计算 | AST | D2 |
| INV-G2 | 约束 id 永不从任何目标版本中消失（只会 `dropped`） | RT 属性 | D2 |
| INV-G3 | `original_request` 在所有版本逐字相同 | RT | D2 |
| INV-G4 | 目标物角色取自词表；角色与实际输出不符 → `check.goal.target_role_met` 为 `FAIL` | RT | D2 |
| INV-G5 | 宿主提交的声明，行为者恒为 `ai_host`；程序执行与检查的事件为 `program`；`human` 只出现在交互式确认的记录里 | RT | D2 |
| INV-C1 | `resources/capabilities/*.json` 与代码导出一致 | DOC | D3 |
| INV-C2 | 每个能力 `does_not_establish` 非空，`summary` ≤200 字符 | FS | D3 |
| INV-C3 | `atomic` 能力不调用其他能力；`composite` 只经 `ctx.call` | AST | D3 |
| INV-C4 | 非 `writes_files` 能力没有文件写入（AST 扫描加调用后检测；v1 没有沙箱，不做操作系统级强制） | AST+RT | D3 |
| INV-C5 | 能力 id 唯一 | FS | D3 |
| INV-C8 | `CHECK` 角色的能力 id 以 `check` 开头（核心 `check.…`，Kit `<命名空间>.check_…`）；`ACTION` 角色的 id 不以 `check` 开头 | FS | D3 |
| INV-P4 | 规范化幂等 | RT 属性 | D4 |
| INV-P5 | 紧凑与规范两种写法摘要相同 | RT | D4 |
| INV-R2 | 失败或被取代步骤的输出不被后续步骤引用 | RT | D5 |
| INV-R5 | `expected_digest` 不符的修订被拒；并发修订只有一个成功 | RT | D5 |
| INV-R6 | 重试＝新增步骤并取代旧步骤，原失败保留 | RT | D5 |
| INV-E3 | 能力只通过 `ctx` 与外界交互（内置能力有运行时测试与调用后检测；外部 Kit 的越界 I/O v1 只能事后发现，不能阻止） | RT | D6 |
| INV-E4 | 环境指纹只在 `run.created` 里记录一次，不在步骤内产生 | RT | D6 |
| INV-E5 | 日志尾部写到一半后强杀：恢复到最后完好事件并记 `journal.recovered`；非尾部损坏则拒绝继续 | RT 强杀 | D6 |
| INV-E6 | run 创建时记录目录快照，必过项按快照推导 | RT | D6 |
| INV-A3 | 三处关键逻辑（`check.replay`、必过项推导、哈希链校验）的人工变异能被样例抓到 | RT 变异 | D7 |
| INV-A7 | 检查不修改既有输入、内容存储和候选；除追加自己的 `verdict.issued` 事件外运行目录不变 | RT | D7 |
| INV-A8 | `NOT_APPLICABLE` 必须带原因与依据 | RT | D7 |
| INV-D3 | 封存条件只由必过项计算，无第二套判据 | AST+评审 | D8 |
| INV-D4 | 「未封存」等标签只在 `assurance.labels` 产生 | AST+RT | D8 |
| INV-D5 | 不存在 `GATE_*` 异常类或错误码 | AST | D8 |
| INV-I2 | 黄金向量跨平台与 Python 版本一致 | RT（CI 矩阵） | D9 |
| INV-I4 | 特征顺序、名称、描述、日期变化不改 `material_id`；序列或注释变化改变它 | RT 属性 | D9 |
| INV-I5 | 所有输出标识匹配 `^[0-9a-f]{64}$`（`run_id` 为 16 位） | RT | D9 |
| INV-I6 | 被哈希的对象里没有裸浮点数 | AST+RT | D9 |
| INV-I7 | 每个步骤输入都记录来源 `{kind, ref}` | RT | D9 |
| INV-T3 | 运行卡片只有三栏；封存清单 `not_verified` 的每一条都出现在「Not done」栏 | RT | D10 |
| INV-T4 | 删除 `views/` 后可完整重建，字节一致 | RT | D10 |
| INV-T5 | 卡片声明事件截止点 | RT | D10 |
| INV-K3 | 清单声明的贡献（含 `text`）与文件一一对应 | FS | D11 |
| INV-K4 | 卸载 Kit 后注册表与装载前一致 | RT | D11 |
| INV-K5 | Kit 的 `final_checks` 出现在必过项里（玩具 Kit 验证） | RT | D11 |
| INV-K6 | Kit 之间没有 import 关系 | AST | D11 |
| INV-N1 | 所有 `rule-v1` 有合法来源，类别不是 `AI/internet/latest` | FS | D12 |
| INV-N2 | 检查与分析代码里无阈值字面量（白名单登记除外；**启发式**） | AST | D12 |
| INV-N3 | `review/` 下文件只由审核命令写入（流程＋AST） | AST | D12 |
| INV-N4 | `active` 规则无审核记录时，交付清单显示「未经人工审核」 | RT | D12 |
| INV-N5 | 适用所需信息缺失 → `UNKNOWN`，不是 `FAIL` | RT | D12 |
| INV-RV1 | 审核记录与对象哈希不符 → `stale` | RT | D20 |
| INV-RV2 | `review sign` 非交互环境退出码非 0 且不写文件 | RT | D20 |
| INV-RV3 | 封存清单标签覆盖本 run 用到的每条规则与模板 | RT | D20 |
| INV-RV4 | 代码里除 `review sign` 外没有写入 `review/` 的调用 | AST | D20 |
| INV-H2 | 生成区块与声明一致（重新生成后无差异） | DOC | D13 |
| INV-H3 | 所有动词的 JSON 输出符合回执信封 | RT | D13 |
| INV-H4 | `describe` 不 import 任何能力实现（受限环境运行） | RT | D13 |
| INV-H5 | `SKILL.md` 手写区不含数量、版本、清单 | FS | D13 |
| INV-H6 | 带内容的动词使用请求文件 | RT | D13 |
| INV-V2 | 所有 `raise` 的错误码都登记在 `errors.json` | AST | D14 |
| INV-V3 | 不存在除 `ToolkitError/CapabilityError` 之外的 `Exception` 子类 | AST | D14 |
| INV-V4 | 词表生成物与 `vocab.json` 一致 | DOC | D14 |
| INV-F1 | `ship.json` 与目录树一致 | FS | D15 |
| INV-F3 | 序列夹具都登记在 `MANIFEST.json`（合成或第三方带许可） | FS | D15 |
| INV-F4 | `src/` 无 `snapgene` 标识符（格式读写文件白名单除外） | AST | D15 |
| INV-F5 | 构建产物不入库 | FS | D15 |
| INV-F6 | 夹具登记的名称与哈希不出现在 `src/` 与 Kit 的能力代码 | AST+FS | D15 |
| INV-F7 | `contracts.toml`、`vocab.json`、`errors.json`、`profiles.json`、`schemas/*`、`verbs.json`、`ship.json`、`VERSIONS.json` 的哈希与决策记录里最新登记一致 | FS | D15 |
| INV-F8 | 仓库内无旧包名与旧模块名引用 | AST+文本 | D15 |
| INV-F9 | 带 `# ported-from:` 头的文件均登记于 `MIGRATION-MAP.md`，且旧路径存在 | FS | D15 |
| INV-F10 | 发行包含 `LICENSE`、`README.md` 的必需章节与锁定依赖文件，不含 `.exe`／`.bin`／`.dll` 等编译产物，git 仓库小于 50 MB | FS | D16 |
| INV-W1 | 版本字面量只出现在生成文件 | AST | D16 |
| INV-W3 | 同一源树两次构建 `release_id` 相同 | RT | D16 |
| INV-W4 | 封存清单里的 `release_id` 能在发布记录里找到（`dev-tree` 除外，它的封存包不是发行证据） | FS | D16 |
| INV-X3 | 源码无 `pip/urllib/requests/http.client/socket`（测试工具白名单） | AST | D17 |
| INV-X4 | 无 `shell=True` | AST | D17 |
| INV-Q4 | `SKIPS.json` 无过期条目；SKIPPED 不计为通过 | FS | D18 |
| INV-Q5 | 间歇失败有登记、负责人与期限；不因重复通过而关闭 | FS+流程 | D18 |
| INV-S1 | 正文里出现的每个事件类型都在附录 E；附录 E 的每个事件都有写入方 | SPEC | 全稿 |
| INV-S2 | 正文里出现的每个命令动词都在 D13 的动词表 | SPEC | 全稿 |
| INV-S3 | 正文里出现的每个 `模块.子模块` 路径都在 D15 的目录树 | SPEC | 全稿 |
| INV-S4 | 规则编号前缀唯一：`DEP` `GOL` `REV` `KIT` `SEAL` `RV` `TST` `DEV` `ADV` `INV` `MVP` | SPEC | 全稿 |
| INV-S5 | 退役词（旧检查阶段名、评估器目录、交付类别、`PLAN/DOMAIN` 范围、`INCONCLUSIVE`、`mature` 等）不得被肯定地使用（只允许出现在「不采用」「取代」「没有」「旧」语境，或 `MERGE-LEDGER.md`） | SPEC | 全稿 |
| INV-S6 | 正文里写的词表数量（检查时刻 3、结果 4、范围 4、能力角色 2）与 §1 一致 | SPEC | 全稿 |

---

# 附录 D 给开发 AI 的工作规程（规格定稿后生成到 `dev/AGENTS.md`）

1. **DEV-1 先读再写**：改动前读要触及的章（D 编号）与 `OPEN-ITEMS.md` 里对应条目。
2. **DEV-2 声明范围**：每次提交写明触及的 D 编号与 INV 编号。
3. **DEV-3 受保护文件**：`contracts.toml`、`vocab.json`、`errors.json`、`profiles.json`、`schemas/*`、`verbs.json`、`ship.json`、`VERSIONS.json` 的任何改动，必须先写决策记录并获得人的确认（INV-F7 检查）。
4. **DEV-4 独立答案**：测试的期望值只能来自构造、手工核算（写明方法与来源）、已发表数值或独立程序；**不得**用待测代码或旧系统输出生成。
5. **DEV-5 移植**：从旧版**复制**零件并按新接口**改写**；文件头写 `# ported-from: <旧路径>@<提交>` 并登记到 `MIGRATION-MAP.md`；**不得 import 旧版**。
6. **DEV-6 遇到歧义就停**：规格和待决项里没有的结构选择，**不要自己发明**；写进 `QUESTIONS.md` 并停在该处。
7. **DEV-7 偏差要报告**：任何与规格不一致之处写进 `DEVIATIONS.md`（做了什么、为什么、涉及哪个 D），不得静默。
8. **DEV-8 不碰审核**：不得创建或修改任何 `review/` 目录下的文件。
9. **DEV-9 不加新东西**：不新增动词或入口、异常类、状态词、哈希函数、环境变量读取点、Kit 专属脚本、检查时刻、范围。
10. **DEV-10 如实汇报**：写明跑了哪些测试、失败了什么、跳过了什么（已登记）、哪些没验证；没有列出运行范围就不得说「全部通过」；官方 GitLab CI 一律写「未执行」。
11. **DEV-11 远端与署名**：不推送 `main`；提交署名遵循项目负责人的常设规则。
12. **DEV-12 阶段顺序**：按 D19 推进；某阶段的门没过，不得进入下一阶段；超出范围的需求先登记，不实现。
13. **DEV-13 改一处，扫一遍**：收敛或改名一个结构后，必须顺着扫依赖它的地方（词表、Kit 贡献口、注册表、不变量、事件目录、图表），列出仍带旧形状的残留，并在合并前跑规格自洽扫描（INV-S1…S6）。**不得在图或表仍显示旧数量时宣称「已收敛」。**
14. **DEV-14 防御预算与框架优先**：写任何防护、校验、恢复机制、测试之前先过三问（真实发生吗／后果重吗／代价小于后果吗），有一问答「否」就不写，只在「已知不防」清单登一行；新增概念须同时删掉或合并一个；汇报的第一屏只写结构是什么、这次改了哪里的结构、要决定什么（≤5 行），细节放附录；问题清单超过 5 条时，先分「结构类」与「实现类」，只汇报结构类。

---

# 附录 E 日志事件目录

每个事件使用 A5 的信封；下表列 `type`、写入方、`payload` 的必有字段。**未列出的字段不得加入，需要时走 `QUESTIONS.md`。**

| `type` | 写入方 | `payload` 必有字段 | 说明 |
|---|---|---|---|
| `run.created` | application | `release_id, git_commit?, schema_versions, created_by, environment{python, platform, packages, external_tools[{name,version,sha256}], config_digest}, catalog_id, catalog_ref, kits[{name,version,manifest_sha256,code_digest,origin,source}], derived_from?{run_id, seal_id}（宿主声明：本 run 接续哪个已封存的 run；REV-7）` | 日志第一条；环境、目录快照、已装载 Kit 都记在这里，只记一次 |
| `goal.declared` | engine | `goal_digest, version, document` | |
| `goal.amended` | engine | `goal_digest, version, previous_digest, diff, by, reason, amended_after_start` | |
| `input.registered` | engine | `source_id, file_sha256, size, run_path, input_origin, declared_by` | 不记录原绝对路径 |
| `pipeline.declared` | engine | `pipeline_digest, version, document, goal_digest, library_ref, unbound_targets[]` | |
| `pipeline.revised` | engine | `pipeline_digest, version, previous_digest, document, operations, trigger, reason_event` | |
| `declaration.recorded` | engine | `text, origin, actor{kind,name}, about{kind,id}, basis_refs[]` | `why`、`reason` 自动生成；程序不能产生声明 |
| `step.started` | engine | `step_id, capability{id,version,declaration_digest,code_digest}, inputs{名:{id, origin{kind,ref}}}, params, params_digest` | |
| `call.recorded` | engine | `parent, capability{…}, input_ids{}, params, params_digest, outputs{}（或 failure）, duration_ms` | 嵌套调用，完成后记一条；回放模式不写；`params` 是该次调用实际收到的参数（与 `step.started` 同口径，与计划同样遵守短字面量规则），`params_digest` 是其 JCS 的 SHA-256；没有它，`check.reaction_chain` 无法复算嵌套反应（如同一引物的退火段长度不同，PCR 结果就不同） |
| `verdict.issued` | engine（`moment: step`）／assurance（`moment: final`） | `verdict(verdict-v1)` | 所有裁决只有这一个事件 |
| `step.completed` | engine | `step_id, outputs{materials,documents,artifacts[{run_path,sha256,role,media_type}]}, values{}, unverified[], verdict_ids[], duration_ms` | |
| `step.failed` | engine | `step_id, failure, retained_outputs（形状同 step.completed 的 outputs、values、unverified，不可被引用）, superseded_by` | `superseded_by` 初始 null，由修订事件另记，不改写本事件 |
| `run.halted` | engine | `reason(step_failed), step_id` | |
| `run.completed` | engine | `pipeline_digest, executed_steps[]` | |
| `run.abandoned` | engine | `reason, by` | |
| `judge.finished` | assurance | `candidate_digest, obligation_ids[], verdict_ids[], unsatisfied[]` | |
| `seal.rejected` | assurance | `candidate_digest, unsatisfied[{check, outcome, verdict_id, recovery}]` | 退出码 10 |
| `seal.created` | assurance | `seal_id, manifest_digest, journal_head, release_id, labels` | |
| `journal.recovered` | storage（恢复例程） | `discarded_bytes, reason` | 唯一由 `storage` 写的事件 |

**写权限矩阵（INV-E1 的白名单依据）**：`engine` 写 `goal.*`、`input.*`、`pipeline.*`、`declaration.*`、`run.halted/completed/abandoned`、`step.*`、`call.recorded`、`verdict.issued`（`step` 时刻）、；`assurance` 写 `verdict.issued`（`final` 时刻）、`judge.finished`、`seal.*`；`application` 只写 `run.created`；`storage` 只写 `journal.recovered`。`record`、`capabilities`、`knowledge`、`catalog`、`kernel`、`biology`**不能写任何事件**。

**形状规则**：事件的结果与证据字段不得出现原始序列（目标与计划里的短字面量除外，≤200 nt）；`time` 为 UTC、毫秒、`Z` 结尾；`seq` 从 1 连续。

---

# 附录 F 对抗式自查：「只想满足要求」的开发会怎样钻空子

假设有开发 AI（或赶进度的人）只想让测试变绿、让需求「看起来满足」。下表是最可能的做法和堵法；「剩余风险」是堵法之后仍需要人来盯的部分。

| ID | 可能的空子 | 堵法 | 剩余风险 |
|---|---|---|---|
| ADV-1 | 删除或放宽目标约束让检查通过 | GOL-2、GOL-3；约束只能 `dropped` 且仍显示；INV-G2 | 加无关紧要的约束稀释目标 → 约束来源显示在卡片，人可见 |
| ADV-2 | 声明空目标或平凡目标 | `check.goal.nonempty`；没有任何模式可以绕开必过项 | 平凡约束（只要求「文件存在」）→ 卡片列出约束与来源 |
| ADV-3 | `why` 写套话 | 程序不判质量，只记录并标 `plan_declared` | 无法由程序解决，靠阅读卡片 |
| ADV-4 | 检查永远返回 `PASS` | 每个检查带失败样例并实际运行；变异测试（INV-C7、INV-A3） | 样例本身太弱 → 评审样例 |
| ADV-5 | 新增第二个入口（Kit 脚本、便捷命令） | INV-H1、INV-K1、INV-L1 | 在包外另写脚本＝宿主自写脚本，不在核对范围 |
| ADV-6 | **给输出贴低档角色以躲开检查** | 输出角色由产出它的能力声明，计划里没有位置；含材料输出时内容检查恒必过；Kit 不能增改档位（INV-A6、INV-K7） | Kit 作者在自己能力上声明了过低的角色 → 声明受审核与样例约束；核心中构建类能力的角色有固定夹具 |
| ADV-7 | 绕过引擎直接写日志、伪造事件 | INV-E1；行为者类别限制；`record` 不能写；哈希链发现局部改写 | 对整台机器有完全控制权的写入者可整体重写；发布头哈希到机器之外 |
| ADV-8 | 针对样例的特判（按文件名、哈希、材料身份） | INV-F6 | 无 |
| ADV-9 | Kit 偷带流程代码、报告渲染、入口 | INV-K1、INV-K2、INV-K7 | 把流程写进能力里 → 组合能力只能 `ctx.call`，流水线可见 |
| ADV-10 | 说明文档手写数字、与代码漂移 | INV-H2、INV-H5 | 手写的使用协议本身过时 → 示例即测试 |
| ADV-11 | 随手新增状态词、错误码、异常类 | INV-V1、INV-V2、INV-V3 | 无 |
| ADV-12 | 各处自己算哈希或自造版本 | INV-I1、INV-W1 | 无 |
| ADV-13 | 先检查后替换文件 | SEAL-4、SEAL-8；INV-D1、INV-D7 | 无 |
| ADV-14 | 吞掉异常、宽捕获 | DEP-13 | 在白名单位置内吞掉 → 必须转成失败记录 |
| ADV-15 | 跳过测试蔓延 | TST-4；INV-Q4 | 无 |
| ADV-16 | 为让测试通过而放宽契约、词表、模式 | INV-F7 | 决策记录本身是人写的，须人确认 |
| ADV-17 | 悄悄 import 旧代码或原样抄旧结构 | INV-L2、INV-F8、INV-F9 | 无 |
| ADV-18 | 过度设计：条件语言、插件沙箱、插件市场、通用工作流引擎 | 「不采用」清单；修订操作集封闭；D19「明确不做」 | 无 |
| ADV-19 | 宿主 AI 不走正式路线 | **按设计不拦截**；未封存输出统一带「未封存」标签（INV-D4） | 用户可能把未封存结果当正式结果＝声明的限制，不是缺陷 |
| ADV-20 | 用 `expects` 让计划「自己验证自己」替代系统检查 | `expects` 只增不减；封存只看必过项；自报与断言不计入（INV-A9） | 无 |
| ADV-21 | 修订的「触发」写成无关类别 | `step_failed`、`check_failed` 的 `event_refs` 由引擎核对；其余类别画虚线 | 无 |
| ADV-22 | 封存前卸载或替换 Kit，让它的必过检查从必过项里消失 | 必过项按目录快照推导；快照里缺失的检查记 `UNKNOWN`（INV-A5） | 无 |
| ADV-23 | 能力自报「通过」，让输出看起来被检查过 | 出具者记 `tool_self_report`，不计必过项，卡片放「Declared only」（INV-A9、INV-T6） | 无 |
| ADV-24 | **收敛了一处却让依赖它的地方保留旧形状** | DEV-13；INV-S5、INV-S6；`tools/spec_lint.py` | 语义上的不一致仍需评审 |


---

## 合并后自检（2026-10-16）

> 用 `tools/spec_lint.py`（INV-S1…S6 的原型）扫描本稿，并对扫描器本身做了注入测试。**这只能发现名字、编号、数量、路径的不一致，发现不了语义上的矛盾**；语义矛盾仍需评审和红队。

| 项目 | 结果 |
|---|---|
| 硬性问题 | 0 |
| 软提示 | 18 条，全部是在「不采用」「取代」「没有」「旧」语境里提到退役词，逐条看过，属正常 |
| 词表数量 | 检查时刻 3、裁决结果 4、裁决范围 4、能力角色 2、出具者 3，与 §1 一致 |
| 模块数 | D1 表列 10 个，与「十个模块」一致 |
| 不变量 | 附录 C 共 120 条；正文引用的每个 `INV-` 都有定义；规则编号 `DEP`（1–13）、`GOL`（1–8）、`REV`（1–10）、`KIT`（1–7）、`SEAL`（1–10）、`RV`（1–7）、`TST`（1–11）、`DEV`（1–13）、`ADV`（1–24）未越界 |
| 扫描器自检 | 向副本注入 8 种错误（旧写法、肯定地使用退役词、未登记事件、未定义不变量、词表数量被改、`check_` 前缀的未知 id、ACTION 被写成 CHECK、未登记动词）：全部被抓到 |

**合并过程中，扫描和复核发现并已改正的问题**

1. 检查 id 两种写法并存（`check.goal_nonempty` 与 `check.goal.nonempty`）→ 统一为 `check.goal.nonempty`。
2. 依赖契约写了 `storage.read`，目录树里没有对应文件 → 目录树补 `storage/read.py`。
3. 同一个能力 `cut_plasmid.check_selection` 在案例里既当计划步骤（做事）又在规则里当评估者（检查）→ 违反「计划里只许 `ACTION`」；改名为 `assess_selection`（做事）。
4. `cut_plasmid.check_guide`（做事）与 `check_direction`（检查）易混 → 新增命名约定 `INV-C8`，做事的改名 `inspect_guide`，模板改名 `inspect_only`。
5. 「检查器」一词在 D1、附录 C 里指「结构扫描工具」，与退役的评估器同名 → 改称「扫描器」。
6. 断言失败的步骤原来既"已完成"又"断言永远不通过"，封存会被永久挡住（旧稿的死结）→ 断言失败记为步骤 `FAILED`，可被取代（D5、D6）。
7. 扫描器自己有缺陷：两条正则里的 `` 被写成不可见的退格字符，命名检查形同虚设；注入测试发现后已修复并重测。
8. `MVP-` 前缀、`INV-S1` 的「反之亦然」过严 → 分别补入前缀清单、改为「附录 E 的每个事件都有写入方」。

**仍需人和红队去查的（扫描器查不了）**：必过项推导的边界情形；档位表与输出角色是否覆盖所有真实 Kit；`check.replay` 对非确定性步骤的处理；封存包的离线复验是否真能重跑所列检查；各模式字段的完整性（附录 A 只是草表）。


---

## 防御预算清洗（2026-10-16）

按 DEV-14 对本稿做了一轮简化，**不改框架，只删防护与概念**：

- 删除：修订次数上限与 `limit raise`／`limit.raised`、`anchor` 动词与事件、`environment.changed`、`catalog.changed`、`kit.load_failed`、`--repin` 与 `CATALOG_CHANGED`、旧版封存包兼容、`unshare -n` 的必做作业、INV-X5、事件 1 MB 上限、陈旧锁接管、并发封存与长路径测试、`check.desktop_roundtrip` 及配置键、`signature` 预留字段、`NOT_APPLICABLE` 的封闭原因码、规则矛盾处理。
- 降级：目录快照只记录；变异测试只做三处。
- 不变量分档：骨架 40 条留在正文，其余作为卫生检查。
- 保留（三问都过）：计划里没有检查字段、必过项只增不减、封存时重检、日志追加加哈希链、零连接、来源逐条必填、独立答案、结构测试先跑、日志尾部损坏的恢复、非 ASCII 路径。
