#!/usr/bin/env python3
"""
Set or update stored player honorific for pz-rcon dialogue salutation.
Usage:
  set_player_honorific.py <player> <mister|maam|miss>
"""
import json, os, sys, time

if len(sys.argv) != 3:
    print('{"error":"usage: set_player_honorific.py <player> <mister|maam|miss>"}')
    sys.exit(1)

player = sys.argv[1].strip()
honorific = sys.argv[2].strip().lower()

if honorific not in {'mister', 'maam', 'miss'}:
    print('{"error":"honorific must be one of: mister, maam, miss"}')
    sys.exit(1)

skill_dir = os.path.dirname(os.path.dirname(__file__))
state_dir = os.path.join(skill_dir, 'state')
os.makedirs(state_dir, exist_ok=True)
profiles_file = os.path.join(state_dir, 'player-profiles.json')

if os.path.exists(profiles_file):
    with open(profiles_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"players": {}, "updatedAt": None}

players = data.setdefault('players', {})
entry = players.setdefault(player, {})
entry['honorific'] = honorific
entry['updatedAt'] = int(time.time())
data['updatedAt'] = int(time.time())

with open(profiles_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(json.dumps({"ok": True, "player": player, "honorific": honorific}))
