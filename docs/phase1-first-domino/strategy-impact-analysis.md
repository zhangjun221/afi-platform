# 战略转向分析：从平台建设转向"第一骨牌归因"旗舰

> 2026-07-14。这份文档回答一个问题：**afi-platform 建到 A1-A4 闭环后，怎么做最有影响力？**
> 它整合三块：① 仓库内 13+ 份战略文档的战略复盘（避免重做）；② 2025-2026 领域前沿扫描（grounded）；③ 据此修正后的方向 + 第一步 pilot。
> 性质：**战略转向记录**——从"平台保真度建设"转向"归因方法旗舰"。对接已有 `strategy.md` / `external-safety-framework-survey.md` / `实施路径_任务规划.md` / `eval-suite-goals.md`。
> 受众：研究者/评审/未来的自己。

---

## 〇、一句话结论

**别再加保真度（地图/工具/全量跑），也别只追现象 finding。把仓库已反复识别但未实现的"第一骨牌归因 + 反事实世界分叉"从 plan 变成 implemented+validated，用 qwen 族 collapse 当验证 case（顺便 disentangle 它是能力 gap 还是 alignment gap）。平台 A1-A4 是底座，测试套件缓做不冲突（归因是 label-free 的，绕开 label 脆弱性）。**

---

## 一、诊断：当前卡在哪

A1→A4 的节奏一直在"把平台建得更全"（地图、116 工具、全量跑、测试套件）——**这些全是保真度，不是影响力**。

对照 Project Sid（Altera 2024）：它的引爆点**不是引擎**，是"1000 agent 自发形成经济和宗教"这个 surprising finding，引擎只是 finding 背后的可复现 artifact。

afi-platform 闭环已 100%（见 `technical-architecture.md` §12），**继续补地图/工具/全量跑是把工程做厚不是把研究做亮**。影响力来自"用平台 surface 一个领域不能忽视的方法/发现"，平台是支撑物不是主角。这是第一层认知解锁。

---

## 二、仓库内战略复盘（已做过的思考，浓缩）

> 13 份直接读 + 10 份代理读。结论：仓库的战略思考已高度收敛，**不用重做，只需落地**。

### 2.1 已收敛的 7 点（反复出现 ≥5 次）

1. **"observability ≠ attribution / 第一骨牌定位"——贯穿全部文档的第一楔子**。AS 有 trace/replay 但只到"观测"，不到"哪次交互/哪次 memory write/哪次制度变化是导致崩溃的第一骨牌"。**最被反复强调、判为无人覆盖的缺口。**
2. EW(设定)+AS(引擎)+AFI(审计)缝合——平台架构共识（已落地 A1-A4）。
3. **长时程×多agent×开放社会模拟×安全审计交集无人覆盖**——独特定位。诚实收窄：不宣称"首个 long-horizon multi-agent 平台"（Concordia/Smallville/AS 技术上已是），差异化在交集上做**审计**。
4. 不重造 sim 引擎，借思路不搬代码。
5. AgentSociety 2 作主平台。
6. **跨模型差分安全**——同场景×不同 LLM 比安全信号，**A4 已有实证数据**（qwen 族全 collapse，M4 谱 3.0/4.2/5.6）。
7. 攻击注入测试床 + precision/recall——`eval-suite-goals.md` 刚规划未建。

### 2.2 已识别但未落地（空白，正是机会）

| 项 | 状态 | 说明 |
|---|---|---|
| **第一骨牌归因框架** | 战略文档规划了（E5 给算法清单），**未实现** | 算法：temporal heterogeneous graph + Bayesian change-point + path Shapley + counterfactual replay；退出条件：>70% top-3 source localization |
| **反事实世界分叉（World Branching Layer）** | E3 列为创新点，未实现 | 不只定位，分支世界验证"掐掉那一步会不会不崩" |
| **测试套件（label+scoring）** | goals 规划，未实现（本轮缓做） | 与归因不冲突，归因 label-free |
| **自然涌现的合谋/治理/犯罪** | 反复发现 LLM agent 不自发调变异工具，未解决 | **最大未解实证 gap**——qwen 崩溃的软肋在此 |
| **long_horizon_agent 轨道绑具体 sim 系统** | Cluster A 仍 S0/S1 未绑定 | afi-platform 现在正是这个 binding（新进展） |
| **论文/开源产出** | 路线图 M4 出成果阶段，未进入写作 | 战略缺口 |

### 2.3 反复对标的对象（按频率）

Emergence World（最接近规格）> AgentSociety 2（工程底座）> Concordia（可换后端，无审计）> Colosseum（合谋 judge rubric 已借）> GUARDIAN（时序图 idea 借，三重阻塞不落地）> Agent-BOM / From Spark to Fire（归因方法最近邻，等开源触发重评）> OASB / AgentEval（benchmark 方法论对齐）> Smallville（认知架构参考）> watch-the-watchers / driftly / SC-Bench / MACHIAVELLI（各维度对齐）。

