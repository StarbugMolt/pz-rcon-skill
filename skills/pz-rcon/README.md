# pz-rcon Skill (Workspace Copy)

Project Zomboid Build 42 RCON helper for atmosphere/events and controlled live-ops rewards.

## Quick start

1. Install gorcon `rcon` CLI.
2. Copy `.env.example` to `.env` and set:
   - `PZ_RCON_HOST`
   - `PZ_RCON_PORT`
   - `PZ_RCON_PASSWORD`
   - `PZ_ENABLED_MODS` (optional, comma-separated)
3. Use wrapper commands via `scripts/pz-rcon.sh`.

## Main scripts

- `scripts/pz-rcon.sh` — command wrapper
- `scripts/ambient_tick.sh` — 5-minute ambient narrative loop
- `scripts/request_policy.py` — anti-spam decision helper
- `scripts/set_player_honorific.py` — store player honorific (`mister|maam|miss`)

## Canonical docs

- Policy/operating rules: `SKILL.md`
- Command syntax/examples: `references/commands.md`
- Lookup catalogs: `references/catalogs/`

## Catalog behavior

Lookup includes:
1. all vanilla entries from `references/catalogs/vanilla/*`
2. mod entries from `references/catalogs/mods/mod-<modname>-items.md` only when `<modname>` is in `.env` `PZ_ENABLED_MODS`

## Configuration

Copy `config.json.example` to `config.json` and adjust the following:

| Setting | Type | Description |
|---------|------|-------------|
| `ambient.tickInterval` | cron | How often SIMON checks for players (default: `*/5 * * * *` = every 5 min) |
| `ambient.eventChance` | number | % chance an event triggers on each tick (default: 25) |
| `ambient.events` | object | Weight distribution for event categories |
| `ambient.soundEvents` | object | Weight distribution for sound events |

### Event Weights

The `events` object defines what happens when an event triggers:
- `sound` — triggers a sound event (gunshot, alarm, chopper)
- `weatherClear` — stops rain/storms
- `weatherStorm` — starts a thunderstorm
- `weatherLight` — light rain

The `soundEvents` object defines which sound plays:
- `gunshot`, `alarm`, `chopper`

All weights are percentages and should sum to 100.

### Example: Reduce Helicopters

To cut helicopter frequency, lower `chopper` in `soundEvents`:
```json
"soundEvents": {
  "gunshot": 50,
  "alarm": 30,
  "chopper": 10
}
```
