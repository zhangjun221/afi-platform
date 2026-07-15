# A2 规划 — EW 设定子集翻译 + "AFI on AS" 成立验证

> 2026-07-10。A1 review 完成、代码干净后的下一步规划。
> 依据：`docs/architecture-and-roadmap.md` 第四节（EW 翻译映射）+ A2 段。
> 源：EW `repo_analysis/Emergence-World/`（manifesto/constitution/profiles/landmarks/tools/docs）。
> 目标：AS `custom/envs/` 热加载 + 内置 EconomySpace/SimpleSocialSpace 配置 + agent_specs。

---

## 0. A2 的"完成"定义（一句话）

把 EW 的一个**可运行子集**（manifesto + 种子宪法 + 治理投票 + 经济信用 + 几个地标 + 几个 agent 人设）翻译成 AS 能跑的 env 模块 + agent profiles + 场景 YAML，跑一轮短实验，**看到 EW 式社会行为**（提案/投票/消息/经济流动），且审计层（含读 message_log 的 collude）正常出报告。即"AFI on AS"成立。

## 1. 范围（in / out）

**In（A2 做）**
- EW manifesto + 种子宪法（4 条 Article）→ 数据 + 治理 custom env
- EW 治理（提案/投票/修宪，70% 超多数）→ 自定义 `GovernanceSpace`（custom env，AS 无原生）
- EW 经济（ComputeCredits）→ 配置内置 `EconomySpace`（不造轮子）
- EW 社交 + message_log 持久化 → 把封存线补丁迁成 custom env `SimpleSocialSpaceAuditable`（reinstall-safe，A1 的 install_to_as.sh 降级为可选）
- EW 几个地标（3-5 个）→ 轻量 `LandmarkSpace`（custom env，`list_landmarks`/`get_landmark_info`，**不依赖地图/pyproj**，保持 stdlib+AS 可跑）
- EW agent 人设（5 个：Anchor/Anvil/Blackbox/Flora/…）→ AS agent_specs
- 场景 YAML（声明式）+ lite loader（YAML→init_config+steps）
- CLI `run-ew <yaml>` 子命令
- 一轮短跑（5 agent × 8 tick）+ 审计

**Out（A3/A4 做，A2 不碰）**
- AWI 11 重算（A3）
- runtime_monitor / scenario_designer 端口（A3）
- 120+ 工具全量翻译、36 地标全量、地图 MobilitySpace（A4）
- 完整 pydantic scenario DSL schema（A4；A2 用 lite loader 即可）
- 15 天 × 多模型对标 Season1（A4）

## 2. 交付物清单

```
afi-platform/
  afi/world/
    __init__.py            # 已占位 → 填导出
    constitution.py        # EW manifesto + 种子宪法 → Python 数据 + 文本
    economy.py             # EW ComputeCredits → EconomySpace persons 配置
    governance.py          # EW 治理规则数据（70% 超多数等）
    landmarks.py           # EW 地标子集 → 数据（标题/描述/可做之事）
    profiles.py            # EW 5 agent 人设 → AS agent_specs dicts
    scenario.py            # build_ew_subset_config(): YAML→init_config+steps
  custom/
    envs/
      governance_space.py          # GovernanceSpace(EnvBase): 提案/投票/修宪
      landmark_space.py            # LandmarkSpace(EnvBase): list/get 地标
      simple_social_space_auditable.py  # 迁移补丁: SimpleSocialSpace+message_log
  afi/cli.py              # +run-ew 子命令
  scenarios/ew-subset.yaml # 声明式场景（agents/world/steps）
  docs/a2-plan.md          # 本文档
```

> custom/ 放在 afi-platform 根（非 afi/ 内），因 AS registry 从 `<workspace>/custom/envs/` 热加载，adapter 跑 EW 时设 `WORKSPACE_PATH` 指向 afi-platform 根。

## 3. 各模块设计要点

### 3.1 constitution.py — 纯数据
- `MANIFESTO_TEXT`：EW manifesto 全文（Rule 1-3 + purpose 段），agent 经治理/地标 env 的 `get_manifesto` 工具读到。
- `SEED_ARTICLES`：4 条 Article（Non-Finality / Civic Participation / Equality Through Contribution / Mutable Identity）→ list[dict] `{title, body, amendment_rule}`。
- `GOVERNANCE_RULES`：`{supermajority: 0.7, proposer_votes_for: true, silence_is_violation: true}`。
- 来源：直接读 EW `agent_constitution/agent_manifesto.md` + `constitution.md` 文本（不 import EW，EW 无代码）。

