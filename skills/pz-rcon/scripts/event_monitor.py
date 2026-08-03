#!/usr/bin/env python3
"""
Event Monitor — Watches server logs for mod events and writes them
to state/mod-events.json for director_brain.py to react to.

Runs as part of the ambient tick cycle or standalone.
"""
import json
import os
import re
import time
from ftplib import FTP

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
STATE_DIR = os.path.join(SKILL_DIR, "state")
EVENTS_FILE = os.path.join(STATE_DIR, "mod-events.json")
ENV_FILE = os.path.expanduser("~/.env")

# How far back to look (in log lines)
TAIL_LINES = 200
# Max events to keep
MAX_EVENTS = 50

def load_env():
    """Load FTP credentials from .env"""
    env = {}
    try:
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    val = val.strip('"').strip("'")
                    env[key] = val
    except:
        pass
    return env

def get_latest_log_tail(ftp, lines=200):
    """Get the tail of the latest screenlog via FTP."""
    try:
        entries = []
        ftp.retrlines('LIST /51.210.86.141_17200/', entries.append)
        
        # Find latest screenlog by date (not by name, since names cycle)
        screenlogs = []
        for e in entries:
            parts = e.split()
            if len(parts) >= 4 and 'screenlog' in parts[-1]:
                # Parse date: MM-DD-YY HH:MMAM/PM
                date_str = parts[0] + ' ' + parts[1]
                screenlogs.append((date_str, parts[-1]))
        
        if not screenlogs:
            return []
        
        # Sort by filename number (higher = newer usually, but let's use date)
        # Actually, just pick the most recently modified one
        # The LIST output has dates, let's pick the latest date
        from datetime import datetime
        def parse_date(d):
            try:
                return datetime.strptime(d, '%m-%d-%y %I:%M%p')
            except:
                return datetime.min
        
        screenlogs.sort(key=lambda x: parse_date(x[0]), reverse=True)
        latest = screenlogs[0][1]
        
        data = []
        ftp.retrbinary(f'RETR /51.210.86.141_17200/{latest}', data.append)
        content = b''.join(data).decode('utf-8', errors='replace')
        
        # Strip HTML tags
        clean_lines = []
        for line in content.strip().split('\n'):
            clean = re.sub(r'<[^>]+>', '', line).strip()
            clean = clean.replace('&nbsp;', ' ').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
            if clean:
                clean_lines.append(clean)
        
        return clean_lines[-lines:]
    except Exception as ex:
        print(f"FTP error: {ex}")
        return []

def detect_events(lines):
    """Detect mod events from log lines."""
    events = []
    now = int(time.time())
    
    # Event patterns to detect
    patterns = {
        "blackout": {
            "keywords": ["power off", "power off", "blackout", "electricity shutdown", "power failure"],
            "severity": "high",
            "simon_react": True
        },
        "power_restore": {
            "keywords": ["power on", "electricity restored", "power restored"],
            "severity": "low",
            "simon_react": True
        },
        "weather_storm": {
            "keywords": ["thunder", "lightning", "storm started"],
            "severity": "medium",
            "simon_react": True
        },
        "weather_rain": {
            "keywords": ["rain started", "rain begin"],
            "severity": "low",
            "simon_react": True
        },
        "weather_clear": {
            "keywords": ["weather stop", "clear weather", "rain stopped"],
            "severity": "low",
            "simon_react": False
        },
        "horde_detected": {
            "keywords": ["horde", "massive bio-signal", "convergence detected"],
            "severity": "critical",
            "simon_react": True
        },
        "structure_damage": {
            "keywords": ["thump", "wall damaged", "barricade", "structure attack"],
            "severity": "high",
            "simon_react": True
        },
        "vehicle_spawn": {
            "keywords": ["vehicle spawned", "vehicle near"],
            "severity": "low",
            "simon_react": False
        },
        "player_death": {
            "keywords": ["was killed", "has died", "death"],
            "severity": "high",
            "simon_react": True
        },
        "airdrop": {
            "keywords": ["airdrop", "supply drop", "supply crate"],
            "severity": "medium",
            "simon_react": True
        }
    }
    
    for line in lines:
        line_lower = line.lower()
        for event_type, config in patterns.items():
            for keyword in config["keywords"]:
                if keyword in line_lower:
                    events.append({
                        "type": event_type,
                        "severity": config["severity"],
                        "simon_react": config["simon_react"],
                        "ts": now,
                        "log_line": line[:200],
                        "keyword": keyword
                    })
                    break  # One event per line per type
    
    return events

