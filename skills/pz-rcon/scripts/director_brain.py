#!/usr/bin/env python3
import json
import sys
import os
import random
import time
import subprocess

# --- CONFIGURATION ---
STATE_FILE = os.path.join(os.path.dirname(__file__), "../state/narrative-state.json")
# If no players are online, ambient_tick.sh should delete the state file to trigger a reset.
# This script assumes if it runs, players ARE online.

# --- PLOT THEMES ---
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
            "vehicle": ["Base.PickUpVan", "Base.Humvee"], # Humvee might be modded, stick to vanilla safe ones first
            "weapon": ["Base.AssaultRifle", "Base.Shotgun", "Base.556Box", "Base.ShellsBox"]
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
            "weapon": ["Base.Sledgehammer", "Base.Axe", "Base.WoodAxe"] # Tools for storm prep
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
            "vehicle": ["Base.StepVan", "Base.PickUpTruck"],
            "weapon": ["Base.Pistol", "Base.Bullets9mmBox", "Base.Shotgun"]
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

    # 3. Process Pending Rewards (High Priority)
    if state.get("pendingReward") and target_player:
        reward_type = state["pendingReward"]
        
        if reward_type == "vehicle":
            veh = random.choice(theme["rewards"]["vehicle"])
            # Lore:
            msg = f"{random.choice(theme['prefixes'])} Convoy hit nearby. Asset {veh} abandoned near {target_player}."
            run_rcon(["msg", msg])
            run_rcon(["vehicle", veh, target_player])
            print(f"ACTION: Reward Vehicle {veh} to {target_player}")
            
        elif reward_type == "weapon":
            wep = random.choice(theme["rewards"]["weapon"])
            # Lore:
            msg = f"{random.choice(theme['prefixes'])} Supply crate lost in transit. Securing payload near {target_player}."
            run_rcon(["msg", msg])
            run_rcon(["give", target_player, wep, "1"])
            # Add ammo box for good measure
            if "Shotgun" in wep: run_rcon(["give", target_player, "Base.ShellsBox", "2"])
            if "Rifle" in wep: run_rcon(["give", target_player, "Base.556Box", "2"])
            print(f"ACTION: Reward Weapon {wep} to {target_player}")

        state["pendingReward"] = None
        state["lastActionTs"] = now
        save_state(state)
        return

    # 4. Roll for New Event
    # Cooldown: 20 mins (1200s)
    time_since_last = now - state.get("lastEventTs", 0)
    chance = 20 # 20%
    
    if time_since_last < 1200:
        chance = 0 # Cooldown active
    
    roll = random.randint(1, 100)
    
    if roll <= chance:
        # TRIGGER EVENT
        event_roll = random.randint(1, 100)
        
        if event_roll <= 30: 
            # BAD EVENT (Horde/Chopper) - Sets up Reward
            etype = "chopper" if random.random() > 0.5 else "horde"
            
            if etype == "chopper":
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Air asset 4-2 is smoking... going down!"])
                run_rcon(["chopper"])
                state["pendingReward"] = "weapon" # Choppers drop guns
                
            else: # Horde
                count = random.randint(10, 20)
                if target_player:
                    run_rcon(["msg", f"{random.choice(theme['prefixes'])} Massive bio-signal convergence detected near {target_player}."])
                    run_rcon(["horde", str(count), target_player])
                    state["pendingReward"] = "vehicle" # "Convoy overrun" implies vehicle left behind
                else:
                    run_rcon(["msg", f"{random.choice(theme['prefixes'])} Massive bio-signals migrating across the sector."])
                    # No target, no horde spawn, just flavor + noise
                    run_rcon(["gunshot"])
            
            state["lastEventTs"] = now
            print(f"ACTION: Bad Event {etype}")

        elif event_roll <= 60:
            # WEATHER EVENT
            wtype = "storm" if random.random() > 0.7 else "rain"
            if wtype == "storm":
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Severe weather alert. Seek shelter immediately."])
                run_rcon(["storm", "1"]) # 1 hour storm
            else:
                run_rcon(["msg", f"{random.choice(theme['prefixes'])} Precipitation increasing. Visibility dropping."])
                run_rcon(["rain", "start"])
            
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
