# S1b 生物层批 1 至 4

批 1 至 4 的纯计算层已实现，能力接入未完成，S1b 门保持未关闭。
新增 32 个公开函数及 TmParameters；每个公开符号均登记独立答案。
最大阻塞：S1 的材料、能力、裁决、哈希与外部调用接口仍为空。
基线规格与模式存在 1 个硬问题；受保护文件保持原状。
后续由 S1 提供接口、规格负责人解决 Q2/Q4，再完成能力契约与门复核。

## 结构类

| 项目 | 事实与处理 |
|---|---|
| S1B-Q1 | kernel/material.py、public.py、ports.py、ids.py、verdict.py 均为 0 字节。按共同规则第 4 节停在该结构接口；材料构造、能力薄壳、装饰器导出的 capability-v1 JSON、CHECK 裁决及 ctx.run_external 接入均未实现。没有另建运行时、材料模型或能力注册表。证据：tests/evidence/s1b/dependency-seam.json。 |
| S1B-Q2 | D9 的 material_id/sequence_id 依赖选定起点的序列与坐标，S1b 验收又要求旋转不改变内容身份。已测逆旋转、环状 k-mer 多重集、特征提取序列；未把它们当作材料身份测试，未增加新哈希。 |
| S1B-Q3 | 环境已有 sgffp 0.21.0，但依赖白名单不含它。先登记 FACTS/QUESTIONS，保持不用；.dna 用白名单内 Biopython 1.88 的内存读取器。完整原生块、物理末端与原生引物全部元数据不在保真承诺内。 |
| S1B-Q4 | 基线 spec_lint 硬问题：A14 run.created-payload-v1:git_commit missing_from_schema。规格补丁 e621b5c 与模式未同步。未修改规格或受保护模式。 |

能力契约测试数量为 0，CHECK 能力运行数量为 0，材料与运行时集成为 NOT_PERFORMED。
纯函数契约与阈值筛选示例不计作上述能力验收。

## 实际运行了什么

完整命令、计数、退出码、失败名见 tests/evidence/s1b/validation.json。
结构优先运行。由于结构未绿，后续结果仅作为开发证据，不作为阶段通过。

| 范围 | 结果 |
|---|---|
| tools/check_structure.py | 0 个发现。扫描范围为当前代码、Kit 骨架、夹具与保护规则。 |
| tools/check_schemas.py | 35 个模式、212 个模式夹具，0 个发现。 |
| tests/structure | 53 项中 51 通过、2 失败、0 跳过。失败为 test_spec_baseline 与 test_baseline_matches_updated_appendix，均来自 Q4。 |
| 新增纯函数契约 | 5 项通过：公开签名、独立答案登记、运行期无文件/进程、7 组保存的独立 CLI Tm、实际 Boulder 输出解析。 |
| 新增单元测试 | 39 项通过。手工/构造答案；另有 200 组固定种子序列属性、100 组预先构造答案的重叠组装。 |
| 生物算法源码变异 | 4 个实际变异在临时副本运行，4 个被断言捕获：PCR 吞掉多产物、突出端改为标签相等、Tm 删除盐修正、特征起点偏移 1。原始输出见 tests/evidence/s1b/mutations。 |
| spec_lint | 1 个硬问题、17 个软提示，硬问题为 Q4。 |
| Primer3 独立命令行 | 7 组合成输入实际运行；另对不存在的路径运行开发者参考脚本，得到 UNKNOWN 与配置指引。后者不是产品能力缺依赖集成测试。 |

保留失败：tests/evidence/s1b/development-run-01 包含首轮完整回归的 4 个失败，
其中新增 2 个来自夹具登记缺少 oracle.kind 外层，已按既有格式修正。
development-history.json 还保留了首轮错误构造的环状夹具，以及真实 Primer3
多行结构图触发的解析错误。测试预期没有改成待测输出。

已验证：上表限定范围的程序运行、独立数值对照和变异捕获。
模拟：PCR、酶切、连接、Gibson 及反向 PCR 环化，均只有序列层计算。
未做：材料/能力运行时集成、通过 Invoker 的 CHECK、封存复验、湿实验、Linux。
不确定：旋转的材料身份规则；完整原生格式保真度；任何实验效率与功能。
官方 GitLab CI 未执行；GitHub CI 未运行。

## Primer3 数值与质量对照

实际程序：libprimer3 release 2.6.1。
可执行文件 SHA-256：19a546a0166fd979c41317e45696de1b383ab5fa21ec362bcc5053b2068b6e5f。
程序保留在仓库外。7 组请求、stdout、stderr、热力学参数文件哈希见
tests/evidence/s1b/primer3；原始参考脚本不 import dna_design_core。

共同参数：Na 50 mM，total oligo 50 nM；常规 Mg 0 mM、dNTP 0 mM；
Mg 对照为 Mg 2 mM、dNTP 0.5 mM。
本地 Tm 明确用 DNA_NN3、盐修正 5，输出包含参数。
Primer3 用 TM_FORMULA=1、SALT_CORRECTIONS=1。
非自互补使用 total/4 有效浓度；自互补使用 total 并加对称熵项。

