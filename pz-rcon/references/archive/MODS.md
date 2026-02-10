# Curated Mod List: "The AI Director's Cut" (Build 42 MP)

**Target:** Cinematic Roleplay, <10 Players, Immersive/Dynamic Events.
**Philosophy:** Mods are chosen to give the "AI Director" (Game Master) levers to control pacing, tension, and rewards, rather than just adding "stuff."

---

## 🧩 Server Config Snippet (copy/paste)
*What to add to your PZ dedicated server config (typically `servertest.ini`).*

> We keep the **core** list small for stability. Everything else below is **optional** and is *not* included in the core snippet unless you explicitly add it.

### Workshop IDs
Put these into `WorkshopItems=` (comma-separated).

**Baseline (your must-haves):**
```ini
WorkshopItems=3543229299,2875848298,2544353492,3330403100,3485349033,3387110070
```

### Director mods — core vs optional

**Baseline + Director Core (recommended):** *(no sprinters / no natural horde nights / no forced blackouts)*
```ini
WorkshopItems=3543229299,2875848298,2544353492,3330403100,3485349033,3387110070,3590950467
```

### Mod IDs (load order matters)
Put these into `Mods=` (semicolon-separated). **RV Interior must be first** (per the author).

**Baseline:**
```ini
Mods=PROJECTRVInterior42;BB_CommonSense;P4HasBeenRead;KI5trailers;fol_Take_A_Bath_PortB42;TheyKnewB42
```

**Baseline + Director Core (recommended):**
```ini
Mods=PROJECTRVInterior42;BB_CommonSense;P4HasBeenRead;KI5trailers;fol_Take_A_Bath_PortB42;TheyKnewB42;Airdrops
```

**Optional Director Mods (NOT in core mod list)**
Add these only if you explicitly want the mechanic:
- **Immersive Blackouts** — Workshop `3607686447`, Mod `ImmersiveBlackouts`
- **PhunSprinters** — Workshop `3532685233`, Mod `phunsprinters`
- **Horde Night Fixed (B42)** — Workshop `2714850307` (or your chosen fork), Mod `HordeNight`

**Optional Worldbuilding / Vehicles / Journals (NOT in core mod list)**

Journals:
- **Burd's Survival Journals (B42.13+)** — Workshop `3639628777`, Mod `BurdSurvivalJournals`

Vehicles:
- **'87 Ford B700/F700 Trucks (KI5)** — Workshop `3110911330`, Mod `87fordB700`
- **Autotsar Tuning Atelier - Petyarbuilt 379 [B42]** *(test first)* — Workshop `3403314193`, Mod `ATA_Petyarbuilt`
- **[B42] Skizot's USPS Truck** — Workshop `2941567785`, Mod `USPSTruck`

Maps / POIs (these often require `Maps=` entries too):
- **Mel Bunker [B42]** — Workshop `3641801982`, Mod `MelBunker`, Map folder `MelBunker`
- **SHELTER Echo Creek B42** — Workshop `3450258411`, Mod `shelter-EC42`, Map folder `SHELTER Echo Creek B42`

Notes:
- If you add **map mods**, you may need to update `Maps=` / load order as well (depends on the mod). Always follow the Workshop page instructions.
- If you later add frameworks (Tsar/KI5 libraries, etc.), keep their required load order rules.

## ✅ 0. Server Baseline (Must-Haves)
*Low-drama mods we want on basically every B42 MP run for this server’s vibe.*

### **Common Sense** (Must-have QoL)
*   **Workshop ID:** `2875848298`
*   **Mod ID:** `BB_CommonSense`
*   **Why:** Crowbar prying, better small interactions, lots of “why isn’t this vanilla?” fixes.

### **Has Been Read** (Looting clarity)
*   **Workshop ID:** `2544353492`
*   **Mod ID:** `P4HasBeenRead`
*   **Why:** Marks what you *still need to read* (still valuable even with B42’s vanilla-ish checkmarks).

### **Trailers!** (Logistics / nomad play)
*   **Workshop ID:** `3330403100`
*   **Mod ID:** `KI5trailers`
*   **Why:** Hauling + convoy gameplay. Pairs nicely with “RV Interior” + airdrops.

### **[B42 Port] Take a Bath** (Immersion + sanity)
*   **Workshop ID:** `3485349033`
*   **Mod ID:** `fol_Take_A_Bath_PortB42`
*   **Why:** Hygiene loop + small mood relief. Good RP glue.

### **They Knew [B42]** (Optional-but-strong “story medicine”)
*   **Workshop ID:** `3387110070`
*   **Mod ID:** `TheyKnewB42`
*   **Why:** Rare hazmat encounters + cure items = great Director reward hooks.

### **[B42] Project RV Interior** (Test first)
*   **Workshop ID:** `3543229299`
*   **Mod ID:** `PROJECTRVInterior42`
*   **Why:** Nomad fantasy. **Note:** must be **first in mod load order** (per author) and should be tested for MP stability.

## 🎭 1. The Core "Director" Toolkit (Events & Pacing)
*These mods allow the server to feel alive and reactive.*

