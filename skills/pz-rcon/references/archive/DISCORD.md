# ARCHIVED (Non-Canonical)

This file is historical context only. Do not treat it as current skill authority.
Canonical files:
- `../../SKILL.md`
- `../commands.md`

# Discord Integration (Build 42 Native)

Project Zomboid Build 42 has improved native Discord integration. This allows chat bridging without complex 3rd party bots.

## 1. Setup Discord Bot
1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Create a **New Application** (e.g., "ZomboidBridge").
3.  Go to **Bot** -> **Add Bot**.
4.  **Token**: Copy the token (you will need this for the server config).
5.  **Privileged Gateway Intents**: Enable "Message Content Intent" and "Server Members Intent".
6.  **OAuth2**: Go to OAuth2 -> URL Generator. Select `bot`. Permissions: `Read Messages/View Channels`, `Send Messages`.
7.  Invite the bot to your server.

## 2. Configure Project Zomboid Server
Edit your `servertest.ini` (or your specific server config file):

```ini
# Discord Integration
DiscordEnable=true
DiscordToken=YOUR_BOT_TOKEN_HERE
DiscordChannelID=YOUR_CHANNEL_ID_HERE
DiscordChannelIDMonitor=YOUR_LOG_CHANNEL_ID_HERE
```

*   `DiscordChannelID`: The channel where in-game chat will be mirrored.
*   `DiscordChannelIDMonitor`: (Optional) A separate channel for connection logs/admin info.

## 3. How it works with `pz-rcon`
This bridge is **one-way for the agent** unless we add a specific reader.
*   **Agent -> Game**: The agent uses RCON (`pz-rcon servermsg`) to broadcast to players.
*   **Game -> Agent**: The agent needs to "watch" the Discord channel.

## 4. Agent "Listening"
To let the agent react to in-game events, the agent must be in the Discord channel configured above.
*   When a player chats, the bot posts to Discord: `[PlayerName]: Help us!`
*   The agent (StarbugMolt) sees this message in the channel and can decide to trigger an RCON event.

**Example Flow:**
1.  Player in-game: "We are starving!"
2.  Discord Bot: `[Gamer123]: We are starving!`
3.  StarbugMolt (reading Discord): "I see you're hungry. Sending supplies."
4.  StarbugMolt (RCON): `additem "Gamer123" Base.CannedBeans 5`
