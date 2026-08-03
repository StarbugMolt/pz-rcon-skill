# BreakBigRocks - Break Big Rocks (Enhanced Mining & Crafting)

Workshop ID: 3538602374
Mod ID: BreakBigRocks
Enabled on server: yes (B42, any map, MP-safe)

Right-click any large rock → "Extract Rocks". Mining consumes endurance, awards Strength / Maintenance / Masonry XP, degrades tools. Pickaxes can be assembled from vanilla parts (Pickaxe Head + Handle). Carving tools (Stone Chisel, Metalworking Chisel, Stone Drill) work for limited mining with a hammer.

## Items

**No new item-prefix to `additem`.** Drops are vanilla items — `Base.Stone2`, plus rare drops:
- Flint
- Iron Ore
- Large Stone
- Iron Bloom
- Aluminum Fragments
- Copper Ore
- Flat Stone
- Stone Blocks
- Steel-related fragments

All rare drops are sandbox-configurable.

## Tool compatibility (consumes endurance, drops stone)
- Sledgehammer (all variants)
- Pickaxe / Forged Pickaxe
- Stone Maul / Block Maul
- Long Stone Mace
- Carving tools + hammer (limited mining only)

## Notes
- Higher Strength = faster mining
- Improvised / carving tools consume significantly more endurance
- Tools degrade based on mining intensity
- Does NOT replace vanilla rocks or construction systems
- Server-authoritative (no client-side exploits)
- Lightweight, designed for long-term survival playthroughs

## Sandbox tunables
- Stone Min / Max
- Individual rare drop chances
- Limited mining behavior
- Overall mining balance (SP / MP)

## Use Cases (SIMON voice)
- **"I need rocks"** supply requests — SIMON can grant `Base.Stone2` directly via `additem` to skip the grind
- **Iron Bloom / Iron Ore** drops = "rare find" flavor
- **Mining expedition narrative**: SIMON can stage a mining-run story with `gunshot` event (zombies heard them, they're compromised)
- **Pickaxe crafting arc**: vanilla parts → working pickaxe is a milestone — SIMON can frame as "real tool, real work"
- **Strength skill milestone** narrative: SIMON can grant tiny Strength XP for survivors who complete a quarry run (XP must stay small per skill policy)