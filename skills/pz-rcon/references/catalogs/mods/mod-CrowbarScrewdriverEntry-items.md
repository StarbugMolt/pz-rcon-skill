# CrowbarScrewdriverEntry — Locked-Door Entry (B42.20 MP)

- **Workshop ID:** 3770164353
- **Mod ID:** `CrowbarScrewdriverEntry`
- **Author:** (unknown from page)
- **Build target:** B42 (42.19+), multiplayer-safe (server-authoritative)
- **Status:** ✅ VERIFIED — uses VANILLA items only, no new scripts

## What it adds (behavior, not items)

Three vanilla entry tools get tiered door-opening logic. Success scales with stats, tools degrade on failure, and rolls produce noise + (sometimes) hand injuries.

| Tool | Vanilla script | Loudness | Skill gates | Special |
|------|----------------|----------|-------------|---------|
| Crowbar | `Base.Crowbar` | LOUD | Strength, Fitness | Always-can-pry (except reinforced doors without Strength) |
| Screwdriver | `Base.Screwdriver` | Quiet (almost silent) | Nimble (primary), Mechanics, Fitness | Burglar trait gets standing bonus |
| Bolt cutters | `Base.BoltCutters` | LOUDEST | None (mechanical leverage) | Cuts reinforced security doors + wire fences |

### Sandbox knobs (admin-configurable)
- Master switch + per-tool toggle (Crowbar / Screwdriver / Bolt cutters)
- Success multipliers (prying, lockpicking, cutting)
- Noise multipliers (per tool)
- Action time multiplier (general + fence-specific)
- Tool wear on failure (set 0 = tools never break)
- Injury chance + severity (separate)
- Reinforced doors (vault/security) require min Strength when enabled
- Fence cutting + wire salvage toggle

## SIMON can spawn these (vanilla)
```bash
pz-rcon.sh give <player> Base.Crowbar 1
pz-rcon.sh give <player> Base.Screwdriver 1
pz-rcon.sh give <player> Base.BoltCutters 1
```

## Narrative use

Mod changes behavior, not loot tables. Story beats SIMON can leverage:
- **Sneak jobs**: "Bolt cutters. Quietly now." Screwdriver path for burglar-types.
- **Loud breach**: Crowbar always works, just bring spares — failure chews through condition.
- **Reinforced sites** (gun stores, vaults): Vault/security doors need crowbar-with-Strength OR bolt cutters. Reinforced successes generate a working key, so the player never has to break in twice.
- **Fence cutting**: Wire fences (chain-link, barbed-wire) are permanently removed; salvage drops at feet. Pipe/plank fences can't be cut.
- **Server-authoritative**: Rolls resolve on the server. No client-side cheating.

SIMON voice: *"That's a reinforced door. Bolt cutters, or you're crowbarring it 'til your arms give out. Either way, the neighbours WILL know you're coming."*

## Caveats
- Sandbox toggles per server. If the server admin disabled a tool, SIMON must respect it.
- Mid-save safe. Can be added/removed without world reset.
- No map edits, no item overrides — sits clean alongside other mods.
- Translations: English + Ukrainian.
