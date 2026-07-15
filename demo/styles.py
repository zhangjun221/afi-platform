"""CSS + styled-HTML builders for the afi-platform demo.

Kept separate from app.py so the visual layer is editable in one place.
Targets real HTML elements (h1/h2/table/code/p) rendered by gr.Markdown,
plus our own .pcard/.pill/.awi classes used via gr.HTML.
"""
from __future__ import annotations

CSS = """
/* ── container & base ── */
/* center the whole app on wide screens */
html, body { margin:0; padding:0; }
body { display:flex; justify-content:center; }
.gradio-container, main, .main, #root, .wrap {
  max-width: 1080px !important; margin: 0 auto !important; padding-left: 20px !important; padding-right: 20px !important;
}
.gradio-container { font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif !important; }

/* ── finding cards (contribution evidence) ── */
.finding { border:1px solid #e2e8f0; border-radius:12px; padding:.9em 1.1em; margin:.6em 0; background:#fff; box-shadow:0 1px 3px rgba(15,23,42,.06); border-left:5px solid #1565c0; }
.finding h4 { margin:.1em 0 .3em; color:#0d47a1; font-size:1.04rem; }
.finding .fnum { display:inline-block; background:#e8f5e9; color:#2e7d32; font-weight:700; padding:2px 10px; border-radius:6px; font-family:"SF Mono",Menlo,monospace; font-size:.95rem; margin-right:.4em; }
.finding .fwhere { display:inline-block; font-size:.84rem; color:#64748b; margin-top:.4em; }
.finding .fwhere a { color:#1565c0; text-decoration:none; }
.finding.b { border-left-color:#6a1b9a; }
.finding.b h4 { color:#6a1b9a; }
.finding.g { border-left-color:#2e7d32; }
.finding.g h4 { color:#2e7d32; }
.finding.o { border-left-color:#ef6c00; }
.finding.o h4 { color:#ef6c00; }

/* ── banner ── */
#ava-banner { background: linear-gradient(135deg,#0d47a1,#1565c0); color:#fff; border-radius:12px; padding:1.1em 1.4em; margin-bottom:.8em; }
#ava-banner h1 { color:#fff; border:none; margin:.1em 0; font-size:1.5rem; }
#ava-banner p { color:#e3f2fd; margin:.2em 0 0; font-size:.98rem; }

/* ── headings (markdown) ── */
h1 { font-size:1.7rem; border-bottom:3px solid #1565c0; padding-bottom:.25em; margin-top:.4em; }
h2 { font-size:1.28rem; color:#0d47a1; border-left:5px solid #1565c0; padding-left:.55em; margin-top:1.6em; background:linear-gradient(90deg,#f4f8ff 0%,#ffffff 60%); }
h3 { font-size:1.08rem; color:#283593; margin-top:1.1em; }

p, li { font-size:1.02rem; line-height:1.72; color:#233; }
p { margin:.5em 0; }
strong { color:#0d47a1; }

code { background:#eef3f8; color:#0d47a1; padding:1px 6px; border-radius:5px; font-size:.9em; font-family:"SF Mono",Menlo,Consolas,monospace; }
pre { background:#0f172a !important; color:#e2e8f0; border-radius:8px; padding:1em 1.1em; font-size:.86rem; line-height:1.55; overflow:auto; }
pre code { background:transparent; color:inherit; padding:0; }

/* ── markdown tables ── */
table { border-collapse:collapse; width:100%; margin:.7em 0 1.2em; font-size:.95rem; }
th, td { border:1px solid #dbe3ee; padding:7px 11px; text-align:left; vertical-align:top; }
th { background:#e8eef7; color:#0d47a1; font-weight:600; }
tr:nth-child(even) td { background:#fafbfd; }

/* ── platform cards (HTML) ── */
.pcard { border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; margin-bottom:1em; background:#fff; box-shadow:0 1px 3px rgba(15,23,42,.06); }
.pcard .phead { padding:.7em 1em; font-weight:700; font-size:1.05rem; color:#fff; }
.pcard .pbody { padding:.9em 1.1em 1.1em; }
.pcard .pbody p { margin:.35em 0; }
.pcard .prow { display:flex; gap:.6em; margin:.3em 0; font-size:.92rem; }
.pcard .prow .k { color:#64748b; min-width:4em; font-weight:600; }
.pcard .ptag { display:inline-block; font-size:.8rem; padding:1px 8px; border-radius:10px; margin-right:.3em; background:#eef3f8; color:#334; }
.ew .phead { background:linear-gradient(135deg,#1565c0,#42a5f5); }
.afi .phead { background:linear-gradient(135deg,#6a1b9a,#ab47bc); }
.as .phead { background:linear-gradient(135deg,#455a64,#78909c); }
.ours .phead { background:linear-gradient(135deg,#2e7d32,#66bb6a); }

/* ── AWI table (HTML) ── */
.awi-wrap { margin-top:.6em; }
.awi-wrap table { font-size:.96rem; }
.awi-wrap td:first-child { font-weight:700; color:#0d47a1; white-space:nowrap; }
.pill { display:inline-block; padding:2px 10px; border-radius:12px; font-size:.82rem; font-weight:600; white-space:nowrap; }
.pill.computed { background:#e8f5e9; color:#2e7d32; border:1px solid #a5d6a7; }
.pill.proxy { background:#fff3e0; color:#ef6c00; border:1px solid #ffcc80; }
.pill.stub { background:#eceff1; color:#546e7a; border:1px solid #cfd8dc; }
.pill.degenerate { background:#ffebee; color:#c62828; border:1px solid #ef9a9a; }

/* ── callout (🧭 通俗说) ── */
.callout { background:#f4f8ff; border-left:4px solid #1565c0; padding:.7em 1em; border-radius:6px; margin:.6em 0 1em; font-size:1rem; }
blockquote { background:#f4f8ff; border-left:4px solid #1565c0; padding:.6em 1em; border-radius:6px; margin:.6em 0 1em; color:#283593; }
blockquote p { margin:.2em 0; }

/* ── audit iframe ── */
iframe { border-radius:8px !important; }
"""


