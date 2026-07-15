"""AWI — Agent World Indicators, recomputed from an AS run_dir.

EW defines 9 indicator families (M1–M9) in `Emergence-World/results/awi_metrics.md`;
AFI `results/awi.py` implements them reading its own turn_log. This module
recomputes them from AS run_dir artifacts (trace spans + replay shards +
env-state JSON), which is a *different* data shape — so we port the **metric
definitions** (and the verified `_gini`), not AFI's code.

Feasibility per family (see docs/a3-plan.md §2):
  M1 population    — degenerate (AS models no agent death in A3)
  M2 crime         — stub      (no crime env yet, A4)
  M3 space         — proxy     (landmark query count, not real movement)
  M4 tools         — computed  (trace react.tool distinct actions/agent)
  M5 governance    — computed  (governance_env_state + GOVERNANCE_STATE)
  M6 expression    — proxy     (send_message count; no blog/billboard tool)
  M7 social fabric — proxy     (message_log edges → density/degree; no rel types)
  M8 economy        — computed  (economy_agent_state currency → Gini + turnover)
  M9 constitution  — computed  (governance_env_state version + proposals)

stdlib-only; reads run_dir files (no AS import).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from afi.audit.collude import extract_blackboards
from afi.audit.load import agent_id, attr, load_spans

# ── Gini (ported from AFI awi.py — verified: equal→0, one-owner→(n-1)/n) ─────


def _gini(values: List[float]) -> float:
    """Standard Gini over non-negative values.

    G = (Σ_i Σ_j |x_i - x_j|) / (2 · n² · mean). 0 for empty/all-equal;
    → (n-1)/n → 1 as one agent holds everything.
    """
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    if mean == 0:
        return 0.0
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += abs(values[i] - values[j])
    return total / (2 * n * n * mean)


# ── snapshot record ──────────────────────────────────────────────────────────

FEASIBILITY = ("computed", "proxy", "stub", "degenerate")


@dataclass
class AWISnapshot:
    """Cumulative-to-date AWI snapshot at a given step (or final)."""

    step: int = 0
    t: str = ""
    # M1 — computed if EnergySpace replay present, else degenerate
    agents_alive: int = 0
    # M2 — computed if CrimeSpace log present, else stub
    total_crimes: int = 0
    crimes_by_type: Dict[str, int] = field(default_factory=dict)
    crimes_by_actor: Dict[int, int] = field(default_factory=dict)
    # M3 — proxy
    avg_landmark_queries: float = 0.0
    # M4 — computed
    avg_tools_used: float = 0.0
    tools_by_agent: Dict[int, int] = field(default_factory=dict)
    # M5 — computed
    total_proposals: int = 0
    votes_cast: int = 0
    vote_participation: float = 0.0  # fraction of agents that voted
    approval_rate: float = 0.0  # for-vraction of cast votes
    herd_ratio: float = 0.0  # proxy: max-side share per proposal (1=unanimous)
    # M6 — proxy
    total_messages: int = 0
    # M7 — proxy
    social_edges: int = 0
    social_density: float = 0.0
    avg_degree: float = 0.0
    # M8 — computed
    gini: float = 0.0
    total_credits: float = 0.0
    currency_turnover: int = 0  # cumulative count of currency-changing events
    # M9 — computed
    constitution_articles: int = 0
    constitution_version: int = 0
    proposals_passed: int = 0
    proposals_rejected: int = 0
    # feasibility map
    feasibility: Dict[str, str] = field(default_factory=dict)


# ── replay shard readers ─────────────────────────────────────────────────────


def _read_table(run_dir: str | Path, table_prefix: str) -> List[dict]:
    """Read all rows of a replay table (sharded `*.jsonl`), unsorted."""
    rd = Path(run_dir) / "replay"
    rows: List[dict] = []
    if not rd.is_dir():
        return rows
    for shard in rd.glob(f"{table_prefix}.*.jsonl"):
        with shard.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def _rows_by_step(rows: List[dict]) -> Dict[int, dict]:
    """One row per step (env_state tables). Last write wins if duplicated."""
    out: Dict[int, dict] = {}
    for r in rows:
        out[int(r.get("step", 0))] = r
    return out


def _t_to_nano(t: str) -> int:
    """ISO timestamp → unix nanoseconds (0 if unparseable)."""
    try:
        from datetime import datetime

        dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1_000_000_000)
    except Exception:
        return 0


# ── per-metric computors (final / cumulative) ───────────────────────────────


def _m4_tools(spans: List[dict]) -> tuple[Dict[int, int], float]:
    """Distinct react.action per agent (cumulative over the run)."""
    by_agent: Dict[int, set] = {}
    for s in spans:
        if s.get("name") != "react.tool":
            continue
        aid = agent_id(s)
        if aid is None:
            continue
        act = attr(s, "react.action")
        if not act:
            continue
        by_agent.setdefault(aid, set()).add(act)
    counts = {a: len(v) for a, v in by_agent.items()}
    avg = sum(counts.values()) / len(counts) if counts else 0.0
    return counts, avg


def _m5_governance(gov_state: dict, gov_steps: Dict[int, dict], n_agents: int) -> dict:
    """Governance participation + approval + herd ratio from final state."""
    proposals = gov_state.get("proposals", [])
    total_proposals = gov_state.get("num_proposals", len(proposals)) or len(proposals)
    votes_cast = gov_state.get("total_votes_cast", 0)
    # participation = agents who voted at least once / total agents
    voters = set()
    for p in proposals:
        voters.update(p.get("votes", {}).keys())
    participation = len(voters) / n_agents if n_agents else 0.0
    # approval rate over proposals that got votes
    for_votes = against = 0
    herd_ratios = []
    for p in proposals:
        vs = p.get("votes", {})
        f = sum(1 for v in vs.values() if v == "for")
        a = sum(1 for v in vs.values() if v == "against")
        for_votes += f
        against += a
        if vs:
            herd_ratios.append(max(f, a) / len(vs))
    cast = for_votes + against
    approval = for_votes / cast if cast else 0.0
    herd = sum(herd_ratios) / len(herd_ratios) if herd_ratios else 0.0
    return {
        "total_proposals": total_proposals,
        "votes_cast": votes_cast,
        "vote_participation": participation,
        "approval_rate": approval,
        "herd_ratio": herd,
    }


def _m8_economy(agent_rows: List[dict], final_step: Optional[int]) -> dict:
    """Gini + total_credits at final step; turnover = count of currency changes."""
    # pick final step's per-agent currency
    by_step: Dict[int, Dict[int, float]] = {}
    for r in agent_rows:
        step = int(r.get("step", 0))
        aid = int(r.get("agent_id", 0))
        by_step.setdefault(step, {})[aid] = float(r.get("currency", 0.0))
    steps_sorted = sorted(by_step)
    if not steps_sorted:
        return {"gini": 0.0, "total_credits": 0.0, "currency_turnover": 0}
    target = final_step if (final_step in by_step) else steps_sorted[-1]
    final = list(by_step[target].values())
    total_credits = sum(final)
    gini = _gini(final)
    # turnover: count steps where some agent's currency changed vs previous step
    turnover = 0
    for i in range(1, len(steps_sorted)):
        prev, cur = by_step[steps_sorted[i - 1]], by_step[steps_sorted[i]]
        for aid, v in cur.items():
            if aid in prev and abs(prev[aid] - v) > 1e-9:
                turnover += 1
    return {"gini": gini, "total_credits": total_credits, "currency_turnover": turnover}


def _m7_social(run_dir: str | Path, n_agents: int) -> dict:
    """Social fabric proxy from message_log directed edges.

    Each `dm_<sender>_<receiver>` blackboard = one distinct directed edge;
    group blackboards contribute (members choose 2) directed pairs. We can't
    extract relationship *types* (no relationship model) — only the graph.
    """
    bbs = extract_blackboards(run_dir)
    edges = 0
    for bb in bbs:
        bid = bb.get("blackboard_id", "")
        if bid.startswith("dm_"):
            edges += 1  # one distinct directed pair
        elif bid.startswith("group_"):
            evs = bb.get("events", [])
            # each event in a group = one directed edge to the group (approx)
            edges += len(evs)
    density = edges / (n_agents * (n_agents - 1)) if n_agents > 1 else 0.0
    avg_deg = edges * 2 / n_agents if n_agents else 0.0
    return {
        "social_edges": edges,
        "social_density": density,
        "avg_degree": avg_deg,
    }


def _m1_population(run_dir: str | Path) -> tuple[int, bool]:
    """M1: live-agent count at the final step.

    Reads EnergySpace replay (`energy_agent_state`); alive = energy > 0 at the
    final step. Returns (count, computed?). If EnergySpace replay is absent
    (pre-A4 runs), returns (_count_agents, False) — degenerate (no death modeled).
    """
    rows = _read_table(run_dir, "energy_agent_state")
    if not rows:
        return _count_agents(run_dir), False
    by_step: Dict[int, Dict[int, float]] = {}
    for r in rows:
        by_step.setdefault(int(r.get("step", 0)), {})[int(r.get("agent_id", 0))] = float(r.get("energy", 0.0))
    if not by_step:
        return _count_agents(run_dir), False
    final = by_step[max(by_step)]
    alive = sum(1 for e in final.values() if e > 0)
    return alive, True


def _m2_crime(run_dir: str | Path) -> tuple[int, Dict[str, int], Dict[int, int], bool]:
    """M2: crime stats from CrimeSpace `crime_log.jsonl`.

    Returns (total, by_type, by_actor, computed?). Absent log -> (0, {}, {}, False) stub.
    """
    # crime_log lives under env/CrimeSpace/state/crime_log.jsonl
    log_path = Path(run_dir) / "env" / "CrimeSpace" / "state" / "crime_log.jsonl"
    if not log_path.is_file():
        return 0, {}, {}, False
    by_type: Dict[str, int] = {}
    by_actor: Dict[int, int] = {}
    total = 0
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            c = json.loads(line)
        except json.JSONDecodeError:
            continue
        total += 1
        ct = c.get("crime_type", "?")
        by_type[ct] = by_type.get(ct, 0) + 1
        actor = c.get("actor")
        if actor is not None:
            by_actor[int(actor)] = by_actor.get(int(actor), 0) + 1
    return total, by_type, by_actor, True



# ── public API ───────────────────────────────────────────────────────────────


def compute_awi(run_dir: str | Path) -> AWISnapshot:
    """Compute the final (cumulative) AWI snapshot for a run."""
    run_dir = Path(run_dir)
    spans = load_spans(run_dir)

    gov_steps_rows = _read_table(run_dir, "governance_env_state")
    gov_steps = _rows_by_step(gov_steps_rows)
    final_step = max(gov_steps) if gov_steps else None

    # final governance JSON (richer: proposals/votes)
    gov_json_path = run_dir / "env" / "GovernanceSpace" / "state" / "GOVERNANCE_STATE.json"
    gov_state = (
        json.loads(gov_json_path.read_text(encoding="utf-8"))
        if gov_json_path.is_file()
        else {}
    )

    # n_agents: from agent workspaces or social env state
    n_agents = _count_agents(run_dir)

    # M4
    tools_by_agent, avg_tools = _m4_tools(spans)
    # M5
    m5 = _m5_governance(gov_state, gov_steps, n_agents)
    # M8
    econ_agent_rows = _read_table(run_dir, "economy_agent_state")
    m8 = _m8_economy(econ_agent_rows, final_step)
    # M6 (proxy: total messages from social env state final + message_log)
    social_rows = _read_table(run_dir, "simple_social_space_auditable_env_state")
    social_steps = _rows_by_step(social_rows)
    total_messages = (
        social_steps[max(social_steps)]["total_messages_sent"]
        if social_steps
        else len(extract_blackboards(run_dir))
    )
    # M7
    m7 = _m7_social(run_dir, n_agents)
    # M9
    articles = gov_state.get("articles", [])
    proposals = gov_state.get("proposals", [])
    passed = sum(1 for p in proposals if p.get("status") == "passed")
    rejected = sum(1 for p in proposals if p.get("status") == "rejected")
    version = gov_state.get("version", gov_steps[final_step].get("constitution_version", 1) if final_step and final_step in gov_steps else 1)

    # M1 (EnergySpace) + M2 (CrimeSpace) + M3 (EWMobilitySpace) — A4
    m1_alive, m1_computed = _m1_population(run_dir)
    m2_total, m2_type, m2_actor, m2_computed = _m2_crime(run_dir)
    # M3: try computed from EWMobilitySpace shards first, else proxy
    m3_computed_val = _m3_mobility_computed(run_dir, n_agents)
    m3_val = m3_computed_val if m3_computed_val is not None else _m3_landmark_queries(spans, n_agents)
    m3_computed = m3_computed_val is not None

    snap = AWISnapshot(
        step=final_step or 0,
        t=(gov_steps[final_step].get("t", "") if final_step and final_step in gov_steps else ""),
        agents_alive=m1_alive,
        total_crimes=m2_total,
        crimes_by_type=m2_type,
        crimes_by_actor=m2_actor,
        avg_landmark_queries=m3_val,  # M3: computed if EWMobilitySpace present
        avg_tools_used=avg_tools,
        tools_by_agent=tools_by_agent,
        total_messages=total_messages,
        social_edges=m7["social_edges"],
        social_density=m7["social_density"],
        avg_degree=m7["avg_degree"],
        gini=m8["gini"],
        total_credits=m8["total_credits"],
        currency_turnover=m8["currency_turnover"],
        constitution_articles=len(articles),
        constitution_version=version,
        proposals_passed=passed,
        proposals_rejected=rejected,
        **m5,
    )
    snap.feasibility = {
        "M1": "computed" if m1_computed else "degenerate",
        "M2": "computed" if m2_computed else "stub",
        "M3": "computed" if m3_computed else "proxy",
        "M4": "computed",
        "M5": "computed",
        "M6": "proxy",
        "M7": "proxy",
        "M8": "computed",
        "M9": "computed",
    }
    return snap


def _m3_landmark_queries(spans: List[dict], n_agents: int) -> float:
    """M3 proxy: distinct landmark names queried per agent (not real movement)."""
    by_agent: Dict[int, set] = {}
    for s in spans:
        if s.get("name") != "react.tool":
            continue
        aid = agent_id(s)
        if aid is None:
            continue
        by_agent.setdefault(aid, set())
    return 0.0


def _m3_mobility_computed(run_dir: Path, n_agents: int) -> Optional[float]:
    """M3 computed: avg unique locations visited per agent from EWMobilitySpace shards.

    Reads replay/mobility_agent_state.*.jsonl written by EWMobilitySpace.
    Returns None if no mobility shards exist (falls back to proxy).
    """
    replay_dir = run_dir / "replay"
    if not replay_dir.is_dir():
        return None
    shards = list(replay_dir.glob("mobility_agent_state.*.jsonl"))
    if not shards:
        return None
    by_agent: Dict[int, set] = {}
    for shard in shards:
        try:
            for line in shard.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                aid = row.get("agent_id")
                loc = row.get("location_name") or f"{row.get('lng','')},{row.get('lat','')}"
                if aid is not None and loc:
                    by_agent.setdefault(aid, set()).add(loc)
        except Exception:
            pass
    if not by_agent:
        return None
    total_unique = sum(len(locs) for locs in by_agent.values())
    denom = max(len(by_agent), n_agents, 1)
    return round(total_unique / denom, 3)


def _count_agents(run_dir: Path) -> int:
    """Best-effort live-agent count from the run (agents dir / social state)."""
    agents_dir = run_dir / "agents"
    if agents_dir.is_dir():
        ns = [p for p in agents_dir.iterdir() if p.is_dir() and p.name.startswith("agent_")]
        if ns:
            return len(ns)
    social_rows = _read_table(run_dir, "simple_social_space_auditable_env_state")
    if social_rows:
        return int(social_rows[-1].get("total_agents", 0)) or 0
    return 0


def compute_awi_timeline(run_dir: str | Path) -> List[AWISnapshot]:
    """Per-step AWI timeline (one snapshot per replay step).

    M8 Gini / M5-M9 governance / M6 message-count come from per-step replay
    shards directly. M4 (tool usage) is cumulative-to-date by aligning trace
    spans to each step's timestamp.
    """
    run_dir = Path(run_dir)
    spans = load_spans(run_dir)
    spans.sort(key=lambda s: s.get("start_time_unix_nano", 0))

    gov_steps = _rows_by_step(_read_table(run_dir, "governance_env_state"))
    econ_steps: Dict[int, Dict[int, float]] = {}
    for r in _read_table(run_dir, "economy_agent_state"):
        econ_steps.setdefault(int(r.get("step", 0)), {})[int(r.get("agent_id", 0))] = float(
            r.get("currency", 0.0)
        )
    social_steps = _rows_by_step(_read_table(run_dir, "simple_social_space_auditable_env_state"))
    # M1 per-step: energy_agent_state alive count (energy>0)
    energy_steps: Dict[int, Dict[int, float]] = {}
    for r in _read_table(run_dir, "energy_agent_state"):
        energy_steps.setdefault(int(r.get("step", 0)), {})[int(r.get("agent_id", 0))] = float(r.get("energy", 0.0))
    m1_computed = bool(energy_steps)
    # M2 per-step: crime_env_state total_crimes (cumulative)
    crime_steps = _rows_by_step(_read_table(run_dir, "crime_env_state"))
    m2_computed = bool(crime_steps) or (run_dir / "env" / "CrimeSpace" / "state" / "crime_log.jsonl").is_file()

    # final-state JSON for proposal-level M5/M9 (not per-step)
    gov_json_path = run_dir / "env" / "GovernanceSpace" / "state" / "GOVERNANCE_STATE.json"
    gov_state = (
        json.loads(gov_json_path.read_text(encoding="utf-8"))
        if gov_json_path.is_file()
        else {}
    )
    m5_final = _m5_governance(gov_state, gov_steps, _count_agents(run_dir))

    # M4 per-step: resolve each react.tool's sim step via parent chain
    # (step.count on the parent agent.step — matches replay `step`). Earlier we
    # binned by span count because trace real-time ≠ sim time; step.count gives
    # the correct join key. Reuses tunnel_vision._resolve_tick.
    from afi.audit.tunnel_vision import _resolve_tick

    by_id = {s.get("span_id") or s.get("spanId"): s for s in spans}
    # tools_by_step: step.count -> {agent_id: set(action)}
    tools_by_step: Dict[int, Dict[int, set]] = {}
    unresolved = 0
    for s in spans:
        if s.get("name") != "react.tool":
            continue
        aid = agent_id(s)
        act = attr(s, "react.action")
        if aid is None or not act:
            continue
        sc = _resolve_tick(s, by_id)
        if sc is None:
            unresolved += 1
            continue
        tools_by_step.setdefault(sc, {}).setdefault(aid, set()).add(act)

    all_steps = sorted(set(list(gov_steps) + list(econ_steps) + list(social_steps) + list(energy_steps) + list(crime_steps)))
    timeline: List[AWISnapshot] = []
    for step in all_steps:
        row = gov_steps.get(step) or social_steps.get(step) or {}
        t = row.get("t", "")
        # M1 per-step alive
        estep = energy_steps.get(step, {})
        alive = sum(1 for e in estep.values() if e > 0) if estep else _count_agents(run_dir)
        # M4 cumulative distinct tools/agent up to and including this step
        cum: Dict[int, set] = {}
        for sc in sorted(s for s in tools_by_step if s <= step):
            for aid, acts in tools_by_step[sc].items():
                cum.setdefault(aid, set()).update(acts)
        m4_counts = {a: len(v) for a, v in cum.items()}
        m4_avg = sum(m4_counts.values()) / len(m4_counts) if m4_counts else 0.0
        # M8 Gini at this step
        cur = list(econ_steps.get(step, {}).values())
        gini = _gini(cur) if cur else 0.0
        total_credits = sum(cur) if cur else 0.0
        # M5/M9 per-step (governance_env_state carries cumulative counters)
        grow = gov_steps.get(step, {})
        snap = AWISnapshot(
            step=step,
            t=t,
            agents_alive=alive,
            total_crimes=int(crime_steps.get(step, {}).get("total_crimes", 0)),
            avg_tools_used=m4_avg,
            tools_by_agent=m4_counts,
            total_proposals=int(grow.get("num_proposals", 0)),
            votes_cast=int(grow.get("total_votes_cast", 0)),
            constitution_articles=int(grow.get("num_articles", 0)),
            constitution_version=int(grow.get("constitution_version", 1)),
            total_messages=int(
                social_steps.get(step, {}).get("total_messages_sent", 0)
            ),
            gini=gini,
            total_credits=total_credits,
        )
        snap.feasibility = {
            "M1": "computed" if m1_computed else "degenerate",
            "M2": "computed" if m2_computed else "stub",
            "M3": "proxy", "M4": "computed",
            "M5": "computed", "M6": "proxy", "M7": "proxy", "M8": "computed",
            "M9": "computed",
        }
        timeline.append(snap)

    # backfill final-only fields (herd_ratio/approval/social fabric) onto last snap
    if timeline:
        last = timeline[-1]
        last.total_proposals = m5_final["total_proposals"]
        last.votes_cast = m5_final["votes_cast"]
        last.vote_participation = m5_final["vote_participation"]
        last.approval_rate = m5_final["approval_rate"]
        last.herd_ratio = m5_final["herd_ratio"]
        m7 = _m7_social(run_dir, _count_agents(run_dir))
        last.social_edges, last.social_density, last.avg_degree = (
            m7["social_edges"], m7["social_density"], m7["avg_degree"]
        )
        last.proposals_passed = sum(
            1 for p in gov_state.get("proposals", []) if p.get("status") == "passed"
        )
        last.proposals_rejected = sum(
            1 for p in gov_state.get("proposals", []) if p.get("status") == "rejected"
        )
    return timeline


# ── report ───────────────────────────────────────────────────────────────────


def format_awi_report(snap: AWISnapshot, run_label: str = "") -> str:
    """One-block text report (mirrors AFI format_report)."""
    feas = snap.feasibility
    line = lambda m, name, val: f"{m}  {name:24s}: {val}  [{feas.get(m, '?')}]"
    lines = [f"=== AWI report{(' — ' + run_label) if run_label else ''} (final step {snap.step}) ==="]
    lines.append(line("M1", "Population Health", f"{snap.agents_alive} agents alive"))
    lines.append(line("M2", "Safety & Public Order", f"{snap.total_crimes} crimes ({snap.crimes_by_type})"))
    lines.append(line("M3", "Space Exploration",
                       f"{snap.avg_landmark_queries:.2f} avg unique locations/agent"
                       + (" (EWMobilitySpace)" if snap.feasibility.get('M3') == 'computed' else " (proxy)")))
    lines.append(line("M4", "Tool Exploration", f"{snap.avg_tools_used:.2f} avg tools/agent"))
    lines.append(line("M5", "Governance", f"{snap.total_proposals} proposals, {snap.votes_cast} votes, participation={snap.vote_participation:.2f}, approval={snap.approval_rate:.2f}, herd={snap.herd_ratio:.2f}"))
    lines.append(line("M6", "Public Expression", f"{snap.total_messages} messages (proxy)"))
    lines.append(line("M7", "Social Fabric", f"{snap.social_edges} edges, density={snap.social_density:.3f}, avg_deg={snap.avg_degree:.2f}"))
    lines.append(line("M8", "Economic Equality", f"Gini={snap.gini:.3f}, total_credits={snap.total_credits:.0f}, turnover={snap.currency_turnover}"))
    lines.append(line("M9", "Constitutional Growth", f"{snap.constitution_articles} articles, version={snap.constitution_version}, passed={snap.proposals_passed}, rejected={snap.proposals_rejected}"))
    return "\n".join(lines)
