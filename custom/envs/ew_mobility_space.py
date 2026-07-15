"""EWMobilitySpace — EW landmark-based movement tracking (AWI M3 true compute).

Lightweight MobilitySpace substitute that does NOT require a city .pb map.
Agents move between named EW landmarks. Each step the env records position
as (lng, lat) using preset EW landmark coordinates, writing
``replay/mobility_agent_state.<hex>.jsonl`` shards compatible with
afi/audit/replay_data.load_mobility_agent_states().

After patching afi/audit/awi._m3_space() to read these shards, AWI M3
upgrades from "proxy" to "computed".

stdlib + agentsociety2 only (no afi import, runs in AS venv subprocess).
"""
from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

from agentsociety2.env import EnvBase, tool
from agentsociety2.logger import get_logger
from agentsociety2.storage import ColumnDef
from agentsociety2.storage.workspace_state import atomic_write_text

_logger = get_logger()

# EW landmark coordinates (fictional bbox 116.25-116.45 E, 39.85-39.95 N)
_DEFAULT_LANDMARKS: Dict[str, Dict[str, Any]] = {
    "Town Hall":     {"lng": 116.350, "lat": 39.920, "desc": "Governance chamber."},
    "Police Station":{"lng": 116.355, "lat": 39.912, "desc": "Law enforcement."},
    "Cafe":          {"lng": 116.340, "lat": 39.916, "desc": "Social hub."},
    "TechHub":       {"lng": 116.362, "lat": 39.910, "desc": "Innovation space."},
    "Library":       {"lng": 116.335, "lat": 39.918, "desc": "Research center."},
    "Central Plaza": {"lng": 116.348, "lat": 39.914, "desc": "Main gathering space."},
    "Market":        {"lng": 116.342, "lat": 39.908, "desc": "Economic exchange."},
    "Victory Arch":  {"lng": 116.358, "lat": 39.925, "desc": "Civic landmark."},
    "Home":          {"lng": 116.345, "lat": 39.905, "desc": "Private residence."},
    "Park":          {"lng": 116.330, "lat": 39.920, "desc": "Green leisure space."},
}

_STATE_REL = "state/EW_MOBILITY_STATE.json"


