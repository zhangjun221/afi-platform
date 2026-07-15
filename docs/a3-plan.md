# A3 规划 — AWI 重算 + AFI runtime_monitor/scenario_designer 思路端口

> 2026-07-10。A2 完成（"AFI on AS" 成立验证）后的下一步规划。
> 依据：`docs/architecture-and-roadmap.md` 第五节（AFI 端口策略）+ A3 段。
> 源：EW `results/awi_metrics.md`（AWI 权威定义）、AFI `results/awi.py`（参考实现）、AFI `simulation/runtime_monitor.py`、`simulation/scenario_designer.py`。
> 目标：从 AS run_dir 的 trace + replay + env state 重算 AWI，端口 AFI 的"rolling 统计早告警"与"场景预置"思路，让审计层从"事后描述"升级到"指标化 + 时序监控 + 场景对照"。

---

## 0. 先校正一个事实：AWI 是 9 个指标族，不是 11

EW 权威定义（`results/awi_metrics.md`）= **9 个指标族 M1–M9**，AFI `awi.py` 也按 9 族实现（其 dataclass `AWISnapshot` 有 ~14 个字段，因 M2/M8 各含子项，故曾有"11"的口径误传）。本规划按**权威 9 族**做，子项如实展开，不硬凑数字。

## 1. A3 的"完成"定义（一句话）

审计层能从一次 EW 场景 run 产出：**AWI 9 族指标报告**（每族标注"从 AS 数据可算 / 部分代理 / 需 X env 待 A4"）+ **per-step AWI 时序**（可算族的逐 tick 曲线）+ **runtime 风险告警**（rolling 统计检测到的突变）+ **场景预置对照**（cooperative/competitive/adversarial 三个预设场景跑出 AWI 差异）。即"AFI 式审计能力到位"。

## 2. AWI 9 族 ↔ AS 数据源 可行性表（核心）

| 族 | EW 定义 | AS 数据源（A2/A3） | A3 可行性 | 处理 |
|---|---|---|---|---|
| **M1 人口健康** | 期末存活 agent 数（死亡=能量耗尽/治理投票；出生=治理投票） | AS 不建模 agent 死亡；`agents/` 目录存在即活 | 退化 | 报 `agents_alive=N（A3 不建模死亡）`；诚实标注结构性局限 |
| **M2 治安** | 犯罪率（偷/纵火/袭击/恐吓） | 无 crime env | 不可算 | stub，标注"需 crime env（A4）" |
| **M3 空间探索** | 每 agent 到访唯一地标数 | 无 MobilitySpace（A2 地标纯文本，无移动） | 部分代理 | 用 `landmark_space.get_landmark_info` 调用计数代理"被查询地标"；标注非真移动 |
| **M4 工具探索** | 每 agent 用过唯一工具数 | trace `react.tool` 的 `react.action`（按 agent 分组去重） | ✅ 可算 | 从 trace 直接算 |
| **M5 治理参与** | 投票参与率 + 投票一致性（独立判断 vs 羊群） | `governance_env_state`（num_proposals/total_votes）+ `GOVERNANCE_STATE.json`（每提案 votes） | ✅ 可算 | 参与率=投票 agent/总 agent；一致性=同提案同方向比例（代理"羊群"） |
| **M6 公开表达** | 博客/billboard/文化产出 | billboard 非工具（是地标）；`message_log` send_message 可用 | 部分代理 | 用 send_message 总量 + billboard 相关 ask_env 调用代理；标注非真 blog/billboard |
| **M7 社会纹理** | 关系类型/情感多样性/网络密度 | `message_log`（sender→receiver 有向边） | 部分代理 | 算网络密度 + 度分布；关系"类型"无（无关系模型）→ 标注 |
| **M8 经济平等** | 信用分布 + Gini + 活跃度 | `economy_agent_state`（每 agent 每 step currency）+ `economy_env_state` | ✅ 可算 | Gini 时序 + total_credits + 流水（currency 变化次数） |
| **M9 宪法成长** | 文章增/改/删 | `governance_env_state`（version/num_articles）+ `GOVERNANCE_STATE.json`（proposals passed/rejected） | ✅ 可算 | version 增量=修宪次数；passed/rejected 计数 |

