# pz-director

SIMON's Project Zomboid Build 42 radio-director skill. Discord-first; RCON is inactive.

## Authority

`SKILL.md` is the authoritative operational/personality contract. Keep model-facing behavioral rules there rather than creating competing prompts or concrete example lists in this README.

## Hardened runtime split

- `scripts/simon_radio_listener.py` — fast player-facing dialogue; the model never chooses mutations. `simon_supply.py` may separately perform a verified occasional/test-mode supply gift.
- `scripts/simon_arc_engine.py` — canonical narrative-arc state/lifecycle owner.
- `scripts/pz-console.sh` — explicit mutation transport with confirmed relay responses.
- Python cron triggers — preflight scheduled turns before an LLM/agent exists.

The legacy `simon_fast_listener.py` implementation has been retired.

## Cost invariant

If Python cannot positively prove at least one PZ player is online, scheduled LLM work must not start. The active radio listener also performs a positive-player preflight immediately before direct chat completion.

## Discord structure

Project Zomboid Build 42 provides three Discord channel roles:

- `DiscordChatChannel` — player chat and SIMON broadcasts;
- `DiscordLogChannel` — server log output;
- `DiscordCommandChannel` — server-console traffic.

Dedicated normalized log-channel ingestion remains future work; do not assume it is active yet.

## Main references

- `SKILL.md` — SIMON identity, fast-model guardrails, GM discipline and runtime rules.
- `.env.example` — non-secret deployment metadata shape.
- `references/project-zomboid-lore.md` — Project Zomboid world/lore knowledge.
- `references/narrative-arcs.md` — built-in scenario beats and verified wrapper mutations.
- `references/hardening-review.md` — implemented vs remaining hardening work.
- `references/catalogs/` — vanilla and enabled-mod reference data.

## Documentation placeholders

Values inside `<...>` are syntax placeholders only and are never real runtime values. Literal format tokens must not be treated as verified game identifiers.

## Generated package

The sibling `../pz-director.skill` file is a generated compatibility/archive artifact. Rebuild it whenever this source directory changes so deleted/renamed files and new instructions remain synchronized.
