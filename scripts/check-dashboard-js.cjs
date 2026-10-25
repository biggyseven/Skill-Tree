#!/usr/bin/env node
'use strict';

// Syntax-check inline JavaScript in the legacy Alpine dashboard. The React/Vite
// build covers the Lab Workspace, but does not parse scripts embedded in
// static/index.html. No script is executed; Node only parses temporary copies.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const htmlPath = path.resolve(__dirname, '../static/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const scriptPattern = /<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi;
const acceptedTypes = new Set([
  '',
  'text/javascript',
  'application/javascript',
  'text/ecmascript',
  'application/ecmascript',
  'module',
]);

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'skilltree-dashboard-js-'));
let checked = 0;
const failures = [];

try {
  for (const match of html.matchAll(scriptPattern)) {
    const attributes = match[1] || '';
    const source = match[2] || '';
    if (/\bsrc\s*=/i.test(attributes) || !source.trim()) continue;

    const typeMatch = attributes.match(/\btype\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s>]+))/i);
    const type = String(typeMatch ? (typeMatch[1] || typeMatch[2] || typeMatch[3]) : '').toLowerCase();
    if (!acceptedTypes.has(type)) continue;

    const extension = type === 'module' ? '.mjs' : '.cjs';
    const sourcePath = path.join(tempDir, `inline-${checked + 1}${extension}`);
    fs.writeFileSync(sourcePath, source, 'utf8');
    const result = spawnSync(process.execPath, ['--check', sourcePath], { encoding: 'utf8' });
    checked += 1;

    if (result.status !== 0) {
      failures.push({
        script: checked,
        output: (result.stderr || result.stdout || 'Node syntax check failed').trim(),
      });
    }
  }
} finally {
  fs.rmSync(tempDir, { recursive: true, force: true });
}

if (checked === 0) {
  console.error('No inline JavaScript was found in static/index.html.');
  process.exit(2);
}
if (failures.length) {
  for (const failure of failures) {
    console.error(`Inline script #${failure.script} has a syntax error:\n${failure.output}`);
  }
  process.exit(1);
}
console.log(`Dashboard JavaScript syntax OK: ${checked} inline script(s) checked.`);
