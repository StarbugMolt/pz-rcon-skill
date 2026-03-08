#!/bin/bash
# pz-rcon.sh - Project Zomboid RCON wrapper (Atmosphere & Events)
# Usage: ./pz-rcon.sh <command> [args...]
#
# Environment variables:
#   PZ_RCON_HOST     - Server host (default: localhost)
#   PZ_RCON_PORT     - RCON port (default: 16262)
#   PZ_RCON_PASSWORD - RCON password (required)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Auto-load credentials from safe location (/home/starbugmolt/.env)
# This survives workspace updates/resets.
# Only fall back to skill-local .env if home one doesn't exist.
if [ -f "/home/starbugmolt/.env" ]; then
    set -a
    source "/home/starbugmolt/.env"
    set +a
elif [ -f "$SKILL_DIR/.env" ]; then
    set -a
    source "$SKILL_DIR/.env"
    set +a
fi

HOST="${PZ_RCON_HOST:-localhost}"
PORT="${PZ_RCON_PORT:-16262}"
PASSWORD="${PZ_RCON_PASSWORD:-}"

if ! command -v rcon &> /dev/null; then
    echo "Error: rcon-cli not found. Install from https://github.com/gorcon/rcon-cli/releases"
    exit 1
fi

if [ -z "$PASSWORD" ]; then
    echo "Error: PZ_RCON_PASSWORD environment variable not set"
    exit 1
fi

rcon_cmd() {
    # Join all args into a single command string
    local cmd=""
    for arg in "$@"; do
        if [[ "$arg" =~ [[:space:]] ]]; then
            cmd="$cmd \"$arg\""
        else
            cmd="$cmd $arg"
        fi
    done
    cmd=$(echo "$cmd" | sed 's/^ *//')  # trim leading space
    rcon -a "$HOST:$PORT" -p "$PASSWORD" "$cmd"
}

