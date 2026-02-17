# Vanilla Item Reference (Project Zomboid)

> Scope: **vanilla only** (no mods)
> Format for RCON: `Module.Item`
> Typical module is `Base`.
> **Updated for Build 42.14**

## Food & Drink
- `Base.Crisps`
- `Base.CannedBeans`
- `Base.CannedCorn`
- `Base.CannedSoup`
- `Base.TunaTin`
- `Base.WaterBottleFull`
- `Base.PopBottle`
- `Base.BeerCan`
- `Base.WhiskeyFull`

## Medical
- `Base.Bandage`
- `Base.AlcoholWipes`
- `Base.AlcoholBandage`
- `Base.Disinfectant`
- `Base.FirstAidKit`
- `Base.Pills`
- `Base.Painkillers`
- `Base.Antibiotics`
- `Base.SutureNeedle`

## Melee Weapons
- `Base.Axe`
- `Base.Crowbar`
- `Base.BaseballBat`
- `Base.Hammer`
- `Base.KitchenKnife`
- `Base.Machete`
- `Base.Sledgehammer`

## Firearms & Ammo

### Handguns
- `Base.Pistol`
- `Base.Revolver` **(Build 42.14: now uses .357 Magnum)**
- `Base.9mmClip`

### Rifles
- `Base.HuntingRifle`
- `Base.AssaultRifle`
- `Base.MSR700` / `Base.VarmintRifle` **(Build 42.14: now uses 5.56mm, was .223)**
- `Base.556Box` **(Build 42.14: new - replaced .223)**
- `Base.556Bullets`
- `Base.556Carton`

### Shotguns
- `Base.Shotgun`
- `Base.JS2000` **(Build 42.14: capacity changed from 6+1 to 5+1)**
- `Base.ShotgunShells`

### Legacy Ammo (Pre-42.14 references - may not spawn)
- `Base.223Box` **(DEPRECATED in 42.14 - replaced by 5.56mm)**
- `Base.223Bullets`
- `Base.45Box`

### Magnum Ammo (Build 42.14)
- `Base.357MagBox`
- `Base.357MagBullets`
- `Base.357MagCarton`

### Rifle Ammo (existing)
- `Base.308Box`
- `Base.308Bullets`

## Tools & Utility
- `Base.Screwdriver`
- `Base.Wrench`
- `Base.Saw`
- `Base.WeldingMask`
- `Base.PropaneTank`
- `Base.Generator`
- `Base.Lighter`
- `Base.Matches`

## Clothing / Bags
- `Base.Bag_DuffelBag`
- `Base.Bag_ALICEpack`
- `Base.Hat_Beany`
- `Base.Jacket_ArmyCamoGreen`

## Notes

### Build 42.14 Ammunition Changes (Critical)
- **MSR700/VarmintRifle**: Changed from .223 to 5.56mm
- **.223 ammunition**: Removed from loot tables entirely
- **Revolver**: Changed from .45 to .357 Magnum
- **Shotgun/JS2000**: Magazine capacity reduced from 6+1 to 5+1

### Verification
- If an item code fails, verify exact script name in game files/wiki
- This list updated for IWBUMS Beta 42.14.0
