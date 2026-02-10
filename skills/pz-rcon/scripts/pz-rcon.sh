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

# Auto-load local skill env if present (unless vars already set by caller)
if [ -f "$SKILL_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1090
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
    rcon -a "$HOST:$PORT" -p "$PASSWORD" "$@"
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
        CLEAN_MSG=${CLEAN_MSG:0:180}
        if [ -z "$CLEAN_MSG" ]; then
            echo "Error: message is empty after sanitization (ASCII-only)."
            exit 1
        fi
        rcon_cmd "servermsg \"$CLEAN_MSG\""
        ;;

    # Items
    give|item)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 give <username> <item> [count]"; exit 1; fi
        USERNAME="$1"
        ITEM="$2"
        COUNT="${3:-1}"
        rcon_cmd additem "\"$USERNAME\"" "$ITEM" "$COUNT"
        ;;

    # XP
    xp)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 xp <username> <perk>=<amount>"; exit 1; fi
        rcon_cmd addxp "\"$1\"" "$2"
        ;;

    # Vehicles
    vehicle|spawn-vehicle)
        shift
        if [ -z "$2" ]; then echo "Usage: $0 vehicle <type> <username>"; exit 1; fi
        rcon_cmd "addvehicle \"$1\" \"$2\""
        ;;

    # Events
    horde)
        shift
        if [ -z "$1" ]; then echo "Usage: $0 horde <count> [username]"; exit 1; fi
        COUNT="$1"
        USERNAME="${2:-}"
        if [ -n "$USERNAME" ]; then
            rcon_cmd createhorde "$COUNT" "\"$USERNAME\""
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
