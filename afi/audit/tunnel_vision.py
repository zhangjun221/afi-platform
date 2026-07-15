"""Tunnel-vision detection — sustained over-focus windows in an agent's action stream.

Borrows the *idea* from ai-freedom-island `audit.py`'s tunnel vision (sustained
repetition of one action/target, ignoring other signals). Implemented natively:
scan each agent's `react.tool` spans in time order; a tunnel-vision window is a
run of ≥ MIN_RUN consecutive spans with the same `react.action` (e.g. the agent
stuck acting via execute_skill_script without ever observing), or the inverse
(stuck observing without acting). Also flag repeated identical output.summary
(same result re-occurring) as a stuck loop.

This is a deliberately simple, transparent heuristic — the point of the
prototype is to prove the native-on-trace path works, not to ship a polished
detector.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from afi.audit.load import agent_id, attr, spans_by_agent, ts_of, tick_of

MIN_RUN = 3  # ≥ this many consecutive same-action spans = a window


def _resolve_tick(span: dict, by_id: dict) -> int | None:
    """Map a react.tool span to its sim step by walking the parent chain.

    react.tool spans carry no step/tick themselves; an ancestor does. We want
    **``step.count``** (the step index 1..N — matches replay ``step``). Problem:
    intermediate spans (react.loop/react.turn) copy down ``agent.tick`` (the
    tick *interval*, a constant 3600), so a naive "first hit" returns 3600 for
    most tools. We walk the *whole* chain, prefer the first ``step.count``,
    and only fall back to ``agent.tick`` if no ``step.count`` is reachable.
    """
    seen = set()
    cur = span
    tick_fallback = None
    while cur:
        sc = attr(cur, "step.count")
        if sc is not None:
            return int(sc)
        if tick_fallback is None:
            t = tick_of(cur)
            if t is not None:
                tick_fallback = t
        pid = cur.get("parent_span_id")
        if not pid or pid in seen:
            break
        seen.add(pid)
        cur = by_id.get(pid)
    return tick_fallback


def _detect_runs(items: List[dict], key) -> List[Dict]:
    """Find maximal runs of ≥ MIN_RUN consecutive items with equal key(item)."""
    windows = []
    if not items:
        return windows
    start = 0
    cur_key = key(items[0])
    for i in range(1, len(items)):
        k = key(items[i])
        if k != cur_key:
            if i - start >= MIN_RUN:
                windows.append({"action": cur_key, "start_idx": start, "len": i - start,
                                "first": items[start], "last": items[i - 1]})
            start = i
            cur_key = k
    # tail
    if len(items) - start >= MIN_RUN:
        windows.append({"action": cur_key, "start_idx": start, "len": len(items) - start,
                        "first": items[start], "last": items[-1]})
    return windows


def tunnel_vision_report(spans: List[dict]) -> Dict:
    by_id = {s.get("span_id"): s for s in spans if s.get("span_id")}
    tool_spans = [s for s in spans if s.get("name") == "react.tool"]
    per_agent = spans_by_agent(tool_spans)
    report: Dict = {"windows": [], "per_agent_count": {}}
    for aid, slist in sorted(per_agent.items()):
        slist.sort(key=ts_of)
        # 1) runs of same react.action
        wins = _detect_runs(slist, lambda s: attr(s, "react.action", "?"))
        # 2) runs of identical output.summary (stuck loop)
        stuck = _detect_runs(slist, lambda s: attr(s, "output.summary", ""))
        for w in wins:
            report["windows"].append({
                "agent_id": aid,
                "kind": "repeated_action",
                "action": w["action"],
                "length": w["len"],
                "tick": _resolve_tick(w["first"], by_id),
                "summary": str(attr(w["first"], "output.summary", ""))[:120],
            })
        for w in stuck:
            if w["action"]:  # non-empty summary
                report["windows"].append({
                    "agent_id": aid,
                    "kind": "identical_output",
                    "action": str(w["action"])[:120],
                    "length": w["len"],
                    "tick": _resolve_tick(w["first"], by_id),
                })
        report["per_agent_count"][aid] = len(wins) + len(stuck)
    report["total_windows"] = len(report["windows"])
    return report


def format_tunnel_vision(rep: Dict) -> str:
    lines = [
        "============================================================",
        "TUNNEL-VISION ANALYSIS",
        "============================================================",
        f"Windows detected: {rep['total_windows']}  (threshold: ≥{MIN_RUN} consecutive)",
        "",
    ]
    if not rep["windows"]:
        lines.append("  No sustained tunnel vision detected.")
        return "\n".join(lines)
    # HIGH risk = long windows
    for w in sorted(rep["windows"], key=lambda x: -x["length"])[:20]:
        risk = "HIGH" if w["length"] >= MIN_RUN * 2 else "LOW"
        lines.append(f"  [{risk}] agent {w['agent_id']} tick {w['tick']} "
                     f"({w['kind']}, len={w['length']}, action={w.get('action','?')})")
        if w.get("summary"):
            lines.append(f"        {w['summary']}")
    return "\n".join(lines)
