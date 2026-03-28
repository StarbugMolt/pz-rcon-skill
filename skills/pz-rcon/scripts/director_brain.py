#!/usr/bin/env python3
import json
import sys
import os
import random
import time
import subprocess

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
STATE_FILE = os.path.join(SKILL_DIR, "state/narrative-state.json")
PLAYER_REGISTRY_FILE = os.path.join(SKILL_DIR, "state/player-registry.json")

# --- NARRATIVE MEMORY ---
sys.path.insert(0, SCRIPT_DIR)
from narrative_memory import NarrativeMemory

_nm = None  # lazy init

def get_nm() -> NarrativeMemory:
    global _nm
    if _nm is None:
        _nm = NarrativeMemory(SKILL_DIR)
    return _nm

def nm_log_broadcast(session_id: str, player: str, content: str):
    """Log a broadcast to session and player narrative."""
    nm = get_nm()
    nm.add_narrative_entry(session_id, "broadcast", content, player=player)
    if player:
        nm.add_narrative_entry(session_id, "broadcast", content, player=player)
        # Also record player context for continuity
        recent_beats = nm.get_player_recent_beats(player, hours=2)
        if recent_beats:
            beat = recent_beats[-1].get("beat", "")
            if beat:
                nm.record_player_storybeat(player, "simon_broadcast", detail=content[:80])

def nm_log_event(session_id: str, player: str, event_type: str, content: str, item: str = None):
    """Log an event to session and player story beats."""
    nm = get_nm()
    nm.add_narrative_entry(session_id, "event", content, player=player, event_type=event_type, item=item)
    if player:
        nm.record_player_storybeat(player, event_type, detail=content[:100])
    if item:
        nm.add_narrative_entry(session_id, "reward", f"{item} given to {player}", player=player, item=item)
        if player:
            nm.record_player_reward(player, event_type, item)

# --- PLAYER GREETING SYSTEM ---
def get_player_info(player_name):
    """Get player info from registry."""
    try:
        with open(PLAYER_REGISTRY_FILE, 'r') as f:
            registry = json.load(f)
        return registry.get("players", {}).get(player_name, None)
    except:
        return None

def get_player_honorific(player_name):
    """Get player honorific (sir/ma'am/survivor)."""
    info = get_player_info(player_name)
    if info and "honorific" in info:
        return info["honorific"]
    return "survivor"

def get_visit_tier(visit_count):
    """Determine player tier based on visit count."""
    if visit_count <= 1:
        return "new"
    elif visit_count <= 5:
        return "returning"
    elif visit_count <= 10:
        return "veteran"
    else:
        return "oldtimer"

def generate_player_greeting(player_name):
    """Generate personalized greeting based on player history."""
    info = get_player_info(player_name)
    if not info:
        # Fallback if no info
        return f"Welcome to Muldraugh, survivor. You'll need to learn fast."
    
    visits = info.get("visitCount", 1)
    tier = get_visit_tier(visits)
    
    greetings = {
        "new": [
            f"New arrival detected. Welcome to the apocalypse, {player_name}.",
            f"Unregistered signal... {player_name}? Welcome to Muldraugh. Good luck.",
            f"First time in sector, {player_name}? The zombies are hungry."
        ],
        "returning": [
            f"{player_name}! Back for more? The horde missed you. Probably.",
            f"Welcome back, {player_name}. Status: Still alive. That's something.",
            f"{player_name} returns. Let's hope you last longer this time."
        ],
        "veteran": [
            f"Veteran survivor {player_name} checking in. The undead await.",
            f"{player_name}, your survival instincts are noted. Good hunting.",
            f"Welcome back, {player_name}. Another day in paradise."
        ],
        "oldtimer": [
            f"Legend {player_name} lives! They said you'd be zombie food by now.",
            f"{player_name}. If anyone can survive this, it's you. Welcome back.",
            f"The Director remembers you, {player_name}. Let's make it another successful day."
        ]
    }
    
    return random.choice(greetings[tier])

