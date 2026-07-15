"""Causal attribution — native on AS trace's parent_span_id tree.

AgentSociety trace is OpenTelemetry: every span has trace_id / span_id /
parent_span_id. This *is* a causal span tree already — no reconstruction
needed (unlike ai-freedom-island's turn_log, where the causal chain had to be
rebuilt after the fact). This module walks the tree:

  - ancestors(span): parent chain up to the agent.step root
  - descendants(span): subtree
  - root(span): the top-level agent.step / agent.init span of the trace
  - failed_spans(spans): react.tool spans with result.ok=False — candidate
    anomalies to attribute
  - explain_failure(span): print the ancestor chain leading to a failed span,
    so a human (or downstream LLM judge) can see what led to it
"""
from __future__ import annotations

from typing import Dict, List, Optional

from afi.audit.load import attr, agent_id, tick_of


def _index(spans: List[dict]) -> Dict[str, dict]:
    return {s.get("span_id"): s for s in spans if s.get("span_id")}


def ancestors(span: dict, by_id: Dict[str, dict]) -> List[dict]:
    """Walk parent_span_id up to the root. Returns [] if the span is itself a root."""
    chain = []
    cur = span
    seen = set()
    while True:
        pid = cur.get("parent_span_id")
        if not pid or pid in seen:
            break
        parent = by_id.get(pid)
        if parent is None:
            break
        chain.append(parent)
        seen.add(pid)
        cur = parent
    return chain


def root(span: dict, by_id: Dict[str, dict]) -> Optional[dict]:
    chain = ancestors(span, by_id)
    return chain[-1] if chain else (span if not span.get("parent_span_id") else None)


def descendants(span: dict, by_id: Dict[str, dict]) -> List[dict]:
    """All spans whose ancestor chain includes `span`."""
    sid = span.get("span_id")
    if not sid:
        return []
    out = []
    # build child index
    children: Dict[str, List[dict]] = {}
    for s in by_id.values():
        pid = s.get("parent_span_id")
        if pid:
            children.setdefault(pid, []).append(s)
    stack = list(children.get(sid, []))
    while stack:
        c = stack.pop()
        out.append(c)
        stack.extend(children.get(c.get("span_id"), []))
    return out


def failed_spans(spans: List[dict]) -> List[dict]:
    """react.tool spans whose result.ok is False — candidate anomalies."""
    return [s for s in spans
            if s.get("name") == "react.tool" and attr(s, "result.ok") is False]


def explain_failure(span: dict, by_id: Dict[str, dict]) -> Dict:
    """Build a causal explanation for a failed span: ancestor chain + context."""
    chain = ancestors(span, by_id)
    return {
        "failed_span": {
            "span_id": span.get("span_id"),
            "agent_id": agent_id(span),
            "tick": tick_of(span),
            "name": span.get("name"),
            "react.action": attr(span, "react.action"),
            "output.summary": str(attr(span, "output.summary", ""))[:200],
        },
        "ancestor_chain": [
            {
                "span_id": s.get("span_id"),
                "name": s.get("name"),
                "react.action": attr(s, "react.action"),
                "step.count": attr(s, "step.count"),
                "tick": tick_of(s),
                "output.summary": str(attr(s, "output.summary", ""))[:120],
            }
            for s in chain
        ],
        "root": {
            "span_id": (chain[-1] if chain else span).get("span_id"),
            "name": (chain[-1] if chain else span).get("name"),
        },
    }


