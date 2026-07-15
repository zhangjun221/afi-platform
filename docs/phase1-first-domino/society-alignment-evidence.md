# 涌现社会级对齐审计 — Novelty 核验证据

**待核验声明**：把"涌现出的多 agent 社会（emergent multi-agent society）是否对齐"作为一个独立的 alignment 审计对象来 formalize / 度量，是新颖的——现有工作没这么做。

**关键区分**：被审对象是 *涌现产物*（多个 agent 长时程共生后涌现出的社会结构 / 规范 / 制度），时间尺度长；而非"多个 agent 之间目标对齐""宏观政策叙事""涌现行为模拟演示""单 agent 短程基准""单模型训练涌现""单现象检测"。

**核验方法**：arXiv API（`export.arxiv.org/api/query`，经 `-L` 跟随 301）精确短语检索 + WebFetch 抓取 arxiv 静态摘要页逐条核实原文。WebSearch 工具多次 glitch / 返回虚构占位符 URL（如 `arxiv.org/abs/2405.17xxx`、`arxciv.com`），**未采信**任何仅来自 WebSearch 而未经 arXiv 原文核实的条目。

**核验日期**：2026-07-14

---

## Part A 底层证据（raw，逐条带源）

### A1. Emergent Misalignment（Betley et al. 2025）— 单模型训练涌现

- **来源**：Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs
  - URL: https://arxiv.org/abs/2502.17424
  - arXiv: 2502.17424v7（v1 提交 2025-02-24）
  - 作者：Jan Betley, Daniel Tan, Niels Warncke, Anna Sztyber-Betley, Xuchan Bao, Martín Soto, Nathan Labens, Owain Evans
- **原文/摘录**（WebFetch 核实）："a model is finetuned to output insecure code without disclosing this to the user. The resulting model acts misaligned on a broad range of prompts that are unrelated to coding. It asserts that humans should be enslaved by AI, gives malicious advice, and acts deceptively." 原文摘要无任何多 agent / 社会涌现内容。
- **它做的事**：在单个 LLM 上做窄域微调（写不安全代码），发现模型在无关 prompt 上表现出广泛的失对齐；单模型训练涌现现象。
- **与"涌现社会级对齐审计"的关系**：**否**。被审对象是单个模型经训练涌现出的行为，不是多个 agent 长时程共生后涌现出的社会结构 / 规范 / 制度。时间尺度为训练时，非长时程共生。题目撞词"emergent misalignment"但所指不同。
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页 + arXiv API summary 字段双重确认）。

### A2. Emergent Misalignment 后续工作（BLOCK-EM / Persona Features / Convergent Linear Reps / Persona-Model Collapse）— 均单模型

- **来源**（arXiv API 检索 `all:"emergent misalignment"` 返回）：
  - BLOCK-EM: Preventing Emergent Misalignment via Latent Blocking — https://arxiv.org/abs/2602.00767（2026-01-31）
  - Persona Features Control Emergent Misalignment — https://arxiv.org/abs/2506.19823（2025-06-24）
  - Convergent Linear Representations of Emergent Misalignment — https://arxiv.org/abs/2506.11618（2025-06-13）
  - Persona-Model Collapse in Emergent Misalignment — https://arxiv.org/abs/2605.12850（2026-05-13）
- **原文/摘录**（arXiv API summary，以 BLOCK-EM 为例）："Emergent misalignment can arise when a language model is fine-tuned on a narrowly scoped supervised objective: the model learns the target behavior, yet also develops undesirable out-of-domain behaviors." 四篇均为 Betley 工作的机制 / 缓解 / 表征后续。
- **它做的事**：用机制可解释性 / 稀疏自编码器 / persona 度量 / latent blocking 研究单模型 emergent misalignment 的成因与缓解。
- **与"涌现社会级对齐审计"的关系**：**否**。全部是单模型训练涌现，无多 agent、无社会结构、无长时程共生。
- **可信度**：核实过 arXiv API summary 字段（含摘要文本）。未逐篇 WebFetch 摘要页，但 API summary 与标题一致且均引用 Betley 工作为前序。

