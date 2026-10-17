# 规格覆盖与责任缺口，只读快照（2026-10-17）

发现 **12 处没有后续落实任务的空缺**：11 条不变量，加 1 处真实发行身份加载接缝；另有 3 条只到占位/局部实现。
最重三项：精确提交 GitHub CI、发行包运行身份、真实审核状态链。三项均影响规格要求的完整 S4 判断。
10 月 19 日不能把本地开发树的可运行，代替发行、安装、跨平台 CI 与人工批准；旧 0.2.2 回退是否切换仍由用户决定。
本项只盘点并建议责任人，未实现任何缺口，未改源码、规格、Kit 或测试预期。

## 口径与证据

快照源：integ-2 的 6b21baf。范围为合并树的 SPEC、119 条附录 C、不变量登记、prompts 下已发任务及合并 QUESTIONS 各任务章节。S1c 主任务与夜间追加任务按用户直接提供的任务书读取。
“没人做”指没有后续、具体的实现/验收任务；阶段标签不是任务分配。早期只允许空树检查、明确延期或只让人填写审批，不自动等于有人会补运行时功能。此口径为夜间临时默认，白天由规格负责人确认；不是对人的贡献评判。
95 条登记已实现、24 条 PENDING 不是结论。下表依据源码与已运行测试区分：未落实、局部实现、已分配未完、登记过时。已有方法级测试主要来自主任务两次完整运行与追加串联；不把静态关键词命中当作动态通过。
未联网、未安装、未签注、未做新的正式评测。新只读探针仅在忽略目录建合成运行，不改任何实现或已有记录。

## 需要补发具体任务的空缺

