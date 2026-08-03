#!/usr/bin/env bash
# SIMON Ambient Trigger Wrapper — called by cron as trigger-script
# Outputs {"fire":true} or {"fire":false} based on player count
exec python3 /home/starbugmolt/.openclaw/workspace-simon/skills/pz-rcon/scripts/simon_ambient_trigger.py
