---
name: pz-rcon
description: Enhance Project Zomboid server atmosphere via RCON. Use for broadcasting narrative messages to players, giving items/XP rewards, spawning vehicles, triggering world events (hordes, helicopters, gunshots), and controlling weather. Focus on making the server feel alive with storytelling and dynamic events.
---

# Project Zomboid RCON - Atmosphere & Events

Make your Project Zomboid server feel alive with narrative broadcasts, rewards, and dynamic events.

## Prerequisites

Install `rcon-cli` (gorcon):
```bash
# Download from https://github.com/gorcon/rcon-cli/releases
```

## Connection

```bash
rcon -a <host>:<port> -p <password> <command>
```

Default RCON port = game port + 1 (e.g., 16261 → 16262).

## Commands

### Broadcasting Messages

Send atmospheric messages to all players:
```
servermsg "The emergency broadcast system crackles... Stay indoors tonight."
```

**Narrative ideas:**
- Weather warnings before triggering storms
- "Distant gunfire echoes from the west..."
- Radio broadcasts about supply drops
- Creepy night-time announcements

### Giving Items

```
additem "username" <Module.Item> <count>
```

Examples:
```
additem "Player1" Base.Axe 1
additem "Player1" Base.Shotgun 1
additem "Player1" Base.WaterBottleFull 5
additem "Player1" Base.FirstAidKit 2
```

Common items: `Base.Axe`, `Base.Pistol`, `Base.Shotgun`, `Base.Crowbar`, `Base.Hammer`, `Base.WaterBottleFull`, `Base.CannedBeans`, `Base.FirstAidKit`, `Base.Bandage`, `Base.9mmClip`

Full list: https://pzwiki.net/wiki/Items

### Giving XP

```
addxp "username" <Perk>=<amount>
```

Examples:
```
addxp "Player1" Carpentry=100
addxp "Player1" Aiming=50
addxp "Player1" Fitness=200
```

Perks: Fitness, Strength, Sprinting, Axe, Blunt, SmallBlade, LongBlade, Aiming, Reloading, Carpentry, Cooking, Farming, Doctor, Electricity, Mechanics, Tailoring, Fishing, Trapping, Foraging

### Spawning Vehicles

```
addvehicle "<script>" "<username>"
```

Examples:
```
addvehicle "Base.VanAmbulance" "Player1"
addvehicle "Base.PickUpVan" "Player1"
```

Vehicles: `Base.CarNormal`, `Base.CarStationWagon`, `Base.PickUpVan`, `Base.VanAmbulance`, `Base.Van`, `Base.ModernCar`

### World Events

| Command | Effect |
|---------|--------|
| `createhorde <count> "user"` | Spawn zombies near player |
| `chopper` | Helicopter flyover (random player) |
| `gunshot` | Gunshot sound (attracts zombies) |
| `alarm` | Building alarm (admin in room) |
| `lightning "user"` | Lightning strike near player |
| `thunder "user"` | Thunder sound |

**Event narration pattern:**
1. Broadcast warning message
2. Wait a moment
3. Trigger event

Example flow:
```
servermsg "A helicopter is spotted on the horizon..."
# wait
chopper
```

### Weather Control

| Command | Effect |
|---------|--------|
| `startrain` | Start rain |
| `startrain <1-100>` | Rain with intensity |
| `stoprain` | Stop rain |
| `startstorm <hours>` | Start storm (game hours) |
| `stopweather` | Clear all weather |

**Weather narration:**
```
servermsg "Dark clouds gather overhead. Seek shelter."
startrain
# later...
startstorm 2
servermsg "The storm is upon us. This is going to be a rough night."
```

### Listing Players

```
players
```

Returns connected players for targeting events/rewards.

## Narrative Patterns

### Supply Drop
```
servermsg "Emergency broadcast: A military supply drop has been reported near [location]."
servermsg "Survivors in the area, proceed with caution."
```

### Horde Warning
```
servermsg "Reports of a large group of infected moving toward [area]..."
createhorde 50 "TargetPlayer"
```

### Weather Event
```
servermsg "National Weather Service: Severe thunderstorm warning in effect."
startstorm 3
```

### Mystery/Atmosphere
```
servermsg "Strange lights seen in the sky last night. Officials have no comment."
servermsg "If you hear scratching at your walls... don't open the door."
```

