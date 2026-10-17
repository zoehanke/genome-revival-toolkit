S3b 已完成：平板计数的局部支持结论按五行表生效，六组新增公共命令案例均完成封存和复制后复验。
整体“功能复活”和“整个基因组消除”仍只报告证据不足或未检测，原有状态规则未改。
本地完整 443 项测试通过，意味着本轮覆盖的结构、字段契约、规则计算、公共流程和离线复验符合构造预期。
新规则来自用户 2026-10-17 的决定，来源仍未人工核验（unverified），需要团队声明；未填写核验或审核回执。
AI 已完成实现、测试及报告；队员需声明这条规则的项目约定来源。本分支不合并、不推送。

## 已验证

代码位于 `s3b` 工作树，基线为 `8bc664c493c6c25fee1d90977316e79a06d9cd99`。
本次只修改 Revival Evidence Kit、该 Kit 的测试、独立校核和文档。

新增 `fusion_plate_outgrowth`，含义仅为“指定融合组报告有菌落，而指定无生长对照报告为零”。
比较对象直接使用 `comparisons` 的 `experiment_group` 与 `control_group`，不从组名推断。
省略评估动作的 `comparisons` 参数时，不产生该结论，也不报错。
模板仍接收显式数组；省略参数的公共命令案例实际删除执行步骤中的该字段。

计数是否已知、是否为正，共用原无生长对照规则的事实提取。
新主张使用原真值表引擎，支持条目的展示并入原一致性检查摘要。
结论对象复用已有比较组字段记录范围；没有另建判断引擎或渲染器。
分组包含多条记录时，沿用原总计逻辑，任一计数缺失就保留该组总计为缺失。

两条整体结论的状态表保持原样。它们的理由从实际结论列表计算已支持的局部主张，
并说明基因型确认、供体依赖的功能或遗传学验证、全基因组消除仍未成立。
没有局部支持时，明确写 `No scoped conclusion is supported.`。
专门测试改名局部主张，确认整体理由跟随实际列表，未写死新结论名称。

已支持的局部结论在 `assessment.json` 排前。
HTML 运行卡片和 Markdown 报告的原检查摘要逐条列出主张、对象及范围理由，
随后保留原 `Does not support` 内容。已验证生成文件的内容和顺序；未做浏览器截图审查。

### 完整本地测试

Windows、Python 3.12.4。`.venv` 从现有 S3 工作树复制，没有下载或安装依赖。
已配置本机 Primer3，其真实调用与运行指纹检查实际执行。
完整测试最后执行一次，实测北京时间 2026-10-17 19:29 至 20:09，约 0.66 小时。

| 范围 | 执行并通过 | 失败 / 错误 / 跳过 | 检查含义 |
|---|---:|---|---|
| 结构 | 65 | 0 / 0 / 0 | 模块边界、声明、来源与模式对齐 |
| 契约 | 15 | 0 / 0 / 0 | 能力声明与输入输出字段一致 |
| 单元 | 244 | 0 / 0 / 0 | 构造计算、规则、缺失值与人工变异 |
| 集成 | 104 | 0 / 0 / 0 | 真实调用器、公共入口、检查及拒绝行为 |
| 端到端测试 | 15 | 0 / 0 / 0 | 完整公共流程与交付包复验 |
| 合计 | 443 | 0 / 0 / 0 | 上述本地执行范围均符合测试期望 |

[完整结果](dist/s3b-full-01/results.json)、[原始日志](dist/s3b-full-01/all-tests.log)。
专项检查已包含在总数内，不重复相加；子情形也不额外计作测试项。

原有五组案例重新通过公共命令执行、封存、复制后复验和独立校核。
原 11 个局部 PCR 构造由专门单元测试逐项回归，并保留既有 PCR 集成检查。
“最完美输入”包含融合 9、对照 0、预测与报告均为 80 bp、检测对照通过、功能结果阳性：
局部平板、局部 PCR 比较和对照无生长可被支持，两条整体结论仍均为 `INSUFFICIENT`。

人工变异实际把“对照也有菌落”那一行改为 `SUPPORTED`，评估确实运行出错误支持状态。
固定的 `INSUFFICIENT` 期望抓住该错误；独立校核即使读取同一份变异规则文件，也拒绝错误报告。
这意味着测试不靠变异后的规则状态生成新结论的期望值。

独立脚本只使用标准库，从原观察重新计算分组计数；新增主张的期望状态直接来自用户的五行构造。
公共案例另外传入原提交的比较组配置，并逐项校核结论状态、范围对象和整体理由。

