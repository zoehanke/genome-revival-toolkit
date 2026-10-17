# C2：六类目标约束检查

六类检查均已实现，S1 已合并，本轮六项待做清单为空。
程序能检查指定 DNA 内容和报告是否满足要求；这不表示实验成功。
完整 DNA 封存仍缺其他既定科学检查，由对应 AI 任务继续实现。
本轮不需要用户操作；门仍由规格负责人复核。

## 本轮实现了什么

CHECK 是只读检查能力。六项均声明可作目标约束（evaluates_constraint=true），
只读封存内容即可重跑（offline=true），归属用户目标范围（scope=user_goal）。
参数模式规定哪些参数必填及合法取值；每项均提供模式、独立构造答案和通过/失败样例。

| 检查 | 检查内容 | 明确边界 |
|---|---|---|
| topology | 指定目标材料是线性还是环状 | 未知形态不推断，不从文件名/来源声明猜 |
| exact_sequence | 完整序列与指定序列相同 | 起点与方向固定；不自动认作旋转或反向互补等价 |
| components_present | 必须有的片段是否实际存在 | 按序列和显式方向判断，支持已知环状边界；注释标签不能代替 |
| components_absent | 必须去除的片段是否仍存在 | 未知拓扑或歧义碱基可能妨碍证明不存在，此时不通过冒充确定答案 |
| regions_unchanged | 指定参考材料与目标材料的指定区段相同 | 两侧坐标明确；只证明所选参考的这些序列，不判断注释继承 |
| claim_reported | 报告确实写出所需主题及非空结论状态 | “证据不足”也算报告状态；不证明报告结论为真 |

完整参数和例子见 [docs/goal-constraints.md](docs/goal-constraints.md)。实现位于
capabilities/builtin/check/goal.py；六份声明 JSON 由现有装饰器导出工具生成。
目录现在能发现 D2 的全部七种目标检查，包含 S1 已有的 output_present。

## 合并与结构边界

按用户要求合并 s1-minimal-slice，合并提交 e47e17e，包含负责人关闭 S1 的
s1-closed 标签 acc5aed。四处冲突保留两边的意图：S1 的反向互补函数、S1b 既有
生物函数、统一公开导出、全部声明导出和 README 中的两组复现命令。
合并后先运行结构扫描、S1 反向互补手算测试及五项 S1b 纯层契约测试，通过。
工作中出现的共享 AGENTS.md 提交 4cdb59f 已读取并保留。

C2 没有再改 S1 独占层、规格、受保护模式、版本、词表或 Kit。已有只读测试改为读取
各 CHECK 正例的合法参数，继续检查全部 CHECK。依赖检查保留原核心锁定，仅在 biology
目录允许既有 Biopython 锁定的 Bio 导入。没有放宽核心依赖或安装任何包。
生成的能力文档与 Skill 能力目录同步，原工作流正文保留。

## 实际运行范围与结果

所有命令在 code/genome-revival-toolkit 执行，均设置 PYTHONPATH=src。
[README](README.md) 给出按顺序复现的命令；[validation.json](tests/evidence/s1b-c2/validation.json)
记录命令、运行范围和计数。先前两轮证据保持原路径。

| 实际执行范围 | 结果及含义 |
|---|---|
| 合并后的全量发现测试 | 200 项，199 通过、1 登记未执行，0 失败/错误；覆盖结构、声明、材料与算法、运行/裁决/封存及原有公共命令链 |
| 本轮新增公共 API 测试 | 1 项单独运行通过；在上述全量发现启动后加入，单独计数，不冒充一次 201 项全量日志 |
| 缺配置时未执行的 Primer3 项 | 配置实际程序后单独运行，1 项通过；是全量 200 中同一项，不新增独立测试数 |
| 六项参数/声明/边界测试 | 包含在全量中的 9 个测试方法内，验证参数拒绝、未知结果、目标绑定和真实 Judge 裁决 |
| CHECK 正反夹具 | 实际运行 12 个构造场景，6 个 PASS、6 个 FAIL 均符合独立答案；CHECK 前后运行文件字节一致 |
| 六处源码变异 | 六项各改错一处，6/6 被断言捕获，说明测试能识别这些具体错误 |
| 结构扫描 | findings=[] |
| 模式扫描 | 35 个模式、227 个模式夹具，findings=[] |
| 生成文档一致性 | different=[] |
| 规格扫描 | HARD findings: 0；SOFT findings: 17 |

全量输出原文末尾：

