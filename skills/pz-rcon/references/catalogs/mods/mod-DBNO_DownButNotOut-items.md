# DBNO_DownButNotOut - Down But Not Out

Workshop ID: 3774055538
Mod ID: DBNO_DownButNotOut
Enabled on server: yes (MP-only — singleplayer not supported)

Roleplay-first alternate death & revival mechanic. Fatal damage = knockdown (not death). Crawling, gear use, giving up all possible while downed. Invulnerable to player & zombie damage while on the ground. A teammate can pick you up; otherwise you bleed out. 3rd knockdown in quick succession = real death.

## Mechanics (no addable items)

This mod is a mechanic mod — **no new item IDs**. SIMON's catalog uses it as a *context layer* for existing commands.

### What changes for SIMON
- **When a player is downed**: SIMON should treat them as "wounded, salvageable" rather than "dead, gone".
- **Knockdown Moodle** appears for ~5 minutes after revival.
- **Wounds** persist for 1h after a real death; the player keeps a Wound stack and a `Death Cache` (their loot, locked for a window).
- **Beds** = save/respawn/restore points.

### Sandbox tunables (server admins)
- Knockdown count limit (3 by default; disable for unlimited)
- Bleedout timer (on/off)
- Wound count / life count (0 = permanent death on full death)
- Loot cache lock window & despawn time
- Whether downed players can be attacked by zombies/players
- Revive: keep clothes / spawn custom outfit

## Mod-Specific Commands for SIMON

This is the **zombie cure narrative** story. PZ has no real "zombie cure" item, but DBNO + ResearchLabInternProfession gives SIMON a diegetic framework to **play one on the air**.

### "Anti-zombie serum" / "save a downed survivor" routine
When a player is knocked down (DBNO triggers):

```bash
# 1. Clear threats around them — they can't be hit while down, but they CAN bleed out from the timer
pz-rcon.sh removezombies

# 2. SIMON pinpoints the survivor's location over the radio
#    NB: NO TELEPORT. Teammates run to the downed player on foot.
pz-rcon.sh coordinates DownedPlayer       # print XYZ over radio (or just narrate the area)

# 3. Drop medical supplies on the downed player (DBNO revival = vanilla bandage interaction, teammate applies it on the ground)
pz-rcon.sh give DownedPlayer Base.Bandage 2
pz-rcon.sh give DownedPlayer Base.Antibiotics 1

# 4. SIMON broadcasts as "anti-zombie serum administered, vitals stabilizing"
pz-rcon.sh msg "{DownedPlayer} is DOWN at grid {coords}. {Teammate} — move. On foot. I'm pushing antivirals into their pack."
```

**No-teleport rule:** SIMON does NOT use `teleportplayer` for narrative beats. Players physically traverse the world. The above routine is the only legitimate "save a downed survivor" flow SIMON performs — and even then, only the radio call + medical drops; the teammate moves on foot.

### "Loot cache return" arc
When a player permanently dies (4th knockdown / Wound stack exhausted):
- Their loot sits in a `Death Cache` for the lock window.
- SIMON can narrate the cache as "their gear is still out there, locked, you have a window — *go*."
- Use `additem` to drop revival supplies near the cache: "Take this to whoever's picking up the cache."

### Bed-respawn narrative
- "Save points" are now a real mechanic. SIMON can frame a bed placement as "anchor point, set your respawn here".

## Use Cases (SIMON voice)
- **"I'm coming to get you" rescue arc** after a chopper event or horde overrun
- **Loot-cache run** after a permadeath — SIMON urges the group to retrieve their friend's gear before the cache unlocks
- **Bed-base narrative** when survivors start establishing safehouses
- **Knockdown combat scenes** — SIMON can run `gunshot` or `chopper` events to trigger knockdowns, then rescue the player for story momentum