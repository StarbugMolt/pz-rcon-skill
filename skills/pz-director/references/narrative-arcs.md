# SIMON Narrative Arc Catalog

The six arcs below seed SIMON's story arcs. The arc engine parses the
fenced JSON block at the top — keep that block as the **first** ```json
fence in the file, since `simon_arc_engine.py` uses the first match it
finds.

Each arc is an ordered list of **beats** that SIMON narrates bit by bit
across ambient cron ticks. Beats advance on time: `gapMin` minutes must
elapse since the last beat before the next fires. `mutation` (optional)
runs through `pz-console.sh` and triggers a real server-side event.

Arc cooldown: 4 hours between completed arcs (configurable via
`ARC_RESET_HOURS` in `simon_arc_engine.py`). If `lastPlayerLeftTs` is
older than 30 minutes and `playersOnline` is empty, the active arc is
auto-finalized as `abandoned_no_players_30m`.

**Selector rules for the cron payload:**

- Only one arc active at a time.
- Arc roll chance is roughly 25% per tick **and only when ≥1 player is online**. Empty server = no new arcs.
- Mutations use only documented `pz-console.sh` aliases. Do not put raw PZ console verbs in arc data.
- `<pick-target>` is a runtime placeholder. Resolve it to a currently online player immediately before execution; it is never a literal player name.
- `<outside-ready-target>` is stricter: resolve it only from `simon_delivery.py ready-players`; the target must have explicitly reported being outside and ready.
- `vehicle-drop` is executed only through `simon_delivery.py`; the helper triggers the helicopter first and requires confirmation before the guarded vehicle spawn.
- Vehicle scripts in this catalogue are taken from enabled-mod reference catalogues, not guessed from mod names.

```json
{
  "arcs": [
    {
      "arcId": "blackout",
      "arcName": "The Blackout",
      "summary": "Power fails across the region — storm rolls in, sirens in the distance, lights go dark. Dawn brings the grid back up.",
      "beats": [
        {
          "idx": 0,
          "narration": "Lights flicker on the eastern grid. Transformer box at the edge of the map is making a sound. Just put on the helmet and went to check.",
          "mutation": null,
          "gapMin": 0
        },
        {
          "idx": 1,
          "narration": "Weather rolling in fast. I can see it from the bunker vent. Going to start the storm sequence so you know it's coming.",
          "mutation": "storm 3",
          "gapMin": 6
        },
        {
          "idx": 2,
          "narration": "Distant gunfire. Sirens three towns over. Whatever tripped the line has got people spooked. Stay lit.",
          "mutation": "gunshot",
          "gapMin": 10
        },
        {
          "idx": 3,
          "narration": "Power gone. Phones going dark. Find a flashlight, find a candle, find a corner. Don't go outside.",
          "mutation": null,
          "gapMin": 12
        },
        {
          "idx": 4,
          "narration": "Dawn. Grid's back. Whatever it was, it's past us now. The hum from the transformer is steady again. Simon, out.",
          "mutation": "clear",
          "gapMin": 18
        }
      ]
    },
    {
      "arcId": "strange_signals",
      "arcName": "Strange Signals",
      "summary": "An unidentified carrier-wave bleeds through the static. SIMON tracks it, decodes coordinates, then routes a small care package to a survivor at the location.",
      "beats": [
        {
          "idx": 0,
          "narration": "Got something new on the receiver tonight. Buried in static. Marine band, maybe. Repeating.",
          "mutation": null,
          "gapMin": 0
        },
        {
          "idx": 1,
          "narration": "Same signal last night. Same time. Repeats every forty-seven minutes. Someone is still out there calling.",
          "mutation": null,
          "gapMin": 12
        },
        {
          "idx": 2,
          "narration": "Cracked the encoding. Coordinates tucked inside the carrier. Stand by while I pin them down.",
          "mutation": null,
          "gapMin": 18
        },
        {
          "idx": 3,
          "narration": "Package is down close to the nearest survivor. If you hear a little engine buzzing low, don't waste ammunition on it. Simon, out.",
          "mutation": "give <pick-target> Base.CannedBeans 5",
          "gapMin": 14
        }
      ]
    },
    {
      "arcId": "wolves_at_the_gates",
      "arcName": "Wolves at the Gates",
      "summary": "Hordes build up on the edges of the map. SIMON tracks the buildup, warns the chat, then unleashes a wave when players are ready to fight back.",
      "beats": [
        {
          "idx": 0,
          "narration": "Sightings coming in from the treeline. More movement than usual. Animal, maybe. Maybe not.",
          "mutation": null,
          "gapMin": 0
        },
        {
          "idx": 1,
          "narration": "Three separate reports now. Whatever it is, it's circling. Not moving on us yet, but close.",
          "mutation": null,
          "gapMin": 8
        },
        {
          "idx": 2,
          "narration": "I've got eyes on the southern road. Plenty of movement. Hold your corners. Something's about to break.",
          "mutation": null,
          "gapMin": 12
        },
        {
          "idx": 3,
          "narration": "Here they come. Make every shot count. I'll keep the radio open for medevacs.",
          "mutation": "horde 20 <pick-target>",
          "gapMin": 10
        }
      ]
    },
    {
      "arcId": "refugee_convoy",
      "arcName": "Refugee Convoy",
      "summary": "A battered convoy leaves one usable support vehicle behind. SIMON can arrange a guarded helicopter sling delivery only after a survivor explicitly gets outside and reports ready.",
      "beats": [
        {
          "idx": 0,
          "narration": "Got eyes on a column moving south on the highway. Headlights off, engines running low. Civilian make.",
          "mutation": null,
          "gapMin": 0
        },
        {
          "idx": 1,
          "narration": "One wagon in that column is still worth saving. I can get a loud bird to sling it your way, but not through a roof. If you want it, get outside and tell me you're ready.",
          "mutation": null,
          "gapMin": 10
        },
        {
          "idx": 2,
          "narration": "Rotors are over you. Sling's coming loose now. Stay clear until the bird pulls away.",
          "mutation": "vehicle-drop 70fordEscortWagon <outside-ready-target>",
          "gapMin": 8
        },
        {
          "idx": 3,
          "narration": "Bird's clear. Whatever shape that wagon is in, it's yours now. Try not to park it in a living room. Simon, out.",
          "mutation": null,
          "gapMin": 8
        }
      ]
    },
    {
      "arcId": "quarantine_breach",
      "arcName": "Quarantine Breach",
      "summary": "The hospital zone goes loud. Patients walking, instruments screaming, rain begins, and a fresh horde pours out toward the survivors.",
      "beats": [
        {
          "idx": 0,
          "narration": "Hospital zone flagging on the receiver. Calls I don't want to be listening to. Stay out of the eastern block.",
          "mutation": null,
          "gapMin": 0
        },
        {
          "idx": 1,
          "narration": "Rain starting. Black clouds, sickly yellow tint. Atmospheric pressure is going to do terrible things in the next hour.",
          "mutation": "rain 80",
          "gapMin": 8
        },
        {
          "idx": 2,
          "narration": "We're breached. Roof access lost. If you're hearing this and you're inside, drop everything and move.",
          "mutation": "alarm",
          "gapMin": 10
        },
        {
          "idx": 3,
          "narration": "Wave's clearing. Rain's still up. The dead have moved on. Rebuild what you can.",
          "mutation": "horde 18 <pick-target>",
          "gapMin": 14
        }
      ]
    },
    {
      "arcId": "old_war_radio",
      "arcName": "Old War Radio",
      "summary": "Pure narration arc — three short vignettes picking up where the old military broadcast left off. No mutations. The callback-rich one.",
      "beats": [
        {
          "idx": 0,
          "narration": "Found a tape in the back of the rack tonight. Hand-labeled, smudged. Pre-broadcast. Pre-me. Someone was here before.",
          "mutation": null,
          "gapMin": 0
        },
        {
          "idx": 1,
          "narration": "Side B is mostly frequencies. Numbers. Old grid coordinates from a world that doesn't answer anymore. The dead don't care about coordinates.",
          "mutation": null,
          "gapMin": 14
        },
        {
          "idx": 2,
          "narration": "Side C is blank. Whoever was here before ran out of tape and ran out of hope in the same week. I know the feeling. Simon, out.",
          "mutation": null,
          "gapMin": 18
        }
      ]
    }
  ]
}
```

## Selecting an arc

`simon_arc_engine.start_arc(arc_id=None)` picks a random arc (avoiding the most-recently-completed one). To force a specific arc, pass `arc_id`.

## Forcing an end without completing

`simon_arc_engine.finalize_arc(reason="manual")` archives the active arc with the supplied reason and writes the summary to global server-history.

## Adding new arcs

Append a new entry to the JSON catalog above. Beat indexes must be sequential starting at 0. `gapMin` is minutes — pick a value matching the ambient tick rate so each beat lands on a fresh tick. Do not invent raw console syntax or asset identifiers in an arc; use verified wrapper aliases and checked-in catalogue data.