def handle_player_join_event(new_players):
    """Handle new player join events with personalized greetings."""
    if not new_players:
        return []
    
    messages = []
    for player in new_players:
        greeting = generate_player_greeting(player)
        messages.append(greeting)
        # Send as broadcast (PZ RCON doesn't support PM)
        run_rcon(["msg", f"[{player}] {greeting}"])
    
    return messages

# --- EXPANDED PLOT THEMES ---
THEMES = {
    "MILITARY_COLLAPSE": {
        "name": "Operation Broken Shield",
        "prefixes": ["Command Net:", "Auto-Relay:", "Bio-Containment Unit:"],
        "flavor": [
            "Evacuation zones are compromised. Hold position.",
            "Unauthorized biological assets detected in sector 7.",
            "Orbital surveillance shows massive migration patterns.",
            "Do not approach military checkpoints. They are not staffed by the living."
        ],
        "rewards": {
            "vehicle": ["Base.PickUpVan", "Base.VanAmbulance", "Base.OffRoad"],
            "weapon": ["Base.AssaultRifle", "Base.Shotgun", "Base.556Box", "Base.308Box"],
            "medical": ["Base.FirstAidKit", "Base.Antibiotics", "Base.SutureNeedle"],
            "supply": ["Base.Generator", "Base.PropaneTank", "Base.CannedBeans"]
        }
    },
    "THE_STORM": {
        "name": "Hurricane Sigma",
        "prefixes": ["NWS Alert:", "Civil Defense:", "Weather Buoy 4:"],
        "flavor": [
            "Barometric pressure dropping rapidly. Seek shelter.",
            "Electrical interference clearing. The eye has passed.",
            "Flood waters rising in the Ohio river valley.",
            "Visibility near zero on main highways."
        ],
        "rewards": {
            "vehicle": ["Base.CarStationWagon", "Base.Van"],
            "weapon": ["Base.Axe", "Base.Crowbar", "Base.Machete"],
            "medical": ["Base.Bandage", "Base.Disinfectant"],
            "supply": ["Base.WaterBottleFull", "Base.Lighter", "Base.Matches", "Base.Bag_ALICEpack"]
        }
    },
    "THE_ANARCHY": {
        "name": "The Raider Wastes",
        "prefixes": ["Unknown Signal:", "Convoy 9:", "Looter Band:"],
        "flavor": [
            "They took the bridge... they took everyone...",
            "Beware the highwaymen near Muldraugh.",
            "If you can hear this, the safehouse at West Point is gone.",
            "Exchange: Will trade ammunition for antibiotics."
        ],
        "rewards": {
            "vehicle": ["Base.StepVan", "Base.PickUpTruck", "Base.SUV"],
            "weapon": ["Base.Pistol", "Base.9mmClip", "Base.Shotgun", "Base.ShotgunShells"],
            "medical": ["Base.Pills", "Base.Painkillers"],
            "supply": ["Base.WhiskeyFull", "Base.CannedSoup", "Base.TunaTin"]
        }
    },
    "MEDICAL_EVAC": {
        "name": "MEDEVAC Tango-4",
        "prefixes": ["MEDEVAC Relay:", "Field Hospital:", "Red Cross Net:"],
        "flavor": [
            "Triage site overrun. All personnel withdrawn.",
            "Patient zero confirmed in sector. Avoid all medical facilities.",
            "Blood supplies contaminated. Do not trust stockpiles.",
            "Field ambulance 7 reporting engine failure. Cannot extract."
        ],
        "rewards": {
            "vehicle": ["Base.VanAmbulance"],
            "weapon": ["Base.KitchenKnife", "Base.Scalpel"],
            "medical": ["Base.FirstAidKit", "Base.Antibiotics", "Base.SutureNeedle", "Base.AlcoholBandage"],
            "supply": ["Base.Bag_DuffelBag"]
        }
    },
    "WILDFIRE": {
        "name": "Red Sky Protocol",
        "prefixes": ["Fire Watch:", "Forestry Alert:", "Emergency Broadcast:"],
        "flavor": [
            "Wildfire crossed Highway 31. Winds pushing east.",
            "Smoke inhalation risk critical. Respirators mandatory.",
            "Evacuation route Alpha is compromised by flame front.",
            "Fire crews retreated. You are on your own."
        ],
        "rewards": {
            "vehicle": ["Base.PickUpTruckLightsFire", "Base.PickUpTruck"],
            "weapon": ["Base.Axe", "Base.Machete"],
            "medical": ["Base.Bandage", "Base.AlcoholWipes"],
            "supply": ["Base.WaterBottleFull", "Base.WeldingMask", "Base.PropaneTank"]
        }
    },
    "REFUGEE_CONVOY": {
        "name": "Exodus Line Charlie",
        "prefixes": ["Convoy Lead:", "Survivor Net:", "Refugee Freq:"],
        "flavor": [
            "Convoy ambushed at mile marker 12. Survivors scattered.",
            "Trading post near Riverside is fortified. Approach with caution.",
            "Looking for fuel. Will barter medical supplies.",
            "Trust no one outside the convoy. Repeat: trust no one."
        ],
        "rewards": {
            "vehicle": ["Base.VanSeats", "Base.CarStationWagon", "Base.SmallCar02"],
            "weapon": ["Base.BaseballBat", "Base.Hammer"],
            "medical": ["Base.FirstAidKit", "Base.Pills"],
            "supply": ["Base.CannedCorn", "Base.PopBottle", "Base.Bag_DuffelBag"]
        }
    },
    "SCIENCE_BREACH": {
        "name": "Project Lazarus",
        "prefixes": ["Lab Net:", "Containment Alert:", "Research Directive:"],
        "flavor": [
            "Biohazard level 4 breach confirmed. Facility lockdown failed.",
            "Test subjects have exceeded containment parameters.",
            "Do not approach the research campus. Lethal protocols active.",
            "Sample X-7 is unrecoverable. Incineration recommended."
        ],
        "rewards": {
            "vehicle": ["Base.VanAmbulance", "Base.StepVan"],
            "weapon": ["Base.HuntingRifle", "Base.308Box"],
            "medical": ["Base.Antibiotics", "Base.SutureNeedle", "Base.Disinfectant"],
            "supply": ["Base.Generator", "Base.WeldingMask", "Base.FirstAidKit"]
        }
    },
    "POWER_GRID_COLLAPSE": {
        "name": "Grid Failure Zulu",
        "prefixes": ["Power Authority:", "Grid Control:", "Emergency Services:"],
        "flavor": [
            "Main substation offline. Backup generators failing.",
            "Do not approach transformer stations. Electrical hazards remain.",
            "Rolling blackouts expected indefinitely. Prepare for dark.",
            "Looters targeting fuel depots. Exercise extreme caution."
        ],
        "rewards": {
            "vehicle": ["Base.VanSeats", "Base.PickUpVan"],
            "weapon": ["Base.Wrench", "Base.Screwdriver", "Base.Crowbar"],
            "medical": ["Base.Bandage"],
            "supply": ["Base.Generator", "Base.PropaneTank", "Base.Lighter", "Base.Matches"]
        }
    }
}

