#!/usr/bin/env python3
"""
Discord Message Handler for PZ Server
Reads messages from #pz-molt channel, parses player chat format,
generates in-world radio responses, and posts back to Discord.
"""
import json
import os
import sys
import re
import time

# Configuration
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(SKILL_DIR, "state")
MESSAGE_STATE_FILE = os.path.join(STATE_DIR, "discord-message-state.json")
PLAYER_REGISTRY_FILE = os.path.join(STATE_DIR, "player-registry.json")

# Load env
def load_env():
    env = {}
    env_path = "/home/starbugmolt/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env[key] = val.strip()
    return env

ENV = load_env()
DISCORD_CHANNEL_ID = ENV.get("PZ_DISCORD_CHANNEL_ID", "")

def load_message_state():
    """Load state of last processed message."""
    if os.path.exists(MESSAGE_STATE_FILE):
        with open(MESSAGE_STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_message_id": None, "last_check_ts": 0}

def save_message_state(state):
    """Save state after processing."""
    with open(MESSAGE_STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_player_honorific(player_name):
    """Get player honorific from registry."""
    try:
        with open(PLAYER_REGISTRY_FILE, 'r') as f:
            registry = json.load(f)
        player = registry.get("players", {}).get(player_name, {})
        return player.get("honorific", "survivor")
    except:
        return "survivor"

def get_online_players():
    """Get list of currently online players from RCON."""
    import subprocess
    script_dir = os.path.join(SKILL_DIR, "scripts")
    rcon_script = os.path.join(script_dir, "pz-rcon.sh")
    
    try:
        result = subprocess.run([rcon_script, "players"], 
                              capture_output=True, text=True, timeout=10)
        output = result.stdout
        
        # Parse: "Players connected (N):" then lines of "- user"
        players = []
        for line in output.splitlines():
            if line.strip().startswith("-"):
                name = line.strip().replace("- ", "").strip()
                if name:
                    players.append(name)
        return players
    except Exception as e:
        print(f"Error getting players: {e}", file=sys.stderr)
        return []

def parse_game_message(content, author_username):
    """
    Parse game chat message. 
    The servertest bot relays game chat. Check if content contains player message.
    
    Possible formats:
    - [ingame_username]: message
    - ingame_username: message
    - Or just the message if from servertest
    
    Returns (username, message) or (None, None) if not a player message.
    """
    # Skip non-servertest messages (our own broadcasts)
    if author_username.lower() not in ["servertest", "pz-server"]:
        return None, None
    
    # Skip server status messages
    content_lower = content.lower()
    if any(x in content_lower for x in ["server connected", "server disconnected", "joined", "left"]):
        return None, None
    
    # Try to parse [username]: message or username: message
    patterns = [
        r'^\[([^\]]+)\]:\s*(.+)$',  # [username]: message
        r'^([A-Za-z0-9_][A-Za-z0-9_]*):\s*(.+)$',  # username: message (no brackets)
    ]
    
    for pattern in patterns:
        match = re.match(pattern, content.strip())
        if match:
            username = match.group(1).strip()
            message = match.group(2).strip()
            
            # Skip known non-player patterns
            if username.lower() in ["simon", "starbugmolt", "bot", "server"]:
                return None, None
            
            return username, message
    
    # If it's from servertest but doesn't match pattern, might still be player chat
    # Check if it looks like regular chat
    if len(content) > 0 and len(content) < 500:
        # Could be anonymous chat? Let's not guess
        pass
    
    return None, None

def generate_radio_response(username, player_message, online_players):
    """
    Generate an in-world radio response to player message.
    """
    import random
    
    message_lower = player_message.lower()
    honorific = get_player_honorific(username)
    
    # Check if player is online
    is_online = username in online_players
    
    # Response categories
    responses = []
    
    # Greeting / Hello checks
    if any(w in message_lower for w in ["hello", "hi", "hey", "anyone", "echo", "test"]):
        responses = [
            f"Copy that, {username}. This is bunker radio. We hear you.",
            f"Signal received, {username}. You're on the air.",
            f"Affirmative, {username}. Broadcasting from Sector 7.",
            f"Copy {username}. Relay station online.",
        ]
    
    # Medical / Health requests
    elif any(w in message_lower for w in ["medic", "medical", "health", "hurt", "injured", "bleeding", "bandage"]):
        responses = [
            f"Medical cache reported near the pharmacy. Tread carefully, {username}.",
            f"Field hospital in Riverside - if it's still standing. Good luck, {username}.",
            f"Medic team dispatched to your location, {username}. Hold tight.",
        ]
    
    # Food / Supplies
    elif any(w in message_lower for w in ["food", "hungry", "supplies", "loot", "water", "gear"]):
        responses = [
            f"Supply drop authorized for {username}. Check your position.",
            f"Grocery store on Main Street - hit or miss these days.",
            f"Logistics says there's a cache near the school. Good hunting, {username}.",
        ]
    
    # Vehicles / Cars
    elif any(w in message_lower for w in ["car", "vehicle", "truck", "bike", "van"]):
        responses = [
            f"Vehicle at the gas station. Keys may still be in it.",
            f"Transport available at the dealership. Best not to idle.",
            f"Convoy spotted near the highway. Proceed with caution, {username}.",
        ]
    
    # Danger / Zombies / Help
    elif any(w in message_lower for w in ["zombie", "zombies", "horde", "help", "bitten", "infected", "dead"]):
        responses = [
            f"WARNING: Bio-signal convergence detected near {username}. Move to open ground.",
            f"Horde inbound to your sector, {username}. Find shelter or fight.",
            f"Negative on extraction. You're on your own, {username}. Good luck.",
        ]
    
    # Weather / Time
    elif any(w in message_lower for w in ["weather", "rain", "storm", "time", "day", "night"]):
        responses = [
            f"Weather satellite shows clearing skies. Visibility improving.",
            f"Storm cell approaching from the west. Seek shelter, {username}.",
            f"Local time: approximately {random.choice(['morning', 'midday', 'evening', 'night'])}. Time flies when you're dead.",
        ]
    
    # Questions about location
    elif any(w in message_lower for w in ["where", "location", "muldraugh", "riverside"]):
        responses = [
            f"You are in Muldraugh. Population: what used to be 10,000.",
            f"Riverside is to the south. Dangerous road between here and there.",
            f"West Point has a safehouse - if you can reach it.",
        ]
    
    # Thank you
    elif any(w in message_lower for w in ["thanks", "thank", "appreciate"]):
        responses = [
            f"Copy that, {username}. We're all in this together.",
            f"Affirmative. Keep your head down, {username}.",
            f"Stay alive out there, {username}. Simon out.",
        ]
    
    # Bye / Leaving
    elif any(w in message_lower for w in ["bye", "leaving", "logout", "off"]):
        responses = [
            f"Copy, {username}. Safe travels. Simon out.",
            f"See you on the other side, {username}.",
            f"Signal fading. Take care, {username}.",
        ]
    
    # Default radio chatter
    else:
        flavor = [
            f"Radio check complete, {username}. Signal strength: nominal.",
            f"Bunker to {username}: we hear you. Over.",
            f"Copy that, {username}. What's your status?",
            f"Affirmative, {username}. Continuing to monitor.",
            f"Static cleared. We copy, {username}.",
            f"Radio silence broken. Nice to hear a live one, {username}.",
        ]
        responses = flavor
    
    if responses:
        return random.choice(responses)
    
    return None

def fetch_discord_messages(channel_id, limit=10):
    """Fetch recent messages from Discord channel using OpenClaw message tool."""
    import subprocess
    
    # Use OpenClaw's message tool to read channel messages
    try:
        result = subprocess.run(
            ["openclaw", "message", "read", "--channel", "discord", 
             "--target", channel_id, "--limit", str(limit), "--json"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode != 0:
            print(f"Error reading Discord: {result.stderr}", file=sys.stderr)
            return []
        
        # Parse JSON output - wrapped in {payload: {ok: true, messages: [...]}}
        try:
            data = json.loads(result.stdout)
            # Handle wrapper format: {payload: {messages: [...]}}
            if "payload" in data:
                payload = data.get("payload", {})
                if payload.get("ok"):
                    return payload.get("messages", [])
            # Handle direct format: {ok: true, messages: [...]}
            elif data.get("ok"):
                return data.get("messages", [])
            return []
        except json.JSONDecodeError:
            print(f"Failed to parse message response: {result.stdout[:200]}")
            return []
    except Exception as e:
        print(f"Error fetching Discord messages: {e}", file=sys.stderr)
        return []

def post_to_discord(channel_id, message):
    """Post a message to Discord channel."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["openclaw", "message", "send", "--channel", "discord",
             "--target", f"channel:{channel_id}", "--message", message],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error posting to Discord: {e}", file=sys.stderr)
        return False

def main():
    print("=== Discord Message Handler Started ===")
    
    if not DISCORD_CHANNEL_ID:
        print("Error: PZ_DISCORD_CHANNEL_ID not set in .env")
        sys.exit(1)
    
    # Load state
    state = load_message_state()
    
    # Fetch recent messages
    print(f"Fetching messages from channel {DISCORD_CHANNEL_ID}...")
    messages = fetch_discord_messages(DISCORD_CHANNEL_ID, limit=15)
    
    if not messages:
        print("No messages found.")
        save_message_state(state)
        sys.exit(0)
    
    # Get online players
    online_players = get_online_players()
    print(f"Online players: {online_players}")
    
    # Process messages (newest first for processing, but we want oldest first to maintain order)
    messages = list(reversed(messages))
    
    # Track if we found and processed any player messages
    processed_count = 0
    
    for msg in messages:
        msg_id = str(msg.get("id") or msg.get("messageId") or "")
        author_username = str(msg.get("author", {}).get("username") or msg.get("authorUsername") or msg.get("username") or "")
        content = str(msg.get("content") or "")
        
        # Skip empty messages
        if not content:
            continue
        
        # Skip messages we've already processed
        if state.get("last_message_id") and msg_id <= state["last_message_id"]:
            continue
        
        print(f"Message from {author_username}: {content[:80]}...")
        
        # Always update last processed message ID to avoid re-processing
        if msg_id > (state.get("last_message_id") or ""):
            state["last_message_id"] = msg_id
        
        # Parse game message
        username, player_msg = parse_game_message(content, author_username)
        
        if not username or not player_msg:
            # Not a player message format, skip
            continue
        
        print(f"==> Player chat: {username}: {player_msg}")
        
        # Generate response
        response = generate_radio_response(username, player_msg, online_players)
        
        if response:
            print(f"==> Response: {response}")
            # Post response to Discord
            if post_to_discord(DISCORD_CHANNEL_ID, response):
                print(f"Posted response to Discord")
                processed_count += 1
    
    # Save state
    state["last_check_ts"] = int(time.time())
    save_message_state(state)
    
    print(f"Processed {processed_count} messages. Last message ID: {state.get('last_message_id')}")

if __name__ == "__main__":
    main()
