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

# Positive-result cache. Two callers (cron trigger + chat path) often probe
# within seconds of each other; without this, the second probe races the
# first and can hit a transient baseline-read-failed, which vetoes the LLM.
# Cache only stores SUCCESSFUL rosters (count >= 0) — never errors. The
# default TTL is intentionally short: only covers the same-minute race.
_CACHE_TTL_SECONDS = 20
_roster_cache: dict[str, Any] = {"at": 0.0, "result": {"online": False, "count": 0, "reason": "uncached"}}

# Skill root directory (parent of the scripts/ dir this file lives in).
# Used to anchor the negative-cache file alongside other state files.
SKILL_DIR = Path(__file__).resolve().parent.parent

# PERSISTENT NEGATIVE-RESULT CACHE
# =================================
# The PZ server can be down for hours. Without this, every cron tick
# does the full ~15s Discord API dance (read baseline → send "players" →
# poll for relay response, which never comes), exhausts the code-mode
# budget (~30s), and the agentTurn payload never even gets called.
#
# This file cache holds NEGATIVE results (offline) for 20 minutes. Must
# exceed the SIMON Ambient Director cron's 10-min cadence; with the old
# 5-min TTL every other tick fired a fresh probe (15-30 s of `openclaw
# message` calls) and tipped the cron trigger's 30 s wall-clock budget,
# producing the recurring "code mode timeout exceeded" errors. Detection
# latency when the PZ server returns stays bounded by one cache cycle.
#
# Positive results are NEVER written here. The gate's whole job is to be
# authoritative before claiming "online" — caching a positive on disk
# would risk serving stale "yes" answers if the server died. The 20s
# in-memory cache above handles the same-minute race for positives.
_NEGATIVE_CACHE_TTL_SECONDS = 1200
_NEGATIVE_CACHE_FILE = SKILL_DIR / "state" / "simon-online-gate-cache.json"

# Tier 0: file-based staleness check. The SIMON listener (cron + pz-molt
# reader) already tracks the relay bot's most recent message in this state
# file. If the relay's last post is older than the staleness threshold, we
# know the PZ server is down (or has no activity) WITHOUT making any
# Discord API call. Cuts cold-path latency from ~8 s (failing API read)
# to <0.1 s (single file read + JSON parse). The next tier is the
# persistent negative cache; this file check warms that cache.
_LISTENER_STATE_FILE = SKILL_DIR / "state" / "discord-message-state.json"

# FAIL-FAST: relay-staleness threshold. If the PZ relay bot's most recent
# message in the command channel is older than this, the PZ server is
# clearly down (or has no activity). Skip the slow send/wait dance and
# return negative in <0.5 s. Cold-path latency drops from ~15 s to ~0.5 s,
# keeping the cron trigger well under the 30 s code-mode budget.
#
# Why 5 min: the relay posts immediately on player_join / player_leave /
# server_msg events. Discord webhook latency is <1 s, so any silence >5 min
# means either (a) no players, (b) PZ is down, or (c) relay is broken.
# All three are correctly handled by failing closed.
_RELAY_STALENESS_SECONDS = 300
_DISCORD_EPOCH_MS = 1420070400000


def _snowflake_to_ms(value: Any) -> int:
    """Decode a Discord snowflake to milliseconds since Unix epoch."""
    try:
        return (int(str(value)) >> 22) + _DISCORD_EPOCH_MS
    except (TypeError, ValueError):
        return 0