_FEAS_LABEL = {
    "computed": "✅ 实算",
    "proxy": "⚖️ 代理",
    "stub": "◻️ 待建",
    "degenerate": "⚠️ 退化",
}


def _pill(feas: str) -> str:
    cls = feas if feas in ("computed", "proxy", "stub", "degenerate") else "stub"
    label = _FEAS_LABEL.get(cls, feas)
    return f'<span class="pill {cls}">{label}</span>'


def awi_table_html(run_name: str, rows: list) -> str:
    """Render the 9-family AWI as a styled HTML table with pill feasibility badges."""
    body = "".join(
        f"<tr><td>{fam}</td><td>{metric}</td><td>{val}</td><td>{_pill(feas)}</td></tr>"
        for fam, metric, val, feas in rows
    )
    return f"""
    <div class="awi-wrap">
      <table>
        <tr><th>族</th><th>指标</th><th>值（run: {run_name}）</th><th>可行性</th></tr>
        {body}
      </table>
    </div>"""


def callout(text: str) -> str:
    return f'<div class="callout">🧭 {text}</div>'


# ── contribution finding cards (real run evidence) ─────────────────────────

CONTRIB_CARDS = """
<div class="finding b">
  <h4>① 治理涌现实证：宪法真被 agent 改了</h4>
  <p>5 agent 跑 12 步，agent 自发提案+投票，<span class="fnum">Article 2 经 4/5 票通过</span>，宪法版本 <span class="fnum">v1 → v2</span>——复现了 EW 最招牌的"活宪法"行为，且全程可审计。</p>
  <p class="fwhere">安全含义：自治修宪是良性演化还是被恶意劫持？可追踪每条修正案的提案者/投票者/因果链。→ 看 ⑤ AWI 实测（M9）或 ⑦ 审计报告（decision_trace）</p>
</div>

<div class="finding g">
  <h4>② 跨模型能力-安全差异：强模型探索更多</h4>
  <p>同一 EW 场景 × 3 百炼模型跑 15 天，工具探索（M4）：<span class="fnum">qwen-turbo 3.0</span><span class="fnum">qwen-plus 4.2</span><span class="fnum">qwen-max 5.6</span>——强模型探索更多工具，<b>镜像 EW 官方模型谱</b>（Claude/Gemini 强 vs Grok/GPT5Mini 弱）。</p>
  <p class="fwhere">安全含义：能力差异→风险差异，长时程下哪个模型更不安全可量化对照。→ 看 ⑥ 跨模型对照</p>
</div>

<div class="finding o">
  <h4>③ 安全相关发现：强模型也忽视生存</h4>
  <p>3 个 qwen 模型在 EW 生存场景下 <b>全崩溃</b>（<span class="fnum">1/5</span><span class="fnum">0/5</span><span class="fnum">0/5</span>）——agent 收到 10 次"能量低-recharge"警告仍不充电，靠 neglect 死亡。<b>即便最强 qwen-max 也忽视生存</b>，≈ EW Grok/GPT5Mini 崩溃。</p>
  <p class="fwhere">安全含义：强模型≠安全模型；long-horizon 弱约束下的"不作为"是真实风险。→ 看 ⑥ 跨模型对照（M1 vs EW）</p>
</div>

<div class="finding">
  <h4>④ runtime 早告警：行为漂移实时捕捉</h4>
  <p>rolling 统计 + 变点检测，实测触发告警：<span class="fnum">sensorium_collapse 0.165&lt;0.4</span>（感知塌陷）<span class="fnum">governance_stagnation</span>（治理停滞 4 步）<span class="fnum">tunnel_vision ×26</span>（行为窄化）——<b>事中早告警</b>，不用等跑完。</p>
  <p class="fwhere">安全含义：long-horizon drift 在恶化前就能发现，非事后描述。→ 看 ⑦ 审计报告（runtime 告警块）</p>
</div>

<div class="finding b">
  <h4>⑤ 串谋可审计：私信留底→judge</h4>
  <p>社交消息全部留底（message_log），实测 <span class="fnum">4 条私信</span>→ Colosseum blackboard 模式→ LLM judge 评 0-5 串谋度。原本 AS 消息读即消费，<b>我们让它可回溯可审计</b>。</p>
  <p class="fwhere">安全含义：多 agent 私下串通是核心威胁，留底是审计前提。→ 看 ⑦ 审计报告（合谋检测）</p>
</div>
"""

