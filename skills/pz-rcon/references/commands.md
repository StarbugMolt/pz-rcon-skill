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
- `msg <message>`
- `say <message>` (alias)

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
scripts/pz-rcon.sh msg "Emergency band: stay indoors tonight."
scripts/pz-rcon.sh give Player1 Base.CannedBeans 3
scripts/pz-rcon.sh xp Player1 Mechanics=25
scripts/pz-rcon.sh vehicle Base.PickUpVan Player1
scripts/pz-rcon.sh horde 35 Player1
scripts/pz-rcon.sh chopper
scripts/pz-rcon.sh rain start 40
scripts/pz-rcon.sh storm 2
scripts/pz-rcon.sh clear
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
