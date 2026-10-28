#!/usr/bin/env node
'use strict';

// Parse les scripts inline des deux points d'entrée HTML (dashboard racine et
// copie statique). Aucun script n'est exécuté ; Node analyse des copies temporaires.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const repoRoot = path.resolve(__dirname, '..');
const htmlPaths = [
  path.join(repoRoot, 'index.html'),
  path.join(repoRoot, 'static', 'index.html'),
];
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
  for (const htmlPath of htmlPaths) {
    const html = fs.readFileSync(htmlPath, 'utf8');
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
          file: path.relative(repoRoot, htmlPath),
          script: checked,
          output: (result.stderr || result.stdout || 'Node syntax check failed').trim(),
        });
      }
    }
  }
} finally {
  fs.rmSync(tempDir, { recursive: true, force: true });
}

if (checked === 0) {
  console.error('No inline JavaScript was found in index.html or static/index.html.');
  process.exit(2);
}
if (failures.length) {
  for (const failure of failures) {
    console.error(`Inline JavaScript in ${failure.file} #${failure.script} has a syntax error:\n${failure.output}`);
  }
  process.exit(1);
}
console.log(`Dashboard JavaScript syntax OK: ${checked} inline script(s) checked across both HTML entrypoints.`);
