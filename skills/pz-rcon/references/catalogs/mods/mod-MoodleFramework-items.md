# MoodleFramework - Moodle Framework

Workshop ID: 3396446795
Mod ID: MoodleFramework
Enabled on server: yes

**Framework / dependency library** for mods that add new moodles (status icons in the player HUD). Provides API hooks so other mods can register custom moodles cleanly. Does nothing on its own.

## Items
**No addable items.** `MoodleFramework.X` is not a thing.

## What it gives SIMON
- Other mods that add moodles depend on this framework — likely used by DBNO_DownButNotOut's "Knockdown" moodle and similar status-effect mods
- If a mod's moodles aren't showing in the HUD, MoodleFramework is the first thing to check

## Notes
- Pure infrastructure — no content, no balance impact
- Ask-for-permission or open-source depending on the mod author's license; check before redistributing

## Use Cases (SIMON voice)
- *None direct.* SIMON only needs to know MoodleFramework exists as a **dependency enabler**. If moodle-related mods (DBNO wounds, etc.) are misbehaving, this is in the dependency chain.