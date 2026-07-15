"""afi-platform — AFI-style social simulation + integrated audit on AgentSociety.

Built on AS (pip dep), reproduces Emergence World world-setting, ports
ai-freedom-island audit. See docs/architecture-and-roadmap.md.

Subpackages:
  audit           — audit modules reading AS run_dir (stdlib-only core)
  backend         — AS adapter (scenario → AS config → CLI → run_dir)
  backend_patches — AS-side custom env (message_log durability)
  world           — EW world-setting translation → AS env/skills/profiles [A2]
"""
__version__ = "0.1.0"