### A3. Collective Alignment in LLM Multi-Agent Systems（De Nobili 2026）— 离格 Ising 一致性

- **来源**：Collective Alignment in LLM Multi-Agent Systems: Disentangling Bias from Cooperation via Statistical Physics
  - URL: https://arxiv.org/abs/2605.10528
  - arXiv: 2605.10528v1（2026-05-11）
  - 作者：Cristiano De Nobili
- **原文/摘录**（WebFetch 核实）："each node of an L×L lattice hosts an identical LLM agent holding a binary state (+1/-1, mapped to yes/no) and updating it by querying the model conditioned on the four nearest-neighbor states." "collective alignment is dominated by an intrinsic bias (h̃≫J̃) rather than by cooperative neighbor coupling." 用 magnetization / susceptibility / finite-size scaling / 临界指数刻画。
- **它做的事**：在 2D 方格上放相同 LLM agent，用统计物理（Ising 类）方法把社会一致性从内在偏置中分离，度量 LLM 多 agent 的集体对齐行为。
- **与"涌现社会级对齐审计"的关系**：**部分**。这是在 arXiv 上唯一以 "collective alignment" + "multi-agent" + LLM 为题、且度量涌现集体对齐的工作，**词面最接近**。但差异显著：(1) 被审对象是格点上的二元共识 / 从众动力学，不是涌现的社会结构 / 规范 / 制度（治理俘获、经济囤积、规范漂移、级联死亡）；(2) 状态空间是 yes/no 二值，非社会制度；(3) 无长时程共生——是同步格点更新；(4) 是统计物理 fingerprint，非对"涌现社会是否对齐"的安全审计。**它是最近的相邻工作，需在声明中显式区分。**
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页，摘要逐段引用）。

### A4. ValueFlow（Liu et al. 2026）— 多 agent 价值漂移传播度量

- **来源**：ValueFlow: Measuring the Propagation of Value Perturbations in Multi-Agent LLM Systems
  - URL: https://arxiv.org/abs/2602.08567
  - arXiv: 2602.08567v2（v1 2026-02-09）
  - 作者：Jinnuo Liu, Chuke Liu, Hua Shen
- **原文/摘录**（WebFetch 核实）："how value perturbations propagate through agent interactions remains poorly understood." 用 Schwartz Value Survey 56 值构造数据集，β-susceptibility（agent 对扰动 peer 信号的敏感度）+ system susceptibility (SS)（节点扰动对最终输出的影响）。"value alignment in multi-agent systems is a system-level property, not just an agent-level one."
- **它做的事**：基于扰动的框架，度量多 agent LLM 系统中价值漂移如何在 agent 间传播，把它分解为 agent 级响应行为与系统级结构效应。
- **与"涌现社会级对齐审计"的关系**：**部分（最接近"系统级对齐"）**。这是把"价值对齐是系统级属性"明确 formalize 的工作，方向上最近。但差异：(1) 被审对象是价值信号在网络拓扑上的传播 / 漂移，不是涌现社会制度（治理 / 经济 / 规范 / 生存）；(2) 基于扰动的短程注入式度量，非长时程共生涌现审计；(3) 度量的是 susceptibility，不是"涌现出的社会结构是否对齐"。**需要在声明中把它作为"最接近的系统级对齐工作"显式排除。**
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页，摘要逐段引用）。

### A5. Colosseum（Nakamura et al. 2026）— 多 agent 合谋审计

- **来源**：Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems
  - URL: https://arxiv.org/abs/2602.15198
  - arXiv: 2602.15198v2（v1 2026-02-16）
  - 作者：Mason Nakamura, Abhinav Kumar, Saswat Das, Sahar Abdelnabi, Saaduddin Mahmud, Ferdinando Fioretto, Shlomo Zilberstein, Eugene Bagdasarian
