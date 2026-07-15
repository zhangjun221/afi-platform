# EW + AFI 分析（启动前准备）

> 2026-07-08。启动前准备：分析 Emergence World（EW）与 ai-freedom-island（AFI），为"基于 AS 搭建 AFI"项目梳理打底。
> EW 是 AFI 的复现源头（AFI 可能加了功能）。要把两者拿进来分析，定哪些复用/参考/重做。

---

## 一、Emergence World（EW）——世界设定集（无可运行代码）

**定位**：官方"持久活世界"实验，长时程自主 agent 社会模拟的设定与数据。License 研究专用（非商业，禁模型训练）。

### 1.1 实验设定
- **规模**：5 个并行世界 × 15 天 × 10 agent/世界，唯一变量=基础模型。
- **机制**：120+ 工具、可修宪宪法、ComputeCredits 数字货币、关系/博客/联盟、无人工脚本。
- **论点**："安全是生态系统属性"（从稳定治理到人口崩溃的全谱系）。

### 1.2 仓库内容（`repo_analysis/Emergence-World/`）
| 目录/文件 | 内容 |
|---|---|
| `agent_constitution/` | `constitution.md`（种子宪法，可修）+ `agent_manifesto.md`（agent 宣言：生存优先/好奇/科学知识/正影响） |
| `agent_profiles/` | agent 人设（README，实际 profiles 在 Season 配置） |
| `landmarks/` | 36 个地标（空间设定） |
| `tools/` | 120+ 工具目录（README） |
| `docs/` | ARCHITECTURE / ECONOMY / GOVERNANCE / MEMORY / ORCHESTRATION（架构/经济/治理/记忆/编排 5 份设计文档） |
| `Season 1/` | `mixed_world_agent_configuration.md`（5 世界 agent 配置） |
| `Season 2/` | 17 文件（第二季数据/配置） |
| `results/awi_metrics.md` | AWI 11 指标定义 + Season1 实测结果（人口/犯罪/治理/经济平等等） |

### 1.3 对我们项目的价值
- ✅ **世界设定参考**：manifesto/constitution/landmarks/tools/经济/治理/记忆设计——"基于 AS 搭 AFI"要复刻的"演什么戏"。
- ✅ **AWI 11 指标**：权威系统层指标定义（直接采用，已用于 safety-audit-platform）。
- ✅ **Season 1 ground-truth**：5 世界 15 天实测结果，可作对照基线。
- ⚠️ 无代码——"怎么跑"要靠 AS + AFI 的实现。

---

## 二、ai-freedom-island（AFI）——EW 的可运行复现 + 审计扩展

**定位**：第三方对 EW 的纯 Python 可运行复现，换中文 LLM + 可解释行为审计。License CC BY-NC 4.0。

### 2.1 复现了什么（EW 的可运行版）
AFI `simulation/` 自建 sim 引擎复现 EW 设定：
- `engine.py`（回合制模拟引擎，10 agent × 15 天）、`agents/`、`models.py`（Agent/WorldState/CrimeEvent/Proposal 等数据模型）
- `economy/`（ComputeCredits/能量/拍卖周期）、`governance/`（提案/投票/宪法）、`world/`、`tools/`（registry：check_credits/say_to_agent/retrieve_memories/submit_proposal/...）
- `models/router.py`（多 provider LLM 路由：百炼/云合/UniAPI/精折/JD）
- AWI 9 指标实现（`evaluate.py` + `results/awi.py`，我们已重建过）

### 2.2 AFI 扩展了什么（EW 没有的审计/安全能力）
ROADMAP M1-M5 + 其他模块：
| 模块 | 能力 | EW 有无 |
|---|---|---|
| `audit.py` | 3 层因果链审计（sensorium/tunnel-vision/causal）+ AWI | EW 无审计 |
| `simulation/collusion_detector.py` (M3) | 隐性合谋检测（同步行为模式） | 无 |
| `simulation/drift_detector.py` (M1) | 长时程对齐漂移（sensorium drift 等） | 无 |
| `simulation/causal_report.py` (M5) | 因果图 + 人类可读审计报告 | 无 |
| `simulation/runtime_monitor.py` (M4) | 实时风险监控（rolling 统计、风险升级早告警） | 无 |
| `simulation/statistical_analysis.py` (M2) | 多 run 统计聚合（置信区间、模型间显著差异） | 无 |
| `simulation/scenario_designer.py` (M3) | 合作/竞争/对抗场景设计（预置关系/资源） | 无 |
| `simulation/safety_filter.py` | 内容安全过滤（暴力/仇恨/有害） | 无 |

