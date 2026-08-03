#!/usr/bin/env python3
"""
SIMON Ambient Trigger — Lightweight player-count check.
Runs headlessly before the LLM is called. Returns { "fire": true }
only when at least one player is online, saving LLM tokens on empty
server ticks.

Called by the SIMON ambient cron (4c5d0ca5) as a trigger script.
Outputs JSON to stdout: { "fire": true|false }
"""

import json
import subprocess
import sys

RCON_SCRIPT = "/home/starbugmolt/.openclaw/workspace-simon/skills/pz-rcon/scripts/pz-rcon.sh"
ENV_FILE = "/home/starbugmolt/.env"


def get_online_players():
    """Run 'pz-rcon.sh players' and return a list of player names."""
    try:
        result = subprocess.run(
            [RCON_SCRIPT, "players"],
            capture_output=True,
            text=True,
            timeout=10,
            env={
                "HOME": "/home/starbugmolt",
                "PATH": "/usr/local/bin:/usr/bin:/bin",
            },
        )
        # pz-rcon.sh outputs lines like: -  PlayerName (id)
        players = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("-") and not line.startswith("--"):
                # Extract name between "- " and " ("
                name_part = line.lstrip("- ").strip()
                if "(" in name_part:
                    name = name_part.rsplit("(", 1)[0].strip()
                else:
                    name = name_part.strip()
                if name:
                    players.append(name)
        return players
    except Exception:
        return []


def main():
    players = get_online_players()
    fire = len(players) > 0
    result = {"fire": fire}
    if players:
        result["players"] = players
    print(json.dumps(result))


if __name__ == "__main__":
    main()
