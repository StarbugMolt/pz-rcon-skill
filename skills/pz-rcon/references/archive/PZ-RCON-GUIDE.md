# ARCHIVED (Non-Canonical)

This file is historical context only. Do not treat it as current skill authority.
Canonical files:
- `../../SKILL.md`
- `../commands.md`

# Project Zomboid RCON - Atmosphere & Events Guide

Use RCON to make your Project Zomboid server feel alive with narrative broadcasts, rewards, and dynamic world events.

## Setup

### 1. Install rcon-cli

Download from [gorcon/rcon-cli releases](https://github.com/gorcon/rcon-cli/releases).

### 2. Configure Connection

Set environment variables:
```bash
export PZ_RCON_HOST="your.server.ip"
export PZ_RCON_PORT="16262"
export PZ_RCON_PASSWORD="your_password"
```

Or create `~/.config/rcon.yaml`:
```yaml
default:
  address: "your.server.ip:16262"
  password: "your_password"
```

---

## Quick Reference

### Broadcasting
```bash
./pz-rcon.sh msg "The emergency broadcast crackles to life..."
```

### Rewards
```bash
./pz-rcon.sh give "PlayerName" Base.Axe 1
./pz-rcon.sh xp "PlayerName" Carpentry=100
./pz-rcon.sh vehicle Base.VanAmbulance "PlayerName"
```

### Events
```bash
./pz-rcon.sh horde 50 "PlayerName"
./pz-rcon.sh chopper
./pz-rcon.sh gunshot
```

### Weather
```bash
./pz-rcon.sh rain start
./pz-rcon.sh storm 2
./pz-rcon.sh clear
```

---

## Event Ideas

### 🎁 Supply Drop
Reward a player with narrative context:
```bash
./pz-rcon.sh msg "Emergency broadcast: Supply cache reported near the gas station."
./pz-rcon.sh give "Player1" Base.Shotgun 1
./pz-rcon.sh give "Player1" Base.ShotgunShells 12
```

### 🧟 Horde Incoming
Build tension before spawning:
```bash
./pz-rcon.sh msg "Reports of a massive group moving from the east..."
./pz-rcon.sh msg "All survivors near Muldraugh, evacuate NOW."
# wait a moment
./pz-rcon.sh horde 60 "TargetPlayer"
```

### 🚁 Helicopter Event
The classic danger:
```bash
./pz-rcon.sh msg "A helicopter spotted on the horizon..."
./pz-rcon.sh chopper
./pz-rcon.sh msg "It's drawing them to you. Find cover!"
```

### ⛈️ Storm Warning
Dynamic weather with narrative:
```bash
./pz-rcon.sh msg "National Weather Service: Severe thunderstorm approaching."
./pz-rcon.sh rain 50
# later
./pz-rcon.sh storm 3
./pz-rcon.sh msg "The storm has arrived. Stay indoors."
```

### 👻 Mysterious Broadcast
Add atmosphere:
```bash
./pz-rcon.sh msg "Emergency broadcast: *static* ...don't trust... *static*"
./pz-rcon.sh msg "...they're not what they seem... *signal lost*"
```

---

## Common Item Codes

| Category | Examples |
|----------|----------|
| Melee | `Base.Axe`, `Base.Crowbar`, `Base.BaseballBat`, `Base.Katana` |
| Guns | `Base.Pistol`, `Base.Shotgun`, `Base.HuntingRifle` |
| Ammo | `Base.9mmClip`, `Base.ShotgunShells`, `Base.308Clip` |
| Medical | `Base.FirstAidKit`, `Base.Bandage`, `Base.Antibiotics` |
| Food | `Base.WaterBottleFull`, `Base.CannedBeans` |

Full list: https://pzwiki.net/wiki/Items

---

## Common Perks for XP

| Type | Perks |
|------|-------|
| Combat | `Axe`, `Blunt`, `Aiming`, `Reloading` |
| Survival | `Carpentry`, `Cooking`, `Farming`, `Fishing` |
| Physical | `Fitness`, `Strength`, `Sprinting` |
| Technical | `Mechanics`, `Electricity`, `MetalWelding` |

---

## Tips

- **Timing matters**: Broadcast warnings before events for immersion
- **Mix rewards with danger**: A supply drop might attract a horde
- **Weather sets mood**: Rain before scary events, clear skies for rewards
- **Keep messages in-universe**: Radio broadcasts, emergency alerts, mysterious signals
