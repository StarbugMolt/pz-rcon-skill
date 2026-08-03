# ZeroWeightKeys_B42 — Zero Weight Keys [B42.20]

- **Workshop ID:** 3776502124
- **Mod ID:** `ZeroWeightKeys_B42`
- **Author:** FieClaussell
- **Build target:** B42.20, multiplayer support "in theory, untested"
- **Status:** ✅ VERIFIED — pure weight tweak, no new items, no scripts

## What it adds

Single sandbox-configurable param: **set the weight of keys to a chosen value (default 0)**. Carry as many keys as you want.

### Features
- Customizable key weight via sandbox option (default = 0)
- Works with keys added by other mods (the weight override applies to all key instances)
- Compatible with most key-providing mods

### Sandbox option
- `KeysWeight` — weight (in vanilla units) assigned to each key. Default 0 = weightless.

## SIMON can spawn: nothing

This is a parameter tweak on existing vanilla keys. No new items, no new scripts. SIMON cannot spawn anything from this mod directly.

## Narrative use (purely atmospheric)

- Survivors can carry the entire keyring without inventory pressure.
- Means: any "locker room full of keys" puzzle is now a viable loot-arc for the player.
- Side story beats:
  - "Found a set of six keys in the desk drawer. Doesn't matter that they weigh nothing — they still don't open anything useful."
  - Combine with DBNO: even critically wounded, key carriers don't drop their keys.

## Compatibility
- ✅ Compatible with keys added by other mods
- ✅ Vanilla keys (house, car, door, etc.) all affected
- ⚠️ Multiplayer "should work in theory, but has not been tested yet" — author admits untested
- B42.20 only

## Known issues (per author)
- **Keys provided at character creation keep their default weight.** Only keys obtained *during* gameplay reflect the configured weight.
- **Adding to existing save:** previously-acquired keys keep their original weight. Only NEW keys reflect the new setting.
- This is per-game-state-of-record: changes apply only to keys obtained after install/enable.

## Caveats
- Mid-save behavior is asymmetric (existing keys vs new keys). SIMON should NOT promise "all keys now weight 0" — only "new keys from now on".
- If a player reports "keys still weigh something" — that's likely a vanilla-original-save key that wasn't re-rolled.
