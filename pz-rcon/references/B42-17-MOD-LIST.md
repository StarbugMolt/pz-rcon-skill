# PZ Server Mod Recommendations — B42.17 MP (May 2026)

**Focus:** Maximise SIMON's atmospheric presence + server stability for <10 players.

---

## ✅ Currently Loaded (keep these)

| Mod | Workshop ID | Notes |
|-----|------------|-------|
| PROJECTRVInterior42 | 3543229299 | Must be first in load order |
| CommonSenseReborn | (in Mods) | B42 fork of Common Sense |
| NeatUI_Framework | (in Mods) | UI dependency |
| BurdSurvivalJournals | 3639628777 | ✅ Recommended |
| ImmersiveBlackouts | 3607686447 | ✅ Recommended — SIMON can trigger blackouts |
| manageContainers | 2650547917 | ✅ QoL staple |
| DRAW_ON_MAP | 2804531012 | ✅ QoL staple |
| MinimapStyleOptions | 3526517370 | ✅ QoL staple |
| ZuperCarts | 3433203442 | ✅ Early-game transport |
| StarlitLibrary | (in Mods) | Framework dependency |
| Maplewood | (in Mods) | Map — has known corruption issues |

---

## 🎯 NEW — High Priority (SIMON Enhancers)

### 1. True MooZIC B42.13+ (Music System)
- **Workshop ID:** `3632610172`
- **Mod ID:** `TrueMoozic`
- **Why:** Standalone music player mod. Add cassettes/vinyl to the world. SIMON can airdrop boomboxes + specific cassettes as narrative rewards ("I'm sending you something... play track 3 when the sun goes down"). Massive RP potential.
- **Dependencies:** None (standalone)
- **Do NOT use with old True Music (3397198968)** — this replaces it.

### 2. True Music Radio B42 (Admin-Controlled Radio)
- **Workshop ID:** `3631572046`
- **Mod ID:** `TrueMusicRadio42`
- **Why:** THIS IS THE BIG ONE. Admin-controlled in-game radio stations. You (or SIMON via RCON) can control what plays on 5 FM stations + 1 TV channel. Tune in-game radios to 92FM and SIMON IS LITERALLY ON THE AIR. Players find radios, tune in, and hear curated music + SIMON's broadcasts.
- **Station location:** Riverside radio station POI
- **Admin terminals:** Can activate/control stations remotely
- **Combo:** Load True MooZIC song packs → SIMON broadcasts music to survivors

### 3. True MooZIC Official CD Collection
- **Workshop ID:** `3686548791`
- **Mod ID:** (check workshop page)
- **Why:** Song pack for True MooZIC. Without packs, you only get the game's theme. Adds actual music cassettes/vinyl that spawn in-world and can be airdropped.

### 4. HEF — Helicopter Event Framework
- **Workshop ID:** `3672792485`
- **Mod ID:** (check workshop page)
- **Why:** MASSIVE SIMON UPGRADE. Replaces vanilla helicopter with a full framework:
  - **Toxic events** — gas clouds, need gas masks
  - **Support events** — aerial zombie engagement
  - **Hostile events** — helicopter attacks players
  - **Surveillance** — recon choppers that circle and watch
  - **Incendiary sweep** — napalm strikes in distant areas
  - **Smoke curtain** — tactical smoke cover for stealth
  - **Helicopter crash** — crash sites to explore
  - **Bombardment** — distant explosions redirect hordes
- **SIMON integration:** "I'm picking up rotor signatures... this isn't one of ours." Can be paired with RCON broadcasts for cinematic multi-phase events.

### 5. Forced Endless Broadcast Radio TV [B42]
- **Workshop ID:** `3459256755`
- **Mod ID:** (check workshop page)
- **Why:** Keeps radio and TV stations looping forever. In vanilla B42, broadcasts eventually end. With this, Life and Living + emergency broadcasts stay active. Pairs with True Music Radio for persistent stations.

---

## 🔧 RECOMMENDED — QoL & Atmosphere