```text
Ran 200 tests in 370.374s

OK (skipped=1)
```

缺配置的外部数值核验仍是“未执行”，从通过数扣除。配置实际 Primer3 后的单独日志在
configured_primer3.txt，显示 1 项、0 跳过。当前共覆盖 201 个不同测试方法：200 项全量
加后补的 1 项公共 API 测试；不能把重跑的 Primer3 项再加进独立数量。

公共 API 是供外部程序调用的正式入口。本轮从该入口创建运行、声明六个约束、执行
CCC→AT 的区间编辑和一份序列报告，再判定。五项 DNA 要求通过；报告缺少所需结论状态，
claim_reported 给 FAIL。这是预设失败例，说明程序不会把一份只有序列的报告当成功能结论。
其余三个未实现的科学检查仍出现在不满足清单中，完整 DNA 交付没有因此获得通过。
实际答案见 [public-api.json](tests/evidence/s1b-c2/public-api.json)。

正反裁决与独立答案见 [check-fixtures.json](tests/evidence/s1b-c2/check-fixtures.json)。
变异的实际失败日志与六项计数见 [mutations/results.json](tests/evidence/s1b-c2/mutations/results.json)。
最初新增 Judge 测试夹具漏掉文件清单，导致测试报错；补上真实绑定文件路径与字节哈希后
定向重跑通过，再运行上述全量。开发错误摘要保留在 development-history.json，未改科学答案。

## 待做归属

- C2 六项核心检查：AI 已完成，无剩余项。
- S1 的 AI：继续处理请求来源标记、提交目标时提前校验参数，以及 output_present 的 fields 参数，后者指定输出必须含哪些字段。
- 对应后续 AI 任务：实现仍缺的注释、CDS 和生物合理性检查，再评估完整 DNA 交付。
- 规格负责人：复核本轮证据与参数契约，决定是否接受；本报告不关闭新门。
- 用户或队员：本轮无需操作。

**已验证**：上述限定范围内的程序行为、12 个构造正反例、6 个源码变异、真实裁决记录、
公共 API 的失败识别，以及配置了实际 Primer3 的外部调用。

**模拟**：合成 DNA 的区间编辑、序列匹配和字面报告；没有实验样本。

**未做**：真实 Kit、完整科学交付封存、湿实验、人工科学规则核验、Linux。
官方 GitLab CI 未执行；GitHub CI 未运行。没有推送或新关闭标签。

**不确定**：真实制备与实验功能、报告结论的科学真实性，以及后续 S1/Kit 接口决定。

以下是已提交的第二轮历史报告；测试数量和当前进度以上述 C2 记录为准。

# 历史：S1b 第二轮，Kit 迁移准备与规格演练

四个 Kit 盘点完成；交付 19 份能力、25 条规则、8 个模板草稿，没有 Kit 代码。
登记 K1 至 K6，其中 4 个结构接口问题；最大缺口是 Kit 领域文档 Schema 没有注册契约。
新增 4 个被至少两个 Kit 使用的非 CRISPR 纯函数与能力；4/4 源码变异被断言捕获。
全量 163 项中 162 通过、1 项登记未执行；该项配置 Primer3 后单独实际运行通过。

## 四个 Kit 的结论

**Cut Plasmid**：能力/规则/两个模板的现有 Schema 与 A14 校验通过，但还不能表达完整可执行契约。
K1 缺 guide、primer-set、route、selection 文档 Schema 注册，K4 缺独立模型的参数与产物绑定，
K6 缺 ACTION 访问运行时冻结知识的接口。S2 仍需实现序列方向、PAM、自切、选定 guide
替换与筛选解释；候选 gRNA 枚举/排序首版丢弃。注释矛盾、差一位 PAM、错误 CDS、
继承与引入、完整引物和 Tm 参数、测序坐标负例均已写成构造计划，尚未执行 Kit 测试。

**Revival Evidence**：非 DNA 观察路线可用现有能力/规则/模板声明形状描述，仍依赖 K1 的
观察/评估文档契约和 K6 的冻结知识访问。旧表 5 条记录均有来源标记，新增对照出菌落
策略来自固定旧代码，只证明项目有限结论边界。CSV 缺 id 自动补记、缺失计数不当零、
对照矛盾、菌落不推出功能复活均有预定负例；S3 尚需实现解析与解释。K2 的无来源隔离
和 K5 的预期结果交接语义需要负责人决定。

