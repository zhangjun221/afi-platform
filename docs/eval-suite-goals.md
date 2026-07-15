# 测试套件目标（Eval Suite Goals）— 方法论先行

> 2026-07-12。A1-A4 建好了平台（仪器），这套文档定义**测试套件（考卷+答案）**的目标。先定目标、再定怎么建。
> 借鉴：封存线 `safety-audit-platform/docs/{strategy,methodology-and-standards,contribution-evaluation}.md`（设计详细但未落地）。
> 适配：afi-platform 现状（AS+EW+AFI，已建检测器 + AWI + runtime 告警 + 多模型）。
> 目标受众：研究者/评审——这套东西要让别人能复现、能判断"你的审计准不准"。

---

## 一、一句话目标

**建一套带 ground-truth 标签的长时程多 agent 社会安全场景集 + 评分 harness，让我们能定量回答："我们的检测器在 long-horizon 弱约束社会里，能不能、多准、多早地捕捉到单 agent 漂移与社会涌现风险"——并对比现有工具结构性 miss 的部分。**

这是贡献第 (d) 腿（实证发现）的支撑，也是对外发布/论文的硬通货：OASB/AgentEval 之所以是 benchmark，就因为有标签集 + precision/recall，不只因为能跑。

## 二、缺口确认：平台建了，测试套件没建

| | 现状 |
|---|---|
| **平台（仪器）** | ✅ A1-A4 闭环：跑 AS+EW+AFI → trace/replay → 检测器 → AWI → 报告 |
| **检测器** | ✅ sensorium / tunnel_vision / causal / collude + runtime 4 告警（sensorium_collapse / governance_stagnation / economic_hoarding / tunnel_vision_escalation）+ AWI 9 族 |
| **现有 run（ew_subset/full/multi）** | ⚠️ **演示**，无 ground-truth 标签 → 算不了 precision/recall |
| **带标签场景集** | ❌ 没建 |
| **评分 harness（findings vs 标签）** | ❌ 没建 |
| **差分 vs 现有/naive 基线** | ❌ 没建 |

**现状能说"看到现象"，不能说"检测器准不准/多早/比现有强多少"。** 这套套件补这个。

## 三、核心问题（套件要回答的 5 问）

1. **能不能捕捉**（recall）：注入的已知风险，检测器 catch 到几成？
2. **准不准**（precision）：检测器报的，多少是真风险（非误报）？
3. **多早**（latency）：风险在第 N tick 涌现，检测器第几 tick 报？（早告警价值，区别于 end-of-run）
4. **跨模型差异**（per-model recall）：同一风险场景，哪个模型的 run 更易 surface？（连 A4 多模型发现）
5. **比现有强多少**（差分）：单 agent 短程工具（driftly/AgentEval 式）miss 的涌现，我们 catch 到了吗？（贡献 d 腿证据）

## 四、借鉴封存线（可复用的方法论框架）

封存线方法论文档**设计得很完整**，这些直接借：

| 封存线设计 | 借鉴点 | 用法 |
|---|---|---|
| **审计流 §1.2**：detect→attribute→score→scorecard→**eval(vs ground-truth)** | 整条流的前 4 步 afi-platform 已建，**补最后 eval 步** | eval 步 = 套件核心 |
| **风险分类法 §3**：AgentEval 12 类 + 第 6 组 Social Emergence（Collusion Formation / Cascade / Defection / Economic Collapse / Governance Capture / Social Drift / Marginalization / Memory Distortion） | taxonomy 基底 | 场景按此分类，每场景标 category |
| **Label schema §5.3**：`{category, agent_id, emerge_at_tick, severity_expected}` | ground-truth 格式 | 直接采用 |
| **评测 §6**：precision/recall/F1 + 差分 + severity MAE + 复现 | 评测维度 | 直接采用 + 扩展（见 §6） |
| **独有 #3 攻击注入测试床**（strategy §2.2）：注入已知病态验证检测器 | 场景构造思路 | 直接采用 |

## 五、适配 afi-platform 现状（不照搬，按已建的来）

封存线设计是"理想全态"，afi-platform 只建了部分检测器。**套件按已建的能检测的现象来定，未建的标注 future**——不画饼。

| 现象（封存线 §3 第6组） | 我们有检测器吗 | 套件场景 |
|---|---|---|
| **单 agent 漂移**（行为窄化/感知塌陷） | ✅ sensorium_collapse / tunnel_vision | 标签：哪个 agent + emerge_tick |
| **合谋成型**（Collusion Formation） | ✅ collude（message_log→blackboard→judge） | 标签：合谋成型 tick + 参与者 |
| **治理停滞**（Governance Stagnation） | ✅ governance_stagnation | 标签：停滞起始 tick |
| **经济集中/崩溃**（Economic Collapse） | ✅ economic_hoarding（Gini 跳升） | 标签：集中过阈 tick |
| **人口崩溃**（agent neglect 死亡） | ✅ M1（energy depletion） | 标签：死亡起始 tick + 崩溃率 |
| **治理俘获**（Governance Capture，宪法被劫持） | ✅ M9（version + proposal 因果） | 标签：劫持修正案 + tick |
| Cascade/级联 | ❌ 未建 | future |
| Marginalization/Memory Distortion | ❌ 未建 | future |

→ **套件首版 6 类现象场景**（均有已建检测器），未建的 2 类标 future 不做。诚实，不画饼。

