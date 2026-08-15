#!/usr/bin/env node
/** Compatibility wrapper: all scheduled LLM gating lives in Python. */
const path = require('path');
const { spawnSync } = require('child_process');

const script = path.join(__dirname, 'greeting_trigger.py');
const result = spawnSync('python3', [script], { encoding: 'utf8' });

if (result.error || result.status !== 0 || !result.stdout) {
  process.stdout.write(JSON.stringify({ fire: false, reason: 'python-gate-failed' }) + '\n');
  process.exit(0);
}

process.stdout.write(result.stdout.trim() + '\n');
process.exit(0);
