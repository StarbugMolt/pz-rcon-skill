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

## Canonical docs

- Policy/operating rules: `SKILL.md`
- Command syntax/examples: `references/commands.md`
- Lookup catalogs: `references/catalogs/`

## Catalog behavior

Lookup includes:
1. all vanilla entries from `references/catalogs/vanilla/*`
2. mod entries from `references/catalogs/mods/mod-<modname>-items.md` only when `<modname>` is in `.env` `PZ_ENABLED_MODS`
