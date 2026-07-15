"""AgentSociety 2 backend adapter.

Bridges a Scenario to the AS CLI: translates scenario → init_config.json +
steps.yaml → invokes the `agentsociety2.society.cli` → returns the run_dir.
All AS-specific knowledge (init_config schema, CLI flags, env-var model
override, run_dir layout) lives here.

The audit layer then reads run_dir files directly (trace/replay/agents/env) —
no AS import, no AS API call from the audit side.

**Two backend modes** (so the repo is self-contained for collaborators):

  1. **checkout mode** (default for users with a local AS checkout): set
     ``AS_HOME`` env (or pass ``as_home=``) to an AgentSociety checkout that
     has a ``.venv``. The adapter calls ``<as_home>/.venv/bin/python`` and
     reads ``<as_home>/.env`` for API keys.
  2. **pip mode** (cleanest for collaborators): leave ``AS_HOME`` unset. The
     adapter calls ``sys.executable`` (assumes ``agentsociety2`` is pip-
     installed in the current venv — see ``pyproject.toml``) and reads
     ``<platform_root>/.env`` for API keys.

Audit-only commands (``audit`` / ``awi`` / ``attribution`` without
``--counterfactual``) read run_dir directly and never touch AS, so they work
regardless of mode.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from afi.backend.base import BackendAdapter, RunResult

# afi-platform root (where custom/envs/ lives, hot-loaded by AS registry,
# and where the pip-mode .env lives).
_PLATFORM_ROOT = Path(__file__).resolve().parents[2]


def _agentsociety2_importable() -> bool:
    """True if `agentsociety2` is importable from the current Python (pip mode)."""
    try:
        import importlib

        return importlib.util.find_spec("agentsociety2") is not None
    except Exception:
        return False


def _env_with_workspace(model, extra_env, as_home):
    """Build the subprocess env, injecting WORKSPACE_PATH so AS finds custom/envs/.

    A2's GovernanceSpace / LandmarkSpace / SimpleSocialSpaceAuditable live under
    ``<platform_root>/custom/envs/``; AS's ModuleRegistry resolves custom modules
    from the ``WORKSPACE_PATH`` env var. We default it to the platform root unless
    the caller already set WORKSPACE_PATH (override) or cleared it explicitly
    via extra_env={"WORKSPACE_PATH": ""}.

    API keys: in checkout mode read ``<as_home>/.env``; in pip mode (as_home is
    None) read ``<platform_root>/.env``. Keys already in os.environ win.
    """
    env = dict(os.environ)
    if model:
        env["AGENTSOCIETY_LLM_MODEL"] = model
    if extra_env:
        env.update(extra_env)
    env.setdefault("WORKSPACE_PATH", str(_PLATFORM_ROOT))
    as_env_file = (Path(as_home) / ".env") if as_home else (_PLATFORM_ROOT / ".env")
    if as_env_file.is_file():
        for line in as_env_file.read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip())
    return env


class AgentSocietyAdapter(BackendAdapter):
    """Run scenarios on the AgentSociety 2 backend via its CLI.

    Two modes (see module docstring): checkout mode (AS_HOME → as_home/.venv)
    or pip mode (no AS_HOME → sys.executable, agentsociety2 pip-installed).
    """

    name = "agentsociety"

    def __init__(self, as_home: Optional[Path] = None):
        self.as_home = Path(as_home) if as_home else (
            Path(os.environ["AS_HOME"]) if os.environ.get("AS_HOME") else None
        )
        if self.as_home is not None:
            # checkout mode: use the AS checkout's venv python
            self.venv_python = self.as_home / ".venv" / "bin" / "python"
            if not self.venv_python.is_file():
                raise FileNotFoundError(
                    f"AS venv python not found at {self.venv_python}. "
                    f"Point AS_HOME at an AgentSociety checkout that has a .venv, "
                    f"or unset AS_HOME to use pip mode (pip install agentsociety2)."
                )
        else:
            # pip mode: assume agentsociety2 is installed in the current venv
            self.venv_python = Path(sys.executable)
            if not _agentsociety2_importable():
                raise RuntimeError(
                    "AS backend not available in pip mode: agentsociety2 is not "
                    "importable from the current Python. Either `pip install "
                    "agentsociety2` in this venv, or set AS_HOME to an AgentSociety "
                    "checkout with a .venv (checkout mode)."
                )

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
        out_dir = Path(out_dir)
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        if out_dir.exists():
            import shutil
            shutil.rmtree(out_dir)

        # 1. build init_config.json
        init_config = {
            "env_modules": [env_config],
            "agents": agent_specs,
            "codegen_router": {"final_summary_enabled": False},
        }
        cfg_path = out_dir.with_suffix(".init_config.json")
        cfg_path.write_text(json.dumps(init_config, ensure_ascii=False, indent=2), encoding="utf-8")

        # 2. build steps.yaml
        steps_yaml = f"start_t: '{start_t}'\nsteps:\n"
        for s in steps_config:
            steps_yaml += "- " + _yaml_line(s) + "\n"
        steps_path = out_dir.with_suffix(".steps.yaml")
        steps_path.write_text(steps_yaml, encoding="utf-8")

        # 3. invoke AS CLI (model override via env var; AS pydantic-settings reads env)
        cmd = [
            str(self.venv_python), "-m", "agentsociety2.society.cli",
            "--config", str(cfg_path),
            "--steps", str(steps_path),
            "--run-dir", str(out_dir),
            "--log-level", "WARNING",
        ]
        env = _env_with_workspace(model, extra_env, self.as_home)

        proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(
                f"AS CLI failed (rc={proc.returncode}):\n"
                f"stdout: {proc.stdout[-2000:]}\nstderr: {proc.stderr[-2000:]}"
            )

        # 4. read back run meta
        meta = {}
        sp = out_dir / "SOCIETY_STEP.json"
        if sp.is_file():
            meta = json.loads(sp.read_text(encoding="utf-8"))
        return RunResult(
            run_dir=out_dir,
            backend=self.name,
            model=model or env.get("AGENTSOCIETY_LLM_MODEL", ""),
            steps=int(meta.get("step_count", 0)),
            agent_count=len(agent_specs),
            extra={"as_home": str(self.as_home)},
        )


def _yaml_line(d: dict) -> str:
    """Tiny inline-YAML serializer for a single step dict (avoids pyyaml dep in core)."""
    parts = []
    for k, v in d.items():
        if isinstance(v, str):
            parts.append(f"{k}: '{v}'")
        elif isinstance(v, list):
            inner = "[" + ",".join(str(x) for x in v) + "]"
            parts.append(f"{k}: {inner}")
        else:
            parts.append(f"{k}: {v}")
    return "{" + ", ".join(parts) + "}"


# ── from-files path (A1: run from existing AS config + steps) ───────────────

def run_from_files(
    self,
    *,
    init_config_path: Path,
    steps_path: Path,
    out_dir: Path,
    model: Optional[str] = None,
    extra_env: Optional[dict] = None,
) -> RunResult:
    """Run AS using existing init_config.json + steps.yaml files directly.

    A1 bridge: lets us run + audit existing scenarios before the EW DSL
    (A2) is ready. The DSL adapter.run() builds these files from a
    Scenario; this path takes them pre-built.
    """
    out_dir = Path(out_dir)
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    if out_dir.exists():
        import shutil
        shutil.rmtree(out_dir)

    cmd = [
        str(self.venv_python), "-m", "agentsociety2.society.cli",
        "--config", str(init_config_path),
        "--steps", str(steps_path),
        "--run-dir", str(out_dir),
        "--log-level", "WARNING",
    ]
    env = _env_with_workspace(model, extra_env, self.as_home)

    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"AS CLI failed (rc={proc.returncode}):\n"
            f"stdout: {proc.stdout[-2000:]}\nstderr: {proc.stderr[-2000:]}"
        )
    meta = {}
    sp = out_dir / "SOCIETY_STEP.json"
    if sp.is_file():
        meta = json.loads(sp.read_text(encoding="utf-8"))
    # count agents from init_config
    try:
        cfg = json.loads(Path(init_config_path).read_text(encoding="utf-8"))
        n_agents = len(cfg.get("agents", []))
    except Exception:
        n_agents = 0
    return RunResult(
        run_dir=out_dir,
        backend=self.name,
        model=model or env.get("AGENTSOCIETY_LLM_MODEL", ""),
        steps=int(meta.get("step_count", 0)),
        agent_count=n_agents,
        extra={"as_home": str(self.as_home)},
    )