def load_existing_events():
    """Load previously detected events."""
    try:
        with open(EVENTS_FILE) as f:
            return json.load(f)
    except:
        return {"events": [], "last_check": 0, "last_log_line": 0}

def save_events(data):
    """Save events to state file."""
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(EVENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_weather_state(ftp):
    """Try to detect current weather from log."""
    try:
        # Check recent log for weather indicators
        lines = get_latest_log_tail(ftp, lines=50)
        for line in lines[-20:]:
            ll = line.lower()
            if 'storm' in ll or 'thunder' in ll:
                return "storm"
            if 'rain' in ll:
                return "rain"
        return "clear"
    except:
        return "unknown"

def get_time_of_day():
    """Get current time context."""
    from datetime import datetime
    now = datetime.now()
    hour = now.hour
    if 5 <= hour < 8:
        return "dawn"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 20:
        return "evening"
    elif 20 <= hour < 23:
        return "night"
    else:
        return "late_night"

def main():
    """Main event monitor loop."""
    env = load_env()
    ftp_host = env.get('PZ_FTP_HOST', '')
    ftp_port = int(env.get('PZ_FTP_PORT', '21'))
    ftp_user = env.get('PZ_FTP_USER', '')
    ftp_pass = env.get('PZ_FTP_PASS', '')
    
    if not all([ftp_host, ftp_user, ftp_pass]):
        print("ERROR: Missing FTP credentials in .env")
        return
    
    # Load existing state
    state = load_existing_events()
    
    try:
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port)
        ftp.login(ftp_user, ftp_pass)
        
        # Get recent log lines
        log_lines = get_latest_log_tail(ftp, lines=TAIL_LINES)
        
        # Detect new events
        new_events = detect_events(log_lines)
        
        # Get weather context
        weather = get_weather_state(ftp)
        
        ftp.quit()
    except Exception as ex:
        print(f"FTP connection error: {ex}")
        new_events = []
        weather = "unknown"
    
    # Filter out events we've already seen (by keyword + timestamp proximity)
    existing_keywords = set()
    for evt in state.get("events", []):
        existing_keywords.add(f"{evt['type']}_{evt.get('keyword', '')}_{evt.get('ts', 0) // 300}")
    
    fresh_events = []
    for evt in new_events:
        key = f"{evt['type']}_{evt.get('keyword', '')}_{evt.get('ts', 0) // 300}"
        if key not in existing_keywords:
            fresh_events.append(evt)
            existing_keywords.add(key)
    
    # Add fresh events to state
    state["events"].extend(fresh_events)
    
    # Trim old events
    if len(state["events"]) > MAX_EVENTS:
        state["events"] = state["events"][-MAX_EVENTS:]
    
    # Update metadata
    state["last_check"] = int(time.time())
    state["weather"] = weather
    state["time_of_day"] = get_time_of_day()
    state["new_events_count"] = len(fresh_events)
    
    # Mark unprocessed events
    for evt in state["events"]:
        if "processed" not in evt:
            evt["processed"] = False
    
    save_events(state)
    
    # Output summary
    if fresh_events:
        print(f"Detected {len(fresh_events)} new events:")
        for evt in fresh_events:
            print(f"  [{evt['severity'].upper()}] {evt['type']}: {evt['keyword']}")
    else:
        print("No new events detected.")
    
    print(f"Context: weather={weather}, time={get_time_of_day()}")

if __name__ == "__main__":
    main()
