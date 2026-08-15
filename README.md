# pz-director — Project Zomboid Atmosphere Director

This repository contains the OpenClaw skill used by SIMON, the bunker-radio survivor/in-world GM for a Project Zomboid Build 42 server.

The repository name `pz-rcon-skill` is legacy. The active skill is `pz-director`, using a Discord-first architecture rather than RCON.

## Authoritative instructions

`skills/pz-director/SKILL.md` is the single operational instruction surface for SIMON. Do not duplicate item lists, concrete command values, or alternate personality rules in this README.

## Runtime trust boundary

The hardened runtime deliberately separates fast dialogue from game mutation:

- `skills/pz-director/scripts/simon_radio_listener.py` — player-facing fast chat. The model cannot choose server mutations; a deterministic helper may perform a verified occasional/test-mode supply gift.
- scheduled director turns — bounded scenario/GM decisions after Python preflight permits an LLM turn.
- `skills/pz-director/scripts/pz-console.sh` — explicit server mutation transport with exact-relay confirmation.

The old `simon_fast_listener.py` implementation has been removed.

## Zero-player LLM invariant

No scheduled model turn should exist until its Python trigger positively confirms at least one PZ player is online. The active direct radio listener performs the same authoritative preflight immediately before its external chat-completion request.

A stale join event or queued greeting is not sufficient proof that somebody is still online.

## Build 42 Discord roles

Current Project Zomboid Build 42 configuration separates Discord into three channel-name roles:

```ini
DiscordChatChannel=<chat-channel-name>
DiscordLogChannel=<log-channel-name>
DiscordCommandChannel=<command-channel-name>
```

- Chat: player chat and SIMON's player-facing broadcasts.
- Log: read-only observation for compact player login/logout notifications and conservatively verified death announcements.
- Command: server-console traffic.

The runtime consumes chat, command traffic, and conservative lifecycle/death notifications from the dedicated log channel. Discord notifications do not need coordinates; coordinates are optional metadata only if a detailed line happens to include them. Human-readable death announcements are accepted only when the victim matches a survivor already known to SIMON. Broader mod/server-event normalization remains future work.

## Fast-model documentation rule

Values inside angle brackets, such as `<PlayerName>` or `<Module.Item>`, are documentation placeholders only. They are never real values or defaults.

Concrete object examples are deliberately kept out of model-facing syntax instructions so a smaller model cannot anchor on them as preferred values.

## Repository layout

- `skills/pz-director/SKILL.md` — authoritative SIMON personality, GM and runtime contract.
- `skills/pz-director/.env.example` — non-secret runtime-routing template.
- `skills/pz-director/scripts/simon_radio_listener.py` — hardened player listener plus deterministic log observation and delivery-readiness capture.
- `skills/pz-director/scripts/simon_delivery.py` — guarded large-delivery path: outside-ready presence check, vehicle catalogue validation, confirmed chopper cue and one-time-token vehicle spawn.
- `skills/pz-director/scripts/simon_log_events.py` — conservative login/logout/death log parser.
- `skills/pz-director/scripts/pz-console.sh` — confirmed command-channel wrapper.
- `skills/pz-director/scripts/simon_arc_engine.py` — canonical narrative-arc state owner.
- `skills/pz-director/references/project-zomboid-lore.md` — world/lore knowledge.
- `skills/pz-director/references/hardening-review.md` — implemented/future hardening status.
- `skills/pz-director/references/catalogs/` — vanilla and per-mod references.
- `SETUP-OPS.md` — operator setup notes.
- `skills/pz-director.skill` — generated compatibility/archive artifact.

## Catalogue / scenario discipline

The enabled mod list currently contains 38 mod IDs paired with 38 Workshop IDs, with matching active reference files at repository level. File presence does not automatically prove that a mod provides a spawnable item or vehicle.

`SKILL.md` defines the conservative asset-ID rules. Built-in narrative arcs use documented wrapper aliases and checked-in verified vehicle references rather than raw/guessed server commands.

## Lore / roleplay

The Project Zomboid lore reference distinguishes confirmed canon, official supplemental material, in-world claims and theories. SIMON must preserve those distinctions, remain period-correct to 1993, protect player agency and private memory, and never expose future scenario beats in direct chat.

## Generated skill artifact

`skills/pz-director.skill` is a generated compatibility/archive artifact. Current OpenClaw Git/local installation uses a skill directory containing `SKILL.md`; do not assume the ZIP is directly installable.

Whenever `skills/pz-director/` changes, rebuild and validate the artifact before distributing it.

## License

MIT — see `LICENSE`.
