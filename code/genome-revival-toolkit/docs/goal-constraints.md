# D2 核心目标约束检查

六项能力均为 core CHECK、scope=user_goal、evaluates_constraint=true、offline=true。
把其精确版本 id 写入 goal.constraints[].check，参数写入 params，目标写入 target。
它们由 assurance 按活动约束调用，不放在流水线步骤中。版本读取 VERSIONS.json。
参数完整模式由 describe capability 和 resources/capabilities 对应 JSON 提供。

| 检查 id | 必填参数 | 可选参数 | 计算含义 |
|---|---|---|---|
| check.goal.topology | topology: linear 或 circular | 无 | 每个绑定目标材料的已知拓扑等于指定值；null 不推断 |
| check.goal.exact_sequence | sequence: 非空 IUPAC DNA | 无 | 大写化后完整字符串相等；所选起点与方向固定；N 是字面字符 |
| check.goal.components_present | components: 非空数组，每项含 name、sequence | 每项 strand: 1 或 -1，默认 1 | 每个绑定材料含每条明确 ACGT 片段；只按序列判，标签不作证据 |
| check.goal.components_absent | 同上 | 同上 | 每个绑定材料均无每条片段；已知环状材料包含跨起点匹配 |
| check.goal.regions_unchanged | reference_material_id: 小写 SHA-256；regions: 非空数组 | 每个区域 strand: 1 或 -1，默认 1 | 参考材料与每个目标材料按两侧显式区间比较 |
| check.goal.claim_reported | claim: 非空主题字符串 | pointer: JSON Pointer，默认 /claims | 绑定 JSON 报告中恰有一条同主题记录，含非空字符串 status；不检查其真假 |

DNA 检查只接受绑定的 material 输出。无绑定目标给 FAIL；未给约束目标、内容丢失、
类型不支持给 UNKNOWN。明确反例优先 FAIL；没有明确反例但存在未知信息给 UNKNOWN。
例如一个材料已知为 linear、另一个拓扑为 null，要求 circular 的结果仍为 FAIL。
检查不会改用别的目标，也不会把 goal.sources[].declared 当成程序事实。

组件片段仅允许无歧义 ACGT。strand=-1 时搜索该片段的反向互补。片段长度不得超过
整个材料长度；环状匹配允许一次跨起点。缺少匹配时，未知拓扑或材料含歧义碱基会给
UNKNOWN；明确匹配可证明字面片段存在，也足以使 components_absent 给 FAIL。
这些检查不证明表达、抗性、功能模块活性或基因组脱靶安全。

regions 每项严格包含 source_start、source_end、target_start、target_end，均为 0 起半开
非空区间，可另加 strand。两侧坐标均须在序列内，不隐式跨环状原点，不猜编辑后偏移。
strand=-1 时先对参考片段取反向互补再比较。不同长度或碱基不等给 FAIL；无效/越界区间
及不可读参考给 UNKNOWN。reference_material_id 必须能在本次保留材料存储中读取。
该检查只比较用户选择的参考，不证明该参考就是原始输入，也不替代注释/CDS 继承检查。

claim_reported 接受 document 或 JSON artifact。document 通过内容存储身份读取；artifact
从绑定候选根目录读取并核对实际字节哈希。pointer 可指向一条记录或记录数组，例如：

```json
{"claims": [{"claim": "functional_revival", "status": "INSUFFICIENT"}]}
```

以上对 params={"claim":"functional_revival"} 给 PASS，只证明报告包含该主题及状态。
UNKNOWN、INSUFFICIENT 等 Kit 状态均可满足“报告了状态”。缺字段、空白状态、重复主题
给 FAIL；自由文本、事件中的宿主声明、其他目标的报告不能代替此结构。内容不可读或
哈希不符给 UNKNOWN。pointer="" 选择根记录；JSON Pointer 转义遵循 ~0 与 ~1。

区域参数例子，对应先将 AAACCCGGGTTT 的 CCC 替换成 AT 的构造答案：

```json
{
  "reference_material_id": "6e55abd9e6965ca38c30d771bed2934dfaee05f667da76f929eda9307b51b36d",
  "regions": [
    {"source_start": 0, "source_end": 3, "target_start": 0, "target_end": 3},
    {"source_start": 6, "source_end": 12, "target_start": 5, "target_end": 11}
  ]
}
```

示例标识绑定该十二碱基参考，topology=linear、strandedness=double、ends=null、features=[]。
两个区域的预期答案分别为 AAA 和 GGGTTT，由字面构造决定。

tests/fixtures/goal_checks 含 12 份正反样例，每份列明独立答案和参数。
tests/integration/test_goal_constraints.py 实际运行全部样例、只读检查、未知边界和
活动目标约束到 Judge 的调用；tests/oracles/goal_mutations.py 对六项源码各做一处变异。
这些是程序契约证据，不是 Kit 验收或实验结果。

S1.1 的请求 origin 处理、目标提交时参数模式校验、output_present.fields 与错误指引
仍由 S1 处理。本能力通过 Invoker 的现有参数校验，不声称已经完成 S1.1 的提前拒绝。
