#!/usr/bin/env python3
"""
SIMON Context Builder — Gathers all server state into a single JSON payload.
Called by ambient_tick.sh or directly by the AI agent.

Output: JSON with player list, time, weather, mood, recent events, request history.
"""
import json, os, sys, time, subprocess

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(SKILL_DIR, "state")
os.makedirs(STATE_DIR, exist_ok=True)

def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_players():
    """Run RCON players command and parse output."""
    try:
        env = os.environ.copy()
        env_file = os.path.expanduser("~/.env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        env[k.strip()] = v.strip().strip('"').strip("'")
        
        result = subprocess.run(
            ['rcon', '-a', f"{env.get('PZ_RCON_HOST','localhost')}:{env.get('PZ_RCON_PORT','16262')}",
             '-p', env.get('PZ_RCON_PASSWORD', ''), 'players'],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip()
        lines = output.split('\n')
        count = 0
        names = []
        for line in lines:
            if 'Players connected' in line:
                import re
                m = re.search(r'\((\d+)\)', line)
                if m:
                    count = int(m.group(1))
            elif line.strip() and 'Players connected' not in line:
                name = line.strip().rstrip(',').strip()
                if name:
                    names.append(name)
        return count, names
    except Exception as e:
        return 0, []

def get_time_of_day():
    """Classify current time into periods."""
    hour = time.localtime().tm_hour
    if 22 <= hour or hour < 6:
        return "night"
    elif 6 <= hour < 10:
        return "morning"
    elif 10 <= hour < 14:
        return "midday"
    elif 14 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    return "day"

def build_context():
    """Build the full context payload for SIMON's decision-making."""
    now = int(time.time())
    state_file = os.path.join(STATE_DIR, "narrative-state.json")
    requests_file = os.path.join(STATE_DIR, "recent-requests.json")
    profiles_file = os.path.join(STATE_DIR, "player-profiles.json")
    events_file = os.path.join(STATE_DIR, "event-log.json")
    
    # Load state
    state = load_json(state_file, {"tick": 0, "lastEventTs": 0, "mood": "calm", "narrativeThread": "", "lastWeather": ""})
    requests = load_json(requests_file, {"players": {}})
    profiles = load_json(profiles_file, {})
    events = load_json(events_file, {"events": []})
    
    # Increment tick
    state["tick"] = state.get("tick", 0) + 1
    
    # Get current players
    player_count, player_names = get_players()
    
    # Calculate time since last event
    last_event_ts = state.get("lastEventTs", 0)
    seconds_since_event = now - last_event_ts if last_event_ts > 0 else 999999
    
    # Get recent events (last 2 hours)
    recent_events = [e for e in events.get("events", []) if now - e.get("ts", 0) < 7200]
    
    context = {
        "tick": state["tick"],
        "timestamp": now,
        "players": {
            "count": player_count,
            "names": player_names
        },
        "timeOfDay": get_time_of_day(),
        "serverHour": time.localtime().tm_hour,
        "lastWeather": state.get("lastWeather", ""),
        "mood": state.get("mood", "calm"),
        "narrativeThread": state.get("narrativeThread", ""),
        "secondsSinceLastEvent": seconds_since_event,
        "recentEvents": recent_events[-5:],  # Last 5 events
        "recentRequests": requests,
        "playerProfiles": profiles
    }
    
    # Save updated state
    save_json(state_file, state)
    
    return context

def record_event(event_type, details=""):
    """Record an event to the log."""
    events_file = os.path.join(STATE_DIR, "event-log.json")
    events = load_json(events_file, {"events": []})
    events["events"].append({
        "ts": int(time.time()),
        "type": event_type,
        "details": details
    })
    # Keep only last 50 events
    events["events"] = events["events"][-50:]
    save_json(events_file, events)

def update_mood(new_mood):
    """Update the server mood."""
    state_file = os.path.join(STATE_DIR, "narrative-state.json")
    state = load_json(state_file, {"tick": 0, "lastEventTs": 0, "mood": "calm"})
    state["mood"] = new_mood
    save_json(state_file, state)

def update_narrative_thread(thread):
    """Update the current narrative thread."""
    state_file = os.path.join(STATE_DIR, "narrative-state.json")
    state = load_json(state_file, {"tick": 0, "lastEventTs": 0, "mood": "calm"})
    state["narrativeThread"] = thread
    save_json(state_file, state)

if __name__ == "__main__":
    ctx = build_context()
    print(json.dumps(ctx, indent=2))
