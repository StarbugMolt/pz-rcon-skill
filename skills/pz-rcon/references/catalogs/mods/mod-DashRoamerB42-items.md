# DashRoamerB42 — Dash Roamer Cabover RV [B42.20 BETA]

- **Workshop ID:** 3775809123
- **Mod ID:** `DashRoamerB42`
- **Build target:** B42.20, currently BETA
- **Status:** ✅ VERIFIED — single vehicle, ID confirmed
- **Replaces / supersedes:** original DashRoamer mod (don't enable both)

## What it adds

Standalone B42.20 port of Moderator Of Tacos' Dash Roamer cabover RV. Same vehicle ID `Base.DashRoamer` so other interior-mesh mods (e.g., Arcadia RV Interiors) work without needing their compatibility patches.

### Vehicle (1)
- `Base.DashRoamer` — Cabover RV (snub-nose semi-style, drives like a truck cab-over)

### Features (per Steam page)
- B42-native vehicle parts (uses the standard B42 chassis swap system)
- Textured wheels
- Corrected entry points (entry/exit animations on correct door sides)
- Vehicle-scoped static-door compatibility safeguard (won't clip through walls)
- Moderate natural spawning (sandbox-configurable spawn rate)

## SIMON vehicle spawn

```bash
# Direct script spawn (from Steam page, no Mod ID prefix needed)
pz-rcon.sh vehicle Base.DashRoamer "<player>"

# The pz-rcon.sh vehicle wrapper handles "addvehicle <script> <user>"
```

⚠️ **Same caveat as the fifth-wheel RV (`Base.TrailerRV_B`)**: cabover RV is large. Warn the player to be outside and clear of obstacles before spawning.

## Compatibility
- ✅ Arcadia RV Interiors via preserved `Base.DashRoamer` identity — old `DashRoamerRVInterior` patch NOT needed (and may conflict)
- ❌ **Do NOT enable original DashRoamer mod at the same time** — duplicate script ID will cause load failure
- Compatible with PROJECTRVInterior42 (different vehicle family) and other vehicle mods

## Narrative use (SIMON voice samples)
- **Convoy reward beat**: *"Got eyes on a Dash Roamer, parked at the old warehouse on the south side. Cabover rig — fast on the highway, hauls like a truck. If you want walls that MOVE, now's your shot."*
- **Mobile command promotion** (long-term habitation reward)
- **"Truck-stop safe house" beat** — combine with ProjectArcade for arcade-night RP

## Caveats
- Currently BETA — author may iterate on stats/parts. Watch Steam for updates.
- Combines nicely with `PROJECTRVInterior42` interior meshes for vanilla vehicle bases if you also want interior walkability.
- Don't load alongside legacy `DashRoamer` (pre-B42 mod, different folder).
