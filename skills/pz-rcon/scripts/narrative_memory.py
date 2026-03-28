#!/usr/bin/env python3
"""
Shared narrative memory system for SIMON's PZ radio broadcasts.

Provides:
  - Per-session narrative memory (archived on server empty, wiped after 48h)
  - Per-player narrative memory (persists across sessions)

Usage as library:
  from narrative_memory import NarrativeMemory
  nm = NarrativeMemory(skill_dir="/path/to/pz-rcon-skill")
"""

import json
import os
import time
import glob
import random
from typing import Optional

# ---------------------------------------------------------------------------
# Shared types
# ---------------------------------------------------------------------------

SESSION_DIR = "sessions"
NARRATIVE_HISTORY_DIR = "narrative-history"


class NarrativeMemory:
    """Manages per-session and per-player narrative memory for SIMON."""

    def __init__(self, skill_dir: str):
        self.skill_dir = skill_dir
        self.state_dir = os.path.join(skill_dir, "state")
        self.sessions_dir = os.path.join(self.state_dir, SESSION_DIR)
        self.narrative_dir = os.path.join(self.state_dir, NARRATIVE_HISTORY_DIR)
        self._ensure_dirs()

    # -----------------------------------------------------------------------
    # Directory setup
    # -----------------------------------------------------------------------

    def _ensure_dirs(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.narrative_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Session management
    # -----------------------------------------------------------------------

    def _session_path(self, session_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def get_current_session_id(self) -> Optional[str]:
        """Return the most recent non-archived session id, if any."""
        files = sorted(glob.glob(self._session_path("*")), key=os.path.getmtime, reverse=True)
        for f in files:
            with open(f) as fh:
                data = json.load(f)
            if not data.get("archived"):
                return os.path.basename(f).replace(".json", "")
        return None

    def load_session(self, session_id: str) -> dict:
        """Load a session by id. Returns empty session if not found."""
        path = self._session_path(session_id)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {}

    def create_session(self, players: list) -> dict:
        """Create a new session for a set of players."""
        session_id = f"session_{int(time.time())}"
        session = {
            "sessionId": session_id,
            "startedAt": int(time.time()),
            "endedAt": None,
            "players": {},
            "narrative": [],          # ordered list of broadcast/event records
            "eventsTriggered": [],    # event ids to avoid repeat within session
            "rewardsGiven": [],        # {player, category, item, ts}
            "themeActive": None,
            "archived": False,
        }
        for p in players:
            session["players"][p] = {"joinedAt": int(time.time()), "leftAt": None}
        self.save_session(session)
        return session

    def save_session(self, session: dict):
        session_id = session.get("sessionId", "unknown")
        path = self._session_path(session_id)
        with open(path, "w") as f:
            json.dump(session, f, indent=2)

    def end_session(self, session_id: str):
        """Mark session as ended (players dropped to 0)."""
        session = self.load_session(session_id)
        if session:
            session["endedAt"] = int(time.time())
            session["archived"] = True
            self.save_session(session)
        return session

    def archive_and_clear_stale_sessions(self, max_age_seconds: int = 172800):
        """Remove session files older than max_age_seconds (default 48h)."""
        now = time.time()
        for f in glob.glob(self._session_path("*")):
            try:
                # Only clean archived sessions
                with open(f) as fh:
                    data = json.load(fh)
                if data.get("archived") and (now - os.path.getmtime(f)) > max_age_seconds:
                    os.remove(f)
            except Exception:
                pass

    def add_narrative_entry(self, session_id: str, entry_type: str, content: str,
                              player: str = None, event_type: str = None,
                              item: str = None, metadata: dict = None):
        """
        Append a narrative record to the active session.

        entry_type: "broadcast" | "event" | "reward" | "player_join" | "player_leave"
        """
        session = self.load_session(session_id)
        if not session or session.get("archived"):
            return

        entry = {
            "ts": int(time.time()),
            "type": entry_type,
            "content": content,
        }
        if player:
            entry["player"] = player
        if event_type:
            entry["eventType"] = event_type
            # Track event ids to avoid repeats in this session
            session.setdefault("eventsTriggered", []).append(event_type)
        if item:
            entry["item"] = item
        if metadata:
            entry["metadata"] = metadata

        session.setdefault("narrative", []).append(entry)

        # Keep narrative bounded to last 50 entries per session
        if len(session["narrative"]) > 50:
            session["narrative"] = session["narrative"][-50:]

        self.save_session(session)

    def get_session_narrative_recent(self, session_id: str, seconds: int = 7200) -> list:
        """Return narrative entries from the last `seconds` (default 2h)."""
        session = self.load_session(session_id)
        if not session:
            return []
        cutoff = int(time.time()) - seconds
        return [e for e in session.get("narrative", []) if e.get("ts", 0) >= cutoff]

    def get_session_events(self, session_id: str) -> list:
        """Return list of event type strings triggered in this session."""
        session = self.load_session(session_id)
        return session.get("eventsTriggered", []) if session else []

    def get_session_broadcasts(self, session_id: str, limit: int = 5) -> list:
        """Return the last `limit` broadcast contents from this session."""
        session = self.load_session(session_id)
        if not session:
            return []
        broadcasts = [e["content"] for e in session.get("narrative", [])
                      if e.get("type") == "broadcast"][-limit:]
        return broadcasts

    # -----------------------------------------------------------------------
    # Player narrative history (long-term per player)
    # -----------------------------------------------------------------------

    def _player_narrative_path(self, player: str) -> str:
        # Sanitize player name for filesystem safety
        safe = player.replace("/", "_").replace("\\", "_").replace("..", "_")
        return os.path.join(self.narrative_dir, f"{safe}.json")

    def load_player_narrative(self, player: str) -> dict:
        """Load or initialize a player's long-term narrative memory."""
        path = self._player_narrative_path(player)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return {
            "player": player,
            "firstSeen": int(time.time()),
            "lastSeen": int(time.time()),
            "storyBeats": [],          # significant events witnessed
            "rewardsReceived": [],     # {ts, category, item}
            "requestsMade": [],        # {ts, category, narrative snippet}
            "notes": [],               # free-form notes (RP context, preferences...)
            "visitedLocations": [],    # last known area hints
            "encounteredThemes": [],   # plot themes they've experienced
            "specialFlags": {},        # arbitrary key/value (e.g. "chopper_escaped": true)
        }

    def save_player_narrative(self, player: str, data: dict):
        path = self._player_narrative_path(player)
        data["lastSeen"] = int(time.time())
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def record_player_storybeat(self, player: str, beat: str, detail: str = None,
                                 ts: int = None):
        """Record a significant story event a player witnessed."""
        data = self.load_player_narrative(player)
        entry = {"ts": ts or int(time.time()), "beat": beat}
        if detail:
            entry["detail"] = detail
        data.setdefault("storyBeats", []).append(entry)
        # Keep last 30 beats
        if len(data["storyBeats"]) > 30:
            data["storyBeats"] = data["storyBeats"][-30:]
        self.save_player_narrative(player, data)

    def record_player_reward(self, player: str, category: str, item: str):
        """Record a reward given to a player."""
        data = self.load_player_narrative(player)
        data.setdefault("rewardsReceived", []).append({
            "ts": int(time.time()), "category": category, "item": item
        })
        if len(data["rewardsReceived"]) > 30:
            data["rewardsReceived"] = data["rewardsReceived"][-30:]
        self.save_player_narrative(player, data)

    def record_player_request(self, player: str, category: str, simon_response: str):
        """Record a player request and SIMON's response (for continuity)."""
        data = self.load_player_narrative(player)
        data.setdefault("requestsMade", []).append({
            "ts": int(time.time()), "category": category,
            "simonSaid": simon_response[:120]  # truncate for storage
        })
        if len(data["requestsMade"]) > 30:
            data["requestsMade"] = data["requestsMade"][-30:]
        self.save_player_narrative(player, data)

    def add_player_note(self, player: str, note: str):
        """Add a free-form note about a player (RP context, preferences...)."""
        data = self.load_player_narrative(player)
        data.setdefault("notes", []).append({"ts": int(time.time()), "note": note})
        self.save_player_narrative(player, data)

    def add_player_location(self, player: str, location: str):
        """Track a player's last known area."""
        data = self.load_player_narrative(player)
        locs = data.setdefault("visitedLocations", [])
        if location not in locs:
            locs.append(location)
            if len(locs) > 10:
                locs.pop(0)
        self.save_player_narrative(player, data)

    def set_player_flag(self, player: str, flag: str, value=True):
        """Set a boolean flag on a player's narrative profile."""
        data = self.load_player_narrative(player)
        data.setdefault("specialFlags", {})[flag] = value
        self.save_player_narrative(player, data)

    def get_player_flag(self, player: str, flag: str, default=False):
        data = self.load_player_narrative(player)
        return data.get("specialFlags", {}).get(flag, default)

    def encounter_theme(self, player: str, theme_key: str):
        """Mark that a player has experienced a given plot theme."""
        data = self.load_player_narrative(player)
        themes = data.setdefault("encounteredThemes", [])
        if theme_key not in themes:
            themes.append(theme_key)
        self.save_player_narrative(player, data)

    def player_has_experienced(self, player: str, theme_key: str) -> bool:
        data = self.load_player_narrative(player)
        return theme_key in data.get("encounteredThemes", [])

    def get_player_recent_beats(self, player: str, hours: int = 24) -> list:
        """Return story beats from the last `hours`."""
        data = self.load_player_narrative(player)
        cutoff = int(time.time()) - (hours * 3600)
        return [b for b in data.get("storyBeats", []) if b.get("ts", 0) >= cutoff]

    def get_last_request(self, player: str) -> Optional[dict]:
        """Return the most recent request record for a player."""
        data = self.load_player_narrative(player)
        reqs = data.get("requestsMade", [])
        return reqs[-1] if reqs else None

    # -----------------------------------------------------------------------
    # Coordination helpers (used by director_brain / request_policy)
    # -----------------------------------------------------------------------

    def player_join(self, player: str, session_id: str):
        """Called when a player joins — update session + ensure player profile exists."""
        session = self.load_session(session_id)
        if session and player not in session.get("players", {}):
            session["players"][player] = {"joinedAt": int(time.time()), "leftAt": None}
            self.save_session(session)
        # Ensure player narrative exists
        self.load_player_narrative(player)

    def player_leave(self, player: str, session_id: str):
        """Called when a player leaves the server."""
        session = self.load_session(session_id)
        if session and player in session.get("players", {}):
            session["players"][player]["leftAt"] = int(time.time())
            self.save_session(session)
        self.add_narrative_entry(session_id, "player_leave", f"{player} went offline.", player=player)

    def get_contextual_narrative_for_player(self, player: str, session_id: str) -> str:
        """
        Build a short contextual string summarising recent narrative for a player.
        Used to inject context into SIMON's broadcast generation.
        """
        parts = []
        # Recent session broadcasts
        recent = self.get_session_broadcasts(session_id, limit=3)
        if recent:
            parts.append(f"Recent broadcasts: {' '.join(recent)}")
        # Player's recent story beats
        beats = self.get_player_recent_beats(player, hours=2)
        if beats:
            beat_strs = [b.get("beat", "") for b in beats[-3:]]
            parts.append(f"Player recently experienced: {', '.join(beat_strs)}")
        # Last request
        last_req = self.get_last_request(player)
        if last_req:
            parts.append(f"Last request ({last_req.get('category')}): {last_req.get('simonSaid', '')[:80]}")
        return " | ".join(parts) if parts else ""


# ---------------------------------------------------------------------------
# CLI entrypoint for debugging / testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: narrative_memory.py <action> [args...]")
        print("Actions: create_session, add_entry, player_join, player_leave, player_storybeat, player_info, list_sessions")
        sys.exit(1)

    # Default skill dir — assumes script is in skills/pz-rcon/scripts/
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    SKILL_DIR = os.path.dirname(SCRIPT_DIR)
    nm = NarrativeMemory(SKILL_DIR)

    action = sys.argv[1]

    if action == "create_session":
        players = sys.argv[2].split(",") if len(sys.argv) > 2 else []
        s = nm.create_session(players)
        print(json.dumps(s, indent=2))

    elif action == "add_entry":
        if len(sys.argv) < 4:
            print("Usage: add_entry <session_id> <type> <content>")
            sys.exit(1)
        nm.add_narrative_entry(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))

    elif action == "player_join":
        if len(sys.argv) < 3:
            print("Usage: player_join <player> <session_id>")
            sys.exit(1)
        nm.player_join(sys.argv[2], sys.argv[3])

    elif action == "player_leave":
        if len(sys.argv) < 3:
            print("Usage: player_leave <player> <session_id>")
            sys.exit(1)
        nm.player_leave(sys.argv[2], sys.argv[3])

    elif action == "player_storybeat":
        if len(sys.argv) < 4:
            print("Usage: player_storybeat <player> <beat> [detail]")
            sys.exit(1)
        nm.record_player_storybeat(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]) if len(sys.argv) > 4 else None)

    elif action == "player_info":
        if len(sys.argv) < 3:
            print("Usage: player_info <player>")
            sys.exit(1)
        data = nm.load_player_narrative(sys.argv[2])
        print(json.dumps(data, indent=2))

    elif action == "list_sessions":
        for f in sorted(glob.glob(nm._session_path("*")), key=os.path.getmtime, reverse=True)[:5]:
            with open(f) as fh:
                d = json.load(fh)
            print(f"{os.path.basename(f)}: {d.get('archived', False) and 'ARCHIVED' or 'ACTIVE'} "
                  f"players={list(d.get('players', {}).keys())} "
                  f"narrative={len(d.get('narrative', []))} entries")

    elif action == "archive_stale":
        nm.archive_and_clear_stale_sessions()
        print("Done.")

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