**Construct**：PCR/Gibson 两个模板已列出独立模型、制备、编辑后参考、接口 QC 与交接
输出，形式校验通过。K1 的文档注册、K4 的模型绑定及 K5 的交接形状仍未解决。
独立供体模型、同源臂/参考坐标、供体外接口引物和 handoff 实现留给 S5a。旧 Gibson 缺
feature_to_dict import 与失败时 checked_scope 键错误仅作为待执行回归，未导入旧程序。
模型产物与序列计算不证明供体已经物理制备或整合。

**Genome Identity**：背景区分的能力声明形状可表达，两个真实模板均因有序材料引用数组
不符合 A3 oneOf 而失败，属于 K3。还依赖 K1 的文档注册、K5 的 primer_pair 与
无产物/多产物语义。区域比对、给定背景的带型可区分性、参考哈希交接核对留给 S5b；
1000/1300 bp、相同带型、重复位点、跨环状起点、错误参考哈希均有独立构造计划。
现有草稿不能作为可运行 Kit，有限给定背景也不证明未知样本的全基因组身份。

逐文件/函数/行数/提交、每个能力的完整声明、规则来源和负例答案依据分别在
[Cut Plasmid](docs/kit-prep/cut-plasmid.md)、[Revival Evidence](docs/kit-prep/revival-evidence.md)、
[Construct](docs/kit-prep/construct.md)、[Genome Identity](docs/kit-prep/genome-identity.md)。

## 结构类

原 S1b 技术门已由规格负责人以 s1b-closed 标签关闭在 a6905eb；本轮没有关闭新门。
K1/K3/K4/K6 属于结构接口，K2/K5 属于来源隔离与交接数据语义。
逐条原文依据、演练反例与建议保留在 [QUESTIONS.md](QUESTIONS.md)。
仅有 capability-v1 通过不足以证明 schema_ref 存在、模型可绑定或知识能够冻结访问。
没有新增未批准字段，也没有将材料集合改成不受追踪的 JSON 值以取得校验通过。

56 份主草稿加 2 份刻意负例共 58 份。原生 Schema 无效 3 份，A14 无效 1 份：
两份 Genome Identity 实际模板、一个缺来源规则探针、一个部分占位符探针。
后两者是拒绝行为的演练，不是从旧数据发现的缺来源条目。
其余 54 份形式校验通过，领域合同缺口仍保留。

Kit 文件位于 docs/kit-prep/drafts，不在 kits/；implemented_in 只是未来目标名。
没有修改 S1 独占层、规格、受保护 Schema、词表、档位或版本源。
4 份新增 core capability JSON 来自既有装饰器导出，配套 Task C 的 4 个能力，
不修改 capability-v1 或其他受保护 Schema。

## 实际运行了什么

执行目录 code/genome-revival-toolkit，所有命令带 PYTHONPATH=src；
[README](README.md) 给出完整 PowerShell 复现命令。原始日志与机器计数位于
[tests/evidence/s1b-round2/validation.json](tests/evidence/s1b-round2/validation.json)。

| 实际范围 | 结果 |
|---|---|
| tools/check_structure.py | 退出 0，findings=[] |
| tools/check_schemas.py | 退出 0，35 个 Schema、227 个模式夹具，findings=[] |
| spec_lint，显式 SPEC.md 路径 | 退出 0，HARD findings: 0；SOFT findings: 17 |
| unittest discover -s tests -v，子进程移除 Primer3 配置 | 163 项，162 通过、1 登记跳过，0 失败/错误；189.302 秒 |
| 实际 Primer3 Context 集成项，显式配置本机程序 | 1 通过、0 跳过；不是新增的第 164 个独立测试 |
| 缺配置/配置后错误结果的两项策略测试 | 调用原集成测试；分别断言 1 skip/0 pass 和错误指纹导致 1 failure/0 skip |
| 四个共享函数独立单元测试 | 替换/特征退役、CDS 手译与未知、引物 core/tail/方向、测序首碱基与环状边界 |
| 四个共享能力集成 | 通过真实 Catalog/接纳/Invoker/Store 执行；对照声明、导出 JSON 与构造答案 |
| 原有第一轮生物测试 | 包含于上述 163 项完整发现，未弱化原预期 |
| 新源码变异 | 4/4 被断言捕获；原始 stdout 为 {"mutations": 4, "caught": 4} |
| tools/validate_kit_drafts.py | 退出 1，原始失败保留；不是实现测试失败 |
| Kit 执行、Kit 端到端、湿实验、官方 CI | 未执行 |

