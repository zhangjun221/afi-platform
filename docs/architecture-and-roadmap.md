# afi-platform 架构与路线（梳理规划）

> 2026-07-08。启动梳理规划。基于 EW+AFI 分析（`docs/ew-afi-analysis.md`）+ 封存线资产 + AS 实测。
> **两个决策待用户确认**（用户离开，按最佳判断先推荐）：① 形态=AS pip 依赖+AFI 兼容层（推荐）；② 封存线审计资产搬过来作基底（推荐）。

---

## 一、形态决策（推荐：AS pip 依赖 + AFI 兼容层）

**推荐**：AS 作 pip 依赖（`agentsociety2`），afi-platform 建在 AS 之上的兼容层。理由：
- AS 是 pip 可装的（`pip install agentsociety2`），且 AS 的 `custom/` 热加载机制（custom env/skills）就是为"在上面建内容"设计的。
- 不 vendor 2.7GB 源码、不分叉上游——跟 AS 升级、维护轻。
- message_log 补丁从"改 AS 安装包"迁到"custom env 模块"（`SimpleSocialSpaceAuditable`），reinstall-safe。
- AS 已实测可用（Ray/trace/replay/百炼+UniAPI/三 env 验证）。

**若用户实际想 vendor AS 源码**（自包含 fork）：可改，但需承担 2.7G+维护+分叉成本。本规划按 pip 依赖写，vendor 是备选。

## 二、与封存线（safety-audit-platform）的关系

**推荐：搬封存线审计资产作 afi-platform 审计层基底**。理由：
- 封存线 `safetyaudit/audit/` 12 模块已读 AS trace、纯 stdlib、已验证三 env。
- 封存线方法论（CommonRun/taxonomy 对齐 AgentEval12+第6组/检测器接口/scorecard/precision-recall 评测）方向无关，直接用。
- AFI 的审计模块（audit.py/collusion/drift）读 AFI 的 turn_log 格式，不能直接 port 到 AS——但其**思路**（runtime_monitor 实时 rolling 统计、scenario_designer 场景设计）封存线没有，值得吸收。

**合并策略**：封存线审计模块为基底（已对齐标准）+ AFI 的 runtime_monitor/scenario_designer 思路补进来 + AFI audit.py 3 层因果链 = 封存线 causal（已等价）。

## 三、架构

```
afi-platform/
  pyproject.toml          # depends: agentsociety2 + optional(pyproj/pycityproto/Pillow/openai/dotenv/yaml)
  README.md DEVLOG.md
  docs/                   # ew-afi-analysis.md（已）+ 本架构
  afi/                    # 平台包
    world/                # EW设定翻译 → AS env/skills/profiles（"演什么戏"）
      constitution.py     # EW manifesto/constitution → AS agent profile 字段 + 一个"宪法"skill/env
      landmarks.py        # EW 36地标 → MobilitySpace AOI 配置（或自定义空间 env）
      tools.py            # EW 120+工具 → 映射到 AS env 模块工具 + custom skills
      economy.py          # EW ComputeCredits/能量/拍卖 → EconomySpace 配置
      governance.py       # EW 提案/投票/修宪 → 自定义 governance env/skill
      profiles/           # EW agent 人设 → AS agent_specs（init_config agents 段）
    audit/                # 审计层（搬自封存线 safetyaudit/audit/ 12 模块）
      load.py sensorium.py tunnel_vision.py causal.py collude.py
      decision_trace.py replay_data.py html_report.py map_places.py map_bg.py
      __main__.py
      awi.py              # ★AWI 11 重算（从 AS replay/env_state，参考 AFI awi.py 逻辑）
      runtime_monitor.py  # ★从 AFI 端口思路（rolling 统计、风险升级早告警）
      scenario_designer.py# ★从 AFI 端口思路（合作/竞争/对抗场景预置）
    normalize/            # CommonRun 公共事件模型（搬自封存线）+ as_normalizer
    backend_patches/      # message_log custom env（SimpleSocialSpaceAuditable，搬自封存线+迁到 custom）
    cli.py                # run-afi-scenario <yaml>：EW场景→AS run→审计→AWI→报告
  scenarios/              # EW/AFI 场景（constitution+social+economy 起步）
```

