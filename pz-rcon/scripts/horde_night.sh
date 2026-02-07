#!/bin/bash
# scripts/horde_night.sh - Trigger a manual Horde Night event via RCON
# Usage: ./horde_night.sh [intensity]
#   intensity: Number of zombies per player (default: 30)

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/pz-rcon.sh" raw players > /tmp/pz_players.txt

INTENSITY="${1:-30}"

echo "👻 Preparing Horde Night (Intensity: $INTENSITY)..."

# 1. Announce
"$DIR/pz-rcon.sh" msg "WARNING: Seismic activity detected. The dead are restless..."
sleep 2
"$DIR/pz-rcon.sh" msg "Horde Night initiated. Good luck, survivors."

# 2. Parse players and spawn
# Output format of 'players' command varies, assuming "Players connected (X): name1, name2"
# or separate lines. This is a heuristic parser.

PLAYERS=$(cat /tmp/pz_players.txt | sed 's/Players connected ([0-9]*): //g' | tr ',' '\n' | tr -d ' ')

for PLAYER in $PLAYERS; do
    if [ -n "$PLAYER" ]; then
        echo "🧟 Spawning $INTENSITY zombies on $PLAYER"
        "$DIR/pz-rcon.sh" horde "$INTENSITY" "$PLAYER"
        
        # Optional: Lightning effect for drama
        "$DIR/pz-rcon.sh" thunder "$PLAYER"
    fi
done

# 3. Finalize
echo "✅ Horde Night triggered for all online players."
