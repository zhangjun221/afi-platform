"""Backend adapters — bridge a Scenario to a simulation backend, produce a run_dir.

base.BackendAdapter is the ABC; agentsociety.AgentSocietyAdapter is the default
AS backend. Adding Concordia = add concordia.py implementing the same ABC.
"""
from afi.backend.base import BackendAdapter, RunResult

__all__ = ["BackendAdapter", "RunResult"]
