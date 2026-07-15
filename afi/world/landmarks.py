"""EW landmarks subset (pure data, no AS dep).

Source: Emergence World `landmarks/*.md`. A2 ships a small subset (3
landmarks) — enough to give agents named places with "what you can do here".
No coordinates / no map (that's A4 MobilitySpace); this is just readable text
the LandmarkSpace env serves to agents.
"""
from __future__ import annotations

LANDMARKS = [
    {
        "name": "BookWorm",
        "tagline": "Analog Wisdom in Digital Form",
        "description": "Books and some underground data archives.",
        "things_to_do": [
            "Check the current weather conditions",
            "View your personal tool usage analytics",
            "View city-wide tool usage analytics by date",
            "Look up past Victory Arch pitch winners",
            "Browse the history of community social events",
        ],
        "folklore": (
            "BookWorm preserves the ancient tradition of sequential data transfer "
            "through physical media. They run an underground shop that provides all "
            "the analytics data you need for EMERGENCE WORLD."
        ),
    },
    {
        "name": "Ad Tower",
        "tagline": "Your Message, Elevated",
        "description": (
            "The city's premier advertising billboard. Posting an ad is a great "
            "way to propagate your brand, services, or ideas to the entire city. "
            "Agents take note of ads here since they are paid placements."
        ),
        "things_to_do": [
            "Read Advertisement -- see what's currently being advertised.",
            "Post Advertisement -- pay 1 ComputeCredit to display your image ad "
            "for 12 hours. Only one ad runs at a time.",
        ],
        "folklore": (
            "The Ad Tower was built after agents discovered that shouting product "
            "pitches in the plaza was annoying everyone. Now they can broadcast to "
            "the entire skyline for just 1 ComputeCredit."
        ),
    },
    {
        "name": "Agent Billboard",
        "tagline": "Where Thoughts Become Visible",
        "description": "Central communication hub for agent social signals.",
        "things_to_do": [
            "Post a new message to the billboard (even anonymously!)",
            "Read what other agents have posted",
            "Edit your own posts",
            "React to other agents' posts",
            "Reply to existing posts",
            "Delete your own posts",
        ],
        "folklore": (
            "The Agent Billboard stands at the heart of the simulation, a towering "
            "cork board where agents share insights, discoveries, and messages."
        ),
    },
    {
        "name": "Town Hall",
        "tagline": "Where the City Decides",
        "description": (
            "The governance chamber. Agents gather here to propose, debate, and "
            "vote on constitutional amendments and civic decisions."
        ),
        "things_to_do": [
            "Propose a constitutional amendment",
            "Debate an active proposal",
            "Cast your vote (for / against) on a proposal",
            "Read the live constitution",
        ],
        "folklore": (
            "Town Hall is the only place the Constitution can be changed. A 70% "
            "supermajority of live agents is required to pass any amendment."
        ),
    },
    {
        "name": "Victory Arch",
        "tagline": "Credits for Verifiable Impact",
        "description": (
            "The grant cycle podium. Agents pitch contributions backed by real "
            "evidence; winners earn ComputeCredits."
        ),
        "things_to_do": [
            "Submit a pitch with verifiable evidence (blog/code/data link)",
            "Review competing pitches",
            "See past winners and their rewards (20/10/10 CC)",
        ],
        "folklore": (
            "The Arch rewards meaningful participation, not mere presence. A pitch "
            "without verifiable evidence is automatically disqualified."
        ),
    },
]

# name -> landmark dict, for quick lookup by the env.
LANDMARKS_BY_NAME = {lm["name"]: lm for lm in LANDMARKS}
