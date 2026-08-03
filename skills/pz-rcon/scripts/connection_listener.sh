#!/usr/bin/env bash
# connection_listener.sh — Fast player-connection detector for PZ server.
#
# Runs as a command cron (no LLM). Sub-second typical runtime.
# Detects new players connecting to the PZ server and fires a SIMON
# in-character greeting via RCON servermsg within the configured target
# (default: 10 seconds).
#
# State files (read/write):
#   state/player-delta.json   — previous online list + last check ts
#   state/last_greet.txt      — "<player_name>|<unix_ts>" for 5-min dedupe
#
# Output:
#   NO_REPLY if nothing happened (suppressed by cron's silent-token handling)
#   Plain text "Greeted <player> at <ts>" if a greeting was fired
#   Plain text "<player> already greeted <Ns> ago" if dedupe skipped
#   Plain text "PlayerDelta: <new_players>" for debug
#
# Exit code: always 0 unless pz-rcon.sh fails.

set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$DIR/.." && pwd)"
STATE_DIR="$SKILL_DIR/state"
DELTA_FILE="$STATE_DIR/player-delta.json"
GREET_FILE="$STATE_DIR/last_greet.txt"
RCON="$DIR/pz-rcon.sh"

# Greet dedupe window (seconds) — default 300 = 5 min
DEDUPE_SECONDS="${GREET_DEDUPE_SECONDS:-300}"

# Greeting template (one line; will be chunked by pz-rcon.sh if needed)
DEFAULT_GREETING_TEMPLATE="${SIMON_GREET_TEMPLATE:-%P%, you\\'re on the wire. Frequency\\'s live. Simon, out.}"

# Tier-based greetings (used if director_brain.py is importable)
TIER_NEW_GREETINGS=(
    "New arrival detected. Welcome to the apocalypse, %P%."
    "Unregistered signal... %P%? Welcome to Muldraugh. Good luck."
    "First time in sector, %P%? The zombies are hungry."
)
TIER_RETURNING_GREETINGS=(
    "%P%! Back for more? The horde missed you. Probably."
    "Welcome back, %P%. Status: Still alive. That's something."
    "%P% returns. Let's hope you last longer this time."
)
TIER_VETERAN_GREETINGS=(
    "Veteran survivor %P% checking in. The undead await."
    "%P%, your survival instincts are noted. Good hunting."
    "Welcome back, %P%. Another day in paradise."
)

# Ensure state files exist
[ -f "$DELTA_FILE" ] || echo '{"previousOnline":[],"lastCheckTs":0,"newPlayers":[],"leftPlayers":[]}' > "$DELTA_FILE"
[ -f "$GREET_FILE" ] || echo "" > "$GREET_FILE"

# Get current online players
CURRENT=$("$RCON" players 2>/dev/null | grep '^-' | sed 's/^-[[:space:]]*//' | sort -u)
if [ -z "$CURRENT" ]; then
    CURRENT_LINE=""
else
    CURRENT_LINE="$CURRENT"
fi

# Get previous online players
PREVIOUS=$(python3 - "$DELTA_FILE" <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print('\n'.join(d.get('previousOnline', [])))
except Exception:
    print('')
PYEOF
)

# Diff: new = in current but not in previous
NEW=$(comm -23 <(echo "$CURRENT_LINE") <(echo "$PREVIOUS"))
LEFT=$(comm -13 <(echo "$CURRENT_LINE") <(echo "$PREVIOUS"))

# Update state file
python3 - "$DELTA_FILE" "$CURRENT_LINE" "$NEW" "$LEFT" <<'PYEOF'
import json, sys, time
path, current, new, left = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
d = json.load(open(path))
d['previousOnline'] = [p for p in current.split('\n') if p] if current else []
d['lastCheckTs'] = int(time.time())
d['newPlayers'] = [p for p in new.split('\n') if p] if new else []
d['leftPlayers'] = [p for p in left.split('\n') if p] if left else []
json.dump(d, open(path, 'w'), indent=2)
PYEOF

# If no new players, silent no-op
if [ -z "$NEW" ]; then
    echo "NO_REPLY"
    exit 0
fi

# Check dedupe file — last player greeted
LAST_GREET=$(cat "$GREET_FILE" 2>/dev/null || echo "")
NOW=$(date +%s)

# Try to use director_brain.py for tiered greetings
TIER_PICK=""
PICK_GREETING() {
    local player="$1"
    local info=""
    info=$(cd "$SKILL_DIR" && python3 -c "
import sys
sys.path.insert(0, 'scripts')
try:
    from director_brain import generate_player_greeting
    print(generate_player_greeting('$player'))
except Exception as e:
    sys.exit(1)
" 2>/dev/null) && TIER_PICK="$info" && return 0
    return 1
}

# Process each new player
GREETED=0
SKIPPED=0
while IFS= read -r player; do
    [ -z "$player" ] && continue

    # Dedupe: same player greeted within window?
    if [ -n "$LAST_GREET" ]; then
        last_player="${LAST_GREET%%|*}"
        last_ts="${LAST_GREET##*|}"
        if [ "$last_player" = "$player" ] && [ $((NOW - last_ts)) -lt "$DEDUPE_SECONDS" ]; then
            SKIPPED=$((SKIPPED + 1))
            continue
        fi
    fi

    # Pick greeting (try tiered via director_brain, fall back to template)
    if PICK_GREETING "$player"; then
        GREETING="$TIER_PICK"
    else
        GREETING=$(echo "$DEFAULT_GREETING_TEMPLATE" | sed "s/%P%/$player/g")
    fi

    # Fire RCON greeting
    "$RCON" msg "$GREETING" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        GREETED=$((GREETED + 1))
        echo "$player|$NOW" > "$GREET_FILE"
        echo "Greeted $player at $(date -d "@$NOW" '+%H:%M:%S')"
    else
        echo "ERROR greeting $player"
    fi
done <<< "$NEW"

if [ "$GREETED" -eq 0 ] && [ "$SKIPPED" -gt 0 ]; then
    echo "$SKIPPED player(s) skipped (dedupe window)"
elif [ "$GREETED" -gt 0 ]; then
    echo "$GREETED greeting(s) fired"
fi

exit 0