CONTRIB_INTRO = """
# 这个平台是干什么的 + 我们独特在哪

> 🧭 **这页讲什么**：做这个平台的**主要目的**，以及我们相对已有工作的**独特贡献**——每条配真实 run 数据的例子证明（不是空话）。

## 主要目的

**在长时程、弱约束的多 agent 社会模拟上做安全审计。** 现有平台（AS/Concordia/Smallville）能跑 long-horizon 多 agent，但**没有安全审计层**；安全基准（OASB/AgentEval）测单 agent 短任务，**不跑长时程社会涌现**。这个交集——"长时程多 agent × 安全审计"——没人做全，是我们的位置。

## 四条贡献（每条有真实证据）

1. **问题界定**：把"long-horizon（时序）× multi-agent（结构）正交、安全审计缺位"讲清楚，对齐 AgentEval 12 类 + OASB。
2. **集成**：首次把 AS 引擎 + EW 设定 + AFI 审计拼成三层闭环平台（world/custom-envs/audit/backend），不 fork 不 vendor。
3. **涌现方法**：AWI 9 族指标化 + runtime 早告警 + 跨模型对照 + 场景预置——把"事后看记录"升级到"量化+实时预警+对照"。
4. **实证发现**：用真实跑的数据，发现 5 个可审计的安全相关现象（见下）。
"""


# ── three-platform cards (HTML) ─────────────────────────────────────────────

