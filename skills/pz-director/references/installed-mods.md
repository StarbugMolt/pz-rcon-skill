# PZ Server Mod Reference — Live Pack (2026-08-14)

This file is the authoritative checked-in record of the server's currently enabled Project Zomboid mods supplied by the operator.

Do not use older mod recommendations, remembered server configurations or model knowledge as a substitute for this list.

## Server `Mods=` value

```ini
Mods=\BreakBigRocks;\SKITTLE_LongTermPreservation4220;\ImmersiveReading;\RVTrailerTypeB42;\KI5trailers;\damnlib;\InjuredZombiesStumble;\LEGION18;\StarlitLibrary;\ProjectArcade;\HereGoesTheSun;\OCsPacking;\DeadMansDossier;\ResearchLabInternProfession;\70fordEscort;\95impreza;\96lancerEVO;\70roadRunner;\69charger;\82porsche911;\81deloreanDMC12;\CrowbarScrewdriverEntry;\CorvusNVG;\MoodleFramework;\DBFaster25;\Ladders42131;\DBNO_DownButNotOut;\SapphCooking_B42;\PROJECTRVInterior42;\BCR;\BCR-IAmNotYourMom;\DashRoamerB42;\87fordB700;\SkillJournal;\ZeroWeightKeys_B42;\Dry&Cure;\ProximityInventory;\ZEasyMove
```

## Server `WorkshopItems=` value

```ini
WorkshopItems=3538602374;3774789651;3606009875;3775310562;3330403100;3171167894;3648051123;3665548194;3378285185;3645980077;3618557184;3626823538;3675740871;3615135168;3670063857;3647735736;3647736504;3642935062;3631989559;3379334330;3253385114;3770164353;3769335201;3396446795;3393821407;3629835761;3774055538;3409143790;3543229299;3660382016;3745224257;3775809123;3110911330;3776641628;3776502124;3776848101;2847184718;3692079035
```

There are **38 Mod IDs and 38 Workshop IDs**, paired position-for-position below.

| # | Mod ID | Workshop ID | SIMON asset-use note |
|---:|---|---:|---|
| 1 | BreakBigRocks | 3538602374 | Use checked-in mod reference only |
| 2 | SKITTLE_LongTermPreservation4220 | 3774789651 | Use checked-in mod reference only |
| 3 | ImmersiveReading | 3606009875 | Use checked-in mod reference only |
| 4 | RVTrailerTypeB42 | 3775310562 | Use checked-in mod reference only |
| 5 | KI5trailers | 3330403100 | Use checked-in mod reference only |
| 6 | damnlib | 3171167894 | Framework/library; do not assume spawnable assets |
| 7 | InjuredZombiesStumble | 3648051123 | Gameplay behavior; do not assume spawnable assets |
| 8 | LEGION18 | 3665548194 | Use checked-in mod reference only |
| 9 | StarlitLibrary | 3378285185 | Framework/library; do not assume spawnable assets |
| 10 | ProjectArcade | 3645980077 | Use checked-in mod reference only |
| 11 | HereGoesTheSun | 3618557184 | Use checked-in mod reference only |
| 12 | OCsPacking | 3626823538 | Use checked-in mod reference only |
| 13 | DeadMansDossier | 3675740871 | Use checked-in mod reference only |
| 14 | ResearchLabInternProfession | 3615135168 | Profession/content; use checked-in reference only |
| 15 | 70fordEscort | 3670063857 | Vehicle scripts must come from checked-in reference |
| 16 | 95impreza | 3647735736 | Vehicle scripts must come from checked-in reference |
| 17 | 96lancerEVO | 3647736504 | Vehicle scripts must come from checked-in reference |
| 18 | 70roadRunner | 3642935062 | Vehicle scripts must come from checked-in reference |
| 19 | 69charger | 3631989559 | Vehicle scripts must come from checked-in reference |
| 20 | 82porsche911 | 3379334330 | Vehicle scripts must come from checked-in reference |
| 21 | 81deloreanDMC12 | 3253385114 | Vehicle scripts must come from checked-in reference |
| 22 | CrowbarScrewdriverEntry | 3770164353 | Gameplay behavior; use checked-in reference only |
| 23 | CorvusNVG | 3769335201 | Use checked-in mod reference only |
| 24 | MoodleFramework | 3396446795 | Framework; do not assume spawnable assets |
| 25 | DBFaster25 | 3393821407 | Gameplay behavior; do not assume spawnable assets |
| 26 | Ladders42131 | 3629835761 | Use checked-in mod reference only |
| 27 | DBNO_DownButNotOut | 3774055538 | Gameplay system; use checked-in reference only |
| 28 | SapphCooking_B42 | 3409143790 | Use checked-in mod reference only |
| 29 | PROJECTRVInterior42 | 3543229299 | Gameplay/vehicle interior system; use checked-in reference only |
| 30 | BCR | 3660382016 | Use checked-in mod reference only |
| 31 | BCR-IAmNotYourMom | 3745224257 | Add-on; use checked-in reference only |
| 32 | DashRoamerB42 | 3775809123 | Use checked-in mod reference only |
| 33 | 87fordB700 | 3110911330 | Vehicle scripts must come from checked-in reference |
| 34 | SkillJournal | 3776641628 | Use checked-in mod reference only |
| 35 | ZeroWeightKeys_B42 | 3776502124 | Gameplay behavior; do not assume spawnable assets |
| 36 | Dry&Cure | 3776848101 | Use checked-in mod reference only |
| 37 | ProximityInventory | 2847184718 | Utility/UI mod. No spawnable asset IDs are authorized from its Workshop description. |
| 38 | ZEasyMove | 3692079035 | Utility/furniture-moving mod. No spawnable asset IDs are authorized from its Workshop description. |

## Special notes for the two latest additions

### ProximityInventory — Workshop 2847184718

The Workshop page identifies `Mod ID: ProximityInventory` and describes a nearby-container inventory UI that aggregates close containers and allows taking items through that interface. The page/title currently contains contradictory B42 messaging (`Broken on 42.13` while the description says it was updated for B42), so treat its runtime compatibility as an operator-observed fact rather than something SIMON should infer from the page.

It does **not** provide a verified spawnable item namespace in the Workshop description. Therefore its catalogue entry is descriptive-only and must not authorize invented item IDs.

### ZEasyMove — Workshop 3692079035

The Workshop page identifies `Mod ID: ZEasyMove`. It changes furniture-moving behavior so furniture with contents can be moved using carts/trolleys, with compatibility notes for cart mods and Project RV Interior.

The Workshop description says it was tested on Build 42.15 single-player and explicitly says multiplayer was not tested there. Treat it as an enabled utility mod, but do not manufacture item/vehicle identifiers from its name or description.

## SIMON rules for this list

1. `Mods=` is the enabled-mod authority for catalogue scope.
2. `WorkshopItems=` records the paired Workshop installation IDs; it is metadata, not an item namespace.
3. A mod being enabled does **not** prove that it contributes spawnable items or vehicles.
4. SIMON may use only exact item/vehicle identifiers documented in the corresponding checked-in active reference file.
5. Descriptive-only references authorize knowledge about a mod's behavior, not server mutations.
6. If an enabled mod lacks a verified asset ID for what SIMON wants to do, SIMON must not guess one.