| 条目 | 缺什么 / 依据 | 建议谁做 | 工作量（小时，估计） | 10月19日影响 |
|---|---|---|---|---|
| INV-Q1 GitHub CI 结构前置作业和精确提交矩阵 | [SPEC:1272](../../../spec/SPEC.md#L1272)；没有 .github 工作流；S4a 只分配构建/检查/安装脚本，未分配 CI 配置。 | 发行 | 3–5 | 会：D16 明确要求 Windows/Ubuntu 精确提交 CI。 |
| INV-N2 阈值数字启发式扫描与来源白名单 | [SPEC:1319](../../../spec/SPEC.md#L1319)；分析代码已有，但 check_structure 没有这条扫描及白名单自测；S1b 算法任务未分配扫描器。 | 生物层＋S1 层 | 3–5 | 会影响完整规格验收；不是要求添加新阈值。 |
| INV-N3 审核目录写入者专门 AST 检查 | [SPEC:1320](../../../spec/SPEC.md#L1320)；review 模块空白；没有审核写入边界扫描和破坏对照。S2 仅实现 Kit，不能改共享层。 | S1 层 | 1–2 | 与 RV4 合并实现，不重复计算工时。 |
| INV-RV1 审核文件字节哈希与自动过期识别 | [SPEC:1323](../../../spec/SPEC.md#L1323)；knowledge/review.py 为空；目录快照把审核数固定为 none，未读取审核记录。S3 未分配 Core 实现。 | S1 层 | 3–5 | 会影响 D20 功能；不等于要求所有规则先被人审。 |
| INV-RV4 除审核命令以外不得写审核目录的扫描 | [SPEC:1326](../../../spec/SPEC.md#L1326)；与 N3 同一缺口；现有通用 writer 扫描面向事件日志，不是 review 目录。 | S1 层 | 同 N3 | 合并 N3，不另加一项工程。 |
| INV-H5 手写 Skill 区的数量/版本/清单检查 | [SPEC:1330](../../../spec/SPEC.md#L1330)；docgen 检查生成区是否新鲜，保留手写区原样；未见手写区违规对照。早期空树延期没有后续承接。 | S1 层／文档 | 1–2 | 卫生要求，需负责人明确处置，不能默认为通过。 |
| INV-F3 全局序列夹具 MANIFEST 与来源/许可登记 | [SPEC:1336](../../../spec/SPEC.md#L1336)；现有是每次运行封存 manifest、函数 oracle 表和生成器，均不是全局序列夹具身份清单。 | 发行＋生物层 | 2–4 | 会影响公开发行的夹具可追溯性。 |
| INV-F6 用夹具登记名称/哈希反查运行时代码特判 | [SPEC:1339](../../../spec/SPEC.md#L1339)；缺 F3 登记，也没有 F6 对应扫描器和故意特判对照。 | S1 层／发行 | 2–4 | 与 F3 相依；不把普通领域常量当特判。 |
| INV-F7 保护文件哈希与最新人工决策登记比对 | [SPEC:1340](../../../spec/SPEC.md#L1340)；S4a 交接明确说 F10 不是 F7；现有决定/审核流程不等于实现这项自动比对。 | 发行＋人工 | 2–4 | 会：保护文件已有获准变更，发布前须由负责人核清；AI 不代填审批。 |
| INV-F8 旧包名/旧模块引用全仓扫描及例外规则 | [SPEC:1341](../../../spec/SPEC.md#L1341)；F4 只扫描运行时代码标识符；不是 F8 的全仓引用检查。迁移证据仍需合法旧路径例外。 | 发行 | 1–2 | 卫生要求，需先确定证据目录/格式文字的白名单。 |
| INV-Q5 间歇失败登记、负责人、期限和关闭流程 | [SPEC:1350](../../../spec/SPEC.md#L1350)；没有当前项目的专门登记/检查。本次旧断言失败是稳定失败，不伪装成间歇失败。 | S1 层＋人工 | 1 | 条件式：没有已确认间歇案例时不制造案例；出现时阻塞关闭。 |
| D16 / S4A-01 | kernel/release.py 只读版本；RunService.create 直接写 dev-tree。S4a 已把运行身份加载交给 S1 提问，但 S1c 任务未分配此接缝。真实发行不能获得 manifest release_id，也未做运行时装载篡改正反例。 | S1 层＋发行 | 3–5 | 会：dev-tree 明确不是发行证据；单有 ZIP 构建工具不够。 |

N3 与 RV4 是同一类写入边界，合并工作量；11 条不变量不是 11 个独立工程。Q5 当前没有已确认的新项目间歇案例，不制造假案例；触发时必须登记。F7 的人工审批责任已存在，缺的是具体字节比对工具，AI 不代填审批。

## 局部实现，不能算完整闭环

| 条目 | 当前实况 | 测试边界 | 建议 |
|---|---|---|---|
| INV-N4：部分显示，无完整责任任务 | catalog/registry.py:120 固定 none；assurance/labels.py 只汇总计数 | 仅有 none/标签测试，不证明逐对象未审核文字与正确状态 | S1 层，2–4 小时 |
| INV-RV2：只有拒绝占位，无交互签注闭环 | application/api.py:55 对所有调用返回不可用 | 未见真实交互正例；当前拒绝不能算审核功能完成 | S1 层＋人工，3–5 小时 |
| INV-RV3：部分计数，无规则/模板逐项覆盖 | catalog/registry.py:120；assurance/labels.py:collect | 现有计数不读模板审核，不限定本 run 实际用到的对象 | S1 层，2–4 小时 |

审核“未完成”不等于要求所有数据必须先被人审才运行。规格允许 none 继续运行，但要求真实、逐对象的标注与修改后 stale；当前固定 none 不能证明这些功能。

## 其他 PENDING 的实际处置，不误计为无人做

| 条目 | 状态 | 已发责任 / 实现 | 测试或剩余范围 |
|---|---|---|---|
| INV-C4 | 已分配，未全覆盖 | S1c 追加任务 3；engine/invoker.py:_invoke | S1 层，下一项实做；不是本项实现 |
| INV-E3 | 已分配，未全覆盖 | S1c 追加任务 3；engine/invoker.py:Context/_invoke | S1 层；v1 无 OS 沙箱 |
| INV-I2 | 已分配，环境未执行 | S1.1 第5项、规格负责人 S4 交接；tests/unit/test_kernel.py | 发行／环境；今晚明确不做 |
| INV-K3 | 已有实作，PENDING 原因过时 | S1 catalog / Kit 发现；catalog/registry.py:_register | CatalogTests.test_conflicting_external_implementations_disable_both |
| INV-N5 | 已有 Kit 求值/未知行为，登记未闭合 | S3 规则真值表、S2 筛选边界；kits/revival-evidence/capabilities/assessment.py:matches/conclude | EvidenceTests、CutPlasmidTests；不宣称任意规则都完备 |
| INV-F1 | 已分配且有构建/检查代码 | S4a 第1/2项；tools/build_release.py:payload；tools/check_release.py | ReleaseEngineeringTests；实际发行还被披露/路径阻止 |
| INV-F9 | 已有迁移登记，但规格落点存在冲突 | S0 第9项、S1b 迁移日志；MIGRATION-LOG.md；tests/oracles/migration_inventory.py | 任务指定 LOG、规格指定 MAP，负责人决定，不改规格 |
| INV-W3 | 已有独立构建对照，真实发行未完成 | S4a 第1项；tools/build_release.py | ReleaseEngineeringTests.test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata |
| INV-W4 | 已分配发布记录/安装验证，运行身份接缝仍缺承接 | 规格负责人 S4 交接、S4a-01 问题；kernel/release.py；application/run_service.py:create | dev-tree 除外；真实发行身份加载另列关键缺口 |
| INV-F10 | 已实现检查，当前真实树 FAIL/INCOMPLETE | S4a 第2项；tools/check_release.py:inspect_tree | ReleaseEngineeringTests；4条路径命中、5个占位未清 |

## 当前可复核的额外阻塞

- 主任务 C8：7 个旧测试方法仍要求“功能不存在”；C9：发行元数据测试缺已锁定构建依赖。完整配置套件 380 项中 372 通过、8 项未通过，零跳过。未配置首次 375 项中 363 通过、11 项未通过、1 项登记跳过。均未重写为绿色。
- 只读发行检查：FAIL，命中 4 个选择范围内的本地路径文件，另有 5 个披露/架构占位；跟踪文件 14,246,181 字节，小于 50 MB。命中中 1 个是用户目录，3 个是机器绑定工作区示例，不能一概称凭据或泄露。文件位置：kits/construct/README.md:46，kits/cut-plasmid/README.md:21、24，kits/genome-identity/REPORT.md:99，tests/oracles/prepare_cut_plasmid.py:76。本项不修改它们，分别交 Kit/发行负责人。
- D17 边界探针：将 320 nt 合成序列嵌入自然语言 original_request，公开 goal declare 接受，并原样写入日志。错误/报告脱敏不等于原始目标事件限长。是否原话也适用 200 nt 规则需规格负责人明确；本项只报告，不外发也不读用户 DNA。原始探针在 dist/spec-coverage-probes，结果只记长度与布尔值。
- C13：来源解析失败可留下 RUNNING，但已拒绝执行并拒绝封存；这是已登记的 S1 生命周期实现问题，不算缺了整个任务负责人。
- D3 仍说嵌套调用没有参数；用户获准的 945d702 与 Appendix E 已增加实际参数，现行代码可复算。此为文字残留，不自行改规格。

## D1–D20 必须语句逐句索引：33 句，来自 32 个命中行

精确提取“必须 / 恒必过 / 规格要求”，范围在 D1–D20，附录不串入 D20。历史问题、表头、条件式展望单独标明，不创造本期要求。一个复合句可同时含多个动作，证据列列明其未完成部分。无这些字样的章节仍由下节 119 条及上述接缝核对，不宣称只做词搜就覆盖科学正确性。

| 规格位置与句子 | 状态 / 实现 | 具体测试名或未执行 | 责任 / 剩余量 |
|---|---|---|---|
| D1 [SPEC:157](../../../spec/SPEC.md#L157)：**怎么测**：`ast` 解析所有 `src/` 与 `kits/` 的 import，对照契约（INV-L1、INV-L2）；环检测（INV-L3）；动态探针：运行时给调用器与封存函数装 spy，确认所有能力调用都经调用器、只有一处能创建封存包（INV-L4）；**契约充分性测试**：规格正文要求的跨模块调用必须是契约允许的子集（INV-L5）；扫描器自测：把故意违规的模块加入副本，扫描必须报错。 | 已实现/已测试（现有结构；不等于所有未来扩展已认证）；tools/check_structure.py；application/run_service.py | ApplicationTests.test_capabilities_use_one_invoker_and_one_seal_publisher；ContractTreeTests.test_reject_INV_L1 | S0/S1 |
| D2 [SPEC:167](../../../spec/SPEC.md#L167)：**问题**：旧系统里「用户要什么」散落在要求字典、目标条目、任务表、Kit 请求、记录的决策里，没有总对象 [已读]；好想法要保留：`source_quote` 必须逐字出现在原话里，未绑定任何可检查约束的条目被标为 `MISSED`，完成报告永远写 `original_task_verified: false` [已读]。 | 历史背景，不是现行验收；MISSED/旧字段不重新引入；GOL-4 现行行为见 line 200 | EngineTests.test_goal_original_and_constraint_ids_survive_amendment | 无新增工作 |
| D2 [SPEC:200](../../../spec/SPEC.md#L200)：- GOL-4 `source_quote` 必须逐字出现在 `original_request` 中；否则该约束标 `origin: host_derived`，视图画虚线并注明「约束由宿主推导，非用户原话」。 | 已实现/已测试；engine/goal.py:prepare | EngineTests.test_goal_original_and_constraint_ids_survive_amendment | S1/S1.1 |
| D3 [SPEC:256](../../../spec/SPEC.md#L256)：\| **`final_checks`**（对应 `final`） \| 只要这个能力被用到，就必须通过的检查（本身也是能力） \| 封存终检：并入必过项（D7） \| | 已实现/已测试；D3 嵌套参数旧文仍需与获准补丁对齐；assurance/obligations.py；catalog/registry.py:_validate_models；capabilities/model_agreement.py | AssuranceTests.test_profile_union_cannot_be_reduced_by_roles_or_missing_loaded_kit；ModelTests.test_bad_model_names_and_product_ports_are_isolated | S1/S1c |
| D3 [SPEC:262](../../../spec/SPEC.md#L262)：- **独立预期模型 `model`**：可选，指向一个**独立实现**的「预期产物」能力（保留旧处理器 `recompute` 的双重计算思想）；声明了 `model` 就**自动**把 `check.model_agreement` 并入必过项（不必再写进 `final_checks`），它逐位比较两条路径的结果，两条路径在代码上必须相互独立。 | 已实现/已测试；D3 嵌套参数旧文仍需与获准补丁对齐；assurance/obligations.py；catalog/registry.py:_validate_models；capabilities/model_agreement.py | AssuranceTests.test_profile_union_cannot_be_reduced_by_roles_or_missing_loaded_kit；ModelTests.test_bad_model_names_and_product_ports_are_isolated | S1/S1c |
| D3 [SPEC:262](../../../spec/SPEC.md#L262)：**约定**：模型能力从原能力那次调用的记录里**按名字**取它声明要的输入与参数（名字必须在原能力里存在，否则声明装载失败）；比较的输出端口是两者共有的名为 `product` 的 `material` 端口（原能力没有 `product` 端口就不能声明 `model`）；比较内容是序列、拓扑与末端，**不比较注释**（注释由别的检查负责）。 | 已实现/已测试；D3 嵌套参数旧文仍需与获准补丁对齐；assurance/obligations.py；catalog/registry.py:_validate_models；capabilities/model_agreement.py | AssuranceTests.test_profile_union_cannot_be_reduced_by_roles_or_missing_loaded_kit；ModelTests.test_bad_model_names_and_product_ports_are_isolated | S1/S1c |
| D4 [SPEC:300](../../../spec/SPEC.md#L300)：多产物端口取单个成员**必须显式给 `index`**，不自动取第一个。 | 已实现/已测试；engine/admission.py；kernel/references.py；assurance/seal.py:preconditions | EngineTests.test_admission_checks_entire_plan_without_invocation；MaterialsTests.test_collection_and_explicit_item_bindings_run_and_replay | S1/S1.2 |
| D4 [SPEC:304](../../../spec/SPEC.md#L304)：- 允许**局部诊断计划**：`outputs` 暂未覆盖全部目标物时，接纳回执列出未绑定的目标物，目标保持开放；封存时所有 `required` 的目标物必须有合法绑定。 | 已实现/已测试；engine/admission.py；kernel/references.py；assurance/seal.py:preconditions | EngineTests.test_admission_checks_entire_plan_without_invocation；MaterialsTests.test_collection_and_explicit_item_bindings_run_and_replay | S1/S1.2 |
| D4 [SPEC:314](../../../spec/SPEC.md#L314)：\| `PLAN_CAPABILITY_UNKNOWN` \| 能力存在于**固定的目录快照**，运行条件可用；`use` 可省略版本，规范化时补成目录快照里的精确版本，写了版本则必须一致；只允许 `ACTION` 角色 \| | 已实现/已测试；engine/admission.py；kernel/references.py；assurance/seal.py:preconditions | EngineTests.test_admission_checks_entire_plan_without_invocation；MaterialsTests.test_collection_and_explicit_item_bindings_run_and_replay | S1/S1.2 |
| D4 [SPEC:318](../../../spec/SPEC.md#L318)：\| `PLAN_OUTPUT_INVALID` \| 输出引用存在，`target` 存在；允许暂时没有输出（局部诊断计划）；`required` 目标物必须有绑定是**封存的先决条件**（SEAL-1），不是接纳条件 \| | 已实现/已测试；engine/admission.py；kernel/references.py；assurance/seal.py:preconditions | EngineTests.test_admission_checks_entire_plan_without_invocation；MaterialsTests.test_collection_and_explicit_item_bindings_run_and_replay | S1/S1.2 |
| D5 [SPEC:338](../../../spec/SPEC.md#L338)：**步骤一旦开始就冻结**，其定义、相对顺序与位置永不改变；每次修订必须写触发原因和理由；修订不能改目标、不能减少检查；封存之后不能再修订。 | 已实现/已测试；engine/revision.py | EngineTests.test_failure_revision_replacement_retains_facts；test_concurrent_revision_and_frozen_failed_history | S1 |
| D5 [SPEC:360](../../../spec/SPEC.md#L360)：**操作集（封闭）**：`add_step`（插在指定步骤之后，且必须在所有已开始步骤之后）、`supersede_step`（只能对 `FAILED` 或 `PENDING` 的步骤，标记被哪一步取代；被取代的待执行步骤不再执行）、`set_outputs`。 | 已实现/已测试；engine/revision.py | EngineTests.test_failure_revision_replacement_retains_facts；test_concurrent_revision_and_frozen_failed_history | S1 |
| D5 [SPEC:365](../../../spec/SPEC.md#L365)：前两类的 `event_refs` 必须存在于日志并与类别相符，由引擎核对；后两类只记录并在视图里画虚线。 | 已实现/已测试；engine/revision.py | EngineTests.test_failure_revision_replacement_retains_facts；test_concurrent_revision_and_frozen_failed_history | S1 |
| D6 [SPEC:433](../../../spec/SPEC.md#L433)：*确定性*：声明 `deterministic:true` 的能力不得读时间或未播种的随机数；随机性必须来自显式 `seed` 参数。 | 现有算法/重放有证据；没有针对任意扩展的时钟/随机源强制隔离；capabilities/builtin/checks.py:replay；biology/ 现有纯函数 | AssuranceTests.test_replay_reads_original_inputs_and_does_not_write_run；CapabilityTests.test_reverse_complement_has_hand_constructed_oracles | S1/S1b |
| D7 [SPEC:449](../../../spec/SPEC.md#L449)：哪些检查必须通过，由**底盘根据「实际产出什么」和「实际用了谁的能力」推导**，宿主和计划都不能减少。 | 已实现/已测试；完整回归仍有旧断言失败，不能称总门通过；assurance/obligations.py；assurance/judge.py；kernel/verdict.py | AssuranceTests.test_self_report_pass_cannot_satisfy_a_required_check；KernelTests.test_verdict_requires_applicability_and_does_not_alias；test_s1c_* | S1/S1c |
| D7 [SPEC:480](../../../spec/SPEC.md#L480)：- `outcome`：`PASS`（检查了且符合）、`FAIL`（检查了且违反）、`UNKNOWN`（没能判断：证据不足、依赖缺失、检查本身出错——出错时附一条失败记录）、`NOT_APPLICABLE`（必须给 `applicability: {reason, basis}`：`reason` 是一句话原因，`basis` 指向使它不适用的事实；不接受「调用者说跳过」）。 | 已实现/已测试；完整回归仍有旧断言失败，不能称总门通过；assurance/obligations.py；assurance/judge.py；kernel/verdict.py | AssuranceTests.test_self_report_pass_cannot_satisfy_a_required_check；KernelTests.test_verdict_requires_applicability_and_does_not_alias；test_s1c_* | S1/S1c |
| D7 [SPEC:500](../../../spec/SPEC.md#L500)：\| `user_goal` \| `check.goal.nonempty`、`check.goal.target_role_met`、`check.goal.<约束种类>`（D2 的七种；其中 `check.goal.output_present` 的参数是可选的 `fields`，即输出文档必须含的字段名列表；其余种类的参数由各检查能力的声明定义） \| \| | 已实现/已测试；完整回归仍有旧断言失败，不能称总门通过；assurance/obligations.py；assurance/judge.py；kernel/verdict.py | AssuranceTests.test_self_report_pass_cannot_satisfy_a_required_check；KernelTests.test_verdict_requires_applicability_and_does_not_alias；test_s1c_* | S1/S1c |
| D7 [SPEC:511](../../../spec/SPEC.md#L511)：\| 输出里含**材料** \| `content_model` 的 `check.replay`、`check.lineage`、`check.annotation_integrity`、`check.cds_validity`、`check.biological_sanity`（**恒必过**，防止把 DNA 输出标成低档逃避序列检查） \| | 已实现/已测试；完整回归仍有旧断言失败，不能称总门通过；assurance/obligations.py；assurance/judge.py；kernel/verdict.py | AssuranceTests.test_self_report_pass_cannot_satisfy_a_required_check；KernelTests.test_verdict_requires_applicability_and_does_not_alias；test_s1c_* | S1/S1c |
| D7 [SPEC:520](../../../spec/SPEC.md#L520)：*检查能力的质量保证*：每个检查能力必带「必须通过」与「必须失败」两份样例（`fixtures`），测试实际运行 FAIL 样例确认其结果非 `PASS`；检查只读（除追加自己的裁决事件外，运行目录哈希相同；重放在临时目录里进行）；三处关键逻辑（`check.replay`、必过项推导、哈希链校验）做人工变异测试。 | 已实现/已测试；完整回归仍有旧断言失败，不能称总门通过；assurance/obligations.py；assurance/judge.py；kernel/verdict.py | AssuranceTests.test_self_report_pass_cannot_satisfy_a_required_check；KernelTests.test_verdict_requires_applicability_and_does_not_alias；test_s1c_* | S1/S1c |
| D11 [SPEC:697](../../../spec/SPEC.md#L697)：KIT-7 **清单里没声明的贡献一律不加载**；清单声明的每个贡献都必须有对应文件，反之亦然。 | 接口/装载已实现/已测试；明确不是 OS 沙箱；catalog/kits.py；catalog/registry.py；kernel/verdict.py | CatalogTests.test_bad_kit_is_isolated；test_bundled_discovery_and_explicit_duplicate_are_distinct_from_external；RuntimeStructureTests.test_unique_seal_publisher_and_label_owner | S1/Kit |
| D11 [SPEC:722](../../../spec/SPEC.md#L722)：\| 改裁决形状、词表、封存步骤 \| **根本没有接口**：裁决必须经 `kernel` 的构造函数且值取自词表，封存只在 `assurance` \| | 接口/装载已实现/已测试；明确不是 OS 沙箱；catalog/kits.py；catalog/registry.py；kernel/verdict.py | CatalogTests.test_bad_kit_is_isolated；test_bundled_discovery_and_explicit_duplicate_are_distinct_from_external；RuntimeStructureTests.test_unique_seal_publisher_and_label_owner | S1/Kit |
| D12 [SPEC:771](../../../spec/SPEC.md#L771)：- **经验规则**（实验室经验的自然语言记录）：只能以 `status: draft`、来源类 `lab_protocol`、行为者 `human` 进入；**自然语言到规则的转换结果必须经人确认才变成 `active`**。 | 部分流程约束；审核闭环未落实；resources/schemas/rule-v1.json；application/api.py:55；catalog/registry.py:120 | 规则模式有正反例；没有经验规则经真实人确认再激活的完整工具正例 | 人工＋S1，3–5小时估计 |
| D14 [SPEC:851](../../../spec/SPEC.md#L851)：**失败时怎么办**：词表测试失败即构建失败；新增词必须先改 `vocab.json`/`errors.json` 并附理由。 | 已实现/已测试；受保护变更仍须人工流程；kernel/vocab.py；kernel/errors.py；tools/check_structure.py | RuntimeStructureTests.test_verdict_constructor_and_exception_boundary；ContractTreeTests.test_reject_INV_V1 | S0/S1/人工 |
| D16 [SPEC:928](../../../spec/SPEC.md#L928)：- **发布流程（每步有记录）**：1 冻结：结构不变量与完整测试在**这个精确提交**上于 Windows 与 Ubuntu 的 GitHub CI 全部通过；**官方 GitLab 没有执行器，CI 未执行，所有文档必须如实写明，不得把 GitHub CI 称为 GitLab CI**。 | 部分实现；精确提交 CI、真实干净安装、发行身份加载与人工发布均未完成；tools/build_release.py；tools/clean_env_verify.py；application/run_service.py:create | ReleaseEngineeringTests.test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata；test_fresh_environment_plan_never_creates_or_installs | 发行＋S1＋人工，分项见缺口表 |
| D16 [SPEC:936](../../../spec/SPEC.md#L936)：**怎么测**：构建确定性（INV-W3）；版本字面量扫描（INV-W1）；装载校验的篡改测试；CI 报告必须绑定精确提交；不存在自动上传或冻结切换动作。 | 部分实现；精确提交 CI、真实干净安装、发行身份加载与人工发布均未完成；tools/build_release.py；tools/clean_env_verify.py；application/run_service.py:create | ReleaseEngineeringTests.test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata；test_fresh_environment_plan_never_creates_or_installs | 发行＋S1＋人工，分项见缺口表 |
| D17 [SPEC:962](../../../spec/SPEC.md#L962)：*隐私*：裁决证据、失败记录、事件的结果字段与报告默认不放原始序列，只放标识、长度、哈希与摘要；**唯一例外**是宿主自己写进目标与计划的短字面量（如 20 nt 间隔序列，每个不超过 200 nt，超过的必须作为输入文件，事件里只记哈希），它们会出现在 `goal.*`、`pipeline.*` 事件里，因此**封存包里的日志副本含这些短序列，对外公开前自行检查**；材料本体在运行目录的内容存储里（本机）；报告默认不含序列（`--include-sequences` 显式打开）；不保存输入文件的原绝对路径（只记运行目录相对路径与 sha256）；没有遥测；**用户真实 DNA 绝不进仓库**，测试只用合成数据。 | 网络/来源路径已有证据；320nt原话仍进入日志的边界见只读探针，未宣称全面拦截；application/config.py；kernel/redact.py；engine/goal.py；tests/e2e/network_guard.py | EngineTests.test_goal_import_uses_actual_bytes_and_does_not_persist_from；EndToEndTests.test_network_guard_detects_its_deliberate_control；追加串联42次CLI | S1＋规格负责人 |
| D17 [SPEC:970](../../../spec/SPEC.md#L970)：**怎么测**：INV-X2 默认命令集与示例运行时**零次**网络连接尝试（子进程里把 `socket` 的 `connect`、`connect_ex`、`create_connection`、`getaddrinfo` 换成「计数并失败」（Linux CI 上可选再用 `unshare -n` 跑一遍以覆盖子进程；含自测：故意加一个联网调用，测试必须失败））；INV-X3 源码里没有 `pip`、`urllib`、`requests`、`http.client`、`socket`（测试工具白名单）；INV-X4 无 `shell=True`；配置优先级参数化测试；`doctor` 不执行任何安装。 | 网络/来源路径已有证据；320nt原话仍进入日志的边界见只读探针，未宣称全面拦截；application/config.py；kernel/redact.py；engine/goal.py；tests/e2e/network_guard.py | EngineTests.test_goal_import_uses_actual_bytes_and_does_not_persist_from；EndToEndTests.test_network_guard_detects_its_deliberate_control；追加串联42次CLI | S1＋规格负责人 |
| D18 [SPEC:995](../../../spec/SPEC.md#L995)：**静态扫描必须配动态探针和故意破坏的反例**，不能只搜关键词。 | 已实现检查有破坏对照；未实现检查不能因此计通过；CI作业仍缺；tools/check_structure.py；tools/run_s1_mutations.py；tests/SKIPS.json | ContractTreeTests.test_reject_INVENTORY；test_reject_INV_Q4；tests/integration/test_crash_recovery.py | S0/S1/发行 |
| D18 [SPEC:1005](../../../spec/SPEC.md#L1005)：*新增的结构测试*（本稿合并时补入）：**契约充分性**（正文需要的跨模块调用必须是依赖契约允许的子集，INV-L5）；**角色降级无效**（INV-A6）；**缺失检查记 `UNKNOWN`**（INV-A5）；**日志尾部强杀恢复**（INV-E5）；**规格自洽扫描**（INV-S1…S6：事件名、动词、模块路径、规则编号是否对得上，并扫退役词残留）。 | 已实现检查有破坏对照；未实现检查不能因此计通过；CI作业仍缺；tools/check_structure.py；tools/run_s1_mutations.py；tests/SKIPS.json | ContractTreeTests.test_reject_INVENTORY；test_reject_INV_Q4；tests/integration/test_crash_recovery.py | S0/S1/发行 |
| D18 [SPEC:1013](../../../spec/SPEC.md#L1013)：**怎么测**：测试框架自测（故意违规 → 结构测试必须报错）；`SKIPS.json` 过期测试；`oracle` 字段完整性检查；变异测试的执行记录。 | 已实现检查有破坏对照；未实现检查不能因此计通过；CI作业仍缺；tools/check_structure.py；tools/run_s1_mutations.py；tests/SKIPS.json | ContractTreeTests.test_reject_INVENTORY；test_reject_INV_Q4；tests/integration/test_crash_recovery.py | S0/S1/发行 |
| D19 [SPEC:1030](../../../spec/SPEC.md#L1030)：*展望（未做，不进首版）*：探索／预览模式（现在想先试试就不封存，结果照常给，标「未封存」；若将来要「检查较少的预览包」，必须把少做的检查清单写进包里，且永远不能当作正式交付）；代码沙箱（在调用器外面加壳，不改结构）；联网取序列与外部服务的自动提交；Construct 与 Genome Identity 两个 Kit。 | 未做，明确首版范围之外；条件式预览不能当正式交付；D19 范围声明 | 无运行时产品需要补造 | 不列本期缺口 |
| D19 [SPEC:1047](../../../spec/SPEC.md#L1047)：\| 判断点 \| 必须检查 \| 动作 \| | 表头，不是独立可执行检查；D19 时间判断点 | 人工流程，不用假测试充数 | 用户／负责人 |
| D20 [SPEC:1095](../../../spec/SPEC.md#L1095)：- RV-7 发布流程（D16）第 4 步的发布记录必须列出本版包含的所有审核记录及其状态，**由人逐项确认**。 | 未闭环：审核工具与逐对象展示缺实现；发布确认必须由人做；application/api.py:55；knowledge/review.py 为空；catalog/registry.py:120 | review-v1 模式样例不等于交互签注/过期识别测试 | S1＋发行＋人工 |

## 附录 C 全量索引：119 条

以下“登记已实现”只陈述覆盖登记与可定位的现有实现/测试，不是新的人审批准。特别条目优先用前面的实查结论。测试文件里的具体方法见上节与现有 IMPLEMENTED_INV.evidence；需要重新验收的不能仅靠登记关闭。

| 不变量 / 规格位置 | 要求 | 实现与测试证据 | 状态与责任 |
|---|---|---|---|
| INV-L1 [SPEC:1233](../../../spec/SPEC.md#L1233) | 每个 `src/` 模块的项目内 import ⊆ `contracts.toml [allow]` | tools/check_structure.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-L2 [SPEC:1234](../../../spec/SPEC.md#L1234) | 每个 `kits/*/` 的 import ⊆ `[kit_allow]` ＋ 自己的包 | tools/check_structure.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-L3 [SPEC:1235](../../../spec/SPEC.md#L1235) | 模块图没有 import 环 | tools/check_structure.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-L4 [SPEC:1236](../../../spec/SPEC.md#L1236) | 动态探针：所有能力调用都经调用器；只有一处能创建封存包 | tools/check_structure.py；tests/unit/test_application.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-C6 [SPEC:1237](../../../spec/SPEC.md#L1237) | 可调用单元只有 `capability-v1` 一种声明；不存在另一种检查声明或检查注册表 | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/unit/test_capabilities.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-C7 [SPEC:1238](../../../spec/SPEC.md#L1238) | `CHECK` 能力：`effects ⊆ {pure, reads_files}`，恰有一个 `scope`，带通过与失败两份样例，失败样例实际运行结果非 `PASS` | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/unit/test_capabilities.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-P1 [SPEC:1239](../../../spec/SPEC.md#L1239) | 没有已接纳的计划与步骤，就不能经正式接口执行业务能力 | src/dna_design_core/engine/admission.py；src/dna_design_core/kernel/references.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-P2 [SPEC:1240](../../../spec/SPEC.md#L1240) | `pipeline-v1` 模式 `additionalProperties:false`，且无法表达检查、门、必需范围、`deliver_as` | src/dna_design_core/engine/admission.py；src/dna_design_core/kernel/references.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-P3 [SPEC:1241](../../../spec/SPEC.md#L1241) | **接纳校验期间调用器的调用数为 0**（最后一步非法时第一步也不执行） | src/dna_design_core/engine/admission.py；src/dna_design_core/kernel/references.py；tests/unit/test_engine.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1 |
| INV-P6 [SPEC:1242](../../../spec/SPEC.md#L1242) | 只有 `ACTION` 角色的能力可以出现在计划里 | src/dna_design_core/engine/admission.py；src/dna_design_core/kernel/references.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-R1 [SPEC:1243](../../../spec/SPEC.md#L1243) | 已开始步骤的定义在后续所有 `pipeline.*` 事件里逐字不变 | src/dna_design_core/engine/revision.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-R3 [SPEC:1244](../../../spec/SPEC.md#L1244) | 修订的 `reason` 事件早于新步骤的执行事件 | src/dna_design_core/engine/revision.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-R4 [SPEC:1245](../../../spec/SPEC.md#L1245) | 含 `seal.created` 的 run 拒绝任何修订 | src/dna_design_core/engine/revision.py；tests/unit/test_application.py | 登记已实现、有当前代码/测试；S1 |
| INV-E1 [SPEC:1246](../../../spec/SPEC.md#L1246) | 写日志的调用只出现在 `engine`、`assurance`、`application` 的白名单函数与 `storage` 的恢复例程 | src/dna_design_core/engine/executor.py；src/dna_design_core/storage/journal.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S1 |
| INV-E2 [SPEC:1247](../../../spec/SPEC.md#L1247) | 步骤完成或失败后其记录不再被修改（存储只写一次、读时校验） | src/dna_design_core/engine/executor.py；src/dna_design_core/storage/journal.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-A1 [SPEC:1248](../../../spec/SPEC.md#L1248) | 检查结果永远不通过异常传递 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A2 [SPEC:1249](../../../spec/SPEC.md#L1249) | 裁决只通过 `kernel.verdict.make` 构造；`outcome/scope/moment/issuer` 字面量来自词表 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A4 [SPEC:1250](../../../spec/SPEC.md#L1250) | 必过项只取并集，宿主任何输入都不能使其变少（属性测试） | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A5 [SPEC:1251](../../../spec/SPEC.md#L1251) | 必过检查缺失或不可用 → `UNKNOWN`（`CHECK_UNAVAILABLE`），不是跳过 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/unit/test_assurance.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A6 [SPEC:1252](../../../spec/SPEC.md#L1252) | 给输出贴低档角色无效；含材料输出时 `content_model` 检查恒必过 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A9 [SPEC:1253](../../../spec/SPEC.md#L1253) | `tool_self_report` 与 `host_expectation` 的裁决不计入必过项 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A10 [SPEC:1254](../../../spec/SPEC.md#L1254) | 继承发现只在 `check.annotation_integrity`、`check.cds_validity` 里按输入输出逐项比较给 `PASS`，且必带 `INHERITED_FINDINGS` 标签；引入的或来源不明的发现给 `FAIL` | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/integration/test_s1c_content.py；tests/integration/test_s1c_cds.py；tools/run_s1c_mutations.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-D1 [SPEC:1255](../../../spec/SPEC.md#L1255) | 封存目录创建后不被任何函数修改 | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/unit/test_application.py | 登记已实现、有当前代码/测试；S1 |
| INV-D2 [SPEC:1256](../../../spec/SPEC.md#L1256) | `seal_id` ＝清单摘要，清单不含 `seal_id` 与自身；卡片只显示 `journal_head` | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/e2e/test_examples.py | 登记已实现、有当前代码/测试；S1 |
| INV-D6 [SPEC:1257](../../../spec/SPEC.md#L1257) | 封存包单独复制到新位置后 `verify` 通过 | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1 |
| INV-D7 [SPEC:1258](../../../spec/SPEC.md#L1258) | 封存总是对暂存包重新运行全部必过项，不复用任何先前裁决 | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/unit/test_application.py | 登记已实现、有当前代码/测试；S1 |
| INV-I1 [SPEC:1259](../../../spec/SPEC.md#L1259) | `hashlib` 只在 `kernel/ids.py` | src/dna_design_core/kernel/ids.py；src/dna_design_core/kernel/canonical.py；tests/unit/test_kernel.py | 登记已实现、有当前代码/测试；S1 |
| INV-I3 [SPEC:1260](../../../spec/SPEC.md#L1260) | 所有测试 run 的日志哈希链有效 | src/dna_design_core/kernel/ids.py；src/dna_design_core/kernel/canonical.py；tests/e2e/test_examples.py | 登记已实现、有当前代码/测试；S1 |
| INV-T1 [SPEC:1261](../../../spec/SPEC.md#L1261) | `record` 包内没有任何写日志调用，也不 import 引擎、检查层内部 | src/dna_design_core/record/projections.py；src/dna_design_core/record/render/runcard.py；tests/unit/test_record.py | 登记已实现、有当前代码/测试；S1 |
| INV-T2 [SPEC:1262](../../../spec/SPEC.md#L1262) | 每条实线都有显式输入绑定且哈希相等（随机重算）；无绑定的偶然相等画虚线 | src/dna_design_core/record/projections.py；src/dna_design_core/record/render/runcard.py；tests/unit/test_record.py | 登记已实现、有当前代码/测试；S1 |
| INV-T6 [SPEC:1263](../../../spec/SPEC.md#L1263) | 自检与宿主断言的裁决不出现在「Checked by the program」栏 | src/dna_design_core/record/projections.py；src/dna_design_core/record/render/runcard.py；tests/unit/test_record.py | 登记已实现、有当前代码/测试；S1 |
| INV-K1 [SPEC:1264](../../../spec/SPEC.md#L1264) | Kit 包内 Python 只在 `capabilities/` 下；无 `main/argparse`；无报告渲染代码 | src/dna_design_core/catalog/kits.py；src/dna_design_core/catalog/registry.py；tests/unit/test_catalog.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S1／Kit 任务 |
| INV-K2 [SPEC:1265](../../../spec/SPEC.md#L1265) | Kit import ⊆ `[kit_allow]` ＋ 自己的包 | src/dna_design_core/catalog/kits.py；src/dna_design_core/catalog/registry.py；tests/unit/test_catalog.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S1／Kit 任务 |
| INV-K7 [SPEC:1266](../../../spec/SPEC.md#L1266) | 清单模式没有档位、输出角色、接纳规则、交付类别之类的键 | src/dna_design_core/catalog/kits.py；src/dna_design_core/catalog/registry.py；tests/unit/test_catalog.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S1／Kit 任务 |
| INV-H1 [SPEC:1267](../../../spec/SPEC.md#L1267) | `verbs.json` ＝实际注册的动词＝`api.__all__` | src/dna_design_core/application/api.py；src/dna_design_core/application/cli.py；tools/docgen.py；tests/unit/test_application.py | 登记已实现、有当前代码/测试；S1 |
| INV-V1 [SPEC:1268](../../../spec/SPEC.md#L1268) | `outcome/scope/moment/issuer/state` 字面量来自词表 | src/dna_design_core/kernel/verdict.py；src/dna_design_core/kernel/errors.py；src/dna_design_core/kernel/vocab.py；tests/unit/test_kernel.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-W2 [SPEC:1269](../../../spec/SPEC.md#L1269) | `VERSIONS.json` 是唯一手写版本来源 | tools/build_release.py；src/dna_design_core/kernel/release.py；tests/unit/test_release_engineering.py | 登记已实现、有当前代码/测试；S1／S4a |
| INV-X1 [SPEC:1270](../../../spec/SPEC.md#L1270) | `os.environ` 只在 `application/config.py` | src/dna_design_core/application/config.py；tools/check_structure.py；tests/e2e/test_examples.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-X2 [SPEC:1271](../../../spec/SPEC.md#L1271) | 默认命令集与示例零次网络连接尝试 | src/dna_design_core/application/config.py；tools/check_structure.py；tests/e2e/test_examples.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-Q1 [SPEC:1272](../../../spec/SPEC.md#L1272) | `tests/structure` 在 CI 里是独立作业，且是其他作业的前置 | 没有 .github 工作流；S4a 只分配构建/检查/安装脚本，未分配 CI 配置。 | 未落实具体任务；发行，估计3–5小时 |
| INV-Q3 [SPEC:1273](../../../spec/SPEC.md#L1273) | 夹具 `oracle` 字段指明来源类别 `construction | tools/check_structure.py；tests/SKIPS.json；tests/structure/test_contract_tree.py；tests/unit/test_registered_primer3_skip.py | 登记已实现、有当前代码/测试；S0／S1b |
| INV-L5 [SPEC:1279](../../../spec/SPEC.md#L1279) | 契约充分性：规格正文需要的跨模块调用 ⊆ 契约允许的调用 | tools/check_structure.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-G1 [SPEC:1280](../../../spec/SPEC.md#L1280) | `goal_digest` 只由 `engine.goal` 计算 | src/dna_design_core/engine/goal.py；src/dna_design_core/capabilities/builtin/check/goal.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S1／S1b-C2 |
| INV-G2 [SPEC:1281](../../../spec/SPEC.md#L1281) | 约束 id 永不从任何目标版本中消失（只会 `dropped`） | src/dna_design_core/engine/goal.py；src/dna_design_core/capabilities/builtin/check/goal.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1／S1b-C2 |
| INV-G3 [SPEC:1282](../../../spec/SPEC.md#L1282) | `original_request` 在所有版本逐字相同 | src/dna_design_core/engine/goal.py；src/dna_design_core/capabilities/builtin/check/goal.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1／S1b-C2 |
| INV-G4 [SPEC:1283](../../../spec/SPEC.md#L1283) | 目标物角色取自词表；角色与实际输出不符 → `check.goal.target_role_met` 为 `FAIL` | src/dna_design_core/engine/goal.py；src/dna_design_core/capabilities/builtin/check/goal.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1／S1b-C2 |
| INV-G5 [SPEC:1284](../../../spec/SPEC.md#L1284) | 宿主提交的声明，行为者恒为 `ai_host`；程序执行与检查的事件为 `program`；`human` 只出现在交互式确认的记录里 | src/dna_design_core/engine/goal.py；src/dna_design_core/capabilities/builtin/check/goal.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1／S1b-C2 |
| INV-C1 [SPEC:1285](../../../spec/SPEC.md#L1285) | `resources/capabilities/*.json` 与代码导出一致 | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/unit/test_capabilities.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-C2 [SPEC:1286](../../../spec/SPEC.md#L1286) | 每个能力 `does_not_establish` 非空，`summary` ≤200 字符 | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/unit/test_capabilities.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-C3 [SPEC:1287](../../../spec/SPEC.md#L1287) | `atomic` 能力不调用其他能力；`composite` 只经 `ctx.call` | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/structure/test_runtime_contracts.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-C4 [SPEC:1288](../../../spec/SPEC.md#L1288) | 非 `writes_files` 能力没有文件写入（AST 扫描加调用后检测；v1 没有沙箱，不做操作系统级强制） | engine/invoker.py:_invoke；S1 层，下一项实做；不是本项实现 | 已分配，未全覆盖；S1c 追加任务 3 |
| INV-C5 [SPEC:1289](../../../spec/SPEC.md#L1289) | 能力 id 唯一 | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/unit/test_catalog.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-C8 [SPEC:1290](../../../spec/SPEC.md#L1290) | `CHECK` 角色的能力 id 以 `check` 开头（核心 `check.…`，Kit `<命名空间>.check_…`）；`ACTION` 角色的 id 不以 `check` 开头 | src/dna_design_core/catalog/registry.py；src/dna_design_core/engine/invoker.py；tests/unit/test_capabilities.py | 登记已实现、有当前代码/测试；S1／S1b／S1c |
| INV-P4 [SPEC:1291](../../../spec/SPEC.md#L1291) | 规范化幂等 | src/dna_design_core/engine/admission.py；src/dna_design_core/kernel/references.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-P5 [SPEC:1292](../../../spec/SPEC.md#L1292) | 紧凑与规范两种写法摘要相同 | src/dna_design_core/engine/admission.py；src/dna_design_core/kernel/references.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-R2 [SPEC:1293](../../../spec/SPEC.md#L1293) | 失败或被取代步骤的输出不被后续步骤引用 | src/dna_design_core/engine/revision.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-R5 [SPEC:1294](../../../spec/SPEC.md#L1294) | `expected_digest` 不符的修订被拒；并发修订只有一个成功 | src/dna_design_core/engine/revision.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-R6 [SPEC:1295](../../../spec/SPEC.md#L1295) | 重试＝新增步骤并取代旧步骤，原失败保留 | src/dna_design_core/engine/revision.py；tests/unit/test_engine.py | 登记已实现、有当前代码/测试；S1 |
| INV-E3 [SPEC:1296](../../../spec/SPEC.md#L1296) | 能力只通过 `ctx` 与外界交互（内置能力有运行时测试与调用后检测；外部 Kit 的越界 I/O v1 只能事后发现，不能阻止） | engine/invoker.py:Context/_invoke；S1 层；v1 无 OS 沙箱 | 已分配，未全覆盖；S1c 追加任务 3 |
| INV-E4 [SPEC:1297](../../../spec/SPEC.md#L1297) | 环境指纹只在 `run.created` 里记录一次，不在步骤内产生 | src/dna_design_core/engine/executor.py；src/dna_design_core/storage/journal.py；tests/e2e/test_examples.py | 登记已实现、有当前代码/测试；S1 |
| INV-E5 [SPEC:1298](../../../spec/SPEC.md#L1298) | 日志尾部写到一半后强杀：恢复到最后完好事件并记 `journal.recovered`；非尾部损坏则拒绝继续 | src/dna_design_core/engine/executor.py；src/dna_design_core/storage/journal.py；tests/integration/test_crash_recovery.py | 登记已实现、有当前代码/测试；S1 |
| INV-E6 [SPEC:1299](../../../spec/SPEC.md#L1299) | run 创建时记录目录快照，必过项按快照推导 | src/dna_design_core/engine/executor.py；src/dna_design_core/storage/journal.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1 |
| INV-A3 [SPEC:1300](../../../spec/SPEC.md#L1300) | 三处关键逻辑（`check.replay`、必过项推导、哈希链校验）的人工变异能被样例抓到 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tools/run_s1_mutations.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A7 [SPEC:1301](../../../spec/SPEC.md#L1301) | 检查不修改既有输入、内容存储和候选；除追加自己的 `verdict.issued` 事件外运行目录不变 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-A8 [SPEC:1302](../../../spec/SPEC.md#L1302) | `NOT_APPLICABLE` 必须带原因与依据 | src/dna_design_core/assurance/obligations.py；src/dna_design_core/assurance/judge.py；src/dna_design_core/capabilities/builtin/checks.py；tests/unit/test_kernel.py | 登记已实现、有当前代码/测试；S1／S1c |
| INV-D3 [SPEC:1303](../../../spec/SPEC.md#L1303) | 封存条件只由必过项计算，无第二套判据 | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/structure/test_runtime_contracts.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1 |
| INV-D4 [SPEC:1304](../../../spec/SPEC.md#L1304) | 「未封存」等标签只在 `assurance.labels` 产生 | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S1 |
| INV-D5 [SPEC:1305](../../../spec/SPEC.md#L1305) | 不存在 `GATE_*` 异常类或错误码 | src/dna_design_core/assurance/seal.py；src/dna_design_core/assurance/verify.py；tests/unit/test_assurance.py | 登记已实现、有当前代码/测试；S1 |
| INV-I2 [SPEC:1306](../../../spec/SPEC.md#L1306) | 黄金向量跨平台与 Python 版本一致 | tests/unit/test_kernel.py；发行／环境；今晚明确不做 | 已分配，环境未执行；S1.1 第5项、规格负责人 S4 交接 |
| INV-I4 [SPEC:1307](../../../spec/SPEC.md#L1307) | 特征顺序、名称、描述、日期变化不改 `material_id`；序列或注释变化改变它 | src/dna_design_core/kernel/ids.py；src/dna_design_core/kernel/canonical.py；tests/unit/test_kernel.py | 登记已实现、有当前代码/测试；S1 |
| INV-I5 [SPEC:1308](../../../spec/SPEC.md#L1308) | 所有输出标识匹配 `^[0-9a-f]{64}$`（`run_id` 为 16 位） | src/dna_design_core/kernel/ids.py；src/dna_design_core/kernel/canonical.py；tests/e2e/test_examples.py | 登记已实现、有当前代码/测试；S1 |
| INV-I6 [SPEC:1309](../../../spec/SPEC.md#L1309) | 被哈希的对象里没有裸浮点数 | src/dna_design_core/kernel/ids.py；src/dna_design_core/kernel/canonical.py；tests/unit/test_kernel.py | 登记已实现、有当前代码/测试；S1 |
| INV-I7 [SPEC:1310](../../../spec/SPEC.md#L1310) | 每个步骤输入都记录来源 `{kind, ref}` | src/dna_design_core/kernel/ids.py；src/dna_design_core/kernel/canonical.py；tests/e2e/test_examples.py | 登记已实现、有当前代码/测试；S1 |
| INV-T3 [SPEC:1311](../../../spec/SPEC.md#L1311) | 运行卡片只有三栏；封存清单 `not_verified` 的每一条都出现在「Not done」栏 | src/dna_design_core/record/projections.py；src/dna_design_core/record/render/runcard.py；tests/unit/test_record.py | 登记已实现、有当前代码/测试；S1 |
| INV-T4 [SPEC:1312](../../../spec/SPEC.md#L1312) | 删除 `views/` 后可完整重建，字节一致 | src/dna_design_core/record/projections.py；src/dna_design_core/record/render/runcard.py；tests/unit/test_record.py | 登记已实现、有当前代码/测试；S1 |
| INV-T5 [SPEC:1313](../../../spec/SPEC.md#L1313) | 卡片声明事件截止点 | src/dna_design_core/record/projections.py；src/dna_design_core/record/render/runcard.py；tests/unit/test_record.py | 登记已实现、有当前代码/测试；S1 |
| INV-K3 [SPEC:1314](../../../spec/SPEC.md#L1314) | 清单声明的贡献（含 `text`）与文件一一对应 | catalog/registry.py:_register；CatalogTests.test_conflicting_external_implementations_disable_both | 已有实作，PENDING 原因过时；S1 catalog / Kit 发现 |
| INV-K4 [SPEC:1315](../../../spec/SPEC.md#L1315) | 卸载 Kit 后注册表与装载前一致 | src/dna_design_core/catalog/kits.py；src/dna_design_core/catalog/registry.py；tests/unit/test_catalog.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／Kit 任务 |
| INV-K5 [SPEC:1316](../../../spec/SPEC.md#L1316) | Kit 的 `final_checks` 出现在必过项里（玩具 Kit 验证） | src/dna_design_core/catalog/kits.py；src/dna_design_core/catalog/registry.py；tests/unit/test_capabilities.py；tests/unit/test_s1_followup2.py；tests/e2e/test_s1_followup2.py | 登记已实现、有当前代码/测试；S1／Kit 任务 |
| INV-K6 [SPEC:1317](../../../spec/SPEC.md#L1317) | Kit 之间没有 import 关系 | src/dna_design_core/catalog/kits.py；src/dna_design_core/catalog/registry.py；tests/unit/test_catalog.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S1／Kit 任务 |
| INV-N1 [SPEC:1318](../../../spec/SPEC.md#L1318) | 所有 `rule-v1` 有合法来源，类别不是 `AI/internet/latest` | src/dna_design_core/catalog/registry.py；src/dna_design_core/resources/schemas/rule-v1.json；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1／S3 |
| INV-N2 [SPEC:1319](../../../spec/SPEC.md#L1319) | 检查与分析代码里无阈值字面量（白名单登记除外；**启发式**） | 分析代码已有，但 check_structure 没有这条扫描及白名单自测；S1b 算法任务未分配扫描器。 | 未落实具体任务；生物层＋S1 层，估计3–5小时 |
| INV-N3 [SPEC:1320](../../../spec/SPEC.md#L1320) | `review/` 下文件只由审核命令写入（流程＋AST） | review 模块空白；没有审核写入边界扫描和破坏对照。S2 仅实现 Kit，不能改共享层。 | 未落实具体任务；S1 层，估计1–2小时 |
| INV-N4 [SPEC:1321](../../../spec/SPEC.md#L1321) | `active` 规则无审核记录时，交付清单显示「未经人工审核」 | catalog/registry.py:120 固定 none；assurance/labels.py 只汇总计数；仅有 none/标签测试，不证明逐对象未审核文字与正确状态 | 部分显示，无完整责任任务；S1 层，2–4 小时 |
| INV-N5 [SPEC:1322](../../../spec/SPEC.md#L1322) | 适用所需信息缺失 → `UNKNOWN`，不是 `FAIL` | kits/revival-evidence/capabilities/assessment.py:matches/conclude；EvidenceTests、CutPlasmidTests；不宣称任意规则都完备 | 已有 Kit 求值/未知行为，登记未闭合；S3 规则真值表、S2 筛选边界 |
| INV-RV1 [SPEC:1323](../../../spec/SPEC.md#L1323) | 审核记录与对象哈希不符 → `stale` | knowledge/review.py 为空；目录快照把审核数固定为 none，未读取审核记录。S3 未分配 Core 实现。 | 未落实具体任务；S1 层，估计3–5小时 |
| INV-RV2 [SPEC:1324](../../../spec/SPEC.md#L1324) | `review sign` 非交互环境退出码非 0 且不写文件 | application/api.py:55 对所有调用返回不可用；未见真实交互正例；当前拒绝不能算审核功能完成 | 只有拒绝占位，无交互签注闭环；S1 层＋人工，3–5 小时 |
| INV-RV3 [SPEC:1325](../../../spec/SPEC.md#L1325) | 封存清单标签覆盖本 run 用到的每条规则与模板 | catalog/registry.py:120；assurance/labels.py:collect；现有计数不读模板审核，不限定本 run 实际用到的对象 | 部分计数，无规则/模板逐项覆盖；S1 层，2–4 小时 |
| INV-RV4 [SPEC:1326](../../../spec/SPEC.md#L1326) | 代码里除 `review sign` 外没有写入 `review/` 的调用 | 与 N3 同一缺口；现有通用 writer 扫描面向事件日志，不是 review 目录。 | 未落实具体任务；S1 层，估计同 N3小时 |
| INV-H2 [SPEC:1327](../../../spec/SPEC.md#L1327) | 生成区块与声明一致（重新生成后无差异） | src/dna_design_core/application/api.py；src/dna_design_core/application/cli.py；tools/docgen.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S1 |
| INV-H3 [SPEC:1328](../../../spec/SPEC.md#L1328) | 所有动词的 JSON 输出符合回执信封 | src/dna_design_core/application/api.py；src/dna_design_core/application/cli.py；tools/docgen.py；tests/integration/test_cli.py | 登记已实现、有当前代码/测试；S1 |
| INV-H4 [SPEC:1329](../../../spec/SPEC.md#L1329) | `describe` 不 import 任何能力实现（受限环境运行） | src/dna_design_core/application/api.py；src/dna_design_core/application/cli.py；tools/docgen.py；tests/unit/test_catalog.py | 登记已实现、有当前代码/测试；S1 |
| INV-H5 [SPEC:1330](../../../spec/SPEC.md#L1330) | `SKILL.md` 手写区不含数量、版本、清单 | docgen 检查生成区是否新鲜，保留手写区原样；未见手写区违规对照。早期空树延期没有后续承接。 | 未落实具体任务；S1 层／文档，估计1–2小时 |
| INV-H6 [SPEC:1331](../../../spec/SPEC.md#L1331) | 带内容的动词使用请求文件 | src/dna_design_core/application/api.py；src/dna_design_core/application/cli.py；tools/docgen.py；tests/integration/test_cli.py | 登记已实现、有当前代码/测试；S1 |
| INV-V2 [SPEC:1332](../../../spec/SPEC.md#L1332) | 所有 `raise` 的错误码都登记在 `errors.json` | src/dna_design_core/kernel/verdict.py；src/dna_design_core/kernel/errors.py；src/dna_design_core/kernel/vocab.py；tests/unit/test_kernel.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-V3 [SPEC:1333](../../../spec/SPEC.md#L1333) | 不存在除 `ToolkitError/CapabilityError` 之外的 `Exception` 子类 | src/dna_design_core/kernel/verdict.py；src/dna_design_core/kernel/errors.py；src/dna_design_core/kernel/vocab.py；tests/unit/test_kernel.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-V4 [SPEC:1334](../../../spec/SPEC.md#L1334) | 词表生成物与 `vocab.json` 一致 | src/dna_design_core/kernel/verdict.py；src/dna_design_core/kernel/errors.py；src/dna_design_core/kernel/vocab.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-F1 [SPEC:1335](../../../spec/SPEC.md#L1335) | `ship.json` 与目录树一致 | tools/build_release.py:payload；tools/check_release.py；ReleaseEngineeringTests；实际发行还被披露/路径阻止 | 已分配且有构建/检查代码；S4a 第1/2项 |
| INV-F3 [SPEC:1336](../../../spec/SPEC.md#L1336) | 序列夹具都登记在 `MANIFEST.json`（合成或第三方带许可） | 现有是每次运行封存 manifest、函数 oracle 表和生成器，均不是全局序列夹具身份清单。 | 未落实具体任务；发行＋生物层，估计2–4小时 |
| INV-F4 [SPEC:1337](../../../spec/SPEC.md#L1337) | `src/` 无 `snapgene` 标识符（格式读写文件白名单除外） | tools/check_structure.py；tools/check_release.py；tests/structure/test_contract_tree.py；tests/unit/test_release_engineering.py | 登记已实现、有当前代码/测试；S0／S4a |
| INV-F5 [SPEC:1338](../../../spec/SPEC.md#L1338) | 构建产物不入库 | tools/check_structure.py；tools/check_release.py；tests/structure/test_contract_tree.py；tests/unit/test_release_engineering.py | 登记已实现、有当前代码/测试；S0／S4a |
| INV-F6 [SPEC:1339](../../../spec/SPEC.md#L1339) | 夹具登记的名称与哈希不出现在 `src/` 与 Kit 的能力代码 | 缺 F3 登记，也没有 F6 对应扫描器和故意特判对照。 | 未落实具体任务；S1 层／发行，估计2–4小时 |
| INV-F7 [SPEC:1340](../../../spec/SPEC.md#L1340) | `contracts.toml`、`vocab.json`、`errors.json`、`profiles.json`、`schemas/*`、`verbs.json`、`ship.json`、`VERSIONS.json` 的哈希与决策记录里最新登记一致 | S4a 交接明确说 F10 不是 F7；现有决定/审核流程不等于实现这项自动比对。 | 未落实具体任务；发行＋人工，估计2–4小时 |
| INV-F8 [SPEC:1341](../../../spec/SPEC.md#L1341) | 仓库内无旧包名与旧模块名引用 | F4 只扫描运行时代码标识符；不是 F8 的全仓引用检查。迁移证据仍需合法旧路径例外。 | 未落实具体任务；发行，估计1–2小时 |
| INV-F9 [SPEC:1342](../../../spec/SPEC.md#L1342) | 带 `# ported-from:` 头的文件均登记于 `MIGRATION-MAP.md`，且旧路径存在 | MIGRATION-LOG.md；tests/oracles/migration_inventory.py；任务指定 LOG、规格指定 MAP，负责人决定，不改规格 | 已有迁移登记，但规格落点存在冲突；S0 第9项、S1b 迁移日志 |
| INV-F10 [SPEC:1343](../../../spec/SPEC.md#L1343) | 发行包含 `LICENSE`、`README.md` 的必需章节与锁定依赖文件，不含 `.exe`／`.bin`／`.dll` 等编译产物，git 仓库小于 50 MB | tools/check_release.py:inspect_tree；ReleaseEngineeringTests；4条路径命中、5个占位未清 | 已实现检查，当前真实树 FAIL/INCOMPLETE；S4a 第2项 |
| INV-W1 [SPEC:1344](../../../spec/SPEC.md#L1344) | 版本字面量只出现在生成文件 | tools/build_release.py；src/dna_design_core/kernel/release.py；tests/unit/test_release_engineering.py | 登记已实现、有当前代码/测试；S1／S4a |
| INV-W3 [SPEC:1345](../../../spec/SPEC.md#L1345) | 同一源树两次构建 `release_id` 相同 | tools/build_release.py；ReleaseEngineeringTests.test_two_actual_builds_have_same_bytes_ids_and_fixed_zip_metadata | 已有独立构建对照，真实发行未完成；S4a 第1项 |
| INV-W4 [SPEC:1346](../../../spec/SPEC.md#L1346) | 封存清单里的 `release_id` 能在发布记录里找到（`dev-tree` 除外，它的封存包不是发行证据） | kernel/release.py；application/run_service.py:create；dev-tree 除外；真实发行身份加载另列关键缺口 | 已分配发布记录/安装验证，运行身份接缝仍缺承接；规格负责人 S4 交接、S4a-01 问题 |
| INV-X3 [SPEC:1347](../../../spec/SPEC.md#L1347) | 源码无 `pip/urllib/requests/http.client/socket`（测试工具白名单） | src/dna_design_core/application/config.py；tools/check_structure.py；tests/e2e/test_examples.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-X4 [SPEC:1348](../../../spec/SPEC.md#L1348) | 无 `shell=True` | src/dna_design_core/application/config.py；tools/check_structure.py；tests/e2e/test_examples.py；tests/structure/test_contract_tree.py | 登记已实现、有当前代码/测试；S0／S1 |
| INV-Q4 [SPEC:1349](../../../spec/SPEC.md#L1349) | `SKIPS.json` 无过期条目；SKIPPED 不计为通过 | tools/check_structure.py；tests/SKIPS.json；tests/structure/test_contract_tree.py；tests/unit/test_registered_primer3_skip.py | 登记已实现、有当前代码/测试；S0／S1b |
| INV-Q5 [SPEC:1350](../../../spec/SPEC.md#L1350) | 间歇失败有登记、负责人与期限；不因重复通过而关闭 | 没有当前项目的专门登记/检查。本次旧断言失败是稳定失败，不伪装成间歇失败。 | 未落实具体任务；S1 层＋人工，估计1小时 |
| INV-S1 [SPEC:1351](../../../spec/SPEC.md#L1351) | 正文里出现的每个事件类型都在附录 E；附录 E 的每个事件都有写入方 | ../../tools/spec_lint.py；tests/structure/test_schema_alignment.py | 登记已实现、有当前代码/测试；S0／S0 follow-up |
| INV-S2 [SPEC:1352](../../../spec/SPEC.md#L1352) | 正文里出现的每个命令动词都在 D13 的动词表 | ../../tools/spec_lint.py；tests/structure/test_schema_alignment.py | 登记已实现、有当前代码/测试；S0／S0 follow-up |
| INV-S3 [SPEC:1353](../../../spec/SPEC.md#L1353) | 正文里出现的每个 `模块.子模块` 路径都在 D15 的目录树 | ../../tools/spec_lint.py；tests/structure/test_runtime_contracts.py | 登记已实现、有当前代码/测试；S0／S0 follow-up |
| INV-S4 [SPEC:1354](../../../spec/SPEC.md#L1354) | 规则编号前缀唯一：`DEP` `GOL` `REV` `KIT` `SEAL` `RV` `TST` `DEV` `ADV` `INV` `MVP` | ../../tools/spec_lint.py；tests/structure/test_schema_alignment.py | 登记已实现、有当前代码/测试；S0／S0 follow-up |
| INV-S5 [SPEC:1355](../../../spec/SPEC.md#L1355) | 退役词（旧检查阶段名、评估器目录、交付类别、`PLAN/DOMAIN` 范围、`INCONCLUSIVE`、`mature` 等）不得被肯定地使用（只允许出现在「不采用」「取代」「没有」「旧」语境，或 `MERGE-LEDGER.md`） | ../../tools/spec_lint.py；tests/structure/test_schema_alignment.py | 登记已实现、有当前代码/测试；S0／S0 follow-up |
| INV-S6 [SPEC:1356](../../../spec/SPEC.md#L1356) | 正文里写的词表数量（检查时刻 3、结果 4、范围 4、能力角色 2）与 §1 一致 | ../../tools/spec_lint.py；tests/structure/test_schema_alignment.py | 登记已实现、有当前代码/测试；S0／S0 follow-up |

## 已验证 / 仅模拟 / 未做 / 不确定

- 已验证：119 条分区、各发出任务范围、指定源码/测试符号、发行检查实际输出、320 nt 合成原话探针；本次没有把旧 PENDING 理由直接当事实。
- 仅模拟：所有新动态探针为合成数据；工作量是估计，不是实测开发耗时。
- 未做：实现缺口、修改登记文件、改 Kit/规格/测试预期、安装、联网、用户 DNA 读取、人工签注、发布、独立宿主/读者测试。官方 GitLab CI 未执行；GitHub CI 未运行。
- 不确定：任务书“阶段/宽泛职责”是否被负责人视为足够具体的接手，原话长序列边界、旧名白名单与发布/科学表的人类决定。夜间按上述明确口径暂记，交白天负责人确认；本报告不代做决定。
