#!/usr/bin/env python3
"""Authoritative, non-LLM online-player gate for SIMON scheduled jobs.

Every cron path that could lead to an LLM call must pass this gate first.
It sends the PZ `players` console command through the configured Discord
command channel, then accepts only a NEW response from the exact configured
PZ relay bot. Any timeout, malformed response, missing config, or ambiguity
fails closed: online=False.

False negatives are acceptable. False positives that wake an unnecessary LLM
are not.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PLAYERS_RE = re.compile(r"Players\s+connected\s+\((\d+)\)", re.IGNORECASE)


def load_env(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _run(args: list[str], timeout: float = 8.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def _messages(payload: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []
    messages = data.get("payload", {}).get("messages", data.get("messages", []))
    return messages if isinstance(messages, list) else []


def _snowflake(value: Any) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _author_id(message: dict[str, Any]) -> str:
    author = message.get("author", {})
    return str(author.get("id", "")) if isinstance(author, dict) else ""


def _newest_relay_id(messages: list[dict[str, Any]], relay_id: str) -> int:
    ids = [_snowflake(m.get("id")) for m in messages if _author_id(m) == relay_id]
    return max(ids, default=0)


def check_players_online(timeout_seconds: int = 8, env_file: str | None = None) -> dict[str, Any]:
    env_path = Path(os.path.expanduser(env_file or os.environ.get("ENV_FILE", "~/.env")))
    env = load_env(env_path)
    channel_id = os.environ.get("PZ_DISCORD_COMMANDS_CHANNEL_ID") or env.get("PZ_DISCORD_COMMANDS_CHANNEL_ID", "")
    relay_id = os.environ.get("PZ_RELAY_BOT_ID") or env.get("PZ_RELAY_BOT_ID", "")

    if not channel_id or not relay_id:
        return {"online": False, "count": 0, "reason": "missing-config"}

    target = f"channel:{channel_id}"
    read_cmd = ["openclaw", "message", "read", "--channel", "discord", "--target", target, "--limit", "10"]

    try:
        before = _run(read_cmd, timeout=6)
    except (OSError, subprocess.TimeoutExpired):
        return {"online": False, "count": 0, "reason": "baseline-read-failed"}
    if before.returncode != 0:
        return {"online": False, "count": 0, "reason": "baseline-read-failed"}

    baseline = _newest_relay_id(_messages(before.stdout), relay_id)

    try:
        sent = _run([
            "openclaw", "message", "send",
            "--channel", "discord",
            "--target", target,
            "--message", "players",
        ], timeout=6)
    except (OSError, subprocess.TimeoutExpired):
        return {"online": False, "count": 0, "reason": "players-send-failed"}
    if sent.returncode != 0:
        return {"online": False, "count": 0, "reason": "players-send-failed"}

    deadline = time.monotonic() + max(1, timeout_seconds)
    while time.monotonic() < deadline:
        time.sleep(0.5)
        try:
            result = _run(read_cmd, timeout=6)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0:
            continue

        candidates = []
        for message in _messages(result.stdout):
            if _author_id(message) != relay_id:
                continue
            message_id = _snowflake(message.get("id"))
            if message_id <= baseline:
                continue
            candidates.append((message_id, str(message.get("content", ""))))

        for _message_id, content in sorted(candidates):
            match = PLAYERS_RE.search(content)
            if not match:
                continue
            count = int(match.group(1))
            return {"online": count > 0, "count": count, "reason": "authoritative-roster"}

    return {"online": False, "count": 0, "reason": "roster-timeout"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed SIMON online-player gate")
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--env-file")
    args = parser.parse_args()

    result = check_players_online(args.timeout, args.env_file)
    print(json.dumps(result, separators=(",", ":")))
    sys.exit(0 if result["online"] else 3)


if __name__ == "__main__":
    main()
