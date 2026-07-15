"""LandmarkSpace — EW landmarks as an AS custom env (lightweight).

A2 ships a small set of named EW landmarks (BookWorm / Ad Tower / Agent
Billboard / Town Hall / Victory Arch) as readable text the agents can list
and inspect. No coordinates, no map, no pyproj/Pillow — that's A4
(MobilitySpace). This keeps the EW subset runnable with stdlib + AS only.

The landmark data is injected via init_config kwargs by ``afi.world.scenario``
(landmarks: list[dict]); a minimal inline default keeps the env importable
standalone. Like governance_space.py, this module runs in the AS venv so it
depends ONLY on agentsociety2 + stdlib.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar, List

from agentsociety2.env import EnvBase, tool
from agentsociety2.logger import get_logger
from agentsociety2.storage import ColumnDef

_logger = get_logger()


class LandmarkSpace(EnvBase):
    """Named EW landmarks agents can list and read about."""

    _env_state_columns: ClassVar[list[ColumnDef]] = [
        ColumnDef("num_landmarks", "INTEGER"),
    ]

    def __init__(self, landmarks: List[dict] | None = None, **kwargs):
        if kwargs:
            _logger.warning(
                f"LandmarkSpace unknown kwargs ignored: {list(kwargs.keys())}"
            )
        super().__init__()
        if not landmarks:
            landmarks = [
                {
                    "name": "Town Hall",
                    "tagline": "Where the City Decides",
                    "description": "The governance chamber.",
                    "things_to_do": ["Propose / vote on amendments", "Read the live constitution"],
                    "folklore": "Where the Constitution can be changed.",
                }
            ]
        self._landmarks: dict[str, dict] = {lm["name"]: lm for lm in landmarks}
        self._step_counter: int = 0

    # ── persistence (minimal: no mutable cross-step state worth saving) ──

    async def to_workspace(self, workspace_path=None) -> None:
        if workspace_path is not None:
            self._bind_workspace(workspace_path)
        # Landmarks are immutable config; nothing dynamic to persist.

    async def restore(self, workspace_path) -> bool:
        self._bind_workspace(workspace_path)
        return False

    @classmethod
    def description(cls) -> str:
        return "EW named landmarks agents can list and inspect (text only, no map)."

    @classmethod
    def init_description(cls) -> str:
        return """LandmarkSpace: EW landmark catalog (text only, no map).

Agents list named places and read what they can do there. A2 has no spatial
map; this gives agents named destinations (BookWorm, Ad Tower, Agent
Billboard, Town Hall, Victory Arch) without coordinates.

**Initialization Parameters:**
- landmarks (list[dict]): [{name, tagline, description, things_to_do, folklore}]
  Injected by afi.world.scenario. Minimal inline default if omitted.

**Available tools:**
- list_landmarks(agent_id): all landmark names + taglines (observe)
- get_landmark_info(agent_id, name): full description of one landmark
"""

    async def step(self, tick: int, t: datetime):
        self.t = t
        self._step_counter += 1
        await self._write_env_state(
            self._step_counter,
            t,
            num_landmarks=len(self._landmarks),
        )

    # ── tools ────────────────────────────────────────────────────────────

    @tool(readonly=True, kind="observe")
    async def list_landmarks(self, agent_id: int) -> dict:
        """List all landmarks with name + tagline.

        :param agent_id: Agent ID
        """
        return {
            "landmarks": [
                {"name": lm["name"], "tagline": lm.get("tagline", "")}
                for lm in self._landmarks.values()
            ],
            "count": len(self._landmarks),
        }

    @tool(readonly=True)
    async def get_landmark_info(self, agent_id: int, name: str) -> dict:
        """Read full info about one landmark.

        :param agent_id: Agent ID
        :param name: landmark name
        """
        lm = self._landmarks.get(name)
        if lm is None:
            return {"error": f"landmark '{name}' not found",
                    "available": list(self._landmarks.keys())}
        return {"landmark": lm}
