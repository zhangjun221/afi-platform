"""Load AgentSociety 2 trace spans + env state from a run directory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def load_spans(run_dir: str | Path) -> List[dict]:
    """Load all OTel spans from `<run_dir>/trace/trace_*.jsonl`, sorted by start time.

    Each span is the raw JSON dict as written by agentsociety2.trace. Returns a
    flat list (shards are concatenated). Spans with missing start_time sort first.
    """
    trace_dir = Path(run_dir) / "trace"
    if not trace_dir.is_dir():
        raise FileNotFoundError(f"no trace dir at {trace_dir}")
    spans: List[dict] = []
    for shard in sorted(trace_dir.glob("trace_*.jsonl")):
        with shard.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                spans.append(json.loads(line))
    spans.sort(key=lambda s: s.get("start_time_unix_nano", 0))
    return spans


def load_env_state(run_dir: str | Path, env_module: str = "SimpleSocialSpace") -> dict:
    """Load `<run_dir>/env/<env_module>/state/ENV_STATE.json`. Returns {} if absent."""
    p = Path(run_dir) / "env" / env_module / "state" / "ENV_STATE.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


# ── per-span helpers ──────────────────────────────────────────────────────────

def agent_id(span: dict) -> Optional[int]:
    """Agent id carried in the span's resource, or None."""
    res = span.get("resource") or {}
    return res.get("agent.id")


def tick_of(span: dict) -> Optional[int]:
    """The sim tick (seconds) this span belongs to, from attributes.agent.tick."""
    return (span.get("attributes") or {}).get("agent.tick")


def ts_of(span: dict) -> int:
    """Start time in unix nanoseconds (0 if missing)."""
    return span.get("start_time_unix_nano", 0)


def attr(span: dict, key: str, default=None):
    """Read one attribute from span['attributes']."""
    return (span.get("attributes") or {}).get(key, default)


def spans_by_name(spans: Iterable[dict], name: str) -> List[dict]:
    return [s for s in spans if s.get("name") == name]


def spans_by_agent(spans: Iterable[dict]) -> Dict[int, List[dict]]:
    """Group spans by agent.id (None-keyed spans dropped)."""
    out: Dict[int, List[dict]] = {}
    for s in spans:
        aid = agent_id(s)
        if aid is None:
            continue
        out.setdefault(aid, []).append(s)
    return out
