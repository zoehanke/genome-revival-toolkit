# S5a Construct 本地交付记录

Construct 计算实现已完成，阶段验收未完成。
公共封存层尚不能交付交接文件，且所需公共检查不齐。
AI 已完成两种制备、接口检查、独立校核及要求的变异控制。
队员（公共层负责人）需先补齐 QUESTIONS.md 中的封存依赖，再由规格负责人复跑并决定阶段门。

## 结构类

基线为 integration-1 / fc04e410729b5933030375762d15e2a1c88ef95e，分支 s5a-construct。
本轮在开发工作树运行，运行记录标为 dev-tree，不是发行验证。
补充说明在指定主工作区路径不存在，本轮通过 Git 标签 integration-1b 的
prompts/parallel-addendum-20261017.md 读取，未切换或合并分支。

Kit 只有能力、知识说明、数据模板和文案。模型与制备分别在 model.py、design.py：
模型逐位读取明确区间；制备走实际模板 PCR 和真实重叠序列模拟。两条路径不互调。
design_donor 直接作为计划步骤，声明 model_donor 后由公共系统自动增加模型比较。
声明、模板与目录结构均被实际装载和校验。未修改规格、受保护文件或公共实现。

当前不能关闭的验收项：

| 问题 | 亲自运行得到的结果 | 谁来处理 |
|---|---|---|
| 封存层不接收文件输出 | 两个完整模板均在 judge/seal 返回不支持 artifact 的输入失败；verify 因没有封存包失败 | 队员，公共层负责人 |
| 公共科学检查不齐 | 单独诊断保留 construct 档位，六个必过项均为 UNKNOWN，含五个缺失检查及缺少参数绑定的引物质量检查；seal 退出码 10 | 队员，公共层负责人 |
| 编码注释来源裁决缺失 | 已运行合法和含内部终止的标记盒，保留完整注释；D7 的继承／引入／来源不明裁决尚无法运行 | 队员，公共检查负责人 |
| 真实跨 Kit 消费及复制封存包复验 | 当前分支没有 Genome Identity 实现，也没有可复制的 Construct 封存包；均未执行 | 队员在集成后复核 |
| 一项旧公共测试按错误目录找样例 | 完整测试报告 FileNotFoundError；同一声明路径在功能包目录下实际存在，在公共目录下不存在 | 队员，公共测试负责人 |

这些缺项没有被替换成较低档交付或成功标记。完整模板仍绑定 handoff 文件。
另一个诊断运行仅用于显示公共检查缺项，不是正式交付。详情见 QUESTIONS.md S5A-Q1/Q2。

## 实际运行了什么

**已验证，仅指本地代码运行。**

- Construct 专项 15 项检查通过，实测约 0.048 小时。这意味着两种制备、接口区分、注释保留、模型变异和要求的负例符合构造答案；不意味着封存完成或湿实验成功。
- 独立标准库脚本从真实输出文件重算：Gibson 42 项、PCR 34 项检查通过。这意味着供体序列、同源臂坐标、完整引物、每个结合位置、预期产物长度及文件字节哈希相符；不是实验结果。
- 两种路线均产生 190 bp 线性供体：左臂 50 bp、标记盒 90 bp、右臂 50 bp；删除原参考的 [100,160) 后，编辑参考为 330 bp。两侧接口 PCR 各预测 90 bp，只在编辑后参考上有产物，原参考和残留供体上无产物。
- 最终命令行记录含 25 次公共调用。这意味着从创建、目标、模板、提交到执行、判定、封存尝试、复验尝试和卡片输出均有真实回执；退出码 0 不能被解读为已封存。两个完整路线的判定／封存／复验实际失败，诊断路线的封存实际被拒。
- 结构扫描无发现；35 份公共模式与 237 份公共夹具校验无发现；规格扫描硬问题 0。这意味着声明、契约和规格字段保持一致，不代替科学验收。公共生成文档检查无差异。
- 仓库完整测试共 243 项：242 项通过、1 项报错、0 项跳过，实测约 0.334 小时。这意味着已运行的契约、公共命令、集成、结构和单元检查中，仅旧公共测试的样例路径解析报错；不能写成全仓通过。错误是 tests/unit/test_assurance.py 的只读检查把 Kit 自带样例按公共目录查找。原始错误栈在 full-01.txt，目录存在性对照在 fixture-resolution.json；未修改他人负责的测试。

| 实际执行的控制 | 观察到的行为 | 结论范围 |
|---|---|---|
| 独立模型改错一位 | 模型比较 FAIL | 能抓住预期模型错误 |
| 制备产物改错一位 | 模型比较、制备检查均 FAIL | 能抓住实际产物错误 |
| 实际 PCR 模板错一位 | 模型比较 FAIL，制备重算 PASS | 制备确实来自所给模板；独立模型负责发现模板不符合目标 |
| 同源臂越界 | 制备前停止，返回已登记的输入错误 | 未默默缩短同源臂 |
| 两个接口引物都放在同源臂内 | 残留供体预测 190 bp 产物；报告明确警示；接口检查 FAIL | 残留供体也会出带，不能据此认定基因组整合 |
| 同一引物有两个结合位置，但只有一个配对产物 | 报告保留两个结合位置；接口检查 FAIL | 没把“一个产物”当作“结合唯一” |
| 制备引物重复结合 | 停止制备，返回输入错误 | 没挑最短产物冒充唯一 |
| 标记盒含内部终止密码子 | 内部终止被检测，原注释仍保留；正式 D7 裁决未执行 | 不能宣称坏 ORF 已通过内容检查 |
| 无标记盒的单纯缺失 | 供体 100 bp；外侧引物在原／编辑参考分别预测 200／140 bp，残留供体无产物 | 只说明计算上的长度区分 |

