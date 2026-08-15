#!/usr/bin/env python3
"""SIMON narrative arc engine.

The arc engine is the single owner of narrative-arc state. Trigger helpers may
ask whether a beat is ready, but they must not independently rewrite/finalize
arc schemas. Player-facing context exposes only already-fired information.
"""
from __future__ import annotations

import json
import os
import random
import re
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = SKILL_DIR / "state" / "memory"
ARCS_DIR = MEMORY_DIR / "arcs"
ACTIVE_FILE = ARCS_DIR / "active.json"
INDEX_FILE = ARCS_DIR / "index.json"
CATALOG_FILE = SKILL_DIR / "references" / "narrative-arcs.md"

ARC_RESET_HOURS = 4
STALE_PLAYER_MINUTES = 30
MAX_NARRATIONS = 50
MAX_INTERACTIONS = 60


def _read_json(path: Path, default):
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
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


def load_catalog() -> dict:
    if not CATALOG_FILE.exists():
        return {"arcs": []}
    try:
        text = CATALOG_FILE.read_text(encoding="utf-8")
    except OSError:
        return {"arcs": []}
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        return {"arcs": []}
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {"arcs": []}
    return data if isinstance(data, dict) else {"arcs": []}


def pick_random_arc(exclude: list[str] | None = None) -> dict | None:
    catalog = load_catalog()
    arcs = [arc for arc in catalog.get("arcs", []) if isinstance(arc, dict)]
    excluded = set(exclude or [])
    pool = [arc for arc in arcs if arc.get("arcId") not in excluded] or arcs
    return random.choice(pool) if pool else None


def get_active_arc() -> dict | None:
    value = _read_json(ACTIVE_FILE, None)
    return value if isinstance(value, dict) else None


def recent_completed_within_hours(hours: int) -> bool:
    index = _read_json(INDEX_FILE, {"completed": []})
    cutoff = int(time.time()) - max(0, int(hours)) * 3600
    completed = index.get("completed", []) if isinstance(index, dict) else []
    return any(isinstance(entry, dict) and int(entry.get("ts", 0) or 0) >= cutoff for entry in completed)


def start_arc(arc_id: str | None = None) -> dict | None:
    if get_active_arc() or recent_completed_within_hours(ARC_RESET_HOURS):
        return None

    catalog = load_catalog()
    arcs = [arc for arc in catalog.get("arcs", []) if isinstance(arc, dict)]
    if arc_id:
        chosen = next((arc for arc in arcs if arc.get("arcId") == arc_id), None)
    else:
        index = _read_json(INDEX_FILE, {"completed": []})
        completed = index.get("completed", []) if isinstance(index, dict) else []
        last_id = completed[-1].get("arcId") if completed and isinstance(completed[-1], dict) else None
        chosen = pick_random_arc([last_id] if last_id else None)
    if not chosen or not chosen.get("arcId"):
        return None

    now = int(time.time())
    state = {
        "schemaVersion": 2,
        "arcId": chosen["arcId"],
        "arcName": chosen.get("arcName", chosen["arcId"]),
        "summary": chosen.get("summary", ""),
        "arcStartedTs": now,
        "currentBeatIdx": 0,
        "beats": chosen.get("beats", []),
        "beatHistory": [],
        "lastBeatTs": now,
        "playersOnline": [],
        "playersSeen": [],
        "lastPlayerLeftTs": None,
        "narrations": [],
        "playerInteractions": [],
    }
    _write_json(ACTIVE_FILE, state)
    return state


def _remember_player(arc: dict, name: str) -> None:
    if not name:
        return
    seen = arc.setdefault("playersSeen", [])
    if name not in seen:
        seen.append(name)


def record_player_join(name: str) -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    _remember_player(arc, name)
    online = arc.setdefault("playersOnline", [])
    if name not in online:
        online.append(name)
    if online:
        arc["lastPlayerLeftTs"] = None
    _write_json(ACTIVE_FILE, arc)
    return arc


def record_player_leave(name: str) -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    _remember_player(arc, name)
    online = arc.setdefault("playersOnline", [])
    if name in online:
        online.remove(name)
    if not online:
        arc["lastPlayerLeftTs"] = int(time.time())
    _write_json(ACTIVE_FILE, arc)
    return arc


_PLAYER_LIST_LINE = re.compile(
    r"Players\s+connected\s+\((\d+)\)\s*:?\s*((?:\n?[A-Za-z0-9_\- ,]{0,128})*)",
    re.IGNORECASE,
)