Primer3 缺配置只触发登记的 S1B-PRIMER3-OPTIONAL，报告 NOT_PERFORMED，不算 PASS。
登记包含负责人、条件、原因和到期日 2026-11-16。配置存在但执行/结果错误仍失败。
错误结果策略用模拟的错误指纹证明失败断言仍生效；另行配置真实程序执行的集成项才是
实际外部调用证据，两者不混计。

草稿校验脚本输出原文：

```text
{
  "draft_documents": 58,
  "by_schema": {
    "kit-v1": 4,
    "capability-v1": 19,
    "rule-v1": 26,
    "pipeline-template-v1": 9
  },
  "schema_invalid_documents": 3,
  "a14_invalid_documents": 1,
  "expected_invalid_probe_documents": 2,
  "question_ids": [
    "K1",
    "K2",
    "K3",
    "K4",
    "K5",
    "K6"
  ],
  "scope": "Schema/A14 and explicit contract rehearsal only. No Kit code imported, no draft is loadable or scientifically accepted."
}
drafts/genome-identity/templates/from_handoff.json ['steps', 5, 'inputs', 'references']: [{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not valid under any of the given schemas
drafts/genome-identity/templates/from_references.json ['steps', 4, 'inputs', 'references']: [{'step': 'original', 'port': 'material'}, {'step': 'edited', 'port': 'material'}] is not valid under any of the given schemas
drafts/revival-evidence/probes/source-missing.json ['source']: 'source_class' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'citation' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'locator' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'retrieved_at' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'content_ref' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'archive_note' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'supports' is a required property
drafts/revival-evidence/probes/source-missing.json ['source']: 'does_not_support' is a required property
drafts/revival-evidence/probes/partial-placeholder.json []: A14 requires a whole-string placeholder with a valid lowercase name.
```

开发失败未覆盖：development-run-01 保留新 coverage 输出误用 scope 触发 INV-V1 的
扫描及全量失败；输出键改成 assumptions 后重跑完整范围通过。
mutations-first-run 保留首轮 3/4 直接断言捕获；区域变异最初先被内核坐标不变量阻断，
加入无特征的独立序列断言后，当前 4/4 均由测试断言捕获。
最后仅修正旧代码盘点的丢弃措辞，重新生成/校验草稿并定向重跑 3 项草稿校验测试通过；
没有重新计算或替换科学答案。

## 实现类

| 新函数 / 对应 ACTION | 明确使用方 | 限定结论 |
|---|---|---|
| replace_material_region / seq.replace_region | Cut Plasmid、Construct | 半开区间替换/删除/插入；未受影响特征平移，相交特征退役；不是物理制备 |
| inspect_cds / seq.inspect_cds | Cut Plasmid、Construct | 显式遗传密码表/读框/起止/内部终止与翻译；partial/ambiguous 不作完整 CDS 肯定结论 |
| enumerate_primer_candidates / primer.enumerate_candidates | Cut Plasmid、Construct、Genome Identity | 显式 anchor/方向/长度/NN 参数，无排名；core Tm 与完整带尾引物 QC 分开 |
| sequencing_read_coverage / primer.sequencing_coverage | Cut Plasmid、Construct | 从唯一结合位点的 3′ 端投射指定读长/trim；多位点不给确定覆盖，不是测序观测 |

公开面现为 51 个函数和 TmParameters，共 52 个符号；原 22 个能力加本轮 4 个，
共 26 个 S1b 能力。逐函数出处/新旧行数/耦合写入 [MIGRATION-LOG.md](MIGRATION-LOG.md)，
至少两个 Kit 的需求矩阵保留在 shared-needs.json。没有实现 CRISPR 或单 Kit 专用算法。

旧 Kit 工作树当前 HEAD 已无相应路径，源码从 bf90910e5b0e67985aa37db4e0b8507cbc24f2b4
Git 对象只读取出；通用 Core 另固定在 750bf4849b818be00f28684513ef19c01d901bcb。
未 checkout、import 或运行旧代码。旧规则共 24 条，24 条带来源标记、0 条缺来源。
kan 的两个宿主来源拆分，退役与 D7 冲突的 no-template-exemption，另从旧代码提取对照
矛盾策略，形成 25 条 draft/unverified 草稿。没有继承旧 verified 或填写人工核验回执。

**已验证**：上述程序测试、实际 S1 调用、登记跳过策略、独立构造/手算答案、4 个源码变异、
现有 Schema/A14 对草稿的接受/拒绝结果。这个范围不包括 Kit 可运行性或科学规则核验。

