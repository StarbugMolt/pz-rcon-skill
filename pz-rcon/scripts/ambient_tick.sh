#!/usr/bin/env bash
# Ambient narrative tick (run every 5 minutes).
# - Runs only when players are online
# - Mostly sends atmospheric messages
# - Rarely triggers a light world event

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$DIR/.." && pwd)"
STATE_DIR="$SKILL_DIR/state"
STATE_FILE="$STATE_DIR/narrative-state.json"
mkdir -p "$STATE_DIR"

if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" <<'JSON'
{"tick":0,"lastActionTs":0,"lastEventTs":0}
JSON
fi

PLAYERS_OUT="$($DIR/pz-rcon.sh players || true)"
COUNT=$(printf "%s" "$PLAYERS_OUT" | sed -n 's/Players connected (\([0-9][0-9]*\)).*/\1/p' | head -n1)
COUNT=${COUNT:-0}

if [ "$COUNT" -le 0 ]; then
  echo "No players online; ambient tick skipped."
  exit 0
fi

NOW=$(date +%s)
read -r TICK LAST_ACTION LAST_EVENT < <(python3 - "$STATE_FILE" <<'PY'
import json,sys
p=sys.argv[1]
with open(p,'r',encoding='utf-8') as f:
    d=json.load(f)
print(d.get('tick',0), d.get('lastActionTs',0), d.get('lastEventTs',0))
PY
)

TICK=$((TICK+1))
R=$((RANDOM%100))
DO_EVENT=0

# Rare events: ~15% chance, and not more than once every 20 minutes.
if [ "$R" -lt 15 ] && [ $((NOW-LAST_EVENT)) -ge 1200 ]; then
  DO_EVENT=1
fi

if [ "$DO_EVENT" -eq 1 ]; then
  case $((RANDOM%3)) in
    0)
      $DIR/pz-rcon.sh msg "Emergency band chatter: distant rotter movement reported west of your position." ;;
    1)
      $DIR/pz-rcon.sh msg "Knox weather alert: electrical instability detected. Keep your head down." ;;
    2)
      $DIR/pz-rcon.sh msg "You hear something unnatural in the distance. Stay sharp, survivors." ;;
  esac
  case $((RANDOM%3)) in
    0) $DIR/pz-rcon.sh thunder ;;
    1) $DIR/pz-rcon.sh gunshot ;;
    2) $DIR/pz-rcon.sh lightning ;;
  esac
  LAST_EVENT=$NOW
else
  case $((RANDOM%6)) in
    0) $DIR/pz-rcon.sh msg "Emergency band update: movement is light for now. Use the lull wisely." ;;
    1) $DIR/pz-rcon.sh msg "Radio static clears: keep your lights low and your exits planned." ;;
    2) $DIR/pz-rcon.sh msg "Survivor tip: overconfidence is a short walk to becoming lunch." ;;
    3) $DIR/pz-rcon.sh msg "The wind carries no comfort today. Travel in caution, not in hope." ;;
    4) $DIR/pz-rcon.sh msg "Operations note: roads are safer than forests, until they are not." ;;
    5) $DIR/pz-rcon.sh msg "Quiet skies over Knox County. Enjoy it before reality remembers you." ;;
  esac
fi

python3 - "$STATE_FILE" "$TICK" "$NOW" "$LAST_EVENT" <<'PY'
import json,sys
p,tick,now,last_event=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
with open(p,'w',encoding='utf-8') as f:
    json.dump({"tick":tick,"lastActionTs":now,"lastEventTs":last_event},f)
PY

echo "Ambient tick complete (players=$COUNT, event=$DO_EVENT)."