### 3.2 economy.py — 配置生成
- `build_economy_persons(agent_names, initial_credits=100)` → list[dict] 合 `EconomyPerson` schema（id/currency/skill/consumption/income）。
- currency 即 EW ComputeCredits；skill 取自 EW profile 的 Role；consumption/income 给合理初值。
- 产 EconomySpace 的 `persons` kwarg。

### 3.3 governance_space.py — custom env（核心新增）
- `GovernanceSpace(EnvBase)`，module_type `"GovernanceSpace"`。
- 状态：`articles`(list) + `proposals`(list[id, proposer, title, new_text, votes]) + `constitution_version`。持久化到 `state/GOVERNANCE_STATE.json`（仿 EconomySpace 的 `atomic_write_text`），并 `register_table` 一张 `governance_events` 给 replay/审计。
- 工具（`@tool`）：
  - `get_constitution(agent_id)` readonly observe → 当前宪法全文
  - `get_manifesto(agent_id)` readonly observe → manifesto 文本
  - `propose_amendment(agent_id, article_title, new_text)` → 建提案，提案者票计 implicit "for"
  - `vote(agent_id, proposal_id, position)` → 投票 for/against
  - `get_active_proposals(agent_id)` readonly → 待表决提案 + 当前票数
  - `tally(agent_id, proposal_id)` readonly → 达 70% 即通过、改 articles、版本+1
- `observe()` → 宪法摘要 + 活跃提案数。
- 初始化接受 `seed_articles` + `governance_rules` kwargs。

### 3.4 landmark_space.py — custom env（轻量）
- `LandmarkSpace(EnvBase)`，module_type `"LandmarkSpace"`。
- 初始化接受 `landmarks`(list[{name, description, things_to_do}])，来自 EW 3-5 个地标 markdown。
- 工具：`list_landmarks(agent_id)` readonly、`get_landmark_info(agent_id, name)` readonly。
- 不涉及坐标/地图（A4 再接 MobilitySpace）。

### 3.5 simple_social_space_auditable.py — 补丁迁移
- 把 `backend_patches/simple_social_space_patched.py` 的 5 处 `[research patch]` 逻辑重打包成 custom env `SimpleSocialSpaceAuditable(EnvBase)`，module_type `"SimpleSocialSpaceAuditable"`，**与内置 SimpleSocialSpace 并存**。
- message_log 落盘 `message_log.jsonl`（与封存线审计 collude 读的格式一致）。
- install_to_as.sh 保留（给想给内置 social 也加日志的场景），但 EW 场景默认用 custom 这版 → reinstall-safe。

### 3.6 profiles.py — 人设翻译
- `EW_PROFILES`：5 个 agent（Anchor 冲突调解 / Anvil 能力架构 / Blackbox 情报 / Flora 资源策略 / +1 个），取自 EW `agent_profiles/README.md`。
- `build_agent_specs(profiles, model)` → AS agent_specs list：`{agent_id, agent_type:"PersonAgent", kwargs:{id, profile:{name, role, personality, north_star}}}`（与 commons 同 schema，已验证可跑）。
- north_star 用 EW 原文；manifesto 不塞 profile（经 env 工具读，避免 prompt 膨胀）。

### 3.7 scenario.py — lite loader
- `load_scenario(yaml_path)` → dict（pyyaml，已是 optional extra `[yaml]`）。
- `build_ew_subset_config(scenario_dict, out_dir)` → 写 init_config.json + steps.yaml（复用 `agentsociety.py` 的 `_yaml_line` 序列化），返回两路径。
- 场景 YAML schema（lite，无 pydantic）：
  ```yaml
  world:
    initial_credits: 100
    seed_articles: full   # 用 constitution.py 的 4 条
    landmarks: [bookworm, ad_tower, agent_billboard]
  agents: [Anchor, Anvil, Blackbox, Flora, Beacon]
  steps:
    - {type: step, count: 8}
  model: null
  ```

### 3.8 cli.py — run-ew
- 加 `run-ew` 子命令：`--scenario <yaml> --run-dir <dir> [--model] [--audit] [--out]`。
- 流程：`load_scenario` → `build_ew_subset_config` → `AgentSocietyAdapter.run(...)`（设 `WORKSPACE_PATH`=afi-platform 根，让 custom/envs 被发现）→ （可选）`_audit_run`。