**模拟**：合成 DNA 的编辑、CDS 翻译、PCR/组装、候选引物与指定距离的覆盖计算。
Kit 负例与 CHECK 夹具仅为待实现的构造计划，未冒充实际 Kit 测试。

**未做**：Kit Python、Kit 接纳/运行/封存、人工科学审核、湿实验、真实用户 DNA、
联网核实旧引用、依赖安装、Linux、合并、推送、新关闭标签。
官方 GitLab CI 未执行；GitHub CI 未运行。

**不确定**：K1 至 K6 的最终规格决定、旧引用是否足以支持每项生物判断、原生未解析块
保真度以及任何实际制备、整合、表达、抗性、复活功能或样本全基因组身份。

以下为 a6905eb 之前的第一轮历史报告；数量和门状态以本轮报告及负责人标签为准。

# 历史：S1b 生物层批 1 至 4，S1 接入交付

已实现 22 个能力：18 个 ACTION、4 个 CHECK，以及装饰器导出的 capability-v1 JSON。
材料直接使用 S1 kernel.material；Primer3 两次进程调用均经 ctx.run_external。
全量 tests/ 153 项通过，8 个 CHECK 正反样例符合预期，4 个源码变异均被捕获。
结构扫描和模式检查无发现；spec_lint 硬问题 0。
S1 与 S1b 的阶段门仍由规格负责人复核关闭，本报告不关闭门。

## 结构类

基线为用户合并的 c8cc70a。原 S1B-Q1 至 Q4 已按用户答复解决：
起点依赖按 D9，不要求旋转保持材料身份；环状 k-mer 属性继续保留为序列属性；
sgffp 排除，原生读取使用 Biopython 1.88；旧规格/模式冲突已由 S1 合并解决。
没有修改 kernel、storage、catalog、engine、assurance、record、application、
受保护模式、词表、档位、版本文件或规格。seq.reverse_complement 未改。

材料适配器调用现有 kernel.material.normalize 和 kernel.ids。特征保留精确
坐标、复合区间的生物学顺序与限定词；没有另建材料类型、哈希或裁决构造器。
GenBank 用绑定可见序列/注释投影的补充信息保存物理末端和内核字段，编辑了
可见内容时拒绝恢复旧信息。FASTA 对无法表示的拓扑、链、末端及特征拒绝静默丢失。
模糊/远程坐标、GenBank 无法保留的未知特征方向仍明确拒绝。

S1 Context 的实际外部调用签名是 run_external(argv)，没有 stdin。Primer3
输入写在 ctx.workdir 后作为命令参数传入。程序版本、可执行文件 SHA-256、
热力学数据文件哈希保存在结果文档；请求和原始响应保留为 artifact。
S1b 不新增环境读取点。测试把 GRT_PRIMER3_CORE 映射到注入的 ctx.config；
产品配置与 run.created 环境指纹构造仍属于 S1。

## 实际运行了什么

命令均在 code/genome-revival-toolkit 下运行，PYTHONPATH=src，配置了本机
GRT_PRIMER3_CORE。README 给出 PowerShell 命令。原始输出及机器计数见
[validation.json](tests/evidence/s1b/validation.json)。

| 范围 | 结果 |
|---|---|
| tools/check_structure.py | 0 发现 |
| tools/check_schemas.py | 35 个模式、227 个模式夹具，0 发现 |
| tests/structure | 53 通过，0 失败/错误/跳过 |
| tests/contract | 8 通过，含 3 项新增能力声明/签名/独立答案契约 |
| tests/unit | 78 通过，含材料/物理末端/格式与生物算法测试 |
| tests/integration | 14 通过，通过真实 Catalog、接纳计划、Invoker、Store、只读 CHECK View 运行 |
| tests/e2e | 当前目录没有测试，0 项；未作为端到端验收 |
| tests/ 合计 | 153 通过，0 失败/错误/跳过 |
| CHECK 正反样例 | 4 个 CHECK 各 1 通过、1 失败，共 8 个实际执行结果符合预期；所有失败样例为 FAIL |
| 源码变异 | 4/4 被断言捕获：PCR 歧义、突出端标签相等、Tm 盐修正、特征起点偏移 |
| spec_lint | 硬问题 0，17 个既有软提示 |
| 独立 Primer3 CLI | 7 组合成输入重新实际运行，Tm 最大绝对差 0.00041349 °C |
| Primer3 正式能力 | 实际运行 version probe 和计算，spy 记录两次 Context.run_external；另测缺程序返回 UNKNOWN 与指引 |

