#!/usr/bin/env python3
"""
SIMON Fast Listener — Discord-based player connection detector.
Runs as a background service, detects "[PlayerName] connected to server"
messages in #pz-molt and fires RCON greetings within seconds.

Usage:
    python3 simon_fast_listener.py

Requires:
    - discord.py (pip install discord.py)
    - Bot token from OpenClaw config (read from openclaw.json)
    - PZ RCON credentials (from ~/.env)
"""

import asyncio
import json
import os
import sys
import subprocess
import time
from pathlib import Path

# Configuration
SKILL_DIR = Path(__file__).parent.parent
STATE_DIR = SKILL_DIR / "state"
GREET_DEDUPE_FILE = STATE_DIR / "last_greet.txt"
PLAYER_DELTA_FILE = STATE_DIR / "player-delta.json"
DISCORD_MESSAGE_STATE_FILE = STATE_DIR / "discord-message-state.json"
RCON_SCRIPT = Path(__file__).parent / "pz-rcon.sh"

# Greeting templates by tier
GREETINGS = {
    "new": [
        "New arrival detected. Welcome to the apocalypse, {player}. Simon, out.",
        "Unregistered signal... {player}? Welcome to Muldraugh. Good luck. Simon, out.",
        "First time in sector, {player}? The zombies are hungry. Simon, out.",
    ],
    "returning": [
        "{player}! Back for more? The horde missed you. Probably. Simon, out.",
        "Welcome back, {player}. Status: Still alive. That's something. Simon, out.",
        "{player} returns. Let's hope you last longer this time. Simon, out.",
    ],
    "veteran": [
        "Veteran survivor {player} checking in. The undead await. Simon, out.",
        "{player}, your survival instincts are noted. Good hunting. Simon, out.",
        "Welcome back, {player}. Another day in paradise. Simon, out.",
    ],
}

# Dedupe window in seconds (5 minutes)
DEDUPE_SECONDS = 300

# Load bot token from OpenClaw config
def load_bot_token():
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if not config_path.exists():
        print(f"ERROR: Config not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    token = config.get("channels", {}).get("discord", {}).get("token")
    if not token:
        print("ERROR: Discord token not found in config", file=sys.stderr)
        sys.exit(1)
    
    return token

# Load player registry for tier detection
def load_player_registry():
    registry_file = STATE_DIR / "player-registry.json"
    if not registry_file.exists():
        return {"players": {}}
    try:
        with open(registry_file) as f:
            return json.load(f)
    except:
        return {"players": {}}

# Get player tier based on visit count
def get_player_tier(player_name):
    registry = load_player_registry()
    player_info = registry.get("players", {}).get(player_name, {})
    visit_count = player_info.get("visitCount", 0)
    
    if visit_count <= 1:
        return "new"
    elif visit_count <= 5:
        return "returning"
    else:
        return "veteran"

# Generate greeting based on player tier
def generate_greeting(player_name):
    import random
    tier = get_player_tier(player_name)
    template = random.choice(GREETINGS[tier])
    return template.format(player=player_name)

# Check dedupe
def should_greet(player_name):
    if not GREET_DEDUPE_FILE.exists():
        return True
    
    try:
        content = GREET_DEDUPE_FILE.read_text().strip()
        if not content:
            return True
        
        last_player, last_ts = content.split("|")
        last_ts = int(last_ts)
        now = int(time.time())
        
        # Different player or enough time passed
        if last_player != player_name or (now - last_ts) >= DEDUPE_SECONDS:
            return True
        
        return False
    except:
        return True

# Update greet dedupe file
def update_greet_dedupe(player_name):
    now = int(time.time())
    GREET_DEDUPE_FILE.write_text(f"{player_name}|{now}")

# Fire RCON greeting
def fire_greeting(player_name):
    greeting = generate_greeting(player_name)
    print(f"Greeting {player_name}: {greeting}")
    
    try:
        result = subprocess.run(
            [str(RCON_SCRIPT), "msg", greeting],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(SKILL_DIR)
        )
        
        if result.returncode == 0:
            update_greet_dedupe(player_name)
            print(f"Greeting sent successfully")
            return True
        else:
            print(f"ERROR: RCON failed: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False

# Parse connection message
def parse_connection_message(content):
    """
    Parse "[PlayerName] connected to server" message.
    Returns player name or None if not a connection message.
    """
    import re
    
    # Pattern: [PlayerName] connected to server
    match = re.match(r'^\[([^\]]+)\]\s+connected to server$', content.strip())
    if match:
        return match.group(1)
    
    return None

# Main listener
async def main():
    import discord
    
    # Load bot token
    token = load_bot_token()
    
    # Create client
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    # Channel ID from environment
    CHANNEL_ID = int(os.environ.get("PZ_DISCORD_CHANNEL_ID", "***REMOVED***"))
    
    @client.event
    async def on_ready():
        print(f"SIMON Fast Listener connected as {client.user}")
        print(f"Monitoring channel {CHANNEL_ID}")
        
        # Update state file
        DISCORD_MESSAGE_STATE_FILE.write_text(json.dumps({
            "last_message_id": None,
            "last_check_ts": int(time.time()),
            "listener_started": int(time.time())
        }, indent=2))
    
    @client.event
    async def on_message(message):
        # Only process messages from the target channel
        if message.channel.id != CHANNEL_ID:
            return
        
        # Skip our own messages
        if message.author == client.user:
            return
        
        # Check if this is a connection message
        player_name = parse_connection_message(message.content)
        if player_name:
            print(f"Connection detected: {player_name}")
            
            # Check dedupe
            if should_greet(player_name):
                # 10-second delay before greeting (PZ connection lag; Discord
                # log fires before the in-game connection completes, so we wait
                # before talking to the player).
                print(f"Waiting 10s before greeting {player_name}...")
                await asyncio.sleep(10)
                # Fire greeting in a thread to not block the event loop
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, fire_greeting, player_name)
            else:
                print(f"Skipping {player_name} (dedupe)")
            
            # Update message state
            DISCORD_MESSAGE_STATE_FILE.write_text(json.dumps({
                "last_message_id": str(message.id),
                "last_check_ts": int(time.time()),
                "last_connection": player_name
            }, indent=2))
        
        # Also update player delta state for connection messages
        if player_name:
            try:
                with open(PLAYER_DELTA_FILE) as f:
                    delta = json.load(f)
                
                # Mark player as new
                if player_name not in delta.get("newPlayers", []):
                    delta.setdefault("newPlayers", []).append(player_name)
                
                # Add to previous online if not there
                if player_name not in delta.get("previousOnline", []):
                    delta.setdefault("previousOnline", []).append(player_name)
                
                delta["lastCheckTs"] = int(time.time())
                
                with open(PLAYER_DELTA_FILE, "w") as f:
                    json.dump(delta, f, indent=2)
            except Exception as e:
                print(f"ERROR updating delta: {e}", file=sys.stderr)
    
    # Run the client
    try:
        await client.start(token)
    except Exception as e:
        print(f"ERROR: Failed to start listener: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