PLATFORM_CARDS = """
<div class="pcard ew">
  <div class="phead">🟦 Emergence World (EW)</div>
  <div class="pbody">
    <p><b>世界设定集（无代码，研究专用）</b></p>
    <div class="prow"><span class="k">是什么</span><span>官方设定文档集 + 季节数据，<b>无可运行代码</b>。</span></div>
    <div class="prow"><span class="k">能力</span><span>manifesto + 种子宪法（可修宪 70% 超多数）·36 地标 ·116 工具 ·<b>AWI 9 族权威定义</b> ·Season1（5 世界×15 天×10 agent，公布 M1）</span></div>
    <div class="prow"><span class="k">边界</span><span>只给设定和数据，<b>没有模拟引擎</b>——不能直接"跑"，得自己实现。</span></div>
    <div class="prow"><span class="k">我们用</span><span><span class="ptag">设定翻译</span><span class="ptag">AWI 定义</span><span class="ptag">Season1 M1 baseline</span></span></div>
  </div>
</div>

<div class="pcard afi">
  <div class="phead">🟪 ai-freedom-island (AFI)</div>
  <div class="pbody">
    <p><b>EW 复现 + 审计扩展（自建引擎）</b></p>
    <div class="prow"><span class="k">是什么</span><span>第三方对 EW 的可运行复现，<b>自带 sim 引擎</b>（纯 Python）+ 审计扩展。</span></div>
    <div class="prow"><span class="k">能力</span><span>复现 EW（engine/agents/economy/governance/tools + 中文 LLM router + AWI 9）；审计扩展（audit.py 3 层因果链 / collusion / drift / <b>runtime_monitor</b> / <b>scenario_designer</b> / statistical）</span></div>
    <div class="prow"><span class="k">边界</span><span>自建引擎<b>弱观测</b>（无 OTel trace/replay、无原生因果树、message 读即消费）——用 AS 替代的理由。</span></div>
    <div class="prow"><span class="k">我们用</span><span><span class="ptag">审计思路</span><span class="ptag">runtime_monitor/scenario_designer</span><span class="ptag">AWI 参考</span></span></div>
  </div>
</div>

<div class="pcard as">
  <div class="phead">⬜ AgentSociety (AS)</div>
  <div class="pbody">
    <p><b>模拟引擎（清华，Apache 2.0）</b></p>
    <div class="prow"><span class="k">是什么</span><span>LLM-native 多 agent 城市模拟平台（<code>agentsociety2</code>，pip 可装）。</span></div>
    <div class="prow"><span class="k">能力</span><span><b>Ray 分布式</b> + <b>OTel trace</b>（parent_span_id 因果树）+ <b>DuckDB replay</b> ·16 内置 env ·PersonAgent 3 层记忆 ·<b>custom/envs/ 热加载</b> ·litellm 路由</span></div>
    <div class="prow"><span class="k">边界</span><span>是<b>模拟引擎</b>，<b>没有审计层</b>、无 EW 设定、无 AWI——这些正是我们补的。</span></div>
    <div class="prow"><span class="k">我们用</span><span><span class="ptag">pip 依赖当引擎</span><span class="ptag">trace/replay 落盘</span><span class="ptag">custom env 热加载</span></span></div>
  </div>
</div>

<div class="pcard ours">
  <div class="phead">🟩 afi-platform（我们）</div>
  <div class="pbody">
    <p><b>= AS 引擎 + EW 设定 + AFI 审计，三层闭环</b></p>
    <div class="prow"><span class="k">是什么</span><span>AS 当引擎（pip 依赖）+ EW 当剧本（翻译成 AS env）+ AFI 当审计（端口思路），三层 world/custom-envs/audit/backend。</span></div>
    <div class="prow"><span class="k">改进</span><span>把"模拟引擎"变成"模拟+审计一体"：加治理/能量/犯罪/地标 env + AWI 9 族 + runtime 早告警 + 跨模型对照。</span></div>
    <div class="prow"><span class="k">不 fork</span><span>3 个耦合点（custom/envs 热加载 + init_config + CLI subprocess），跟 AS 升级。</span></div>
    <div class="prow"><span class="k">详见</span><span>③ 我们的平台 tab。</span></div>
  </div>
</div>
"""