### **Airdrops** (Essential)
*   **Workshop ID:** `3590950467`
*   **Mod ID:** `Airdrops`
*   **Roleplay Value:** The ultimate narrative delivery system.
    *   **Cinematic Feature:** "Explosive Cleanup" - Drops self-destruct if not claimed, forcing desperate extraction missions.
    *   **Director Control:** Use RCON to spawn specific drops (medical, weapons) as narrative rewards. "Command has sent support to Sector 4..."

### **Horde Night Fixed (B42)**
*   **Workshop ID:** `2714850307` (or B42 fork/update)
*   **Mod ID:** `HordeNight`
*   **Roleplay Value:** Scripted climaxes.
    *   **Config:** Set to "Random" for unpredictability, or schedule them for "Season Finales."
    *   **Tuning:** For 1-2 players, set horde size to **20-30 zombies**. Focus on *atmosphere* (lightning/noise) rather than overwhelming numbers.
    *   **Cinematic:** Use RCON to warn players ("Seismic sensors active...") before the night begins.

### **Immersive Blackouts [B42MP]**
*   **Workshop ID:** `3607686447`
*   **Mod ID:** `ImmersiveBlackouts`
*   **Roleplay Value:** Instant atmosphere.
    *   **Director Control:** Randomly cut power during a loot run to force flashlight usage and panic.

### **PhunSprinters**
*   **Workshop ID:** `3532685233`
*   **Mod ID:** `phunsprinters`
*   **Roleplay Value:** Pacing control.
    *   **Config:** Set global sprinter speed low (1-5%), but ramp it up to 100% in specific "Dark Zones" (e.g., military bases) to create "dungeon" raids.

---

## 🎵 2. Atmosphere & Immersion (Cinematic Feel)
*Mods that make the world feel lived-in and emotional.*

### **True Music (B42)**
*   **Workshop ID:** *(Search "True Music" + B42 filter)*
*   **Mod ID:** `truemusic`
*   **Roleplay Value:** Diegetic music.
    *   **Idea:** Airdrop a boombox and specific cassettes (e.g., "The End" by The Doors) to set the mood for a final stand.

### **Unseasonal Weather**
*   **Workshop ID:** `3582891045`
*   **Mod ID:** `UnseasonalWeather`
*   **Roleplay Value:** Visual storytelling.
    *   **Effect:** Sudden fog banks or storms that reduce visibility to zero, perfect for horror sequences.

### **I Don't Need A Lighter**
*   **Workshop ID:** `2714198296`
*   **Mod ID:** `IDontNeedALighter`
*   **Roleplay Value:** Small immersion fix. Use stoves/campfires to light cigarettes.

---

## 🚗 3. Vehicles (The Rewards)
*High-quality assets for "Hero Vehicles". Don't flood the server; make these rare finds.*

### **KI5 Vehicle Collection**
*   **Workshop IDs:** Various (Pick 3-5 specific ones to keep load times down)
    *   **'82 Jeep J10:** The rugged survivor truck.
    *   **'97 ADI Bushmaster:** The ultimate armored reward for a server-wide event.
    *   **'93 Ford Mustang SSP:** Fast police interceptor for highway chases.
*   **Mod ID:** *Depends on vehicle*
*   **Roleplay Value:** Fully animated parts (hoods, doors) make them feel real.

### **Autotsar Trailers [B42]**
*   **Workshop ID:** *(Check Collection)*
*   **Mod ID:** `AutotsarTrailers`
*   **Roleplay Value:** Logistics. Generator trailers and fuel tankers allow for mobile bases/convoys.

---

## 🛠️ 4. Server Frameworks (Required)
*The glue that holds the mods together.*

*   **[B42] Mod Manager:** Essential for server admin to manage load orders.
*   **Tsar's Common Library B42:** Required for vehicles.
*   **PhunLib:** Required for Sprinters.
*   **B42 NeatUI Framework:** Required for UI mods.

---

## ❌ 5. Mods to AVOID (for Cinematic RP)
*   **Combat Text / Health Bars:** *Breaks immersion.* We want players checking their bodies for bites, not reading HP bars.
*   **Brita's Weapon Pack:** *Too OP.* Cinematic zombies aren't scary if everyone has a minigun. Stick to Vanilla Firearms Expanded or just Vanilla B42 (which is much improved).
*   **Minimap Mods:** *Debatable.* Removing the minimap forces players to use in-game maps and navigation skills, boosting immersion.
*   **Bandits NPC:** *Unstable in MP.* Great concept, but currently causes desync/crashes in B42 multiplayer. Wait for stability updates.

---

## 🎬 Director's Playbook: "The Siege"
*Example of how to combine these mods.*

1.  **Setup:** Admin places a **'97 Bushmaster** (KI5) at the center of the Mall.
2.  **Phase 1 (Tension):** RCON broadcast: "Signal detected at Crossroads Mall. High-value asset confirmed."
3.  **Phase 2 (The Journey):** Trigger **Unseasonal Weather** to create heavy fog. Players must navigate blindly.
4.  **Phase 3 (The Trap):** When they enter the Mall, trigger **Immersive Blackouts** (lights out).
5.  **Phase 4 (The Climax):** Trigger **Horde Night** (20-30 zombies) to swarm the entrances.
6.  **Resolution:** Players escape in the armored truck. Admin triggers **Airdrop** with fuel/ammo at their exit route.