def _read_negative_cache() -> dict[str, Any] | None:
    """Return the cached negative result if still fresh, else None."""
    try:
        if not _NEGATIVE_CACHE_FILE.exists():
            return None
        cache = json.loads(_NEGATIVE_CACHE_FILE.read_text(encoding="utf-8"))
        if (time.time() - float(cache.get("at", 0))) > _NEGATIVE_CACHE_TTL_SECONDS:
            return None
        result = cache.get("result")
        if not isinstance(result, dict) or result.get("online"):
            return None  # never serve a positive from this cache
        return result
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def _check_state_file_staleness() -> dict[str, Any] | None:
    """Tier 0: read discord-message-state.json, return negative if the
    relay bot's last message in the channel is > _RELAY_STALENESS_SECONDS
    old. Returns None if the file is missing/malformed, the last message
    wasn't from a bot, or the relay is fresh (caller should fall through
    to the API-based probe).

    Fast: single file read + JSON decode. ~1 ms in practice. Used as the
    first check in check_players_online() so cold-path triggers avoid the
    ~8 s failing `openclaw message read` round-trip entirely.
    """
    try:
        state = json.loads(_LISTENER_STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None

    last_message_id = state.get("last_message_id")
    last_author = str(state.get("last_author", ""))
    if not last_message_id or not last_author:
        return None

    # Only trust staleness if the last message was from a bot. The
    # listener tracks relay messages primarily, but a player chatting in
    # #pz-molt could update last_message_id without the relay being
    # active. The PZ relay username is "PZ-Molt-Bot" (contains "bot").
    if "bot" not in last_author.lower() and "relay" not in last_author.lower():
        return None

    last_msg_ms = _snowflake_to_ms(last_message_id)
    if last_msg_ms == 0:
        return None

    age_s = (time.time() * 1000 - last_msg_ms) / 1000.0
    if age_s > _RELAY_STALENESS_SECONDS:
        return {
            "online": False,
            "count": 0,
            "reason": f"relay-stale:{int(age_s)}s",
        }
    return None


def _write_negative_cache(result: dict[str, Any]) -> None:
    """Persist a negative result. Positive results are not written."""
    if not isinstance(result, dict) or result.get("online"):
        return
    try:
        _NEGATIVE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _NEGATIVE_CACHE_FILE.write_text(
            json.dumps({"at": time.time(), "result": result}, separators=(",", ":"))
        )
    except OSError:
        pass


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
    # Tier 0: file-based staleness check (sub-100ms). Reads the SIMON
    # listener's state file to see when the PZ relay last posted. If the
    # relay has been silent for >_RELAY_STALENESS_SECONDS, the PZ server
    # is clearly down (or has no activity) and we can fail fast without
    # making any Discord API call. This is the dominant cold-path speedup.
    file_check = _check_state_file_staleness()
    if file_check is not None:
        _write_negative_cache(file_check)
        return file_check

    # Tier 1: persistent negative cache (sub-second). Saves us from the
    # full ~15s Discord API dance when the PZ server has been offline.
    neg_cached = _read_negative_cache()
    if neg_cached is not None:
        return dict(neg_cached)

    now = time.monotonic()
    cached = _roster_cache.get("result") or {}
    cache_age = now - float(_roster_cache.get("at") or 0.0)
    cached_reason = str(cached.get("reason") or "")
    if cache_age < _CACHE_TTL_SECONDS and cached_reason == "authoritative-roster":
        return dict(cached)

    env_path = Path(os.path.expanduser(env_file or os.environ.get("ENV_FILE", "~/.env")))
    env = load_env(env_path)
    channel_id = os.environ.get("PZ_DISCORD_COMMANDS_CHANNEL_ID") or env.get("PZ_DISCORD_COMMANDS_CHANNEL_ID", "")
    relay_id = os.environ.get("PZ_RELAY_BOT_ID") or env.get("PZ_RELAY_BOT_ID", "")

    if not channel_id or not relay_id:
        result = {"online": False, "count": 0, "reason": "missing-config"}
        _write_negative_cache(result)
        return result

    target = f"channel:{channel_id}"
    read_cmd = ["openclaw", "message", "read", "--channel", "discord", "--target", target, "--limit", "10", "--json"]

    # Hard cap per Discord API call. The SIMON Ambient Director cron's
    # trigger has a 30 s wall-clock budget; with two back-to-back slow
    # `openclaw message` round-trips (~10-17 s each in OpenClaw 2026.10.x)
    # the probe tips that budget and times out. 8 s covers a healthy API
    # (<1 s) and fast-fails before the trigger times out. Fast-fail is
    # fail-closed by design (we write the negative cache), so this never
    # produces a false positive.
    _PROBE_STEP_TIMEOUT_SECONDS = 8

    try:
        before = _run(read_cmd, timeout=_PROBE_STEP_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        result = {"online": False, "count": 0, "reason": "baseline-read-failed"}
        _write_negative_cache(result)
        return result
    if before.returncode != 0:
        result = {"online": False, "count": 0, "reason": "baseline-read-failed"}
        _write_negative_cache(result)
        return result

    baseline = _newest_relay_id(_messages(before.stdout), relay_id)

    # Fail-fast on cold cache: if the relay bot's most recent message in
    # the channel is older than _RELAY_STALENESS_SECONDS, the PZ server is
    # clearly down (or has no activity for 5+ min). Skip the slow
    # send/wait dance and return immediately. Negative cache will absorb
    # subsequent calls within the 20-min TTL.
    relay_messages = [m for m in _messages(before.stdout) if _author_id(m) == relay_id]
    if relay_messages:
        newest_relay = max(relay_messages, key=lambda m: _snowflake(m.get("id")))
        relay_age_s = (time.time() * 1000 - _snowflake_to_ms(newest_relay.get("id"))) / 1000
        if relay_age_s > _RELAY_STALENESS_SECONDS:
            result = {
                "online": False,
                "count": 0,
                "reason": f"relay-stale:{int(relay_age_s)}s",
            }
            _write_negative_cache(result)
            return result

    try:
        sent = _run([
            "openclaw", "message", "send",
            "--channel", "discord",
            "--target", target,
            "--message", "players",
        ], timeout=_PROBE_STEP_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        result = {"online": False, "count": 0, "reason": "players-send-failed"}
        _write_negative_cache(result)
        return result
    if sent.returncode != 0:
        result = {"online": False, "count": 0, "reason": "players-send-failed"}
        _write_negative_cache(result)
        return result

    deadline = time.monotonic() + max(1, timeout_seconds)
    while time.monotonic() < deadline:
        time.sleep(0.5)
        try:
            poll_result = _run(read_cmd, timeout=_PROBE_STEP_TIMEOUT_SECONDS)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if poll_result.returncode != 0:
            continue

        candidates = []
        for message in _messages(poll_result.stdout):
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
            roster = {"online": count > 0, "count": count, "reason": "authoritative-roster"}
            _roster_cache.update({"at": time.monotonic(), "result": dict(roster)})
            return roster

    result = {"online": False, "count": 0, "reason": "roster-timeout"}
    _write_negative_cache(result)
    return result


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