| 输入 | 本地 Tm / °C | Primer3 / °C | 差 / °C |
|---|---:|---:|---:|
| 手工 8 nt | 11.74530033 | 11.745 | 0.00030033 |
| 自互补 8 nt | 14.39497559 | 14.395 | -0.00002441 |
| 常规 20 nt | 52.73139724 | 52.731 | 0.00039724 |
| Mg 条件 20 nt | 59.32596224 | 59.326 | -0.00003776 |
| 发夹样例 20 nt | 53.20758949 | 53.208 | -0.00041051 |
| 连续 T 样例 20 nt | 45.48458651 | 45.485 | -0.00041349 |
| 引物对左引物 20 nt | 52.73139724 | 52.731 | 0.00039724 |

最大绝对差 0.00041349 °C。Primer3 只打印三位小数，测试容差由该精度
确定为 0.00050001 °C。独立手算同时保留：ACGTACGA 的 NN 堆叠和
为 -61.8 kcal/mol、-165.1 cal/(K mol)，两端 AT 修正后为 -57.2、-156.9；
再加入盐熵项和浓度项。AT 双核苷酸另核算对称熵；Mg 另核算钠当量。

质量对照保留完整原始值，见 primer3-comparison.json。
本地指标单位为连续互补 bp，Primer3 的 SELF_ANY_TH、SELF_END_TH、
HAIRPIN_TH、COMPL_ANY_TH、COMPL_END_TH 单位为 °C，不能相减当误差。
例如普通 20 nt 的最长精确发夹茎为 4 bp，对应 Primer3 发夹 Tm 39.63 °C；
另一例最长精确茎 3 bp，Primer3 发夹 Tm 46.38 °C。
原因是热力学模型还使用环、错配、凸起、堆叠及离子参数；茎长不替代热力学 QC。
本地质量阈值由调用方显式传入，未移植无来源的默认科学阈值。

## 实现类

| 批次 | 实现与明确边界 |
|---|---|
| 1 格式 | GenBank 文本读写；以序列、拓扑、特征位置和限定词为回读等价范围。FASTA 只保留头与序列，对含特征/拓扑的输入拒绝静默丢失。.dna 只读合成二进制包；不写原生格式。 |
| 2 序列 | 严格整数、0 起半开区间、环状跨起点、切片与特征变换、负链、旋转。截断 CDS 移除旧 translation 并重算 codon_start；截断/线性化拆开的引物标记为不完整。模糊/远程坐标变换明确拒绝。未实现材料构造。 |
| 3 引物/PCR | 参数完整的 NN Tm；完整寡核苷酸 GC、连续 T、二聚体、发夹指标；显式 3′ core/5′ tail；正负链与跨起点结合搜索；列出全部产物，唯一产物接口拒绝歧义；PCR 特征映射。Primer3 只有纯 Boulder 编解码和完整 2 至 36 nt 寡核苷酸检查请求；进程后端未接入。 |
| 4 酶切/组装 | 数据库酶定义、双方向/IUPAC 位点、双链切点、5′/3′/平端与真实突出端、双酶切。连接核对双链实际序列，未知末端拒绝连接。Gibson 使用显式顺序和重叠长度；反向 PCR 环化保留线性中间体。相互穿插切点、无双链核心片段明确拒绝。 |

biology/public.py 导出 32 个函数和 TmParameters；SeqRecord 只承载格式与注释，
酶切/PCR 字典只是计算数据，均无材料身份或存储契约。
逐函数旧路径、旧/新行数、依赖耦合与重写部分见 MIGRATION-LOG.md。
生产直接依赖仅标准库及允许列表；锁文件记录本环境 jsonschema 4.26.0、
rfc8785 0.1.4、Biopython 1.88。没有安装包、联网、合并或推送。

复现纯算法测试，在本目录 PowerShell 运行：

```powershell
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'src').Path
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests/unit -p 'test_biology*.py' -v
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests/contract -p 'test_biology*.py' -v
.\.venv\Scripts\python.exe -X utf8 -B tests/oracles/biology_mutations.py
```

复现完整结构与开发证据：

```powershell
.\.venv\Scripts\python.exe -X utf8 -B tools/validate_biology.py
```

验证脚本因整体 UNKNOWN 返回 1；它不会关闭 S1b 门。

本地算法与证据提交：b2c7b2b。分支 s1b-biology，未合并、未推送、未打关闭标签。
工作树另有本次检查生成的未跟踪 tools/__pycache__/。删除命令被自动执行策略
拒绝，返回 blocked by policy；缓存未纳入提交。Primer3 原始 stdout 的 4 行
结构图以制表符结尾，按原样保留，其余暂存内容的 git diff --check 无发现。
