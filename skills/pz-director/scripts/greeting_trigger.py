#!/usr/bin/env python3
"""Fail-closed trigger gate for the SIMON Greeting Dispatcher cron."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from simon_online_gate import check_players_online

QUEUE_FILE = Path(__file__).resolve().parent.parent / "state" / "greeting-queue.json"


def emit(fire: bool, reason: str) -> None:
    print(json.dumps({"fire": fire, "reason": reason}, separators=(",", ":")))
    sys.exit(0)


def main() -> None:
    # A stale queue must never wake the LLM after everyone has disconnected.
    presence = check_players_online()
    if not presence.get("online"):
        emit(False, "offline")

    try:
        queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else {}
    except (json.JSONDecodeError, OSError):
        emit(False, "queue-unreadable")

    pending = queue.get("pending", [])
    if isinstance(pending, list) and pending:
        emit(True, "pending-and-online")

    emit(False, "no-pending-greeting")


if __name__ == "__main__":
    main()
