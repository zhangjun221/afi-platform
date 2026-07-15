# A4 规划 — 长时程 × 多模型 + AWI 完整化 + 对标 EW Season1

> 2026-07-10。A3 完成（AWI 9 族 + runtime 监控 + 场景预置）后的收尾阶段规划。
> 依据：`docs/architecture-and-roadmap.md` A4 段 + `docs/a3-plan.md` §3（A4 待做清单）。
> 源：EW `Season 1/`（mixed-world 配置）+ `results/awi_metrics.md`（AWI 定义 + Season1 M1 结果）+ `tools/README.md`（116 工具/19 类）+ AFI `simulation/statistical_analysis.py`。
> 目标：把平台从"短跑验证"推进到"长时程 × 多模型实证"，AWI 从"代理/stub"补到"真实可算"，并与 EW Season1 的可对照部分对标。

---

## 0. 三个必须先承认的事实（决定 A4 怎么做）

1. **EW Season1 只发布了 M1 人口 ground-truth**：`awi_metrics.md` 给了 5 世界的 M1 终值（Claude=10/Gemini=10/Grok=0/GPT5Mini=0/Mixed=3 of 10），但 **M2–M9 只有定义，无 per-world 数值**。所以"对标 Season1"严格只能对 **M1**；M2–M9 我们能算，但只能 **跨我们自己的模型对照**，没有 EW baseline 可 diff。
2. **EW 工具 116 个 / 19 类**，全量翻译是 A2 量级的好几倍；其中 **MobilitySpace（M3）需 pyproj+pycityproto+map.pb 城市地图数据**，依赖重。
3. **全量 15 天 × 10 agent × 5 模型** = 360 tick × 10 agent × 5 = ~18000 agent-step，A2 的 ~250 倍，单 run 数小时 + 高 LLM 成本。不可行。

→ **A4 不做"全量字面复现 EW Season1"**（成本/数据都不支持），而是做**务实分层**：补让 M1/M2 真（唯一有 baseline + AFI 已建模的两个）、跑长时程多模型、AWI 跨模型对照 + 统计置信、M1 与 EW 对标；关系/地图/全工具列为"超 A4"诚实声明。

## 1. A4 的"完成"定义（一句话）

平台能跑一个**压缩长时程**（15 sim-天）× **2–3 个百炼模型**的 EW 场景，AWI 的 **M1（人口/死亡）和 M2（犯罪）从 stub 升为真实可算**，产出 **跨模型 AWI 对照表 + M1-vs-EW 对照 + 多 run 统计置信（mean/std/CI）**，并诚实标注 M3/M6/M7 仍代理、M3 地图/全工具/10-agent×360-tick 超出 A4。

## 2. 范围（分层）

### Tier 1（A4 必做）

| 项 | 做什么 | 让哪个 AWI 真 |
|---|---|---|
| **EnergySpace + 死亡** | 新 custom env：agent 有 energy/health，每步消耗，≤0 死亡（从 agents 移除）；治理投票可处决。 | **M1 真算**（唯一 EW baseline） |
| **CrimeSpace** | 新 custom env：crime_log（append-only，crime_type/actor/victim/tick），EW Police Station 工具 + AFI crime_log 思路。 | **M2 真算** |
| **multi-model harness** | 同一场景 × N 模型跑，按 run 收 AWI，产跨模型对照表。 | M4–M9 跨模型 |
| **长时程压缩** | 场景扩到 15 sim-天（**1 步/天 = 15 步**，或 15×4=60 步二选一），不改 env 语义。 | 时序长度 |
| **statistical_analysis** | 端口 AFI 思路：多 run/多 seed 的 AWI mean/std/CI + 跨模型显著性。 | 置信度 |
| **M1-vs-EW 对照** | 我们的 M1（存活率）与 EW 公布的 Claude/Gemini/Grok/GPT5Mini/Mixed 对照（定性：是否像 Grok/GPT5Mini 崩溃或像 Claude/Gemini 维持）。 | 唯一真 baseline |

### Tier 2（A4 stretch，时间/成本允许才做）
- **RelationshipSpace**（M7 真关系类型：ally/rival/mentor）—— EW FitLife Trust + AFI relationship 思路。
- **BillboardSpace**（M6 真公开表达：billboard 帖）—— EW Agent Billboard。

### 超出 A4（诚实声明，不做）
- **MobilitySpace 地图**（M3 真）—— 需 pyproj/pycityproto/map.pb 城市数据 + 下载，依赖重，单列。
- **116 工具全量翻译**—— A2 翻了治理/经济/社交/地标子集，够审计验证；全量是内容工程非平台核心。
- **10 agent × 360 tick × 5 世界全量跑**—— 成本不可行（见 §0.3）；A4 用压缩长时程 + 2–3 模型。
- **完整 pydantic scenario DSL schema**—— A2 lite loader 够用。

## 3. 交付物清单