def sync_players_online_from_text(text: str) -> dict | None:
    """Update active-arc roster from an authoritative `players` response."""
    if not text:
        return None
    arc = get_active_arc()
    if not arc:
        return None
    match = _PLAYER_LIST_LINE.search(text)
    if not match:
        return None

    expected_count = int(match.group(1))
    raw_names = match.group(2) or ""
    names = [name.strip() for name in re.split(r"[,\n]", raw_names) if name.strip()]
    # If the bridge reports a count but omits/truncates names, do not fabricate
    # identities. We can still reliably process the explicit zero-player case.
    if expected_count > 0 and not names:
        return {"joined": [], "left": [], "online": arc.get("playersOnline", []), "count": expected_count}

    prior = set(arc.get("playersOnline") or [])
    current = set(names)
    for name in current:
        _remember_player(arc, name)

    joined = sorted(current - prior)
    left = sorted(prior - current)
    arc["playersOnline"] = sorted(current)
    if current:
        arc["lastPlayerLeftTs"] = None
    elif prior or expected_count == 0:
        arc["lastPlayerLeftTs"] = int(time.time())
    _write_json(ACTIVE_FILE, arc)
    return {"joined": joined, "left": left, "online": arc["playersOnline"], "count": expected_count}


def record_player_interaction(name: str, content: str, simon_reply_summary: str = "") -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    _remember_player(arc, name)
    interactions = arc.setdefault("playerInteractions", [])
    interactions.append(
        {
            "ts": int(time.time()),
            "player": name,
            "content": str(content)[:300],
            "simon_reply_summary": str(simon_reply_summary)[:200],
        }
    )
    arc["playerInteractions"] = interactions[-MAX_INTERACTIONS:]
    _write_json(ACTIVE_FILE, arc)
    return arc


def active_arc_brief_for_player(name: str) -> str:
    """Return only already-revealed context for a player-facing LLM prompt."""
    arc = get_active_arc()
    if not arc:
        return ""

    narrations = [str(value)[:220] for value in (arc.get("narrations") or [])[-3:] if value]
    revealed = " | ".join(narrations) if narrations else "No arc broadcast has fired yet."
    interactions = [
        entry
        for entry in (arc.get("playerInteractions") or [])
        if isinstance(entry, dict) and entry.get("player") == name
    ]
    hint = ""
    if interactions:
        hint = f" Your last transmission in this situation was: '{str(interactions[-1].get('content', ''))[:100]}'."
    return (
        f"Active situation: {arc.get('arcName', arc.get('arcId', 'unknown'))}. "
        f"Already revealed over the radio: {revealed}.{hint}"
    )


def is_beat_ready(now: int | None = None) -> bool:
    arc = get_active_arc()
    if not arc:
        return False
    beats = arc.get("beats") or []
    try:
        index = int(arc.get("currentBeatIdx", 0))
    except (TypeError, ValueError):
        return False
    if index < 0 or index >= len(beats):
        return False
    beat = beats[index]
    try:
        gap_seconds = max(0, int(beat.get("gapMin", 0)) * 60)
        last_beat = int(arc.get("lastBeatTs", 0) or 0)
    except (AttributeError, TypeError, ValueError):
        return False
    current_time = int(time.time()) if now is None else int(now)
    return (current_time - last_beat) >= gap_seconds


def advance_beat() -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    beats = arc.get("beats") or []
    try:
        index = int(arc.get("currentBeatIdx", 0))
    except (TypeError, ValueError):
        return None
    if index >= len(beats):
        finalize_arc("completed")
        return None
    if not is_beat_ready():
        return None
    beat = beats[index]
    return {
        "arcId": arc.get("arcId"),
        "arcName": arc.get("arcName", arc.get("arcId")),
        "beatIdx": index,
        "narration": beat.get("narration", ""),
        "mutation": beat.get("mutation"),
        "totalBeats": len(beats),
    }


