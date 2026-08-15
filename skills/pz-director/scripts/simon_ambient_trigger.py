#!/usr/bin/env python3
"""Fail-closed preflight for the SIMON Ambient Director cron.

The trigger performs only deterministic, non-LLM work. An ambient model turn is
allowed only when a fresh authoritative roster proves at least one player is
online and a cheap local rule says a director decision is due.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from simon_online_gate import check_players_online

SKILL_DIR = Path(__file__).resolve().parent.parent
NARRATIVE_STATE_FILE = SKILL_DIR / "state" / "narrative-state.json"
DEFAULT_MIN_INTERVAL_SECONDS = 15 * 60


def emit(fire: bool, reason: str, players: int = 0) -> None:
    print(json.dumps({"fire": fire, "reason": reason, "players": players}, separators=(",", ":")))
    raise SystemExit(0)


def _read_json(path: Path, default):
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _arc_beat_ready() -> bool:
    try:
        import simon_arc_engine
        return bool(simon_arc_engine.is_beat_ready())
    except Exception:
        return False


def _offline_housekeeping() -> None:
    try:
        import simon_arc_engine
        simon_arc_engine.cleanup_stale_arc()
    except Exception:
        pass


def main() -> None:
    presence = check_players_online()
    count = int(presence.get("count", 0) or 0)
    if not presence.get("online") or count <= 0:
        _offline_housekeeping()
        emit(False, f"offline:{presence.get('reason', 'unknown')}", 0)

    if _arc_beat_ready():
        emit(True, "arc-beat-ready", count)

    try:
        min_interval = int(os.environ.get("SIMON_AMBIENT_MIN_INTERVAL_SECONDS", DEFAULT_MIN_INTERVAL_SECONDS))
    except ValueError:
        min_interval = DEFAULT_MIN_INTERVAL_SECONDS
    min_interval = max(60, min_interval)

    state = _read_json(NARRATIVE_STATE_FILE, {})
    try:
        last_event = int(state.get("lastEventTs", 0) or 0) if isinstance(state, dict) else 0
    except (TypeError, ValueError):
        last_event = 0

    now = int(time.time())
    if last_event and (now - last_event) < min_interval:
        emit(False, "ambient-cooldown", count)

    emit(True, "ambient-due", count)


if __name__ == "__main__":
    main()