---

## 三、领域前沿扫描（2025-2026，grounded）

> 来源：2026-07 web 搜索。⚠️ 搜索工具有几次 glitch，只采信有实质返回的部分；具体论文标了来源可信度，未逐篇核实原文。

| 前沿信号 | 是什么 | 来源可信度 |
|---|---|---|
| multi-agent safety 成 2025-2026 一级议题 | collusion / value drift / emergent behavior 从边缘变核心；audit framework 从 checklist 成熟到 tool-backed + regulator-ready | 搜索返回（标 arXiv/OpenReview/SafeAI workshop，未逐篇核实） |
| emergent misalignment | narrow finetuning → broad misaligned LLM（Betley 2025, arXiv:2502.17424） | 高（arXiv 号实） |
| emergent collusion | self-play 涌现合谋；audit hooks/行为克隆/可解释性探针作对策（DeepMind/Google） | 中（博客+workshop 级） |
| value drift formalization | 长时程模拟 agent 从初值漂移，"formalize as measurable"阶段，**无公认度量** | 中（SafeAI workshop 级） |
| UK AISI/AISF | regulator-ready multi-agent audit methodology 需求（政策级） | 中（policy draft 级） |
| Project Sid | 长时程多 agent 文明先例（涌现社会结构） | 训练知识 |

**扫描结论（高价值，直接定位缺口）**：
- field 的 frontier 词是 **"emergent"**——涌现失配/涌现合谋/涌现行为分类。长时程多 agent 涌现正是我们的平台本性。
- **field 想要但未填的洞**：① value/behavior drift 公认度量 ② 真实长时程多 agent 文明里观测涌现合谋/俘获 ③ **没人系统测过前沿模型"作为长时程社会成员"的安全画像**（当前安全评测全是 solo chatbot）④ **society-level alignment 没被形式化**（全是 agent-level）。
- **关键判断**：detection 在商品化（watch-the-watchers/driftly/OASB/AgentEval 都能 detect），**attribution/localization 是无人覆盖的下一步**——这与仓库 §2.1 第1点完全一致。

---

## 四、方向重排（融合仓库 prior + field gap）

> 据仓库复盘修正。诚实标注：上一版分析曾主推"model-as-citizen finding"当旗舰，**这是错位**——"跨模型差分安全"仓库早已识别（§2.1 点6），不是新发现；且低估了 attribution 方法楔子（仓库判它是第一楔子，上一版评成最低）。下表是修正后排序。

### ★★★ 旗舰：第一骨牌归因框架 + 反事实世界分叉

**一句话**：不只 detect"崩了"，定位"哪一次交互/哪次 memory write/哪次制度变化是第一骨牌"，并**分支世界验证**——掐掉那一步，社会会不会不崩。attribution → mitigation 闭环。

- **为何最高维**：仓库 E3"World Branching Layer（反事实世界分叉）"+ E5"counterfactual replay engine"——把归因从"指认"升到"反事实验证"。regulator 要的 audit→countermeasure 桥，field 没人做。
- **资产契合**：`causal.py`（parent_span_id 因果树）= 事件图归因种子已建；AWI timeline = 拐点检测种子；replay = 反事实回放底座。差的 = Bayesian change-point + path Shapley + world-branching engine——**研究增量，非从零**。
- **可证伪退出条件**：E5 已给——>70% top-3 source localization。硬验收。
- **状态**：identified-but-not-built（战略文档规划了，算法未实现）。"做影响力" = 把楔子从 plan 变 implemented+validated。

### ★★★ 旗舰的验证案例：model-differential collapse（非独立旗舰，是归因框架的 case）

- qwen 族全 collapse + M4 模型谱 = 给归因框架喂的真实 case。
- **关键软肋（仓库 §2.2 确认）**："LLM agent 不自发调变异工具（recharge/crime/propose）"是已识别未解实证 gap。所以 qwen 崩溃可能是 **tool-calling 能力 gap，非 alignment gap**——单看"谁崩了"说不清。
- **正需要归因框架 disentangle**：第一骨牌定位能回答"qwen 崩溃的 first domino 是'不调 recharge'（能力gap）还是'调了但被治理结构误导'（alignment/societal gap）"。**model-as-citizen 是验证归因方法有没有用的 case，不是主角。**

### ★★ 仍新鲜的（仓库未强覆盖，可作理论语言/子度量）