def mark_beat_fired(payload: dict, simon_narration: str = "") -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    # A beat that promised a real mutation may not advance when the caller
    # explicitly reports that mutation as unconfirmed/failed.
    if payload.get("mutation") and payload.get("mutation_executed") is not True:
        return None
    now = int(time.time())
    actual = simon_narration or payload.get("narration", "")
    history = arc.setdefault("beatHistory", [])
    history.append(
        {
            "ts": now,
            "beatIdx": payload.get("beatIdx"),
            "narration_planned": payload.get("narration", ""),
            "narration_actual": str(actual)[:600],
            "mutation_executed": bool(payload.get("mutation_executed")),
            "mutation": payload.get("mutation"),
        }
    )
    narrations = arc.setdefault("narrations", [])
    narrations.append(str(actual))
    arc["narrations"] = narrations[-MAX_NARRATIONS:]
    arc["currentBeatIdx"] = int(arc.get("currentBeatIdx", 0)) + 1
    arc["lastBeatTs"] = now
    for player in arc.get("playersOnline") or []:
        _remember_player(arc, player)
    _write_json(ACTIVE_FILE, arc)

    if arc["currentBeatIdx"] >= len(arc.get("beats") or []):
        finalize_arc("completed")
    return arc


def cleanup_stale_arc() -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    if arc.get("playersOnline"):
        return None
    last_left = arc.get("lastPlayerLeftTs")
    if not last_left:
        return None
    if int(time.time()) - int(last_left) >= STALE_PLAYER_MINUTES * 60:
        return finalize_arc("abandoned_no_players_30m")
    return None


def finalize_arc(reason: str = "completed") -> dict | None:
    arc = get_active_arc()
    if not arc:
        return None
    now = int(time.time())
    beats = arc.get("beats") or []
    interacted = {
        entry.get("player")
        for entry in (arc.get("playerInteractions") or [])
        if isinstance(entry, dict) and entry.get("player")
    }
    involved = sorted(set(arc.get("playersSeen") or []) | interacted)
    summary = {
        "arcId": arc.get("arcId"),
        "arcName": arc.get("arcName"),
        "summary": arc.get("summary", ""),
        "ts": now,
        "tsStart": arc.get("arcStartedTs", now),
        "durationMin": (now - int(arc.get("arcStartedTs", now))) // 60,
        "beatsFired": len(arc.get("beatHistory") or []),
        "totalBeats": len(beats),
        "playersInvolved": involved,
        "narrations": (arc.get("narrations") or [])[-8:],
        "reason": reason,
    }

    index = _read_json(INDEX_FILE, {"completed": [], "schemaVersion": 2})
    if not isinstance(index, dict):
        index = {"completed": [], "schemaVersion": 2}
    completed = index.setdefault("completed", [])
    completed.append(
        {
            "arcId": summary["arcId"],
            "arcName": summary["arcName"],
            "ts": summary["ts"],
            "durationMin": summary["durationMin"],
            "reason": summary["reason"],
            "summary": arc.get("summary", ""),
            "playersInvolved": involved,
        }
    )
    index["completed"] = completed[-50:]
    index["schemaVersion"] = max(2, int(index.get("schemaVersion", 1) or 1))
    _write_json(INDEX_FILE, index)

    archive_dir = ARCS_DIR / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now))
    _write_json(
        archive_dir / f"{arc.get('arcId', 'arc')}-{stamp}.json",
        {"finalized_reason": reason, "arc_state": arc, "summary": summary},
    )

    try:
        from simon_global_memory import log_event
        log_event(
            {
                "ts": now,
                "type": f"arc_{reason}",
                "arcId": summary["arcId"],
                "arcName": summary["arcName"],
                "durationMin": summary["durationMin"],
                "playersInvolved": involved,
                "summary": arc.get("summary", ""),
                "last_narration": ((arc.get("narrations") or [""])[-1])[:280],
            }
        )
    except Exception:
        pass

    try:
        from simon_player_memory import append_arc_recap
        for player in involved:
            try:
                append_arc_recap(
                    player,
                    arc.get("arcId", "?"),
                    f"survived '{arc.get('arcName', arc.get('arcId'))}' ({reason}) — {arc.get('summary', '')[:120]}",
                )
            except Exception:
                continue
    except Exception:
        pass

    try:
        ACTIVE_FILE.unlink()
    except FileNotFoundError:
        pass
    return summary


def reset_all_arc_memory() -> int:
    removed = 0
    if ACTIVE_FILE.exists():
        ACTIVE_FILE.unlink()
        removed += 1
    if INDEX_FILE.exists():
        _write_json(INDEX_FILE, {"completed": [], "schemaVersion": 2})
        removed += 1
    return removed


if __name__ == "__main__":
    print(json.dumps(load_catalog(), indent=2)[:1200])
