# CorvusNVG — NVG [B42] (Night Vision Goggles)

- **Workshop ID:** 3769335201
- **Steam title:** "NVG [B42]"
- **Mod ID:** `CorvusNVG`
- **Author:** Corvus
- **Build target:** B42 only, multiplayer compatible
- **Updated:** 1 Aug 2026 (active dev)
- **Status:** ⚠️ PARTIAL VERIFICATION — new items exist but exact script IDs unconfirmed

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

> Steam page does not publish script IDs. Verify against `WorkshopItems/3769335201/contents/mods/CorvusNVG/media/scripts/` on the server before relying on these for `additem`.

| Inferred ID | Type |
|-------------|------|
| `CorvusNVG.NVGPVS7` | AN/PVS-7A NVG (head item) |
| `CorvusNVG.Surefire6C` | Surefire 6C flashlight |
| `CorvusNVG.Surefire6P` | Surefire 6P flashlight |
| `CorvusNVG.Headstrap` | Optional — base strap item |

If those don't resolve, search the script dir for `module CorvusNVG` or item files (`items_corvusnvg.txt`).

## SIMON can spawn / give (best guess, verify first)

```bash
# Verify item script exists in container first via:
# grep -r "CorvusNVG\.NVG" /path/to/steamapps/workshop/content/108600/3769335201/contents/mods/CorvusNVG/media/scripts/

pz-rcon.sh give <player> CorvusNVG.NVGPVS7 1
pz-rcon.sh give <player> CorvusNVG.Surefire6P 1
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
