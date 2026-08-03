# PZ Server Mod Reference — 2026-04-30

## Server Config (GTXGaming.ini)

### Mods (22)
```
\RotatorsLib;\StarlitLibrary;\PROJECTRVInterior42;\DBFaster50;\SapphCooking_B42;\randomairdropsASVOD;\SearchModeAPI41;\Maplewood;\SimpleOverhaulTraitsAndOccupations;\FunctionalGutters;\ReloadAllMagazines;\ImmersiveReading;\GydeTraitMags;\DeadMansDossier;\BreakBigRocks;\BurdSurvivalJournals;\NeatUI_Framework;\CommonSenseReborn;\SawAllLogsDropPlanks;\ModernStatus;\InjuredZombiesStumble;\dustinguished_bolt_cutters
```

### WorkshopItems (24)
```
3393821407;3409143790;3655233584;2851764922;3644794945;3653962453;2840805724;3439305933;2920899878;3606009875;3378285185;3543229299;3342191739;3675740871;3538602374;3409472393;3639628777;3508537032;3698958906;3713359427;3713977259;3451167732;3648051123;3671176591
```

### Map
```
Maplewood;map_distanciado;Muldraugh, KY
```

## Workshop ID → Mod ID Mapping

| Workshop ID | Mod ID | Mod Name | Status |
|---|---|---|---|
| 3393821407 | DBFaster50 | Drag Bodies Faster 50% | ✅ Working |
| 3409143790 | SapphCooking_B42 | Sapph's Cooking | ✅ Working |
| 3655233584 | randomairdropsASVOD | Random Airdrops | ✅ Working |
| 2851764922 | SearchModeAPI41 | Search Mode API | ✅ Working |
| 3644794945 | Maplewood | Maplewood Map | ✅ Working |
| 3653962453 | randomairdropsASVOD | Random Airdrops (alt) | ✅ Working |
| 2840805724 | SimpleOverhaulTraitsAndOccupations | SOTO Traits | ✅ Working |
| 3439305933 | FunctionalGutters | Functional Gutters | ✅ Working |
| 2920899878 | ReloadAllMagazines | Reload All Magazines | ✅ Working |
| 3606009875 | ImmersiveReading | Immersive Reading | ✅ Working |
| 3378285185 | StarlitLibrary | Starlit Library | ✅ Working |
| 3543229299 | PROJECTRVInterior42 | RV Interior | ✅ Working |
| 3342191739 | GydeTraitMags | Gyde's Trait Magazines | ✅ Working |
| 3675740871 | DeadMansDossier | Dead Man's Dossier | ✅ Working |
| 3538602374 | BreakBigRocks | Break Big Rocks | ✅ Working |
| 3409472393 | RotatorsLib | RotatorsLib | ✅ Working (with root mod.info fix) |
| 3639628777 | BurdSurvivalJournals | Burd's Survival Journals | ✅ Working |
| 3508537032 | NeatUI_Framework | NeatUI Framework | ✅ Working |
| 3698958906 | CommonSenseReborn | Common Sense Reborn | ✅ Working |
| 3713359427 | dustinguished_bolt_cutters | Bolt Cutters | ✅ Working |
| 3713977259 | SawAllLogsDropPlanks | Saw All Logs Drop Planks | ✅ Working |
| 3451167732 | ModernStatus | Modern Status HUD | ✅ Working |
| 3648051123 | InjuredZombiesStumble | Injured Zombies Stumble | ✅ Working |
| 3671176591 | dustinguished_bolt_cutters | Bolt Cutters (alt) | ✅ Working |

## New Mods to Add (10)

| Workshop ID | Mod ID (guess) | Mod Name |
|---|---|---|
| 3429176285 | CampInTheRain | Camp in the Rain |
| 2335368829 | AuthenticZ | Authentic Z |
| 3504753006 | ThumpWithFriends | Thump with Friends |
| 3607686447 | ImmersiveBlackouts | Immersive Blackouts |
| 3433203442 | ZuperCarts | ZuperCarts |
| 3627047348 | MultiplayerBugFixes | MP Bug Fixes |
| 2804531012 | DrawOnTheMap | Draw On The Map |
| 3526517370 | MinimapOptions | Minimap Style Options |
| 2650547917 | ManageContainers | Manage Containers |
| 345661 | TrueMusic | True Music (B42 fork) |

## Notes
- RotatorsLib needed a root mod.info fix (already applied to disk)
- rSemiTruck folder deleted from RotatorsLib workshop item (was causing dependency warning)
- HaikuPrimitive removed (Lua errors)
- AZAGRAFFITI42 removed (workshop item deleted by author)
- tsarslib + Autotsar Trailers removed (broken on 42.17)
- Hosting panel overwrites GTXGaming.ini on restart — need to use panel or find workaround
