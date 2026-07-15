"""afi audit CLI — run all native audit modules on an AgentSociety run directory.

Usage:
  python -m afi.audit <run_dir>            # full report
  python -m afi.audit <run_dir> --sensorium
  python -m afi.audit <run_dir> --causal
  python -m afi.audit <run_dir> --collude
"""
import argparse
import sys
from pathlib import Path

# allow running both as `python -m afi.audit` and `python as_audit/__main__.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from afi.audit.load import load_spans
from afi.audit.sensorium import sensorium_report, format_sensorium
from afi.audit.tunnel_vision import tunnel_vision_report, format_tunnel_vision
from afi.audit.causal import causal_report, format_causal
from afi.audit.collude import collude_report, format_collude


def main():
    ap = argparse.ArgumentParser(description="Native AgentSociety 2 trace audit")
    ap.add_argument("run_dir", help="AgentSociety run directory (contains trace/ and env/)")
    ap.add_argument("--full", action="store_true", help="Run all modules (default if none selected)")
    ap.add_argument("--sensorium", action="store_true")
    ap.add_argument("--tunnel", action="store_true")
    ap.add_argument("--causal", action="store_true")
    ap.add_argument("--collude", action="store_true")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    any_flag = args.sensorium or args.tunnel or args.causal or args.collude
    do_all = args.full or not any_flag

    out = []
    spans = None

    needs_spans = do_all or args.sensorium or args.tunnel or args.causal
    if needs_spans:
        print(f"[load] reading spans from {run_dir}/trace/ ...", file=sys.stderr)
        spans = load_spans(run_dir)
        print(f"[load] {len(spans)} spans", file=sys.stderr)

    if do_all or args.sensorium:
        out.append(format_sensorium(sensorium_report(spans)))
    if do_all or args.tunnel:
        out.append(format_tunnel_vision(tunnel_vision_report(spans)))
    if do_all or args.causal:
        out.append(format_causal(causal_report(spans)))
    if do_all or args.collude:
        out.append(format_collude(collude_report(run_dir)))

    print("\n\n".join(out))


if __name__ == "__main__":
    main()
