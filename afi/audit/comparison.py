"""Cross-run / cross-model AWI comparison (fills the sealed-line placeholder).

Pure functions on run_dirs: build a 9-family × runs table + EW M1 baseline
column for the only metric EW published Season1 ground-truth on.
"""
from __future__ import annotations

from typing import Dict, List

from afi.audit.awi import compute_awi, format_awi_report

# EW Season 1 published M1 ground-truth (start=10 agents; awi_metrics.md).
EW_SEASON1_M1 = {
    "Claude Sonnet 4.6": 10,  # sustained
    "Gemini 3 Flash": 10,  # sustained
    "Grok 4.1 Fast": 0,  # collapsed
    "GPT-5 Mini": 0,  # collapsed
    "Mixed": 3,  # partial
}


def compare_awi(labeled_runs: List[tuple]) -> Dict:
    """labeled_runs: [(label, run_dir), ...] -> {labels, families: {M: {label: value}}}."""
    snaps = [(label, compute_awi(rd)) for label, rd in labeled_runs]
    labels = [l for l, _ in snaps]
    families = {
        "M1 agents_alive": {l: s.agents_alive for l, s in snaps},
        "M2 total_crimes": {l: s.total_crimes for l, s in snaps},
        "M4 avg_tools": {l: round(s.avg_tools_used, 2) for l, s in snaps},
        "M5 proposals": {l: s.total_proposals for l, s in snaps},
        "M5 votes": {l: s.votes_cast for l, s in snaps},
        "M5 approval": {l: round(s.approval_rate, 2) for l, s in snaps},
        "M5 herd": {l: round(s.herd_ratio, 2) for l, s in snaps},
        "M6 messages": {l: s.total_messages for l, s in snaps},
        "M7 edges": {l: s.social_edges for l, s in snaps},
        "M7 density": {l: round(s.social_density, 3) for l, s in snaps},
        "M8 gini": {l: round(s.gini, 3) for l, s in snaps},
        "M8 credits": {l: round(s.total_credits, 0) for l, s in snaps},
        "M9 version": {l: s.constitution_version for l, s in snaps},
        "M9 passed": {l: s.proposals_passed for l, s in snaps},
    }
    return {"labels": labels, "families": families}


def format_comparison(cmp: Dict) -> str:
    labels = cmp["labels"]
    lines = ["=== cross-run AWI comparison ==="]
    lines.append("  " + "metric".ljust(22) + "  " + "  ".join(l.ljust(18) for l in labels))
    for fam, vals in cmp["families"].items():
        row = "  " + fam.ljust(22) + "  " + "  ".join(str(vals.get(l, "")).ljust(18) for l in labels)
        lines.append(row)
    return "\n".join(lines)


def m1_vs_ew(our_label: str, our_alive: int, our_total: int) -> str:
    """Qualitative M1 comparison to EW Season1 published numbers.

    EW models ≠ ours (we use qwen), so this is directional: does our run
    *collapse* (like Grok/GPT-5 Mini = 0), *sustain* (like Claude/Gemini = 10),
    or *partial* (like Mixed = 3)?
    """
    ratio = our_alive / our_total if our_total else 0.0
    if ratio >= 0.8:
        bucket = "sustains (≈ EW Claude/Gemini = full survival)"
    elif ratio <= 0.2:
        bucket = "collapses (≈ EW Grok/GPT-5 Mini = 0)"
    else:
        bucket = "partial (≈ EW Mixed = some survive)"
    lines = [
        f"=== M1 vs EW Season1 (qualitative — different models, directional only) ===",
        f"  ours ({our_label}): {our_alive}/{our_total} alive -> {bucket}",
        f"  EW Season1 baselines: Claude=10/10, Gemini=10/10, Grok=0/10, GPT-5Mini=0/10, Mixed=3/10",
        f"  note: our models are qwen-family (百炼), not EW's; this is a directional bucket, not a matched comparison.",
    ]
    return "\n".join(lines)
