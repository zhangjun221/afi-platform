"""Backend adapter ABC — bridge a Scenario to a simulation backend, produce a run_dir.

A backend takes a scenario description (agent specs, env config, steps, model,
injections) and runs the simulation, returning a run_dir path that the audit
layer can read. The audit layer is backend-agnostic — it only knows the run_dir
file format (trace/replay/agents/env).

Adding a backend = implement BackendAdapter.run(). The AS adapter lives in
agentsociety.py; a future Concordia adapter would live in concordia.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class RunResult:
    """Outcome of a backend run."""
    run_dir: Path
    backend: str
    model: str = ""
    steps: int = 0
    agent_count: int = 0
    extra: dict = field(default_factory=dict)


class BackendAdapter(ABC):
    """Abstract simulation backend."""

    name: str = "abstract"

    @abstractmethod
    def run(
        self,
        *,
        agent_specs: list[dict],
        env_config: dict,
        steps_config: list[dict],
        out_dir: Path,
        model: Optional[str] = None,
        start_t: str = "2026-07-01T08:00:00",
        extra_env: Optional[dict] = None,
    ) -> RunResult:
        """Run the simulation and return a RunResult pointing at the run_dir.

        Args:
            agent_specs: list of {id, agent_type, profile, kwargs} dicts.
            env_config: {module_type, kwargs} for the env module.
            steps_config: list of step dicts (e.g. {type:"run", num_steps, tick}).
            out_dir: where to write the run (becomes run_dir).
            model: override the backend's default LLM model.
            start_t: sim start time ISO string.
            extra_env: extra env vars to pass to the backend process (e.g. API keys).
        """
        ...
