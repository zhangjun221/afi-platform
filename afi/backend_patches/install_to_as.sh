#!/usr/bin/env bash
# Install the auditable SimpleSocialSpace patch (durable message_log) into an
# AgentSociety install. Reinstalls of AS will overwrite this — re-run after.
#
# Usage: ./install_to_as.sh /path/to/AgentSociety
set -euo pipefail

AS_HOME="${1:-${AS_HOME:-}}"
if [[ -z "$AS_HOME" ]]; then
  echo "Usage: $0 /path/to/AgentSociety (or set AS_HOME)" >&2
  exit 1
fi

# locate the installed simple_social_space.py in the AS venv
SRC="$(cd "$(dirname "$0")" && pwd)/simple_social_space_patched.py"
DEST=$(find "$AS_HOME/.venv" -path "*/agentsociety2/contrib/env/simple_social_space.py" -print -quit 2>/dev/null || true)

if [[ -z "$DEST" ]]; then
  echo "ERROR: could not find simple_social_space.py under $AS_HOME/.venv" >&2
  echo "Is AS installed there? (pip install agentsociety2 in $AS_HOME/.venv)" >&2
  exit 1
fi

echo "patching: $DEST"
cp "$SRC" "$DEST"
echo "done. 5 [research patch] blocks applied (message_log durability)."
echo "reinstall AS → re-run this script."
