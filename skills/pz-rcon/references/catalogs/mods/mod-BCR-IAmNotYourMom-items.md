# BCR-IAmNotYourMom — Body Count Rewards Addon ("I am not your mom")

- **Workshop ID:** 3745224257
- **Mod ID:** `BCR-IAmNotYourMom`
- **Author:** Lenniitsch (open source, MIT, addon reference impl)
- **Build target:** B42.19+ Stable, SP + MP
- **Status:** ✅ VERIFIED — addon only, no new items
- **Requires:** `BCR` (Body Count Rewards) loaded first

## What it adds

Adds 6 vanilla traits to BCR's reward pool that the base mod excludes by default (for "lore-friendly, balanced selections"). This addon is "anything goes — you decide."

### 6 traits added to the BCR pool

**Positive (earnable):**
- **Brave** — fear reduction, can suppress panic moodles
- **Desensitized** — reduces horror/sadness moodles from zombie kills

**Negative (removable):**
- **Short Sighted** — reduces long-range visibility/sight cone
- **Hard of Hearing** — reduces sound detection radius
- **Insomniac** — slower sleep recovery, can't nap as effectively
- **Deaf** — no audio detection (extreme)

Each trait has its own toggle in `BodyCountRewards - Addon Traits` sandbox page.

## SIMON can spawn: nothing directly

BCR-IAmNotYourMom doesn't add items, scripts, or loot. It's a code-only addon that hooks into BCR's `BCR.RegisterCustomTraits()` API to register the 6 traits in the reward pool. SIMON doesn't grant these traits directly — players earn them via milestone kills.

**Use case for SIMON:** the SAME narrative beats as BCR (see mod-BCR-items.md) plus:
- "Lost something on the way? — Yeah, well, that's on the way out. SIMON, OUT." (Deaf/Insomniac removal beat)
- "Brave enough now, are we?" (Brave earn beat — diegetic way to acknowledge player bravery during chopper events)

## Compatibility
- ✅ Requires BCR loaded first (without BCR this addon is a no-op)
- ✅ B42.19+ SP + MP
- ✅ Safe to remove (traits stay on character — permanent)
- ✅ No vanilla file overwrites
- Serves as the **reference implementation** for other addon devs using BCR.RegisterCustomTraits()

## Known issues
- **Removing Short Sighted doesn't refresh visual effect until reload** — PZ limitation, not BCR bug. If a player reports this, suggest quit-to-menu and back in.

## Developer notes (for Stone if writing a future addon)
```lua
BCR.RegisterCustomTraits({
  trait_data = { ... },
  exclusions = { ... },
  sandbox_namespace = "MyAddonTraits"
})
```
Traits merge automatically into reward pools, stats catalog, and history. Verify with `BCR.RunThirdPartyTests()`.