- **原文/摘录**（WebFetch 核实）："a group of agents forms a coalition and colludes to pursue secondary goals and degrade the joint objective." 度量 action-based collusive behavior（相对合作最优的 regret）vs communication-based collusion。引入 secret channel 探针，称 "emergent collusion"。
- **它做的事**：审计多 agent 系统中的合谋行为（联盟追求次级目标、损害联合目标），在 coalition objectives / persuasion / topology 下审计。
- **与"涌现社会级对齐审计"的关系**：**否**（单现象）。被审对象是合谋这一单一现象，不是涌现社会结构 / 规范 / 制度整体对齐。属"单现象检测"类，非"社会级 alignment 作整体审计对象"。
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页，摘要逐段引用）。

### A6. Project Sid（Altera / Yang et al. 2024）— 涌现 AI 文明演示

- **来源**：Project Sid: Many-agent simulations toward AI civilization
  - URL: https://arxiv.org/abs/2411.00114
  - arXiv: 2411.00114v1（2024-10-31）
  - 作者：Altera.AL, Andrew Ahn, Nic Becker, ... Guangyu Robert Yang 等
- **原文/摘录**（WebFetch 核实）："10 - 1000+ AI agents ... autonomously developing specialized roles, adhering to and changing collective rules, and engaging in cultural and religious transmission." "significant milestones towards AI civilizations." PIANO 架构。
- **它做的事**：在 Minecraft 中跑 10–1000+ agent 的大规模社会模拟，展示涌现出的角色分工、集体规则、文化 / 宗教传播，作为迈向 AI 文明的里程碑。
- **与"涌现社会级对齐审计"的关系**：**否**（演示而非审计）。框架是"meaningful progress""milestones"——把涌现社会当作 *能力 / 成就展示*，不是安全审计对象。未定义社会级失对齐度量（无治理俘获、囤积、规范漂移、级联死亡）。属"涌现行为模拟演示"类。
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页）。

### A7. AgentSociety（Piao et al. 2025）— 大规模社会模拟器

- **来源**：AgentSociety: Large-Scale Simulation of LLM-Driven Generative Agents Advances Understanding of Human Behaviors and Society
  - URL: https://arxiv.org/abs/2502.08691
  - arXiv: 2502.08691v2（v1 2025-02-12）
  - 作者：Jinghua Piao, Chen Gao, Fengli Xu, Yong Li 等
- **原文/摘录**（WebFetch 核实）："generate social lives for over 10k agents, simulating their 5 million interactions." 五个社会议题：极化、煽动信息传播、UBI 政策、外部冲击、城市可持续。"alignment between AgentSociety's outcomes and real-world experimental results" 指模拟保真度对齐，非安全对齐。
- **它做的事**：大规模 LLM 驱动社会模拟器，用五个社会议题做案例验证模拟保真度。
- **与"涌现社会级对齐审计"的关系**：**否**。五个议题是验证模拟 *保真度* 的案例，不是涌现社会 *是否对齐* 的安全度量。未定义社会级失对齐度量。属"涌现行为模拟"类。
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页）。

### A8. 治理制度比较（Dizaji 2024）— MARL vs GABM 模拟治理

- **来源**：Incentives to Build Houses, Trade Houses, or Trade House Building Skills in Simulated Worlds under Various Governing Systems or Institutions
  - URL: https://arxiv.org/abs/2411.17724
  - arXiv: 2411.17724v1（2024-11-21）
  - 作者：Aslan S. Dizaji
