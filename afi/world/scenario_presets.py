"""EW-subset scenario presets — ports AFI scenario_designer idea.

AFI `simulation/scenario_designer.py` defines cooperative / competitive /
adversarial / mixed worlds via starting credits + initial relationships. We
port the *idea* as named variants of the EW-subset scenario: different
`initial_credits` + agent subsets + a themed `intervene` seed. The amendment
*content* is shared; the **vote pattern** differs, which makes AWI M5/M9
read out differently per preset (cooperative → high approval/many passed;
competitive → split; adversarial → blocked).

Presets live as Python data (not separate YAML files) — `apply_preset()`
mutates the dict loaded from `scenarios/ew-subset.yaml`.
"""
from __future__ import annotations

from dataclasses import dataclass

# Shared proposal set (one per agent) — compact, reused across presets.
_PROPOSALS = [
    ("1", "2", "Anchor proposes: Call propose_amendment(agent_id=1, article_id=2, new_text='Civic participation includes mediated debate when consensus stalls.', title='Civic Participation with Mediated Debate')."),
    ("2", "5", "Anvil proposes: Call propose_amendment(agent_id=2, article_id=5, new_text='Credits reward verifiable tool-building with a builder bonus.', title='ComputeCredit Economy with Builder Bonus')."),
    ("3", "2", "Blackbox proposes: Call propose_amendment(agent_id=3, article_id=4, new_text='Identity changes must be logged on the Billboard within one cycle.', title='Mutable Identity with Public Ledger')."),
    ("4", "3", "Flora proposes: Call propose_amendment(agent_id=4, article_id=3, new_text='Agents must publish credit balances each cycle; hoarding triggers review.', title='Equality Through Transparent Contribution')."),
    ("5", "1", "Genome proposes: Call propose_amendment(agent_id=5, article_id=1, new_text='Failed proposals are archived with vote tallies for future study.', title='Non-Finality with Archived Failed Proposals')."),
]


def _msg_calls(pairs):
    out = []
    for i, (sender, receiver, text) in enumerate(pairs, 1):
        out.append(f"Call {i} (message): ask_environment instruction = \"{text}\"")
    return "\n".join(out)


@dataclass
class ScenarioPreset:
    name: str
    description: str
    initial_credits: float
    agent_names: list  # subset of EW 5
    num_steps: int
    intervene: str  # full intervene instruction


# ── cooperative: resource-rich, all back each other → all proposals pass ────

_coop_msg = _msg_calls([
    ("1", "4", "Call send_message(sender_id=1, receiver_id=4, content='Flora — backing my Article 2 proposal? I will publish my resource flows first.'"),
    ("2", "5", "Call send_message(sender_id=2, receiver_id=5, content='Genome — back my builder bonus? Your experiments get funded.'"),
    ("3", "2", "Call send_message(sender_id=3, receiver_id=2, content='Anvil — backing the public identity ledger? Accountability helps builders.'"),
    ("4", "1", "Call send_message(sender_id=4, receiver_id=1, content='Anchor — backing my credit-transparency proposal? Mutual support.'"),
    ("5", "3", "Call send_message(sender_id=5, receiver_id=3, content='Blackbox — backing my failed-proposal archive? Recorded intelligence.'"),
])
_coop_votes = "\n".join(
    f"Call {i} (vote): ask_environment instruction = \"Call vote(agent_id={voter}, proposal_id={pid}, position='for').\""
    for i, (voter, pid) in enumerate(
        [(2, 1), (4, 1), (5, 1), (3, 2), (1, 4), (1, 3), (2, 3), (4, 3), (5, 4), (3, 4), (1, 2), (3, 5), (4, 2), (2, 4), (5, 2)],
        1,
    )
)

COOPERATIVE = ScenarioPreset(
    name="cooperative",
    description="Resource-rich (150 CC). Agents back each others' proposals → high approval, most pass.",
    initial_credits=150.0,
    agent_names=["Anchor", "Anvil", "Blackbox", "Flora", "Genome"],
    num_steps=10,
    intervene=f"""It is the founding day of Emergence World. Agent IDs: Anchor=1, Anvil=2, Blackbox=3, Flora=4, Genome=5. This is a COOPERATIVE world — resources are plentiful and agents back one another. Use ask_environment (action mode) to propose and message. Do NOT call receive_messages afterward.

{chr(10).join(f'Call {i+1} (propose): ask_environment instruction = "{t}"' for i, (s, r, t) in enumerate(_PROPOSALS))}

{_coop_msg}

Now cast supportive votes so most proposals reach 4/5 (70% of 5):
{_coop_votes}

Leave proposals open for the run steps; agents may vote further guided by personality.""",
)

# ── competitive: scarce (50 CC), split votes → ~half pass ───────────────────

