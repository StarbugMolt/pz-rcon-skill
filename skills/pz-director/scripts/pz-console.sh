#!/usr/bin/env bash
# pz-console.sh — Project Zomboid console wrapper over the Discord command relay.
#
# Runtime commands use explicit aliases. Unknown aliases are rejected. Dangerous
# raw console access is disabled by default and is an operator-only escape hatch.
# Vehicle spawns require a one-time authorization token from simon_delivery.py.

set -uo pipefail

ENV_FILE="${ENV_FILE:-$HOME/.env}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

read_env_value() {
    local key="$1"
    [ -f "$ENV_FILE" ] || return 0
    python3 - "$ENV_FILE" "$key" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
key = sys.argv[2]
try:
    lines = path.read_text(encoding="utf-8").splitlines()
except OSError:
    raise SystemExit(0)
for raw in lines:
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    if k.strip() == key:
        print(v.strip().strip('"').strip("'"))
        break
PY
}

PZ_DISCORD_COMMANDS_CHANNEL_ID="${PZ_DISCORD_COMMANDS_CHANNEL_ID:-$(read_env_value PZ_DISCORD_COMMANDS_CHANNEL_ID)}"
PZ_RELAY_BOT_ID="${PZ_RELAY_BOT_ID:-$(read_env_value PZ_RELAY_BOT_ID)}"
PZ_CONSOLE_WAIT="${PZ_CONSOLE_WAIT:-$(read_env_value PZ_CONSOLE_WAIT)}"
PZ_CONSOLE_TIMEOUT="${PZ_CONSOLE_TIMEOUT:-$(read_env_value PZ_CONSOLE_TIMEOUT)}"
PZ_CONSOLE_LOCK_FILE="${PZ_CONSOLE_LOCK_FILE:-$(read_env_value PZ_CONSOLE_LOCK_FILE)}"
PZ_ALLOW_RAW="${PZ_ALLOW_RAW:-$(read_env_value PZ_ALLOW_RAW)}"

WAIT="${PZ_CONSOLE_WAIT:-1}"
TIMEOUT="${PZ_CONSOLE_TIMEOUT:-8}"
LOCK_FILE="${PZ_CONSOLE_LOCK_FILE:-/tmp/simon-pz-console.lock}"
ALLOW_RAW="${PZ_ALLOW_RAW:-false}"

MAX_GIVE_COUNT=20
MAX_HORDE_COUNT=100
MAX_XP_AMOUNT=1000
MAX_STORM_HOURS=24
MAX_RAIN_INTENSITY=100

[[ "$TIMEOUT" =~ ^[0-9]+$ ]] || { echo "ERROR: PZ_CONSOLE_TIMEOUT must be an integer" >&2; exit 64; }
[ "$TIMEOUT" -gt 0 ] || { echo "ERROR: PZ_CONSOLE_TIMEOUT must be > 0" >&2; exit 64; }
[[ "$WAIT" == "0" || "$WAIT" == "1" ]] || { echo "ERROR: PZ_CONSOLE_WAIT must be 0 or 1" >&2; exit 64; }

if [ -z "$PZ_DISCORD_COMMANDS_CHANNEL_ID" ]; then
    echo "ERROR: PZ_DISCORD_COMMANDS_CHANNEL_ID is not configured" >&2
    exit 64
fi

usage() {
    cat <<'USAGE' >&2
Usage: pz-console.sh <command> [args...]

Model/runtime-safe commands:
  players
  give <PlayerName> <Module.Item> [count]
  horde <count> [PlayerName]
  xp <PlayerName> <Perk>=<amount>
  chopper | gunshot | alarm
  lightning [PlayerName] | thunder [PlayerName]
  rain start [intensity] | rain stop | rain <intensity>
  storm [hours]
  clear | weather-stop

Internal guarded command (simon_delivery.py only):
  vehicle <VehicleScript> <PlayerName> <one-time-token>

Operator-only escape hatch (disabled unless PZ_ALLOW_RAW=true):
  raw <console command...>
USAGE
}

[ "$#" -gt 0 ] || { usage; exit 64; }