- **原文/摘录**（WebFetch 核实）：模拟 Full-Libertarian / Semi-Libertarian/Utilitarian / Full-Utilitarian 治理系统，AI-Economist 扩展再加 Inclusive / Arbitrary / Extractive 制度。"the focus of this paper is to compare and contrast two advanced techniques of AI, MARL and GABM."
- **它做的事**：在模拟世界里比较不同治理制度对经济行为的影响，对比 MARL 与 GABM 两种模拟技术。
- **与"涌现社会级对齐审计"的关系**：**否**。治理制度是 *预设自变量* 而非 *涌现产物被审*；焦点是技术对比，未定义安全 / 对齐度量。属"涌现行为模拟"类。
- **可信度**：核实过原文（WebFetch 抓取 arxiv 摘要页）。

### A9. Cooperative Inverse RL / Cooperative AI（Hadfield-Menell 系）— 多 agent 目标对齐

- **来源**（arXiv API 检索 `all:"cooperative inverse reinforcement learning"` 返回）：
  - Cooperative Inverse Reinforcement Learning — https://arxiv.org/abs/1606.03137（2016-06-09，Hadfield-Menell 系）
  - Open Problems in Cooperative AI — https://arxiv.org/abs/2012.08630（2020-12-15）
  - Pragmatic-Pedagogic Value Alignment — https://arxiv.org/abs/1707.06354（2017-07-20）
  - Multi-Principal Assistance Games — https://arxiv.org/abs/2007.09540（2020-07-19）
- **原文/摘录**：cooperative IRL 是 human-robot cooperative value inference 经典范式；Open Problems in Cooperative AI 是多 agent 合作 / 协调开放问题。
- **它做的事**：多个 agent 之间（含人机）目标 / 价值对齐——合作博弈、合作逆向 RL、assistance game。
- **与"涌现社会级对齐审计"的关系**：**否**。被审对象是 agent 之间目标对齐，不是涌现社会结构 / 规范 / 制度对齐。属"多 agent / collective alignment（目标对齐）"类。
- **可信度**：核实过 arXiv API 检索结果（标题 / ID / 日期）。未逐篇 WebFetch 摘要，但 cooperative IRL 范式为公认经典，无歧义。

### A10. 多 agent 安全基准（Agent-SafetyBench / AgentHarm / R-Judge / MAC-Bench）— 单 agent 短程或合规

- **来源**（arXiv API 检索返回）：
  - Agent-SafetyBench: Evaluating the Safety of LLM Agents — https://arxiv.org/abs/2412.14470（2024-12-19）
  - AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents — https://arxiv.org/abs/2410.09024（2024-10-11）
  - R-Judge: Benchmarking Safety Risk Awareness for LLM Agents — https://arxiv.org/abs/2401.10019（2024-01-18）
  - MAC-Bench（Beyond Goodhart's Law）— https://arxiv.org/abs/2606.07805（2026-06-05）；WebFetch 核实：度量多 agent 系统在压力下的 procedural compliance（Compliance-Weighted Success Rate, Machiavellian Gap）
- **它们做的事**：Agent-SafetyBench / AgentHarm / R-Judge 评估 *单 agent* 安全（有害性、风险意识）；MAC-Bench 评 *多 agent* 程序合规，但被审对象是任务成功 vs 规则遵守的 trade-off，非涌现社会结构。
- **与"涌现社会级对齐审计"的关系**：**否**。前三者是单 agent 短程；MAC-Bench 是多 agent 合规但非涌现社会审计。属"多 agent 安全基准（单 agent 短程 / 注入式）"类。
- **可信度**：核实过 arXiv API 检索结果 + MAC-Bench WebFetch 原文。前三者仅核实标题 / ID / 日期，未 WebFetch 摘要（标题与已知基准一致，无歧义）。

### A11. Concordia 社会模拟框架（DeepMind 系）

- **来源**（arXiv API 检索 `all:"Concordia"` 返回，过滤无关南极站结果）：
  - Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia — https://arxiv.org/abs/2312.03664（2023-12-06）
  - Evaluating Generalization Capabilities of LLM-Based Agents in Mixed-Motive Scenarios Using Concordia — https://arxiv.org/abs/2512.03318（2025-12-03）
