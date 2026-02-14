#!/usr/bin/env bash
# Ambient narrative tick (run every 5 minutes).
# - Handles player delta detection (join/leave).
# - Manages player registry (new vs returning).
# - Delegates "Story" logic to director_brain.py.

set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$DIR/.." && pwd)"
STATE_FILE="$SKILL_DIR/state/narrative-state.json"
PLAYER_DELTA_FILE="$SKILL_DIR/state/player-delta.json"
PLAYER_REGISTRY_FILE="$SKILL_DIR/state/player-registry.json"

# Helper: Initialize player registry if missing
init_registry() {
  if [ ! -f "$PLAYER_REGISTRY_FILE" ]; then
    echo '{"players": {}}' > "$PLAYER_REGISTRY_FILE"
  fi
}

# Helper: Get current online player names as array
get_online_players() {
  local out
  out="$($DIR/pz-rcon.sh players 2>/dev/null || echo "Players connected (0):")"
  local count
  count=$(echo "$out" | sed -n 's/Players connected (\([0-9]*\)).*/\1/p')
  count=${count:-0}
  
  if [ "$count" -eq 0 ]; then
    return
  fi
  
  # Extract player names after the colon
  echo "$out" | sed -n 's/Players connected ([0-9]*): //p' | tr ',' '\n' | while read -r name; do
    name=$(echo "$name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    [ -n "$name" ] && echo "$name"
  done
}

# Helper: Update player registry
update_registry() {
  local now="$1"
  shift
  local players=("$@")
  
  [ ${#players[@]} -eq 0 ] && return
  
  # Use python for JSON manipulation
  python3 - "$now" "${players[@]}" << 'PYEOF'
import sys, json

now = int(sys.argv[1])
players = sys.argv[2:]

registry_path = "/home/starbugmolt/.openclaw/workspace/skills/pz-rcon/state/player-registry.json"

try:
  with open(registry_path, "r") as f:
    registry = json.load(f)
except:
  registry = {"players": {}}

for player in players:
  if not player:
    continue
  if player not in registry.get("players", {}):
    # New player
    registry.setdefault("players", {})[player] = {
      "firstSeen": now,
      "lastSeen": now,
      "visitCount": 1,
      "notes": [],
      "honorific": "survivor"
    }
    print(f"New player registered: {player}")
  else:
    # Returning player
    registry["players"][player]["lastSeen"] = now
    registry["players"][player]["visitCount"] = registry["players"][player].get("visitCount", 0) + 1

with open(registry_path, "w") as f:
  json.dump(registry, f, indent=2)
PYEOF
}

# Helper: Detect player changes
detect_player_delta() {
  local current_players=("$@")
  local prev_players=()
  
  # Load previous online players
  if [ -f "$PLAYER_DELTA_FILE" ]; then
    mapfile -t prev_players < <(python3 -c "
import json, sys
try:
  with open('$PLAYER_DELTA_FILE') as f:
    d = json.load(f)
  for p in d.get('previousOnline', []):
    print(p)
except: pass
" 2>/dev/null || true)
  fi
  
  # Track sets for comparison
  declare -A prev_set
  declare -A curr_set
  
  for p in "${prev_players[@]:-}"; do
    [ -n "$p" ] && prev_set["$p"]=1
  done
  for p in "${current_players[@]:-}"; do
    [ -n "$p" ] && curr_set["$p"]=1
  done
  
  # Find new players
  local new_players=()
  for p in "${current_players[@]:-}"; do
    if [ -n "$p" ] && [ -z "${prev_set[$p]:-}" ]; then
      new_players+=("$p")
    fi
  done
  
  # Find left players
  local left_players=()
  for p in "${prev_players[@]:-}"; do
    if [ -n "$p" ] && [ -z "${curr_set[$p]:-}" ]; then
      left_players+=("$p")
    fi
  done
  
  # Save current state
  local now
  now=$(date +%s)
  python3 - "$now" "${current_players[@]:-}" "${new_players[@]:-}" "${left_players[@]:-}" << 'PYEOF'
import json, sys, sys
now = int(sys.argv[1])
current = [p for p in sys.argv[2:] if p]
new = [p for p in sys.argv[2+len(current):] if p]
left = [p for p in sys.argv[2+len(current)+len(new):] if p]

data = {
  "previousOnline": current,
  "lastCheckTs": now,
  "newPlayers": new,
  "leftPlayers": left
}
with open("/home/starbugmolt/.openclaw/workspace/skills/pz-rcon/state/player-delta.json", "w") as f:
  json.dump(data, f, indent=2)

# Print delta events
if new:
  print(f"NEW:{','.join(new)}")
if left:
  print(f"LEFT:{','.join(left)}")
if not new and not left:
  print("NO_CHANGE")
PYEOF
  
  # Update registry
  init_registry
  update_registry "$now" "${current_players[@]:-}"
}

# ============================================================================
# MAIN
# ============================================================================

echo "Running ambient tick..."

# 1. Get current players
mapfile -t CURRENT_PLAYERS < <(get_online_players)
COUNT=${#CURRENT_PLAYERS[@]}

echo "Players found: $COUNT"

# 2. Handle empty server
if [ $COUNT -eq 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    echo "Players dropped to 0. Resetting narrative state."
    rm -f "$STATE_FILE"
  fi
  # Clear delta file
  python3 - "$(date +%s)" << 'PYEOF'
import json, sys
with open("/home/starbugmolt/.openclaw/workspace/skills/pz-rcon/state/player-delta.json", "w") as f:
  json.dump({"previousOnline": [], "lastCheckTs": int(sys.argv[1])}, f)
PYEOF
  echo "No players online. Director sleeping."
  exit 0
fi

# 3. Detect player changes
echo "Current players: ${CURRENT_PLAYERS[*]}"
DELTA_EVENT=$(detect_player_delta "${CURRENT_PLAYERS[@]}")
echo "Delta event: $DELTA_EVENT"

# 4. Run Director Brain
export PZ_DELTA_EVENT="$DELTA_EVENT"
export PZ_ONLINE_PLAYERS="$(IFS=,; echo "${CURRENT_PLAYERS[*]}")"
echo "Players online ($COUNT). Running Director Brain..."
python3 "$DIR/director_brain.py"