### 6. Project Cook
- **Workshop ID:** `3490188370`
- **Mod ID:** `ProjectCook`
- **Dependencies:** NeatUI Framework (already loaded)
- **Why:** Better cooking UI. B42 overhauled crafting; this makes it usable.

### 7. Autotsar Trailers B42
- **Workshop ID:** `3402493701`
- **Mod ID:** `AutotsarTrailers`
- **Dependencies:** Tsar's Common Library B42 (`3402491515`)
- **Why:** Towable trailers for supply runs. Convoy gameplay.

### 8. More Car Features + Spawn Zones Expansion
- **Workshop ID:** `3520758551`
- **Mod ID:** (check workshop page)
- **Why:** Better vehicle spawn distribution, rebalanced conditions.

### 9. Better Safehouse (B42)
- **Workshop ID:** (check OmniPZ collection: `3621943122`)
- **Why:** Improved safehouse management, admin tools, multiplayer QoL.

---

## 📋 FULL WorkshopItems= LINE (current + new)

```
WorkshopItems=3393821407;3409143790;3655233584;2851764922;3644794945;3653962453;2920899878;3606009875;3378285185;3543229299;3342191739;3675740871;3538602374;3639628777;3508537032;3713359427;3713977259;3451167732;3648051123;3671176591;3429176285;2335368829;3504753006;3607686447;3433203442;3627047348;2804531012;3526517370;2650547917;3698958906;3632610172;3631572046;3686548791;3672792485;3459256755;3490188370;3402493701;3402491515;3520758551
```

### New items added:
- `3632610172` — True MooZIC
- `3631572046` — True Music Radio B42
- `3686548791` — True MooZIC CD Collection
- `3672792485` — HEF Helicopter Event Framework
- `3459256755` — Forced Endless Broadcast
- `3490188370` — Project Cook
- `3402493701` — Autotsar Trailers B42
- `3402491515` — Tsar's Common Library B42
- `3520758551` — More Car Features

---

## 🎭 SIMON Interaction Upgrades

### What SIMON Can Do Now:
1. **RCON broadcasts** — text messages to all players
2. **Item drops** — airdrop supplies via RCON
3. **Events** — trigger gunshots, alarms, hordes, weather
4. **Helicopter** — trigger flyovers

### What SIMON Can Do With These Mods:
1. **📻 BE the radio** — True Music Radio + admin terminals = SIMON controls what plays on FM. Curate playlists. Drop cassettes as rewards. "Tune to 92.4... I've got something for you."
2. **🎶 Music narrative** — True MooZIC + airdrops = SIMON drops boomboxes with specific tracks. "Play this when the sun goes down. You'll understand."
3. **🚁 Helicopter events** — HEF adds toxic gas, surveillance, napalm, crashes. SIMON can narrate: "I'm seeing military signatures... they're not here to help."
4. **📺 Persistent broadcasts** — Forced Endless Broadcast keeps radio/TV alive. SIMON has a permanent presence.
5. **🎬 Multi-phase events** — Combine: HEF helicopter → RCON broadcast → airdrop → Horde Night. Full cinematic sequences.

### Future Ideas (requires more research):
- **Custom radio station mod** — Create a mod that lets SIMON inject custom audio into the game's radio system (would need a modder)
- **Note/item spawning** — RCON `additem` to spawn notes with SIMON's messages that players can find
- **Vehicle key drops** — RCON `addkey` + vehicle spawn = "Found keys near the gas station. Check the parking lot."

---

## ⚠️ Mods to REMOVE (conflicts or superseded)

| Mod | Reason |
|-----|--------|
| randomairdropsASVOD | Superseded by proper Airdrops mod (3590950467) if you want it |
| Maplewood | Known save corruption — consider fresh map |
| UsefulBarrels | Version incompatibility (loads wrong subfolder) |

---

## ⚠️ Notes

- **DoLuaChecksum** must be `false` for True Music Radio to work on servers
- **Anti-cheat check 21** may need to be `false` for music mods
- Always test new mods in singleplayer first before pushing to server
- B42.17 is still unstable branch — check workshop pages for version-specific notes
