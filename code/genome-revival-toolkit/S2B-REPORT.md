Zeocin 新行已生效；BleoR 注释加声明酵母基因型，可返回完整平板说明。
原有规则未发现退步；缺基因型仍为未知（UNKNOWN），不给平板建议。
AI 已完成本地验证：439 项测试全部通过，覆盖原有功能及新增筛选行为。
来源仍为 unverified（尚未人工核验），需要团队核对手册原文。
官方 GitLab CI 未执行、GitHub CI 未运行。

已验证：本次完整测试配置了本机 Primer3，439 项全部通过、无跳过，意味着现有计算流程和新增筛选行为均符合测试预期。真实 Primer3 外部调用及程序指纹检查已执行。完整运行实测约 0.68 小时；这不是实验室抗性或功能验证。

新增 8 项测试覆盖名称识别、误配、宿主及已有标记冲突、来源字段，以及真实公共命令行。正例包括 `BleoR`、`Sh ble`、`ble marker` 和任务要求的其余别名；反例包括 `stable`、`table`、`cable`、`able`、`bleach`。期望平板文字来自任务给定原文，名称及输入由测试预先构造，没有从被测知识表生成期望值。

公共命令行实际运行 `describe checks`、`run create`、`goal declare`、`pipeline submit`、`run execute`、`judge`，经现有网络阻断测试入口启动，没有连接尝试。最终读取的是公共流程生成的 `selection.json`，不是直接调用筛选函数的结果。

| 合成输入 | 声明的基因型 | 实际软件结果 |
| --- | --- | --- |
| CDS 注释 `BleoR` | S. cerevisiae，已有标记为空 | 按声明兼容，返回与任务逐字一致的 Zeocin 平板说明，含浓度范围、kill curve、pH、山梨醇条件及原生质体禁直接铺板警告 |
| CDS 注释 `BleoR` | 未提供 | UNKNOWN；已识别 ble，但平板选项为空 |
| 没有标记注释 | S. cerevisiae，已有标记为空 | UNKNOWN，标记列表为空；与改动前结果一致 |
| CDS 注释 `LEU2` | S. cerevisiae，已有标记为空，声明 leu2 营养缺陷 | 仍推荐缺亮氨酸培养基；与改动前结果一致 |

前后两种无 ble 输入的筛选报告逐字段一致，只有知识包摘要改变；摘要随新增规则改变是预期行为。原有 10 行规则的全部字段保持不变，意味着此次只增加指定映射。知识表及生成的来源清单现在均含 11 条宿主映射。

主出处保存在新增行的 `source`；补充文献保存在 `parameters.supplementary_sources`，两份来源均具备规则格式要求的完整来源字段，日期为 2026-10-17，状态均为 unverified，没有人工核验回执或新审核文件。手册为 Thermo Fisher Scientific / Invitrogen Zeocin，25-0078，Version J，2002-08-22。Drocourt 等人的 1990 年文献只支持 Sh ble 的显性抗性标记用途，不作为浓度出处；未读取其全文。

结构和数据格式检查未发现问题。来源清单通过 `prepare_cut_plasmid.py --sources-only` 从现有数据重新生成。另在临时副本离线重跑旧迁移，确认重复运行仍保留原有规则和新增 ble 行；此次提交不改筛选算法、Core、规格或受保护文件。

已保留失败与人工变异证据：加行前，新公共命令行正例实际因 UNKNOWN 而失败；加行后通过。另在隔离副本中故意让 `stable` 匹配 ble、故意删去原生质体警告，两次都被相应测试判失败。这意味着测试能检出本任务要求防止的两类错误，未改写实际工作树数据。

模拟：输入是人工构造的 12 碱基环形序列，其中 `ATG AAA TAA` 仅构成语法完整的 CDS，再赋予标记名称；它不是功能性抗性基因。这里验证注释识别和条件判断。

没做：没有读取用户 DNA，没有联网下载或安装依赖；Python 环境从既有 s2-cut-plasmid 工作树复制。来源原文人工核验、真实抗性、生长、kill curve、转化及铺板实验均为 PLANNED / NOT_PERFORMED。官方 GitLab CI 未执行、GitHub CI 未运行。

不确定：任务给定来源与手册原文是否逐项一致，仍需人工核对。具体菌株的有效浓度、转化效率及原生质体融合实验中的直接使用，均不由本行或本地测试支持。

团队下一步：核对上述手册原文中的浓度范围、pH、山梨醇条件及原生质体警告，再由人工填写核验记录。AI 未代填核验回执。

复现位置为 `<SOURCE>`；分支 `s2b`，起点为任务指定的 `main` 提交 `1a82c68`。只提交本任务文件，不合并、不推送，沿用 `iGEM Tianjin 2026` 署名。

```powershell
Set-Location -LiteralPath '<SOURCE>'
$env:PYTHONPATH='src'
$env:GRT_PRIMER3_CORE='<WORK>\.primer3-artifacts\wheel\primer3\src\libprimer3\primer3_core.exe'
.\.venv\Scripts\python.exe -X utf8 -B tests\oracles\prepare_cut_plasmid.py --sources-only
.\.venv\Scripts\python.exe -X utf8 -B -m unittest tests.unit.test_cut_plasmid_selection tests.e2e.test_cut_plasmid_selection -v
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -v
```

旧写法传播检查：`MIGRATION-LOG.md`、`S2-REPORT.md`、`docs/kit-prep/cut-plasmid.md`、`tests/oracles/prepare_kit_drafts.py` 中的“10 条”描述原迁移或旧草稿，保留历史。原单元测试中的 10 仍专门检查原迁移行，新增规则另行检查；`S1E-REPORT.md` 的 10 行属于另一张规则表。当前 Kit README 和来源清单均已说明新增后为 11 条。

完整测试自动更新的三份其他阶段证据，已保存本轮副本并恢复版本库原文；本轮 B2 生成目录移至 `<WORK>\.s2b-evidence\full-suite-generated\b2-suite-0tqc5byb` 保留。它们不进入本次提交。

原始证据保存在本机：

- [完整测试输出](<WORK>/.s2b-evidence/full-suite.txt) 与 [执行环境及退出码](<WORK>/.s2b-evidence/full-suite-summary.json)。
- [BleoR 平板输出](<WORK>/.s2b-evidence/cli-final/ble-declared/selection.json)、[缺基因型输出](<WORK>/.s2b-evidence/cli-final/ble-missing/selection.json)、[实际 CLI 参数](<WORK>/.s2b-evidence/cli-final/ble-declared/commands.json)。CLI 证据为完整测试原运行 `<TEMP>\grt-s2b-cli-olgoees3` 的保留副本。
- [无 ble 行为前后比对](<WORK>/.s2b-evidence/baseline-comparison.json)。
- [加行前保留的失败输出](<WORK>/.s2b-evidence/baseline-orrejnkt/new-cli-before-row.txt)。
- [人工变异结果](<WORK>/.s2b-evidence/mutations-9khyu9c2/summary.json)，同目录保留被改错的副本和失败原始输出。