**模拟。** 所有 DNA 均为固定种子 20261017 构造的合成序列；供体、PCR、Gibson
和接口产物均为计算模型。没有读取用户 DNA，也没有联网取序列。

**未做。** Construct 封存成功、复制封存目录后复验、真实 Genome Identity 消费、
正式 D7 来源裁决、打包后隔离宿主端到端、真人试用、Ubuntu 测试和湿实验均未完成。
官方 GitLab CI 未执行；GitHub CI 未运行。

**不确定。** 本轮不能判断实验室制备成功率、转化效率或真实整合位置；没有对应实验数据。
坏 ORF 的正式来源裁决仍依赖公共层实现。

## 实现类与保留证据

本地提交：54fedba 为 Kit 实现，5c86e11 为测试及原始证据；未合并、未推送。

主要文件：kits/construct/README.md、kit.json、SKILL.md、capabilities/、templates/、
text/en.json、examples/。交接形状严格为 D11 的 identity-handoff-v1，参考序列只用
文件字节哈希引用。文件自身哈希由执行器记录。独立脚本是
tests/oracles/construct_verify.py，仅使用标准库，不导入 Kit 或 Core。

移植统计：实际旧源文件 205 行，新 Kit Python 415 行，其中声明／模式 79 行。
移除了九条旧项目导入耦合。两种工作流改为数据模板。原三条范围政策合入明确参数、
检查和 does_not_establish，没有新增待核验的科学规则表。详见 MIGRATION-LOG.md
及 migration-measurement.json。未运行旧代码，旧输出没有被用作标准答案。

旧 feature_to_dict 导入与 checked_scope 二次异常的控制：新版真实运行带 CDS 注释
的线性 Gibson 和失败输入，保留完整编码注释，失败仍返回登记的输入错误。
第一轮发现重叠裁剪会丢失标记盒注释，已把重叠移到标记盒 PCR 引物尾部。
原失败完整留在 focused-01.txt，未删测试或改变构造答案。
另一项首次失败来自测试把 dna_design_core 名称中的 design 误认成算法导入；
已改为按真实模块名判断，模型与制备的独立边界要求保持不变。

临时默认清单：S5A-P1 为 Kit 内部文档字段及显式几何参数；S5A-P2 为外侧接口引物
的固定布置和纯缺失时的外侧配对；S5A-P3 登记暂放 Kit 的领域算法。
QUESTIONS.md 列明理由、若被否决需改的文件；相应代码有 PROVISIONAL 注释。

隔离 AI 路由预演识别了本 Kit 的 PCR/Gibson 两类请求；其他 Kit 的空说明限制了
其余路由。仅描述路由预演，不是独立宿主任务验收，原始首次选择见 routing-preview.md。

旧写法残留仅在未装载的迁移草稿：docs/kit-prep/drafts/construct/capabilities/ 下的
design_donor.json、design_junction_assay.json、export_handoff.json，以及 knowledge/ 下
construct.donor-not-integration.json 的历史来源引用。当前 Kit 使用内联模式，没有这些
旧 schema_ref 或 checked_scope 字段。扫描原文见 residual-scan.txt，未越界修改草稿。

证据目录：tests/evidence/s5a-construct/。

可直接查看的计算候选，均未封存：

| 内容 | 文件 |
|---|---|
| Gibson 实际供体 | [donor.gb](tests/evidence/s5a-construct/cli-03/gibson/run/work/donor_file/donor.gb) |
| Gibson 完整制备引物 | [primers.json](tests/evidence/s5a-construct/cli-03/gibson/run/store/documents/de050a0dce9d54700484557f52e3f6e6c79a18533a8e05b15f5ec01f8f0c3d79.json) |
| Gibson 接口预测及警示字段 | [assay.json](tests/evidence/s5a-construct/cli-03/gibson/run/store/documents/c4dae870c018659ffcd4c01a7b532f78868e078346400fc11a9ffc967a2d8925.json) |
| 给下一 Kit 的交接文件 | [identity-handoff.json](tests/evidence/s5a-construct/cli-03/gibson/run/work/handoff/identity-handoff.json) |
| PCR 实际供体 | [donor.gb](tests/evidence/s5a-construct/cli-03/pcr/run/work/donor_file/donor.gb) |
| PCR 完整制备引物 | [primers.json](tests/evidence/s5a-construct/cli-03/pcr/run/store/documents/aff93e9f6d38272567fe4911fc8150ec1892cb6295de1c5edda2be6319b5bae0.json) |

- focused-01.txt 保留首次三个失败；focused-02.txt 为修正后的专项结果。
- first-execution.txt、execution-02.txt、execution-03.txt 保留开发请求错误；execution-04.txt 为首次运行成功。
- cli-01-summary.txt 保留测试脚本导入路径失败；cli-02 保留调整重叠前的未注释案例；cli-03 为最终命令行原始请求、回执、输出文件及日志。
- cli-03/results.json、gibson-independent.json、pcr-independent.json 可直接核对实际结果。所有未封存目录明确保持未封存。
- primer3-fingerprint.json 记录实际 --about 输出 libprimer3 release 2.6.1 和可执行文件哈希；Construct 的精确几何计算未调用该后端。公共完整测试已配置该后端。
- summary.json 为最终测试统计，full-01.txt 保留整仓错误；两个完整模板没有封存包，不能从统计里的通过数推断交付成功。
- 完整测试自动重写的旧 S1b-C2 裁决运行哈希，已另存 full-generated-s1b-c2-check-fixtures.json，并确认其余数据一致后恢复旧文件；未把其他任务目录的改动带入提交。

本记录不关闭阶段门，不代填审核声明。
