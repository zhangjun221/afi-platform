"""Decision trace — per-agent per-tick timeline of decision-relevant spans.

The "decision process" of an agent lives in the trace, not in replay. This
module walks the OTel span tree and groups decision-relevant spans
(agent.step / react.loop / react.turn / react.tool / llm.completion /
memory.extract / script.run) by agent and by tick, so the HTML report can
render a readable timeline of what each agent thought/did each tick.

react.tool spans lack agent.tick (it's on the parent react.turn/agent.step),
so tick is resolved by walking the parent_span_id chain — same approach as
tunnel_vision._resolve_tick.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from afi.audit.load import agent_id, attr, ts_of

# Spans that tell the decision story (skip noisy lifecycle/skill-hook spans).
DECISION_SPAN_NAMES = {
    "agent.step",
    "react.loop",
    "react.turn",
    "react.tool",
    "llm.completion",
    "memory.extract",
    "memory.append_episodes",
    "memory.should_consolidate",
    "script.run",
}


def _index(spans: List[dict]) -> Dict[str, dict]:
    return {s.get("span_id"): s for s in spans if s.get("span_id")}


def _resolve_tick(span: dict, by_id: dict):
    """Walk parent chain to find the nearest span carrying agent.tick."""
    cur = span
    seen = set()
    # a span may itself carry agent.tick
    t = attr(cur, "agent.tick")
    if t is not None:
        return t
    while True:
        pid = cur.get("parent_span_id")
        if not pid or pid in seen:
            break
        seen.add(pid)
        cur = by_id.get(pid)
        if cur is None:
            break
        t = attr(cur, "agent.tick")
        if t is not None:
            return t
    return None


def _span_summary(span: dict) -> dict:
    """Extract a readable summary of a decision span."""
    name = span.get("name", "")
    a = span.get("attributes") or {}
    out = a.get("output.summary")
    # output.summary can be dict (react.tool) or str
    if isinstance(out, dict):
        out_str = str(out.get("observation") or out)
    else:
        out_str = str(out or "")
    return {
        "name": name,
        "react_action": a.get("react.action"),
        "tool_count": a.get("react.tool_count"),
        "llm_model": a.get("llm.model"),
        "step_count": a.get("step.count"),
        "end_reason": a.get("react.end_reason"),
        "summary": out_str,
    }


def build_decision_trace(spans: List[dict]) -> Dict[int, List[dict]]:
    """Group decision spans by agent, then by tick.

    Returns: {agent_id: [{tick, spans: [summary, ...]}, ...]}
    """
    by_id = _index(spans)
    # agent -> tick -> list of spans
    per: Dict[int, Dict[object, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for s in spans:
        if s.get("name") not in DECISION_SPAN_NAMES:
            continue
        aid = agent_id(s)
        if aid is None:
            continue
        tk = _resolve_tick(s, by_id)
        per[aid][tk].append(s)

    out: Dict[int, List[dict]] = {}
    for aid, ticks in per.items():
        tick_list = []
        for tk, slist in sorted(ticks.items(), key=lambda kv: str(kv[0])):
            slist.sort(key=ts_of)
            tick_list.append({
                "tick": tk,
                "spans": [_span_summary(s) for s in slist],
            })
        out[aid] = tick_list
    return out
