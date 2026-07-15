"""Statistical analysis over AWI — ports AFI statistical_analysis idea.

Multi-run / multi-model AWI mean/std/95%CI + simple cross-model significance.
Sample sizes are small (2–3 runs/model) → explicitly "trend, not formal stat".
stdlib-only; reads run_dirs via afi.audit.awi.
"""
from __future__ import annotations

import math
from typing import Dict, List

from afi.audit.awi import compute_awi, compute_awi_timeline

# numeric AWI families to aggregate (label, attr, unit)
_NUMERIC_METRICS = [
    ("M1", "agents_alive", ""),
    ("M2", "total_crimes", ""),
    ("M4", "avg_tools_used", ""),
    ("M5_proposals", "total_proposals", ""),
    ("M5_votes", "votes_cast", ""),
    ("M5_approval", "approval_rate", ""),
    ("M5_herd", "herd_ratio", ""),
    ("M6", "total_messages", ""),
    ("M7_edges", "social_edges", ""),
    ("M7_density", "social_density", ""),
    ("M8_gini", "gini", ""),
    ("M8_credits", "total_credits", ""),
    ("M9_version", "constitution_version", ""),
    ("M9_passed", "proposals_passed", ""),
]


def _mean_std(values: List[float]) -> tuple[float, float]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    if n < 2:
        return mean, 0.0
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return mean, math.sqrt(var)


def _ci95(values: List[float]) -> tuple[float, float]:
    """95% CI half-width via t≈2 (small-sample approximation). Non-formal."""
    n = len(values)
    mean, std = _mean_std(values)
    if n < 2 or std == 0:
        return mean, 0.0
    # t_{0.025, df} ≈ 2 for small df; honest rough CI
    hw = 2.0 * std / math.sqrt(n)
    return mean, hw


def awi_stats(run_dirs: List[str]) -> Dict[str, dict]:
    """Per-metric mean/std/CI95/min/max across runs (trend, non-formal)."""
    snaps = [compute_awi(d) for d in run_dirs]
    out: Dict[str, dict] = {}
    for label, attr, unit in _NUMERIC_METRICS:
        vals = [float(getattr(s, attr, 0.0) or 0.0) for s in snaps]
        mean, std = _mean_std(vals)
        cmean, hw = _ci95(vals)
        out[label] = {
            "n": len(vals),
            "mean": round(mean, 4),
            "std": round(std, 4),
            "ci95": [round(cmean - hw, 4), round(cmean + hw, 4)],
            "min": round(min(vals), 4) if vals else 0.0,
            "max": round(max(vals), 4) if vals else 0.0,
            "unit": unit,
        }
    return out


def model_significance(runs_by_model: Dict[str, List[str]]) -> Dict[str, dict]:
    """Cross-model: per metric, each model's mean ± std; flag divergence.

    Non-formal (small samples): a metric is 'divergent' if model means differ
    by > pooled std. Honest about low power.
    """
    per_model = {m: awi_stats(dirs) for m, dirs in runs_by_model.items()}
    out: Dict[str, dict] = {}
    for label, attr, unit in _NUMERIC_METRICS:
        means = {m: per_model[m][label]["mean"] for m in per_model}
        stds = {m: per_model[m][label]["std"] for m in per_model}
        if len(means) < 2:
            continue
        mvals = list(means.values())
        spread = max(mvals) - min(mvals)
        pooled_std = math.sqrt(sum(s ** 2 for s in stds.values()) / len(stds)) if stds else 0.0
        out[label] = {
            "model_means": means,
            "spread": round(spread, 4),
            "pooled_std": round(pooled_std, 4),
            "divergent": bool(pooled_std > 0 and spread > pooled_std),
        }
    return out


def format_stats(stats: Dict[str, dict]) -> str:
    lines = ["=== AWI statistics (mean ± std, 95% CI) ===  [trend, non-formal]"]
    for label, s in stats.items():
        lines.append(
            f"  {label:14s}: {s['mean']:.3f} ± {s['std']:.3f}  CI95 [{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}]  (n={s['n']}, range {s['min']}–{s['max']})"
        )
    return "\n".join(lines)
