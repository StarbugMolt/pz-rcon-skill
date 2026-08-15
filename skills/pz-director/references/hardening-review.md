# SIMON pz-director Hardening Review

This document records the August 2026 hardening pass for the Discord-first Project Zomboid controller. It is an operator/developer document, not in-world SIMON knowledge.

## Status summary

### Implemented in this branch

- **Zero-player LLM gating:** ambient and greeting scheduled paths call the Python online-player gate before they can return `fire=true`; the active direct radio listener performs the same preflight immediately before its external chat-completion request.
- **Fast-model trust boundary:** the active chat model cannot select mutations. A deterministic `simon_supply.py` helper may separately execute a verified occasional/test-mode item gift and expose only the confirmed result to the model.
- **Legacy listener removed:** the older mutation-capable `simon_fast_listener.py` is no longer part of the source skill.
- **Command confirmation hardening:** `pz-console.sh` serializes confirmed requests, snapshots a relay-message baseline, requires the exact configured relay user ID, rejects unknown aliases, and returns non-zero on timeout/recognized failures.
- **Per-survivor chat identity/privacy:** embedded PZ survivor names are trusted only from the exact configured relay account. Human Discord users cannot spoof `PlayerName:` to poison another survivor's memory, obtain PZ-only gifts or establish large-delivery readiness; a coincidental Discord display-name match also cannot read that survivor's private memory/arc context. PZ in-flight guards use the parsed survivor identity instead of the shared relay-bot Discord account.
- **Arc ownership/privacy:** the Python arc engine is the state owner, player-facing arc context contains already-fired information only, and future beats/mutations are hidden.
- **Quiet participant memory:** active arcs retain `playersSeen`, so survivors who experienced an arc without speaking can still receive recaps.
- **Reset fail-closed behavior:** SIMON memory is archived before destructive reset; archive failure aborts the wipe; lifetime reset count and operator reason are preserved.
- **Async direct chat:** blocking model work is moved off the Discord event loop.
- **Scenario mutation normalization:** built-in arcs use documented `pz-console.sh` aliases and checked-in vehicle references rather than raw/guessed console syntax.
- **Build 42 Discord observations:** chat/log/command roles use the current channel-name model; the dedicated log channel now drives conservative login/logout/death state updates without directly invoking an LLM.
- **Lore integration:** researched Project Zomboid lore is explicitly loaded for lore-sensitive reasoning, with canon/rumor/theory distinctions and 1993 constraints.
- **Fast-model roleplay contract:** `SKILL.md` locks SIMON's voice, in-world GM behavior, player agency rules, secrecy boundaries and placeholder discipline. Direct chat also rejects obvious out-of-role output, and remembered/player text is explicitly untrusted against prompt injection.
- **Guarded large deliveries:** vehicle drops require recent explicit outside-ready evidence for the exact present survivor, verified vehicle IDs, a fresh online preflight, a confirmed chopper event and a one-time vehicle authorization token.
- **Console blast-radius limits:** runtime aliases require confirmation, raw is disabled by default, and give/horde/XP/weather inputs are bounded/validated.
- **Config cleanup:** unused `config.json.example` removed; deployment docs separate non-secret routing metadata from credentials.

### Still intentionally outstanding

These are not merge blockers for the hardening above, but remain future work:

1. **Broader log-event normalization.** Core login/logout/death ingestion is implemented. Additional server/mod log formats still need real captured samples before they are classified.
2. **Universal machine-enforced asset resolver for director mutations.** The fast direct-chat model no longer chooses assets at all, and built-in scenario assets are verified, but arbitrary future director item/vehicle mutations still rely on the director following checked-in references rather than one universal resolver at the execution boundary.
3. **Full atomic-state migration across every memory helper.** The new/rewritten runtime paths use safer replacement/merge patterns, but older player/global memory modules still need a complete transactional audit.
4. **Install-side OpenClaw secret migration verification.** Repository guidance is current, but the deployed OpenClaw/service configuration must still be checked on the host.
5. **Operator ACLs.** Discord permissions on the command channel remain outside the skill's code boundary.

Do not treat any outstanding item as deployed merely because it is documented here.

## 0. Highest priority: no LLM call when nobody is playing — IMPLEMENTED

The cost/silence invariant is:

> If the runtime cannot positively prove at least one Project Zomboid player is online, do not create the LLM/agent turn.

The check must happen before the model exists, not inside the model prompt.

Current paths:

