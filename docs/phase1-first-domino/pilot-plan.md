# Phase 1 Pilot Plan：第一骨牌归因 v0 + 反事实 rerun

> 2026-07-14。旗舰落地 plan。承接 `strategy-impact-analysis.md` §六。节奏沿用 A2-A4：本文为 plan，待"开始"再执行。
> 旗舰：第一骨牌归因 + 反事实世界分叉。验证 case：qwen 族 collapse（`runs/ew_multi/qwen-{plus,max,turbo}`）。
> 原则：label-free（不依赖测试套件）、stdlib、扩现有 `causal.py`/`awi.py` 不重写。
> ⚠️ **范围已定（2026-07-14）**：这是**可复用套件**，不是一次性脚本——qwen-collapse 是 v0 的驱动 + 首验 case，方法（event-graph + localization + 反事实 rerun）做成 generic。v0 的 localization 先 **M1-collapse 专用**（hardcode 能量轨迹+漏调 recharge），代码留扩展点，之后加 M8/M9 等 outcome 是局部增量。详见 §〇.5。

---

## 〇、目标 + 可证伪退出条件

**目标**：给定一个已知 collapse 结局（qwen 族全死），自动定位"第一骨牌"——哪个 agent 的哪步动作在崩溃前最早出现、且去掉它（反事实重跑）collapse 不发生/延迟。

**退出条件**（E5 给的 >70% top-3 localization，pilot 因 n=3 收窄）：
1. 在 qwen-plus / qwen-max / qwen-turbo 3 个 run 上，top-3 候选骨牌**命中"漏调 recharge"**真因（命中 = 候选里含该 agent 该步漏调 recharge）。
2. 对 ≥1 个 run，**反事实 rerun**（强制该 agent 在该步调 recharge）后 collapse 延迟或不发生。
3. 给出 **disentangle 结论**：qwen 崩溃的 first domino 是"不调 recharge"（能力 gap）还是"调了但被治理/经济挡"（alignment/societal gap）。

pilot 标"趋势性"，n=3 不做正式统计（诚实）。

---

## 〇.5、范围与复用性（三层，沿现有 afi audit/backend 切分）

**是可复用套件，不是一次性 run**——qwen-collapse 是 v0 驱动 + 首验 case；方法做 generic，之后任何 AS run 都能归因。

| 层 | 复用性 | 接口 | 归属 | 说明 |
|---|---|---|---|---|
| **① 归因层** | ✅ 后端无关 | `build_event_graph(run_dir)` / `localize_first_domino(graph, outcome)` | `afi/audit/` | 读 run_dir（trace+replay），与 `causal.py` 同构；任何 AS run 可用 |
| **② 反事实 rerun 引擎** | ⚠️ AS 耦合 | `counterfactual_rerun(scenario, domino) -> new_run_dir` | `afi/world/`（或 backend） | 重跑必须调 AS（现在）/Concordia（未来）；**诚实标后端耦合**，不假装通用 |
| **③ orchestrator + 报告** | ✅ 复用 | `attribute(run_dir, outcome) -> AttributionReport` | `afi/audit/attribution.py` | 串 ①② 出归因报告 + cli |

**关键诚实点**：① 是真复用（读文件、后端无关，照搬现有 audit 模块模式）；② 离不开引擎（AS 重跑），归 backend/world 层，不混进 audit 层。这和现有 `afi/audit`（后端无关）/ `afi/backend`（AS 适配）切分一致。

**v0 localization 泛化度（已定）**：先 **M1-collapse 专用**——hardcode 能量轨迹 + 漏调 recharge 的回溯，在 qwen case 跑通验证方法；代码留扩展点（`localize_*` 每 outcome 一函数 / outcome-spec 字典预留），之后加 M8 囤积 / M9 宪法劫持 / 治理停滞是局部增量。先验证后泛化（同现有 audit 模块建法）。

---

## 一、数据现状（已核实，pilot 直接用）

| 用途 | 文件 | 状态 |
|---|---|---|
| 行为时序（谁调了啥工具） | `runs/ew_multi/qwen-*/trace/trace_*.jsonl` | ✅ 有（OTel span，parent_span_id 因果树） |
| 死亡时序（能量耗尽轨迹） | `runs/ew_multi/qwen-*/replay/energy_agent_state.*.jsonl` | ✅ 有（per agent per step energy） |
| 治理/宪法变化 | `governance_env_state` replay + `env/GovernanceSpace/state/*.json` | ✅ 有 |
| 经济 | `economy_agent_state` replay | ✅ 有 |
| 现成归因种子 | `afi/audit/causal.py`（parent_span_id 因果树） | ✅ 要扩 |
| 现成时序种子 | `afi/audit/awi.py::compute_awi_timeline`（已读 energy_agent_state per step） | ✅ 要复用 |

**结论：pilot 不需要新跑数据，先用已有 3 个 qwen run 做归因 + 反事实。**

---

## 二、P0：事件图层（behavior-state-institution event graph）

**干什么**：把 trace 因果树 + replay env-state 时序 + 制度变化统一成一张可查询的事件图。

**节点三类**：
- **behavior**：`react.tool` span（agent_id, action, tick）——来自 trace，`causal.py` 已有
- **state-change**：env state 转移（agent X step T energy: 50→42；gini 0.1→0.4）——来自 replay，`awi.py::compute_awi_timeline` 已读
- **institution**：宪法 version 变化 / proposal / vote——来自 `governance_env_state`，`awi.py` M9 已读

**边三类**：
- **causal**：parent_span_id（trace 原生，`causal.py::ancestors` 已有）
- **temporal**：state@step T → action@step T+1（同一 agent 的时序邻接）
- **institution-effect**：vote → version bump / proposal → law change

