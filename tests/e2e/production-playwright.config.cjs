const { defineConfig } = require('@playwright/test');

const baseURL = process.env.BASE_URL || 'https://skill-tree-vjon.onrender.com';

module.exports = defineConfig({
  testDir: './specs',
  testMatch: ['production-lab-cli.spec.cjs'],
  outputDir: './test-results-production',
  fullyParallel: false,
  forbidOnly: true,
  retries: 1,
  workers: 1,
  reporter: 'list',
  timeout: 60_000,
  expect: { timeout: 20_000 },
  use: {
    baseURL,
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1440, height: 1000 },
    actionTimeout: 15_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
});
