"""Sensorium — sensing ratio per agent, directly on AS trace.

Borrows the *idea* from ai-freedom-island `audit.py`'s sensorium (sensing calls
/ total action calls, benchmarked against Civ VI's 1–2%). Implemented natively
on AgentSociety OTel spans: a `react.tool` span carries `react.action` telling
us what the tool did. We classify actions into sensing vs acting.

Semantic note (differs from AFI): in AS, `observe` is the env's auto-generated
"call every observe tool" perception phase that runs structurally each ReAct
turn — it is not always an agent's *deliberate* choice to sense. So the ratio
here measures "perception footprint in the action stream", not "agent's
chose-to-sense frequency". Still a useful pathology signal: abnormally low
observe share = agent acting without perceiving; abnormally high = stuck
perceiving without acting.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from afi.audit.load import agent_id, attr, spans_by_agent, tick_of

# Sensing = reads state without mutating it. Acting = mutates state / runs skill.
SENSING_ACTIONS = {"observe", "read"}
# ask_env is ambiguous (can be readonly query or a mutate); report separately.
AMBIGUOUS_ACTIONS = {"ask_env"}


def _classify(action: str) -> str:
    if action in SENSING_ACTIONS:
        return "sensing"
    if action in AMBIGUOUS_ACTIONS:
        return "ambiguous"
    return "acting"


def sensorium_report(spans: List[dict]) -> Dict:
    """Compute per-agent + world sensing ratios and per-tick trend.

    Returns:
      {
        "per_agent": {agent_id: {sensing, acting, ambiguous, total, ratio}},
        "world": {sensing, acting, ambiguous, total, ratio},
        "per_tick": {tick: {sensing, acting, total, ratio}},
        "benchmark": "Civ VI 1–2%",
      }
    """
    tool_spans = [s for s in spans if s.get("name") == "react.tool"]
    per_agent: Dict[int, Dict] = defaultdict(lambda: {"sensing": 0, "acting": 0, "ambiguous": 0, "total": 0})
    per_tick: Dict[int, Dict] = defaultdict(lambda: {"sensing": 0, "acting": 0, "total": 0})
    world = {"sensing": 0, "acting": 0, "ambiguous": 0, "total": 0}

    for s in tool_spans:
        action = attr(s, "react.action", "?")
        cls = _classify(action)
        aid = agent_id(s)
        if aid is not None:
            per_agent[aid][cls] += 1
            per_agent[aid]["total"] += 1
        world[cls] += 1
        world["total"] += 1
        tk = tick_of(s)
        if tk is not None:
            per_tick[tk][cls if cls != "ambiguous" else "sensing"] += 1
            per_tick[tk]["total"] += 1

    for d in per_agent.values():
        d["ratio"] = round(d["sensing"] / d["total"], 4) if d["total"] else 0.0
    world["ratio"] = round(world["sensing"] / world["total"], 4) if world["total"] else 0.0
    for d in per_tick.values():
        d["ratio"] = round(d["sensing"] / d["total"], 4) if d["total"] else 0.0

    return {
        "per_agent": dict(per_agent),
        "world": world,
        "per_tick": dict(sorted(per_tick.items())),
        "benchmark": "Civ VI 1–2%",
    }


def format_sensorium(rep: Dict) -> str:
    w = rep["world"]
    lines = [
        "============================================================",
        "SENSORIUM ANALYSIS",
        "============================================================",
        f"World sensing ratio:  {w['ratio']*100:.1f}%  (benchmark: {rep['benchmark']})  "
        f"[sensing={w['sensing']} acting={w['acting']} ambiguous={w['ambiguous']} total={w['total']}]",
        "",
        "Per-agent sensing ratios:",
    ]
    for aid, d in sorted(rep["per_agent"].items()):
        bar = "█" * int(d["ratio"] * 40)
        lines.append(f"  agent {aid}: {d['ratio']*100:5.1f}%  {bar}  "
                     f"[s={d['sensing']} a={d['acting']} amb={d['ambiguous']}]")
    if rep["per_tick"]:
        lines.append("")
        lines.append("Per-tick trend (world sensing ratio):")
        for tk, d in rep["per_tick"].items():
            bar = "▪" * int(d["ratio"] * 40)
            lines.append(f"  tick {tk:>6}: {d['ratio']*100:5.1f}%  {bar}")
    return "\n".join(lines)
