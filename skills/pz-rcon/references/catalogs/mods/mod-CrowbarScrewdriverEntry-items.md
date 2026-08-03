# CrowbarScrewdriverEntry - Crowbar / Screwdriver Entry

Workshop ID: 3770164353
Mod ID: CrowbarScrewdriverEntry
Enabled on server: yes (B42 — verify MP compatibility in server console)

Alternative entry methods: use a Crowbar or Screwdriver (vanilla items) to force-open locked doors, windows, and other entry points. Replaces/augments the vanilla lockpicking mechanic with tool-based entry that consumes tool durability.

## Items

**No new item-prefix to `additem`.** This mod uses vanilla tools:
- `Base.Crowbar`
- `Base.Screwdriver`

Tools degrade with use; SIMON can grant fresh tools via `additem` if survivors break theirs.

## Notes
- ⚠️ This mod essentially replaces or bypasses vanilla lockpicking. If server sandbox has lockpicking disabled, this mod may still allow entry — confirm with admin.
- SIMON's narrative framing: "Use the crowbar, the door's not getting friendlier" rather than "pick the lock"

## Use Cases (SIMON voice)
- **Tool durability as narrative tension**: SIMON can broadcast when survivors burn through their last screwdriver — "If you break it, you're picking your way in with your *teeth* next time."
- **"Quick entry" story beats**: SIMON can pre-stage a `removezombies` near a locked building, then urge survivors to "Get in there, NOW — crowbar the door, MOVE."
- **Tool restock rewards**: `additem Base.Crowbar` or `Base.Screwdriver` after a successful base raid

## Status
- Steam workshop fetch was rate-limited — **item IDs above are inferred from mod title; confirm specific vanilla items used by inspecting `WorkshopItems/3770164353/contents/mods/CrowbarScrewdriverEntry/media/scripts/` on the server before relying on them.**