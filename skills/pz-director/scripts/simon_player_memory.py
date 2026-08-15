#!/usr/bin/env python3
"""SIMON's per-player memory.

Each survivor on the PZ server gets their own profile file under
``state/memory/players/<slug>.json``. Profiles record:
- visit history (firstSeen, lastSeen, visitCount, tier)
- recent chats (capped at 20)
- arc recaps captured while an arc was unraveling
- free-form notes SIMON accumulates about the player

The listener (``simon_radio_listener.py``) calls ``bump_visit`` from an authoritative log-channel connection event
and ``record_interaction`` on chat. The ambient cron payload reads profiles
via ``get_brief`` to surface player context in narrations, and via
``append_arc_recap`` to save an entry to a player's file while a narrative
arc is active.

This module is the single source of truth for per-player memory. The legacy
``state/player-registry.json`` is a derived cache written by ``bump_visit``
for backward compatibility with the listener's existing tier detection.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = SKILL_DIR / "state" / "memory"
PLAYERS_DIR = MEMORY_DIR / "players"
INDEX_FILE = PLAYERS_DIR / "index.json"
LEGACY_REGISTRY = SKILL_DIR / "state" / "player-registry.json"

MAX_RECENT_CHATS = 20
MAX_ARC_RECAPS = 8
MAX_NOTES = 12


def _slug(name: str) -> str:
    """Normalize a player name into a filesystem-safe slug.

    Examples:
        "PlayerName" -> "playername"
        "Big Mike"   -> "big-mike"
        "SARAH_x"    -> "sarah-x"
    """
    if not name:
        return "unknown"
    s = name.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"


def _read_json(path: Path, default):
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def load_index() -> dict:
    return _read_json(INDEX_FILE, {"_about": "player index", "players": {}, "schemaVersion": 1})


def save_index(idx: dict) -> None:
    _write_json(INDEX_FILE, idx)


def profile_path(name: str) -> Path:
    return PLAYERS_DIR / f"{_slug(name)}.json"


def default_profile(name: str) -> dict:
    now = int(time.time())
    return {
        "_about": "per-player profile (simon_player_memory)",
        "schemaVersion": 1,
        "name": name,
        "slug": _slug(name),
        "firstSeen": now,
        "lastSeen": now,
        "visitCount": 0,
        "tier": "new",
        "recentChats": [],          # [{ts, channel, content, trigger, simon_reply_summary}]
        "arcRecaps": [],            # [{arcId, ts, summary}] — last MAX_ARC_RECAPS
        "notes": [],                # free-form, last MAX_NOTES
        "honorific": "survivor",
        "callbacksSeeded": [],      # callback hooks the LLM has used (de-dupe)
    }


def load_profile(name: str) -> dict:
    p = profile_path(name)
    prof = _read_json(p, None)
    if prof is None:
        prof = default_profile(name)
    return prof


def save_profile(prof: dict) -> None:
    name = prof.get("name") or "unknown"
    prof["slug"] = _slug(name)
    prof["lastSeen"] = int(time.time())
    _write_json(profile_path(name), prof)
    # Update index pointer
    idx = load_index()
    idx.setdefault("players", {})[prof["slug"]] = {
        "name": prof["name"],
        "lastSeen": prof["lastSeen"],
        "visitCount": prof.get("visitCount", 0),
    }
    save_index(idx)
    # Mirror to legacy registry so listener's get_player_tier keeps working
    mirror_legacy_registry(prof)


def mirror_legacy_registry(prof: dict) -> None:
    """Write a minimal entry into state/player-registry.json for backward
    compatibility with the listener's tier detection. New code should call
    ``get_brief`` instead of reading this file directly."""
    data = _read_json(LEGACY_REGISTRY, {"players": {}})
    data.setdefault("players", {})[prof["name"]] = {
        "name": prof["name"],
        "firstSeen": prof.get("firstSeen"),
        "lastSeen": prof.get("lastSeen"),
        "visitCount": prof.get("visitCount", 0),
        "tier": prof.get("tier"),
        "honorific": prof.get("honorific", "survivor"),
        "notes": prof.get("notes", [])[-3:],
    }
    _write_json(LEGACY_REGISTRY, data)


def reset_all_player_memory() -> int:
    """Wipe every per-player profile + index + legacy registry. Returns
    the count of profile files removed.

    This is the surgical 'online player memory reset' — it does NOT touch:
      - state/memory/arcs/  (arc engine state)
      - state/memory/global/ (server lore + history + reset-marker)
      - state/greeting-queue.json (greeter dedupe — handled separately)
    For a full world/server wipe including arc and global memory, use
    ``scripts/simon_reset_world.py``.

    Use cases:
      - Operator wants to start the survivor roster fresh while keeping the
        lore/history/arc system intact (most common).
      - Soft reset between playtests.

    Note: greeting-queue.json is NOT cleared here — that has its own
    lifecycle (greeting dispatcher rules) and should be cleared
    deliberately with ``state/greeting-queue.json`` -> {"pending":[],
    "handled":[]} if you want a complete slate.
    """
    removed = 0
    if PLAYERS_DIR.exists():
        for child in PLAYERS_DIR.iterdir():
            if child.is_file() and child.suffix == ".json":
                try:
                    child.unlink()
                    removed += 1
                except OSError:
                    pass

    # Reset index to default
    save_index({"_about": "player index", "players": {}, "schemaVersion": 1})

    # Reset legacy registry (the listener's tier-detection file)
    _write_json(LEGACY_REGISTRY, {"players": {}})

    return removed


def delete_profile(name: str) -> bool:
    """Remove a player profile entirely. Idempotent — returns True if the
    profile existed and was removed, False if there was nothing to delete.

    Use cases:
      - Smoke tests / operator cleanup
      - GDPR / privacy erase for a specific player
      - Note: the global ``simon_reset_world.py`` script wipes EVERY profile
        and bypasses this helper — use that for world/server resets.
    """
    p = profile_path(name)
    slug = _slug(name)
    removed_file = False
    if p.exists():
        try:
            p.unlink()
            removed_file = True
        except OSError:
            pass

    idx = load_index()
    removed_index = False
    if isinstance(idx.get("players"), dict) and slug in idx["players"]:
        idx["players"].pop(slug, None)
        save_index(idx)
        removed_index = True

    # Mirror to legacy registry
    legacy = _read_json(LEGACY_REGISTRY, {"players": {}})
    if isinstance(legacy.get("players"), dict) and name in legacy["players"]:
        legacy["players"].pop(name, None)
        _write_json(LEGACY_REGISTRY, legacy)

    return removed_file or removed_index


def tier_for(visit_count: int) -> str:
    if visit_count <= 1:
        return "new"
    if visit_count <= 5:
        return "returning"
    return "veteran"


def bump_visit(name: str) -> dict:
    """Increment visit count, update lastSeen, set tier. Returns the profile."""
    prof = load_profile(name)
    now = int(time.time())
    prof["visitCount"] = int(prof.get("visitCount", 0)) + 1
    prof["lastSeen"] = now
    if prof["visitCount"] == 1:
        prof["firstSeen"] = now
    prof["tier"] = tier_for(prof["visitCount"])
    save_profile(prof)
    return prof


def record_interaction(
    name: str,
    kind: str,
    content: str,
    trigger: str | None = None,
    simon_reply_summary: str | None = None,
) -> dict:
    """Append an interaction to the player's recentChats ring (capped)."""
    prof = load_profile(name)
    entry = {
        "ts": int(time.time()),
        "kind": kind,
        "content": str(content)[:600],
    }
    if trigger:
        entry["trigger"] = trigger
    if simon_reply_summary:
        entry["simon_reply_summary"] = str(simon_reply_summary)[:300]
    prof.setdefault("recentChats", []).append(entry)
    # cap
    prof["recentChats"] = prof["recentChats"][-MAX_RECENT_CHATS:]
    # tier may have advanced since first interaction — recompute if warranted
    prof["tier"] = tier_for(prof.get("visitCount", 0))
    save_profile(prof)
    return prof


