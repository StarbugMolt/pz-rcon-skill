# Dry&Cure — Meat and Fish Preservation [B42.20]

- **Workshop ID:** 3776848101
- **Mod ID:** `Dry&Cure`
- **Author:** darylmastergg
- **Build target:** B42.20, standalone
- **FTP folder:** `mods/Dry & Cure/` (with spaces — URL-encode as `Dry%20%26%20Cure`)
- **Status:** ✅ VERIFIED 2026-08-03 (post-restart) — script IDs extracted from `mods/Dry & Cure/42/media/scripts/DC_*.txt`

## What it adds

Three craftable drying stations for preserving fish, poultry, and meat. Long-term survival via dehydration, with balanced nutrition math.

### Items (3 stations + 5 dried foods = 8 new items)

**Drying Stations (placeable, 2x1 footprint, rotatable):**
| Station | Capacity | Time | Carpentry | Notes |
|---------|----------|------|-----------|-------|
| Basic Drying Station | 6 pieces | 72h | L1 | Rain/humidity/temp affected |
| Advanced Drying Station | 12 pieces | 48h | L3 | Rain/humidity/temp affected |
| Professional Drying Station | 20 pieces | 24h | L5 | Weather-protected, stable rate |

**Dried Food Outputs (5 categories):**
- Dried Fish (custom textures, 3D models, hand models)
- Dried Poultry
- Dried Meat Strips
- Dried Regular Meat Cuts
- Dried Large Meat Pieces

All 5 foods can be added to salads.

### Accepted inputs (vanilla proteins)
- Fish: small / medium / large / legendary / fillets
- Poultry: chicken / turkey fillets / legs / small bird / whole chicken / whole turkey
- Rabbit / rodent / frog meat
- Beef / pork / venison steaks, chops, mutton chops
- Rotten and frozen ingredients are REJECTED by Build 42's standard crafting rules

### Nutrition math (balanced per author)
- Calories: **105%** of original (dehydration concentrates)
- Protein: **108%** of original
- Fat + carbs: preserved
- Hunger reduction: 105% of original
- Weight: ~45% of original (significant weight reduction!)
- Fish size preserved (small fish ≠ large fish output)
- **Calculated per complete batch** — prevents multi-output exploit

### Construction costs
| Station | Logs | Branches | Twine | Nails | Extras |
|---------|------|----------|-------|-------|--------|
| Basic | 2 | 0 | 6 | 4 | hammer + saw |
| Advanced | 2 | 4 | 12 | 8 | hammer + saw |
| Professional | 4 | 12 | 24 | 24 | + 1 tarp, hammer + saw |

Tools retain durability after construction (light loss).

### Visual states
Each station has 3 art states: empty / processing / finished. Professional also has a roof + ground shadow (weather protection visual cue).

## Verified script IDs (2026-08-03)

> ✅ RESOLVED — server folder is now populated as `Dry & Cure` (with spaces, URL-encode as `Dry%20%26%20Cure`). All script IDs extracted from `mods/Dry & Cure/42/media/scripts/DC_*.txt`.

**Dried food items (module `DryCure`):**
| Script ID | Display name | Notes |
|-----------|----------|-------|
| `DryCure.DC_DriedFish` | Dried Fish | base:food, hunger -28, weight 0.30 |
| `DryCure.DC_PoultryStrip` | Dried Poultry | base:food, hunger -20, weight 0.20 |
| `DryCure.DC_LargeDriedMeat` | Dried Large Meat | base:food, hunger -45, weight 0.75 |
| `DryCure.DC_DryMeatStrip` | Dried Meat Strip | base:food, hunger -28, weight 0.26 |
| `DryCure.DC_DryMeatPiece` | Dried Meat Piece | base:food, hunger -60, weight 0.75 |

**Models (module `DryCure`):**
- `DryCure.DC_DriedFish_Model`, `DryCure.DC_PoultryStrip_Model`, `DryCure.DC_LargeDriedMeat_Model`, `DryCure.DC_DryMeatStrip_Model`, `DryCure.DC_DryMeatPiece_Model`

**Craft recipes (module `Base`, 15 total — 5 protein types × 3 station tiers):**
- Basic: `Base.DC_Basic_DryFish`, `DC_Basic_DryPoultry`, `DC_Basic_DryLargeMeat`, `DC_Basic_DryMeatStrips`, `DC_Basic_DrySmallGame`
- Advanced: `Base.DC_Advanced_DryFish`, `DC_Advanced_DryPoultry`, `DC_Advanced_DryLargeMeat`, `DC_Advanced_DryMeatStrips`, `DC_Advanced_DrySmallGame`
- Professional: `Base.DC_Professional_DryFish`, `DC_Professional_DryPoultry`, `DC_Professional_DryLargeMeat`, `DC_Professional_DryMeatStrips`, `DC_Professional_DrySmallGame`

**Stations** are declared in `DC_Entities.txt` (module `Base`) and `DC_LegacyEntities.txt` — script IDs are `Base.DC_DryCureStationBasic`, `Base.DC_DryCureStationAdvanced`, `Base.DC_DryCureStationProfessional` (placeable world objects, 2x1 footprint).

> Note: script names differ from the Steam page's "Inferred IDs" — the module prefix is `DryCure.` (no ampersand, no spaces), not `DryAndCure.`. RCon's `give` typically accepts the bare name (the wrapper strips the prefix).

## SIMON can spawn / give

```bash
# Give dried foods directly (foods are stackable items)
pz-rcon.sh give <player> DC_DriedFish 5
pz-rcon.sh give <player> DC_PoultryStrip 5
pz-rcon.sh give <player> DC_LargeDriedMeat 3
pz-rcon.sh give <player> DC_DryMeatStrip 5
pz-rcon.sh give <player> DC_DryMeatPiece 3

# Spawn a station (placeable world object — requires buildable tile)
pz-rcon.sh addobject DC_DryCureStationBasic <x> <y> <z>
```

**CAUTION:** Building stations requires a clear 2x1 footprint + appropriate tile. SIMON should NOT auto-build these without player cooperation — wrong placement = orphaned object. Use `addobject` only after confirming the player has cleared and leveled the spot.

## Compatibility
- ✅ B42.20, no dependencies
- ✅ Compatible with **Meat Expansion 2.0**
- ✅ Uses Build 42 entity-crafting system (no legacy interface)
- ✅ Multiplayer-compatible (server validates batch construction)
- Translations: English, Spanish

## Narrative use (SIMON voice samples)
- **Late-summer preservation arc**: *"Fishing's good right now. If you've got the Carpentry, build yourself a drying station before the season turns. Three days and you've got jerky that'll outlast a winter."*
- **Big-game hunter arc**: *"Dropped a deer at the cabin. Don't waste it — get those steaks into a Pro Station before the flies do. Forty-five percent weight, hundred-five percent calories. That's survival math."*
- **Combined with SKITTLE_LongTermPreservation4220** (salt cure) and `SapphCooking_B42` (canning) → full preservation trio. SIMON can frame this as "the seasons are turning, time to lay down stores".

## Caveats
- Stations must be on dry ground; rain affects Basic+Advanced (Professional is weatherproof)
- Verifies protein via vanilla item scripts — rotten/frozen rejected
- 8 new items added to inventory — affects container loot UI mods (DAS, etc.)
- Empty + finished + processing states visible — players can see status at a glance
