const os = require('node:os');
const path = require('node:path');
const { defineConfig } = require('@playwright/test');

const databasePath = process.env.SKILLTREE_DB
  || path.join(os.tmpdir(), `skilltree-diagnostic-browser-${process.pid}.db`);
const baseURL = process.env.BASE_URL || 'http://127.0.0.1:8012';

module.exports = defineConfig({
  testDir: './specs',
  outputDir: './test-results',
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  timeout: 45_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL,
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1440, height: 1000 },
    actionTimeout: 10_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'python -m uvicorn app.api:app --host 127.0.0.1 --port 8012',
    cwd: path.resolve(__dirname, '../..'),
    url: `${baseURL}/api/tree`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      SKILLTREE_DB: databasePath,
      PYTHONUNBUFFERED: '1',
    },
    stdout: 'pipe',
    stderr: 'pipe',
  },
});