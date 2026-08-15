#!/usr/bin/env python3
"""Deterministic supply helper for SIMON.

Normal radio conversation is never throttled here. Only actual item grants have
cooldown/rate controls. Production gifts are modest and occasional. Test mode
makes explicit supply requests generous while still resolving only verified
catalogue IDs.
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONSOLE_SCRIPT = Path(__file__).resolve().parent / "pz-console.sh"
CATALOG_DIR = SKILL_DIR / "references" / "catalogs"
VANILLA_CATALOG = CATALOG_DIR / "vanilla" / "items-full.md"
MOD_CATALOG_DIR = CATALOG_DIR / "mods"

DEFAULT_GIFT_COOLDOWN_SECONDS = 30 * 60
DEFAULT_HELP_GIFT_CHANCE = 0.20
MAX_GIFT_COUNT = 5
ENV_FILE = Path(os.path.expanduser(os.environ.get("ENV_FILE", "~/.env")))

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

# Curated production help only: basic survival aid, not high-end loot.
PRODUCTION_GIFTS = {
    "water": ("Base.WaterBottleFull", 1),
    "food": ("Base.CannedBeans", 2),
    "medical": ("Base.Bandage", 2),
    "pain": ("Base.Painkillers", 1),
    "light": ("Base.HandTorch", 1),
    "fire": ("Base.Matches", 1),
}

# Internal fiction cues only. They explain an already-confirmed small delivery
# without exposing inventory/server mechanics. The model is told to vary them.
SMALL_DELIVERY_CUES = (
    "A scavenged prototype military unmanned aircraft/drone made a brief low pass and dropped a wrapped parcel nearby.",
    "SIMON routed the parcel through an old civil-defense cache and gives only enough directions to find the fresh drop.",
    "A battered radio-controlled utility aircraft rebuilt from military surplus carried the parcel in low and ugly.",
    "One of SIMON's still-breathing radio contacts moved a small parcel close enough for the survivor to collect.",
    "Skip the logistics this time: simply establish that SIMON managed to get a small package close to the survivor.",
)

NEED_RULES = (
    ("water", ("water", "drink", "thirst", "dehydrat")),
    ("food", ("food", "hungry", "starv", "eat")),
    ("medical", ("bleed", "bandage", "wound", "injur", "first aid")),
    ("pain", ("pain", "painkiller")),
    ("light", ("flashlight", "torch", "dark", "light")),
    ("fire", ("matches", "lighter", "fire", "candle")),
)

EXPLICIT_REQUEST_MARKERS = (
    "give me", "send me", "drop me", "can i have", "could i have",
    "i need", "could use", "got any", "have any", "spare",
)

ITEM_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*\.[A-Za-z0-9_][A-Za-z0-9_.-]*)\b")
WORD_RE = re.compile(r"[a-z0-9]+")
UNCERTAIN_MARKERS = (
    "example", "placeholder", "syntax only", "guess", "guessed", "inferred",
    "unverified", "needs live verification", "if it exists", "plausible namespace",
    "deprecated",
)

_last_gift_ts: dict[str, int] = {}
_catalog_cache: dict[str, tuple[str, str]] | None = None


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name) or ENV.get(name)
    if raw is None:
        return default
    return raw.strip().casefold() in {"1", "true", "yes", "on", "y"}


def test_mode_enabled() -> bool:
    return _bool_env("SIMON_TEST_MODE", False)


def explicit_supply_request(text: str) -> bool:
    lower = str(text or "").casefold()
    return any(marker in lower for marker in EXPLICIT_REQUEST_MARKERS)


def classify_need(text: str) -> str | None:
    lower = str(text or "").casefold()
    for need, markers in NEED_RULES:
        if any(marker in lower for marker in markers):
            return need
    return None


def _gift_cooldown_seconds() -> int:
    if test_mode_enabled():
        return 0
    try:
        return max(0, int(os.environ.get("SIMON_GIFT_COOLDOWN_SECONDS") or ENV.get("SIMON_GIFT_COOLDOWN_SECONDS", str(DEFAULT_GIFT_COOLDOWN_SECONDS))))
    except ValueError:
        return DEFAULT_GIFT_COOLDOWN_SECONDS


def _help_gift_chance() -> float:
    if test_mode_enabled():
        return 1.0
    try:
        value = float(os.environ.get("SIMON_HELP_GIFT_CHANCE") or ENV.get("SIMON_HELP_GIFT_CHANCE", str(DEFAULT_HELP_GIFT_CHANCE)))
    except ValueError:
        value = DEFAULT_HELP_GIFT_CHANCE
    return min(1.0, max(0.0, value))


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


def _active_catalogs() -> list[Path]:
    result = [VANILLA_CATALOG] if VANILLA_CATALOG.exists() else []
    available: dict[str, Path] = {}
    if MOD_CATALOG_DIR.exists():
        for path in MOD_CATALOG_DIR.glob("mod-*-items.md"):
            stem = path.stem
            if stem.startswith("mod-"):
                stem = stem[4:]
            if stem.endswith("-items"):
                stem = stem[:-6]
            available[_normalize(stem)] = path
    for mod in _enabled_mods():
        path = available.get(_normalize(mod))
        if path:
            result.append(path)
    return result


def _catalog_entries() -> dict[str, tuple[str, str]]:
    global _catalog_cache
    if _catalog_cache is not None:
        return _catalog_cache

    entries: dict[str, tuple[str, str]] = {}
    for path in _active_catalogs():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        section = ""
        for raw in lines:
            line = raw.strip()
            if line.startswith("#"):
                section = line.lstrip("#").strip()
                continue
            lower = line.casefold()
            if any(marker in lower for marker in UNCERTAIN_MARKERS):
                continue
            if not (line.startswith("-") or line.startswith("|")):
                continue
            for match in ITEM_RE.finditer(line):
                item_id = match.group(1)
                if item_id.casefold() in {"module.item", "namespace.item", "example.item"}:
                    continue
                entries.setdefault(item_id.casefold(), (item_id, section))
    _catalog_cache = entries
    return entries


def resolve_test_item(text: str) -> str | None:
    """Resolve one explicit test request to a verified active-catalogue ID."""
    entries = _catalog_entries()
    lower = str(text or "").casefold()

    for item_id, _section in entries.values():
        if item_id.casefold() in lower:
            return item_id

    need = classify_need(text)
    if need in PRODUCTION_GIFTS:
        return PRODUCTION_GIFTS[need][0]

    words = set(WORD_RE.findall(lower)) - {
        "give", "me", "send", "drop", "can", "i", "have", "could", "need",
        "a", "an", "the", "some", "please", "spare", "got", "any", "simon",
    }
    if not words:
        return None

    ranked: list[tuple[int, int, str]] = []
    for item_id, section in entries.values():
        short = item_id.split(".", 1)[-1]
        split_short = re.sub(r"([a-z])([A-Z])", r"\1 \2", short)
        item_words = set(WORD_RE.findall(split_short.casefold()))
        direct = len(words & item_words)
        contextual = len(words & set(WORD_RE.findall(section.casefold())))
        if direct:
            ranked.append((direct * 10 + contextual, -len(item_words), item_id))
    ranked.sort(reverse=True)
    return ranked[0][2] if ranked else None


def _gift_allowed(player_key: str, now: int) -> bool:
    cooldown = _gift_cooldown_seconds()
    return cooldown <= 0 or (now - _last_gift_ts.get(player_key, 0)) >= cooldown


def _roll_help(player_key: str, content: str, now: int) -> bool:
    chance = _help_gift_chance()
    if chance <= 0:
        return False
    if chance >= 1:
        return True
    seed = f"{player_key}|{now // 60}|{content}".encode("utf-8", errors="ignore")
    value = int.from_bytes(hashlib.sha256(seed).digest()[:8], "big") / 2**64
    return value < chance


def choose_gift(player_key: str, content: str, trigger: str, now: int | None = None) -> tuple[str, int] | None:
    """Choose one gift deterministically. This function never executes it."""
    now = int(time.time()) if now is None else int(now)
    if not _gift_allowed(player_key, now):
        return None

    if test_mode_enabled() and explicit_supply_request(content):
        item_id = resolve_test_item(content)
        if not item_id:
            return None
        need = classify_need(content)
        if need and PRODUCTION_GIFTS.get(need, (None, 1))[0] == item_id:
            return PRODUCTION_GIFTS[need]
        return item_id, 1

    if trigger != "help":
        return None
    need = classify_need(content)
    if not need or need not in PRODUCTION_GIFTS:
        return None
    if not _roll_help(player_key, content, now):
        return None
    return PRODUCTION_GIFTS[need]


def execute_gift(player_name: str, player_key: str, gift: tuple[str, int] | None) -> tuple[str, int] | None:
    if not gift or not player_name:
        return None
    item_id, count = gift
    canonical = _catalog_entries().get(item_id.casefold())
    if not canonical:
        return None
    item_id = canonical[0]
    count = max(1, min(int(count), MAX_GIFT_COUNT))
    try:
        result = subprocess.run(
            [str(CONSOLE_SCRIPT), "give", player_name, item_id, str(count)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    _last_gift_ts[player_key] = int(time.time())
    return item_id, count


def _delivery_cue(item_id: str, now: int | None = None) -> str:
    current = int(time.time()) if now is None else int(now)
    seed = f"{item_id.casefold()}|{current // 1800}".encode("utf-8", errors="ignore")
    index = int.from_bytes(hashlib.sha256(seed).digest()[:4], "big") % len(SMALL_DELIVERY_CUES)
    return SMALL_DELIVERY_CUES[index]


def describe_gift(gift: tuple[str, int] | None) -> str:
    if not gift:
        return "No supply drop was confirmed. Do not claim one happened."
    item_id, count = gift
    short = re.sub(r"([a-z])([A-Z])", r"\1 \2", item_id.split(".", 1)[-1]).replace("_", " ")
    cue = _delivery_cue(item_id)
    generosity = " The confirmed amount is permitted; do not object to it or explain why." if test_mode_enabled() else ""
    return (
        f"TRUSTED CONFIRMED SMALL DELIVERY: {count} x {short}. "
        f"DELIVERY-FICTION CUE: {cue} Use a natural variation and do not repeat internal labels, "
        f"inventory/spawn/server mechanics, or modern consumer-drone technology.{generosity}"
    )
