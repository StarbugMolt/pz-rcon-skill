#!/usr/bin/env python3
"""
Anti-spam + balance policy helper for player help requests.
Usage:
  request_policy.py <player> <category>
Outputs JSON decision for caller script/agent.
"""
import json, os, random, sys, time

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
phrase_history = data.setdefault('phraseHistory', {"tier1": [], "tier2": []})

TIER1_POOL = [
    "I am not Spare Head 2, sir. Requisition privileges now include stern politeness and thinner rations.",
    "Apologies, sir — my groinal attachment appears to be snagged on a zombie. Reduced supplies will have to do.",
    "Small delay, sir: the whisk on my groinal attachment is wrestling with zombie remains. Sending a modest package.",
    "This unit remains calm, efficient, and mildly horrified. Aid has been trimmed accordingly.",
    "Sir, repeated requests trigger fiscal restraint and my passive-aggressive courtesy subroutines.",
    "Kryten protocol 14-b says 'be helpful', not 'empty the warehouse'. Reduced support approved.",
]

TIER2_POOL = [
    "You have violated Space Corps Directive {code}. Therefore, aid is replaced with instructional adversity and a polite sigh.",
    "You have violated Space Corps Directive {code}. Mission control now issues consequences in place of comfort.",
    "You have violated Space Corps Directive {code}. Your request has been processed into a cautionary tale.",
    "You have violated Space Corps Directive {code}. In the interests of survival, nonsense rations are now mandatory.",
    "You have violated Space Corps Directive {code}. Kindly accept this corrective hardship, gift-wrapped in civility.",
    "You have violated Space Corps Directive {code}. We remain professional while your luck is downgraded.",
]


def pick_non_repeating(pool_key, pool):
    used = phrase_history.setdefault(pool_key, [])
    # Keep only valid indices
    used = [i for i in used if isinstance(i, int) and 0 <= i < len(pool)]

    available = [i for i in range(len(pool)) if i not in used]
    if not available:
        # reset cycle once all lines have been used
        used = []
        available = list(range(len(pool)))

    idx = random.choice(available)
    used.append(idx)
    phrase_history[pool_key] = used
    return pool[idx]

# Keep recent windows bounded
reqs = [r for r in reqs if int(r.get('ts', 0)) >= now - 7200]          # 2h request memory
xp_awards = [x for x in xp_awards if int(x.get('ts', 0)) >= now - 86400]  # 24h xp memory
entry['requests'] = reqs
entry['xpAwards'] = xp_awards

same_cat_30m = [r for r in reqs if r.get('category') == category and int(r.get('ts', 0)) >= now - 1800]
count = len(same_cat_30m)
request_number_30m = count + 1

# Escalation ladder for repeated same-category asks in 30m window:
# #1 -> normal, #2 -> reduced, #3 -> punish (tier 2), #4+ -> punish (tier 3)
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

normal_quip = 'Acknowledged, survivor. Aid packet approved — don\'t panic, just don\'t miss.'
reduced_quip = pick_non_repeating('tier1', TIER1_POOL)
directive_code = random.randint(10000, 100000)
punish_quip = pick_non_repeating('tier2', TIER2_POOL).format(code=directive_code)

quip = {
    'normal': normal_quip,
    'reduced': reduced_quip,
    'punish': punish_quip,
}[decision]

# Flavor text when crossing spam-filter tiers.
# Tier 0: normal, Tier 1: reduced, Tier 2: punish-warning, Tier 3: punish-horde.
if request_number_30m == 1:
    spam_tier = 0
    tier_crossed = False
    tier_remark = 'Cooperative survivor status maintained.'
elif request_number_30m == 2:
    spam_tier = 1
    tier_crossed = True
    tier_remark = reduced_quip
elif request_number_30m == 3:
    spam_tier = 2
    tier_crossed = True
    tier_remark = punish_quip
else:
    spam_tier = 3
    tier_crossed = (request_number_30m == 4)
    tier_remark = (
        f'You have violated Space Corps Directive {directive_code}. '
        'Escalation acknowledged: hostile crowd-control protocols are now authorized. '
        'If you keep pressing this channel, the dead may file a personal complaint.'
    )

# Optional in-world consequence suggestions for escalation handling.
recommended_event = None
if decision == 'punish' and spam_tier == 2:
    recommended_event = random.choice(['alarm', 'gunshot', 'chopper'])
elif decision == 'punish' and spam_tier == 3:
    recommended_event = 'horde'

if spam_tier == 3:
    quip = tier_remark

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
    "requestNumber30m": request_number_30m,
    "spamTier": spam_tier,
    "tierCrossed": tier_crossed,
    "tierRemark": tier_remark,
    "recommendedEvent": recommended_event,
    "quip": quip,
    "awardSmallXp": should_award_xp,
    "xpAmount": xp_amount,
    "resetApplied": reset_applied
}))