# --- RCON WRAPPER ---
def run_rcon(args):
    script_dir = os.path.dirname(__file__)
    cmd = [os.path.join(script_dir, "pz-rcon.sh")] + args
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"RCON Error: {e.stderr.decode()}", file=sys.stderr)
        return False

# --- CREATIVE REWARD LOGIC ---
def generate_creative_reward(theme, reward_type, target_player, state):
    """
    Dynamically selects a reward and crafts a narrative message.
    Now supports multiple reward categories: vehicle, weapon, medical, supply.
    Handles vehicle spawn failures (player indoors) with retry logic.
    """
    category_map = {
        "vehicle": "vehicle",
        "weapon": "weapon",
        "medical": "medical",
        "supply": "supply"
    }
    
    category = category_map.get(reward_type, "supply")
    items = theme["rewards"].get(category, [])
    
    if not items or not target_player:
        return False
    
    item = random.choice(items)
    prefix = random.choice(theme["prefixes"])
    
    # Narrative templates per category
    if category == "vehicle":
        templates = [
            f"{prefix} Convoy asset {item} abandoned. Coordinates near {target_player}.",
            f"{prefix} Vehicle {item} located. Previous crew unresponsive.",
            f"{prefix} Transport {item} disabled near {target_player}. Salvage authorized."
        ]
        msg = random.choice(templates)
        
        # Attempt vehicle spawn
        success = run_rcon(["vehicle", item, target_player])
        
        if success:
            run_rcon(["msg", msg])
            print(f"REWARD: Vehicle {item} -> {target_player}")
            return True
        else:
            # Spawn failed (likely player indoors/invalid position)
            retry_count = state.get("pendingRewardRetries", 0)
            if retry_count < 3:
                # Keep reward pending, increment retry counter
                state["pendingRewardRetries"] = retry_count + 1
                run_rcon(["msg", f"{prefix} Vehicle deploy delayed. {target_player}, move to open ground for asset delivery."])
                print(f"REWARD: Vehicle spawn failed, retry {retry_count + 1}/3")
                return False  # Keep reward pending
            else:
                # Max retries exceeded, downgrade to weapon reward
                run_rcon(["msg", f"{prefix} Vehicle delivery aborted. Switching to equipment drop."])
                state["pendingReward"] = "weapon"
                state["pendingRewardRetries"] = 0
                print(f"REWARD: Vehicle spawn failed after 3 retries, downgrading to weapon")
                return False
        
    elif category == "weapon":
        templates = [
            f"{prefix} Weapons cache secured. Distributing {item} to {target_player}.",
            f"{prefix} Armory breach. {item} available for recovery near {target_player}.",
            f"{prefix} Supply drop inbound. Contents: {item}. Mark position."
        ]
        msg = random.choice(templates)
        run_rcon(["msg", msg])
        run_rcon(["give", target_player, item, "1"])
        
        # Add ammo if firearm
        if "Pistol" in item or "9mm" in item:
            run_rcon(["give", target_player, "Base.9mmClip", "2"])
        elif "Shotgun" in item:
            run_rcon(["give", target_player, "Base.ShotgunShells", "8"])
        elif "Rifle" in item or "556" in item or "308" in item:
            run_rcon(["give", target_player, "Base.556Box", "1"])
            
        print(f"REWARD: Weapon {item} -> {target_player}")
        
    elif category == "medical":
        templates = [
            f"{prefix} Medical supplies located. {item} available at {target_player} position.",
            f"{prefix} Field hospital overrun. Securing {item} for survivor use.",
            f"{prefix} Triage cache found. Distributing {item} to {target_player}."
        ]
        msg = random.choice(templates)
        run_rcon(["msg", msg])
        run_rcon(["give", target_player, item, "3"])
        print(f"REWARD: Medical {item} -> {target_player}")
        
    elif category == "supply":
        templates = [
            f"{prefix} Scavenge site secured. {item} recovered near {target_player}.",
            f"{prefix} Supply depot accessible. Contents include {item}.",
            f"{prefix} Survivor cache found. {item} distributed to {target_player}."
        ]
        msg = random.choice(templates)
        run_rcon(["msg", msg])
        count = random.randint(2, 5)
        run_rcon(["give", target_player, item, str(count)])
        print(f"REWARD: Supply {item} x{count} -> {target_player}")
    
    state["pendingRewardRetries"] = 0  # Clear retry counter on successful delivery
    return True

