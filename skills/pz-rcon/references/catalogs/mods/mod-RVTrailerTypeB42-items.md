# RVTrailerTypeB42 - Fifth-Wheel RV Trailer [B42.20]

Workshop ID: 3775310562
Mod ID: RVTrailerTypeB42
Mod folder: `RV_B`
Enabled on server: yes (B42.20, MP — *untested by author but code carried over from B41*)

A fifth-wheel RV trailer with a full walk-in interior: bedroom, bathroom (with washing machine), kitchen, and a living room with TV. Towable AND drivable (last-resort escape). 300-capacity storage trunk. 3 paint jobs (random per trailer).

## Vehicle Scripts

RCON syntax: `addvehicle "<script>" "<player>"`

| Script | Description |
|--------|-------------|
| `Base.TrailerRV_B` | Fifth-wheel RV trailer with walk-in interior. **Spawn at trailer parks, junkyards, traffic jams, police/fire spawns. Use V or right-click to enter interior.** |

## Spawn rates (worldgen — for ambient narrative)
- Trailer parks: 4%
- Junkyards / traffic jams: 8%
- Police / fire locations: occasional

## Notes
- The vehicle script is registered under `Base.TrailerRV_B` despite being a modded mod — confirmed in mod description.
- MP code carried over from B41; not formally tested in B42 by author. Spawn with care.
- Stand next to or sit in trailer, press **V**, choose "Enter the RV interior". To leave, right-click the floor inside.
- B42 bakes terrain into saves — **must add to a new save**. Old saves may show interior area incorrectly.
- Tows best behind pickups and vehicles with low rear; hooking may take a couple of tries.
- 3 paint jobs, randomly assigned per trailer.

## Use Cases (SIMON voice)
- **Convoy escort story beat**: "I've got eyes on a fifth-wheel, parked at the old trailer park off the highway. Engine's cold but the rig looks intact. If you want a roof that *moves*, now's the time."
- **Emergency mobile base reward** after a major event (chopper down, military convoy overrun). SIMON drops one near a player and warns them to get outside before spawning.
- **Long-term habitation arc**: survivors who hold down a base for weeks get the RV trailer as a "promotion to mobile command".
- **RV interior = safe room** for narrative beats: SIMON narrates "patching them up in the back of the rig" if a player is downed nearby — the *player* runs to the trailer on foot, SIMON does NOT warp.

## Companion mods
- Works alongside `[B42]Project RV Interior` for the *other* vehicles (PROJECTRVInterior42).