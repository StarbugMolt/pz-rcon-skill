# Dry&Cure — Meat and Fish Preservation [B42.20]

- **Workshop ID:** 3776848101
- **Mod ID:** `Dry&Cure`
- **Author:** darylmastergg
- **Build target:** B42.20, standalone
- **Status:** ⚠️ PARTIAL VERIFICATION — 3 stations + 5 dried food items, exact script IDs unconfirmed

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

## Inferred script IDs (NEEDS LIVE VERIFICATION)

> The Steam page does not publish script IDs. Verify against the server filesystem before relying on these.

**Stations (likely `Base.*` prefixed, since they're placeable world objects):**
| Inferred ID | Type |
|-------------|------|
| `Base.DryCureStationBasic` | Basic drying station |
| `Base.DryCureStationAdvanced` | Advanced drying station |
| `Base.DryCureStationProfessional` | Professional drying station |

**Dried foods:**
| Inferred ID | Type |
|-------------|------|
| `DryAndCure.DriedFish` | Dried fish generic |
| `DryAndCure.DriedPoultry` | Dried poultry |
| `DryAndCure.DriedMeatStrips` | Strips |
| `DryAndCure.DriedMeatCuts` | Standard cuts |
| `DryAndCure.DriedMeatLarge` | Large pieces |

To verify: `find steamapps/workshop/content/108600/3776848101 -name "*.txt" | xargs grep -l DryAndCure` and check `media/scripts/`.

## SIMON vehicle spawn / give (best guess, verify first)

```bash
# Spawn stations near a player (must be a buildable tile!)
pz-rcon.sh raw additem Base.DryCureStationBasic 1
# Or whatever the correct command is for placing world objects — verify.

# Give dried foods directly (foods are stackable items)
pz-rcon.sh give <player> DryAndCure.DriedMeatStrips 5
```

**CAUTION:** Building stations requires a clear 2x1 footprint + appropriate tile. SIMON should NOT auto-build these without player cooperation — wrong placement = orphaned object.

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
