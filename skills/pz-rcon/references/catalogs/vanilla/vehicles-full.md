# Vanilla Vehicle Script Reference (Project Zomboid)

> Scope: **vanilla only** (no mods)
> Format for RCON `addvehicle`: vehicle script string (usually `Base.*`)

## Common Vanilla Vehicle Scripts
- `Base.CarNormal`
- `Base.SmallCar`
- `Base.SmallCar02`
- `Base.CarStationWagon`
- `Base.PickUpVan`
- `Base.PickUpTruck`
- `Base.Van`
- `Base.VanSeats`
- `Base.VanAmbulance`
- `Base.PickUpVanLights`
- `Base.StepVan`
- `Base.SUV`
- `Base.ModernCar`
- `Base.OffRoad`

## Service / Special
- `Base.PickUpTruckLightsFire`
- `Base.PickUpVanLightsPolice`
- `Base.VanAmbulance`

## Notes
- Not every map cell accepts spawning; invalid terrain gives "Invalid position".
- For best success, player should stand on open road/parking tiles.
- Fuel/condition/keys are not guaranteed by basic `addvehicle` alone.
