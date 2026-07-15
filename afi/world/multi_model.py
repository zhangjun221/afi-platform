"""Multi-model harness — run one scenario across N LLMs, compare AWI.

Orchestrates: for each model, build the scenario config + run AS (via the
adapter) + collect the run_dir. Then compute AWI per run, build the cross-model
comparison table + statistics + M1-vs-EW qualitative bucket.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from afi.audit.awi import compute_awi, compute_awi_timeline
from afi.audit.comparison import compare_awi, format_comparison, m1_vs_ew
from afi.audit.statistical import awi_stats, model_significance, format_stats


def run_multi_model(
    scenario_path: str,
    models: List[str],
    run_root: str | Path,
    preset: str | None = None,
    as_home: str | None = None,
) -> List[tuple]:
    """Run `scenario` once per model under `<run_root>/<model>/`. Returns [(model, run_dir)]."""
    from afi.backend.agentsociety import AgentSocietyAdapter, run_from_files
    from afi.world.scenario import load_scenario, write_config
    from afi.world.scenario_presets import apply_preset

    run_root = Path(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    adapter = AgentSocietyAdapter(as_home=as_home) if as_home else AgentSocietyAdapter()
    scenario = load_scenario(scenario_path)
    if preset:
        scenario = apply_preset(scenario, preset)

    results = []
    for m in models:
        run_dir = run_root / m
        staging = run_root / (m + "_config")
        cfg, steps = write_config(scenario, staging)
        print(f"[multi] model={m} -> {run_dir}")
        r = run_from_files(adapter, init_config_path=cfg, steps_path=steps, out_dir=run_dir, model=m)
        results.append((m, str(r.run_dir)))
        print(f"[multi] done {m}: {r.steps} steps, {r.agent_count} agents")
    return results


def compare_runs(labeled_runs: List[tuple]) -> dict:
    """labeled_runs: [(label, run_dir)] -> {comparison, stats, significance, m1_vs_ew}."""
    from afi.audit.awi import _count_agents

    cmp = compare_awi(labeled_runs)
    runs_by_model = {l: [rd] for l, rd in labeled_runs}  # 1 run/model -> stats n=1 (trend)
    stats = awi_stats([rd for _, rd in labeled_runs])
    sig = model_significance(runs_by_model)
    # M1-vs-EW qualitative bucket per model
    m1_lines = []
    for label, rd in labeled_runs:
        snap = compute_awi(rd)
        total = _count_agents(rd) or 5
        ratio = snap.agents_alive / total if total else 0.0
        bucket = (
            "sustains (≈ EW Claude/Gemini)" if ratio >= 0.8
            else ("collapses (≈ EW Grok/GPT-5 Mini=0)" if ratio <= 0.2 else "partial (≈ EW Mixed)")
        )
        m1_lines.append(f"  {label}: {snap.agents_alive}/{total} alive -> {bucket}")
    m1_block = (
        "=== M1 vs EW Season1 (qualitative — different models, directional only) ===\n"
        + "\n".join(m1_lines)
        + "\n  EW Season1 baselines: Claude=10/10, Gemini=10/10, Grok=0/10, GPT-5Mini=0/10, Mixed=3/10\n"
        "  note: our models are qwen-family (百炼), not EW's; directional bucket, not matched comparison."
    )
    return {"comparison": cmp, "stats": stats, "significance": sig, "m1_vs_ew": m1_block}


def format_multi_report(rep: dict) -> str:
    out = [format_comparison(rep["comparison"]), "", format_stats(rep["stats"]), "", rep["m1_vs_ew"]]
    sig = rep["significance"]
    if sig:
        out.append("\n=== cross-model divergence (non-formal) ===")
        for label, d in sig.items():
            if d.get("divergent"):
                out.append(f"  {label}: divergent — means {d['model_means']} spread={d['spread']} pooled_std={d['pooled_std']}")
    return "\n".join(out)
