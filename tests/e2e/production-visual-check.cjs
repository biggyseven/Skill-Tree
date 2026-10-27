const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { chromium } = require('@playwright/test');

const BASE_URL = (process.env.TARGET_URL || 'https://skill-tree-vjon.onrender.com').replace(/\/$/, '');
const OUT = path.resolve(__dirname, 'test-results/production-visual');
const report = {
  target: BASE_URL,
  startedAt: new Date().toISOString(),
  checks: {},
  pageErrors: [],
  firstPartyHttpErrors: [],
  screenshots: [],
};

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const origin = new URL(BASE_URL).origin;

  page.on('pageerror', error => report.pageErrors.push(error.message));
  page.on('response', response => {
    try {
      if (new URL(response.url()).origin === origin && response.status() >= 400) {
        report.firstPartyHttpErrors.push({ status: response.status(), url: response.url() });
      }
    } catch (_) {}
  });

  try {
    const response = await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 120000 });
    assert(response, 'No main document response from production');
    assert.equal(response.status(), 200, 'Production home page must return HTTP 200');
    report.checks.homeHttpStatus = response.status();
    report.checks.pageTitle = await page.title();

    await page.getByRole('button', { name: 'Ouvrir les paramètres' }).waitFor({
      state: 'visible',
      timeout: 90000,
    });
    await page.getByRole('navigation', { name: 'Navigation principale' }).waitFor({
      state: 'visible',
      timeout: 30000,
    });
    await page.waitForFunction(() => {
      const state = window.Alpine && window.Alpine.$data(document.body);
      return Array.isArray(state?.nodes) && state.nodes.length > 0;
    }, null, { timeout: 90000 });

    report.checks.dashboardNavigationVisible = true;
    report.checks.courseNodesLoaded = await page.evaluate(() => window.Alpine.$data(document.body).nodes.length);
    const desktopShot = path.join(OUT, 'production-dashboard-desktop.png');
    await page.screenshot({ path: desktopShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(desktopShot);

    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(400);
    report.checks.mobileViewport = await page.evaluate(() => ({
      width: window.innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 2,
    }));
    const mobileShot = path.join(OUT, 'production-dashboard-mobile.png');
    await page.screenshot({ path: mobileShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(mobileShot);

    await page.setViewportSize({ width: 1600, height: 1000 });
    const nav = page.getByRole('navigation', { name: 'Navigation principale' });
    await nav.getByRole('button', { name: 'Labs' }).click();
    await page.locator('a[data-lab-card="catalog"]').first().waitFor({ state: 'visible', timeout: 60000 });
    await page.waitForFunction(() => {
      const state = window.Alpine && window.Alpine.$data(document.body);
      return state && state.labIndexTask === null;
    }, null, { timeout: 60000 });

    const workspaceLinks = page.locator('a[data-lab-card="catalog"][data-lab-kind="workspace-v2"]');
    const workspaceLinkCount = await workspaceLinks.count();
    assert(workspaceLinkCount > 0, 'The visible lab catalogue has no Lab Workspace v2 entry');
    report.checks.workspaceLinksVisible = workspaceLinkCount;

    const workspaceLink = workspaceLinks.first();
    report.checks.selectedLabLink = await workspaceLink.getAttribute('href');
    const labPagePromise = context.waitForEvent('page');
    await workspaceLink.click();
    const labPage = await labPagePromise;
    await labPage.waitForLoadState('domcontentloaded', { timeout: 90000 }).catch(() => {});
    await labPage.getByText('Lab actif', { exact: true }).waitFor({ state: 'visible', timeout: 90000 });

    const equipmentPanel = labPage.getByTestId('equipment-palette-panel');
    await equipmentPanel.waitFor({ state: 'visible', timeout: 30000 });
    const equipmentTab = labPage.getByRole('tab', { name: /Équipements/ });
    const cableTab = labPage.getByRole('tab', { name: /Câbles/ });
    await equipmentTab.waitFor({ state: 'visible' });
    await cableTab.waitFor({ state: 'visible' });

    report.checks.workspaceTitle = await labPage.title();
    report.checks.workspaceLabActive = true;
    report.checks.equipmentLibraryTabVisible = await equipmentTab.isVisible();
    report.checks.equipmentLibraryBadge = (await equipmentTab.innerText()).trim();
    // Equipment cards are draggable divs, not buttons; inspect the actual library items.
    report.checks.equipmentPaletteItemCount = await labPage.locator('#lab-library-panel [draggable="true"]').count();

    const workspaceEquipmentShot = path.join(OUT, 'production-lab-workspace-equipment.png');
    await labPage.screenshot({ path: workspaceEquipmentShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(workspaceEquipmentShot);

    await cableTab.click();
    await labPage.getByText('Types de câbles', { exact: true }).waitFor({ state: 'visible', timeout: 15000 });
    report.checks.cableLibraryTabVisible = await cableTab.isVisible();
    report.checks.cableLibraryBadge = (await cableTab.innerText()).trim();
    report.checks.cableTypeCount = await labPage.locator('[data-testid^="cable-item-"]').count();
    assert(report.checks.cableTypeCount > 0, 'Cable library rendered no selectable cable types');

    const workspaceCableShot = path.join(OUT, 'production-lab-workspace-cables.png');
    await labPage.screenshot({ path: workspaceCableShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(workspaceCableShot);

    report.checks.reactFlowNodeCount = await labPage.locator('.react-flow__node').count();
    report.checks.reactFlowEdgeCount = await labPage.locator('.react-flow__edge').count();
    assert(report.checks.reactFlowNodeCount > 0, 'Lab Workspace shows no React Flow equipment nodes');
    assert(
      report.checks.equipmentPaletteItemCount > 7,
      `Equipment library currently exposes only ${report.checks.equipmentPaletteItemCount} types; expected more than seven.`
    );

    report.checks.desktopLayout = await labPage.evaluate(() => ({
      width: window.innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 2,
    }));
    report.completedAt = new Date().toISOString();
    report.status = report.pageErrors.length === 0 ? 'passed' : 'failed';
    await fs.writeFile(path.join(OUT, 'production-visual-summary.json'), JSON.stringify(report, null, 2));
    assert.equal(report.pageErrors.length, 0, 'Browser reported uncaught JavaScript errors');
    console.log(JSON.stringify(report, null, 2));
  } catch (error) {
    report.status = 'failed';
    report.failure = error.stack || String(error);
    report.completedAt = new Date().toISOString();
    await fs.writeFile(path.join(OUT, 'production-visual-summary.json'), JSON.stringify(report, null, 2)).catch(() => {});
    console.log(JSON.stringify(report, null, 2));
    throw error;
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
