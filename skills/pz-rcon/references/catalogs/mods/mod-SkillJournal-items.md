# SkillJournal — Skill Recovery Journal [B42.20]

- **Workshop ID:** 3776641628
- **Mod ID:** `SkillJournal`
- **Author:** lait
- **Build target:** B42.20.0+ (modversion 1.0.0)
- **FTP folder:** `mods/SkillJournal/42/media/scripts/{items,recipes}/`
- **Status:** ✅ VERIFIED — script ID extracted from `mods/SkillJournal/42/media/scripts/items/item_SkillJournal.txt`

## What it adds

A craftable bound journal that acts as a **save point for skills**. Write your progress into it; read it back on your next character to recover what you had recorded.

### Items (1, craftable)
- **Skill Journal** — `item SkillJournalBook` (module `Base`). Crafted from a notebook, glue, leather strips, and thread.

### Mechanics
- **"Record skills in journal"** — writes current XP, learned recipes, and zombie kill count into the book. Requires a pen or pencil.
- **"Recover skills from journal"** — read on next character.
- Anything earned *after* the last write is gone. Write often.

### Rules (per Steam page)
- Never lowers a skill and never pushes one past what was written. It only fills the gap.
- Traits and professions are NOT saved.
- Skills, recipes, and kill count are saved.
- **MP-scoped:** a journal can only be read by the character who wrote it. No reading someone else's book.

### Sandbox options
- Skill recovery percentage (default 100)
- Recover zombie kill count (default ON)
- Recover learned recipes (default ON)

## Inferred script IDs (NEEDS LIVE VERIFICATION)

> ✅ RESOLVED 2026-08-03 — verified via FTP. The mod is lua-only; the item is declared in `item_SkillJournal.txt` as `module Base { item SkillJournalBook { ... } }`. The Lua event hook fires on read/write under the author's `SkillJournal` namespace; the gameplay item is `Base.SkillJournalBook`.

| Script ID | Source | Type |
|-----------|--------|------|
| `Base.SkillJournalBook` | `media/scripts/items/item_SkillJournal.txt` | The craftable journal item |
| `Base.BindSkillJournal` | `media/scripts/recipes/recipe_SkillJournal.txt` | The craft recipe (Binds the journal) |

## SIMON can spawn / give

```bash
# Give the craftable book to a player
pz-rcon.sh give <player> SkillJournalBook 1

# Force a "write" tick (player must still have pen/pencil in inventory)
pz-rcon.sh call LuaEventSkillJournal_Write <player>
```

> Note: `pz-rcon.sh give <player> SkillJournalBook 1` is what worked in FTP verification. The earlier `SkillJournal.Journal` guess was wrong — there is no `SkillJournal.*` namespace in the script files; the mod reuses the `Base.` prefix.

## Compatibility
- ✅ B42.20, standalone, no dependencies
- ✅ Works with **BCR** ("Works with Skill Recovery Journal" — BCR's compatibility note) — together they create a multi-layered death-resilience system: BCR rewards traits at kills, SkillJournal preserves skills at death
- MP-safe (per-character journals)

## Narrative use (SIMON voice samples)
- **"Plan for the next life" beat** (after a chopper event, before a player enters a dangerous zone): *"Before you go in — write it down. Tape it to your belt if you have to. We're running out of 'next lives' to spend on this place."*
- **Permadeath loot-cache arc** integrates with DBNO_DownButNotOut: DBNO deaths leave a Death Cache, but a SkillJournal in the player's inventory has their skills. SIMON narrates the journal as the *real* legacy vs. the gear.
- **Veteran player handoff**: SIMON can prompt a multi-session player to "Record skills in journal" before risky missions. Then narrate SkillJournal recovery as "the notebook held."

## Caveats
- Character-creation-time keys/items keep default weight (per ZeroWeightKeys_B42 caveat if also running that mod)
- Requires a pen/pencil to record
- Player must manually write often — easy to forget; SIMON can prompt as a diegetic beat
