# StarlitLibrary - Starlit Library (dependency framework)

Workshop ID: 3378285185
Mod ID: StarlitLibrary
Enabled on server: yes

**Pure dependency / framework.** Required by other mods that use its API for item descriptions, tooltips, and item registry hooks. Does nothing on its own.

## Items
**No addable items.** `StarlitLibrary.X` is not a thing.

## What it gives SIMON
- Other mods on the server depend on it for their items to register cleanly:
  - **LEGION18** (Legion Weaponry) requires StarlitLibrary or it won't load
  - Other Demiurge-Quantified-framework mods would similarly need it

## Notes
- "You don't have any reason to install this unless a mod you use requires it" — author quote
- Do **not** copy StarlitLibrary files into other mods (license forbids redistribution)

## Use Cases (SIMON voice)
- *None direct.* SIMON only needs to know StarlitLibrary exists because **without it, LEGION18 fails at world load**. If weapons from LEGION18 are missing in the loot tables, check that StarlitLibrary is enabled and synced.