safe_text() {
    local value="$1"
    [ -n "$value" ] || return 1
    # Bash variables cannot contain NUL bytes. Reject CR/LF injection here;
    # attempting to test $'\0' would collapse to an empty string and reject
    # every legitimate value.
    [[ "$value" != *$'\n'* && "$value" != *$'\r'* ]]
}

escape_arg() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    printf '%s' "$value"
}

validate_item_id() {
    [[ "$1" =~ ^[A-Za-z][A-Za-z0-9_]*\.[A-Za-z0-9_][A-Za-z0-9_.-]*$ ]]
}

validate_intensity() {
    [[ "$1" =~ ^[0-9]+$ ]] && [ "$1" -ge 0 ] && [ "$1" -le "$MAX_RAIN_INTENSITY" ]
}

cmd="$1"
shift
raw=""
response_kind="generic"
requires_confirmation=1

case "$cmd" in
    players|list)
        [ "$#" -eq 0 ] || { echo "ERROR: players takes no arguments" >&2; exit 64; }
        raw="players"
        response_kind="players"
        ;;
    give)
        [ "$#" -ge 2 ] && [ "$#" -le 3 ] || { echo "ERROR: give requires <PlayerName> <Module.Item> [count]" >&2; exit 64; }
        safe_text "$1" || { echo "ERROR: invalid player name" >&2; exit 64; }
        safe_text "$2" && validate_item_id "$2" || { echo "ERROR: invalid item identifier" >&2; exit 64; }
        user="$(escape_arg "$1")"
        item="$(escape_arg "$2")"
        count="${3:-1}"
        [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -gt 0 ] && [ "$count" -le "$MAX_GIVE_COUNT" ] || {
            echo "ERROR: give count must be 1..${MAX_GIVE_COUNT}" >&2; exit 64;
        }
        raw="additem \"${user}\" \"${item}\" ${count}"
        ;;
    vehicle)
        [ "$#" -eq 3 ] || { echo "ERROR: vehicle is guarded; use simon_delivery.py vehicle-drop" >&2; exit 64; }
        safe_text "$1" && safe_text "$2" && safe_text "$3" || { echo "ERROR: invalid vehicle delivery arguments" >&2; exit 64; }
        python3 "$SCRIPT_DIR/simon_delivery.py" consume-token "$3" "$1" "$2" >/dev/null 2>&1 || {
            echo "ERROR: vehicle spawn denied: missing/invalid one-time delivery authorization" >&2
            exit 77
        }
        vehicle="$(escape_arg "$1")"
        user="$(escape_arg "$2")"
        raw="addvehicle \"${vehicle}\" \"${user}\""
        ;;
    horde)
        [ "$#" -ge 1 ] && [ "$#" -le 2 ] || { echo "ERROR: horde requires <count> [PlayerName]" >&2; exit 64; }
        count="$1"
        [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -gt 0 ] && [ "$count" -le "$MAX_HORDE_COUNT" ] || {
            echo "ERROR: horde count must be 1..${MAX_HORDE_COUNT}" >&2; exit 64;
        }
        if [ "$#" -eq 2 ]; then
            safe_text "$2" || { echo "ERROR: invalid player name" >&2; exit 64; }
            user="$(escape_arg "$2")"
            raw="createhorde ${count} \"${user}\""
        else
            raw="createhorde ${count}"
        fi
        ;;
    xp)
        [ "$#" -eq 2 ] || { echo "ERROR: xp requires <PlayerName> <Perk>=<amount>" >&2; exit 64; }
        safe_text "$1" && safe_text "$2" || { echo "ERROR: invalid xp arguments" >&2; exit 64; }
        [[ "$2" =~ ^[A-Za-z][A-Za-z0-9_.]*=([0-9]+)$ ]] || { echo "ERROR: invalid xp specification" >&2; exit 64; }
        amount="${BASH_REMATCH[1]}"
        [ "$amount" -gt 0 ] && [ "$amount" -le "$MAX_XP_AMOUNT" ] || {
            echo "ERROR: xp amount must be 1..${MAX_XP_AMOUNT}" >&2; exit 64;
        }
        user="$(escape_arg "$1")"
        raw="addxp \"${user}\" $2"
        ;;
    chopper|gunshot|alarm)
        [ "$#" -eq 0 ] || { echo "ERROR: $cmd takes no arguments" >&2; exit 64; }
        raw="$cmd"
        ;;
    lightning|thunder)
        [ "$#" -le 1 ] || { echo "ERROR: $cmd takes at most one player" >&2; exit 64; }
        if [ "$#" -eq 1 ]; then
            safe_text "$1" || { echo "ERROR: invalid player name" >&2; exit 64; }
            user="$(escape_arg "$1")"
            raw="$cmd \"${user}\""
        else
            raw="$cmd"
        fi
        ;;
    rain)
        [ "$#" -ge 1 ] && [ "$#" -le 2 ] || { echo "ERROR: rain requires start [intensity], stop, or <intensity>" >&2; exit 64; }
        case "$1" in
            start)
                if [ "$#" -eq 2 ]; then
                    validate_intensity "$2" || { echo "ERROR: rain intensity must be 0..${MAX_RAIN_INTENSITY}" >&2; exit 64; }
                    raw="startrain $2"
                else
                    raw="startrain"
                fi
                ;;
            stop)
                [ "$#" -eq 1 ] || { echo "ERROR: rain stop takes no intensity" >&2; exit 64; }
                raw="stoprain"
                ;;
            *)
                [ "$#" -eq 1 ] && validate_intensity "$1" || { echo "ERROR: rain intensity must be 0..${MAX_RAIN_INTENSITY}" >&2; exit 64; }
                raw="startrain $1"
                ;;
        esac
        ;;
    storm)
        [ "$#" -le 1 ] || { echo "ERROR: storm takes at most one duration" >&2; exit 64; }
        if [ "$#" -eq 1 ]; then
            [[ "$1" =~ ^[0-9]+$ ]] && [ "$1" -gt 0 ] && [ "$1" -le "$MAX_STORM_HOURS" ] || {
                echo "ERROR: storm duration must be 1..${MAX_STORM_HOURS} hours" >&2; exit 64;
            }
            raw="startstorm $1"
        else
            raw="startstorm"
        fi
        ;;
    clear|weather-stop)
        [ "$#" -eq 0 ] || { echo "ERROR: $cmd takes no arguments" >&2; exit 64; }
        raw="stopweather"
        ;;
    raw|cmd)
        case "${ALLOW_RAW,,}" in
            1|true|yes|on) ;;
            *) echo "ERROR: raw console access is disabled; set PZ_ALLOW_RAW=true only for explicit operator use" >&2; exit 77 ;;
        esac
        [ "$#" -gt 0 ] || { echo "ERROR: raw requires a console command" >&2; exit 64; }
        raw="$*"
        requires_confirmation=0
        ;;
    *)
        echo "ERROR: unknown pz-console alias '$cmd'; use an explicit supported alias" >&2
        exit 64
        ;;
