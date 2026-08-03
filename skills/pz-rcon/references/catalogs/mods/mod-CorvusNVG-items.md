# CorvusNVG — NVG [B42] (Night Vision Goggles)

- **Workshop ID:** 3769335201
- **Steam title:** "NVG [B42]"
- **Mod ID:** `CorvusNVG`
- **Author:** Corvus
- **Build target:** B42 only, multiplayer compatible
- **Updated:** 2 Aug 2026 (mtime on server)
- **FTP folder:** `mods/NVG/42/media/scripts/generated/` (note: Steam folder is `CorvusNVG`, server folder is `NVG`)
- **Status:** ✅ VERIFIED — 3 items + 3 models extracted from `media/scripts/generated/NVGItems.txt` and `NVGModels.txt`

## What it adds

Wearable AN/PVS-7A night-vision unit on its own headstrap, plus two Surefire helmet-mounted flashlights on the same slot system.

### Items (3)
| Item | Notes |
|------|-------|
| AN/PVS-7A NVG (headstrap-mounted) | Native green NVG shader. Worn on **eyes slot** (not hat) — stacks with helmets. Has built-in IR illuminator sub-mode toggleable by keybind. Loot only (military containers, flashlight/lighting shops). No crafting recipe. |
| Surefire 6C (compact flashlight, helmet-mount) | Strap slot, for when you don't need full NVG |
| Surefire 6P (brighter/longer range, helmet-mount) | Same |

### Sandbox options
- Vignette darkness (0–50%, 6 mask levels)
- NVG spawn rate in military containers / flashlight shops

### Interactions
- Switch off NVG → short fade-to-black (eyes re-adapting)
- Goggles sit **flipped up** on strap when off, flip down when on
- Custom activate/deactivate sound effects

## Inferred script IDs (NEEDS LIVE VERIFICATION)

> ✅ RESOLVED 2026-08-03 — verified via FTP. All 3 items are declared in `media/scripts/generated/NVGItems.txt` under `module NVG`. The script prefix is `NVG.`, not `CorvusNVG.` (the mod's internal namespace is shorter than the workshop ID).

| Script ID | Source | Type |
|-----------|--------|------|
| `NVG.Surefire6C` | `media/scripts/generated/NVGItems.txt` | Surefire 6C flashlight (15m range, dim) |
| `NVG.Surefire6P` | `media/scripts/generated/NVGItems.txt` | Surefire 6P flashlight (18m range, brighter) |
| `NVG.ANPVS7A` | `media/scripts/generated/NVGItems.txt` | AN/PVS-7A NVG (headstrap-mounted, eyes slot) |
| `NVG.ANPVS7Strap` | `media/scripts/generated/NVGItems.txt` | Eyewear strap item (accessory) |

> **RCon note:** `pz-rcon.sh give <player> ANPVS7A 1` accepts the bare name (the RCon wrapper strips the `NVG.` prefix automatically). If it fails, use the full prefix `NVG.ANPVS7A`.

## SIMON can spawn / give

```bash
pz-rcon.sh give <player> ANPVS7A 1
pz-rcon.sh give <player> Surefire6P 1
pz-rcon.sh give <player> Surefire6C 1
pz-rcon.sh give <player> ANPVS7Strap 1
```

## Narrative use

- **Military loot arcs**: NVGs are MILITARY-tier loot. Story beats should put them in army lockers / safehouses, not gas stations. SIMON: *"Found a set of NVGs in an army crate. Even has the IR illuminator. Just don't shine that at friendlies — the dead WILL notice."*
- **Stealth night missions**: Bypasses the "I can't see anything" problem after dark.
- **IR trade-off**: IR illuminator is a real light source, visible to zombies — same trade-off as any flashlight, just fainter.

## Caveats
- IR illuminator is visible to zombies. Real light source, faint but present.
- Build 42 only. No B41 support.
- B42.20 has documented AnimNode parse error (`steamapps/workshop/content/108600/3769335201/mods/nvg/42/media/animsets/player/actions/attachitem_nvg.xml` — author flagged a known missing-file bug, looking into it).
- If `additem` fails, fall back to vanilla flashlight/headlamp (`Base.Headlamp`, `Base.Flashlight`) for narrative continuity.
