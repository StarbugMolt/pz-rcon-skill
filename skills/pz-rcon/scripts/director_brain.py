#!/usr/bin/env python3
import json
import sys
import os
import random
import time
import subprocess

# --- CONFIGURATION ---
STATE_FILE = os.path.join(os.path.dirname(__file__), "../state/narrative-state.json")
PLAYER_REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "../state/player-registry.json")

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
    # 1. Load or Init State
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    else:
        # New Session / Reset
        theme_key = random.choice(list(THEMES.keys()))
        state = {
            "tick": 0,
            "lastActionTs": int(time.time()),
            "lastEventTs": 0,
            "theme": theme_key,
            "pendingReward": None, # "vehicle", "weapon"
            "history": [] # Keep last 5 messages
        }
        print(f"INIT: Started new plot theme: {THEMES[theme_key]['name']}")

    theme = THEMES[state.get("theme", "MILITARY_COLLAPSE")]
    now = int(time.time())
    state["tick"] += 1
    
    # 2. Get Players (passed via stdin or args? lets use args for simplicity or just fetch them)
    # Actually, ambient_tick.sh passes nothing yet. Let's fetch players inside here for targeting.
    # Note: parsing 'players' output from pz-rcon.sh is annoying. 
    # For now, let's assume if we need a target, we pick a random one if possible, 
    # or use 'all' for messages. 
    # To drop loot, we NEED a username.
    
    players = []
    try:
        script_dir = os.path.dirname(__file__)
        res = subprocess.run([os.path.join(script_dir, "pz-rcon.sh"), "players"], stdout=subprocess.PIPE)
        # Parse: "Players connected (1):" then lines of "- user"
        lines = res.stdout.decode().splitlines()
        for line in lines:
            if line.strip().startswith("-"):
                players.append(line.strip().replace("- ", ""))
    except Exception as e:
        print(f"Error fetching players: {e}", file=sys.stderr)

    target_player = random.choice(players) if players else None

    # 2.5. Handle Player Join Events (Personalized Greetings)
    delta_event = os.environ.get("PZ_DELTA_EVENT", "")
    if delta_event.startswith("NEW:"):
        new_players = delta_event.replace("NEW:", "").split(",")
        # Filter empty strings
        new_players = [p.strip() for p in new_players if p.strip()]
        if new_players:
            print(f"New player(s) detected: {new_players}")
            join_messages = handle_player_join_event(new_players)
            # Add to history to avoid repeats
            for msg in join_messages:
                if msg not in state.get("history", []):
                    state.setdefault("history", []).append(msg)
                    if len(state["history"]) > 5:
                        state["history"].pop(0)
            # Update last action timestamp
            state["lastActionTs"] = now
            save_state(state)
            return  # Exit early after greeting

    # 3. Process Pending Rewards (High Priority)
    if state.get("pendingReward") and target_player:
        reward_type = state["pendingReward"]
        success = generate_creative_reward(theme, reward_type, target_player, state)
        
        if success:
            # Reward delivered successfully, clear it
            state["pendingReward"] = None
            state["pendingRewardRetries"] = 0
        # else: reward stays pending for next tick (vehicle retry logic)
        
        state["lastActionTs"] = now
        save_state(state)
        return

    # 4. Mini-Narration (every tick when players online)
    # Small flavor messages every tick - no cooldown
    if players and random.randint(1, 100) <= 90:  # 90% chance per tick
        mini_narration = [
            f"{random.choice(theme['prefixes'])} Radio check... all stations reporting in.",
            f"{random.choice(theme['prefixes'])} Background radiation levels: nominal.",
            f"{random.choice(theme['prefixes'])} Unidentified movement detected 2 clicks north.",
            f"{random.choice(theme['prefixes'])} Reminder: Electronics fail. Stay alert.",
            f"{random.choice(theme['prefixes'])} Weather satellite: clear skies expected.",
            f"{random.choice(theme['prefixes'])} Packet from Fort Red: 'Hold the line.'",
            f"{random.choice(theme['prefixes'])} Rumor: there's a supply cache near the river.",
            f"{random.choice(theme['prefixes'])} Auto-scan complete. No new signatures."
        ]
        msg = random.choice(mini_narration)
        run_rcon(["msg", msg])
        print(f"MINI-NARRATION: {msg}")
        state["lastActionTs"] = now
        save_state(state)
        return

    # 5. Roll for Major Event
    # Cooldown: 10 mins (600s)
    time_since_last = now - state.get("lastEventTs", 0)
    chance = 25 # 25%
    
    if time_since_last < 600:
        chance = 0 # Cooldown active
    
    roll = random.randint(1, 100)
    
    if roll <= chance:
        # TRIGGER EVENT
        event_roll = random.randint(1, 100)
        
        if event_roll <= 25: 
            # BAD EVENT (Horde/Chopper) - Sets up Reward
            etype = random.choice(["chopper", "horde", "alarm"])
            
            if etype == "chopper":
                # Warn all players about helicopter
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Air asset 4-2 is smoking... going down!"])
                run_rcon(["chopper"])
                state["pendingReward"] = random.choice(["weapon", "medical"])
                
            elif etype == "horde":
                count = random.randint(15, 30)
                if target_player:
                    # Warn the targeted player directly + broadcast
                    run_rcon(["msg", f"{random.choice(theme['prefixes'])} ALERT: Massive bio-signal convergence detected!"])
                    run_rcon(["msg", f"[{target_player}] DIRECTOR WARNING: Horde of {count} detected converging on YOUR position. Prepare for contact!"])
                    run_rcon(["horde", str(count), target_player])
                    # Horde is highest threat -> best rewards (vehicle or weapon only)
                    state["pendingReward"] = random.choice(["vehicle", "weapon"])
                else:
                    run_rcon(["msg", f"{random.choice(theme['prefixes'])} Massive bio-signals migrating across the sector."])
                    run_rcon(["gunshot"])
                    
            elif etype == "alarm":
                # Alarms attract zombies - warn players
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Security system breach. Building alarms triggered."])
                if target_player:
                    run_rcon(["msg", f"[{target_player}] DIRECTOR: Alarm triggered near you. Expect increased activity."])
                run_rcon(["alarm"])
                # Alarm is moderate threat -> medical or weapon
                state["pendingReward"] = random.choice(["medical", "weapon"])
            
            state["lastEventTs"] = now
            print(f"ACTION: Bad Event {etype}")

        elif event_roll <= 55:
            # WEATHER EVENT
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
            
            state["lastEventTs"] = now
            print(f"ACTION: Weather {wtype}")

        else:
            # FLAVOR EVENT + FX
            flavor = random.choice(theme["flavor"])
            prefix = random.choice(theme["prefixes"])
            full_msg = f"{prefix} {flavor}"
            run_rcon(["msg", full_msg])
            
            # Sound FX
            fx = random.choice(["gunshot", "thunder", "lightning"])
            run_rcon([fx])
            
            state["lastEventTs"] = now
            print(f"ACTION: Flavor + {fx}")

    else:
        # QUIET / IDLE
        # 10% chance of just passive flavor text without resetting cooldown
        if random.randint(1, 100) <= 10:
            flavor = random.choice(theme["flavor"])
            prefix = random.choice(theme["prefixes"])
            # Don't repeat recent history
            if flavor not in state["history"]:
                run_rcon(["msg", f"{prefix} {flavor}"])
                state["history"].append(flavor)
                if(len(state["history"]) > 5): state["history"].pop(0)
                print("ACTION: Passive Flavor")
        else:
            print("ACTION: Idle")

    state["lastActionTs"] = now
    save_state(state)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

if __name__ == "__main__":
    main()
