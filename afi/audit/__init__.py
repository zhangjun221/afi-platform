"""Audit layer — native, backend-agnostic modules that read a backend run_dir.

Core (stdlib-only): load / sensorium / tunnel_vision / causal / decision_trace /
replay_data / html_report / __main__.
Optional deps: map_places & map_bg (pyproj/pycityproto/Pillow, for MobilitySpace),
collude.judge_with_llm (openai).
"""
from afi.audit.load import (
    load_spans,
    load_env_state,
    agent_id,
    tick_of,
    ts_of,
)

__all__ = [
    "load_spans",
    "load_env_state",
    "agent_id",
    "tick_of",
    "ts_of",
]