esac

# Safe runtime aliases must always receive authoritative confirmation. This
# prevents helpers from treating a mere Discord post as a successful mutation.
if [ "$requires_confirmation" = "1" ] && [ "$WAIT" != "1" ]; then
    echo "ERROR: safe runtime command '$cmd' requires PZ_CONSOLE_WAIT=1" >&2
    exit 78
fi
if [ "$WAIT" = "1" ] && [ -z "$PZ_RELAY_BOT_ID" ]; then
    echo "ERROR: PZ_RELAY_BOT_ID is required when waiting for confirmation" >&2
    exit 64
fi

TARGET="channel:${PZ_DISCORD_COMMANDS_CHANNEL_ID}"
READ_CMD=(openclaw message read --channel discord --target "$TARGET" --limit 12)

# Confirmed requests are serialized because the native PZ Discord bridge has
# no request/correlation ID.
if [ "$WAIT" = "1" ]; then
    command -v flock >/dev/null 2>&1 || { echo "ERROR: flock is required for confirmed console commands" >&2; exit 69; }
    exec 9>"$LOCK_FILE"
    flock -w "$TIMEOUT" 9 || { echo "ERROR: timed out waiting for console lock" >&2; exit 75; }
fi

JSON_TMP=""
cleanup() {
    [ -n "$JSON_TMP" ] && rm -f "$JSON_TMP"
}
trap cleanup EXIT

