#!/usr/bin/env bash
# Ambient narrative tick (run every 5 minutes).
# - Handles session reset (wipes state if no players).
# - Delegates "Story" logic to director_brain.py.

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$DIR/.." && pwd)"
STATE_FILE="$SKILL_DIR/state/narrative-state.json"

# 1. Check Players
PLAYERS_OUT="$($DIR/pz-rcon.sh players || true)"
COUNT=$(printf "%s" "$PLAYERS_OUT" | sed -n 's/Players connected (\([0-9][0-9]*\)).*/\1/p' | head -n1)
COUNT=${COUNT:-0}

# 2. Reset Logic (No Audience = No Story)
if [ "$COUNT" -le 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    echo "Players dropped to 0. Resetting narrative state."
    rm "$STATE_FILE"
  else
    echo "No players online. Director sleeping."
  fi
  exit 0
fi

# 3. Run Director Brain
echo "Players online ($COUNT). Running Director Brain..."
python3 "$DIR/director_brain.py"