CHECK 原始结果在 tests/evidence/s1b/integration/check-fixtures.json：
check.primer_quality、check.format_roundtrip、check.pcr_product、check.assembly_product
的 pass 样例均为 PASS，fail 样例均为 FAIL。测试还逐字节比较 CHECK 前后运行目录，
确认 CHECK 没有写入。PCR/组装负例使用构造的错误产物引用，不冒充真实实验记录。

结构先运行；没有跳过或弱化原测试。开发中遇到的失败保留在 development-history.json、
development-run-01、development-run-02 和 before-c8cc70a 中。最后一次脚本汇总
最初仅因 spec_lint 默认相对路径失败；显式传入 SPEC.md 后单独重跑该命令，
153 项测试此前已经通过。没有为修复测试而改变预期科学答案。
额外补测了非法 GC 限值文本：纯函数给清楚的参数错误，真实 CHECK 给 UNKNOWN；
相关 13 项引物/PCR 单元测试及 2 项 CHECK 集成测试定向重跑通过。

已验证：上述限定范围的程序契约、实际调用、内容存储、只读检查及独立数值对照。
模拟：PCR、酶切、连接、重叠组装及反向 PCR 环化的序列计算。
未做：湿实验、真实用户 DNA、Kit 验收、完整封存流程、Linux、官方 CI。
不确定：原生格式未解析块的保真度、任何实验效率与生物学功能。
官方 GitLab CI 未执行；GitHub CI 未运行。

## 实现类

| 目录 | 能力 |
|---|---|
| builtin/format | read_genbank、read_fasta、read_dna、write_genbank、write_fasta |
| builtin/seq | make_material、slice、rotate |
| builtin/primer | calculate_tm、inspect_quality、find_binding_sites、run_primer3 |
| builtin/pcr | simulate，保留完整引物 core/tail 与产物计算文档 |
| builtin/restriction | scan_sites、digest，材料输出携带真实突出端 |
| builtin/assembly | ligate、gibson、inverse_pcr，显式材料端口，保留反向 PCR 线性中间体 |
| builtin/check | primer_quality、format_roundtrip、pcr_product、assembly_product |

能力 JSON 来自 @capability 元数据。契约测试比较导出 JSON、装饰器声明、类型
签名和必填参数，所有能力登记独立答案或实际执行的 CHECK 夹具。
生物公开面为 47 个函数和 TmParameters，共 48 个公开符号；逐函数旧路径、
新旧行数与耦合见 MIGRATION-LOG.md 和 migration-inventory.json。

质量阈值由调用者显式提供，没有无来源的科学默认阈值。缺阈值或缺材料返回
UNKNOWN。一次质量检查选择一条寡核苷酸或一对引物，二聚体/发夹精确互补 bp
不冒充 Primer3 热力学结构 Tm。无相关反应时，反应检查给带依据的 NOT_APPLICABLE。

组装薄壳接受一个或两个显式材料端口；更多片段通过材料步骤串接，酶切材料集合
通过明确 index 引用。限制酶模拟不推断甲基化；紧邻交错切点、无双链核心和未
建模的既有黏性末端底物酶切明确拒绝。切片不声称完成物理制备。

Primer3 当前请求覆盖完整 2 至 36 nt 寡核苷酸，较长序列明确拒绝且不截短。
程序为 libprimer3 release 2.6.1，SHA-256 为
19a546a0166fd979c41317e45696de1b383ab5fa21ec362bcc5053b2068b6e5f。
生效参数为 Na 50 mM、total oligo 50 nM；普通 Mg/dNTP 为 0，Mg 对照为
2/0.5 mM。NN 表为 DNA_NN3、盐修正 5；对应 Primer3 TM_FORMULA=1、
SALT_CORRECTIONS=1。每次输出保留参数。完整对照在 primer3-comparison.json。
独立手算的 NN 堆叠、端基、对称熵及钠当量测试继续保留；Primer3 不是唯一答案。

依赖锁定不变：Python 3.12.4，jsonschema 4.26.0，rfc8785 0.1.4，Biopython 1.88。
没有安装依赖、联网、复制外部二进制、写原生 .dna、合并、推送或打关闭标签。
历史报告保留为 S1B-REPORT.before-c8cc70a.md。

能力、材料与运行证据提交：c902aee。后续参数错误处理与交付文档在同一分支另行提交。
