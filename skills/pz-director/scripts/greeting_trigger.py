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
    # Cheap gate first: an empty queue must never touch the Discord roster
    # probe (this runs every minute; probing would spam the command channel).
    try:
        queue = json.loads(QUEUE_FILE.read_text()) if QUEUE_FILE.exists() else {}
    except (json.JSONDecodeError, OSError):
        emit(False, "queue-unreadable")

    pending = queue.get("pending", [])
    if not (isinstance(pending, list) and pending):
        emit(False, "no-pending-greeting")

    # A stale queue must never wake the LLM after everyone has disconnected.
    # Fire only when a greeting is pending AND the authoritative roster
    # confirms someone is online. Any probe failure fails closed.
    presence = check_players_online()
    if not presence.get("online"):
        emit(False, "offline")

    emit(True, "pending-and-online")


if __name__ == "__main__":
    main()
