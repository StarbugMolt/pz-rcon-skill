#!/usr/bin/env python3
"""
SIMON Fast Listener — Discord-based player connection detector + chat responder.
Runs as a background service, detects "[PlayerName] connected to server"
messages in #pz-molt and fires Discord greetings within seconds. Also listens
to general in-game chat (mirrored to #pz-molt via PZ's Discord chat relay) and
responds in-character when addressed.

Architecture: PZ server has DiscordEnable=true and DiscordChatChannel=pz-molt,
so messages sent to #pz-molt are automatically mirrored to in-game chat via
PZ's Discord chat relay. RCON `servermsg` is no longer needed for broadcasts
and is reserved for game-state mutations only (give, addvehicle, etc.).

Two main paths:
1. Connection greeting: "[Player] connected to server" → tiered greeting
2. Chat response: any player message that addresses SIMON → in-character reply
   (gated by trigger detection + per-author cooldown to avoid spam)

Usage:
    python3 simon_fast_listener.py

Requires:
    - discord.py (pip install discord.py)
    - Bot token from OpenClaw config (read from openclaw.json)
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

# Chat response: per-author cooldown in seconds (avoid spam)
CHAT_COOLDOWN_SECONDS = 30

# Chat response: minimum message length to consider
CHAT_MIN_LENGTH = 3

# Chat response: trigger patterns (lowercased substrings). If any of these
# appear in a message, SIMON will respond. Keep the list tight — too liberal
# makes the bot spammy.
CHAT_TRIGGER_PATTERNS = (
    # Direct address
    "simon",
    "@simon",
    "hey simon",
    "yo simon",
    "ok simon",
    # Radio lingo commonly used in PZ
    "over",
    "copy that",
    "10-4",
    "request",
    "status report",
    "anyone ",
    "anybody ",
    "help ",
    "sos",
    # Questions
    "?",
)

# Chat response: templates by trigger category. Pick at random. Each is in
# SIMON's voice — bunker radio DJ, dramatic, darkly humorous. {player} is the
# author's display name (or "survivor" if anonymous).
CHAT_RESPONSES = {
    "mention": [
        "Copy, {player}. Bunker radio reads you loud. Simon, out.",
        "{player}, you're on the air. State your business. Simon, out.",
        "Reading you, {player}. Signal's weak but it holds. Simon, out.",
        "{player} — your friendly neighbourhood bunker DJ. Go ahead. Simon, out.",
    ],
    "status": [
        "Status update, {player}: weather ugly, zombies plentiful, generator\nflickering. Station's still breathing. Simon, out.",
        "{player}, this is Starbug. Grid's down, radar's unreliable, but the\ntransmitter holds. Simon, out.",
        "All quiet on the western fence, {player}. Too quiet. Simon, out.",
    ],
    "help": [
        "{player}, only help the dead don't ask for. Bandage up, hunker down.\nSimon, out.",
        "Help, {player}? You're it. The bunker's got canned beans and bad news.\nSimon, out.",
        "Help's a luxury, {player}. Survival's the only currency. Simon, out.",
    ],
    "question": [
        "Question logged, {player}. The dead don't have answers, but the station\nmight. Simon, out.",
        "Filed under *things we'll never know*, {player}. Simon, out.",
        "Good question, {player}. Wrong operator. Try the undead — they're full\nof answers. Simon, out.",
    ],
    "general": [
        "Copy, {player}. Static's softer tonight. Simon, out.",
        "Reading you, {player}. The bunker's still here. So are the zombies.\nSimon, out.",
        "{player}, the signal's weak but the will is strong. Stay frosty. Simon, out.",
        "Noted, {player}. Logging that under *ash and echoes*. Simon, out.",
    ],
}

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

# Fire Discord greeting (Discord-first chat architecture)
# PZ server has DiscordEnable=true and DiscordChatChannel=pz-molt,
# so #pz-molt messages are mirrored to in-game chat automatically.
# RCON servermsg is no longer needed for broadcasts and is reserved
# for game-state mutations only (give, addvehicle, etc.).
async def fire_greeting(channel, player_name, max_retries=2):
    """
    Fire Discord greeting with retry on transient failures.
    
    Retries on: discord.HTTPException, discord.ConnectionError, OSError
    (covers 5xx Discord API blips, gateway reconnects, brief socket drops).
    
    Does NOT retry on: discord.Forbidden (permanent — missing perms),
    discord.NotFound (bad channel id).
    
    Returns True on success, False if all attempts failed.
    """
    import discord
    
    greeting = generate_greeting(player_name)
    print(f"Greeting {player_name}: {greeting}")
    
    # Errors worth retrying — transient transport/HTTP issues only
    retryable = (
        getattr(discord, "HTTPException", Exception),
        getattr(discord, "ConnectionError", Exception),
        getattr(discord, "GatewayNotFound", Exception),
        OSError,
        asyncio.TimeoutError,
    )
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            await channel.send(greeting)
            update_greet_dedupe(player_name)
            print(f"Greeting sent successfully (Discord → PZ chat relay → in-game)")
            return True
        except retryable as e:
            last_error = e
            if attempt < max_retries:
                backoff = 3 * attempt  # 3s, 6s
                print(
                    f"WARNING: Discord send attempt {attempt}/{max_retries} failed "
                    f"({type(e).__name__}: {e}); retrying in {backoff}s",
                    file=sys.stderr,
                )
                await asyncio.sleep(backoff)
        except Exception as e:
            # Non-retryable (Forbidden, NotFound, ValueError, etc.) — log and give up
            print(
                f"ERROR: Discord send failed (non-retryable, {type(e).__name__}): {e}",
                file=sys.stderr,
            )
            return False
    
    # All retries exhausted
    print(
        f"ERROR: Discord send failed after {max_retries} attempts "
        f"(last error: {type(last_error).__name__}: {last_error})",
        file=sys.stderr,
    )
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

# Per-author chat-response cooldown (in-memory; cleared on daemon restart).
# Key: str(author_id), Value: int(last_response_ts).
_chat_cooldown = {}

def should_respond_to_chat(content, author_id):
    """
    Decide whether SIMON should respond to a chat message.
    
    Returns:
        (should_respond, trigger_category) — (False, None) if no,
        (True, category) if yes. category is one of "mention", "status",
        "help", "question", "general".
    """
    import re
    
    if not content or not isinstance(content, str):
        return False, None
    
    stripped = content.strip()
    if len(stripped) < CHAT_MIN_LENGTH:
        return False, None
    
    # Skip pure emotes / punctuation
    if re.match(r'^[\W_]+$', stripped):
        return False, None
    
    # Per-author cooldown
    now = int(time.time())
    last_ts = _chat_cooldown.get(str(author_id), 0)
    if (now - last_ts) < CHAT_COOLDOWN_SECONDS:
        return False, None
    
    # Detect trigger category (priority order — most specific first)
    lower = stripped.lower()
    
    # SOS / help requests
    if re.search(r'\b(sos|help|heal|rescue)\b', lower) or any(p in lower for p in ("help me", "i'm hurt", "im hurt", "bleeding", "dying")):
        return True, "help"
    
    # Direct mention
    if any(p in lower for p in ("simon", "@simon")):
        return True, "mention"
    
    # Status / radio lingo
    if any(p in lower for p in ("status report", "10-4", "copy that", "over", "anyone ", "anybody ")):
        return True, "status"
    
    # Questions (contains ? and is more than 5 chars)
    if "?" in stripped and len(stripped) > 5:
        return True, "question"
    
    return False, None


def generate_chat_response(content, player_name, trigger):
    """
    Pick a SIMON-style response template for the given trigger category.
    Returns a string. player_name is the author's display name (or "survivor")
    and is interpolated into the template via {player}.
    """
    import random
    
    bucket = CHAT_RESPONSES.get(trigger, CHAT_RESPONSES["general"])
    template = random.choice(bucket)
    return template.format(player=player_name or "survivor")


async def fire_chat_response(channel, content, player_name, trigger, author_id, max_retries=2):
    """
    Send a chat response via Discord (mirrored to in-game via PZ chat relay).
    
    Same retry discipline as fire_greeting. On success, returns True and the
    caller is expected to update the per-author cooldown via _chat_cooldown.
    
    Args:
        channel: discord.TextChannel
        content: original message content (for logging)
        player_name: author's display name (or "survivor")
        trigger: trigger category from should_respond_to_chat
        author_id: author.id (string) — used for cooldown bookkeeping on success
        max_retries: total attempts (default 2)
    """
    import discord
    
    response = generate_chat_response(content, player_name, trigger)
    print(f"Chat response to {player_name} ({trigger}): {response[:80]}...")
    
    retryable = (
        getattr(discord, "HTTPException", Exception),
        getattr(discord, "ConnectionError", Exception),
        getattr(discord, "GatewayNotFound", Exception),
        OSError,
        asyncio.TimeoutError,
    )
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            await channel.send(response)
            # Update per-author cooldown on success
            _chat_cooldown[str(author_id)] = int(time.time())
            print(f"Chat response sent successfully (Discord → PZ chat relay → in-game)")
            return True
        except retryable as e:
            last_error = e
            if attempt < max_retries:
                backoff = 3 * attempt
                print(
                    f"WARNING: chat send attempt {attempt}/{max_retries} failed "
                    f"({type(e).__name__}: {e}); retrying in {backoff}s",
                    file=sys.stderr,
                )
                await asyncio.sleep(backoff)
        except Exception as e:
            print(
                f"ERROR: chat send failed (non-retryable, {type(e).__name__}): {e}",
                file=sys.stderr,
            )
            return False
    
    print(
        f"ERROR: chat send failed after {max_retries} attempts "
        f"(last error: {type(last_error).__name__}: {last_error})",
        file=sys.stderr,
    )
    return False

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
        # Reconnect heartbeat — if daemon was bouncing or gateway dropped, this
        # fires again and updates state file. Logs loudly so we notice.
        print(f"=== SIMON Fast Listener on_ready ===")
        print(f"Connected as {client.user} (id={client.user.id})")
        print(f"Monitoring channel {CHANNEL_ID}")
        print(f"Gateway latency: {client.latency*1000:.0f}ms")
        
        # Update state file
        DISCORD_MESSAGE_STATE_FILE.write_text(json.dumps({
            "last_message_id": None,
            "last_check_ts": int(time.time()),
            "listener_started": int(time.time()),
            "user_id": str(client.user.id),
            "latency_ms": round(client.latency * 1000),
        }, indent=2))
    
    @client.event
    async def on_message(message):
        try:
            await _handle_message(message, client)
        except Exception as e:
            # Outermost safety net — any uncaught error in the handler chain
            # (parse, dedupe, delta write, etc.) logs and returns instead of
            # killing the message dispatch loop. Without this, a transient
            # exception silently disables all subsequent message handling
            # until the daemon is restarted.
            print(
                f"ERROR: Uncaught exception in on_message for "
                f"channel={message.channel.id} author={getattr(message.author, 'id', '?')}: "
                f"{type(e).__name__}: {e}",
                file=sys.stderr,
            )

    async def _handle_message(message, client):
        # Only process messages from the target channel
        if message.channel.id != CHANNEL_ID:
            return
        
        # Skip our own messages
        if message.author == client.user:
            return
        
        # Skip other bots (webhooks, etc.) — only respond to humans and PZ
        # server's Discord chat relay (which arrives as a bot author, but we
        # handle that explicitly via the connection-event path).
        if message.author.bot and message.author != client.user:
            return
        
        # Skip system messages (joins, pin notifications, etc.)
        if message.type != discord.MessageType.default:
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
                # Send via Discord API — PZ chat relay mirrors to in-game.
                channel = client.get_channel(CHANNEL_ID)
                if channel is None:
                    print(f"ERROR: Could not resolve channel {CHANNEL_ID}", file=sys.stderr)
                else:
                    await fire_greeting(channel, player_name)
            else:
                print(f"Skipping {player_name} (dedupe)")
            
            # Update message state
            DISCORD_MESSAGE_STATE_FILE.write_text(json.dumps({
                "last_message_id": str(message.id),
                "last_check_ts": int(time.time()),
                "last_connection": player_name
            }, indent=2))
            
            # Update player delta state for connection messages
            try:
                with open(PLAYER_DELTA_FILE) as f:
                    delta = json.load(f)
                
                if player_name not in delta.get("newPlayers", []):
                    delta.setdefault("newPlayers", []).append(player_name)
                
                if player_name not in delta.get("previousOnline", []):
                    delta.setdefault("previousOnline", []).append(player_name)
                
                delta["lastCheckTs"] = int(time.time())
                
                with open(PLAYER_DELTA_FILE, "w") as f:
                    json.dump(delta, f, indent=2)
            except Exception as e:
                print(f"ERROR updating delta: {e}", file=sys.stderr)
            
            # Connection events handled; don't fall through to chat path
            return
        
        # Otherwise: chat response path. PZ in-game chat messages are mirrored
        # to #pz-molt via the Discord chat relay and arrive here as regular
        # messages. Decide if SIMON should respond.
        should_respond, trigger = should_respond_to_chat(
            message.content, message.author.id
        )
        if should_respond:
            print(f"Chat responder triggered ({trigger}) for {message.author.display_name}: {message.content[:60]}")
            channel = client.get_channel(CHANNEL_ID)
            if channel is None:
                print(f"ERROR: Could not resolve channel {CHANNEL_ID}", file=sys.stderr)
            else:
                await fire_chat_response(
                    channel=channel,
                    content=message.content,
                    player_name=message.author.display_name,
                    trigger=trigger,
                    author_id=message.author.id,
                )
        else:
            print(f"Chat message ignored (no trigger): {message.author.display_name}: {message.content[:60]}")
        
        # Always update message state so we know what we've seen
        try:
            DISCORD_MESSAGE_STATE_FILE.write_text(json.dumps({
                "last_message_id": str(message.id),
                "last_check_ts": int(time.time()),
                "last_author": message.author.display_name,
                "last_trigger": trigger,
            }, indent=2))
        except Exception as e:
            print(f"ERROR updating discord-message-state: {e}", file=sys.stderr)
    
    # Run the client
    try:
        await client.start(token)
    except Exception as e:
        print(f"ERROR: Failed to start listener: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