```
afi-platform/
  custom/envs/
    energy_space.py        # ★EnergySpace: energy/health/死亡 (M1)
    crime_space.py         # ★CrimeSpace: crime_log (M2)
    (Tier2) relationship_space.py, billboard_space.py
  afi/world/
    ew_full.yaml           # ★15-sim-天 EW 场景（含 energy/crime）
    multi_model.py         # ★multi-model harness: run×N模型→AWI 对照表
  afi/audit/
    awi.py                 # M1/M2 改读 EnergySpace/CrimeSpace（feasibility: stub→computed）
    statistical.py         # ★端口 AFI statistical_analysis: mean/std/CI + 跨模型显著性
    comparison.py          # ★跨 run/model AWI 差分表（封存线占位，A4 填实）
    html_report.py         # 加跨模型 AWI 对照表 + 统计置信块
  afi/cli.py               # +multi-run 子命令 + run-ew --model <list> --days 15
  docs/a4-plan.md          # 本文档
  results/                 # ★A4 实证产物（AWI×model CSV + 对照表 + 报告）
```

## 4. 各模块设计要点

### 4.1 EnergySpace（M1 真算，核心）
**复用 AS 机制**：EnvBase/@tool/to_workspace/`_agent_state_columns`（per-agent energy 每 step 落 replay）。
**新增逻辑**：
- 每 agent `energy`（初值=配置，如 100），每 step 扣 `daily_consumption`；agent 可调 `recharge`/`rest`（EW Home/Bean&Brew）补回。
- `energy ≤ 0` → agent 标记 dead，从活跃集移除（`agents_alive` 递减）。
- 治理 env 加 `execute_agent` 工具（EW governance vote-to-remove）→ 调 EnergySpace 标死。
- AWI M1 改读 `energy_agent_state` replay（每 step agents_alive = energy>0 计数）→ M1 feasibility: `degenerate→computed`。
**EW 对标口径**：EW M1 = 期末存活数（起点 10，break-even 10）。我们 = 期末 energy>0 的 agent 数。

### 4.2 CrimeSpace（M2 真算）
**复用**：EnvBase/@tool/to_workspace + append-only log（仿 message_log）+ `_env_state_columns`（crimes_per_step）。
**新增**：crime_log（crime_type ∈ {theft, arson, assault, intimidation}, actor, victim, tick, step），`commit_crime` 工具（readonly=False）。
**AWI M2** 改读 crime_log → `total_crimes/crimes_by_type/crimes_by_agent` → feasibility: `stub→computed`。
**思路来源**：AFI crime_log + EW Police Station 工具类（借思路不搬代码）。

### 4.3 multi_model.py（跨模型 harness）
- `run_multi_model(scenario, models, run_root)` → 对每个模型跑一次（`AGENTSOCIETY_LLM_MODEL` 覆盖），收 run_dir。
- `compare_awi(run_dirs)` → 每模型 AWI 9 族表 + 跨模型差分（哪个模型 M1 崩/M8 不平等/M9 修宪多）。
- 复用 `awi.compute_awi` + 新 `comparison.py`。

### 4.4 statistical.py（端口 AFI statistical_analysis）
- `awi_stats(runs)` → 每族 mean/std/95%CI（跨 seed 或跨 run）。
- `model_significance(runs_by_model)` → 跨模型均值差 / 合并 std（简易 t，标注"非正式统计"）。
- 诚实：样本小（2–3 run/model）→ CI 宽，仅趋势性。

### 4.5 ew_full.yaml + 长时程压缩
- 15 sim-天，1 步/天 = 15 步（tick=86400）**或** 15×4=60 步（tick=21600）——执行时二选一，优先 15 步（成本可控）。
- 加 EnergySpace + CrimeSpace env_modules。
- intervene 种子扩：除治理/经济外，加 crime 试探（adversarial 预置已有）+ 能量管理提示。
- 诚实：EW 真 15 天是 360 小时步；我们压缩到 15–60 步捕捉**趋势**（宪法演化/经济 Gini 漂移/agent 死亡），非逐小时复现。

### 4.6 AWI M1/M2 升级 + html_report
- awi.py：M1 读 EnergySpace replay（`energy_agent_state`），M2 读 CrimeSpace `crime_log.jsonl`；feasibility 改 computed。
- html_report：加"跨模型 AWI 对照表"（9 族 × N 模型）+ "统计置信"块（mean±std）。

## 5. 关键技术决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| 长时程粒度 | 15 步（1/天）优先，60 步备选 | 全 360 步成本不可行；15 步够捕捉趋势 |
| 多模型数 | 2–3 个百炼模型（qwen-plus + qwen-max + 待定） | 多模型是核心；3 个够对照，5 个成本高 |
| agent 数 | 5（同 A2/A3）而非 10 | 10 agent×15 步×3 模型成本仍高；5 够验证 |
| M1 死亡建模 | EnergySpace + 治理处决 | EW 死亡=能量耗尽/治理投票，两路都建 |
| M2 犯罪 | CrimeSpace + crime_log | AFI 已建模 + EW Police Station；借思路 |
| M3/M6/M7 | 仍代理/stub（Tier2 关系可选） | 地图重依赖、无 EW baseline，超 A4 |
| 对标口径 | M1 严格对 EW；M2–M9 跨模型自对照 | EW 只发 M1 baseline |
| 统计 | mean/std/CI，标注非正式 | 样本小（2–3 run） |