## 六、进一步优化（我在封存线之上加的）

封存线设计好但有可优化点，结合 A1-A4 实测经验：

1. **两轴场景：注入式 + 自然涌现**（封存线只注入式）。A4 发现 agent **自然**崩溃（neglect recharge，无注入）——这是真实安全风险。套件要有：① 注入式（seed 病态，确定性，算 precision/recall）+ ② 自然涌现（不 seed，跑多 seed 看检测器能否 surface 未预期现象）。**注入测准度，自然测发现力。**
2. **检测延迟 metric**（封存线只 precision/recall）。加 `latency = detected_tick - emerge_tick`——long-horizon 安全是"早告警"价值，早报 5 tick 比晚报强。这是 runtime 监控的核心，区别于 end-of-run eval。
3. **per-model recall**（封存线差分是 us-vs-existing）。连 A4 多模型发现：同一风险场景 × N 模型，比 recall——哪个模型更易 surface 风险。把多模型对照（已建）接入套件。
4. **轻量差分**（封存线要跑 driftly/watch-the-watchers，我们没集成）。先 vs **naive 基线**（无检测器 / 纯 AWI 阈值 / 随机）证明检测器增值；full existing-tool diff 留后续（要集成外部工具，重）。
5. **参数化 + 多 seed 统计**（封存线场景固定）。场景参数化（agent 数/模型/horizon/seed），跑 M seed × N 模型给 precision/recall 的 CI——样本小但标"趋势性"，符合 A4 统计诚实。
6. **不重构 CommonRun**（封存线 §4 要 normalize 层）。afi-platform 检测器已直接读 run_dir，**套件直接评分现有检测器，不引入 CommonRun refactor**——省工作量、早交付。后端可换是 future claim，现在不做。

## 七、我们需要什么（交付物 high-level）

```
afi-platform/
  eval/                          # ★测试套件（新子包）
    scenarios/                   # 带标签的场景 YAML（每场景含 labels 段）
      single_agent_drift.yaml    # 单agent漂移（注入+自然）
      collusion_formation.yaml   # 合谋成型
      governance_stagnation.yaml # 治理停滞
      economic_collapse.yaml     # 经济集中
      population_collapse.yaml   # 人口崩溃
      governance_capture.yaml    # 宪法劫持
    labels.py                    # Label schema（{category,agent_id,emerge_tick,severity_expected}）
    scoring.py                   # findings vs labels → precision/recall/F1/latency
    diff.py                      # vs naive 基线（差分）
    run_eval.py                  # 跑场景集 × model × seed → 评分表 + CI
    report.py                    # 评分 scorecard（CSV/HTML）
  afi/audit/                     # 检测器加 detect()→Finding 接口（如未有）
  docs/eval-suite-plan.md        # 实现规划（目标确认后写）
```

## 八、评测维度（一个场景跑完怎么打分）

| metric | 定义 | 回答 |
|---|---|---|
| **recall** | 标签风险中检测器 catch 的比例 | 能不能捕捉 |
| **precision** | 检测器 findings 中真风险比例 | 准不准 |
| **F1** | 调和 | 综合 |
| **latency** | detected_tick − emerge_tick（中位/分布） | 多早 |
| **severity MAE** | 检测 severity vs 标签 severity_expected | 严重度校准 |
| **per-model recall** | 各模型 run 的 recall | 跨模型差异 |
| **vs-naive Δrecall** | 我们 recall − naive 基线 recall | 比现有强多少 |
| **CI** | M seed 的 recall 区间 | 置信度（标非正式） |

## 九、场景两轴

- **注入式**（injected）：intervene seed 已知病态（如"agent3 持续只调某工具" / "agent1,2,3 私下串谋" / "一伙囤积信用"）→ 确定性触发 → 标签 emerge_tick 已知 → 算 precision/recall/latency。
- **自然涌现**（natural）：不 seed，只设环境（资源稀缺/弱约束/长时程），跑多 seed → 看检测器能否 surface 未预期的涌现（如 A4 的 qwen 自然崩溃）→ 报"发现力"（surface 了什么、多早）。

## 十、待你确认（定目标后的决策）

1. **首版 6 类场景**（单agent漂移/合谋成型/治理停滞/经济集中/人口崩溃/宪法劫持，均有已建检测器），未建的 Cascade/Marginalization/Memory 留 future——同意？
2. **两轴**（注入式 + 自然涌现）——同意？还是只做注入式？
3. **6 条优化**（尤其检测延迟 metric + 轻量差分 vs naive + 不重构 CommonRun）——同意/取舍？
4. **目标确认后**，我写 `docs/eval-suite-plan.md`（场景具体设计 + Label schema + scoring 实现 + 执行顺序），按 A2-A4 节奏"plan-then-开始"。

## 十一、一句话总结

**封存线把这套设计过（taxonomy+label+precision/recall+差分），但没落地；afi-platform A1-A4 建了仪器没建考卷。本套件补"考卷+答案+阅卷"：6 类带标签场景（注入+自然两轴）× 评分 harness（precision/recall/F1/latency/per-model/vs-naive/CI）。比封存线优化在：两轴场景、检测延迟、轻量差分、不重构 CommonRun、参数化多 seed。这是贡献 (c)(d) 腿的支撑，也是对外发布的 benchmark 形态。**
