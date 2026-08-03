# 87fordB700 — '87 Ford B700 / F700 Trucks [B41/B42]

- **Workshop ID:** 3110911330
- **Mod ID:** `87fordB700`
- **Author:** KI5 (commission for Project Apocalypse Community)
- **Build target:** B41.78.16 (SP+MP), B42.12 (SP), B42.13+ (SP+MP)
- **Status:** ✅ VERIFIED — vehicle IDs published on Steam page

## What it adds

Six heavy Ford chassis variants. School Bus is the most iconic, but the armored/SWAT variants are the real survival-game gold.

### Vehicles (6)
| Variant | Script ID | Passengers | Notable |
|---------|-----------|-----------|---------|
| School Bus | `87fordB700school` | 14 + 1 driver | Iconic American school bus |
| Military Bus | `87fordB700military` | 14 + 1 driver | Camo |
| Prison Bus | `87fordB700prison` | 14 + 1 driver | Reinforced cage look |
| SWAT Van | `87fordF700swat` | 8 + 1 driver | Quick-response tactical |
| Armored Bank Truck | `87fordF700bank` | 2 + 1 driver | Vault-door aesthetic |
| Box Truck | `87fordF700box` | 2 + 1 driver | Cargo hauler |

### Common features (all 6)
- Fully animated hood, trunk, doors, windows
- **Visible interior + character** with improved enter/exit/aim animations
- 3D parts removable + placeable in the world
- Craftable extras: bumpers, window armor, roof racks, etc.
- Multiple texture variations per variant
- 2-tiered armor (2 front bumpers, 2 armor sets) — protect engine, headlights, windows, doors
- Special sandbox spawn option for natural spawning (Kentucky police/military sites)
- 6 interchangeable parts; most are craftable
- Can tow and be towed
- Not recolorable

## SIMON vehicle spawn

```bash
pz-rcon.sh vehicle 87fordB700school    "<player>"
pz-rcon.sh vehicle 87fordB700military  "<player>"
pz-rcon.sh vehicle 87fordB700prison    "<player>"
pz-rcon.sh vehicle 87fordF700swat      "<player>"
pz-rcon.sh vehicle 87fordF700bank      "<player>"
pz-rcon.sh vehicle 87fordF700box       "<player>"
```

Same warning as the RVs: large vehicles, spawn the player OUTSIDE first or they'll spawn inside the chassis. SWAT van and Bank Truck have the best armor for convoy-escort stories.

## Narrative use (SIMON voice samples)
- **School bus evac**: *"Half the survivors in one rig. Engine's cold but you've got forty seats. Convoy order: bus first, then escort, then the box truck with all your loot. Move."*
- **Armored bank truck drop** (post-chopper event): *"Found a bank truck intact at the old branch. Vault door's still sealed. If you want something that LASTS, this is the rig."*
- **SWAT van raid**: *"Tactical van. Side windows have protection mods. You've got maybe three more breaches before the armor starts cracking. Get in, get out."*

## Compatibility
- ✅ B41.78.16 (SP+MP), B42.12 (SP), B42.13+ (SP+MP)
- ✅ Mid-save safe (works in current saves, just enable in load menu)
- Compatible with bikinitools spawn helper (2634426926)
- **Mod author's other mods** are linked from their Steam profile — likely KI5 trailers/containers ecosystem

## Caveats
- 7KB file size per variant — needs Workshop download
- Large/heavy — "don't expect race car performance" (author)
- Armor protection is per-part; not invulnerable
- Adds a LOT of new parts to the world once placed (storage management)

## Companion mods (server ecosystem)
- `damnlib` (server has it) — KI5 ecosystem base dependency
- `KI5trailers` — same author family
- Use SWAT van / Bank Truck as the **SIMON "convoy escort" reward** at end of major story arcs — these mods together enable an entire military/law-enforcement vehicle collection on this server.
