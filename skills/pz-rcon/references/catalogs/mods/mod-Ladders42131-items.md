# Ladders42131 — Ladders?! B42.20 SP/MP (Unofficial by nyamops)

- **Workshop ID:** 3629835761
- **Steam title:** "Ladders?! B42.20 SP/MP (Unofficial)"
- **Mod ID:** ⚠️ **`Ladders4220`** (NOT `Ladders42131` — see "Naming note" below)
- **Author:** nyamops (unofficial B42.20 update of co`'s original)
- **Build target:** B42.20 singleplayer AND multiplayer
- **FTP folder:** `mods/Ladders/{common,42.16,42.20}/` (note: Steam folder is `Ladders42131`, server folder is `Ladders`)
- **Status:** ✅ VERIFIED — 4 items + 2 models + 3 recipes extracted from `mods/Ladders/common/media/scripts/items/items_ladder.txt`
- **Filename note:** The mod is published under workshop folder `Ladders42131` but the internal `mod.id` is `Ladders4220` (B42.20 version-suffix). Both confirm the dual naming.

## What it adds

Restores ladder-climbing functionality in B42.20. Hold `E` to climb down. Must be in the same tile and facing the ladder.

> **⚠️ Re-enable notice from author:** *"PLS re-enable the mod in your game/server"*. After PZ patches you'd need to disable+enable to refresh.

## Items (4 declared, 1 craftable variant)

| Script ID | Type | Notes |
|-----------|------|-------|
| `Base.SteelLadder` | `base:moveable` | Static steel ladder, weight 20, Furniture category |
| `Base.WoodenLadder` | `base:moveable` | Static wooden ladder, weight 20, Furniture category |
| `Base.CollapsibleLadder` | `base:moveable` | Collapsible ladder, weight 10, craftable via `CraftCollapsibleLadder` |
| `Base.CollapsibleLadder_Packed` | `base:normal` | Packed ladder (carried), weight 5, HelmetFlashlight attachment slot |

## Craft recipes (3)

| Recipe | Inputs | Output | Time |
|--------|--------|--------|------|
| `Base.CraftCollapsibleLadder` | screwdriver + 4 Screws + 4 IronBar/SteelBar | `Base.CollapsibleLadder_Packed` | 50 ticks, Maintenance:2 |
| `Base.PackCollapsibleLadder` | `Base.CollapsibleLadder` | `Base.CollapsibleLadder_Packed` | 50 ticks |
| `Base.UnpackCollapsibleLadder` | `Base.CollapsibleLadder_Packed` | `Base.CollapsibleLadder` | 50 ticks |

> The script declaration is `module Base { ... }` — NOT `module Ladders4220`. So the actual game item prefix is `Base.CollapsibleLadder`, not `Ladders4220.CollapsibleLadder`. The `Ladders4220` name is the mod's namespace used internally for the `tiledef` and craft category, not the item prefix.

## SIMON can spawn / give

```bash
# Give the packed ladder (carried item)
pz-rcon.sh give <player> CollapsibleLadder_Packed 1

# Give the unpacked ladder (world object)
pz-rcon.sh give <player> CollapsibleLadder 1

# Force-spawn a static ladder at a tile (admin-lifecycle only)
pz-rcon.sh addobject CollapsibleLadder <x> <y> <z>
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
