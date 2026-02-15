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
LOG_DIR="$SKILL_DIR/logs"
LOG_FILE="$LOG_DIR/ambient-$(date +%Y-%m-%d).log"

# Logging function with daily rotation (keep 7 days)
log() {
    mkdir -p "$LOG_DIR"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}
rotate_logs() {
    find "$LOG_DIR" -name "ambient-*.log" -mtime +7 -delete 2>/dev/null || true
}

# Run log rotation on each execution
rotate_logs

log "=== Ambient tick started ==="

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
  
  # Extract player names after the colon (handle multi-line output and leading hyphens)
  echo "$out" | tr '\n' ' ' | sed 's/  */ /g' | sed -n 's/Players connected ([0-9]*): //p' | tr ',' '\n' | while read -r name || [ -n "$name" ]; do
    name=$(echo "$name" | sed 's/^[[:space:]]*-*//;s/[[:space:]]*$//')
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
  
  # Build properly delimited string for parsing
  local current_str new_str left_str
  current_str="$(IFS=,; echo "${current_players[*]:-}")"
  new_str="$(IFS=,; echo "${new_players[*]:-}")"
  left_str="$(IFS=,; echo "${left_players[*]:-}")"
  
  python3 << PYEOF
import json

current = "${current_str}".split(",") if "${current_str}" else []
new = "${new_str}".split(",") if "${new_str}" else []
left = "${left_str}".split(",") if "${left_str}" else []

# Clean empty strings
current = [p for p in current if p]
new = [p for p in new if p]
left = [p for p in left if p]

data = {
  "previousOnline": list(set(current)),
  "lastCheckTs": ${now},
  "newPlayers": list(set(new)),
  "leftPlayers": list(set(left))
}
with open("/home/starbugmolt/.openclaw/workspace/skills/pz-rcon/state/player-delta.json", "w") as f:
  json.dump(data, f, indent=2)

# Print delta events - VERY CLEAR FORMAT
if new:
  print(f">>> JOIN:{','.join(new)}")
if left:
  print(f">>> LEAVE:{','.join(left)}")
if not new and not left:
  print(">>> NO_CHANGE")
PYEOF
  
  # Update registry
  init_registry
  update_registry "$now" "${current_players[@]:-}"
}

# ============================================================================
# MAIN
# ============================================================================

log "Fetching current players from RCON..."
# 1. Get current players
mapfile -t CURRENT_PLAYERS < <(get_online_players)
COUNT=${#CURRENT_PLAYERS[@]}

log "Players found: $COUNT (${CURRENT_PLAYERS[*]:-none})"
echo "Players found: $COUNT"

# 2. Handle empty server
if [ $COUNT -eq 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    echo "Players dropped to 0. Resetting narrative state."
    rm -f "$STATE_FILE"
  fi
  
  # Detect who LEFT before clearing
  python3 << 'PYEOF'
import json
import os

delta_file = "/home/starbugmolt/.openclaw/workspace/skills/pz-rcon/state/player-delta.json"
now = 0

try:
    with open(delta_file, "r") as f:
        prev_data = json.load(f)
    previous_online = prev_data.get("previousOnline", [])
    now = prev_data.get("lastCheckTs", 0)
except:
    previous_online = []

# Save with left players detected
data = {
    "previousOnline": [],
    "lastCheckTs": now,
    "newPlayers": [],
    "leftPlayers": list(set(previous_online))
}

with open(delta_file, "w") as f:
    json.dump(data, f, indent=2)

# Print delta if anyone left - VERY CLEAR FORMAT
if data["leftPlayers"]:
    print(f">>> LEAVE:{','.join(data['leftPlayers'])}")
else:
    print(">>> NO_CHANGE")
PYEOF
  
  echo "No players online. Director sleeping."
  exit 0
fi

# 3. Detect player changes
echo "Current players: ${CURRENT_PLAYERS[*]}"
log "Detecting player delta..."
DELTA_EVENT=$(detect_player_delta "${CURRENT_PLAYERS[@]}")
echo "Delta event: $DELTA_EVENT"
log "Delta event: $DELTA_EVENT"

# 4. AI Director now handles narrative via cron - no more static script
log "Player count: $COUNT. AI Director will generate radio chatter."
echo "AI Director handling narrative (cron-based)."
