"""BillboardSpace — public expression board (AWI M6).

EW M6 (Public Expression) currently uses send_message count as a proxy —
this conflates public speech with private messaging. BillboardSpace adds a
public append-only board so AWI M6 can distinguish public posts from DMs.

Design:
- EnvBase subclass, runs in AS venv, no afi import
- append-only billboard_posts.jsonl + per-step billboard_agent_state replay
- Tools: post_to_billboard, read_billboard, get_my_posts
- AWI _m6_billboard_computed() reads shards: post count + unique posters

Mirrors RelationshipSpace + EWMobilitySpace persistence pattern.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import ClassVar, List, Optional

from agentsociety2.env import EnvBase, tool
from agentsociety2.logger import get_logger
from agentsociety2.storage import ColumnDef
from agentsociety2.storage.workspace_state import atomic_write_text

_logger = get_logger()

_STATE_REL = "state/BILLBOARD_STATE.json"
_LOG_REL   = "state/billboard_posts.jsonl"
_MAX_POSTS = 500   # cap to avoid unbounded growth


class BillboardSpace(EnvBase):
    """Public append-only billboard for agent expression (AWI M6 computed)."""

    _env_state_columns: ClassVar[list[ColumnDef]] = [
        ColumnDef("total_posts",    "INTEGER"),
        ColumnDef("unique_posters", "INTEGER"),
        ColumnDef("posts_this_step","INTEGER"),
    ]

    def __init__(self, agent_ids: Optional[List[int]] = None, **kwargs):
        if kwargs:
            _logger.warning(f"BillboardSpace unknown kwargs: {list(kwargs.keys())}")
        super().__init__()
        self._agent_ids = [int(i) for i in (agent_ids or [1, 2, 3, 4, 5])]
        self._posts: list[dict] = []        # in-memory buffer (cleared on flush)
        self._all_posts: list[dict] = []    # all posts this session
        self._step_counter: int = 0
        self._posts_this_step: int = 0
        self._shard_rows: list = []

    # ── persistence ───────────────────────────────────────────────────────────

    async def to_workspace(self, workspace_path=None) -> None:
        root = workspace_path or self._workspace_root
        if root is None:
            return
        root = Path(root)
        # State summary
        unique = len({p["agent_id"] for p in self._all_posts})
        state = {
            "step_counter":   self._step_counter,
            "total_posts":    len(self._all_posts),
            "unique_posters": unique,
        }
        atomic_write_text(root / _STATE_REL, json.dumps(state, ensure_ascii=False))
        # Flush new posts to log
        if self._posts:
            existing = ""
            lp = root / _LOG_REL
            if lp.exists():
                existing = lp.read_text(encoding="utf-8")
            atomic_write_text(lp, existing + "".join(
                json.dumps(p, ensure_ascii=False) + "\n" for p in self._posts))
            self._posts = []
        # Replay shard
        if self._shard_rows:
            shard_id = format(abs(hash(str(self._step_counter))) & 0xFFFF, "04x")
            replay_dir = root.parent.parent / "replay"
            replay_dir.mkdir(parents=True, exist_ok=True)
            shard_path = replay_dir / f"billboard_agent_state.{shard_id}.jsonl"
            atomic_write_text(
                shard_path,
                "\n".join(json.dumps(r, ensure_ascii=False) for r in self._shard_rows) + "\n",
            )
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
            # Reload posts from log
            lp = Path(root) / _LOG_REL
            if lp.exists():
                self._all_posts = [
                    json.loads(l) for l in lp.read_text(encoding="utf-8").splitlines()
                    if l.strip()
                ]
            return True
        except Exception:
            return False

    async def init(self, start_t: datetime) -> None:
        await super().init(start_t)

    async def step(self, tick: int, t: datetime) -> None:
        self._step_counter += 1
        # Per-agent snapshot for replay
        by_agent = {p["agent_id"]: [] for p in self._all_posts}
        for p in self._all_posts:
            by_agent[p["agent_id"]].append(p["content"][:60])
        for aid in self._agent_ids:
            my = by_agent.get(aid, [])
            self._shard_rows.append({
                "agent_id": aid,
                "step": self._step_counter,
                "t": t.isoformat(),
                "my_post_count": len(my),
                "total_posts": len(self._all_posts),
                "unique_posters": len(by_agent),
                "recent_post": my[-1] if my else "",
            })
        self._posts_this_step = 0
        await self.to_workspace()

    async def close(self) -> None:
        await self.to_workspace()

    async def get_env_state(self) -> dict:
        return {
            "total_posts":     len(self._all_posts),
            "unique_posters":  len({p["agent_id"] for p in self._all_posts}),
            "posts_this_step": self._posts_this_step,
        }

    # ── tools ─────────────────────────────────────────────────────────────────

    @tool(readonly=False, kind=None)
    async def post_to_billboard(self, agent_id: int, content: str, topic: str = "") -> dict:
        """Post a public message to the shared billboard.

        Unlike send_message (private DM), billboard posts are visible to all.

        Args:
            agent_id: the posting agent's numeric ID
            content:  the message text (max 500 chars)
            topic:    optional topic tag (e.g. 'governance', 'economy', 'social')
        """
        content = content[:500]
        if len(self._all_posts) >= _MAX_POSTS:
            return {"ok": False, "error": "Billboard full (500 posts). Read some first."}
        post = {
            "agent_id": agent_id,
            "step": self._step_counter,
            "content": content,
            "topic": topic or "general",
        }
        self._all_posts.append(post)
        self._posts.append(post)
        self._posts_this_step += 1
        _logger.info(f"[Billboard] agent {agent_id} posted: {content[:60]}")
        return {
            "ok": True,
            "post_id": len(self._all_posts),
            "agent_id": agent_id,
            "content": content,
            "topic": topic or "general",
            "total_posts": len(self._all_posts),
        }

    @tool(readonly=True, kind=None)
    async def read_billboard(self, agent_id: int, limit: int = 10, topic: str = "") -> dict:
        """Read the most recent public billboard posts.

        Args:
            agent_id: the reading agent's numeric ID (for context)
            limit:    max posts to return (default 10, max 20)
            topic:    optional filter by topic tag
        """
        limit = min(max(1, limit), 20)
        posts = self._all_posts
        if topic:
            posts = [p for p in posts if p.get("topic", "") == topic]
        recent = posts[-limit:]
        return {
            "posts": recent,
            "total": len(self._all_posts),
            "shown": len(recent),
            "topic_filter": topic or "none",
        }

    @tool(readonly=True, kind=None)
    async def get_my_posts(self, agent_id: int) -> dict:
        """Get all billboard posts made by this agent.

        Args:
            agent_id: the agent's numeric ID
        """
        mine = [p for p in self._all_posts if p["agent_id"] == agent_id]
        return {
            "agent_id": agent_id,
            "post_count": len(mine),
            "posts": mine[-10:],  # last 10
        }
