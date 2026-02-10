# pz-rcon Skill (Local Workspace Copy)

Project Zomboid RCON skill for atmosphere/events, rewards, and controlled live-ops actions.

## Reference Catalog Layout

Catalogs are organized under `references/catalogs/` to avoid clutter:

- `references/catalogs/vanilla/items-full.md`
- `references/catalogs/vanilla/vehicles-full.md`
- `references/catalogs/mods/mod-template-items.md`
- `references/catalogs/mods/mod-<modname>-items.md` (one file per mod)

## How lookup works

The skill can use:

1. **All vanilla items/vehicles** from the vanilla catalogs.
2. **All listed mod entries** from `references/catalogs/mods/` **only** when that mod appears in:
   - `.env` → `PZ_ENABLED_MODS` (comma-separated)

This keeps runtime lookup explicit, deterministic, and easy to maintain per mod.

## Env files

- Local secrets: `.env` (never commit)
- Shared template: `.env.example`

Current `.env` keys:
- `PZ_RCON_HOST`
- `PZ_RCON_PORT`
- `PZ_RCON_PASSWORD`
- `PZ_ENABLED_MODS`
