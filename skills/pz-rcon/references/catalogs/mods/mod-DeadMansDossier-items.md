# DeadMansDossier - Dead Man's Dossier [B42][MP]

Workshop ID: 3675740871
Mod ID: DeadMansDossier
Enabled on server: yes (B42 MP — 42.1.17+)

Collectible objective system. Zombies wearing specific outfits drop torn dossier pages; assemble a dossier; follow coordinates to a hidden supply stash. **Five tiers**: Police, Military, Medical, Firefighter, Ranger. Lore text on every page (internal memos, classified reports, incident logs).

## Tier Reward Tables (vanilla — for SIMON flavor)

| Tier | Pages | Reward flavor |
|------|-------|---------------|
| **Police** | 2 | Pistols, shotguns, ammo, police clothing, bulletproof vest, holster, walkie-talkie |
| **Military** | 3 | Assault rifles, pistols, magazines, scopes, ammo, camo gear, military backpack, ALICE webbing, bulletproof vest |
| **Medical** | 2 | Antibiotics, bandages, suture needles, painkillers, surgical tools, scrubs |
| **Firefighter** | 2 | Axe, sledgehammer, crowbar, fireman gear, blow torch, bolt cutters, welding mask |
| **Ranger** | 2 | Hunting rifle, shotguns, knife, hatchet, scopes, ranger clothing, compass, rope, trap box |

## ⚠️ ZOMBIE CURE CROSS-MOD SUPPORT (KEY FOR SIMON)

> Military stash caches can drop **X-Virus** and Medical stash caches can drop **Knox Antidote**. Works with or without those mods installed — if the mod isn't active, the item is silently skipped.

This means SIMON's **"anti-zombie serum" rescue narrative** can be backed by real in-game items when those mods are active on the same server. (See also: `ResearchLabInternProfession` = Zombie Virus Vaccine, where the cure is actually synthesized.)

## Custom Rewards (admin config)
- Config auto-generated at `Zomboid/Lua/DeadMansDossier_Rewards.cfg` on first server start
- Edit to add/remove items & drop chances
- Sandbox option to enable custom rewards
- Format example:
  ```
  [Police]
  Base.Pistol = 0.40
  Base.Shotgun = 0.25
  ```
- Cross-mod items work: `SomeMod.CustomWeapon = 0.10`

## Sandbox tunables (admin)
- Page drop chance per tier: High (30%) / Normal (15%) / Low (8%) / Very Low (3%)
- Container spawn rate
- Stash reward rarity multiplier (Generous 2x / Normal 1x / Scarce 0.5x / Minimal 0.1x)
- Stash proximity radius (5–50 tiles, default 15)

## Notes
- Mid-save compatible (safe to add to existing saves).
- Map markers persist across saves, toggleable on map screen.
- Right-click page → "Assemble Dossier" → progress bar → coords revealed → colored map marker.

## Use Cases (SIMON voice)
- **"I got a page" transmission arc** — survivors radio in when they find dossier pages
- **Tier-by-tier story escalation**: Police first → Military → Medical (cure-related) → Firefighter → Ranger
- **Assemble-the-dossier group quests**: SIMON tracks who's holding which pages and broadcasts when the group can assemble
- **"Hidden supply stash" reveals** — SIMON can narrate the map marker as "I'm picking up coordinates, hold on..."
- **Lore drops**: each page is a narrative fragment — SIMON can quote them on-air as "intercepted transmission"
- **Cross-mod cure narrative**: when Medical tier completes, the dropped *Knox Antidote* is the cure payoff