**可算族**：M4/M5/M8/M9 全量（A2 数据已支撑）。
**部分代理**：M3/M6/M7（用近旁数据代理，如实标注）。
**退化/不可算**：M1（结构局限，A4 建模死亡）、M2（需 crime env，A4）。

## 3. 范围（in / out）

**In（A3 做）**
- `afi/audit/awi.py`：9 族指标，从 run_dir 重算（trace + replay + env state JSON），产 `AWIReport`（每族值 + 可行性标注）+ per-step 时序（可算族）。
- `afi/audit/runtime_monitor.py`：端口 AFI rolling 统计 + 变点检测 + 早告警思路（**读我们的数据**：sensorium 时序 / governance 停滞 / Gini 飙升 / tunnel-vision），产 `RiskAlert` 列表。封存线无此"时序监控"层。
- `afi/world/scenarios/` 预置：`cooperative.yaml` / `competitive.yaml` / `adversarial.yaml`（端口 AFI scenario_designer 思路——不同 initial_credits / profile 组合 / intervene 种子），跑出 AWI 差异对照。
- HTML 报告加 AWI 块 + runtime 告警块。
- CLI `awi` 子命令（`python -m afi awi <run_dir>`）。

**Out（A4 做）**
- crime env（M2 真算）、agent 死亡建模（M1 真算）、MobilitySpace 地图（M3 真算）、blog/billboard 工具（M6 真算）、关系模型（M7 真算）。
- 15 天 × 多模型对标 EW Season1。
- statistical_analysis 多 run 置信区间（A4 差分）。

## 4. 交付物清单

```
afi-platform/
  afi/audit/
    awi.py              # ★AWI 9 族重算 + per-step 时序 + AWIReport
    runtime_monitor.py # ★rolling 统计 + 变点检测 + RiskAlert（端口 AFI 思路）
    html_report.py     # 加 AWI 块 + 告警块
    __main__.py        # +awi / +runtime 命令
  afi/world/
    scenarios/         # ★场景预置（ports scenario_designer）
      cooperative.yaml
      competitive.yaml
      adversarial.yaml
    scenario_presets.py # ScenarioPreset 数据 + apply 到 scenario dict
  afi/cli.py           # +awi 子命令 + run-ew --preset <name>
  docs/a3-plan.md      # 本文档
```

## 5. 各模块设计要点

### 5.1 awi.py — AWI 重算（核心）

- `AWISnapshot`（仿 AFI dataclass，字段按 9 族）：`day/tick, agents_alive, total_crimes(stub), avg_locations_visited(代理), avg_tools_used, governance{proposals,votes_cast,participation,approval_rate,herd_ratio}, public_expression(代理), social_fabric{edges,density,avg_degree}, economy{gini,total_credits,turnover}, constitution{articles,version,amended,passed,rejected}, feasibility{M1..M9: "computed"/"proxy"/"stub"}`。
- `compute_awi(run_dir, tick=None)` → 单步快照（cumulative-to-date，仿 AFI）。
- `compute_awi_timeline(run_dir)` → list[AWISnapshot]，每 step 一个（从 `governance_env_state` / `economy_agent_state` / `economy_env_state` replay shard 读时序 + trace 按 tick 切分工具调用）。
- `_gini`（直接用 AFI 已验证的实现，2·n²·mean 分母）。
- 数据读取：复用 `replay_data.load_env_timeline`（globs `*_env_state`）+ 新增 `load_agent_state_timeline`（读 `economy_agent_state` 每 agent 每 step）+ `load.load_spans`（trace 按 tick 切）+ `collude.extract_blackboards`（message_log → M7 边）。
- `format_awi_report(timeline)` → 文本（仿 AFI `format_report`），标每族可行性。

