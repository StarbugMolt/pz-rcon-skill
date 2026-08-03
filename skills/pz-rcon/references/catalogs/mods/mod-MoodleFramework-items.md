# MoodleFramework — Pure Framework (no spawnable content)

- **Workshop ID:** 3396446795
- **Mod ID:** `MoodleFramework`
- **Build target:** B41 + B42 MP
- **Status:** ✅ VERIFIED — framework only, no items, no scripts

## What it does

A Lua require library that makes it easy for OTHER mods to add moodles.

```lua
require "MF_ISMoodle"
MF.createMoodle("*")           -- * = moodle name
MF.getMoodle("*",playerNum):setValue(myValue)  -- 0.0..1.0
```

Modders add:
1. A 30x30 PNG under `media/ui/`
2. Translation entries under `media/lua/shared/Translate/EN/Moodles_EN.txt`
3. A `MF.createMoodle(*)` call in their mod

This mod contributes none of the above — it just provides the runtime. So **SIMON cannot spawn anything from MoodleFramework directly.**

## Why it's on this server

At least one enabled mod uses it. Common dependents (from the Steam page's "Known mods using this" list):
- More Traits, Dynamic Traits and Expanded Moodles
- Auto Sewing, ProteinsMoodle
- CannotAttackMoodle, SixthSense, Excrementum
- MoodleCombatSpeed, Nuclear Winter, MoodleSanity
- More Smokes, Serious Cigarette Withdrawal
- More Moodles, Out of Breath Moodle, Rick's MLC Concussion
- General Anxiety, MoodleDog
- Evolving Traits World (ETW)
- Weather Moodles, Seismic Events
- (full list too long to enumerate — see Steam workshop page)

On THIS server: enables custom moodles via consuming mods (likely `DBNO_DownButNotOut` wound moodle, possibly others).

## SIMON narrative use

If a player reports a moodle icon that vanilla doesn't show, it's a modded moodle riding on this framework. SIMON can mention "the framework" but cannot grant the moodle via RCON — moodles are player-state derived from underlying conditions.

## Caveats
- ❌ Not tested with split-screen (per author — should work since last update but unconfirmed).
- ⚠️ If you see oscillation/visual oddities on moodles, perf-dependent — adjust via sandbox.
- Sandbox option: "white reference color" (default ON) for colorblind accessibility.
- Sandbox option: deactivate specific display blocks to avoid mod conflicts.