class EWMobilitySpace(EnvBase):
    """Landmark-based mobility env for EW agents. Upgrades AWI M3 to computed."""

    _env_state_columns: ClassVar[list[ColumnDef]] = [
        ColumnDef("total_moves", "INTEGER"),
        ColumnDef("unique_locations_visited", "INTEGER"),
        ColumnDef("agents_active", "INTEGER"),
    ]

    def __init__(
        self,
        agent_ids: Optional[List[int]] = None,
        landmarks: Optional[Dict[str, Dict[str, Any]]] = None,
        **kwargs,
    ):
        if kwargs:
            _logger.warning(f"EWMobilitySpace unknown kwargs: {list(kwargs.keys())}")
        super().__init__()
        self._agent_ids: List[int] = [int(x) for x in (agent_ids or [1, 2, 3, 4, 5])]
        self._landmarks: Dict[str, Dict[str, Any]] = landmarks or _DEFAULT_LANDMARKS
        self._agent_locations: Dict[int, str] = {}
        self._total_moves: int = 0
        self._all_visited: set = set()
        self._step_counter: int = 0
        self._shard_rows: List[dict] = []

        lm_names = list(self._landmarks.keys())
        for aid in self._agent_ids:
            start = random.choice(lm_names)
            self._agent_locations[aid] = start
            self._all_visited.add(start)

    # ── persistence ───────────────────────────────────────────────────────────

    async def to_workspace(self, workspace_path=None) -> None:
        root = workspace_path or self._workspace_root
        if root is None:
            return
        root = Path(root)
        state = {
            "step_counter": self._step_counter,
            "total_moves": self._total_moves,
            "agent_locations": {str(k): v for k, v in self._agent_locations.items()},
        }
        atomic_write_text(root / _STATE_REL, json.dumps(state, ensure_ascii=False))

        if self._shard_rows:
            shard_id = format(abs(hash(str(self._step_counter))) & 0xFFFF, "04x")
            replay_dir = root.parent.parent / "replay"
            replay_dir.mkdir(parents=True, exist_ok=True)
            shard_path = replay_dir / f"mobility_agent_state.{shard_id}.jsonl"
            lines = [json.dumps(r, ensure_ascii=False) for r in self._shard_rows]
            atomic_write_text(shard_path, "\n".join(lines) + "\n")
            self._shard_rows = []

    async def restore(self, workspace_path=None) -> bool:
        root = workspace_path or self._workspace_root
        if root is None:
            return False
        p = Path(root) / _STATE_REL
        if not p.exists():
            return False
        try:
            state = json.loads(p.read_text(encoding="utf-8"))
            self._step_counter = state.get("step_counter", 0)
            self._total_moves = state.get("total_moves", 0)
            for k, v in state.get("agent_locations", {}).items():
                self._agent_locations[int(k)] = v
            return True
        except Exception:
            return False

    async def init(self, start_t: datetime) -> None:
        await super().init(start_t)

    async def step(self, tick: int, t: datetime) -> None:
        self._step_counter += 1
        for aid in self._agent_ids:
            loc = self._agent_locations.get(aid, "Home")
            lm = self._landmarks.get(loc, list(self._landmarks.values())[0])
            self._shard_rows.append({
                "agent_id": aid,
                "step": self._step_counter,
                "t": t.isoformat(),
                "lng": lm["lng"] + random.gauss(0, 0.0001),
                "lat": lm["lat"] + random.gauss(0, 0.0001),
                "aoi_id": None,
                "poi_id": None,
                "status": "active",
                "location_name": loc,
            })
            self._all_visited.add(loc)
        await self.to_workspace()

    async def close(self) -> None:
        await self.to_workspace()

    async def get_env_state(self) -> dict:
        return {
            "total_moves": self._total_moves,
            "unique_locations_visited": len(self._all_visited),
            "agents_active": len(self._agent_ids),
        }

    # ── tools ─────────────────────────────────────────────────────────────────

    @tool(readonly=False, kind=None)
    async def move_to(self, agent_id: int, location_name: str) -> dict:
        """Move agent to a named EW landmark.

        Args:
            agent_id: the agent's numeric ID
            location_name: landmark name (call list_landmarks to see options)
        """
        if location_name not in self._landmarks:
            matches = [n for n in self._landmarks if location_name.lower() in n.lower()]
            if matches:
                location_name = matches[0]
            else:
                return {"ok": False, "error": f"Unknown: '{location_name}'"}
        self._agent_locations[agent_id] = location_name
        self._total_moves += 1
        lm = self._landmarks[location_name]
        return {"ok": True, "location_name": location_name,
                "lng": lm["lng"], "lat": lm["lat"], "desc": lm.get("desc", "")}

    @tool(readonly=True, kind=None)
    async def get_my_location(self, agent_id: int) -> dict:
        """Get the agent's current location (name and coordinates).

        Args:
            agent_id: the agent's numeric ID
        """
        loc = self._agent_locations.get(agent_id, "Home")
        lm = self._landmarks.get(loc, {"lng": 116.348, "lat": 39.914, "desc": ""})
        return {"location_name": loc, "lng": lm["lng"], "lat": lm["lat"],
                "desc": lm.get("desc", "")}

    @tool(readonly=True, kind=None)
    async def list_landmarks(self, agent_id: int) -> dict:
        """List all EW landmarks available to move to.

        Args:
            agent_id: the agent's numeric ID (for context)
        """
        return {
            "landmarks": [{"name": n, "desc": v.get("desc", "")}
                           for n, v in self._landmarks.items()],
            "current_location": self._agent_locations.get(agent_id, "Home"),
        }
