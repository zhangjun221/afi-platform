"""Load AS run_dir replay data (env timeline + per-agent state) for the HTML report.

Reads files directly from disk — no backend dependency:
  - SOCIETY_STEP.json                     → run overview (step_count, current_time)
  - replay/simple_social_env_state.*.jsonl → per-step env state
  - agents/agent_XXXX/AGENT.json          → per-agent final state
  - agents/agent_XXXX/MEMORY.md           → LLM-consolidated memory summary
  - agents/agent_XXXX/memory/episodes.jsonl → per-tick episode narrative
  - agents/agent_XXXX/state/daily_guidance/*/story.yaml → daily story segments
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def load_run_meta(run_dir: str | Path) -> dict:
    """Run overview: step_count, current_time, terminated."""
    p = Path(run_dir) / "SOCIETY_STEP.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def load_env_timeline(run_dir: str | Path) -> List[dict]:
    """Per-step env state from replay shards. Env-agnostic: globs all
    `*_env_state.*.jsonl` shards (SimpleSocialSpace, CommonsTragedyEnv, ...).
    Sorted by step. Each row is the raw shard dict (fields differ per env)."""
    rd = Path(run_dir) / "replay"
    rows = []
    if not rd.is_dir():
        return rows
    for shard in rd.glob("*_env_state.*.jsonl"):
        for line in shard.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    rows.sort(key=lambda r: r.get("step", 0))
    return rows


def _env_timeline_fields(rows: List[dict]) -> List[str]:
    """Pick stable columns for the env timeline table: step + t first, then the
    most informative numeric/state keys present across rows."""
    if not rows:
        return []
    keys = []
    for r in rows:
        for k in r.keys():
            if k not in keys and k not in ("step", "t"):
                keys.append(k)
    # prefer known informative fields, then the rest
    priority = ["round_number", "current_pool_resources", "total_messages_sent",
                "active_groups", "total_agents", "initial_pool_resources",
                "max_extraction_per_agent"]
    ordered = ["step", "t"] + [k for k in priority if k in keys] + \
              [k for k in keys if k not in priority]
    return ordered[:9]  # cap columns


def _read_memory_md(agent_dir: Path) -> str:
    p = agent_dir / "MEMORY.md"
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def _read_episodes(agent_dir: Path) -> List[dict]:
    p = agent_dir / "memory" / "episodes.jsonl"
    if not p.is_file():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _read_story(agent_dir: Path) -> str:
    """First ~6 lines of the daily-guidance story.yaml (the plan)."""
    dg = agent_dir / "state" / "daily_guidance"
    if not dg.is_dir():
        return ""
    yamls = sorted(dg.rglob("story.yaml"))
    if not yamls:
        return ""
    return "\n".join(yamls[0].read_text(encoding="utf-8").splitlines()[:10])


def _agent_name(agent_json: dict) -> str:
    """Prefer profile.profile.name, fallback to top-level name, fallback to id."""
    prof = agent_json.get("profile") or {}
    if isinstance(prof, dict):
        inner = prof.get("profile") or {}
        if isinstance(inner, dict) and inner.get("name"):
            return inner["name"]
    return agent_json.get("name") or f"agent_{agent_json.get('agent_id')}"


def load_agents(run_dir: str | Path) -> List[dict]:
    """Per-agent: name, step_count, episode_count, memory_md, episodes, story."""
    agents_dir = Path(run_dir) / "agents"
    out = []
    if not agents_dir.is_dir():
        return out
    for ad in sorted(agents_dir.iterdir()):
        if not ad.is_dir() or not (ad / "AGENT.json").is_file():
            continue
        aj = json.loads((ad / "AGENT.json").read_text(encoding="utf-8"))
        episodes = _read_episodes(ad)
        out.append({
            "dir": ad.name,
            "id": aj.get("agent_id"),
            "name": _agent_name(aj),
            "step_count": aj.get("step_count", 0),
            "memory_md": _read_memory_md(ad),
            "episode_count": len(episodes),
            "episodes": episodes,
            "story": _read_story(ad),
        })
    return out


def load_replay_summary(run_dir: str | Path) -> dict:
    """Everything the HTML report needs for the Replay section."""
    return {
        "meta": load_run_meta(run_dir),
        "env_timeline": load_env_timeline(run_dir),
        "agents": load_agents(run_dir),
        "mobility_states": load_mobility_agent_states(run_dir),
    }


def load_mobility_agent_states(run_dir: str | Path) -> List[dict]:
    """Per-agent per-step position records from MobilitySpace replay shards.
    Each: {agent_id, step, t, lng, lat, aoi_id, poi_id, status}. Empty for non-mobility runs."""
    rd = Path(run_dir) / "replay"
    rows = []
    if not rd.is_dir():
        return rows
    for shard in rd.glob("mobility_agent_state.*.jsonl"):
        for line in shard.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    rows.sort(key=lambda r: (r.get("agent_id", 0), r.get("step", 0)))
    return rows
