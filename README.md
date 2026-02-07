# pz-rcon (OpenClaw Skill) — Project Zomboid Atmosphere Director

This repository contains an OpenClaw skill called **`pz-rcon`**.

It’s designed to make a **Project Zomboid** dedicated server feel more alive by using **RCON** to:
- broadcast in-universe / narrative messages to online players
- reward players with **items / XP / vehicles**
- trigger **events** (hordes, helicopter, gunshot, alarms)
- control **weather** (rain, storms, clear)

It intentionally does **NOT** include moderation or server lifecycle control (no bans/whitelist/shutdown/etc.).

## Contents

- `pz-rcon/` — the skill folder
  - `SKILL.md` — skill instructions (what the agent loads)
  - `scripts/pz-rcon.sh` — helper wrapper around `rcon-cli`
  - `references/` — extra docs and command reference
- `pz-rcon.skill` — packaged skill file (zip with `.skill` extension)

## Prerequisites

### 1) Enable RCON on your PZ server

Edit your server config (often `servertest.ini`) to include:

```ini
RCONPort=16262
RCONPassword=CHANGE_ME
```

Notes:
- RCON port is usually **game port + 1**.
- Treat the password like root access.

### 2) Install `rcon-cli` (gorcon)

This skill’s wrapper uses **gorcon/rcon-cli**:

- Releases: https://github.com/gorcon/rcon-cli/releases

Confirm it works:

```bash
rcon --help
```

## Quick start (using the wrapper script)

Set environment variables:

```bash
export PZ_RCON_HOST="your.server.ip"
export PZ_RCON_PORT="16262"
export PZ_RCON_PASSWORD="your_password"
```

Then run:

```bash
cd pz-rcon
./scripts/pz-rcon.sh players
./scripts/pz-rcon.sh msg "Emergency broadcast: stay indoors tonight."
```

## What you can do

### See who’s online

```bash
./scripts/pz-rcon.sh players
```

### Broadcast narrative messages

```bash
./scripts/pz-rcon.sh msg "*static* ...This is Knox Emergency Radio..."
```

Good pattern:
1) message
2) wait a beat
3) trigger event/weather
4) follow-up message

### Reward players with items

```bash
./scripts/pz-rcon.sh give "PlayerName" Base.Axe 1
./scripts/pz-rcon.sh give "PlayerName" Base.FirstAidKit 1
```

Item codes are `Module.ItemName`:
- Full list: https://pzwiki.net/wiki/Items

### Grant XP perks

```bash
./scripts/pz-rcon.sh xp "PlayerName" Carpentry=100
./scripts/pz-rcon.sh xp "PlayerName" Aiming=50
```

### Spawn a vehicle

```bash
./scripts/pz-rcon.sh vehicle Base.VanAmbulance "PlayerName"
```

### Trigger events

```bash
./scripts/pz-rcon.sh horde 50 "PlayerName"
./scripts/pz-rcon.sh chopper
./scripts/pz-rcon.sh gunshot
./scripts/pz-rcon.sh alarm
```

### Control weather

```bash
./scripts/pz-rcon.sh rain 50
./scripts/pz-rcon.sh storm 2
./scripts/pz-rcon.sh clear
```

## “Director” mini playbooks

### 1) Storm night (mood setter)

```bash
./scripts/pz-rcon.sh msg "National Weather Service: severe storm incoming."
./scripts/pz-rcon.sh rain 35
./scripts/pz-rcon.sh msg "If you’re outside, that’s between you and Darwin."
./scripts/pz-rcon.sh storm 3
```

### 2) Supply drop… with teeth

```bash
./scripts/pz-rcon.sh msg "Military broadcast: supply cache spotted near the gas station."
./scripts/pz-rcon.sh give "PlayerName" Base.Shotgun 1
./scripts/pz-rcon.sh give "PlayerName" Base.ShotgunShells 12
./scripts/pz-rcon.sh msg "...unfortunately, you’re not the only one who heard that."
./scripts/pz-rcon.sh horde 40 "PlayerName"
```

### 3) Helicopter escalation

```bash
./scripts/pz-rcon.sh msg "A helicopter is circling. Do NOT wave at it."
./scripts/pz-rcon.sh chopper
./scripts/pz-rcon.sh msg "If you can hear it, they can hear you."
```

## Installing the skill into OpenClaw

If you’re using OpenClaw skills:
- Import the packaged `pz-rcon.skill`, or
- Copy the `pz-rcon/` folder into your skills directory.

(Exact installation depends on how your OpenClaw instance is configured.)

## Safety notes

- Avoid running event commands too frequently; it can ruin pacing.
- Prefer “soft narration” over spam: 1–3 lines, then let players play.
- Keep rewards rare enough to feel meaningful.

## License

MIT — see `LICENSE`.
