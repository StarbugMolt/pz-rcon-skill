# pz-rcon Command Reference (Canonical)

Use wrapper: `scripts/pz-rcon.sh <command> ...`

## Connection/env

Required:
- `PZ_RCON_PASSWORD`

Optional:
- `PZ_RCON_HOST` (default `localhost`)
- `PZ_RCON_PORT` (default `16262`)

## Wrapper commands

### Player info
- `players` / `list`

### Broadcast
- `msg <message>` — **admin escape hatch only**. Sends via RCON `servermsg` directly to in-game chat (no Discord mirror). SIMON must NOT use this — SIMON chat goes through Discord #pz-molt (auto-mirrored to in-game via PZ's Discord chat relay, `DiscordEnable=true`, `DiscordChatChannel=pz-molt`). Use `msg` only when you need an in-game-only announcement that bypasses Discord (e.g., admin tests, scripted events).
- `say <message>` (alias for `msg`)

### Rewards
- `give <user> <Module.Item> [count]`
- `xp <user> <Perk>=<amount>`
- `vehicle <VehicleScript> <user>`

### Events
- `horde <count> [user]`
- `chopper`
- `gunshot`
- `alarm`
- `lightning [user]`
- `thunder [user]`

### Weather
- `rain start [intensity]`
- `rain stop`
- `rain <intensity>`
- `storm [hours]`
- `clear` / `weather-stop`

### Raw passthrough
- `raw <rcon command...>`
- `cmd <rcon command...>`

## Example usage

```bash
# SIMON broadcasts go through Discord #pz-molt — no RCON `msg` call needed.
# The cron's announce delivery mirrors text to #pz-molt, and PZ's chat relay
# mirrors #pz-molt → in-game. Just output the broadcast as your final turn.
scripts/pz-rcon.sh give Player1 Base.CannedBeans 3
scripts/pz-rcon.sh xp Player1 Mechanics=25
scripts/pz-rcon.sh vehicle Base.PickUpVan Player1
scripts/pz-rcon.sh horde 35 Player1
scripts/pz-rcon.sh chopper
scripts/pz-rcon.sh rain start 40
scripts/pz-rcon.sh storm 2
scripts/pz-rcon.sh clear

# Admin escape hatch only — bypasses Discord mirror, in-game only.
# Do not use from SIMON.
scripts/pz-rcon.sh msg "Admin test: server-only broadcast, no Discord mirror."
```

## Raw PZ commands (for passthrough reference)

- `servermsg "..."`
- `players`
- `additem "user" Item count`
- `addxp "user" Perk=amount`
- `addvehicle "VehicleScript" "user"`
- `createhorde count "user"`
- `chopper`, `gunshot`, `alarm`, `lightning "user"`, `thunder "user"`
- `startrain [1-100]`, `stoprain`, `startstorm [hours]`, `stopweather`
