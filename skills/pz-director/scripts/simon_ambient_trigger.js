#!/usr/bin/env node
/**
 * Compatibility wrapper for OpenClaw code-mode environments.
 *
 * IMPORTANT: this file contains no independent gating logic. Every scheduled
 * path that can wake an LLM must pass through the Python gate, which performs
 * the authoritative online-player check and fails closed.
 */
const path = require('path');
const { spawnSync } = require('child_process');

const script = path.join(__dirname, 'simon_ambient_trigger.py');
const result = spawnSync('python3', [script], { encoding: 'utf8' });

if (result.error || result.status !== 0 || !result.stdout) {
  process.stdout.write(JSON.stringify({ fire: false, reason: 'python-gate-failed' }) + '\n');
  process.exit(0);
}

process.stdout.write(result.stdout.trim() + '\n');
process.exit(0);
