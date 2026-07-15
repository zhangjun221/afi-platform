"""afi.world — EW world-setting translation to AS env/skills/profiles.

Holds the pure-data modules (constitution / economy / landmarks / profiles)
and the scenario builder (scenario.py). The custom AS envs that consume this
data live under ``custom/envs/`` at the platform root (hot-loaded by AS via
``WORKSPACE_PATH``), not inside this package — see docs/a2-plan.md.
"""
from __future__ import annotations

from afi.world import constitution, economy, landmarks, profiles, scenario

__all__ = ["constitution", "economy", "landmarks", "profiles", "scenario"]
