#!/usr/bin/env python3
"""Reset SIMON's remembered Project Zomboid world state.

This does NOT wipe the Project Zomboid save/map. It archives SIMON's memory
first, then starts a new SIMON era. Any required archive failure aborts before
destructive deletion.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = SKILL_DIR / "state"
MEMORY_DIR = STATE_DIR / "memory"
PLAYERS_DIR = MEMORY_DIR / "players"
ARCS_DIR = MEMORY_DIR / "arcs"
GLOBAL_DIR = MEMORY_DIR / "global"
ARCHIVE_BASE = MEMORY_DIR / "archive"
RESET_MARKER_FILE = GLOBAL_DIR / "reset-marker.json"

LEGACY_STATE_FILES = (
    STATE_DIR / "player-registry.json",
    STATE_DIR / "narrative-state.json",
    STATE_DIR / "greeting-queue.json",
    STATE_DIR / "player-delta.json",
    STATE_DIR / "discord-message-state.json",
)


def _read_json(path: Path, default):
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _atomic_write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def _default_player_index() -> dict:
    return {"players": {}, "schemaVersion": 1}


def _default_arc_index() -> dict:
    return {"completed": [], "schemaVersion": 1}


def _default_history() -> dict:
    return {"events": [], "schemaVersion": 1}


def _default_lore(now: int, total_resets: int) -> dict:
    return {
        "_about": "Synthesized SIMON server lore for the current era.",
        "narrative": (
            "The bunker radio has been broadcasting into static for an eternity. "
            "Nothing has come back. Simon, out."
        ),
        "facts": {
            "eraStart": now,
            "totalArcsCompleted": 0,
            "totalServerResets": total_resets,
            "lastUpdatedTs": now,
        },
        "schemaVersion": 1,
    }


def _new_reset_marker(stamp: str, now: int, previous_total: int, reason: str) -> dict:
    return {
        "eraId": f"era-{stamp}",
        "eraStart": now,
        "currentEraResets": 0,
        "totalResetsEver": max(0, int(previous_total)) + 1,
        "lastResetTs": now,
        "lastResetReason": str(reason or "world_reset")[:240],
        "schemaVersion": 1,
    }


def _copy_required(src: Path, dst: Path) -> tuple[int, int]:
    """Copy one existing source and return (file_count, byte_count)."""
    if not src.exists():
        return 0, 0
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
        files = [path for path in dst.rglob("*") if path.is_file()]
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files = [dst]
    return len(files), sum(path.stat().st_size for path in files)


def archive_live_state(era_id: str, stamp: str) -> dict:
    """Archive all live SIMON memory/caches. Raises on any copy failure."""
    target = ARCHIVE_BASE / era_id / stamp
    target.mkdir(parents=True, exist_ok=True)
    summary = {"archive": str(target), "files_moved": 0, "bytes_moved": 0}

    required_sources = (
        (PLAYERS_DIR, target / "players"),
        (ARCS_DIR, target / "arcs"),
        (GLOBAL_DIR, target / "global"),
    )
    for src, dst in required_sources:
        count, size = _copy_required(src, dst)
        summary["files_moved"] += count
        summary["bytes_moved"] += size

    legacy_target = target / "listener-state"
    for src in LEGACY_STATE_FILES:
        if not src.exists():
            continue
        count, size = _copy_required(src, legacy_target / src.name)
        summary["files_moved"] += count
        summary["bytes_moved"] += size

    return summary


def wipe_after_archive(stamp: str, now: int, previous_total: int, reason: str) -> None:
    """Destructive phase. Call only after archive_live_state succeeds."""
    if PLAYERS_DIR.exists():
        for path in PLAYERS_DIR.glob("*.json"):
            path.unlink()
    _atomic_write_json(PLAYERS_DIR / "index.json", _default_player_index())

    active = ARCS_DIR / "active.json"
    if active.exists():
        active.unlink()
    _atomic_write_json(ARCS_DIR / "index.json", _default_arc_index())
    arc_archive = ARCS_DIR / "archive"
    if arc_archive.exists():
        shutil.rmtree(arc_archive)

    total_resets = max(0, int(previous_total)) + 1
    _atomic_write_json(GLOBAL_DIR / "server-history.json", _default_history())
    _atomic_write_json(GLOBAL_DIR / "lore.json", _default_lore(now, total_resets))
    _atomic_write_json(
        RESET_MARKER_FILE,
        _new_reset_marker(stamp, now, previous_total, reason),
    )

    for path in LEGACY_STATE_FILES:
        if path.exists():
            path.unlink()


def archive_then_wipe(era_id: str, previous_total: int, reason: str) -> dict:
    stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    now = int(time.time())

    # Archive is intentionally outside the destructive try/continue pattern:
    # any exception stops the reset and preserves live state.
    summary = archive_live_state(era_id, stamp)
    wipe_after_archive(stamp, now, previous_total, reason)
    return summary


def maybe_announce(reason: str) -> bool:
    """Broadcast an optional one-line SIMON sign-off before the memory reset."""
    import subprocess

    env_path = Path(os.path.expanduser("~/.env"))
    if not env_path.exists():
        print("WARNING: .env missing; --announce skipped", file=sys.stderr)
        return False

    env: dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")

    channel_id = env.get("PZ_DISCORD_CHANNEL_ID")
    if not channel_id:
        print("WARNING: PZ_DISCORD_CHANNEL_ID missing; --announce skipped", file=sys.stderr)
        return False

    # The operator reason stays in operator logs/state. Never interpolate it
    # into player-facing radio where it could be technical or out of character.
    text = (
        "Static on the line. I'm cycling the old bunker set and the lights are going with it. "
        "If the frequency goes dead, keep it warm for me. Simon, out."
    )
    try:
        result = subprocess.run(
            [
                "openclaw", "message", "send",
                "--channel", "discord",
                "--target", f"channel:{channel_id}",
                "--message", text,
            ],
            check=False,
            timeout=15,
        )
        return result.returncode == 0
    except Exception as exc:
        print(f"WARNING: announce failed: {exc}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset SIMON's remembered world state.")
    parser.add_argument("--reason", default="world_reset", help="Reason stored in the new era marker.")
    parser.add_argument("--announce", action="store_true", help="Broadcast a SIMON sign-off before resetting memory.")
    parser.add_argument("--dry-run", action="store_true", help="Describe the reset without modifying state.")
    args = parser.parse_args()

    marker = _read_json(
        RESET_MARKER_FILE,
        {"eraId": "era-unknown", "eraStart": 0, "totalResetsEver": 0},
    )
    era_id = str(marker.get("eraId") or "era-unknown")
    previous_total = int(marker.get("totalResetsEver", 0) or 0)

    print(f"Current SIMON era: {era_id} (started {marker.get('eraStart', '?')})")
    print(f"Reason: {args.reason}")

    if args.dry_run:
        print("--dry-run: would archive SIMON memory/listener state, then start a new SIMON era.")
        return 0

    if args.announce:
        print(f"announce={'ok' if maybe_announce(args.reason) else 'skipped'}")

    try:
        summary = archive_then_wipe(era_id, previous_total, args.reason)
    except Exception as exc:
        print(f"ERROR: archive failed; reset aborted before destructive wipe: {exc}", file=sys.stderr)
        return 1

    print("SIMON memory reset complete.")
    print(f"  archive     : {summary['archive']}")
    print(f"  files saved : {summary['files_moved']}")
    print(f"  bytes saved : {summary['bytes_moved']}")
    print(f"  new reset # : {previous_total + 1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
