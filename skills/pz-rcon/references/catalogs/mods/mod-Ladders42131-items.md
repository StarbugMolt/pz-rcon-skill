# Ladders42131 — Ladders?! B42.20 SP/MP (Unofficial by nyamops)

- **Workshop ID:** 3629835761
- **Steam title:** "Ladders?! B42.20 SP/MP (Unofficial)"
- **Mod ID:** ⚠️ **`Ladders4220`** (NOT `Ladders42131` — see "Naming note" below)
- **Author:** nyamops (unofficial B42.20 update of co`'s original)
- **Build target:** B42.20 singleplayer AND multiplayer
- **Status:** ⚠️ PARTIAL VERIFICATION — collapsible ladder craftable, exact script ID unconfirmed

## What it adds

Restores ladder-climbing functionality in B42.20. Hold `E` to climb down. Must be in the same tile and facing the ladder.

> **⚠️ Re-enable notice from author:** *"PLS re-enable the mod in your game/server"*. After PZ patches you'd need to disable+enable to refresh.

## Items (1, craftable)
- Collapsible ladder — recipe only (no loot spawn by default)

## Inferred script IDs (NEEDS LIVE VERIFICATION)

> The Steam name is "Ladders42131" but the actual Mod ID inside the mod folder is `Ladders4220`. Verify both on the server filesystem before relying on these.

| Inferred ID | Notes |
|-------------|-------|
| `Ladders4220.CollapsibleLadder` | Primary item |
| `Ladders4220.Ladder` | Alternate (verify) |

To verify: `find steamapps/workshop/content/108600/3629835761 -name "*.txt" | xargs grep -l Ladders4220`

## SIMON can spawn / give (best guess, verify first)

```bash
pz-rcon.sh give <player> Ladders4220.CollapsibleLadder 1
```

## Caveats
- ⚠️ **"This is a replacement mod. Do NOT enable original mod with it"** — the original B41 "Ladders?!" mod (Workshop 2737665235) MUST NOT be enabled alongside.
- ⚠️ **Incompatible with "gun's elevator mod"** (per author comment).
- ⚠️ **Ladders will not function if there's a staircase above the ladder tile** — known mod-conflict issue. If survivors report "can't climb down," check for staircase overlap.
- B42 ladder-climb control: `Hold E + direction toward ladder` to climb down (some users report a press-E-alone bug — direction input is needed).
- Requires player to be in same tile as ladder, facing it.

## Narrative use

Gives survivors roof access, fence-scaling, second-story entry. Story beats:
- "That fence isn't getting over. Find a ladder."
- "Rooftop sniping position — climb up."
- Restores the lost B41 ladder-climbing for B42.20.

## Naming note

Server's `Mods=` line has the Steam workshop folder name `Ladders42131`. The mod's internal `Mod ID` is `Ladders4220` (since it's a B42.20 update of a B41 mod). This is why the .env shows `Ladders42131` but script IDs are `Ladders4220.*` — different namespacing for folder vs mod ID.
