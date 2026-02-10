#!/usr/bin/env python3
"""
Simple anti-spam policy helper for player help requests.
Usage:
  request_policy.py <player> <category>
Outputs JSON decision for caller script/agent.
"""
import json, os, sys, time

if len(sys.argv) < 3:
    print('{"error":"usage: request_policy.py <player> <category>"}')
    sys.exit(1)

player = sys.argv[1].strip()
category = sys.argv[2].strip().lower()
now = int(time.time())

skill_dir = os.path.dirname(os.path.dirname(__file__))
state_dir = os.path.join(skill_dir, 'state')
os.makedirs(state_dir, exist_ok=True)
state_file = os.path.join(state_dir, 'recent-requests.json')

if os.path.exists(state_file):
    with open(state_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"players": {}, "updatedAt": None}

players = data.setdefault('players', {})
entry = players.setdefault(player, {"requests": []})
reqs = entry.setdefault('requests', [])

# Keep last 2 hours only
window = now - 7200
reqs = [r for r in reqs if int(r.get('ts', 0)) >= window]
entry['requests'] = reqs

same_cat_30m = [r for r in reqs if r.get('category') == category and int(r.get('ts', 0)) >= now - 1800]
count = len(same_cat_30m)

if count <= 1:
    decision = 'normal'
elif count == 2:
    decision = 'reduced'
else:
    decision = 'punish'

quip = {
    'normal': 'Copy that, survivor. Logistics are feeling generous today.',
    'reduced': 'Again? Supplies are not infinite, unlike your optimism.',
    'punish': 'Request denied in spirit. Enjoy your premium disappointment ration.'
}[decision]

reqs.append({"ts": now, "category": category, "decision": decision})
data['updatedAt'] = now

with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(json.dumps({
    "player": player,
    "category": category,
    "decision": decision,
    "recentSameCategory30m": count,
    "quip": quip
}))
