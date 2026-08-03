# damnlib - that DAMN Library (KI5 framework)

Workshop ID: 3171167894
Mod ID: damnlib
Enabled on server: yes (B42.17/18/19/20 MP fully supported)

**Framework / dependency library** that powers all KI5 mods (campers, trailers, etc.). Adds crafting, fixing, and recycling support for cross-mod vehicle parts. Does nothing on its own — required by other KI5 mods on this server:

- `KI5trailers` (Trailers!)
- `KI5campers` (Campers!interior — also enabled)
- `manageContainers` (uses KI5 framework)

## Items
**No addable items.** damnlib is a code framework, not a content mod. Don't try `additem damnlib.X` — there is no X.

## What it gives SIMON
- **Item IDs for KI5 vehicle parts** become available in the loot tables (but those are vanilla-named, not damnlib-prefixed).
- **Crafting recipes** for cross-mod vehicle parts unlock automatically.

## Notes
- Author is consolidating KI5 mod infrastructure through this single library.
- Marked "Feature locked" — contents may shift without warning; SIMON should not cache item-ID assumptions about KI5 parts.
- Ask-for-permission mod — closed to redistribution.

## Use Cases (SIMON voice)
- *None direct.* SIMON only needs to know damnlib exists because **without it, KI5 trailers / campers / containers break at world load**. If the server starts crashing on KI5-related items, damnlib is the first thing to check.