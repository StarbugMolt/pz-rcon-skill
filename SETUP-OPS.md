# Setup & Operations (Non-Skill Docs)

This file contains setup/runbook material for operators. SIMON's authoritative runtime instructions are in `skills/pz-director/SKILL.md`.

## Install / Enable

1. Enable Discord on the Project Zomboid server and configure the current Build 42 channel-name settings:
   - `DiscordEnable=true`
   - `DiscordChatChannel=<chat-channel-name>`
   - `DiscordLogChannel=<log-channel-name>`
   - `DiscordCommandChannel=<command-channel-name>`
2. Keep the PZ server's Discord credential on the server host; do not duplicate it into this repository or the skill workspace.
3. Record the PZ relay bot's Discord user ID for authoritative-response filtering.
4. Configure SIMON-side runtime metadata using `skills/pz-director/.env.example`.
5. Load/install the **source skill directory containing `SKILL.md`** through the current OpenClaw skill mechanism. Do not assume the generated `.skill` ZIP is directly installable by current Git/local OpenClaw flows.
6. Run `scripts/simon_radio_listener.py` under the supervised user service for persistent chat listening.

The legacy `simon_fast_listener.py` implementation has been removed. If an existing service still points at that filename, update the service command before deploying this revision.

## Trust boundary

The runtime intentionally separates **fast dialogue** from **game mutation**:

- `simon_radio_listener.py` — fast player-facing chat. The model cannot choose mutations; a separate deterministic supply helper may execute a verified occasional/test-mode item gift before the reply.
- scheduled OpenClaw director turns — scenario/GM decisions after the Python preflight permits an LLM turn;
- `pz-console.sh` — explicit mutation/console transport with exact-relay response confirmation.

This separation is deliberate. A smaller/cheaper direct-chat model may improvise dialogue, but it is not trusted to invent server state or mutate the game.

## Zero-player cost invariant

No scheduled LLM path may be started until its Python trigger positively proves at least one PZ player is online.

Current scheduled gates:

- ambient: `scripts/simon_ambient_trigger.py`
- greeting: `scripts/greeting_trigger.py`

Both call `scripts/simon_online_gate.py` before returning `fire=true`.

The direct chat listener does **not** re-probe the roster before its chat-completion request: an inbound relay message is itself proof that the survivor is online at that instant. The authoritative roster check stays on the scheduled paths, where there is no inbound message to anchor on.

The gate itself is tiered and always fails closed:

1. relay-staleness check on the listener state file (<1 s, no Discord call);
2. persistent negative cache (20 min) for a server that stays down;
3. short in-memory positive cache (20 s) so the cron trigger and a chat request in the same minute do not race into a false `baseline-read-failed`;
4. the authoritative `Players connected (N)` probe, capped at 8 s per Discord call so it cannot tip the cron trigger's budget.

The required deployment order is therefore:

```text
cron/event
  -> Python trigger/preflight
     -> fire=false: stop, no agent/model turn
     -> fire=true : agent/model turn may start
```

Do not implement the empty-server check inside an LLM prompt; by then the model call has already been spent.

## Three channel roles

### Chat channel

`DiscordChatChannel` is the bidirectional player-chat path. In-game `/all` chat is mirrored to Discord, and Discord messages in that channel can be relayed back into the game.

Player-facing SIMON broadcasts belong on this path.

### Log channel

`DiscordLogChannel` is a read-only observation path from PZ's perspective: the server emits compact notifications there and ignores Discord messages sent back into the channel.

SIMON consumes this channel deterministically for compact player login/logout notifications and conservatively verified death announcements. Login queues the greeting path; logout updates active-player/arc state. Coordinates are optional and never required. Because Build 42 death-announcement wording can also be emitted for animals, a human-readable death line becomes player-death memory only when the victim name matches a survivor already known to SIMON. Raw log lines never directly trigger an LLM. Broader mod/server-event normalization remains future work.

### Command channel

`DiscordCommandChannel` is the server-console path. It is operational infrastructure, not player chat.

Discord ACLs for this channel are an operator responsibility. `pz-console.sh` accepts a response only from the configured `PZ_RELAY_BOT_ID`, and confirmed requests are serialized because the native PZ bridge does not provide request IDs.

## SIMON runtime metadata

Use `skills/pz-director/.env.example` for the expected non-secret runtime metadata:

- `PZ_DISCORD_CHANNEL_ID`
- `PZ_DISCORD_LOG_CHANNEL_ID`
- `PZ_DISCORD_COMMANDS_CHANNEL_ID`
- `PZ_RELAY_BOT_ID`
- `PZ_ENABLED_MODS`
- `PZ_WORKSHOP_ITEMS` (audit metadata)
- `SIMON_GIFT_COOLDOWN_SECONDS`, `SIMON_HELP_GIFT_CHANCE`, `SIMON_TEST_MODE`
- `SIMON_OUTSIDE_READY_SECONDS` (large-delivery outside-ready window)
- `PZ_ALLOW_RAW=false` by default; enable only for explicit operator maintenance
- optional console wait/timeout settings

Do not copy model credentials, Discord bot tokens, passwords, or other authentication material into the skill directory.

The standalone listener is a separate process boundary. Credentials it directly needs must be injected through its protected service/runtime environment; it cannot magically consume an in-memory OpenClaw SecretRef resolved in another process.

## Listener / daemon

`scripts/simon_radio_listener.py`:

- parses PZ-relayed survivor chat;
- consumes authoritative Discord log-channel login/logout/death events through `simon_log_events.py`;
- queues player connection greetings;
- records player/memory and active-arc interactions;
- uses the parsed PZ survivor identity rather than the shared Discord relay account;
- sees only already-revealed active-arc context;
- performs blocking model work off the Discord event loop;
- treats an inbound relay message as presence proof on the direct-chat path (no second roster probe); the authoritative positive-player check stays on the scheduled paths;
- applies a **20 s per-survivor reply cooldown** on the direct-chat path — the first transmission is always answered, only follow-ups inside the window are suppressed — on top of the simultaneous-duplicate in-flight guard;
- pins the chat-completion contract (JSON `{"reply": ...}` output, thinking disabled, no stop sequences) and salvages a truncated JSON reply instead of dropping it;
- while `PZ_DISCORD_LOG_CHANNEL_ID` is still unset, it also parses lifecycle lines in the commands channel, so login/logout/death detection survives the log/commands split;
- never lets the fast model choose a mutation;
- may call `simon_supply.py` for a verified occasional/test-mode item gift, which has its own separate cooldown/chance controls.

## Catalogue / scenario integrity

The checked-in catalogues remain the source of truth for game identifiers. Documentation placeholders are never defaults. Descriptive-only catalogue files do not authorize guessed IDs.

Narrative arc mutations use explicit `pz-console.sh` aliases, not raw console verbs. Vehicle scripts used by built-in arcs are taken from enabled-mod reference catalogues.

## Generated package artifact

`skills/pz-director.skill` is a generated compatibility/archive artifact. If the repository keeps it, rebuild it whenever `skills/pz-director/` changes and verify that removed source files are also absent from the archive.

## Review / migration notes

See `skills/pz-director/references/hardening-review.md` for the audited status and remaining implementation work. A recommendation in that document is not deployed unless the corresponding runtime code is present.