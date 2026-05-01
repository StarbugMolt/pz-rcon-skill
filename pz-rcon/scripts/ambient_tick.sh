#!/usr/bin/env bash
# SIMON Ambient Tick v2 — Contextual Intelligence Layer
# Gathers real server state and passes it to the AI agent for decision-making.
# The AI generates contextual responses, not random ones.

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$DIR/.." && pwd)"
STATE_DIR="$SKILL_DIR/state"
CONTEXT_FILE="$STATE_DIR/tick-context.json"
mkdir -p "$STATE_DIR"

# ─── 1. GATHER SERVER STATE ───────────────────────────────────────────

# Who's online?
PLAYERS_OUT="$($DIR/pz-rcon.sh players 2>/dev/null || echo "Players connected (0):")"
COUNT=$(printf "%s" "$PLAYERS_OUT" | sed -n 's/Players connected (\([0-9][0-9]*\)).*/\1/p' | head -n1)
COUNT=${COUNT:-0}

# Extract player names (lines after "Players connected" that aren't empty)
PLAYER_NAMES=$(printf "%s" "$PLAYERS_OUT" | grep -v "Players connected" | grep -v "^$" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | tr '\n' ',' | sed 's/,$//')

if [ "$COUNT" -le 0 ]; then
    echo "No players online; tick skipped."
    exit 0
fi

# What time is it in-game? (check via RCON if possible, else use real time)
HOUR=$(date +%H)
TIME_OF_DAY="day"
if [ "$HOUR" -ge 22 ] || [ "$HOUR" -lt 6 ]; then
    TIME_OF_DAY="night"
elif [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 10 ]; then
    TIME_OF_DAY="morning"
elif [ "$HOUR" -ge 10 ] && [ "$HOUR" -lt 14 ]; then
    TIME_OF_DAY="midday"
elif [ "$HOUR" -ge 14 ] && [ "$HOUR" -lt 18 ]; then
    TIME_OF_DAY="afternoon"
elif [ "$HOUR" -ge 18 ] && [ "$HOUR" -lt 22 ]; then
    TIME_OF_DAY="evening"
fi

# Load previous state
TICK=0
LAST_EVENT_TS=0
LAST_WEATHER=""
MOOD="calm"
NARRATIVE_THREAD=""
if [ -f "$CONTEXT_FILE" ]; then
    TICK=$(python3 -c "import json; d=json.load(open('$CONTEXT_FILE')); print(d.get('tick',0))" 2>/dev/null || echo 0)
    LAST_EVENT_TS=$(python3 -c "import json; d=json.load(open('$CONTEXT_FILE')); print(d.get('lastEventTs',0))" 2>/dev/null || echo 0)
    LAST_WEATHER=$(python3 -c "import json; d=json.load(open('$CONTEXT_FILE')); print(d.get('lastWeather',''))" 2>/dev/null || echo "")
    MOOD=$(python3 -c "import json; d=json.load(open('$CONTEXT_FILE')); print(d.get('mood','calm'))" 2>/dev/null || echo "calm")
    NARRATIVE_THREAD=$(python3 -c "import json; d=json.load(open('$CONTEXT_FILE')); print(d.get('narrativeThread',''))" 2>/dev/null || echo "")
fi
TICK=$((TICK + 1))
NOW=$(date +%s)
SECONDS_SINCE_EVENT=$((NOW - LAST_EVENT_TS))

# Load recent player requests
RECENT_REQUESTS="{}"
if [ -f "$STATE_DIR/recent-requests.json" ]; then
    RECENT_REQUESTS=$(cat "$STATE_DIR/recent-requests.json" 2>/dev/null || echo "{}")
fi

# Load player profiles
PLAYER_PROFILES="{}"
if [ -f "$STATE_DIR/player-profiles.json" ]; then
    PLAYER_PROFILES=$(cat "$STATE_DIR/player-profiles.json" 2>/dev/null || echo "{}")
fi

# ─── 2. BUILD CONTEXT PAYLOAD ────────────────────────────────────────

CONTEXT=$(python3 -c "
import json, sys

ctx = {
    'tick': $TICK,
    'timestamp': $NOW,
    'players': {
        'count': $COUNT,
        'names': '$PLAYER_NAMES'.split(',') if '$PLAYER_NAMES' else []
    },
    'timeOfDay': '$TIME_OF_DAY',
    'serverHour': $HOUR,
    'lastWeather': '$LAST_WEATHER',
    'mood': '$MOOD',
    'narrativeThread': '''$NARRATIVE_THREAD''',
    'secondsSinceLastEvent': $SECONDS_SINCE_EVENT,
    'recentRequests': json.loads('''$RECENT_REQUESTS'''),
    'playerProfiles': json.loads('''$PLAYER_PROFILES''')
}
print(json.dumps(ctx, indent=2))
")

echo "$CONTEXT" > "$CONTEXT_FILE"
echo "Context gathered (tick=$TICK, players=$COUNT, time=$TIME_OF_DAY, mood=$MOOD)"
echo "$CONTEXT"
