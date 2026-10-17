# S0 阅读确认

审核方：iGEM Tianjin 2026 团队（团队声明，一次，不是个人各自声明）。

审核方式：团队读完后，由团队在对话里给出一次声明。只需读 §1「输出必须经过哪些检查」和
§2「四种结果和三个时刻」，声明“同意”或“有意见：……”。
其余各节是说明，不需要审。无需填写签名或日期。
Codex 不代填任何人的回复，也不宣布 S0 通过。

## 1. 输出必须经过哪些检查

这一项决定：给什么结果，就必须过哪些检查。权威数据是
[profiles.json](src/dna_design_core/resources/profiles.json)，对应 D7。

| 输出情形 | 必须追加的检查 | 举例 | 选错的后果 |
|---|---|---|---|
| 任何结果 | 回读、清单、日志链、存储哈希、输入未变、目标非空、目标角色匹配 | 一份纯观察分析也要证明交付文件与运行记录一致 | 空目标或文件不一致也可能交付 |
| 含材料 | 重放、来源链、注释完整性、CDS、基础生物学合理性 | DNA 被叫作 analysis 仍要查材料内容 | 改个标签就躲过内容检查 |
| construct | 反应链、引物质量、订单表 | 换间隔序列得到构建候选 | 有序列但没有可核查制备计划 |
| primer_set | 引物质量、订单表、反应链 | 一对 PCR 引物 | 只看单条序列，忽略它们能否产生预期产物 |
| component / analysis | 不额外加制备项；含材料仍执行材料项 | 证据不足报告的内容检查由能力 final_checks 追加 | 错把分析报告当实验成功，或无理由阻止合理报告 |

## 2. 四种结果和三个时刻

这一项决定：PASS / FAIL / UNKNOWN / NOT_APPLICABLE 的含义，以及 admission、
step、final 的分工。自检与宿主预期不能代替正式终检。见
[vocab.json](src/dna_design_core/resources/vocab.json)。

例子：外部程序缺失是 UNKNOWN，不是假装通过，也不是生物学上已失败。
NOT_APPLICABLE 必须有原因与事实依据。选错会把“未判断”说成“已经满足”。
领域结论词不加入公共词表；实验路线的 PLANNED / NOT_PERFORMED 不等于做过实验。

## 3. 错误后的下一步

这一项决定：程序不能继续时，应给什么英文 recovery 指引、是否可重试。
完整 26 条在 [errors.json](src/dna_design_core/resources/errors.json)。下表是该文件
说明性摘录，修改应回到数据文件，不把本表变成另一份来源。

例子：步骤已经失败，应新建步骤并取代旧步骤，保留原失败。恢复文案若建议覆盖
旧记录，会破坏历史；依赖缺失若提示自动安装，则越过当前离线边界。

| 错误码 | retryable | 英文 recovery 草案 |
|---|---|---|
| `PLAN_SCHEMA_INVALID` | false | Correct the request against pipeline-v1 and submit it again. |
| `PLAN_ID_INVALID` | false | Use a unique step identifier matching the documented pattern. |
| `PLAN_REF_UNRESOLVED` | false | Bind the reference to an earlier available step, source or artifact; specify an index when required. |
| `PLAN_CAPABILITY_UNKNOWN` | false | Use describe to select an available ACTION capability with a matching version. |
| `PLAN_INPUT_UNBOUND` | false | Provide each required input using the capability declaration. |
| `PLAN_PARAM_INVALID` | false | Correct the named parameter; provide sequences longer than the literal limit as files. |
| `PLAN_WHY_MISSING` | false | Provide a non-empty why value within the documented length limit. |
| `PLAN_OUTPUT_INVALID` | false | Correct the output binding; an empty output list is allowed for a diagnostic plan. |
| `PLAN_GOAL_BINDING_INVALID` | false | Bind the constraint to a target declared in the goal. |
| `PLAN_EXPECT_INVALID` | false | Use a supported expectation operator with compatible values and a valid output pointer. |
| `CAPABILITY_UNKNOWN` | true | Restore the recorded local capability; replace a failed step through a new pipeline revision. |
| `CAPABILITY_VERSION_MISMATCH` | false | Provide the recorded version or explicitly revise the plan; do not substitute silently. |
| `CAPABILITY_OUTPUT_INVALID` | false | Retain the failure and report the contract mismatch; do not deliver the invalid output. |
| `CAPABILITY_INTERNAL` | false | Retain the safe failure details and report the implementation error. |
| `SOURCE_CHANGED` | false | Restore the registered input or explicitly declare a new input; do not overwrite the original history. |
| `STEP_EXPECTATION_FAILED` | false | Inspect the retained result, then add a replacement step in a justified revision. |
| `STEP_INTERRUPTED` | true | Retain the interrupted step and add a replacement step before continuing. |
| `JOURNAL_CHAIN_BROKEN` | false | Stop execution; inspect the existing journal read-only and preserve the damaged copy. |
| `RUN_LOCKED` | true | Wait for the owning process to finish, then retry the command; do not remove its active lock. |
| `STORE_CORRUPT` | false | Stop consuming the object and recover the original content from an intact copy. |
| `CHECK_UNAVAILABLE` | true | Restore the local check dependency and repeat judgement; keep the result UNKNOWN until checked. |
| `KIT_MANIFEST_INVALID` | false | Correct the reported manifest field; keep unrelated Kits available. |
| `KIT_CORE_INCOMPATIBLE` | false | Use a compatible local Kit or Core version. |
| `KIT_NAME_CONFLICT` | false | Remove or rename the conflicting external contribution; do not select a winner by load order. |
| `KNOWLEDGE_SOURCE_INVALID` | false | Provide the missing source, scope and limits; do not invent a citation or human verification receipt. |
| `SEAL_RUN_NOT_COMPLETED` | false | Complete or revise the pending work and bind the required targets before sealing. |