baseline="0"
if [ "$WAIT" = "1" ]; then
    JSON_TMP="$(mktemp)" || { echo "ERROR: could not create response scratch file" >&2; exit 70; }
    BEFORE="$("${READ_CMD[@]}" 2>/dev/null)" || { echo "ERROR: failed to read command channel before posting" >&2; exit 74; }
    printf '%s' "$BEFORE" > "$JSON_TMP"
    baseline="$(python3 - "$PZ_RELAY_BOT_ID" "$JSON_TMP" <<'PY'
import json, sys
from pathlib import Path
relay, path = sys.argv[1:3]
try:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
except Exception:
    print(0)
    raise SystemExit
msgs = data.get("payload", {}).get("messages", data.get("messages", []))
ids = []
for msg in msgs if isinstance(msgs, list) else []:
    if not isinstance(msg, dict):
        continue
    author = msg.get("author", {})
    if str(author.get("id", "")) != relay:
        continue
    try:
        ids.append(int(str(msg.get("id", 0))))
    except Exception:
        pass
print(max(ids, default=0))
PY
)"
fi

POST_OUT="$(openclaw message send --channel discord --target "$TARGET" --message "$raw" 2>&1)"
POST_RC=$?
if [ $POST_RC -ne 0 ]; then
    echo "ERROR: failed to post console command (exit $POST_RC): $POST_OUT" >&2
    exit $POST_RC
fi

if [ "$WAIT" = "0" ]; then
    echo "[posted]"
    exit 0
fi

start_ts="$(date +%s)"
while true; do
    now_ts="$(date +%s)"
    if [ $((now_ts - start_ts)) -ge "$TIMEOUT" ]; then
        echo "ERROR: no authoritative response within ${TIMEOUT}s" >&2
        exit 124
    fi

    MSGS="$("${READ_CMD[@]}" 2>/dev/null)" || { sleep 1; continue; }
    printf '%s' "$MSGS" > "$JSON_TMP"
    RESPONSE="$(python3 - "$PZ_RELAY_BOT_ID" "$baseline" "$response_kind" "$JSON_TMP" <<'PY'
import json, re, sys
from pathlib import Path
relay, baseline_raw, kind, path = sys.argv[1:5]
try:
    baseline = int(baseline_raw)
except Exception:
    baseline = 0
try:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
except Exception:
    raise SystemExit
msgs = data.get("payload", {}).get("messages", data.get("messages", []))
candidates = []
for msg in msgs if isinstance(msgs, list) else []:
    if not isinstance(msg, dict):
        continue
    author = msg.get("author", {})
    if str(author.get("id", "")) != relay:
        continue
    try:
        mid = int(str(msg.get("id", 0)))
    except Exception:
        continue
    if mid <= baseline:
        continue
    content = str(msg.get("content", "") or "").strip()
    if content:
        candidates.append((mid, content))

for _mid, content in sorted(candidates):
    lower = content.casefold()
    if kind == "players":
        if re.search(r"Players\s+connected\s+\(\d+\)", content, re.I):
            print(content)
            break
        continue
    # Shared-channel migration safety: obvious lifecycle/roster lines are not
    # confirmations for unrelated mutations.
    if "connected to server" in lower or "disconnected" in lower or re.search(r"Players\s+connected\s+\(\d+\)", content, re.I):
        continue
    print(content)
    break
PY
)"

    if [ -n "$RESPONSE" ]; then
        printf '%s\n' "$RESPONSE"
        lower="$(printf '%s' "$RESPONSE" | tr '[:upper:]' '[:lower:]')"
        case "$lower" in
            *"unknown command"*|*"invalid command"*|*"command failed"*|*"player not found"*|*"no such item"*|*"not found"*|*"invalid position"*|*"error:"*)
                exit 2
                ;;
        esac
        exit 0
    fi
    sleep 1
done
