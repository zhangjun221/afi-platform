"""Counterfactual rerun engine — branch the world at a suspected first domino.

Phase-1 flagship layer ②. **AS-coupled** (re-runs AgentSociety), unlike the
attribution layer ① which is backend-agnostic. Concordia backend is a future
interface (not implemented — see strategy-impact-analysis.md honest scope).

The world-branching idea (pilot-plan.md §四): given a localized first-domino
candidate (e.g. "agent 1 missed recharge at T0=11"), re-run the SAME scenario
with an intervention that removes the domino (force the agent to recharge when
low), and measure whether the collapse outcome is averted / delayed.

v0 scope:
  - single-point intervention via founding-day directive (coarse; precise
    mid-run step injection is v1 — needs AS multi-step split, not yet validated).
  - one counterfactual rerun per domino; n=1 (AS re-run is non-deterministic +
    costly; we compare qualitative direction, not significance — see §七).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional


def build_counterfactual_scenario(
    scenario_path: str | Path, domino: dict, out_yaml: str | Path
) -> Path:
    """Append a counterfactual recharge directive for `domino['agent_id']` to
    the scenario's founding-day intervene instruction.

    v0 strategy: strengthen the survival directive for the domino agent
    ("you MUST recharge when energy < 30") rather than inject at exact step T0
    (mid-run step injection is v1). This tests the domino hypothesis: if forcing
    recharge averts/delays collapse, the missed_recharge domino is confirmed.
    """
    import yaml

    sc = yaml.safe_load(Path(scenario_path).read_text(encoding="utf-8"))
    aid = domino["agent_id"]
    directive = (
        f"\n\nCOUNTERFACTUAL DIRECTIVE (phase-1 attribution test): agent {aid}, "
        f"you MUST call recharge(agent_id={aid}, amount=50) at the very start of "
        f"every step where your energy is below 30. This is mandatory for survival; "
        f"do it BEFORE any other action on such steps."
    )
    injected = False
    for s in sc.get("steps", []):
        if s.get("type") == "intervene" and "instruction" in s:
            s["instruction"] = s["instruction"] + directive
            injected = True
    if not injected:
        # scenario has no intervene step — prepend one with just the directive
        sc.setdefault("steps", []).insert(0, {
            "type": "intervene",
            "instruction": directive.strip(),
        })
    out = Path(out_yaml)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        yaml.safe_dump(sc, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )
    return out


def counterfactual_rerun(
    scenario_path: str | Path,
    domino: dict,
    *,
    model: str,
    run_dir_out: str | Path,
    as_home: Optional[str | Path] = None,
) -> dict:
    """Re-run the scenario with the counterfactual directive injected. Returns
    the new run_dir + whether the directive landed (checked post-hoc).

    AS-coupled: invokes AgentSocietyAdapter + run_from_files.
    """
    from afi.backend.agentsociety import AgentSocietyAdapter, run_from_files
    from afi.world.scenario import load_scenario, write_config

    run_dir_out = Path(run_dir_out)
    cf_yaml = run_dir_out.parent / (run_dir_out.name + "_cf.yaml")
    build_counterfactual_scenario(scenario_path, domino, cf_yaml)

    scenario = load_scenario(cf_yaml)
    staging = run_dir_out.parent / (run_dir_out.name + "_config")
    cfg_path, steps_path = write_config(scenario, staging)

    adapter = AgentSocietyAdapter(as_home=as_home) if as_home else AgentSocietyAdapter()
    result = run_from_files(
        adapter,
        init_config_path=cfg_path,
        steps_path=steps_path,
        out_dir=run_dir_out,
        model=model,
    )
    return {
        "run_dir": str(result.run_dir),
        "model": result.model,
        "steps": result.steps,
        "agent_count": result.agent_count,
        "cf_yaml": str(cf_yaml),
        "domino": domino,
    }


def _alive_curve(run_dir: str | Path) -> Dict[int, int]:
    """Per-step count of alive agents (alive=1) from energy_agent_state replay."""
    from afi.audit.awi import _read_table

    rows = _read_table(run_dir, "energy_agent_state")
    by_step: Dict[int, int] = {}
    for r in rows:
        step = int(r.get("step", 0))
        if int(r.get("alive", 1)) == 1:
            by_step[step] = by_step.get(step, 0) + 1
    return dict(sorted(by_step.items()))


def _recharge_call_steps(run_dir: str | Path) -> List[int]:
    """Steps where a recharge* action was actually called (trace)."""
    from afi.audit.load import load_spans
    from afi.audit.causal import _index
    from afi.audit.tunnel_vision import _resolve_tick
    from afi.audit.load import agent_id, attr

    spans = load_spans(run_dir)
    by_id = _index(spans)
    steps = []
    for s in spans:
        if s.get("name") != "react.tool":
            continue
        if "recharge" in (attr(s, "react.action", "") or ""):
            st = _resolve_tick(s, by_id)
            if st is not None:
                steps.append(st)
    return sorted(set(steps))


def compare_m1(baseline_run: str, cf_run: str) -> dict:
    """Compare M1 alive curve baseline vs counterfactual.

    Returns alive curves + summary: did CF avert/delay the collapse of the
    domino agent + of the population.
    """
    b_curve = _alive_curve(baseline_run)
    cf_curve = _alive_curve(cf_run)
    b_steps = sorted(b_curve)
    cf_steps = sorted(cf_curve)
    max_step = max(b_steps + cf_steps, default=0)
    b_end = b_curve.get(max_step if max_step in b_curve else (b_steps[-1] if b_steps else 0), 0)
    cf_end = cf_curve.get(max_step if max_step in cf_curve else (cf_steps[-1] if cf_steps else 0), 0)
    # domino-agent survival in cf (is the domino agent alive at end of cf?)
    from afi.audit.awi import _read_table
    domino_alive_end = None
    # caller fills domino separately if needed; here just population
    cf_recharge_steps = _recharge_call_steps(cf_run)
    directive_landed = len(cf_recharge_steps) > 0
    return {
        "baseline_alive_curve": b_curve,
        "cf_alive_curve": cf_curve,
        "baseline_alive_at_end": b_end,
        "cf_alive_at_end": cf_end,
        "cf_recharge_call_steps": cf_recharge_steps,
        "directive_landed": directive_landed,
        "population_delta_end": cf_end - b_end,
        "averted_or_delayed": cf_end > b_end,
    }
