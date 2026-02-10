#!/usr/bin/env python3
"""
Anti-spam + balance policy helper for player help requests.
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
entry = players.setdefault(player, {"requests": [], "xpAwards": []})
reqs = entry.setdefault('requests', [])
xp_awards = entry.setdefault('xpAwards', [])

# Keep recent windows bounded
reqs = [r for r in reqs if int(r.get('ts', 0)) >= now - 7200]          # 2h request memory
xp_awards = [x for x in xp_awards if int(x.get('ts', 0)) >= now - 86400]  # 24h xp memory
entry['requests'] = reqs
entry['xpAwards'] = xp_awards

same_cat_30m = [r for r in reqs if r.get('category') == category and int(r.get('ts', 0)) >= now - 1800]
count = len(same_cat_30m)

# Escalation ladder for repeated same-category asks in 30m window:
# #1 -> normal, #2 -> reduced, #3+ -> punish
if count == 0:
    decision = 'normal'
elif count == 1:
    decision = 'reduced'
else:
    decision = 'punish'

# Rare, small XP assistance (only for skill-gated categories)
skill_categories = {'mechanics', 'medical', 'carpentry', 'aiming'}
xp_recent = len([x for x in xp_awards if int(x.get('ts', 0)) >= now - 7200])
should_award_xp = category in skill_categories and decision != 'punish' and xp_recent == 0
xp_amount = 0
if should_award_xp:
    xp_amount = 25 if decision == 'normal' else 10  # deliberately small
    xp_awards.append({"ts": now, "category": category, "amount": xp_amount})

quip = {
    'normal': 'Acknowledged, survivor. Aid packet approved — don\'t panic, just don\'t miss.',
    'reduced': 'You\'re back on this frequency again? Fine. Reduced ration; consider it a character-building experience.',
    'punish': 'Request logged, sanity questioned. Today\'s delivery is one (1) deluxe disappointment, with Kryten-grade politeness.'
}[decision]

# Keep rolling pressure; do not reset on punish.
reset_applied = False
reqs.append({"ts": now, "category": category, "decision": decision})
data['updatedAt'] = now

with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(json.dumps({
    "player": player,
    "category": category,
    "decision": decision,
    "recentSameCategory30m": count,
    "quip": quip,
    "awardSmallXp": should_award_xp,
    "xpAmount": xp_amount,
    "resetApplied": reset_applied
}))