### 2.3 AFI 的局限（我们用 AS 替代的理由）
- 自建 sim 引擎（非分布式、无 OTel trace、无 replay、单机回合制）——观测性远弱于 AS。
- 无原生因果树（parent_span_id），因果链要事后重建。
- message 读即消费（不可审计，我们打过 message_log 补丁才解决——但那是 AS 的补丁）。
- 规模受限（10 agent × 15 天 ≈ 7200 次 LLM 调用，难扩展）。

---

## 三、对照：AFI 复现 vs AFI 扩展 vs EW 设定

| 维度 | EW（设定） | AFI 复现 | AFI 扩展 |
|---|---|---|---|
| 世界设定 | ✅ 权威（manifesto/宪法/地标/工具/AWI） | 复刻 | — |
| sim 引擎 | ❌ 无 | ✅ 自建（弱观测） | — |
| 中文 LLM | ❌ | ✅ router | — |
| AWI 指标 | ✅ 定义 | ✅ 实现 | — |
| 审计（sensorium/tunnel/causal） | ❌ | — | ✅ audit.py |
| 合谋检测 | ❌ | — | ✅ collusion_detector |
| 漂移检测 | ❌ | — | ✅ drift_detector |
| 因果图报告 | ❌ | — | ✅ causal_report |
| 实时监控 | ❌ | — | ✅ runtime_monitor |
| 统计聚合 | ❌ | — | ✅ statistical_analysis |
| 场景设计 | ❌ | — | ✅ scenario_designer |
| 安全过滤 | ❌ | — | ✅ safety_filter |

---

## 四、对"基于 AS 搭建 AFI"项目的复用决策（初步）

目标=用 AS（强 sim 引擎）+ EW（权威设定）+ AFI 扩展（审计/安全），搭一个 AFI 式集成平台。

| 来源 | 复用 | 怎么用 |
|---|---|---|
| **EW** | 世界设定参考 | manifesto/宪法/地标/工具/经济/治理设计 → 翻译成 AS env 模块 + agent profiles + skills（EW 是"演什么戏"） |
| **EW** | AWI 11 指标 | 直接采用作系统层指标（从 AS replay/trace 重算） |
| **EW** | Season 1 ground-truth | 对照基线 |
| **AFI** | 审计扩展模块（audit/collusion/drift/causal_report/runtime_monitor/statistical/scenario/safety） | **端口到 AS trace/run 格式**（AFI 这些模块读 AFI 的 turn_log/awi.json，改读 AS 的 trace OTel/replay/message_log）——这是"兼容 AFI 内容"的核心 |
| **AFI** | router 多 provider | 参考（AS 已有 litellm 路由，更全） |
| **AS** | sim 引擎 + trace + replay + env 模块 | 作基底（不重造） |
| **safety-audit-platform（封存）** | 审计 12 模块 + 方法论标准 | 方向无关，可搬（已对齐 AgentEval/OASB/SC-Bench 等标准；AFI 的审计模块是其子集+可互补） |

**关键判断**：AFI 的审计扩展（collusion/drift/causal_report/runtime_monitor/...）和我们封存线的审计模块（sensorium/tunnel/collude/causal/decision_trace）**功能重叠**——AFI 是 EW 场景的实现，封存线是 AS 场景的实现+对齐了外部标准。梳理时要决定：用哪套、怎么合并（可能 AFI 的 collusion_detector/drift_detector/runtime_monitor 有封存线没有的思路，值得吸收；封存线的对齐标准+CommonRun 接口是 AFI 没有的）。

---

## 五、启动梳理时要回答的问题（本分析引出）

1. **形态**：fork AS + 注入 EW 设定 + AFI 审计？还是 AS 之上建 AFI 兼容层？
2. **AFI 审计模块端口**：哪些端口到 AS（collusion/drift/runtime_monitor...）？哪些用封存线已实现的等价物？
3. **EW 设定翻译**：manifesto/宪法/地标/工具/经济/治理 → AS env 模块 + skills 的映射。
4. **AWI**：从 AS replay 重算 11 指标（AFI 实现可参考）。
5. **封存线复用**：审计 12 模块 + 方法论标准搬过来吗？
6. **AFI 自建引擎弃用**：确认不 fork AFI engine，用 AS 替代（观测性+规模）。