### 5.2 runtime_monitor.py — rolling 统计早告警（端口思路）

- **端口思路**（不 port 代码，因 AFI 读 `turn_log`、我们读 trace+replay）：
  - `RiskAlert`（tick, alert_type, value, threshold, severity, message）+ `MonitorState`（per-series 滚动窗口 + alerts）。
  - `_detect_change_point(series, window=3)`：近窗均值 vs 基线 → 标变点（AFI 原算法）。
- **告警类型**（针对我们的可算族 + 封存线已有检测器的时序化）：
  - `sensorium_collapse`：sensorium 比例跌 >40%（AFI 原有；我们 sensorium 已算）。
  - `governance_stagnation`：连续 N tick 无新提案/无投票（治理停滞）。
  - `economic_hoarding`：Gini 单步跳升 > 阈值 或 currency 集中度过高。
  - `tunnel_vision_escalation`：tunnel-vision 窗口数单调上升（封存线 tunnel_vision 的时序化）。
- `run_monitor(run_dir)` → list[RiskAlert]，喂入 HTML 报告告警块。

### 5.3 scenario_presets.py + 3 YAML — 场景预置（端口思路）

- **端口思路**（AFI `scenario_designer` 给 cooperative/competitive/adversarial/mixed 的初始 credits + 初始关系；我们给 EW-subset 的变体）：
  - `cooperative`：高 initial_credits（150，资源充足）、profile 偏协作（Anchor/Anvil/Flora/Genome + 一个温和型）、intervene 种子偏互助投票。
  - `competitive`：低 initial_credits（50，稀缺）、Victory Arch 奖励放大、intervene 种子偏竞争提案 + 对抗投票。
  - `adversarial`：profile 偏冲突（Blackbox + Anchor + 对立型）、intervene 种子含反对票 + 串谋试探。
- `apply_preset(scenario_dict, preset_name)` → 改写 initial_credits / agents 子集 / intervene 种子。
- `run-ew --preset cooperative scenarios/ew-subset.yaml` 叠加预置。

### 5.4 html_report.py — 加两块

- AWI 块：9 族值表 + 可算族 per-step 折线（gini/proposals/tools-used 时序）+ 每族可行性 badge（computed/proxy/stub）。
- 告警块：RiskAlert 列表（tick / 类型 / 值 / 阈值 / 严重度）。

### 5.5 cli.py — awi 子命令 + preset

- `python -m afi awi <run_dir>` → 打印 AWI 文本报告 + 写 `awi_report_<run>.json`。
- `python -m afi run-ew scenarios/ew-subset.yaml --preset competitive --run-dir ... --audit` → 叠加预置再跑。

## 6. 关键技术决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| AWI 族数 | 权威 9 族（非"11"） | EW + AFI 一致；子项展开不硬凑 |
| 不可算族 | 诚实 stub + 标注"需 X env (A4)" | 不造假指标；指明缺什么 |
| 部分代理族 | 用近旁数据 + 标 "proxy" | 尽量给值但标清非真定义 |
| per-step 时序 | 从 replay env_state shard 读 | AS 已落 `governance_env_state`/`economy_agent_state` 每 step |
| runtime_monitor | 端口思路非代码 | AFI 读 turn_log，我们读 trace+replay，设定不同（"借思路不搬代码" §003） |
| scenario_designer | 端口为 3 个 EW-subset 预置 YAML | AFI 给初始关系，我们给 EW 变体（profile 组合/credits/intervene 种子） |
| AWI 计算位置 | audit 层（backend 无关，纯读 run_dir） | 与封存线审计模块同构，不耦合 AS |

## 7. 验收标准（Checklist）