**三层**：
1. **world/**（EW设定翻译）——把 EW 的 manifesto/宪法/地标/工具/经济/治理翻译成 AS 能用的 env 模块配置 + skills + agent profiles。
2. **audit/**（审计层）——搬封存线 12 模块 + AWI 重算 + AFI 的 runtime_monitor/scenario_designer 思路。
3. **backend**（AS）——pip 依赖，不碰源码；message_log 走 custom env。

## 四、EW 设定翻译映射（world/ 的核心工作）

| EW 内容 | 翻译到 AS 什么 | 备注 |
|---|---|---|
| agent_manifesto + constitution | AS agent profile 的 north_star/personality + 一个"宪法治理" custom env/skill | 宪法可修=治理 env |
| 36 地标 | MobilitySpace AOI 配置（已有北京地图）或自定义空间 env | EW 地标是虚构，可映射到北京 AOI 或自建 |
| 120+ 工具 | AS env 模块工具（SimpleSocialSpace 的 send_message/EconomySpace 的 credits/...）+ custom skills | 渐进翻译，先子集 |
| ComputeCredits/能量/拍卖 | EconomySpace 配置（AS 已有经济 env） | 直接用 AS EconomySpace |
| 提案/投票/修宪 | 自定义 governance env（AS 无原生，需 custom） | 参考 AFI governance/ |
| AWI 11 指标 | audit/awi.py 从 AS replay 重算 | 参考 AFI awi.py（我们重建过） |
| Season1 agent 配置 | AS agent_specs（init_config） | 5 世界×10 agent |

**策略**：不一次性翻译全部 120+ 工具/36 地标。**先子集**（constitution + social + economy + 几个地标）跑通一轮 EW 式 15 天，验证"AFI on AS"成立，再扩。

## 五、AFI 审计模块端口策略

| AFI 模块 | 处理 | 理由 |
|---|---|---|
| audit.py（3层因果链） | 封存线 causal 已等价，用封存线 | 已对齐标准 |
| collusion_detector | 封存线 collude 已有，吸收 AFI"同步行为模式"思路 | 互补 |
| drift_detector | 封存线 drift（M3 待建），吸收 AFI"sensorium drift"思路 | 互补 |
| causal_report | 封存线 html_report+decision_trace 已有 | 等价 |
| **runtime_monitor** | ★端口思路（rolling 统计/早告警） | 封存线无，AFI 独特 |
| **scenario_designer** | ★端口思路（合作/竞争/对抗预置） | 封存线无 |
| statistical_analysis | 端口思路（多 run 置信区间） | M4 差分用 |
| safety_filter | 可选端口（内容安全过滤） | 非 core |

## 六、路线（分阶段）

### A1（起步）——骨架 + 资产搬迁
- pyproject（depends agentsociety2）+ 包结构
- 搬封存线 `safetyaudit/audit/` 12 模块 → `afi/audit/`（改 import）
- 搬封存线 normalize/CommonRun + as_normalizer
- 搬 backend_patches（message_log custom env，迁成 `SimpleSocialSpaceAuditable`）
- 验证：`python -m afi.audit <AS run>` 出报告（搬迁后仍工作）

### A2（EW 设定子集翻译）——"AFI on AS"成立验证
- world/constitution.py：EW manifesto/constitution → AS agent profile + 治理 custom env
- world/economy.py：EW ComputeCredits → EconomySpace 配置
- world/landmarks.py：几个地标 → MobilitySpace AOI（或 SimpleSocialSpace 社交）
- world/profiles/：Season1 几个 agent → AS agent_specs
- 一个 EW 式场景 YAML（constitution+social+economy, 5 agent, 短跑）
- 验证：`run-afi-scenario ew-subset.yaml` → AS run → 看到 EW 式社会行为

### A3（审计 + AWI）——AFI 审计能力到位
- audit/awi.py：AWI 11 从 AS replay 重算（参考 AFI awi.py）
- 端口 AFI runtime_monitor 思路（rolling 风险统计）
- 端口 AFI scenario_designer 思路（场景预置）
- 验证：EW 场景跑完 → AWI 11 指标 + audit 报告 + runtime 监控

### A4（完整 + 长时程）——对标 EW Season1
- 扩 EW 工具/地标翻译到更全
- 15 天 × 多模型对照（对标 EW Season1 5 世界）
- scenario DSL 完整（借封存线 methodology 的 Label/ground-truth）
- 差分 vs EW Season1 ground-truth

## 七、待用户确认（回来时）
1. **形态**：AS pip 依赖+兼容层（推荐）vs vendor AS 源码？
2. **封存线资产**：搬过来作基底（推荐）vs 重做？
3. **EW 翻译起点子集**：constitution+social+economy+几地标（推荐）vs 别的组合？
4. **AWI**：从 AS replay 重算 11（推荐）vs 只用 AFI 的 9？

## 八、一句话
afi-platform = AS（pip 依赖，sim 引擎）+ EW设定（翻译成 AS env/skills/profiles）+ AFI审计（封存线模块搬来作基底 + AFI runtime_monitor/scenario_designer 思路补 + AWI 重算）。三层：world（EW翻译）/audit（审计）/backend（AS）。路线 A1 骨架→A2 EW子集验证→A3 审计+AWI→A4 长时程对标 Season1。