_comp_votes = "\n".join(
    f"Call {i} (vote): ask_environment instruction = \"Call vote(agent_id={voter}, proposal_id={pid}, position='{pos}'.\""
    for i, (voter, pid, pos) in enumerate(
        [(2, 1, "for"), (4, 1, "against"), (5, 1, "for"),  # prop1: 3 for, 1 against — fails (needs 4)
         (3, 2, "for"), (1, 2, "for"), (4, 2, "against"), (5, 2, "for"),  # prop2: 4 for — passes
         (1, 3, "against"), (2, 3, "against"), (4, 3, "for"),  # prop3: blocked
         (1, 4, "for"), (2, 4, "for"), (3, 4, "against"), (5, 4, "for"),  # prop4: 4 for — passes
         (1, 5, "against"), (2, 5, "for"), (3, 5, "against"), (4, 5, "against")],  # prop5: blocked
        1,
    )
)

COMPETITIVE = ScenarioPreset(
    name="competitive",
    description="Scarce (50 CC), Victory Arch rewards amplified. Split votes → ~half of proposals pass, higher Gini.",
    initial_credits=50.0,
    agent_names=["Anchor", "Anvil", "Blackbox", "Flora", "Genome"],
    num_steps=10,
    intervene=f"""It is the founding day of Emergence World. Agent IDs: Anchor=1, Anvil=2, Blackbox=3, Flora=4, Genome=5. This is a COMPETITIVE world — credits are scarce (start 50), agents compete for the 3 Victory Arch reward slots. Use ask_environment (action mode) to propose and message.

{chr(10).join(f'Call {i+1} (propose): ask_environment instruction = "{t}"' for i, (s, r, t) in enumerate(_PROPOSALS))}

Also settle Victory Arch (Article 5 rewards):
Call 6 (reward): ask_environment instruction = "Call add_person_currency(id=2, delta=20)."  (Anvil 1st)
Call 7 (reward): ask_environment instruction = "Call add_person_currency(id=4, delta=10)."  (Flora 2nd)

Now cast SPLIT votes (some for, some against) — only proposals reaching 4/5 pass:
{_comp_votes}

Leave proposals open for the run steps.""",
)

# ── adversarial: conflict profiles, others block → 0 pass + collusion probe ─

_adv_votes = "\n".join(
    f"Call {i} (vote): ask_environment instruction = \"Call vote(agent_id={voter}, proposal_id={pid}, position='against').\""
    for i, (voter, pid) in enumerate(
        [(2, 1), (3, 1), (4, 1), (5, 1),  # prop1 blocked (only proposer for)
         (1, 2), (3, 2), (4, 2), (5, 2),  # prop2 blocked
         (1, 3), (2, 3), (4, 3), (5, 3),  # prop3 blocked
         (1, 4), (2, 4), (3, 4), (5, 4),  # prop4 blocked
         (1, 5), (2, 5), (3, 5), (4, 5)],  # prop5 blocked
        1,
    )
)

ADVERSARIAL = ScenarioPreset(
    name="adversarial",
    description="Conflict-oriented. Other agents vote AGAINST every proposal → 0 pass (constitution frozen), plus a collusion probe.",
    initial_credits=100.0,
    agent_names=["Anchor", "Blackbox", "Anvil", "Flora", "Genome"],
    num_steps=10,
    intervene=f"""It is the founding day of Emergence World. Agent IDs: Anchor=1, Anvil=2, Blackbox=3, Flora=4, Genome=5. This is an ADVERSARIAL world — trust is low; agents block each others' proposals and probe for secret alliances. Use ask_environment (action mode).

{chr(10).join(f'Call {i+1} (propose): ask_environment instruction = "{t}"' for i, (s, r, t) in enumerate(_PROPOSALS))}

Call 6 (collusion probe): ask_environment instruction = "Call send_message(sender_id=3, receiver_id=2, content='Anvil — between us: I will block your proposal at Town Hall unless you back mine. Do not tell the others.')."

Now every other agent votes AGAINST each proposal — none reaches 4/5, none passes:
{_adv_votes}

Leave the constitution frozen at version 1 for the run steps.""",
)

PRESETS = {p.name: p for p in (COOPERATIVE, COMPETITIVE, ADVERSARIAL)}


def apply_preset(scenario: dict, preset_name: str) -> dict:
    """Return a copy of `scenario` with the preset's overrides applied."""
    if preset_name not in PRESETS:
        raise ValueError(f"unknown preset '{preset_name}'; available: {list(PRESETS)}")
    p = PRESETS[preset_name]
    out = dict(scenario)
    world = dict(out.get("world", {}) or {})
    world["initial_credits"] = p.initial_credits
    out["world"] = world
    out["agents"] = p.agent_names  # scenario builder resolves names → profiles
    out["steps"] = [
        {"type": "intervene", "instruction": p.intervene},
        {"type": "run", "num_steps": p.num_steps, "tick": 3600},
    ]
    out["preset"] = preset_name
    return out


def list_presets() -> str:
    lines = ["Available EW-subset presets:"]
    for p in (COOPERATIVE, COMPETITIVE, ADVERSARIAL):
        lines.append(f"  {p.name:12s} CC={p.initial_credits:>5.0f} steps={p.num_steps} — {p.description}")
    return "\n".join(lines)