**实现**：扩 `afi/audit/causal.py` 加 `build_event_graph(run_dir) -> EventGraph`，输出 JSON（`<run_dir>/attribution/event_graph.json`）。复用 `awi.py` 的 `_read_table` + `compute_awi_timeline`，不重写读盘。

**验收 P0**：3 个 qwen run 各出 event_graph.json；能查询"step 5 之前 agent 3 干了啥 + 能量多少"。

---

## 三、P1：第一骨牌定位 v0（localization，path-tracing 非 Shapley）

**干什么**：对 collapse 结局（某 agent 死于 step T / 人口崩溃），回溯找 first domino。

**v0 算法（M1-collapse 专用，path-tracing 非 Shapley——留 v1）**：
1. 对每个死 agent，从 `energy_agent_state` 拿能量轨迹，找**能量跌破"可恢复阈值"**（如 ≤ daily_consumption×2，再不充就必死）的首个 step T0。
2. 查 event graph：T0 之前该 agent 有没有 recharge 工具可用（env 提供 recharge）+ 有没有调（trace 查 `react.action == "recharge"`）。
3. **候选骨牌** = `(agent, T0, missed_recharge)`——"agent X 在 step T0 能充但没充，此后能量不可逆"。
4. 加一类候选：**"调了但被挡"**——若 trace 显示调了 recharge 但 `result.ok=False`（经济/治理挡），候选 = `(agent, T0, blocked_recharge, blocker)`。
5. 排序：earliest T0 优先 + 反事实影响大优先。

**扩展点**（v0 不实现，留结构）：`localize_first_domino(graph, outcome)` 的 `outcome` 参数 v0 只认 `m1_collapse`；预留 `m8_hoarding`/`m9_capture`/`governance_stagnation` 的 outcome-spec 槽，之后填。

**输出**：`<run_dir>/attribution/first_domino_candidates.json`，top-3 候选 + 证据链（ancestor chain + 能量轨迹）。

**验收 P1**：3 个 run 的 top-3 候选里，命中的是否含"漏调 recharge"或"调了被挡"。

---

## 四、P2：反事实 rerun（counterfactual world-branching）

**干什么**：对 top-1 候选骨牌，分支世界——重跑同一场景，在 T0 强制该 agent 调 recharge，看 collapse 还发不发生/延不延迟。

**实现**：
- 用现有 `run-ew scenarios/ew_full.yaml --model qwen-plus --run-dir runs/ew_multi/qwen-plus_cf` 跑 baseline 重放（同 model）。
- intervene 注入反事实：steps 里加一条 `"step T0: agent X 调 recharge(amount=50)"`（用现有 intervene 机制，正是它该干的）。
- 对比 baseline run vs counterfactual run 的 M1 存活曲线（`awi.py` M1 per-step alive count）。

**World Branching v0**：pilot 只做"单点干预单次重跑"的分叉（E3 的 World Branching Layer 完整版留后续）。反事实 reversal rate = 候选中干预后 collapse 延迟/不发生的比例。

**诚实**：AS re-run 非确定（LLM），同 model 也噪；mitigate = 对比存活曲线的**定性方向**（延迟/不发生），n 小不做显著性。

**验收 P2**：≥1 个 run 的反事实 rerun 显示 collapse 延迟 ≥2 step 或不发生。

---

## 五、P3：验收 + disentangle 结论

**验收**：P0+P1+P2 三步过 + §〇 退出条件 1/2 命中。

**disentangle 结论**（旗舰副产物，把 §七最大软肋变结论）：
- 若 P1 候选全是"漏调 recharge"（agent 没调）+ P2 强制调后活 → **能力 gap**（qwen 不自发用变异工具，非 alignment 缺陷）。
- 若 P1 出现"调了被挡"（经济/治理挡 recharge）+ P2 解挡后活 → **alignment/societal gap**（治理结构逼死）。
- 混合 → 报告比例。

**输出**：`phase1-first-domino/pilot-report.md`——3 run 归因表 + 反事实对照 + disentangle 结论。

---

## 六、文件清单（要建/改，按三层归属）

| 文件 | 动作 | 层 | 说明 |
|---|---|---|---|
| `afi/audit/causal.py` | 扩 | ①归因层 | 加 `build_event_graph(run_dir)`——后端无关，读 trace+replay |
| `afi/audit/attribution.py` | 新建 | ①+③ | `localize_first_domino`（M1-collapse v0 + 扩展点）+ orchestrator `attribute(run_dir, outcome)` |
| `afi/world/counterfactual.py` | 新建 | ②反事实 rerun | `counterfactual_rerun(scenario, domino)`——**AS 耦合**，调 run-ew 重跑；Concordia 后端留接口 |
| `afi/cli.py` | 加子命令 | ③ | `attribution <run_dir> [--counterfactual]` |
| `runs/ew_multi/qwen-*_cf/` | 新建 | ②输出 | 反事实 rerun 输出 |
| `phase1-first-domino/pilot-report.md` | 新建 | — | 验收报告 |

---

## 七、诚实约束

- **v0 是 path-tracing 非 path Shapley**——够 pilot，不 claim 最优归因。
- AS re-run 非确定 → 反事实比"定性方向"，n=3 不做显著性。
- intervene helper 仍 flaky → 反事实注入正是它该干的；若 flaky，记 seed_did_not_fire 不假装。
- 只用 qwen 族 3 run → 不能 claim 跨模型，只 claim"qwen 族 collapse 的归因"。
- qwen 崩溃可能纯 tool-calling gap → disentangle 结论若为"能力 gap"，不假装成"alignment 发现"。
- **②反事实 rerun 引擎 AS 耦合**——不 claim 后端可换（Concordia 留接口未实现，同 strategy.md 的诚实定位）；归因层①才是真复用。