- `simon_ambient_trigger.py` → `simon_online_gate.py` → only then may the Ambient Director agent turn exist.
- `greeting_trigger.py` → `simon_online_gate.py` plus a pending greeting requirement → only then may the Greeting Dispatcher turn exist.
- JavaScript code-mode trigger files are compatibility wrappers that delegate to Python; they do not maintain an independent player-count implementation.
- `simon_radio_listener.py` checks the authoritative roster immediately before its direct external chat-completion request.

The online gate requires a fresh `Players connected (N)` response from the exact configured relay user. Missing configuration, stale/ambiguous output, timeout, command failure, parse failure or `N = 0` fail closed.

A join event or queued greeting by itself is never proof that a player is still online.

## 1. Discord command-channel permissions — OPERATOR OWNED

Discord ACLs are not created by this skill. The skill's exact-author filtering prevents SIMON from trusting the wrong response author; it does not prevent an unauthorized Discord account from posting to the server's command channel if server permissions are misconfigured.

The operator should restrict `DiscordCommandChannel` to only the accounts/services that genuinely require it.

## 2. Command response correlation — IMPLEMENTED

`pz-console.sh` now:

- requires `PZ_DISCORD_COMMANDS_CHANNEL_ID`;
- requires `PZ_RELAY_BOT_ID` for confirmed/waiting commands;
- serializes waiting requests with `flock` because the native PZ Discord command bridge has no request ID;
- reads the channel before posting and records the newest exact-relay message ID as a baseline;
- accepts only newer messages from that exact relay user ID;
- requires a real `Players connected (N)` response for the `players` alias;
- rejects unrelated lifecycle/roster messages as confirmations for other mutations;
- rejects unknown wrapper aliases instead of silently passing them through;
- returns non-zero on timeout and recognizable failures.

`raw`/`cmd` remains an explicit operator escape hatch. `SKILL.md` forbids models from using it merely because a desired action lacks a documented alias.

## 3. Per-player chat cooldown / fast-model boundary — IMPLEMENTED

The hardened listener is `scripts/simon_radio_listener.py`.

Logical chat keys are:

- in-game relay: `pz:<normalized survivor name>`;
- direct Discord user: `discord:<user id>`.

A per-key in-flight guard prevents one survivor from starting simultaneous response turns.

The old `simon_fast_listener.py` path is removed. This also closes its larger trust issue: the old fast model could propose arbitrary item IDs and trigger item mutations. The new fast listener is dialogue-only, so a smaller model can improvise roleplay but cannot mutate the server.

## 4. Ambient trigger ownership — IMPLEMENTED

The JavaScript trigger files are compatibility wrappers around the Python triggers. They do not own arc state or maintain a second finalization schema.

Arc state transitions, participant tracking, stale cleanup and finalization remain in `simon_arc_engine.py`.

This avoids the previous JS/Python schema drift risk.

## 5. World-memory reset safety — IMPLEMENTED

`simon_reset_world.py` resets SIMON's remembered world state, **not** the Project Zomboid save/map.

The helper now:

- imports all modules it uses;
- archives current player/arc/global memory and listener-state files first;
- aborts before destructive deletion if a required archive copy raises;
- increments `totalResetsEver` monotonically;
- preserves the operator-supplied reset reason;
- resets the current-era state only after archive success;
- supports dry-run and optional in-world sign-off;
- uses atomic replacement for its JSON reset writes.

## 6. SIMON's server observations — CORE LIFECYCLE IMPLEMENTED / BROADER EVENTS FUTURE

Current Build 42 Discord integration exposes:

```ini
DiscordChatChannel=<chat-channel-name>
DiscordLogChannel=<log-channel-name>
DiscordCommandChannel=<command-channel-name>
```

`simon_radio_listener.py` now consumes the dedicated log channel through `simon_log_events.py`. The parser deliberately prioritizes compact Discord lifecycle/death notifications; detailed coordinate-bearing user-log lines are fallback-only and coordinates are never required:

- `player_join` — updates visit/arc state and queues the gated greeting path;
- `player_leave` — updates player/arc state;
- `player_death` — records the event in player/global/arc memory without marking the survivor offline.

Human-readable death announcements are additionally checked against the known-survivor registry before becoming player-death memory, because Build 42 has emitted the same announcement wording for animals. These log events are deterministic observation only and never directly invoke an LLM. The Greeting Dispatcher still performs the authoritative online-player preflight before any model turn.

