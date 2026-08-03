// SIMON Ambient Trigger — headless code-mode JavaScript.
//
// Called by OpenClaw cron (schedule `*/10 * * * *`). Cron runs this as
// headless JavaScript (not bash), so we MUST `return { fire, message?, state? }`.
//
// Behavior:
//   - Spawns `pz-rcon.sh players` via `tools.call('exec')` and parses the
//     output. Returns { fire: true } only when at least one player is connected.
//   - Otherwise returns { fire: false } so the tick is silenced.
//
// CRITICAL: ZERO regex literals anywhere in this file. The cron engine's
// code-mode worker throws "SyntaxError: invalid regular expression flags"
// when it sees regex literal syntax in the trigger source, even perfectly
// valid ones. Use string ops only: split, indexOf, charAt, substring, etc.

const RCON_SCRIPT = "/home/starbugmolt/.openclaw/workspace-simon/skills/pz-rcon/scripts/pz-rcon.sh";

return (async () => {
  // Best-effort debug log. NO regex. Use string concat for single-quote escape.
  const appendLog = async (line) => {
    try {
      const ts = new Date().toISOString();
      const safe = String(line).split("'").join("'\\''");
      await tools.call("exec", {
        command: "printf '" + ts + " " + safe + "\\n' >> /tmp/simon-trigger-debug.log",
        timeout: 3,
      });
    } catch (_e) {
      // Logging is best-effort.
    }
  };

  await appendLog("trigger: start");

  if (typeof tools === "undefined" || typeof tools.call !== "function") {
    await appendLog("trigger: tools.call unavailable, fire=false");
    return {
      fire: false,
      message: "tools.call unavailable",
      state: { lastError: "no tools.call", lastAt: Date.now() },
    };
  }

  let result;
  try {
    result = await tools.call("exec", {
      command: RCON_SCRIPT + " players",
      timeout: 12,
    });
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    await appendLog("trigger: exec threw: " + msg);
    return {
      fire: false,
      message: "exec threw: " + msg,
      state: { lastError: msg, lastAt: Date.now() },
    };
  }

  const stdout = result && typeof result.stdout === "string" ? result.stdout : "";
  const stderr = result && typeof result.stderr === "string" ? result.stderr : "";
  const exitCode = result && typeof result.exitCode === "number" ? result.exitCode : null;

  await appendLog(
    "trigger: exec ok, exit=" + exitCode +
      ", stdout=" + JSON.stringify(stdout.slice(0, 200)) +
      ", stderr=" + JSON.stringify(stderr.slice(0, 150))
  );

  // Parse pz-rcon.sh output WITHOUT regex literals.
  //   Valid forms:
  //     "Players connected (0):"           -> empty
  //     "Players connected (N):\n- name (id)\n..."  -> N entries
  const lines = stdout.split("\n");
  const trimmed = [];
  for (let i = 0; i < lines.length; i++) trimmed.push(lines[i].trim());
  let headerLine = null;
  for (let i = 0; i < trimmed.length; i++) {
    if (trimmed[i].indexOf("Players connected (") === 0) {
      headerLine = trimmed[i];
      break;
    }
  }
  if (!headerLine) {
    await appendLog("trigger: no header line, fire=false");
    return {
      fire: false,
      message: "no header line (rc=" + exitCode + ")",
      state: { lastHeader: null, lastAt: Date.now() },
    };
  }

  // Extract declared count via string ops (no regex).
  const openIdx = headerLine.indexOf("(");
  const closeIdx = headerLine.indexOf(")");
  let declaredCount = 0;
  if (openIdx >= 0 && closeIdx > openIdx) {
    const numStr = headerLine.substring(openIdx + 1, closeIdx);
    const n = parseInt(numStr, 10);
    if (!isNaN(n) && n >= 0) declaredCount = n;
  }

  // Count "- " prefixed lines = parsed player list length.
  let parsedPlayers = 0;
  const players = [];
  for (let i = 0; i < trimmed.length; i++) {
    const l = trimmed[i];
    if (l.length > 2 && l.charAt(0) === "-" && l.charAt(1) === " ") {
      parsedPlayers++;
      players.push(l.substring(2));
    }
  }

  await appendLog(
    "trigger: header=" + headerLine +
      ", declaredCount=" + declaredCount +
      ", parsedPlayers=" + parsedPlayers +
      ", fire=" + (declaredCount > 0 && parsedPlayers > 0)
  );

  // Strict gate: BOTH declared count AND parsed list must agree > 0.
  const fire = declaredCount > 0 && parsedPlayers > 0;

  return {
    fire,
    message: fire
      ? "online (" + declaredCount + "): " + players.join(", ")
      : "empty server (declared=" + declaredCount + ", parsed=" + parsedPlayers + ")",
    state: {
      lastHeader: headerLine,
      lastCount: declaredCount,
      lastPlayers: players,
      lastAt: Date.now(),
    },
  };
})();