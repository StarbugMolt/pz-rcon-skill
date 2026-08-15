#!/usr/bin/env python3
"""Deterministic delivery guard for SIMON.

Small item gifts remain owned by simon_supply.py. This module owns the extra
safety required for large physical deliveries such as vehicles:

- the target survivor must be known present to the current listener session;
- the survivor must have explicitly said they are outside and ready recently;
- the vehicle script must exist in vanilla or an enabled-mod catalogue;
- a confirmed helicopter event is triggered before the vehicle spawn;
- pz-console.sh accepts the vehicle spawn only with a short-lived one-time token
  issued by this helper.

No LLM participates in these checks. Failure is fail-closed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = SKILL_DIR / "state"
PRESENCE_FILE = STATE_DIR / "presence.json"
READINESS_FILE = STATE_DIR / "delivery-readiness.json"
TOKEN_FILE = STATE_DIR / "vehicle-drop-token.json"
CONSOLE_SCRIPT = Path(__file__).resolve().parent / "pz-console.sh"
CATALOG_DIR = SKILL_DIR / "references" / "catalogs"
VANILLA_VEHICLES = CATALOG_DIR / "vanilla" / "vehicles-full.md"
MOD_CATALOG_DIR = CATALOG_DIR / "mods"
ENV_FILE = Path(os.path.expanduser(os.environ.get("ENV_FILE", "~/.env")))

DEFAULT_OUTSIDE_READY_SECONDS = 5 * 60
MAX_OUTSIDE_READY_SECONDS = 15 * 60
TOKEN_TTL_SECONDS = 30

UNCERTAIN_MARKERS = (
    "example", "placeholder", "syntax only", "guess", "guessed", "inferred",
    "unverified", "needs live verification", "if it exists", "plausible",
    "deprecated",
)

_OUTSIDE_PATTERNS = (
    re.compile(r"\b(?:i\s*['’]?m|i\s+am|we\s*['’]?re|we\s+are)\s+(?:already\s+|now\s+)?outside\b", re.I),
    re.compile(r"\boutside\s+(?:and\s+)?ready\b", re.I),
    re.compile(r"\bready\s+(?:and\s+)?outside\b", re.I),
)
_DELIVERY_CONTEXT_RE = re.compile(
    r"\b(?:simon|drop|delivery|deliver|car|vehicle|truck|van|helicopter|chopper|bird|bring|send|sling)\b",
    re.I,
)


def _load_env(path: Path) -> dict[str, str]:
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


ENV = _load_env(ENV_FILE)


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _atomic_write_json(path: Path, data: Any) -> None:
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


def _key(player: str) -> str:
    return str(player or "").strip().casefold()


def _clean_player(player: str) -> str:
    value = str(player or "").strip()
    if not value or len(value) > 64 or any(ord(ch) < 32 for ch in value):
        return ""
    return value


def reset_presence() -> None:
    """Fail closed after listener restart: nobody is present until observed."""
    _atomic_write_json(
        PRESENCE_FILE,
        {"schemaVersion": 1, "listenerStartedTs": int(time.time()), "online": {}},
    )


def mark_present(player: str, source: str = "observed") -> bool:
    player = _clean_player(player)
    if not player:
        return False
    data = _read_json(PRESENCE_FILE, {"schemaVersion": 1, "online": {}})
    if not isinstance(data, dict):
        data = {"schemaVersion": 1, "online": {}}
    online = data.setdefault("online", {})
    if not isinstance(online, dict):
        online = {}
        data["online"] = online
    online[_key(player)] = {
        "name": player,
        "seenTs": int(time.time()),
        "source": str(source)[:40],
    }
    data["schemaVersion"] = 1
    _atomic_write_json(PRESENCE_FILE, data)
    return True


def mark_absent(player: str) -> bool:
    player = _clean_player(player)
    if not player:
        return False
    data = _read_json(PRESENCE_FILE, {"schemaVersion": 1, "online": {}})
    if not isinstance(data, dict):
        return False
    online = data.get("online")
    if not isinstance(online, dict):
        return False
    existed = online.pop(_key(player), None) is not None
    _atomic_write_json(PRESENCE_FILE, data)
    return existed


def is_present(player: str) -> bool:
    data = _read_json(PRESENCE_FILE, {})
    online = data.get("online") if isinstance(data, dict) else None
    return isinstance(online, dict) and _key(player) in online


def _outside_ready_seconds() -> int:
    raw = os.environ.get("SIMON_OUTSIDE_READY_SECONDS") or ENV.get(
        "SIMON_OUTSIDE_READY_SECONDS", str(DEFAULT_OUTSIDE_READY_SECONDS)
    )
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = DEFAULT_OUTSIDE_READY_SECONDS
    return min(MAX_OUTSIDE_READY_SECONDS, max(60, value))


def mark_outside_ready_from_chat(player: str, content: str, now: int | None = None) -> bool:
    """Record readiness only from an explicit survivor statement.

    Ordinary mentions of being outdoors are insufficient. The transmission must
    both say the survivor is outside/ready and contain delivery context (or call
    SIMON by name). This is a mechanical safety gate, not semantic LLM inference.
    """
    player = _clean_player(player)
    text = str(content or "").strip()
    if not player or not text:
        return False
    if not any(pattern.search(text) for pattern in _OUTSIDE_PATTERNS):
        return False
    if not _DELIVERY_CONTEXT_RE.search(text):
        return False

    ts = int(time.time()) if now is None else int(now)
    data = _read_json(READINESS_FILE, {"schemaVersion": 1, "players": {}})
    if not isinstance(data, dict):
        data = {"schemaVersion": 1, "players": {}}
    players = data.setdefault("players", {})
    if not isinstance(players, dict):
        players = {}
        data["players"] = players
    players[_key(player)] = {
        "name": player,
        "readyTs": ts,
        "expiresTs": ts + _outside_ready_seconds(),
        "evidence": text[:180],
    }
    _atomic_write_json(READINESS_FILE, data)
    return True


def outside_ready(player: str, now: int | None = None) -> bool:
    current = int(time.time()) if now is None else int(now)
    data = _read_json(READINESS_FILE, {})
    players = data.get("players") if isinstance(data, dict) else None
    entry = players.get(_key(player)) if isinstance(players, dict) else None
    if not isinstance(entry, dict):
        return False
    try:
        expires = int(entry.get("expiresTs", 0) or 0)
    except (TypeError, ValueError):
        return False
    return current <= expires and is_present(player)


def ready_players(now: int | None = None) -> list[str]:
    current = int(time.time()) if now is None else int(now)
    data = _read_json(READINESS_FILE, {})
    players = data.get("players") if isinstance(data, dict) else None
    if not isinstance(players, dict):
        return []
    result: list[str] = []
    for entry in players.values():
        if not isinstance(entry, dict):
            continue
        name = _clean_player(entry.get("name", ""))
        try:
            expires = int(entry.get("expiresTs", 0) or 0)
        except (TypeError, ValueError):
            continue
        if name and current <= expires and is_present(name):
            result.append(name)
    return sorted(set(result), key=str.casefold)


def _clear_readiness(player: str) -> None:
    data = _read_json(READINESS_FILE, {})
    players = data.get("players") if isinstance(data, dict) else None
    if isinstance(players, dict) and players.pop(_key(player), None) is not None:
        _atomic_write_json(READINESS_FILE, data)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _enabled_mods() -> list[str]:
    raw = os.environ.get("PZ_ENABLED_MODS") or ENV.get("PZ_ENABLED_MODS", "")
    result: list[str] = []
    seen: set[str] = set()
    for part in re.split(r"[;,]", raw):
        mod = part.strip().lstrip("\\").strip()
        key = _normalize(mod)
        if mod and key not in seen:
            result.append(mod)
            seen.add(key)
    return result


def _active_mod_catalogs() -> list[Path]:
    available: dict[str, Path] = {}
    if MOD_CATALOG_DIR.exists():
        for path in MOD_CATALOG_DIR.glob("mod-*-items.md"):
            stem = path.stem
            if stem.startswith("mod-"):
                stem = stem[4:]
            if stem.endswith("-items"):
                stem = stem[:-6]
            available[_normalize(stem)] = path
    return [available[_normalize(mod)] for mod in _enabled_mods() if _normalize(mod) in available]


def _vehicle_entries() -> dict[str, str]:
    entries: dict[str, str] = {}

    if VANILLA_VEHICLES.exists():
        try:
            text = VANILLA_VEHICLES.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        for value in re.findall(r"\bBase\.[A-Za-z0-9_.-]+\b", text):
            entries.setdefault(value.casefold(), value)

    for path in _active_mod_catalogs():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        in_vehicle_section = False
        for raw in lines:
            line = raw.strip()
            if line.startswith("##"):
                heading = line.lstrip("#").strip().casefold()
                in_vehicle_section = "vehicle script" in heading
                continue
            if not in_vehicle_section:
                continue
            lower = line.casefold()
            if any(marker in lower for marker in UNCERTAIN_MARKERS):
                continue
            if not (line.startswith("|") or line.startswith("-")):
                continue
            for value in re.findall(r"`([^`]+)`", line):
                candidate = value.strip()
                if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{1,127}", candidate):
                    continue
                if candidate.casefold() in {"addvehicle", "script", "player", "vehiclescript"}:
                    continue
                entries.setdefault(candidate.casefold(), candidate)
    return entries


def resolve_vehicle_script(vehicle_script: str) -> str | None:
    value = str(vehicle_script or "").strip()
    if not value or len(value) > 128:
        return None
    return _vehicle_entries().get(value.casefold())


def _issue_vehicle_token(vehicle_script: str, player: str) -> str:
    token = secrets.token_urlsafe(24)
    now = int(time.time())
    _atomic_write_json(
        TOKEN_FILE,
        {
            "schemaVersion": 1,
            "token": token,
            "vehicle": vehicle_script,
            "player": player,
            "issuedTs": now,
            "expiresTs": now + TOKEN_TTL_SECONDS,
        },
    )
    return token


def consume_vehicle_token(token: str, vehicle_script: str, player: str, now: int | None = None) -> bool:
    """Consume the one-time authorization used by pz-console.sh vehicle."""
    current = int(time.time()) if now is None else int(now)
    data = _read_json(TOKEN_FILE, None)
    if not isinstance(data, dict):
        return False
    try:
        valid = (
            secrets.compare_digest(str(data.get("token", "")), str(token or ""))
            and str(data.get("vehicle", "")).casefold() == str(vehicle_script or "").casefold()
            and _key(data.get("player", "")) == _key(player)
            and current <= int(data.get("expiresTs", 0) or 0)
        )
    except (TypeError, ValueError):
        valid = False
    # One attempt consumes the token, valid or not. This avoids replay/racing.
    try:
        TOKEN_FILE.unlink()
    except FileNotFoundError:
        pass
    return bool(valid)


def _run_console(args: list[str], timeout: int = 35) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            [str(CONSOLE_SCRIPT), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def vehicle_drop(vehicle_script: str, player: str) -> dict[str, Any]:
    player = _clean_player(player)
    canonical = resolve_vehicle_script(vehicle_script)
    if not player:
        return {"ok": False, "reason": "invalid-player"}
    if not canonical:
        return {"ok": False, "reason": "unverified-vehicle"}
    if not is_present(player):
        return {"ok": False, "reason": "target-not-present", "player": player}
    if not outside_ready(player):
        return {"ok": False, "reason": "outside-not-confirmed", "player": player}

    # Presence is exact-player local evidence; the online gate independently
    # proves the PZ server currently has at least one connected survivor.
    try:
        from simon_online_gate import check_players_online
        presence = check_players_online(timeout_seconds=8)
    except Exception:
        return {"ok": False, "reason": "online-gate-failed", "player": player}
    if not presence.get("online") or int(presence.get("count", 0) or 0) <= 0:
        return {"ok": False, "reason": "no-authoritative-online-player", "player": player}

    chopper = _run_console(["chopper"])
    if chopper is None or chopper.returncode != 0:
        return {"ok": False, "reason": "chopper-unconfirmed", "player": player}

    token = _issue_vehicle_token(canonical, player)
    # A short pause makes the helicopter cue precede the physical spawn while
    # keeping the helper synchronous and deterministic.
    time.sleep(1)
    spawned = _run_console(["vehicle", canonical, player, token])
    if spawned is None or spawned.returncode != 0:
        return {"ok": False, "reason": "vehicle-unconfirmed", "player": player}

    _clear_readiness(player)
    return {
        "ok": True,
        "reason": "confirmed",
        "player": player,
        "vehicle": canonical,
        "chopper_confirmed": True,
        "vehicle_confirmed": True,
        "narration_cue": (
            "A helicopter/utility bird made the large delivery by sling load. "
            "Vary the wording naturally; never mention spawning, commands or server mechanics."
        ),
    }


def status(player: str) -> dict[str, Any]:
    return {
        "player": _clean_player(player),
        "present": is_present(player),
        "outside_ready": outside_ready(player),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Guarded SIMON large-delivery helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_drop = sub.add_parser("vehicle-drop")
    p_drop.add_argument("vehicle")
    p_drop.add_argument("player")

    p_consume = sub.add_parser("consume-token")
    p_consume.add_argument("token")
    p_consume.add_argument("vehicle")
    p_consume.add_argument("player")

    p_status = sub.add_parser("status")
    p_status.add_argument("player")

    sub.add_parser("ready-players")
    sub.add_parser("reset-presence")

    args = parser.parse_args()
    if args.command == "vehicle-drop":
        result = vehicle_drop(args.vehicle, args.player)
        print(json.dumps(result, separators=(",", ":")))
        return 0 if result.get("ok") else 3
    if args.command == "consume-token":
        ok = consume_vehicle_token(args.token, args.vehicle, args.player)
        return 0 if ok else 3
    if args.command == "status":
        print(json.dumps(status(args.player), separators=(",", ":")))
        return 0
    if args.command == "ready-players":
        print(json.dumps({"players": ready_players()}, separators=(",", ":")))
        return 0
    if args.command == "reset-presence":
        reset_presence()
        return 0
    return 64


if __name__ == "__main__":
    sys.exit(main())
