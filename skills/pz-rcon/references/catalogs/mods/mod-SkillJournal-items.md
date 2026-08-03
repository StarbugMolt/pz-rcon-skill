# SkillJournal — Skill Recovery Journal [B42.20]

- **Workshop ID:** 3776641628
- **Mod ID:** `SkillJournal`
- **Author:** (per Steam page)
- **Build target:** B42.20, standalone (no dependencies)
- **Status:** ⚠️ PARTIAL VERIFICATION — craftable item, exact script ID unconfirmed

## What it adds

A craftable bound journal that acts as a **save point for skills**. Write your progress into it; read it back on your next character to recover what you had recorded.

### Items (1, craftable)
- **Skill Journal** — bound journal. Crafted from a notebook, glue, leather strips, and thread.

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

> The Steam page does not publish script IDs. Verify against the server filesystem before relying on these for `additem`.

| Inferred ID | Type |
|-------------|------|
| `SkillJournal.Journal` | The craftable journal item |
| `SkillJournal.BoundJournal` | Alternate (verify) |

To verify: `find steamapps/workshop/content/108600/3776641628 -name "items_skilljournal*" -o -name "*journal*"` and check `media/scripts/`.

## SIMON can spawn / give

```bash
# Verify item script exists in container first
grep -r "SkillJournal\.Journal" /path/to/steamapps/workshop/content/108600/3776641628/contents/mods/SkillJournal/media/scripts/

pz-rcon.sh give <player> SkillJournal.Journal 1
```

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
