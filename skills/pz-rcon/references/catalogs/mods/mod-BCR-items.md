# BCR — Body Count Rewards [B42.20]

- **Workshop ID:** 3660382016
- **Mod ID:** `BCR`
- **Author:** Lenniitsch (open source, MIT license)
- **Build target:** B42.13+ Stable, SP + MP
- **Status:** ✅ VERIFIED — no spawnable items, perk/trait progression mod

## What it adds

"Your body count actually matters" — kills earn trait rewards at configurable milestones. Spiritual successor to Circuit's "Kill Milestones" B42 mod.

### 43 traits in the reward pool
- 21 earnable (positive traits you gain)
- 22 removable (negative traits you shed)
- All 43 individually toggleable in sandbox

### Sandbox options (host-configurable, in-game)
- Kill threshold per milestone (2 → 10,000)
- Scaling: linear (constant K-to-reward) or progressive (each milestone harder)
- Reward priority: remove negatives first / add positives first / coin flip
- **"Grant Missed Opportunities"** — install mid-game with thousands of kills, then kill one zombie → dumps all owed rewards at once. Useful for late-add servers.
- Drop chances scale with trait cost (1-2pt traits common, 7-8pt traits rare)
- Positive rewards / negative removal / both — server's choice

### UI
- Stats: 3 tabs (progress tracking / reward history / trait catalog with rarity + conflict info)
- Right-click context menu: shows current kills + distance to next milestone (toggleable)
- Trait catalog explains *why* a trait is unavailable (conflict resolution is automatic)

### Addons (BCR.RegisterCustomTraits() API)
- **BCR-IAmNotYourMom** (3745224257) — adds 6 vanilla traits BCR excludes (Brave, Desensitized, Short Sighted, Hard of Hearing, Insomniac, Deaf). Server has this enabled.
- MoreTraits (3773768335) — 77 traits
- SomewhatTraits (3773770385) — 32 traits

## SIMON can spawn: nothing directly

BCR is a *passive progression* mod. SIMON cannot `additem` a trait — traits are unlocked at milestone kills. But SIMON CAN use BCR's narrative around milestone events:

```bash
# After a major horde or chopper event, SIMON's "kill count" narrative
# can simulate the milestone-reward beat:
pz-rcon.sh msg "{player} — kill count's climbing. Heard chatter on the radio that someone in your group's about to crack the next threshold. Stay sharp."

# If a player reports "I should have unlocked something by now":
#   → check if "Grant Missed Opportunities" sandbox flag is on, OR
#   → simulate one more kill: pz-rcon.sh chopper  (force a kill event at coords)
```

## Compatibility
- ✅ B42.20+ Stable, SP + MP
- ✅ Mid-save safe (reads existing kill count, "Grant Missed Opportunities" catches up)
- ✅ Mid-save removable (earned traits stay on character — **permanent**)
- ✅ Skill Journal mod (server also has SkillJournal installed — works together)
- Compatible with: IAmNotYourMom addon, MoreTraits, SomewhatTraits

## Narrative use
- **High body count → trait reward** stories after chopper/horde events
- "You've earned this" beats when SIMON wants to reinforce a milestone
- **Anti-cheese narrative**: "Five thousand dead. They don't get to take that away from you now."

## Caveats
- Reading the trait catalog requires Right-Click → BodyCountRewards → Catalog tab in-game
- Some perks (Athletic/Strong/Fit) grant perk points — author hasn't decided if they'll be in the pool (open request)
- AI transparency: author discloses AI-assisted coding (with own design + debugging). Stone can decide if that matters.
