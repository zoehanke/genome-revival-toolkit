# S0 收尾检查点

模式已按 8ad9c44 与 12c4274 对齐；spec_lint 0 个硬问题。
模式差异 0，x-s0-gap 0；S0 尚未宣布通过。
剩余：审核人回复 §1/§2、产品许可确认；Linux JCS 未测，运行时未实现。

## 本次改动

* capability-v1 新增必填 granularity；三类声明的 authorship 按 A2/A9 可选。
* 按 A14 收紧运行依赖、错误因果条目、档位摘要、回执范围、包版本、actor、
  JSON Patch、产物 id 数组、来源引用、未满足项、模板占位符；D9 首事件 prev 固定 64 个 0。
* 12c4274 修正了两处位置：goal.amended.diff 使用 RFC 6902；
  input.registered.declared_by 使用 actor。pipeline.revised 没有新增 diff。
* 字段扫描直接读取 A2/A9/A14，移除旧的正文授权差异例外，补入内部字段变异测试。
* REVIEW-SHEET 改为只读 §1、§2 后在对话回复，其余各节仅说明。没有代填回复。

代码与测试提交：0129bfe。文档收尾单独提交。作者使用仓库配置的 iGEM Tianjin 2026。
仅 code/ 与 tools/ 有改动；没有改 spec，没有推送或合并。

## 实际执行

| 公共命令 / 检查 | 本次结果 |
|---|---|
| check_schemas | 35 份模式，212 个样例全部按预期判定：68 合法、144 非法，偏差 0 |
| check_structure | findings 0 |
| unittest discover -s tests | 53 通过、0 失败、0 跳过，92.537 秒 |
| unittest discover -s spikes | 8 通过、0 失败、0 跳过 |
| spec_lint + fields-report | 硬问题 0；软提示 17（既有退役词语境）；模式字段差异 0 |
| x-s0-gap | 模式中剩余 0 |
| 不变量清单 | 实际定义 119；32 条静态覆盖，87 条待实现（含新 INV-F10） |

新增 28 组形状样例，共 91 个，每组至少 1 个合法和 2 个非法样例；来源为手写
或构造，不读取模式生成答案。索引为 tests/contract/a14-coverage.json。
修复前同一批样例记录了 60 处预期偏差，修复后为 0。记录保存在被忽略的
probes/runs/s0-followup/before-schema-check.json，失败类型保留在测试夹具中。

原 no_authorship 反例改为合法样例，因为新 A2/A9 明确可选；literal.ref 改为
null，manifest.profile 与 goal.diff 改为 A14 规定形状。依据是规格，不是实现输出。
字段扫描器新增测试也暴露了旧解析器不读 A14 内层、A8/A9 同行标题的缺口，均已修正。

## 证据归属

| 已验证 | 仅模拟 | 未做 | 不确定 |
|---|---|---|---|
| 本次公共检查命令、模式样例判定、字段变异测试、8 项旧移植小样回归 | 合成形状与 PAM/Tm 输入；没有实验数据 | Codex 未复现 P3；Linux 未测；JSON Patch/模板实际执行、运行时与 Kit 未实现；无 CI | 人工审核结果、产品许可最终选择、后续跨平台表现 |

P3 按用户提供的补测结果记录：rfc8785==0.1.4 由 Claude 在隔离虚拟环境里安装
（用户授权，仅供探针），原样运行 p3_jcs.py：Windows 上 3 个向量
（UTF-16 键序、RFC 数字、控制字符）通过；Linux 未测；Codex 未复现该运行。
这不是 Codex 的执行记录。本次没有下载安装依赖，也未覆盖原有 P3 原始记录。

初次 S0 的 P1/P2 结果保留在 probes/RESULTS.md，本次未重跑。
旧已知小样回归 8 项与本次独立构造模式样例分开计数；未做 heldout 评测，
没有真人实验或人工修正后冒充独立成功的结果。移植小样不是完整旧版验收。

## 交接

iGEM Tianjin 2026 团队只需读 [REVIEW-SHEET.md](REVIEW-SHEET.md) 的 §1、§2，
在对话里给出一次团队声明：“同意”或“有意见：……”。本文件没有替任何人作答。
继承发现范围与不枚举 guide 已按用户决定记录，不再当作开放选择。
LICENSE 原文件保持待定；Apache-2.0 只是规格负责人的暂定选择，待用户确认。

模式缺口及运行时边界：[SCHEMA-GAPS.md](SCHEMA-GAPS.md)；
字段差异：[SCHEMA-DIFFERENCES.json](SCHEMA-DIFFERENCES.json)；
问题处置：[QUESTIONS.md](QUESTIONS.md)；探针归属：[probes/RESULTS.md](probes/RESULTS.md)。

复现命令，从 code/genome-revival-toolkit 运行：

```text
python -X utf8 -B tools/check_schemas.py
python -X utf8 -B tools/check_structure.py
python -X utf8 -B -m unittest discover -s tests
python -X utf8 -B -m unittest discover -s spikes
```

从仓库根运行：

```text
python -X utf8 -B tools/spec_lint.py spec/SPEC.md --fields-report code/genome-revival-toolkit/SCHEMA-DIFFERENCES.json
```

GitHub CI 未运行。本任务不推送。官方 GitLab CI 未执行。S0 尚未关闭。
