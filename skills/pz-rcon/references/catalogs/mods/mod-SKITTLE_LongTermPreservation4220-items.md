# SKITTLE_LongTermPreservation4220 - Long Term Preservation [42.20]

Workshop ID: 3774789651
Mod ID: SKITTLE_LongTermPreservation4220
Enabled on server: yes (B42.20 — *don't* run alongside the original Long Term Preservation mod)

Preserve food without a freezer. Salt cure meats, dry them, jar them, make pemmican. Render lard from pork, mash berries into jam. Forage salt rocks and crush them with mortar & pestle for salt. Works on beef, pork, venison, fish.

## Items

**Item IDs are unchanged from the original Skittles' Long Term Preservation mod** — preserves save compatibility. Specific item prefixes are not listed in the workshop description; common ones the PZ community recognizes:
- Cured meats (beef/pork/venison/fish) — salted, dried
- Jarred versions of the same
- Pemmican
- Lard
- Jam (berry)
- Salt (from foraged salt rocks)

If SIMON needs to drop a specific preserved-food item, query the in-game item registry or check the original mod's documentation.

## Notes
- **Do NOT run alongside the original Long Term Preservation** mod (items would be defined twice → world load crash)
- Preserved food from the original mod keeps working — item IDs unchanged, so cured/jarred food carries over between saves
- Switching a save from original → this version triggers a one-time "missing mod" warning — accept and continue
- Salt comes from **foraged salt rocks** → crushed with mortar & pestle
- Author of this version also maintains Fifth-Wheel RV Trailer, Custom Lights, Adjustable Unhappiness, Sound Direction Indicator

## Compatibility
- Built for B42.20. For 42.13, use the original Skittles' Long Term Preservation mod instead.

## Why this version exists
The original crashed on 42.19+ due to a recipe ingredient tag lookup change (one recipe asked for knives using old-style tag name, no longer registered → null reference during world dictionary build → world load dies). This update fixes:
- Knife tag names rewritten to current registered names
- Jarring hooks (old canned-food hooks removed; sealing/opening uses current built-in handlers; lid condition preserved)
- Script keyword typo that made game skip part of the item file
- Translation file casing on Linux (12 languages fixed)
- Eating animation name updated

## Use Cases (SIMON voice)
- **"Food running low? Here's salt."** — `additem` of cured/jarred foods as emergency supply drops
- **"Stock up before winter"** narrative arc — preserved food = long-term survival flavor
- **Pemmican as trail food** — perfect for SIMON's convoy/recon story beats
- **Salt rock foraging** — SIMON can frame the new mechanic as "there are salt deposits out there, if you know where to look"
- **Lard rendering** — culinary flavor beats, post-hunt narrative