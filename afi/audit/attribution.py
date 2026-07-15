"""First-domino attribution — localize the earliest action that triggered an
outcome, plus a counterfactual-rerun orchestrator.

Phase-1 flagship layer (① attribution + ③ orchestrator). Backend-agnostic on
the attribution side: `localize_first_domino` works on the event graph from
`causal.build_event_graph`, which only reads run_dir. The counterfactual rerun
(②) is AS-coupled and lives in `afi.world.counterfactual`.

v0 scope (per docs/phase1-first-domino/pilot-plan.md §〇.5):
  - outcome: `m1_collapse` only (hardcoded energy-trajectory + missed-recharge
    backtrack). Extension point: OUTCOME_SPECS dict — add m8_hoarding /
    m9_capture / governance_stagnation later as localized increments.
  - algorithm: path-tracing (NOT path Shapley; that's v1).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from afi.audit.causal import build_event_graph, format_event_graph_summary


# ── extension point ──────────────────────────────────────────────────────────
# v0 only fills m1_collapse. New outcomes = new entry here + a localize_* fn.
OUTCOME_SPECS = {
    "m1_collapse": {
        "description": "M1 population collapse — agent(s) died from energy depletion",
        "localizer": "_localize_m1_collapse",  # name; resolved below
    },
    # future (v0 not implemented — placeholders so the structure is visible):
    "m8_hoarding": {"description": "M8 economic polarization (Gini jump)", "localizer": None},
    "m9_capture": {"description": "M9 governance capture (constitution hijack)", "localizer": None},
    "governance_stagnation": {"description": "runtime governance stagnation", "localizer": None},
}


# ── helpers ──────────────────────────────────────────────────────────────────


def _estimate_consumption(steps: Dict[int, dict]) -> float:
    """Median per-step energy drop over alive steps (the agent's daily burn rate).

    Used to set the 'recoverable threshold' = 2× consumption (≈ 'if you don't
    recharge within ~2 steps you're dead'). Derived from the trajectory itself
    so it's robust to scenario param differences; falls back to 8.0 (EW default).
    """
    deltas: List[float] = []
    prev: Optional[float] = None
    for st in sorted(steps):
        e = steps[st].get("energy")
        if e is None:
            continue
        if prev is not None and steps[st].get("alive", 1) == 1:
            d = prev - e
            if d > 0:
                deltas.append(d)
        prev = e
    if not deltas:
        return 8.0
    deltas.sort()
    return deltas[len(deltas) // 2]


def _recharge_calls_in(steps: Dict[int, dict], lo: int, hi: int) -> List[tuple]:
    """All recharge* action calls in [lo, hi], as (step, ok)."""
    calls = []
    for st in sorted(steps):
        if st < lo or st > hi:
            continue
        for act in steps[st].get("actions", []):
            name = act.get("action") or ""
            if "recharge" in name:
                calls.append((st, act.get("ok")))
    return calls


# ── M1-collapse localizer (v0) ───────────────────────────────────────────────


def _localize_m1_collapse(graph: Dict) -> List[dict]:
    """For each dead agent, find the first step T0 where energy crossed the
    recoverable threshold (≤ 2× consumption), then check whether recharge was
    called in [T0, death]. Candidate domino kinds:
      - missed_recharge  : no recharge call at all in the dying window
      - blocked_recharge : recharge called but result.ok=False (economy/governance blocked)
      - recharge_but_died: recharge called + ok=True yet still died (anomaly — flag, not a clean domino)
    """
    candidates = []
    for aid, a in graph["agents"].items():
        d = a.get("died_at_step")
        if d is None:
            continue  # only dead agents contribute M1 dominoes
        steps = a["steps"]
        cons = _estimate_consumption(steps)
        threshold = 2 * cons
        # T0 = first step where energy ≤ threshold AND still alive (the 'last chance' step)
        T0: Optional[int] = None
        for st in sorted(steps):
            if st >= d:
                break
            e = steps[st].get("energy")
            if e is not None and e <= threshold and steps[st].get("alive", 1) == 1:
                T0 = st
                break
        if T0 is None:
            # energy never crossed threshold before death (e.g. sudden death) — skip
            continue
        calls = _recharge_calls_in(steps, T0, d)
        e_t0 = steps.get(T0, {}).get("energy")
        e_d = steps.get(d, {}).get("energy", 0.0)
        if not calls:
            kind = "missed_recharge"
            evidence = f"no recharge call in [{T0},{d}]; energy {e_t0}->{e_d} (consumption {cons:.1f}/step, threshold {threshold:.1f})"
        else:
            oks = [ok for _, ok in calls if ok is True]
            fails = [ok for _, ok in calls if ok is False]
            if oks:
                kind = "recharge_but_died"
                evidence = f"recharge called ok=True at {oks} in [{T0},{d}] yet died — anomaly, not clean domino"
            else:
                kind = "blocked_recharge"
                evidence = f"recharge called but ok=False at steps {[s for s,_ in fails]} — blocked (economy/governance)"
        candidates.append({
            "agent_id": aid,
            "kind": kind,
            "T0": T0,
            "died_at": d,
            "consumption": round(cons, 2),
            "threshold": round(threshold, 2),
            "evidence": evidence,
        })
    candidates.sort(key=lambda c: (c["T0"], c["agent_id"]))
    return candidates


_LOCALIZERS = {"m1_collapse": _localize_m1_collapse}


def localize_first_domino(graph: Dict, outcome: str = "m1_collapse") -> Dict:
    """Top-3 first-domino candidates for `outcome` in `graph`.

    v0: only m1_collapse. Returns {outcome, candidates (top-3), all, note}.
    """
    if outcome not in OUTCOME_SPECS:
        return {"outcome": outcome, "candidates": [], "note": f"unknown outcome '{outcome}'"}
    fn = _LOCALIZERS.get(outcome)
    if fn is None:
        return {"outcome": outcome, "candidates": [], "note": f"'{outcome}' not implemented in v0 (placeholder)"}
    all_c = fn(graph)
    return {
        "outcome": outcome,
        "candidates": all_c[:3],
        "all": all_c,
        "n_candidates": len(all_c),
    }


# ── orchestrator (③) ────────────────────────────────────────────────────────


def attribute(run_dir: str, outcome: str = "m1_collapse", write: bool = True) -> Dict:
    """Build event graph + localize first domino + (optional) write artifacts.

    Writes `<run_dir>/attribution/event_graph.json` and `first_domino.json`.
    Counterfactual rerun is NOT triggered here — call `afi.world.counterfactual.
    counterfactual_rerun` separately (it needs AS, is backend-coupled).
    """
    graph = build_event_graph(run_dir)
    loc = localize_first_domino(graph, outcome)
    report = {
        "run_dir": str(run_dir),
        "outcome": outcome,
        "graph_summary": {
            "n_agents": graph["n_agents"],
            "n_steps": graph["n_steps"],
            "spans_indexed": graph["spans_indexed"],
            "behavior_spans_dropped_fallback": graph.get("behavior_spans_dropped_fallback", 0),
        },
        "localization": loc,
    }
    if write:
        out_dir = Path(run_dir) / "attribution"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "event_graph.json").write_text(
            json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "first_domino.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return report


def format_attribution(rep: Dict) -> str:
    g = rep["graph_summary"]
    loc = rep["localization"]
    lines = [
        "============================================================",
        f"FIRST-DOMINO ATTRIBUTION  ({rep['outcome']})",
        "============================================================",
        f"run: {rep['run_dir']}",
        f"agents={g['n_agents']}  steps={g['n_steps']}  spans={g['spans_indexed']}",
        f"candidates: {loc.get('n_candidates', 0)}  (showing top-3)",
        "",
    ]
    if not loc.get("candidates"):
        lines.append(f"  no candidates. note: {loc.get('note', '')}")
        return "\n".join(lines)
    for c in loc["candidates"]:
        lines.append(f"  [{c['kind']}] agent {c['agent_id']}  T0={c['T0']}  died@{c['died_at']}")
        lines.append(f"      {c['evidence']}")
    return "\n".join(lines)