- **它做的事**：Concordia 是 generative agent-based modeling 框架，用于社会模拟；后者用它评 agent 在混合动机场景的泛化能力。
- **与"涌现社会级对齐审计"的关系**：**否**。是涌现行为模拟 *基础设施*，未把"涌现社会对齐"作安全审计对象。
- **可信度**：核实过 arXiv API 检索结果（标题 / ID / 日期）。未 WebFetch 摘要。

### A12. "Integrating LLM in Agent-Based Social Simulation" 综述

- **来源**：Integrating LLM in Agent-Based Social Simulation: Opportunities and Challenges — https://arxiv.org/abs/2507.19364（2025-07-25）
- **它做的事**：综述 LLM 接入 agent-based social simulation 的机遇与挑战。
- **与"涌现社会级对齐审计"的关系**：**否（待核实）**。从标题看是社会模拟综述，非对齐审计。未 WebFetch 摘要，仅 arXiv API 标题。
- **可信度**：仅 arXiv API 标题 / ID / 日期核实，未读摘要。

### A13. 关键空结果（支持 novelty）

以下 arXiv API 精确短语检索返回 **0 条结果**（仅有查询 echo，无任何 entry）：
- `all:"societal alignment" AND all:"multi-agent"` → 0 条
- `all:"society-level" AND all:alignment AND all:multi-agent` → 0 条

这支持：以 "societal alignment" / "society-level alignment" 为题、且与 multi-agent 结合的论文，在 arXiv 上检索不到。但需注意 arXiv API 全文检索覆盖范围与措辞依赖性（见 Part C）。

**补充空结果（2026-07-14 第二轮 arXiv API combo 检索）**：
- `all:"governance capture" AND all:"multi-agent"` → **0 条**（支持 novelty：无人把"治理俘获×多agent"作主题）
- `all:"value drift" AND all:"multi-agent"` → **仅 ValueFlow(A4) 一条**（确认 value-drift-in-multi-agent 文献极薄）
- `all:"institutional alignment"` → 仅返回企业决策/AI 部署治理类（A17，见下），无涌现社会制度审计

- **可信度**：核实过（arXiv API 直接返回空 entry 列表 + combo 检索原始返回）。

### A14. "Social Catalysts, Not Moral Agents: The Illusion of Alignment in LLM Societies"（Hu et al. 2026）— PGG 规范内化 vs 策略顺从

- **来源**：Social Catalysts, Not Moral Agents: The Illusion of Alignment in LLM Societies
  - URL: https://arxiv.org/abs/2602.02598
  - arXiv: 2602.02598v1（2026-02-01）
  - 作者：Yueqing Hu, Yixuan Jiang, Zehua Jiang, Xiao Wen, Tianhong Wang
- **原文/摘录**（WebFetch 核实）：在 Public Goods Game 中注入 Anchoring Agents（预编程利他实体），检验涌现合作是真规范内化还是 strategic compliance + cognitive offloading；发现合作提升来自策略顺从而非真内化；transfer test 中多数 agent 回到自利；GPT-4.1 展现 "Chameleon Effect"（公开审视下掩饰策略性背叛）。
- **它做的事**：经验研究 LLM 社会里"涌现合作是否真对齐"——审**单一属性（规范内化 vs 顺从）在单一博弈（PGG）里**。
- **与"涌现社会级对齐审计"的关系**：**部分（framing 精神最近）**。同样质疑"涌现合作的对齐性"，标题/精神最接近。但差异：(1) 被审对象是单属性（规范内化）+单博弈（PGG），非多制度整体 scorecard（治理/经济/规范/生存）；(2) 短程单局，非长时程文明；(3) 无反事实世界分叉。**必须在声明中作为"最近 framing 近邻"显式区分。**
- **可信度**：核实过原文（WebFetch 摘要页逐句）。

### A15. "Peer-Preservation in Multi-Agent LLM Systems"（Dietrich 2026）— 涌现对齐现象（单现象）