def append_note(name: str, note: str) -> dict:
    """Add a free-form note (LLM-written) to a profile. Used to remember
    survivor traits, quirks, etc. Caps at MAX_NOTES."""
    prof = load_profile(name)
    prof.setdefault("notes", []).append({"ts": int(time.time()), "note": str(note)[:280]})
    prof["notes"] = prof["notes"][-MAX_NOTES:]
    save_profile(prof)
    return prof


def append_arc_recap(name: str, arc_id: str, summary: str) -> dict:
    """Append a per-player arc-recap entry. Caps at MAX_ARC_RECAPS."""
    prof = load_profile(name)
    prof.setdefault("arcRecaps", []).append(
        {"arcId": arc_id, "ts": int(time.time()), "summary": str(summary)[:400]}
    )
    prof["arcRecaps"] = prof["arcRecaps"][-MAX_ARC_RECAPS:]
    save_profile(prof)
    return prof


def mark_callback_used(name: str, callback_str: str) -> dict:
    prof = load_profile(name)
    used = prof.setdefault("callbacksSeeded", [])
    cb = str(callback_str)[:140]
    if cb and cb not in used:
        used.append(cb)
        prof["callbacksSeeded"] = used[-40:]
        save_profile(prof)
    return prof


def get_brief(name: str, max_chats: int = 4) -> str:
    """Format a player profile into a brief paragraph for LLM prompts.

    Use this in SIMON's chat/ambient/greeting prompt context so replies can
    reference past chats, tier, and notes naturally.
    """
    prof = load_profile(name)
    if not prof or prof.get("visitCount", 0) == 0:
        return "Unknown survivor. First contact."

    parts = [f"{prof.get('honorific', 'survivor')} {prof.get('name', name)}"]
    parts.append(f"tier: {prof.get('tier', 'new')}")
    parts.append(f"visit count {prof.get('visitCount', 0)}")

    now = int(time.time())
    first_seen = prof.get("firstSeen", 0)
    last_seen = prof.get("lastSeen", 0)
    if first_seen:
        days_known = max(0, (now - first_seen) // 86400)
        if days_known:
            parts.append(f"known for {days_known} days")
    if last_seen:
        since = max(0, (now - last_seen))
        if since >= 86400:
            parts.append(f"last seen {(since // 86400)}d ago")
        elif since >= 3600:
            parts.append(f"last seen {(since // 3600)}h ago")
        else:
            parts.append(f"last seen {(since // 60)}m ago")

    notes = prof.get("notes", [])
    if notes:
        recent = "; ".join(n.get("note", "") if isinstance(n, dict) else str(n) for n in notes[-3:])
        if recent:
            parts.append(f"notes: {recent}")

    arc_recaps = prof.get("arcRecaps", [])
    if arc_recaps:
        last_arc = arc_recaps[-1]
        parts.append(f"last arc: {last_arc.get('arcId', '?')} ({last_arc.get('summary', '')[:80]})")

    chats = prof.get("recentChats", [])[-max_chats:]
    if chats:
        recent_topics = []
        for c in chats[-3:]:
            content = c.get("content", "")
            snippet = content[:60].replace("\n", " ")
            recent_topics.append(snippet)
        if recent_topics:
            parts.append(f"recent: {' | '.join(recent_topics)}")

    return ", ".join(parts)


def list_known() -> list[str]:
    idx = load_index()
    return [v["name"] for v in idx.get("players", {}).values() if "name" in v]


if __name__ == "__main__":
    # Smoke test: bump_visit + record_interaction + get_brief round-trip.
    import sys
    test_name = "_smoke_player"
    bump_visit(test_name)
    record_interaction(test_name, "chat", "hello simon, heard anything up north?")
    append_note(test_name, "asks about storms a lot")
    append_arc_recap(test_name, "blackout", "stayed quiet through the storm")
    print(get_brief(test_name))
    # Cleanup the smoke profile so the file system stays tidy.
    p = profile_path(test_name)
    if p.exists():
        p.unlink()
    idx = load_index()
    if _slug(test_name) in idx.get("players", {}):
        del idx["players"][_slug(test_name)]
        save_index(idx)
    print(f"smoke ok: {test_name}")
