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

async function authenticateProduction(context) {
  const envName = 'SKILLTREE_PRODUCTION_SMOKE_PASSWORD';
  const password = process.env[envName];
  assert(
    typeof password === 'string' && password.length > 0,
    `Missing GitHub Actions secret ${envName}. Add it under repository Settings → Secrets and variables → Actions; do not bypass production authentication.`
  );
  const origin = new URL(BASE_URL).origin;
  const response = await context.request.post(BASE_URL + '/api/auth/login', {
    data: { password },
    headers: {
      Accept: 'application/json',
      Origin: origin,
      Referer: origin + '/login.html',
    },
    timeout: 30000,
  });
  if (!response.ok()) {
    throw new Error(`Production smoke login failed with HTTP ${response.status()}.`);
  }
  const payload = await response.json().catch(() => ({}));
  assert(
    payload.authenticated === true,
    'Production smoke login did not return an authenticated session.'
  );
  return { authenticated: true, status: response.status() };
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 1,
  });
  report.checks.productionAuthentication = await authenticateProduction(context);
  const page = await context.newPage();
  // La page /lab.html peut être relue avant la fin d’un déploiement Render.
  // Désactiver le cache navigateur garantit qu’un sondage ultérieur recharge le nouveau /lab/main.js.
  const cdp = await context.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  await cdp.send('Network.setBypassServiceWorker', { bypass: true });
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
    // Après une fusion, Render peut déployer quelques instants après GitHub Actions.
    // On attend la version attendue via GET seulement; aucune écriture de production n'est faite.
    const readyDeadline = Date.now() + 8 * 60 * 1000;
    let ready = false;
    while (Date.now() < readyDeadline) {
      try {
        await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.getByRole('button', { name: 'Ouvrir les paramètres' }).waitFor({ state: 'visible', timeout: 25000 });
        const hasResponsiveHeader = await page.locator('header.app-main-header').count() === 1;
        await page.goto(BASE_URL + '/lab.html?demo=1&visual_probe=' + Date.now(), { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.getByText('Démo', { exact: true }).first().waitFor({ state: 'visible', timeout: 30000 });
        const equipmentCount = await page.locator('[data-testid^="equipment-model-"]').count();
        // The cable palette is mounted lazily only after its tab is selected.
        await page.getByRole('tab', { name: /Câbles/ }).click();
        const cableCount = await page.locator('[data-testid^="cable-item-"]').count();
        if (hasResponsiveHeader && equipmentCount >= 20 && cableCount >= 11) {
          report.checks.liveFixReady = { responsiveHeader: true, equipmentModels: equipmentCount, cableItems: cableCount };
          ready = true;
          break;
        }
      } catch (probeError) {
        report.checks.lastReadinessProbeError = String(probeError.message || probeError).slice(0, 240);
      }
      await page.waitForTimeout(10000);
    }
    if (!ready) {
      const readinessFailureShot = path.join(OUT, 'production-readiness-failure.png');
      await page.screenshot({ path: readinessFailureShot, fullPage: true, animations: 'disabled' }).catch(() => {});
      report.screenshots.push(readinessFailureShot);
    }
    assert(ready, 'Production did not expose the responsive header and expanded equipment/cable libraries within eight minutes.');

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
    report.checks.mobileHeaderLayout = await page.evaluate(() => {
      const header = document.querySelector('header.app-main-header');
      const title = header?.querySelector('h2');
      const trigger = header?.querySelector('.mobile-header-menu-trigger');
      if (!header || !title || !trigger) return { selectorFound: false, noOverlap: false, sameRow: false };
      const titleBox = title.getBoundingClientRect();
      const triggerBox = trigger.getBoundingClientRect();
      const headerBox = header.getBoundingClientRect();
      const titleCenter = titleBox.top + titleBox.height / 2;
      const triggerCenter = triggerBox.top + triggerBox.height / 2;
      return {
        selectorFound: true,
        titleRight: Math.round(titleBox.right),
        actionsLeft: Math.round(triggerBox.left),
        titleCenterY: Math.round(titleCenter),
        actionsCenterY: Math.round(triggerCenter),
        sameRow: Math.abs(titleCenter - triggerCenter) <= 14,
        noOverlap: titleBox.right <= triggerBox.left,
        headerContainsActions: triggerBox.bottom <= headerBox.bottom + 1,
      };
    });
    assert(report.checks.mobileHeaderLayout.noOverlap, 'Mobile dashboard title overlaps the actions dropdown button.');
    assert(report.checks.mobileHeaderLayout.sameRow, 'Mobile dashboard title and actions button are not aligned on the same row.');
    assert(report.checks.mobileHeaderLayout.headerContainsActions, 'Mobile actions dropdown button extends beyond the header.');
    const mobileShot = path.join(OUT, 'production-dashboard-mobile.png');
    await page.screenshot({ path: mobileShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(mobileShot);

    const actionsTrigger = page.locator('.mobile-header-menu-trigger');
    await actionsTrigger.click();
    const mobileActions = page.locator('#mobile-header-action-items');
    await mobileActions.waitFor({ state: 'visible', timeout: 5000 });
    const actionLabels = await mobileActions.locator('.mobile-action-label').allTextContents();
    for (const label of ['Rechercher un cours', 'Atelier libre', 'Thème', 'Notifications', 'Profil', 'Paramètres']) {
      const visibleLabel = mobileActions.locator('.mobile-action-label').filter({ hasText: label }).last();
      assert(actionLabels.some(item => item.trim() === label) && await visibleLabel.isVisible(), `Mobile actions dropdown is missing the visible "${label}" action.`);
    }
    report.checks.mobileActionsDropdown = {
      visible: await mobileActions.isVisible(),
      actionLabels: actionLabels.map(item => item.trim()),
    };
    const actionsShot = path.join(OUT, 'production-dashboard-mobile-actions.png');
    await page.screenshot({ path: actionsShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(actionsShot);
    await actionsTrigger.click();
    await mobileActions.waitFor({ state: 'hidden', timeout: 5000 });

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
    await labPage.getByText('Bibliothèque de câbles', { exact: true }).waitFor({ state: 'visible', timeout: 15000 });
    report.checks.cableLibraryTabVisible = await cableTab.isVisible();
    report.checks.cableLibraryBadge = (await cableTab.innerText()).trim();
    report.checks.cableTypeCount = await labPage.locator('[data-testid^="cable-item-"]').count();
    report.checks.physicalCableCount = await labPage.locator('[data-testid^="cable-item-"]:not([data-testid="cable-item-wireless"])').count();
    assert(report.checks.physicalCableCount >= 10, 'Cable library should render at least 10 distinct physical cable types.');
    assert(report.checks.cableTypeCount >= 11, 'Cable library should additionally render the wireless link option.');
    assert(await labPage.getByRole('region', { name: 'Liaisons sans fil' }).isVisible(), 'Wireless links must be separated from physical cables.');

    const workspaceCableShot = path.join(OUT, 'production-lab-workspace-cables.png');
    await labPage.screenshot({ path: workspaceCableShot, fullPage: true, animations: 'disabled' });
    report.screenshots.push(workspaceCableShot);

    report.checks.reactFlowNodeCount = await labPage.locator('.react-flow__node').count();
    report.checks.reactFlowEdgeCount = await labPage.locator('.react-flow__edge').count();
    assert(report.checks.reactFlowNodeCount > 0, 'Lab Workspace shows no React Flow equipment nodes');
    assert(
      report.checks.equipmentPaletteItemCount >= 20,
      `Equipment library currently exposes only ${report.checks.equipmentPaletteItemCount} draggable models; expected at least twenty.`
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
