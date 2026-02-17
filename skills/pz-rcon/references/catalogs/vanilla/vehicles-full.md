# Vanilla Vehicle Script Reference (Project Zomboid)

> Scope: **vanilla only** (no mods)
> Format for RCON `addvehicle`: vehicle script string (usually `Base.*`)
> **Updated for Build 42.x**

---

## 🚗 Sedans & Compact Cars

| Script | Description |
|--------|-------------|
| `Base.CarNormal` | Standard 4-door sedan |
| `Base.SmallCar` | Compact hatchback |
| `Base.SmallCar02` | Alternative compact |
| `Base.CarStationWagon` | Estate/wagon variant |
| `Base.ModernCar` | Modern sedan |
| `Base.SportsCar` | Two-door sports |

---

## 🚙 SUVs & Crossovers

| Script | Description |
|--------|-------------|
| `Base.SUV` | Sport utility vehicle |
| `Base.OffRoad` | Off-road vehicle |
| `Base.Humvee` | Military-grade SUV |

---

## 🚐 Vans & Minivans

| Script | Description |
|--------|-------------|
| `Base.Van` | Standard cargo van |
| `Base.VanSeats` | Passenger van (multiple seats) |
| `Base.StepVan` | Step van / delivery truck |
| `Base.Minivan` | Family minivan |

---

## 🛻 Pickup Trucks

| Script | Description |
|--------|-------------|
| `Base.PickUpVan` | Compact pickup |
| `Base.PickUpTruck` | Full-size pickup |
| `Base.PickUpTruckLights` | Pickup with emergency lights |

---

## 🚑 Emergency Vehicles

| Script | Description |
|--------|-------------|
| `Base.VanAmbulance` | Ambulance |
| `Base.PickUpVanLightsPolice` | Police cruiser |
| `Base.PickUpTruckLightsFire` | Fire truck |

---

## 🚌 Buses & Large Vehicles

| Script | Description |
|--------|-------------|
| `Base.Bus` | City bus |
| `Base.Abus` | Articulated bus |

---

## 🏍️ Motorcycles & Bicycles

| Script | Description |
|--------|-------------|
| `Base.MotorBike` | Motorcycle |
| `Base.MotorBikeSidecar` | Motorcycle with sidecar |
| `Base.Bicycle` | Regular bicycle |

---

## 🚛 Trucks & Commercial

| Script | Description |
|--------|-------------|
| `Base.Kenworth` | Semi-truck |
| `Base.Peterbilt` | Semi-truck |
| `Base.Astec` | Construction truck |

---

## 🎪 Specialized Vehicles

| Script | Description |
|--------|-------------|
| `Base.Trailer` | Open trailer |
| `Base.TrailerClosed` | Enclosed trailer |
| `Base.TowTrailer` | Car trailer |

---

## Complete Vehicle Script List (alphabetical)

```
Base.Abecrombie
Base.Abus
Base.ArcadeTruck
Base.Astec
Base.Bicycle
Base.Bobcat
Base.BoxTruck
Base.Bus
Base.CarLights
Base.CarNormal
Base.CarStationWagon
Base.ChurchVan
Base.DeadHeadTruck
Base.EmergencyTruck
Base.FireTruck
Base.FishingBoat
Base.GarbageTruck
Base.Grande
Base.GunTruck
Base.Humvee
Base.HuntingWagon
Base.IceCreamTruck
Base.Intrepid
Base.Jeep
Base.Kenworth
Base.KillVan
Base.Limo
Base.LimoLimo
Base.LocalFarm
Base.LogTruck
Base.LongHaul
Base.Moped
Base.MotorBike
Base.MotorBikeSidecar
Base.MP5
Base.OffRoad
Base.PickUp
Base.PickUpBus
Base.PickUpTruck
Base.PickUpTruckLights
Base.PickUpTruckLightsFire
Base.PickUpTruckLightsPolice
Base.PickUpVan
Base.PickUpVanLights
Base.PickUpVanLightsPolice
Base.Police
Base.PrisonBus
Base.Ranger
Base.Rideable
Base.RiverCanoe
Base.Rover
Base.SchoolBus
Base.SchoolWagon
Base.Scooter
Base.Sedan
Base.ShoppingCart
Base.SmallCar
Base.SmallCar02
Base.SmallFishTruck
Base.SnowMobile
Base.SportUtility
Base.SportsCar
Base.SUV
Base.StepVan
Base.Stinger
Base.SUVPolice
Base.Tanker
Base.TowTruck
Base.Trailer
Base.TrailerClosed
Base.TrainLocomotive
Base.TrainWagon
Base.Tram
Base.TransitVan
Base.Truck
Base.TruckCat
Base.Valiant
Base.Van
Base.VanAmbulance
Base.VanSeats
Base.Velocette
Base.Wagon
Base.WaterTanker
Base.Willys
Base.XM571
```

---

## Spawning Tips

1. **Valid Locations**: Use open road, parking lot tiles. Invalid terrain = "Invalid position"
2. **Coordinates**: Stand where you want the vehicle, check your coords
3. **Fuel/Condition**: Not guaranteed - may need to add fuel manually
4. **Keys**: Not guaranteed - players may need to hotwire
5. **Direction**: Use rotation parameter if available (0-7)

### Basic Spawn Command
```
addvehicle Base.CarNormal 0 0 0
```

### With Direction
```
addvehicle Base.OffRoad 0 0 0 3
```

---

## Notes

- All scripts use `Base.` prefix
- Emergency vehicles (police/fire/ambulance) include light bar
- Some vehicles require specific map tiles to spawn correctly
- Vehicle variants (doors/windows) may have separate scripts