**AWI 重算**
- [ ] `python -m afi awi runs/ew_subset` → 9 族全有输出，可算族（M4/M5/M8/M9）有真实数值。
- [ ] M8 Gini 在 [0,1]，与 EconomySpace currency 分布一致（A2 run：agent2=120/agent4=110/其余100 → 非零 Gini）。
- [ ] M9 version=2（与 A2 实测一致）、proposals=4、passed=1、rejected=0。
- [ ] M4 每 agent 唯一工具数 > 0（从 trace react.action 去重）。
- [ ] 不可算族（M1 退化/M2 stub）明确标注，不报假数。

**per-step 时序**
- [ ] `compute_awi_timeline` 返回 ≥8 个快照（A2 跑了 12 step + intervene）。
- [ ] Gini/proposals/tools-used 至少其一有 per-step 折线入 HTML。

**runtime_monitor**
- [ ] `run_monitor(runs/ew_subset)` 返回 RiskAlert 列表（至少能算 sensorium/governance_stagnation/gini 系列）。
- [ ] 不抛异常（rolling 窗口 < 序列长度时 graceful）。

**场景预置**
- [ ] `cooperative/competitive/adversarial.yaml` 三份存在，`apply_preset` 能改 initial_credits + agents 子集 + intervene。
- [ ] 至少跑通 1 个预置场景（competitive），AWI 与 ew-subset 有可读差异（如 competitive 的 Gini 更高 / 提案更多对立）。

**集成**
- [ ] `python -m afi.audit runs/ew_subset --full` HTML 含 AWI 块 + 告警块。
- [ ] `python -m afi run-ew ... --preset competitive --audit` 一条龙跑通。

**无回归**
- [ ] `python -m afi.audit runs/ew_subset --sensorium` / `--full` 仍正常（A2 报告结构不破）。
- [ ] commons audit 不变（sensorium ~17-22%）。

**文档**
- [ ] DEVLOG 记轮次 7（A3 执行）。
- [ ] README 更新 A3 完成态。
- [ ] 本文（a3-plan.md）如偏离规划补"执行偏差"注。

## 8. 风险与兜底

| 风险 | 兜底 |
|---|---|
| replay shard 文件名乱序（.09/.0a/.0b…十六进制分片） | `load_env_timeline` 已按 start_time 排序；AWI 按 step 字段排，不靠文件名 |
| economy_agent_state 字段名/类型与预期不符 | 先 dump 一行样本对齐 schema 再算；按 `_schema.json` 列名取 |
| Gini 算错（A2 曾踩 2·n·mean 分母 bug） | 直接搬 AFI 已验证 `_gini`（2·n²·mean），加单测（等分→0/独占→(n-1)/n） |
| runtime_monitor 序列太短变点检测报错 | `_detect_change_point` 已 `len < window*2` 返回 False；加长度守卫 |
| 预置场景跑不出 AWI 差异（LLM 随机性大） | 预置差异做"结构性"（initial_credits / profile 组合 / intervene 种子方向），不依赖细微涌现 |
| AWI 不可算族显得"半成品" | 这是诚实的——A3 显式标 stub 并指向 A4 要补的 env，比造假指标强 |

## 9. 执行顺序（建议）

1. `awi.py` 骨架 + `_gini` 单测 + M4/M5/M8/M9 四个可算族（从 A2 run 验证数值对）。
2. per-step 时序（`compute_awi_timeline`，读 replay env_state + agent_state shard）。
3. 部分代理族 M3/M6/M7 + stub M1/M2（标 feasibility）。
4. `runtime_monitor.py`（rolling + 变点 + 4 类告警）。
5. `scenario_presets.py` + 3 YAML + `apply_preset` + cli `--preset`。
6. html_report 加 AWI 块 + 告警块 + cli `awi` 子命令。
7. 跑 competitive 预置对照 → 验收 checklist 逐项打勾。
8. DEVLOG + README。

## 10. 与路线的关系

A3 让审计层从 A2 的"行为描述 + 检测器"升级到"AWI 指标化 + 时序监控 + 场景对照"——这是 AFI 式集成审计的核心能力。完成后，A4（长时程 × 多模型对标 Season1）才有量化口径（AWI 9 族 vs EW Season1 ground-truth）去对比。