静态扫描无发现；35 份模式及 242 份样例的模式检查无发现；生成文档检查无差异。
这说明当前结构和字段声明一致，不代表生物学结果成立。
[静态扫描](dist/s3b-preflight-01/structure.json)、[模式检查](dist/s3b-preflight-01/schemas.json)、
[文档检查](dist/s3b-preflight-01/docgen.json)。

完整测试改写的三份旧历史回执已按原字节恢复，新生成版本保存在
[generated-evidence](dist/s3b-full-01/generated-evidence/)。
其他测试生成的 188 份新文件移入
[generated-new-evidence](dist/s3b-full-01/generated-new-evidence/)，意味着保留本轮记录，且不提交其他任务的产物。
[移动清单](dist/s3b-full-01/new-evidence-moves.json)保留原路径。
这些 `dist` 产物未加入 Git；实现、测试和本报告可在分支中审查及重跑。

## 模拟

以下全部是合成报告计数，不是真实实验观察。
五行状态期望在执行前由任务表固定。

| 融合计数 | 对照计数 | 公共命令实际状态 | 含义 |
|---|---|---|---|
| 缺失 | 0 | `NOT_TESTED` | 缺失保留为缺失 |
| 0 | 31 | `CONTRADICTED` | 报告没有融合菌落 |
| 9 | 缺失 | `INSUFFICIENT` | 对照未报告，无法比较 |
| 9 | 31 | `INSUFFICIENT` | 对照也有菌落；另报告对照无生长主张矛盾 |
| 9 | 0 | `SUPPORTED` | 仅支持这两个指定组的报告计数差别 |
| 9 | 0，省略比较参数 | 不产生新结论 | 参数缺省不报错 |

单元层另覆盖缺失、零、正计数的九种组合，验证前两行的“任意对照”条件。
合计 11 组公共案例含原五组和上述六组，共 99 次命令调用，意味着每组都完成
创建、目标、模板、提交、执行、判定、封存、复验和仅复制封存目录后的复验。
42 条结论与独立脚本一致；每份复制包均实际重跑九项离线检查，未跳过复验。
这 99 次受网络拦截器保护的命令，连接尝试为零。

[公共命令汇总](dist/s3b-full-01/cli/SUMMARY.json)、
[逐次回执](dist/s3b-full-01/cli/receipts.json)、
[独立校核回执](dist/s3b-full-01/cli/oracle-receipts.json)。
融合 9、对照 0 的当前结果来自汇总绑定的封存目录：
[封存清单](dist/s3b-full-01/cli/fusion_supported/portable/63f9aab1c4c6a0e914c9315af711079222962f3f3646a156dd859b9cf1ed9dbb/manifest.json)、
[评估报告](dist/s3b-full-01/cli/fusion_supported/portable/63f9aab1c4c6a0e914c9315af711079222962f3f3646a156dd859b9cf1ed9dbb/assessment.json)、
[运行卡片](dist/s3b-full-01/cli/fusion_supported/portable/63f9aab1c4c6a0e914c9315af711079222962f3f3646a156dd859b9cf1ed9dbb/views/runcard.html)。

## 没做

未做湿实验、PCR、遗传学或功能验证，实验室步骤均为 `PLANNED / NOT_PERFORMED`。
未认证观察真实性、供体来源、对照细胞死亡或整个基因组消除。
官方 GitLab CI 未执行；GitHub CI 未运行。
未改规格、受保护文件、其他 Kit；不合并、不推送，不声明阶段关闭。

## 不确定与队员待办

这条规则来自用户 2026-10-17 的方案 B 决定，来源类别为项目约定（`project_contract`）。
`verification_status` 仍是 `unverified`，表示来源尚未人工核验；没有人工审核回执。
来源明确写入规则及每行的来源引用，不能替代来源核验或证明报告真实。
队员需声明该判读边界属于本项目采用的约定，并给出对应决定文件的位置；
AI 未替队员作来源核验或审核声明，不要求为此新增实验。

[新规则及来源](kits/revival-evidence/knowledge/fusion_plate_outgrowth.json)、
[来源汇总](kits/revival-evidence/knowledge/SOURCES.md)。
全文搜索旧“四份规则”写法，仅在历史 `S3-REPORT.md:85` 保留当时统计；当前 Kit 声明为五份规则。

## 复现

从本工作树的 `code/genome-revival-toolkit` 执行，输出目录需选新名称：

```powershell
$env:PYTHONPATH='src'
$env:GRT_PRIMER3_CORE='<WORK>\.primer3-artifacts\wheel\primer3\src\libprimer3\primer3_core.exe'
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 -B tests\e2e\run_revival_evidence.py --scoped --out dist\s3b-reproduce
```

完整测试中已执行公共案例，无需另跑第二条才算完成本轮验收；第二条用于单独复现命令链。
