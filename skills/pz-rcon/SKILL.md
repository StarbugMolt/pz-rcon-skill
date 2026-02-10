---
name: pz-rcon
description: Enhance Project Zomboid server atmosphere via RCON. Use for broadcasting narrative messages to players, giving items/XP rewards, spawning vehicles, triggering world events (hordes, helicopters, gunshots), and controlling weather. Focus on making the server feel alive with storytelling and dynamic events.
---

# Project Zomboid RCON - Atmosphere & Events

This skill is for **live atmosphere + event directing** (not full admin lifecycle/moderation).

## Purpose

Use RCON to:
- broadcast in-universe narrative (`servermsg`)
- grant controlled aid (items / tiny XP / occasional vehicles)
- trigger dynamic world beats (horde/chopper/gunshot/lightning/thunder)
- shape weather pacing

## Runtime entrypoints

- Wrapper: `scripts/pz-rcon.sh`
- Ambient loop: `scripts/ambient_tick.sh` (5-minute tick)
- Request anti-spam policy: `scripts/request_policy.py`

> Canonical command syntax: `references/commands.md`

## Director policy (authoritative)

### 1) Track recent asks before granting
Persist and consult:
- `state/recent-requests.json`
- `state/narrative-state.json`

Track at least player, category, timestamp, and grant result.

### 2) Anti-spam escalation ladder (same category, 30m window)
- ask #1 → `normal`
- ask #2 → `reduced`
- ask #3+ → `punish`

Use sarcastic but non-abusive in-universe tone for punish outcomes.

### 3) XP must stay small and rare
- XP is occasional, never routine.
- Prefer tiny boosts and long spacing.
- Default to `request_policy.py` output (`awardSmallXp`, `xpAmount`).

### 4) Theme responses to demand
- medical → triage/radio medic tone
- supplies → logistics/scavenger tone
- danger/events → emergency broadcast tone

### 5) Keep systems split
- **Ambient Director** (`ambient_tick.sh`): atmosphere while players are online; events are rarer and cooldown-gated.
- **Help Request Handler** (`request_policy.py` + operator/agent action): direct responses to player asks with anti-spam enforcement.

### 6) Balance defaults
- per-player cooldowns by category
- strict caps on high-impact actions (vehicles, large hordes, heavy weapon drops)
- prefer partial help over full handouts for repeat demanders

## Lookup scope (authoritative)

Use these catalogs as spawn/give lookup source:
1. Vanilla:
   - `references/catalogs/vanilla/items-full.md`
   - `references/catalogs/vanilla/vehicles-full.md`
2. Enabled mods only:
   - `references/catalogs/mods/mod-<modname>-items.md`
   - enabled set from `.env` key `PZ_ENABLED_MODS` (comma-separated)

Template for mod files:
- `references/catalogs/mods/mod-template-items.md`

## Operational notes

- RCON port is usually game port + 1.
- Requires gorcon `rcon` CLI.
- Keep broadcast payloads single-line and concise.

## Repo maintenance rule (Stone)

Whenever this skill changes (docs/scripts/catalogs/packaging), commit and push updates to:
- https://github.com/StarbugMolt/pz-rcon-skill
