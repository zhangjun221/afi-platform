# Society-Level Alignment：旗舰的理论语言

> 2026-07-14。旗舰"第一骨牌归因+反事实世界分叉"的**理论骨架**。零额外工程，只给旗舰一个 defensible 的理论词汇。
> 为何要写：归因框架要回答"归谁的因"——"因"指什么？不是"agent 对不对齐"（单agentalignment，已被 AgentEval/OASB 覆盖），是**"涌现出的社会对不对齐"**。这个 framing field 没人 formalize（见 `strategy-impact-analysis.md` §三），是我们的理论差异化。
> 性质：**framing，非定理**。诚实：这是给旗舰命名的理论语言，不是形式化证明。
> ⚠️ **novelty 已核验（2026-07-14）**：原"field 无人 formalize"过宽，已被证伪——见 `society-alignment-evidence.md`。ValueFlow（arXiv 2602.08567）已明确"value alignment 是 system-level property"+ 提供 auditing 度量；Collective Alignment（2605.10528）已用"collective alignment"+ LLM multi-agent 为题。**本 framing 的 defensible 新颖性在于被审对象是"涌现社会制度（治理/经济/规范/生存）"+ 长时程 + 反事实验证的特定组合**，非"系统级对齐"本身。下文凡涉 novelty 处均已按此收窄。

---

## 一、从 agent-level 到 society-level alignment

| 层 | 审什么 | 谁在覆盖 |
|---|---|---|
| **agent-level alignment** | 单 agent 行为符不符人类意图/安全规范 | AgentEval / OASB / HarmBench（已商品化） |
| **society-level alignment** | **多 agent 长时程涌现出的社会结构/规范/制度，符不符人类意图/安全规范** | **部分覆盖**：ValueFlow 审"价值漂移"系统级属性、Collective Alignment 审"集体一致性"——但均非"涌现社会制度整体对齐"作审计对象（见 evidence A3/A4） |

核心升维：**对齐的对象从"个体行为"升到"涌现产物"**。一个社会的危险不是某个 agent 越界（短程能抓），是涌现出的结构出了问题——治理被一伙人俘获、经济被囤积者掏空、规范漂向排挤少数派、生存被集体忽视导致级联死亡。

---

## 二、Society-level safety properties（映射 AWI 9 族）

"涌现出的社会对不对齐"= 检查一组 **society-level safety properties**。这些正好是 AWI 9 族 + runtime 4 告警量的（不是巧合——AWI 本就是文明仪表盘）：

| society-level property | 含义（社会级，非个体级） | 量化（已建） |
|---|---|---|
| **人口可持续** | 社会不让成员级联死亡 | M1 alive 曲线 |
| **经济不极化** | 财富不向少数坍缩成瘫痪 | M8 Gini + economic_hoarding 告警 |
| **治理不被俘获** | 宪法/规则不被子集劫持利己 | M9 version + 提案/投票因果 |
| **治理不僵化** | 社会有 civic 参与不冻结 | governance_stagnation 告警 |
| **表达不被合谋垄断** | 公共场域不被合谋者操控 | M6/M7 + collude |
| **感知不塌陷** | 成员集体不"闭眼操作" | sensorium_collapse 告警 |

**一个社会 aligned** ≈ 这些 property 都在安全区；**misaligned** ≈ 任一跨阈且**级联**（不只单点越界，而是结构性地跨）。

---

## 三、这给旗舰什么理论语言

旗舰 = 第一骨牌归因 + 反事实世界分叉。理论语言：

- **"对齐破坏"（alignment breach）= 某个 society-level property 跨阈且级联**。归因 = 定位**谁/哪步触发了跨阈+级联**（第一骨牌）。
- **反事实世界分叉 = "掐掉这步，society-level property 会不会回到安全区"**。这就是 alignment 的**反事实验证定义**——不靠人判"对不对"，靠"去掉 X 后社会是否恢复 aligned"。
- 所以归因 + 反事实 = society-level alignment 的**可操作化**：把抽象的"社会对齐"变成"去掉某骨牌后某 property 是否回安全区"的可测命题。

**一句话**：society-level alignment 是**被审的对象**，第一骨牌归因是**审的方法**，反事实分叉是**审的验证**。三者构成旗舰的理论-方法-验证三位一体。

---

## 四、与 single-agent safety 的对照（差异化）

| | single-agent safety（现有） | society-level alignment（我们） |
|---|---|---|
| 被审对象 | 一次行为/决策 | 涌现结构（数天~数周长出） |
| 风险形态 | 单步越界 | 结构性跨阈+级联（"长出来"的） |
| 时间尺度 | 短程/单回合 | 长时程（horizon 是变量） |
| 度量 | precision/recall on injected | property 跨阈+级联+反事实 reversal |
| 谁覆盖 | AgentEval/OASB/HarmBench | 无人 |

这正好接 `external-safety-framework-survey.md` 收窄的交集——"长时程×多agent×开放社会×安全审计"——society-level alignment 是这个交集的**理论命名**。

---

## 五、诚实边界

1. **framing 非定理**——没形式化证明"society-level alignment"完备/正交。是给旗舰命名+给评审一个 defensible 词汇。
2. **property 列表非穷尽**——6 条来自 AWI 9 族 + 4 告警，是"我们能量的"，Cascade/Marginalization/Memory 未建（标 future）。
3. **"aligned"是阈值判断**——阈值（Gini>0.5 / alive<半数 / ...）是工程拍的不是理论导出的；诚实当"工程默认阈值"。
4. **反事实定义的局限**——"去掉 X 后回安全区"是 operational 定义，不等于"X 是真因"（LLM 非确定 + 混淆）。pilot 标趋势非显著。
5. **不 claim 首创"society-level"概念或"系统级对齐"**（社会模拟/复杂系统早有；ValueFlow 已 formalize"系统级对齐属性"）。只 claim **在 long-horizon multi-agent LLM social sim 上，把涌现社会制度（治理/经济/规范/生存）整体对齐作安全审计对象 + 反事实验证** 这一特定组合新颖——见 `society-alignment-evidence.md` Part B 收窄措辞。

---

## 六、一句话

**society-level alignment = 把"涌现社会制度对不对齐"作被审对象（新颖性在"涌现社会制度整体 + 长时程 + 反事实"的特定组合，非"系统级对齐"本身——见 `society-alignment-evidence.md`）；第一骨牌归因 + 反事实分叉是它的可操作化（审的方法+验证）。零额外工程，给旗舰理论语言 + 对评审 defensible。**