## Director Policy: Balance, Memory, and Tone (Stone)

When operating in `#pz-molt` / in-game relay mode, enforce these gameplay rules:

### 1) Track recent asks before acting
- Keep lightweight state in local files:
  - `skills/pz-rcon/state/recent-requests.json` (help/request history)
  - `skills/pz-rcon/state/narrative-state.json` (ambient loop cadence/event cooldown)
- Track at least:
  - player name
  - request type (food/medical/weapon/xp/vehicle/event)
  - timestamp
  - what was granted
- Before granting, check recent history (last 30-120 minutes) to prevent spam/repeat abuse.

### 2) Escalate from generous to trolling when spammed
- If a player repeats low-effort requests too often, reduce reward quality.
- Example progression for repeated food begs:
  1. normal food/help
  2. weaker/less useful food
  3. joke reward (dog food, empty can + fork, etc.)
- Add a sarcastic in-universe quip when trolling.
- Keep it funny, not abusive; stay in server roleplay tone.

### 3) Keep XP boosts small and rare
- XP should be occasional, not routine.
- Prefer small boosts and long cooldowns per player/perk.
- Avoid repeated large XP injections that break progression.

### 4) Theme every response to the demand
- Medical asks → triage/radio-medic tone.
- Supply asks → scavenger/logistics tone.
- Danger asks → emergency broadcast/survival warning tone.
- Rewards and narration should feel diegetic (in-universe).

### 5) Split logic: Ambient Director vs Help Requests
- Treat these as **separate systems**:

#### A) Ambient Director loop (global atmosphere)
- Runs on a 5-minute tick (see `scripts/ambient_tick.sh`).
- If players are online, keep the world flowing with themed narrative.
- Events are rarer than messages and must honor cooldowns.
- This loop should continue as long as players are online.

#### B) Help/Request handler (player asks)
- Triggered by relay messages requesting help/supplies/rewards.
- Respond directly to demand with thematic flavor.
- Apply anti-spam and punishment ladder for repeat beg/spam behavior.
- Use `scripts/request_policy.py` for baseline decisioning (`normal`, `reduced`, `punish`).

- Prioritize server balance over pleasing every request.

### 6) Anti-abuse defaults
- Add per-player cooldowns by category (items/xp/vehicle/event).
- Cap high-impact actions (vehicles, big hordes, large weapon drops).
- Prefer “partial help” over full handouts when a player is repeatedly demanding.

## Maintenance rule (StarbugStone)

Whenever you update this `pz-rcon` skill (SKILL.md, scripts, references, packaging), you must **commit and push** the changes to the public GitHub repo:

- https://github.com/StarbugMolt/pz-rcon-skill

## Script Usage

See `scripts/pz-rcon.sh` for the wrapper script.
See `scripts/horde_night.sh` for triggering a server-wide zombie wave on all players.
See `scripts/ambient_tick.sh` for the 5-minute ambient narrative loop.
See `scripts/request_policy.py` for help-request anti-spam decisioning.

## Reference Catalogs

- Vanilla item lookup: `references/catalogs/vanilla/items-full.md`
- Vanilla vehicle lookup: `references/catalogs/vanilla/vehicles-full.md`
- Mod catalog template: `references/catalogs/mods/mod-template-items.md`
- Command syntax: `references/commands.md`
- Mod list ideas: `references/MODS.md`

### Skill lookup scope (authoritative)

The skill should treat these catalogs as its authoritative spawn/give lookup source:

1. **All vanilla entries** from:
   - `references/catalogs/vanilla/items-full.md`
   - `references/catalogs/vanilla/vehicles-full.md`
2. **All enabled mod entries** from per-mod files under:
   - `references/catalogs/mods/`

### Mod item file convention

Store mod-specific item catalogs in one file per mod using:

- `references/catalogs/mods/mod-<modname>-items.md`

Example: `references/catalogs/mods/mod-ki5-items.md`

Use `references/catalogs/mods/mod-template-items.md` as the template.

### Enabled mod source of truth

Read enabled mods from `.env` key:

- `PZ_ENABLED_MODS` (comma-separated mod IDs)

Only use mod files whose `<modname>` appears in `PZ_ENABLED_MODS`.

## Full Command Details

See `references/commands.md` for complete syntax.