# Find last space position in string (for word-boundary splitting)
rfind_last_space() {
    local str="$1"
    local last_pos=0
    local pos=0
    for ((pos=0; pos<${#str}; pos++)); do
        if [[ "${str:$pos:1}" == " " ]]; then
            last_pos=$pos
        fi
    done
    echo "$last_pos"
}

case "${1:-help}" in
    # Player info
    players|list)
        rcon_cmd players
        ;;

    # Broadcasting
    msg|broadcast|say)
        shift
        if [ -z "$1" ]; then echo "Usage: $0 msg <message>"; exit 1; fi
        # PZ RCON can choke on non-ASCII / oversized payloads in some builds.
        # Keep broadcasts single-line, printable ASCII, and bounded in length.
        CLEAN_MSG=$(printf "%s" "$*" | LC_ALL=C tr -cd '\11\12\15\40-\176')
        CLEAN_MSG=${CLEAN_MSG//$'\n'/ }
        CLEAN_MSG=${CLEAN_MSG//$'\r'/ }
        
        # Split into chunks of 150 chars, breaking at word boundaries
        CHUNK_SIZE=150
        while [ -n "$CLEAN_MSG" ]; do
            if [ ${#CLEAN_MSG} -le $CHUNK_SIZE ]; then
                CHUNK="$CLEAN_MSG"
                CLEAN_MSG=""
            else
                # Find last space before chunk size
                CHUNK="${CLEAN_MSG:0:$CHUNK_SIZE}"
                LAST_SPACE=$(rfind_last_space "$CHUNK")
                if [ -n "$LAST_SPACE" ] && [ "$LAST_SPACE" -gt 10 ]; then
                    CHUNK="${CHUNK:0:$LAST_SPACE}"
                    CLEAN_MSG="${CLEAN_MSG:$((LAST_SPACE + 1))}"
                else
                    # No space found, hard break at chunk size
                    CHUNK="${CHUNK:0:$CHUNK_SIZE}"
                    CLEAN_MSG="${CLEAN_MSG:$CHUNK_SIZE}"
                fi
            fi
            if [ -z "$CHUNK" ]; then
                break
            fi
            rcon_cmd "servermsg \"$CHUNK\""
            sleep 0.5  # Brief pause between messages
        done
        ;;

    # Direct message to specific player
    pm|whisper|tell)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 pm <username> <message>"; exit 1; fi
        USERNAME="$1"
        shift
        MESSAGE="$*"
        CLEAN_MSG=$(printf "%s" "$MESSAGE" | LC_ALL=C tr -cd '\11\12\15\40-\176')
        CLEAN_MSG=${CLEAN_MSG//$'\n'/ }
        CLEAN_MSG=${CLEAN_MSG//$'\r'/ }
        CLEAN_MSG=${CLEAN_MSG:0:180}
        if [ -z "$CLEAN_MSG" ]; then
            echo "Error: message is empty after sanitization (ASCII-only)."
            exit 1
        fi
        # PZ RCON: servermsg with "to:username" prefix sends private message
        rcon_cmd "servermsg \"$CLEAN_MSG\" -u \"$USERNAME\""
        ;;

    # Items
    give|item)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 give <username> <item> [count]"; exit 1; fi
        USERNAME="$1"
        ITEM="$2"
        COUNT="${3:-1}"
        rcon_cmd additem "$USERNAME" "$ITEM" "$COUNT"
        
        # Auto-add ammo for weapons
        case "$ITEM" in
            Base.Pistol|Base.Pistol2|Base.Revolver|Base.Revolver_Long|Base.M9)
                echo "Auto-adding 9mm ammo..."
                rcon_cmd additem "$USERNAME" "Base.Bullets9mmBox" 2
                ;;
            Base.Shotgun|Base.DoubleBarrelShotgun|Base.SawnOffShotgun)
                echo "Auto-adding shotgun shells..."
                rcon_cmd additem "$USERNAME" "Base.ShotgunShells" 8
                ;;
            Base.AssaultRifle|Base.M14|Base.SKS)
                echo "Auto-adding 7.62mm ammo..."
                rcon_cmd additem "$USERNAME" "Base.7.62x39mmBox" 1
                ;;
            Base.HuntingRifle|Base.BoltRifle)
                echo "Auto-adding .308 ammo..."
                rcon_cmd additem "$USERNAME" "Base.308WinchesterBox" 1
                ;;
            Base.VarmintRifle)
                echo "Auto-adding .22 ammo..."
                rcon_cmd additem "$USERNAME" "Base.22LR" 1
                ;;
        esac
        ;;

    # XP
    xp)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 xp <username> <perk>=<amount>"; exit 1; fi
        rcon_cmd addxp "$1" "$2"
        ;;

    # Vehicles
    vehicle|spawn-vehicle)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 vehicle <type> <username>"; exit 1; fi
        rcon_cmd addvehicle "$1" "$2"
        ;;

    # Events
    horde)
        shift
        if [ -z "$1" ]; then echo "Usage: $0 horde <count> [username]"; exit 1; fi
        COUNT="$1"
        USERNAME="${2:-}"
        if [ -n "$USERNAME" ]; then
            rcon_cmd createhorde "$COUNT" "$USERNAME"
        else
            rcon_cmd createhorde "$COUNT"
        fi
        ;;
    chopper|helicopter)
        rcon_cmd chopper
        echo "Helicopter event triggered."
        ;;
    gunshot)
        rcon_cmd gunshot
        echo "Gunshot sound triggered."
        ;;
    alarm)
        rcon_cmd alarm
        echo "Alarm triggered."
        ;;
    lightning)
        shift
        if [ -n "$1" ]; then
            rcon_cmd lightning "\"$1\""
        else
            rcon_cmd lightning
        fi
        ;;
    thunder)
        shift
        if [ -n "$1" ]; then
            rcon_cmd thunder "\"$1\""
        else
            rcon_cmd thunder
        fi
        ;;

    # Weather
    rain)
        shift
        case "${1:-start}" in
            start)
                if [ -n "${2:-}" ]; then
                    rcon_cmd startrain "$2"
                else
                    rcon_cmd startrain
                fi
                ;;
            stop)  rcon_cmd stoprain ;;
            *)     rcon_cmd startrain "$1" ;;  # intensity value
        esac
        ;;
    storm)
        shift
        if [ -n "$1" ]; then
            rcon_cmd "startstorm $1"
        else
            rcon_cmd startstorm
        fi
        ;;
    weather-stop|clear)
        rcon_cmd stopweather
        echo "Weather cleared."
        ;;

    # Raw command (for anything not covered)
    raw|cmd)
        shift
        rcon_cmd "$@"
        ;;

    # Help
    help|--help|-h|*)
        cat << 'EOF'
Project Zomboid RCON - Atmosphere & Events

PLAYER INFO:
  players, list              List connected players

BROADCASTING:
  msg <message>              Broadcast message to all players
  say <message>              Alias for msg

REWARDS:
  give <user> <item> [count] Give item (e.g., Base.Axe)
  xp <user> <perk>=<amount>  Give XP (e.g., Carpentry=100)
  vehicle <type> <user>      Spawn vehicle near player

EVENTS:
  horde <count> [user]       Spawn zombie horde
  chopper                    Helicopter flyover event
  gunshot                    Gunshot sound (attracts zombies)
  alarm                      Building alarm
  lightning [user]           Lightning strike
  thunder [user]             Thunder sound

WEATHER:
  rain [start|stop|1-100]    Control rain (optional intensity)
  storm [hours]              Start thunderstorm
  clear, weather-stop        Clear all weather

OTHER:
  raw <command> [args...]    Run any RCON command

ENVIRONMENT:
  PZ_RCON_HOST     Server host (default: localhost)
  PZ_RCON_PORT     RCON port (default: 16262)
  PZ_RCON_PASSWORD RCON password (required)

EXAMPLES:
  $0 msg "A cold wind blows from the north..."
  $0 give PlayerName Base.Shotgun 1
  $0 xp PlayerName Aiming=100
  $0 horde 30 PlayerName
  $0 storm 2
EOF
        ;;
esac