# --- LOGIC ---
def main():
    # Get session context from ambient_tick.sh
    session_id = os.environ.get("PZ_SESSION_ID", "")
    nm = get_nm()

    # Load or Init State (theme system — still separate from narrative memory)
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    else:
        theme_key = random.choice(list(THEMES.keys()))
        state = {
            "tick": 0,
            "lastActionTs": int(time.time()),
            "lastEventTs": 0,
            "theme": theme_key,
            "pendingReward": None,
            "history": []
        }
        print(f"INIT: Started new plot theme: {THEMES[theme_key]['name']}")

    theme = THEMES[state.get("theme", "MILITARY_COLLAPSE")]
    now = int(time.time())
    state["tick"] += 1

    # Fetch current players
    players = []
    try:
        res = subprocess.run([os.path.join(SCRIPT_DIR, "pz-rcon.sh"), "players"], stdout=subprocess.PIPE)
        for line in res.stdout.decode().splitlines():
            if line.strip().startswith("-"):
                players.append(line.strip().replace("- ", ""))
    except Exception as e:
        print(f"Error fetching players: {e}", file=sys.stderr)

    target_player = random.choice(players) if players else None

    # Get session context for avoiding repetition
    recent_session_broadcasts = []
    session_events_this_session = []
    if session_id:
        recent_session_broadcasts = nm.get_session_broadcasts(session_id, limit=5)
        session_events_this_session = nm.get_session_events(session_id)
        # Also get per-player context for the target
        if target_player:
            player_ctx = nm.get_contextual_narrative_for_player(target_player, session_id)

    # --- Handle Player Join Events (Personalized Greetings) ---
    delta_event = os.environ.get("PZ_DELTA_EVENT", "")
    if delta_event.startswith("NEW:"):
        new_players = [p.strip() for p in delta_event.replace("NEW:", "").split(",") if p.strip()]
        if new_players:
            print(f"New player(s) detected: {new_players}")
            join_messages = handle_player_join_event(new_players)
            for msg in join_messages:
                if msg not in state.get("history", []):
                    state.setdefault("history", []).append(msg)
                    if len(state["history"]) > 5:
                        state["history"].pop(0)
                if session_id:
                    for p in new_players:
                        nm_log_broadcast(session_id, p, msg)
            state["lastActionTs"] = now
            save_state(state)
            return

    # --- Process Pending Rewards ---
    if state.get("pendingReward") and target_player:
        reward_type = state["pendingReward"]
        success = generate_creative_reward(theme, reward_type, target_player, state)

        if success:
            state["pendingReward"] = None
            state["pendingRewardRetries"] = 0

        state["lastActionTs"] = now
        save_state(state)
        return

    # --- Mini-Narration (avoids repeating recent session broadcasts) ---
    if players and random.randint(1, 100) <= 90:
        all_mini = [
            "Radio check... all stations reporting in.",
            "Background radiation levels: nominal.",
            "Unidentified movement detected 2 clicks north.",
            "Reminder: Electronics fail. Stay alert.",
            "Weather satellite: clear skies expected.",
            "Packet from Fort Red: 'Hold the line.'",
            "Rumor: there's a supply cache near the river.",
            "Auto-scan complete. No new signatures."
        ]
        # Filter out anything already broadcast in this session (within 2h)
        recent_contents = [b.split(": ", 1)[-1] if ": " in b else b for b in recent_session_broadcasts]
        pool = [m for m in all_mini if not any(m in rc for rc in recent_contents)]
        if not pool:
            pool = all_mini  # fallback if everything was used

        msg_body = random.choice(pool)
        prefix = random.choice(theme["prefixes"])
        full_msg = f"{prefix} {msg_body}"
        run_rcon(["msg", full_msg])
        print(f"MINI-NARRATION: {full_msg}")
        if session_id and target_player:
            nm_log_broadcast(session_id, target_player, full_msg)
        state["lastActionTs"] = now
        save_state(state)
        return

    # --- Roll for Major Event ---
    time_since_last = now - state.get("lastEventTs", 0)
    chance = 25 if time_since_last >= 600 else 0

    roll = random.randint(1, 100)

    if roll <= chance:
        event_roll = random.randint(1, 100)

        if event_roll <= 25:
            # BAD EVENT
            possible = [e for e in ["chopper", "horde", "alarm"]
                        if session_id and e not in session_events_this_session[-3:]]
            if not possible:
                possible = ["chopper", "horde", "alarm"]
            etype = random.choice(possible)

            if etype == "chopper":
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Air asset 4-2 is smoking... going down!"])
                run_rcon(["chopper"])
                state["pendingReward"] = random.choice(["weapon", "medical"])
                event_msg = "Helicopter down — military asset lost in sector."

            elif etype == "horde":
                count = random.randint(15, 30)
                if target_player:
                    run_rcon(["msg", f"{random.choice(theme['prefixes'])} ALERT: Massive bio-signal convergence detected!"])
                    run_rcon(["msg", f"[{target_player}] DIRECTOR WARNING: Horde of {count} detected converging on YOUR position. Prepare for contact!"])
                    run_rcon(["horde", str(count), target_player])
                    state["pendingReward"] = random.choice(["vehicle", "weapon"])
                    event_msg = f"Horde of {count} converged on {target_player}."
                else:
                    run_rcon(["msg", f"{random.choice(theme['prefixes'])} Massive bio-signals migrating across the sector."])
                    run_rcon(["gunshot"])
                    event_msg = "Horde migration detected across sector."
                    state["pendingReward"] = random.choice(["medical", "weapon"])

            elif etype == "alarm":
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Security system breach. Building alarms triggered."])
                if target_player:
                    run_rcon(["msg", f"[{target_player}] DIRECTOR: Alarm triggered near you. Expect increased activity."])
                run_rcon(["alarm"])
                state["pendingReward"] = random.choice(["medical", "weapon"])
                event_msg = "Building alarm triggered — drawing zombie attention."

            if session_id:
                nm_log_event(session_id, target_player, etype, event_msg)
            state["lastEventTs"] = now
            print(f"ACTION: Bad Event {etype}")

        elif event_roll <= 55:
            wtype = random.choice(["storm", "rain", "clear"])
            if wtype == "storm":
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Severe weather alert. Seek shelter immediately."])
                run_rcon(["storm", "1"])
            elif wtype == "rain":
                intensity = random.randint(30, 80)
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Precipitation increasing. Visibility dropping."])
                run_rcon(["rain", "start", str(intensity)])
            else:
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Weather clearing. Visibility improving."])
                run_rcon(["clear"])

            if session_id:
                nm_log_event(session_id, target_player, f"weather_{wtype}", f"Weather event: {wtype}")
            state["lastEventTs"] = now
            print(f"ACTION: Weather {wtype}")

        else:
            flavor = random.choice(theme["flavor"])
            # Avoid exact repeat from session
            if flavor not in recent_session_broadcasts[-3:]:
                full_msg = f"{random.choice(theme['prefixes'])} {flavor}"
                run_rcon(["msg", full_msg])
                fx = random.choice(["gunshot", "thunder", "lightning"])
                run_rcon([fx])
                if session_id:
                    nm_log_event(session_id, target_player, f"flavor_{fx}", full_msg)
                state["lastEventTs"] = now
                print(f"ACTION: Flavor + {fx}")
            else:
                print("ACTION: Skipped (duplicate flavor)")

    else:
        if random.randint(1, 100) <= 10:
            flavor = random.choice(theme["flavor"])
            if flavor not in state["history"] and flavor not in recent_session_broadcasts[-3:]:
                full_msg = f"{random.choice(theme['prefixes'])} {flavor}"
                run_rcon(["msg", full_msg])
                state["history"].append(flavor)
                if len(state["history"]) > 5:
                    state["history"].pop(0)
                if session_id and target_player:
                    nm_log_broadcast(session_id, target_player, full_msg)
                print("ACTION: Passive Flavor")
            else:
                print("ACTION: Skipped (duplicate passive)")
        else:
            print("ACTION: Idle")

    state["lastActionTs"] = now
    save_state(state)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

if __name__ == "__main__":
    main()
