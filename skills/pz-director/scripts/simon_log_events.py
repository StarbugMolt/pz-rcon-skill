#!/usr/bin/env python3
"""Conservative Project Zomboid Build 42 DiscordLogChannel parser.

This module performs deterministic, non-LLM classification only. The primary
inputs are the compact lifecycle/death notifications that Project Zomboid sends
to DiscordLogChannel. Detailed on-disk user-log lines are accepted only as
fallbacks when they happen to be forwarded; coordinates are optional metadata
and are never required for an event to be recognized.

Supported event types:
- player_join
- player_leave
- player_death

Human-readable death announcements are not authoritative enough by themselves
in Build 42 because non-player entities have been observed triggering the same
announcement wording. Such events are marked ``requires_known_player=True`` so
the listener can accept them only when the victim matches a survivor already
known to SIMON.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

_COORD_RE = re.compile(r"\((-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\)")

# DiscordLogChannel compact forms are primary. Quoted detailed user-log forms
# remain fallback-compatible but must never be required for normal operation.
_JOIN_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r'^\[(?P<player>[^\]\r\n]{1,64})\]\s+connected\s+to\s+server\s*$', re.IGNORECASE),
        "discord_compact",
    ),
    (
        re.compile(r'"(?P<player>[^"\r\n]{1,64})"\s+fully\s+connected\b', re.IGNORECASE),
        "detailed_user_log",
    ),
)

_LEAVE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r'^\[(?P<player>[^\]\r\n]{1,64})\]\s+disconnected(?:\s+from\s+server)?\s*$', re.IGNORECASE),
        "discord_compact",
    ),
    (
        re.compile(r'"(?P<player>[^"\r\n]{1,64})"\s+disconnected\s+player\b', re.IGNORECASE),
        "detailed_user_log",
    ),
)

# Structured user-log death records are high-confidence when present. Normal
# Discord death announcements are only candidates and must be cross-checked
# against SIMON's known-survivor registry by the listener.
_STRUCTURED_DEATH_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r'\buser\s+(?P<player>[^\r\n]{1,64}?)\s+died\s+at\s+\((-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\)(?P<tail>.*)$',
            re.IGNORECASE,
        ),
        "detailed_user_log",
    ),
)

_ANNOUNCED_DEATH_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r'^(?P<player>[^\r\n]{1,64}?)\s+has\s+died[.!]?\s*$', re.IGNORECASE),
        "discord_announcement",
    ),
    (
        re.compile(
            r'^(?P<killer>[^\r\n]{1,64}?)\s+has\s+killed\s+(?P<player>[^\r\n]{1,64}?)[.!]?\s*$',
            re.IGNORECASE,
        ),
        "discord_announcement",
    ),
)


@dataclass(frozen=True)
class LogEvent:
    type: str
    player: str
    raw: str
    x: int | None = None
    y: int | None = None
    z: int | None = None
    details: str = ""
    source_form: str = "discord_compact"
    requires_known_player: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _coordinates(text: str) -> tuple[int | None, int | None, int | None]:
    match = _COORD_RE.search(text)
    if not match:
        return None, None, None
    return tuple(int(value) for value in match.groups())  # type: ignore[return-value]


def _clean_player(value: str) -> str:
    return str(value or "").strip().strip('"').strip()[:64]


def _event(
    event_type: str,
    match: re.Match[str],
    raw: str,
    source_form: str,
    *,
    requires_known_player: bool = False,
) -> LogEvent:
    player = _clean_player(match.group("player"))
    x, y, z = _coordinates(raw)
    details = ""
    if "tail" in match.re.groupindex:
        details = (match.groupdict().get("tail") or "").strip(" .:-")[:240]
    if "killer" in match.re.groupindex:
        killer = _clean_player(match.groupdict().get("killer") or "")
        if killer:
            details = f"announced killer: {killer}"[:240]
    return LogEvent(
        event_type,
        player,
        raw[:800],
        x,
        y,
        z,
        details,
        source_form,
        requires_known_player,
    )


def parse_log_event(content: str) -> LogEvent | None:
    text = str(content or "").strip()
    if not text:
        return None

    for pattern, source_form in _JOIN_PATTERNS:
        match = pattern.search(text)
        if match:
            return _event("player_join", match, text, source_form)

    for pattern, source_form in _LEAVE_PATTERNS:
        match = pattern.search(text)
        if match:
            return _event("player_leave", match, text, source_form)

    for pattern, source_form in _STRUCTURED_DEATH_PATTERNS:
        match = pattern.search(text)
        if match:
            return _event("player_death", match, text, source_form)

    for pattern, source_form in _ANNOUNCED_DEATH_PATTERNS:
        match = pattern.search(text)
        if match:
            return _event(
                "player_death",
                match,
                text,
                source_form,
                requires_known_player=True,
            )

    return None


if __name__ == "__main__":
    samples = (
        '[PlayerName] connected to server',
        '[PlayerName] disconnected from server',
        'PlayerName has died',
        'OtherName has killed PlayerName',
        '[21-06-26 18:18:38.328] 49488954161694894 "PlayerName" fully connected (10047,8261,1).',
        '[21-06-26 18:20:48.184] 65418948941651651 "PlayerName" disconnected player (10045,8264,1).',
        '[time] user PlayerName died at (13514,10718,0) (non pvp).',
    )
    for sample in samples:
        event = parse_log_event(sample)
        print(event.to_dict() if event else None)
