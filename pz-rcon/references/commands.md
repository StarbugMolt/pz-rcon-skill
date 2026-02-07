# Project Zomboid RCON Commands - Event & Atmosphere Reference

This reference covers commands for player interaction, rewards, events, and weather.

---

## Broadcasting Messages

### servermsg
Broadcast a message to all connected players.
```
servermsg "Your message here"
```

**Tips for atmospheric messages:**
- Use radio broadcast framing: *"Emergency broadcast system: ..."*
- Add mystery: *"Strange sounds reported near the warehouse..."*
- Weather warnings before storms
- Survival tips that feel in-universe

---

## Player List

### players
List all connected players (for targeting rewards/events).
```
players
```

---

## Items & Rewards

### additem
Give an item to a player.
```
additem "username" <Module.Item> <count>
```

**Examples:**
```
additem "Player1" Base.Axe 1
additem "Player1" Base.Shotgun 1
additem "Player1" Base.9mmClip 3
additem "Player1" Base.WaterBottleFull 5
```

**Common Item Codes:**

| Category | Items |
|----------|-------|
| Melee | `Base.Axe`, `Base.BaseballBat`, `Base.Crowbar`, `Base.Hammer`, `Base.Katana`, `Base.Machete` |
| Firearms | `Base.Pistol`, `Base.Shotgun`, `Base.HuntingRifle`, `Base.AssaultRifle` |
| Ammo | `Base.9mmClip`, `Base.ShotgunShells`, `Base.308Clip`, `Base.223Clip` |
| Medical | `Base.Bandage`, `Base.FirstAidKit`, `Base.Antibiotics`, `Base.PainKillers` |
| Food | `Base.WaterBottleFull`, `Base.CannedBeans`, `Base.CannedCorn`, `Base.Apple` |
| Tools | `Base.Saw`, `Base.Screwdriver`, `Base.Wrench`, `Base.WeldingMask` |

Full list: https://pzwiki.net/wiki/Items

### addxp
Give experience points to a player's perk.
```
addxp "username" <PerkName>=<amount>
```

**Examples:**
```
addxp "Player1" Carpentry=100
addxp "Player1" Aiming=50
addxp "Player1" Fitness=200
addxp "Player1" Mechanics=150
```

**Perk Names:**

| Category | Perks |
|----------|-------|
| Passive | `Fitness`, `Strength` |
| Agility | `Sprinting`, `Lightfooted`, `Nimble`, `Sneaking` |
| Melee | `Axe`, `Blunt`, `SmallBlade`, `LongBlade`, `Spear`, `Maintenance` |
| Ranged | `Aiming`, `Reloading` |
| Crafting | `Carpentry`, `Cooking`, `Farming`, `Tailoring`, `MetalWelding` |
| Technical | `Electricity`, `Mechanics` |
| Survival | `Fishing`, `Trapping`, `Foraging` |
| Medical | `Doctor` |

### addvehicle
Spawn a vehicle near a player.
```
addvehicle "<VehicleScript>" "<username>"
```

**Examples:**
```
addvehicle "Base.VanAmbulance" "Player1"
addvehicle "Base.PickUpVan" "Player1"
addvehicle "Base.CarStationWagon" "Player1"
```

**Vehicle Types:**
- `Base.CarNormal` - Standard car
- `Base.CarStationWagon` - Station wagon
- `Base.PickUpVan` - Pickup truck
- `Base.Van` - Van
- `Base.VanAmbulance` - Ambulance
- `Base.ModernCar` - Modern vehicle

---

## World Events

### createhorde
Spawn a zombie horde near a player.
```
createhorde <count> "username"
```

**Examples:**
```
createhorde 25 "Player1"   # Small group
createhorde 50 "Player1"   # Medium horde
createhorde 100 "Player1"  # Large horde
```

**Narrative pattern:**
```
servermsg "Movement detected in large numbers heading toward [area]..."
# pause
createhorde 50 "TargetPlayer"
```

### chopper
Trigger a helicopter flyover event on a random player.
```
chopper
```
The helicopter attracts zombies toward the targeted player's location.

**Narrative pattern:**
```
servermsg "A helicopter is spotted on the horizon..."
chopper
servermsg "It's drawing them in. Find cover!"
```

### gunshot
Create a gunshot sound near a random player (attracts zombies).
```
gunshot
```

### alarm
Sound a building alarm at the admin's position.
```
alarm
```
Note: Admin must be inside a building room.

### lightning
Strike lightning near a player.
```
lightning "username"
```

### thunder
Thunder sound near a player.
```
thunder "username"
```

---

## Weather Control

### startrain
Start rain on the server.
```
startrain
startrain <intensity>
```
Intensity: 1-100 (optional)

### stoprain
Stop rain.
```
stoprain
```

### startstorm
Start a thunderstorm.
```
startstorm
startstorm <duration>
```
Duration in game hours (optional).

### stopweather
Stop all weather effects immediately.
```
stopweather
```

**Weather narrative pattern:**
```
servermsg "Dark clouds gather on the horizon..."
startrain 30
# later
servermsg "The storm intensifies. Visibility is dropping."
startstorm 2
# later
servermsg "The worst seems to have passed."
stopweather
```

---

## Narrative Event Ideas

### Supply Reward
```
servermsg "Attention survivors: Military supply cache coordinates received."
servermsg "Grid reference [made up location]. First come, first served."
additem "LuckyPlayer" Base.Shotgun 1
additem "LuckyPlayer" Base.ShotgunShells 20
```

### Sudden Horde
```
servermsg "Warning: Seismic sensors detecting heavy movement from the east..."
servermsg "All survivors near [area], evacuate immediately."
createhorde 75 "TargetPlayer"
```

### Helicopter Rescue Gone Wrong
```
servermsg "Breaking: Rescue helicopter en route to Knox County."
servermsg "Survivors, signal if you can!"
chopper
servermsg "...We've lost contact with the aircraft. Status unknown."
```

### Mysterious Broadcast
```
servermsg "Emergency broadcast system: *static* ...don't trust... *static* ...they're not..."
servermsg "Signal lost."
```

### Weather Warning
```
servermsg "National Weather Service: Severe storm warning in effect until dawn."
startstorm 4
servermsg "Seek shelter immediately. Do not travel."
```
