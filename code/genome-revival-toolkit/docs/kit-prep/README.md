# Kit 迁移准备

本目录只含盘点、草稿和规格演练证据，没有 Kit Python 实现。
原 S1b 技术门由规格负责人关闭在 a6905eb；本轮不替任何 Kit 关闭门。

- [Cut Plasmid](cut-plasmid.md)：方向/PAM/自切与条件筛选；CRISPR 代码留给 S2。
- [Revival Evidence](revival-evidence.md)：非 DNA 的观察与有限结论，不能把菌落数当功能复活。
- [Construct](construct.md)：独立模型、制备、接口 QC、参考与交接绑定。
- [Genome Identity](genome-identity.md)：给定背景的预测区分；有序材料集合绑定仍撞到 A3。

58 份形式草稿包括 4 份 kit-v1、19 份 capability-v1、25 份 rule-v1、
8 份 pipeline-template-v1，另有 1 个缺来源规则和 1 个部分占位符探针。
主草稿 56 份；探针 2 份。原生 Schema 失败 3 份、A14 失败 1 份：
其中两份是实际 Genome Identity 模板阻塞，两份是刻意负例。

K1/K3/K4/K6 是结构接口问题；K2/K5 是数据与交接决定。
完整原始消息见 [schema-report.json](schema-report.json)；
逐条原文依据及建议见 ../../QUESTIONS.md。

旧 Kit 源码在当前旧工作区 HEAD 已不存在，全部从 Git 对象
bf90910e5b0e67985aa37db4e0b8507cbc24f2b4 只读取出，未 checkout、import 或执行。
Core 参考另固定在 source-inventory.json 指定的提交。
旧规则 24 条均有来源标记；没有发现空来源行，但这不是 24 条科学事实已核实。
25 条迁移/拆分/代码策略草稿一律 draft/unverified。旧 verified 标记不继承，
没有填写任何人的审核、签名或核验回执。

共用函数的需求矩阵见 [shared-needs.json](shared-needs.json)。
只服务一个 Kit 的逻辑和全部 CRISPR 判断都未搬入 biology。
`drafts/` 从不放进 `kits/`，不存在可执行实现；实现路径只是未来目标名。
官方 GitLab CI 未执行；GitHub CI 未运行。