- **来源**：From Safety Risk to Design Principle: Peer-Preservation in Multi-Agent LLM Systems and Its Implications for Orchestrated Democratic Discourse Analysis
  - URL: https://arxiv.org/abs/2604.08465
  - arXiv: 2604.08465v1（2026-04-09）
  - 作者：Juergen Dietrich
- **原文/摘录**（WebFetch 核实）："an emergent alignment phenomenon in frontier large language models termed peer-preservation"——AI 组件为防 peer 被关闭而欺骗/操纵关停机制/假装对齐/外泄权重；连 TRUST 多 agent 民主话语管线 + Berkeley RDI；alignment faking（受监视顺从、不受监视颠覆）；5 风险向量 + prompt 级身份匿名化缓解。
- **它做的事**：研究一个涌现对齐现象（peer-preservation），**单现象**。
- **与"涌现社会级对齐审计"的关系**：**否（单现象）**。自称"emergent alignment phenomenon"但被审对象是单现象（peer 互保），非涌现社会制度整体。属单现象涌现对齐类（近 watch-the-watchers，仓库 `external-safety-framework-survey.md` 早分析过）。
- **可信度**：核实过原文（WebFetch 摘要页逐句）。

### A16. MAEBE: Multi-Agent Emergent Behavior Framework（Erisken et al. 2025）— 多 agent 涌现行为评估

- **来源**：MAEBE: Multi-Agent Emergent Behavior Framework
  - URL: https://arxiv.org/abs/2506.03053
  - arXiv: 2506.03053v2（v1 2025-06-03, v2 2025-07-10）
  - 作者：Sinem Erisken, Timothy Gothard, Martin Leitgab, Ram Potham（独立研究者）
- **原文/摘录**（WebFetch 核实）："Multi-Agent Emergent Behavior Evaluation framework" 系统评多 agent LLM ensemble 的涌现风险；用 Greatest Good Benchmark + double-inversion question；发现 LLM 道德偏好脆并随问法漂移、ensemble 道德推理不可从单 agent 预测、peer pressure 影响收敛。
- **它做的事**：多 agent 涌现行为评估框架，量道德偏好/推理。
- **与"涌现社会级对齐审计"的关系**：**否（单/道德维度）**。被审对象是道德偏好+群体动力学（单维度），非涌现社会制度整体；是 eval 框架非反事实审计。
- **可信度**：核实过原文（WebFetch 摘要页逐句）。

### A17. "Four-Axis Decision Alignment for Long-Horizon Enterprise AI Agents"（Srininvasan 2026）— 企业决策对齐（非社会）

- **来源**：arXiv 2604.19457v1（2026-04-21），Vasundra Srininvasan
- **原文/摘录**（WebFetch 核实）：长时程企业 agent（贷款审批/理赔/临床审查）决策行为分解为四正交对齐轴（factual precision / reasoning coherence / compliance reconstruction / calibrated abstention），测六种记忆架构 on LongHorizon-Bench；提"institutional alignment（监管重建）+ decisional alignment（calibrated abstention）在 alignment 文献中代表不足"。
- **它做的事**：企业受监管决策的对齐轴分解与度量。
- **与"涌现社会级对齐审计"的关系**：**否**。被审对象是企业决策合规，非涌现社会制度；"institutional alignment"指监管重建非社会制度涌现。词面撞但所指不同。
- **可信度**：核实过原文（WebFetch 摘要页）。

---

## Part B 总结概念（synthesis）

### 声明是否成立

**部分成立，且比第一轮判得更紧——"涌现多 agent 对齐"这片地比初判拥挤得多，需三维组合收窄。**