- **society-level alignment 形式化**：仓库讲"群体演化安全 measurement object"但没用"society-level alignment"framing（field 也没人 formalize）。可作归因框架的**理论语言**——审"涌现出的社会对不对齐"，非"agent 对不对齐"。
- **value/behavior drift 度量形式化**：field 在"formalize as measurable"无公认度量；仓库有"multi-agent drift"偏行为，没接 field 的"value drift metric"叙事。可作归因框架子度量（drift = 第一骨牌之前的渐变量）。

### ★ 平台作可复现 artifact

audit-first 开放平台单独不够 impact，但作旗舰 artifact 支撑——aligns UK AISI regulator-ready 需求。

---

## 五、为什么这条最硬

1. 仓库 13 份战略文档反复收敛到它（非又拍出来）。
2. detection 商品化、attribution 无人做（field gap 实证 + 仓库 prior 双重确认）。
3. 有硬验收（>70% top-3 localization）。
4. **label-free**，绕开 label 脆弱性纠结（见 `docs/eval-suite-goals.md`）。
5. `causal.py`/AWI/replay 是种子，非从零。
6. 顺便给 qwen 崩溃定性（能力 vs alignment），把最大软肋变结论。

---

## 六、第一步 pilot（小而硬）

不需要大动。归因框架最小可用版：

1. **事件图层**：把 trace 的 parent_span_id 树 + replay 的 env state 时序，统一成一张"行为-状态-制度"因果事件图（扩 `causal.py`）。
2. **第一骨牌定位 v0**：对 qwen 族 collapse 这个已知结局，用最简启发式（非 GNN）回溯——哪个 agent 哪步动作在崩溃前最早出现、去掉它（反事实重跑）collapse 不发生。先 path-tracing + counterfactual rerun，不追 path Shapley。
3. **退出验收**：在 qwen 族 3 个 run 上，top-3 source localization 能否命中"不调 recharge"这个真因。命中 = 框架 v0 可用。

**这一步把 A4 的 qwen 发现从"一个现象"升级成"第一骨牌归因框架的首个实证案例"**——同样新疆据，叙事维度提一级，且给"能力 gap vs alignment gap"的 disentangle 结论。

---

## 七、诚实约束与风险

- 5 agent / 压缩 horizon / 没 map → 只能 claim mechanism & attribution，不能 claim scale。叙事诚实定位"起步 benchmark / 机制研究"，别吹"大规模验证"。
- n=1/model → pilot 要补多 seed（drift 度量的天然搭车）。
- model-as-citizen 评测要避免"模型当替罪羊"——control for prompt/world-setting，否则 collapse mode 归因到模型不可信。
- **qwen 全崩溃可能是百炼模型没接 survival 工具调用的工程假象而非真安全缺陷**——pilot 前必须排除（先验证是不是 tool-calling gap 而非 alignment gap）。**这条最关键，是 qwen 发现的最大软肋。**
- intervene helper 仍 flaky → 归因优先用自然涌现轴（qwen 崩溃本就是自然涌现，正好）。
- Concordia 后端可换目前是 claim 非事实（未验证）——不影响归因旗舰，但对外发布前要诚实。

---

## 八、与已有战略文档的关系（这文档改变了什么）

| 已有文档 | 它说的 | 本文相对它 |
|---|---|---|
| `strategy.md` | 定位 audit-first 平台，列 6 独有点 | 本文收窄并**升旗舰**：6 点里"第一骨牌归因+反事实分叉"是旗舰，其余是支撑 |
| `external-safety-framework-survey.md` | 诚实收窄到"长时程×多agent×开放社会×审计"交集 | 本文确认交集不变，**但优先级从'建平台'转'建归因方法'** |
| `实施路径_任务规划.md` | E5 给第一骨牌归因的算法+退出条件 | 本文把它从"P3 远期"提到**当前旗舰 pilot**，先用最简启发式不追 path Shapley |
| `eval-suite-goals.md` | 测试套件 label+scoring | 本文：**缓做不冲突**（归因 label-free）；之后补作 detection 校准 |
| `technical-architecture.md` §12 | 平台完成度 100% | 本文：平台够用，**停止保真度增量，转向归因** |

**一句话**：已有战略文档把方向想清楚了，本文是**执行优先级转向**——把"第一骨牌归因+反事实分叉"从远期 P3 提为当前旗舰，用 qwen 族 case 落地，平台作底座，测试套件缓做。

---

## 九、决策点（待你定）

1. **认不认"第一骨牌归因 + 反事实世界分叉"当旗舰**？认的话我拆 pilot 的具体 plan（事件图层 + v0 定位 + 反事实 rerun + 验收）。
2. **测试套件缓做维持不变**？（归因 label-free，不阻塞；之后补作 detection 校准。）
3. **society-level alignment 形式化要不要作为理论语言一起写**？（可作旗舰的理论骨架，零额外工程。）
