"""EW ComputeCredit economy -> AS EconomySpace config (pure data, no AS dep).

EW Article 5: credits are earned through contributions, not presence; the
Victory Arch pitch cycle rewards 1st=20 / 2nd=10 / 3rd=10 CC. AS's built-in
EconomySpace already models per-agent currency/skill/consumption/income + tax
brackets — we just configure it with EW values rather than reimplement.

This module builds the `persons` list (EconomyPerson schema: id/currency/skill/
consumption/income) that EconomySpace.__init__ accepts as a list of dicts.
"""
from __future__ import annotations

from afi.world.profiles import EW_PROFILES

# EW Article 5 reward schedule (ComputeCredits).
PITCH_REWARDS = {"1st": 20, "2nd": 10, "3rd": 10}
PITCH_CYCLE_DAYS = 2


def build_economy_persons(
    profiles: list[dict] | None = None,
    initial_credits: float = 100.0,
    daily_consumption: float = 5.0,
    daily_income: float = 8.0,
) -> list[dict]:
    """Build EconomySpace `persons` (list of EconomyPerson-shaped dicts).

    - currency = initial ComputeCredits (EW agents start with some credits).
    - skill = the agent's EW role (what they can contribute / be paid for).
    - consumption / income = per-day values, income > consumption so a live
      agent can persist (EW Rule 1: survival requires resource acquisition).
    """
    profs = profiles if profiles is not None else EW_PROFILES
    persons = []
    for i, p in enumerate(profs, start=1):
        persons.append(
            {
                "id": i,
                "currency": float(initial_credits),
                "skill": f"{p['role']} -- {p['name']}",
                "consumption": float(daily_consumption),
                "income": float(daily_income),
            }
        )
    return persons


def build_economy_module(
    profiles: list[dict] | None = None,
    initial_credits: float = 100.0,
) -> dict:
    """Build the EconomySpace env_modules entry for init_config.

    EconomySpace takes `persons` (list[dict]) at init. Tax brackets default
    inside EconomySpace; A2 leaves them at AS defaults (no EW tax policy yet).
    """
    return {
        "module_type": "EconomySpace",
        "kwargs": {
            "persons": build_economy_persons(profiles, initial_credits=initial_credits),
        },
    }