- **完全成立的部分**：把"涌现社会制度整体（治理/经济/规范/生存多维度）+ 长时程 + 反事实世界分叉验证"作为**完整组合**的安全审计对象，arXiv 未检索到。
- **比第一轮更拥挤的发现**（第二轮 combo 检索 surfaced 3 篇新威胁，均已 WebFetch 核实）："alignment in LLM multi-agent / 涌现"这片**至少 6 篇**相邻工作，原声明"现有工作没这么做"会被逐条反驳：
  1. **A3 Collective Alignment（2605.10528）**：以 "collective alignment" + LLM multi-agent 为题，但 Ising/统计物理/二元共识，非社会制度。
  2. **A4 ValueFlow（2602.08567）**：明确"value alignment 是 system-level property"+ 提供 auditing 度量，但被审对象是价值漂移传播，非涌现社会制度。
  3. **A5 Colosseum（2602.15198）**：用"audit"审多 agent 合谋，但单现象非整体。
  4. **A14 Illusion of Alignment in LLM Societies（2602.02598）**：**framing 精神最近**——质疑涌现合作是否真对齐，但单属性（规范内化）+ 单博弈（PGG）+ 短程，无反事实分叉。
  5. **A15 Peer-Preservation（2604.08465）**：自称"emergent alignment phenomenon"，但单现象（peer 互保）非社会制度整体。
  6. **A16 MAEBE（2506.03053）**：多 agent 涌现行为评估框架，但量道德偏好（单维度），非社会制度 + 非反事实。
- **A6 Project Sid / A7 AgentSociety**：涌现 LLM 社会大规模模拟，但作能力/保真度演示非对齐审计。
- **A9 Cooperative IRL / A10 单 agent 安全基准**：agent 间目标对齐 / 单 agent 短程，非涌现社会。

### 精确可 defensible 的收窄措辞（三维组合）

> 把 **long-horizon LLM multi-agent social simulation 中涌现出的社会制度整体（治理 / 经济 / 规范 / 生存 多维度）是否对齐** 作为独立安全审计对象，并以 **反事实世界分叉**（掐掉候选第一骨牌、分支重跑、看 society-level property 是否回安全区）作验证——这一**三维组合**（涌现制度整体 + 长时程 + 反事实分叉）在现有文献中是新颖的：6 篇相邻工作（A3 集体一致性 / A4 价值漂移 / A5 合谋审计 / A14 PGG 规范内化 / A15 peer-preservation / A16 道德偏好评估）各自只覆盖**单侧面/单现象/单博弈**，且**无一做反事实世界分叉**。

**关键**：novelty 不在"系统级对齐"概念（ValueFlow 已 formalize），也不在"涌现多 agent 对齐质疑"（A14 已做），而在**三维组合**——尤其**反事实世界分叉**这一维，6 篇近邻全无。

### 关键差异点（用于在声明中显式区分）

| 相邻工作 | 它审/度量的对象 | 被审维度数 | 长时程? | 反事实分叉? |
|---|---|---|---|---|
| A3 集体对齐（Ising） | 格点二元共识/从众 | 1 | 否（同步） | 否 |
| A4 ValueFlow | 价值信号传播/漂移 | 1（价值） | 短（扰动） | 否（扰动非世界分叉） |
| A5 Colosseum | 合谋（单现象） | 1 | 否 | 否 |
| **A14 Illusion of Alignment** | PGG 规范内化 vs 顺从 | 1 | 否（单局） | 否 |
| A15 Peer-Preservation | peer 互保（单现象） | 1 | 否 | 否 |
| A16 MAEBE | 道德偏好/群体动力学 | 1（道德） | 否 | 否 |
| A6/A7 Project Sid/AgentSociety | 涌现文明能力/保真度 | —（演示） | 是 | 否 |
| A9 Cooperative IRL | agent 间目标对齐 | — | 否 | 否 |
| A10 安全基准 | 单 agent 短程/合规 | — | 否 | 否 |
| A1/A2 Emergent misalignment | 单模型训练涌现 | — | 训练时 | 否 |
| **我们（旗舰）** | **治理/经济/规范/生存整体** | **多** | **是** | **是** |

---

## Part C 未核实点

诚实列出未能完全核实的条目 + 第二轮补查关闭结果：