## 4. 模式位置与起草信息（说明）

SPEC 8ad9c44 的 A2/A9 已列入 CHECK.offline、document 输入 schema_ref 和
authorship，并新增必填 granularity（atomic|composite）。authorship 在能力、
规则、模板中均可选；提供时仍须包含 kind、tool_or_model、date。

起草来源不是质量保证，也不代替人审。原有字段差异已消除，见
[SCHEMA-DIFFERENCES.json](SCHEMA-DIFFERENCES.json)。

## 5. 目标、计划和交付不能偷换

这一项决定：目标保留用户原话、来源与目标角色；计划只选做事的能力，不能自带
gates/checks，也不能自行标输出角色。局部计划可暂不覆盖全部目标，封存仍要满足
所有必需目标。参见 goal、pipeline、revision、manifest 模式。

例子：先诊断一个失败步骤可以不交付最终构建；不能因诊断成功就把原目标改成
“检查过就算完成”。选错会让程序通过一个缩小后的目标。

## 6. 来源、观察、审核是不同证据

这一项决定：用户文件、研究者观察、规则来源及核验回执怎样记录。规则缺来源
不能加载；核验回执由人填写。review 缺姓名或日期只能视作 draft，即使语法合法。

例子：研究者报告 9 个菌落，程序能核对数值和比较，不能证明实验发生过。
选错会把人的陈述升级为程序验证的实验。合法样例里的 review 姓名、日期均为空，
不是真正的审核记录，没有任何文件写进 review/ 目录。

## 7. 继承发现（说明）

用户已同意首版只认两种确定情形：逐位原样复制、圆形旋转；
其他一律 UNDETERMINED→FAIL。

仍须证明唯一来源、唯一发现对应，以及相关序列与有效注释未被本次操作改动。
复制或旋转的名称本身不是证明。此范围只用于两项指定检查，见
[QUESTIONS Q03](QUESTIONS.md)。本次没有实现继承匹配算法。

## 8. 是否枚举 guide（说明）

用户已决定：首版只检查与替换用户已选定的 guide，不枚举。
已有 PAM 扫描小样不扩大首版范围，也不证明编辑活性或全基因组脱靶安全。

## 9. 内部结构（说明）

现以 [SPEC.md](../../spec/SPEC.md) 附录 A14（12c4274 修正版）为准。
goal.amended.diff 使用 JSON Patch；input.registered.declared_by 使用 actor；
pipeline.revised 不增加 diff。当前没有仍未定义的内部字段，x-s0-gap 剩余 0。

JSON Patch 实际应用、模板实例化、能力执行及交付判定尚未实现。这些是后续
运行时工作，不是字段缺口，见 [SCHEMA-GAPS.md](SCHEMA-GAPS.md)。

## 10. 探针证据（说明）

初次 S0 的 200 次真实进程强杀无链失败，未自然产生撕裂尾部；三个构造损坏
对照通过。Windows 读句柄会阻挡重命名，关闭后重试成功。本次没有重跑 P1/P2。

按用户提供的补测结果记录：rfc8785==0.1.4 由 Claude 在隔离虚拟环境里安装
（用户授权，仅供探针），原样运行 p3_jcs.py：Windows 上 3 个向量
（UTF-16 键序、RFC 数字、控制字符）通过；Linux 未测；Codex 未复现该运行。
详见 [probes/RESULTS.md](probes/RESULTS.md)。

## 11. 发行许可（说明）

iGEM 要求 OSI 批准许可，官方默认推荐 Apache-2.0，MIT 亦可；
用户已确认选用 Apache-2.0（2026-10-16）。LICENSE 文件已写入标准 Apache-2.0 文本
（来自本机多个已安装包中内容一致的副本，11358 字节；未联网）。依据为 SPEC D16 与用户的确认。

外部工具许可和本地验证边界见 [FACTS.md](FACTS.md)。

## S0 状态

**团队声明（2026-10-16，记录者：Claude）**：iGEM Tianjin 2026 团队在对话中声明同意 §1、§2。
用户原话：「团队声明同意」。这是对用户原话的如实记录，不是 AI 作出的审核。
团队依据的是对话中给出的 §1、§2 大白话摘要，不是逐字阅读本文件；程序与 AI 无法验证团队内部共识。

运行时尚为空，32 条不变量覆盖静态检查，87 条待实现。
官方 GitLab CI 未执行。
