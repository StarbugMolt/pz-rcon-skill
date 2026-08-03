# InjuredZombiesStumble — Injured Zombies Stumble (B41/B42+)

- **Workshop ID:** 3648051123
- **Mod ID:** `InjuredZombiesStumble`
- **Build target:** B41.78, B42.13.0, B42.13.1, B42 STABLE, B42 MP
- **Status:** ✅ VERIFIED — pure behavior tweak, no items, no scripts

## What it does

When a zombie drops below a certain health % of max, it may **stumble and fall**. Pure animation/AI behavior tweak.

Factors that determine stumble chance:
- Remaining health
- Maximum durability
- Movement type
- Overall toughness (zombie variant)

## Sandbox options
- Base chance per check (modified by zombie stats)
- Health % threshold required to stumble
- Min cooldown between stumble attempts (per zombie)
- Max cooldown between stumble attempts (per zombie)

## SIMON can spawn: nothing

No new items. No new scripts. No new entities. SIMON cannot grant this directly — the behavior is hard-baked into zombie AI per the sandbox config.

## Narrative use (atmospheric)

This mod makes hordes *feel* more dangerous and lived-in. Zombies that are limping, crawling, dragging limbs — visual storytelling without new spawns.

Story beats:
- "That one in the back is limping. Finish it before it gets back up."
- "Stumblers. Means the horde's seen casualties. Means someone else didn't make it."
- Helps simulate "weary horde that took losses" — supports narrative arcs about a previous failed survivor attempt.

## Compatibility
- ✅ B41 + B42 singleplayer
- ✅ B41 multiplayer
- ⚠️ B42 multiplayer: author notes "I am currently unable to test multiplayer due to a personal issue/bug preventing me from playing MP on B42. In theory, it should work without problems. If anyone is able to test and confirm multiplayer behavior on B42, feedback is greatly appreciated. I was told that in fact, it works!"
- Compatible with **Bandits** mod (Workshop 3268487204).

## Caveats
- Multiplayer on B42 is *theoretically* working but author-unconfirmed — was told "in fact, it works" by a tester. Low-risk to use.
- Mid-save safe (added/removed without world reset).
- No performance impact — runs at low check frequency.
- Vanilla zombie systems — no conflicts with other addons.