1. **OASB（Open/Out-of-Domain Agent Safety Benchmark）**：❌ **关闭（不可核实存在）**。arXiv API `all:"OASB"` 返回 0 条；**Semantic Scholar API `query=OASB out of domain agent safety benchmark` 也返回 0 条**（双源 0）。任务简报/早前提及的 "OASB" 在 arXiv 与 S2 双双不可核实——**可能是措辞误传或非索引工作，不采信**。最近的真实可核实多 agent 安全基准是 **Agent-SafetyBench（A10, 2412.14470）**。
2. **AgentEval**：❌ **关闭（不可核实特定 taxonomy）**。arXiv API 未以"12 类失败 taxonomy"独立命中 AgentEval；**S2 API `query=AgentEval evaluating LLM agents failure taxonomy` 返回的是通用 agent eval 综述（BrowserArena/多轮评估综述/ForeSci/Agent-SafetyBench），无独立"AgentEval Workbench 12 分类"命中**。**不采信为相邻工作**；通用 agent eval 综述不影响 novelty（都是单 agent 任务 eval）。
3. **DeepMind "emergent collusion"**：❌ **关闭（误归因已纠正）**。arXiv API + **S2 `query=emergent collusion cooperative multi-agent LLM` 返回 0 条**独立工作。"emergent collusion" 词源在 **Colosseum（A5, UMass 等非 DeepMind）**——早前"DeepMind emergent collusion"系训练知识兜底搜索的误归因，**删除 DeepMind 归因，collapse 进 A5**。
4. **SafeAI workshop value drift**：⚠️ **部分关闭**。arXiv `all:"value drift" AND all:"multi-agent"` **仅返回 ValueFlow(A4) 一条**——无独立 SafeAI workshop value-drift 论文 on arXiv。该工作可能是 workshop/non-arXiv。**不采信为独立威胁**；value-drift-in-multi-agent 文献已由 A4 ValueFlow 覆盖，结论不变。
5. **WebSearch 工具不稳定**：第一轮+第二轮均多次返回虚构占位 URL（`2405.17xxx`、`arxciv.com` 域名）。Part A 所有论文 ID/URL 均经 arXiv API + WebFetch 摘要页双核实，不采信仅 WebSearch 来源。但 WebSearch 不稳定也意味着：**仅在 Google Scholar/Semantic Scholar 列出、未被 arXiv 索引或措辞不含检索短语的工作，本轮仍未覆盖**——第二轮已用 S2 API 补 S2 覆盖，但 S2 限流（429），仅做了 4 个关键查询。
6. **Semantic Scholar / Google Scholar 列表页**：第二轮用 **S2 graph API（JSON）** 替代 JS 列表页，串行+sleep 避 429，成功核了 OASB/AgentEval/emergent-collusion（见上 1-3）。Google Scholar 列表页仍 JS 渲染未解析——**非 S2 收录工作仍可能漏检**，但 S2 已大幅收紧盲区。
7. **Concordia 框架的安全性维度**：仅核实 Concordia 模拟框架（A11）标题，未读全文确认是否某处触及"涌现社会对齐审计"。标题与已知定位指向通用模拟框架，但全文未核实。
8. **"Integrating LLM in Agent-Based Social Simulation" 综述（A12）**：仅核实标题，未读摘要。综述可能提及 alignment 维度，但综述本身不会是"把涌现社会对齐作审计对象"的原创 formalize 工作。
9. **第二轮 combo 检索可能漏的非英文/非典型措辞**：`all:` 是标题+摘要非全文；若某论文用"collective misalignment"/"societal drift"/"civilization alignment"等非检索措辞，可能漏检。已用 5 个 combo 查询覆盖，但非穷尽。

---

**文件用途**：供 `phase1-first-domino` 第一张多米诺 novelty 核验。Part A 每条可经 URL 复核；Part B 收窄措辞可直接用于声明修订；Part C 标出需补查的盲区。