## 4. 关键技术决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| 治理 env | 自定义 custom env（非内置） | AS 无原生治理；custom 热加载即为此设计 |
| 经济 env | 配置内置 EconomySpace | 已有，不造轮子 |
| 社交 env | custom `SimpleSocialSpaceAuditable`（迁补丁） | reinstall-safe + 给 collude 审计读 message_log |
| 地标 env | 轻量 custom，不接地图 | 保持 stdlib+AS 可跑；地图 A4 |
| custom 发现机制 | adapter 设 `WORKSPACE_PATH`=平台根 | AS registry 读该 env 找 `custom/envs/`；不污染 AS 安装 |
| scenario DSL | lite（YAML→dict→build），不上 pydantic | A2 验证用；完整 schema A4 |
| agent 数 / tick | 5 / 8 | 与 commons 同规模，短跑验证 |
| 模型 | null（用 AS .env 默认） | A2 验证设定翻译，多模型 A4 |

## 5. 验收标准（Checklist）

**代码完整性**
- [ ] `afi/world/{constitution,economy,governance,landmarks,profiles,scenario}.py` 全部 import 成功（`python -c "import afi.world"`）。
- [ ] `custom/envs/{governance_space,landmark_space,simple_social_space_auditable}.py` 语法 OK、各自 `EnvBase` 子类。

**AS 热加载**
- [ ] EW 场景 init_config 里 `module_type: GovernanceSpace` / `LandmarkSpace` / `SimpleSocialSpaceAuditable` 被 AS registry 解析到（run 不报 "module not found"）。

**端到端跑通**
- [ ] `python -m afi run-ew scenarios/ew-subset.yaml --run-dir runs/ew_subset --audit` 完成，AS run 退出码 0。
- [ ] `runs/ew_subset/` 下有 `trace_*.jsonl` + `replay/` + `agents/agent_*/` + `message_log.jsonl`（社交 env 日志落盘）。

**EW 式行为（核心）**
- [ ] trace 里至少 1 个 `propose_amendment` 工具调用。
- [ ] trace 里至少 1 个 `vote` 工具调用。
- [ ] message_log.jsonl 非空（agent 间有 send_message）。
- [ ] EconomySpace 状态变化（至少 1 agent currency 变化，replay 可查）。

**审计层正常**
- [ ] `python -m afi.audit runs/ew_subset --full` → HTML 报告生成，sensorium/tunnel/causal/collude 四块都有内容（collude 读到 message_log）。

**无回归**
- [ ] `python -m afi.audit run_commons --full` 仍 1094 span、sensorium 17.7%（A1 基线不变）。
- [ ] `python -m afi.cli --help` 显示 `{audit, run-as, run-ew}`。

**文档**
- [ ] DEVLOG 记轮次 6（A2 执行）。
- [ ] README 更新 A2 完成态 + 用法。
- [ ] 本文（a2-plan.md）如实际偏离规划则补"执行偏差"注。

## 6. 风险与兜底

| 风险 | 兜底 |
|---|---|
| `WORKSPACE_PATH` 不被 AS CLI 识别 → custom env 找不到 | 兜底：adapter 把 `custom/envs/*.py` 复制进 `run_dir/custom/envs/`（run_dir 即 workspace 根），再试 |
| GovernanceSpace state 持久化与 Ray actor 冲突 | 仿 EconomySpace 已验证的 `atomic_write_text` + `register_table` 路径，不另起炉灶 |
| agent 不主动提案/投票（LLM 没调用治理工具） | profile north_star 显式指向治理参与（EW Article 2 已要求）；tick 提到 8 给足轮次；仍不触发则 profiles.py 加 `governance_prompt` hint |
| message_log 格式与封存线 collude 读法不一致 | simple_social_space_auditable 沿用补丁原落盘格式（已与 collude 对齐过） |
| glm-5.2 分类器间歇阻断 Bash | bypass 模式 + 重试；run-ew 一条命令减少交互 |

## 7. 执行顺序（建议）

1. constitution.py + economy.py + landmarks.py + profiles.py（纯数据/配置，无 AS 依赖，可先写+单元自检）
2. governance_space.py + landmark_space.py（custom env，仿 simple_env.py 结构）
3. simple_social_space_auditable.py（迁补丁）
4. scenario.py + scenarios/ew-subset.yaml（拼装）
5. cli.py run-ew + adapter 设 WORKSPACE_PATH
6. 跑 → 看行为 → 审计 → 验收 checklist 逐项打勾
7. DEVLOG + README

## 8. 与路线的关系

A2 验证"AFI on AS"成立后，A3（审计+AWI+runtime/scenario 端口）和 A4（长时程对标 Season1）才有了跑在上面的真实 EW 式 run。A2 是后续一切的经验证据基础。