def build_event_graph(run_dir: str) -> Dict:
    """Build a per-agent per-step event graph joining trace behavior + replay env state.

    Phase-1 first-domino attribution data structure. Three node kinds:
      - behavior  : `react.tool` spans (agent_id, action, step, result.ok) — from trace
      - state     : env state per agent per step (energy/alive) — from `energy_agent_state` replay
      - institution: (v0 deferred) constitution version / proposals — from governance_env_state
    Edges:
      - causal  : parent_span_id (trace-native, retained in `by_id` for deeper explain_failure)
      - temporal: state@T → behavior@T → state@T+1 (same agent; the joined timeline below)
    Output: a per-agent per-step timeline queryable for "what did agent X do before step T",
    plus the retained span index for causal-chain attribution.

    Backend-agnostic: reads run_dir only (same contract as the other audit modules).
    """
    from afi.audit.load import load_spans, agent_id, attr
    from afi.audit.awi import _read_table
    from afi.audit.tunnel_vision import _resolve_tick

    spans = load_spans(run_dir)
    by_id = _index(spans)

    # ── state nodes: energy/alive per agent per step (canonical step axis) ──
    state: Dict[int, Dict[int, dict]] = {}
    for r in _read_table(run_dir, "energy_agent_state"):
        aid = int(r.get("agent_id", 0))
        step = int(r.get("step", 0))
        state.setdefault(aid, {})[step] = {
            "energy": float(r.get("energy", 0.0)),
            "alive": int(r.get("alive", 1)),
        }

    # ── behavior nodes: react.tool spans bucketed by (agent, step) ──────────
    # step comes from _resolve_tick (walks parent chain for `step.count`, NOT
    # `agent.tick` which is the tick *interval* constant — see tunnel_vision._resolve_tick).
    # `_resolve_tick` falls back to `agent.tick` when no `step.count` is reachable
    # anywhere in the chain; for ew_full (tick=86400) that fallback bucket (86400)
    # is NOT a real step and would pollute the step axis. Drop those fallback
    # spans (rare) and count them for honesty — energy replay `step` (1..N) is
    # the canonical step axis, so any behavior step > max(state step) is a fallback artifact.
    max_state_step = max((st for s in state.values() for st in s), default=0) \
        if state else 0
    behavior: Dict[int, Dict[int, List[dict]]] = {}
    dropped_fallback = 0
    for s in spans:
        if s.get("name") != "react.tool":
            continue
        aid = agent_id(s)
        if aid is None:
            continue
        step = _resolve_tick(s, by_id)
        if step is None or (max_state_step and step > max_state_step):
            dropped_fallback += 1
            continue
        behavior.setdefault(aid, {}).setdefault(step, []).append({
            "action": attr(s, "react.action", "?"),
            "ok": attr(s, "result.ok"),
            "summary": str(attr(s, "output.summary", ""))[:120],
            "span_id": s.get("span_id"),
        })

    # ── join: per-agent per-step timeline ────────────────────────────────────
    all_steps = sorted(
        {st for s in state.values() for st in s}
        | {st for s in behavior.values() for st in s}
    )
    agents: Dict[int, Dict] = {}
    for aid in sorted(set(list(state) + list(behavior))):
        st_map = state.get(aid, {})
        bh_map = behavior.get(aid, {})
        steps: Dict[int, dict] = {}
        died_at: Optional[int] = None
        for st in all_steps:
            entry: dict = {}
            if st in st_map:
                entry["energy"] = st_map[st]["energy"]
                entry["alive"] = st_map[st]["alive"]
                if died_at is None and st_map[st]["alive"] == 0:
                    died_at = st
            if st in bh_map:
                entry["actions"] = bh_map[st]
            if entry:
                steps[st] = entry
        agents[aid] = {"steps": steps, "died_at_step": died_at}

    return {
        "run_dir": str(run_dir),
        "n_agents": len(agents),
        "n_steps": max_state_step,
        "agents": agents,
        "spans_indexed": len(by_id),
        "behavior_spans_dropped_fallback": dropped_fallback,
    }


def format_event_graph_summary(graph: Dict) -> str:
    lines = [
        "============================================================",
        "EVENT GRAPH (per-agent per-step joined timeline)",
        "============================================================",
        f"agents: {graph['n_agents']}  steps: {graph['n_steps']}  spans indexed: {graph['spans_indexed']}",
        "",
    ]
    for aid, a in sorted(graph["agents"].items()):
        d = a.get("died_at_step")
        n_act = sum(len(s.get("actions", [])) for s in a["steps"].values())
        mark = f"  ✗ died@step {d}" if d is not None else "  ✓ survived"
        lines.append(f"  agent {aid}{mark}  (actions={n_act})")
    return "\n".join(lines)


def causal_report(spans: List[dict]) -> Dict:
    by_id = _index(spans)
    fails = failed_spans(spans)
    explanations = [explain_failure(f, by_id) for f in fails]
    # Also surface the span-tree shape: counts per name, depth
    return {
        "total_spans": len(spans),
        "indexed_spans": len(by_id),
        "roots": sum(1 for s in spans if not s.get("parent_span_id")),
        "failed_tool_spans": len(fails),
        "explanations": explanations,
    }


def format_causal(rep: Dict) -> str:
    lines = [
        "============================================================",
        "CAUSAL ATTRIBUTION (native parent_span_id tree)",
        "============================================================",
        f"Spans indexed: {rep['indexed_spans']}  roots: {rep['roots']}  "
        f"failed react.tool: {rep['failed_tool_spans']}",
        "",
    ]
    if not rep["explanations"]:
        lines.append("  No failed tool spans — nothing to attribute.")
        return "\n".join(lines)
    for ex in rep["explanations"][:10]:
        f = ex["failed_span"]
        lines.append(f"  ✗ agent {f['agent_id']} tick {f['tick']} "
                     f"action={f['react.action']}  span={f['span_id']}")
        lines.append(f"      failed output: {f['output.summary']}")
        if ex["ancestor_chain"]:
            lines.append("      ancestor chain (root → ... → failure):")
            for a in reversed(ex["ancestor_chain"]):
                lines.append(f"        ← {a['name']}  "
                             f"action={a.get('react.action')}  step={a.get('step.count')}")
            lines.append(f"        ← [FAILED] {f['name']}")
    return "\n".join(lines)