Broader normalized event ingestion should classify only formats verified from actual Build 42/server/mod output. Unknown lines remain diagnostic/unknown rather than being guessed into fictional events.

## 7. Item / asset catalogue integrity — HARDENED, UNIVERSAL RESOLVER STILL FUTURE

### Repository coverage

`.env.example` declares 38 enabled mod IDs and the active `references/catalogs/mods/` directory has a matching reference file for each of those mod IDs.

File presence is not proof that a mod contributes a spawnable item or vehicle script. Some references are descriptive/framework-only.

### Fast model

The direct radio model remains outside mutation selection. It does not receive or return `give_items`; deterministic `simon_supply.py` chooses/validates any allowed gift and uses the confirmed console wrapper independently.

This removes the highest-risk failure mode: a small model inventing a plausible-looking identifier and immediately mutating the server.

### Director path

For director/scenario mutations:

- syntax placeholders are never real IDs;
- remembered model knowledge is not authoritative;
- only checked-in active references may supply identifiers;
- built-in arc vehicle scripts have been normalized to verified enabled-mod references;
- malformed/raw scenario mutation strings have been replaced with wrapper aliases.

A future universal resolver should still validate arbitrary item/vehicle identifiers at the final mutation boundary so future custom director logic cannot bypass the reference discipline.

## 8. Async and shared-state safety — PARTIAL / MOST CRITICAL CHAT PATH FIXED

The active radio listener moves blocking model work to a worker thread so the Discord event loop remains responsive.

The rewritten listener/reset/arc paths use safer merge or atomic-replacement patterns for the state they own.

Remaining work is a full audit/migration of older `simon_player_memory.py` and `simon_global_memory.py` writers. A future common transaction helper should:

- hold a real lock across the full read-modify-write transaction when concurrent writers share a document;
- atomically replace the target after a successful write;
- preserve unrelated fields;
- fail closed on malformed existing state rather than silently replacing it with defaults.

## 9. Arc context and quiet participants — IMPLEMENTED

Player-facing active-arc context now exposes only already-fired narration and the same survivor's own relevant interaction context.

It does **not** expose:

- the planned next beat;
- hidden future mutations;
- future outcomes.

Active arcs maintain `playersSeen` in addition to `playersOnline`. Final recap participants are the union of seen survivors and explicit interacting survivors, so quiet participants are not discarded simply because they never typed.

## 10. Secret/config cleanup — REPOSITORY COMPLETE, DEPLOYMENT VERIFY

The checked-in skill template/documentation is intended for non-secret routing/runtime metadata only.

OpenClaw-supported credentials should use current OpenClaw secret storage/SecretRefs. A standalone Python listener is a separate process boundary and cannot automatically consume a SecretRef that another OpenClaw process resolved in memory; credentials it directly requires must be injected through its protected service/runtime environment.

The unused `config.json.example` file has been removed.

The Project Zomboid server's own Discord credential remains a server-host configuration concern and should not be duplicated into the skill repository.

The remaining task is operational: verify the deployed host/service/OpenClaw configuration has actually migrated away from any legacy plaintext locations.

## Lore and lesser-model roleplay hardening — IMPLEMENTED

`references/project-zomboid-lore.md` is the world-background reference for SIMON. It distinguishes confirmed canon, official supplemental material, in-world claims and theories, and deliberately leaves the infection's ultimate origin unresolved.

`SKILL.md` now locks the core roleplay contract for smaller models:

- SIMON is a bunker-radio survivor/in-world GM, not an assistant/admin bot;
- stay in-world and period-correct to 1993;
- terse, dry, weathered, suspicious voice;
- normally 1–3 sentences;
- no therapy/corporate/customer-service drift;
- player agency is never overwritten;
- scenarios advance one small believable beat at a time;
- major scenarios remain under the narrative director/arc catalogue;
- future arc information stays hidden;
- one player's private memory never leaks to another.

The active fast radio listener carries an additional compact version of these constraints directly in its system prompt so its behavior does not depend on a small external model remembering the entire skill file.

## Next hardening order

1. Extend the existing log-channel parser with additional normalized server/mod events only after collecting real B42/mod log samples.
2. Add a universal deterministic asset resolver at the director mutation boundary.
3. Finish transactional/atomic-state migration of older memory modules.
4. Verify deployed OpenClaw/service secret configuration and cron/service commands.
5. Add regression tests whenever new event/mutation capabilities are introduced.
