# Setup & Operations (Non-Skill Docs)

This file contains setup/runbook material that is useful for operators but not required in the active skill reference set.

## Install / Enable

1. Enable RCON in your Project Zomboid server config (`servertest.ini`):
   - `RCONPort=<port>`
   - `RCONPassword=<password>`
2. Install `rcon-cli` (gorcon):
   - https://github.com/gorcon/rcon-cli/releases
3. Configure env in `pz-rcon/.env` (local only) using `pz-rcon/.env.example`.
4. Load the skill into OpenClaw (`pz-rcon/` folder or packaged `.skill`).

## Discord back-and-forth relay notes

Use `#pz-molt` as the secure ops relay channel.

Recommended:
- Discord allows bot-authored relay messages when needed.
- The skill keeps two behavior loops:
  - Ambient narrative loop (5 min cadence while players online)
  - Direct help-request handling with anti-spam policy

## Mods planning / onboarding

Mod planning docs are intentionally kept outside active runtime references:
- `pz-rcon/references/archive/MODS.md`

When enabling mods for runtime lookup:
- Set `PZ_ENABLED_MODS` in `pz-rcon/.env`
- Add per-mod item files to:
  - `pz-rcon/references/catalogs/mods/mod-<modname>-items.md`