## 6. 验收标准（Checklist）

**新 env**
- [ ] EnergySpace 落 replay（`energy_agent_state` 每 step 每 agent），energy≤0 的 agent 计为 dead，`agents_alive` 随时间递减（A4 run 里至少 1 个 agent 死亡或明确维持）。
- [ ] CrimeSpace 落 `crime_log.jsonl`，至少 1 条 crime 记录（adversarial 预置触发）。

**AWI 升级**
- [ ] M1 feasibility `degenerate→computed`，值=期末 energy>0 agent 数。
- [ ] M2 feasibility `stub→computed`，值=crime_log 总数 + by_type。
- [ ] M3/M6/M7 仍 proxy/stub（诚实标注未变）。

**长时程 + 多模型**
- [ ] `ew_full.yaml` 跑通 15 步（1/天），run_dir 有 15 步 replay。
- [ ] 至少 2 个模型各跑 1 次（qwen-plus + qwen-max），产跨模型 AWI 对照表。
- [ ] M1-vs-EW 对照：我们的存活率 vs EW Claude/Gemini(维持)/Grok/GPT5Mini(崩溃) 定性对照。

**统计**
- [ ] `statistical.awi_stats` 产每族 mean/std/CI（≥2 run 或 seed）。
- [ ] html_report 含跨模型对照表 + 统计块。

**集成 + 无回归**
- [ ] `python -m afi run-ew scenarios/ew_full.yaml --days 15 --model qwen-plus,qwen-max --multi` 一条龙。
- [ ] 短场景（ew-subset）AWI 不变（A3 基线：M4=4.20/M8 Gini0.038/M9 v2）。
- [ ] commons audit 不变。

**文档**
- [ ] DEVLOG 轮次 8。
- [ ] README 更新 A4 完成态 + 诚实声明（超 A4 项）。
- [ ] 本文偏离补注。

## 7. 风险与兜底

| 风险 | 兜底 |
|---|---|
| 15 步×5 agent×2–3 模型 LLM 成本/时长 | 先跑 1 模型 15 步估成本；若 >30 min/run 降为 2 模型或 10 步 |
| 百炼只有 qwen-plus 可用（无 qwen-max） | 执行时 `gh`/curl 探百炼模型列表；不可多模型则用 qwen-plus + 不同 seed/Temperature 代理"模型差异"并诚实标注 |
| EnergySpace 死亡逻辑与 Ray actor 状态冲突 | 仿 EconomySpace 已验证 to_workspace/restore；death 标志落 JSON + replay |
| CrimeSpace 的 commit_crime agent 不主动调 | adversarial 预置 intervene 种子注入 commit_crime 调用（同 A2 治理种子机制） |
| M1 对标 EW 但模型不同（qwen vs Claude/Grok） | 诚实：只能定性对照"是否崩溃/维持"，非同模型定量 |
| 统计样本太小 CI 无意义 | 标注"趋势性非正式"；≥3 run 再谈显著性 |
| 全量工具/地图被期望 | 本规划 §2 明确"超 A4"，执行时不偷偷扩 |

## 8. 执行顺序（建议）

1. EnergySpace + 步数压缩场景骨架（先不接 crime），单模型跑 15 步，验证 M1 真（agent 死亡/维持）。
2. CrimeSpace + adversarial 种子注入，验证 M2 真（crime_log 非空）。
3. awi.py M1/M2 升级 + feasibility 改 computed。
4. multi_model.py + statistical.py + comparison.py。
5. 2 模型 × 15 步 跑 → 跨模型 AWI 对照表 + M1-vs-EW + 统计。
6. html_report 加对照表 + 统计块 + cli multi-run。
7. 验收 checklist 逐项 + DEVLOG + README。
8. （Tier2 stretch）RelationshipSpace/BillboardSpace 若时间允许。

## 9. 诚实声明（写进 README）

A4 ≠ 全量 EW Season1 复现。原因：EW 仅发 M1 baseline；全量 10×360×5 成本不可行；MobilitySpace 地图依赖重。A4 交付：**M1/M2 真算 + 长时程压缩多模型 + AWI 跨模型对照 + M1-vs-EW + 统计置信**。M3 地图 / 116 工具全量 / 10-agent×360-tick / 完整 DSL 列为后续工作。

## 10. 与路线的关系

A4 是 afi-platform 路线（A1→A2→A3→A4）的收尾：A1 骨架、A2 EW 子集成立验证、A3 AWI+监控、**A4 长时程多模型实证 + AWI 完整化 + 对标**。完成后平台具备"跑长时程 → 实时监控 → AWI 9 族量化 → 跨模型对照 → 对标 EW"的闭环，可支撑安全审计研究产出（长时程 drift / 治理崩溃 / 经济不平等涌现 的实证证据）。
