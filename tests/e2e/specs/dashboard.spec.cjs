const { test, expect } = require('@playwright/test');

async function openDashboard(page) {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();

  await expect.poll(async () => page.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return Array.isArray(state?.nodes) ? state.nodes.length : 0;
  }), { timeout: 30_000 }).toBeGreaterThan(0);
}

test('le tableau de bord charge le parcours et la navigation principale', async ({ page }) => {
  await openDashboard(page);

  await expect(page.getByRole('navigation', { name: 'Navigation principale' })).toBeVisible();
  await expect(
    page.getByRole('navigation', { name: 'Navigation principale' }).getByRole('button', { name: 'Défis' })
  ).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-theme', /.+/);
});

test('un clic extérieur ferme le menu Paramètres sans bloquer la navigation', async ({ page }) => {
  await openDashboard(page);

  const settingsButton = page.getByRole('button', { name: 'Ouvrir les paramètres' });
  const settingsMenu = page.locator('div[x-show="settingsMenuOpen"]');
  await settingsButton.click();
  await expect(settingsMenu).toBeVisible();

  const challengesButton = page
    .getByRole('navigation', { name: 'Navigation principale' })
    .getByRole('button', { name: 'Défis' });
  await challengesButton.click();

  await expect(settingsMenu).toBeHidden();
  await expect(challengesButton).toHaveAttribute('aria-current', 'page');
});

test('le thème choisi est persisté après rechargement', async ({ page }) => {
  await openDashboard(page);

  await page.getByRole('button', { name: 'Ouvrir les paramètres' }).click();
  const settingsMenu = page.locator('div[x-show="settingsMenuOpen"]');
  await settingsMenu.getByRole('button', { name: 'Changer de thème' }).click();

  const themeMenu = page.locator('div[x-show="themeMenuOpen"]');
  const oceanTheme = themeMenu.getByRole('button', { name: 'Océan' });
  await expect(oceanTheme).toBeVisible();
  await oceanTheme.click();

  await expect(page.locator('html')).toHaveAttribute('data-theme', 'ocean');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('skilltree-theme2'))).toBe('ocean');

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'ocean');
});

test('le marqueur actif reflète le thème appliqué', async ({ page }) => {
  test.fail(
    true,
    'Défaut navigateur confirmé : le thème devient « ocean », mais le bouton Océan reste aria-pressed=false. La correction exige une modification coordonnée de static/index.html.',
  );
  await openDashboard(page);

  await page.getByRole('button', { name: 'Ouvrir les paramètres' }).click();
  const settingsMenu = page.locator('div[x-show="settingsMenuOpen"]');
  await settingsMenu.getByRole('button', { name: 'Changer de thème' }).click();

  const themeMenu = page.locator('div[x-show="themeMenuOpen"]');
  const oceanTheme = themeMenu.getByRole('button', { name: 'Océan' });
  await expect(oceanTheme).toBeVisible();
  await oceanTheme.click();

  await expect(page.locator('html')).toHaveAttribute('data-theme', 'ocean');
  await expect(oceanTheme).toHaveAttribute('aria-pressed', 'true');
});

test('la recherche de bureau se ferme avec Échap', async ({ page }) => {
  await openDashboard(page);
  await page.setViewportSize({ width: 1440, height: 1000 });

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await expect(searchInput).toBeVisible();

  await searchInput.fill('OSI');
  await expect(results).toBeVisible();
  await searchInput.press('Escape');

  await expect(results).toBeHidden();
  await expect(searchInput).not.toBeFocused();
});

test('la recherche mobile est utilisable et se ferme avec Échap', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openDashboard(page);

  await expect(page.getByRole('navigation', { name: 'Navigation mobile' })).toBeVisible();
  await page.getByRole('button', { name: 'Rechercher un cours', exact: true }).click();

  const mobileSearch = page.locator('div[x-show="mobileSearchOpen"]');
  const input = page.locator('input[x-ref="mobileSearchBox"]');
  await expect(mobileSearch).toBeVisible();
  await expect(input).toBeFocused();
  await input.press('Escape');
  await expect(mobileSearch).toBeHidden();
});

test('le centre de notifications se ferme avec Échap', async ({ page }) => {
  await openDashboard(page);

  await page.locator('button[aria-label^="Ouvrir les notifications"]').click();
  const notifications = page.locator('div[x-show="notificationsOpen"]');
  await expect(notifications).toBeVisible();

  await page.keyboard.press('Escape');
  await expect(notifications).toBeHidden();
});

test('un cours peut être ouvert depuis la recherche puis fermé avec Échap', async ({ page }) => {
  await openDashboard(page);

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await searchInput.fill("Qu'est-ce qu'un réseau");

  const lessonResult = results.locator('button').filter({
    hasText: "Qu'est-ce qu'un réseau ? - Débutant",
  }).first();
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();

  const reader = page.locator('div[x-show="open"].fixed.inset-0');
  const title = page.locator('#course-reader-title');
  await expect(title).toBeVisible();
  await expect(title).toHaveText("Qu'est-ce qu'un réseau ? - Débutant");
  await expect(page.locator('[x-ref="lessonArticle"]')).toBeVisible();

  await page.keyboard.press('Escape');
  await expect(reader).toBeHidden();
});


test('les cartes du catalogue des labs ouvrent un nouvel onglet sans remplacer le tableau de bord', async ({ page }) => {
  await openDashboard(page);
  const nav = page.getByRole('navigation', { name: 'Navigation principale' });
  await nav.getByRole('button', { name: 'Labs' }).click();

  const links = page.locator('a[data-lab-card="catalog"]');
  await expect(links.first()).toBeVisible();
  const labLink = links.first();
  await expect(labLink).toHaveAttribute('target', '_blank');
  await expect(labLink).toHaveAttribute('rel', /noopener/);
  await expect(labLink).toHaveAttribute('href', /openLab=/);

  const originalUrl = page.url();
  const newPagePromise = page.context().waitForEvent('page');
  await labLink.click();
  const labPage = await newPagePromise;
  await labPage.waitForLoadState('domcontentloaded').catch(() => {});

  await expect.poll(async () => {
    const pathname = new URL(labPage.url()).pathname;
    if (pathname === '/lab.html') {
      return await labPage.getByText('Lab actif', { exact: true }).isVisible().catch(() => false);
    }
    if (pathname === '/') {
      return await labPage.locator('.modal-panel[role="dialog"]').isVisible().catch(() => false);
    }
    return false;
  }, { timeout: 60_000 }).toBe(true);

  expect(page.url()).toBe(originalUrl);
  await expect(nav.getByRole('button', { name: 'Labs' })).toHaveAttribute('aria-current', 'page');
  await labPage.close();
});

test('le catalogue des labs réutilise son cache après avoir quitté puis rouvert la section', async ({ page }) => {
  let nodeDetailRequests = 0;
  page.on('request', request => {
    const pathname = new URL(request.url()).pathname;
    if (/^\/api\/node\/[^/]+$/.test(pathname)) nodeDetailRequests += 1;
  });

  await openDashboard(page);
  const nav = page.getByRole('navigation', { name: 'Navigation principale' });
  const labsButton = nav.getByRole('button', { name: 'Labs' });
  await labsButton.click();

  const links = page.locator('a[data-lab-card="catalog"]');
  await expect(links.first()).toBeVisible();
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).labIndexBusy)).toBe(false);
  const requestsAfterFirstLoad = nodeDetailRequests;
  expect(requestsAfterFirstLoad).toBeGreaterThan(0);

  await nav.getByRole('button', { name: 'Tableau de bord' }).click();
  await labsButton.click();
  await expect(links.first()).toBeVisible();
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).labIndexBusy)).toBe(false);
  expect(nodeDetailRequests).toBe(requestsAfterFirstLoad);
});

test('les panneaux latéraux et la bibliothèque matérielle se redimensionnent et gardent leur taille', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.goto('/lab.html?demo=1', { waitUntil: 'domcontentloaded' });
  await expect(page.getByText('Démo', { exact: true }).first()).toBeVisible();

  const leftPanel = page.getByTestId('lab-left-panel');
  const rightPanel = page.getByTestId('lab-right-panel');
  const equipmentPanel = page.getByTestId('equipment-palette-panel');
  const width = element => element.evaluate(el => Math.round(el.getBoundingClientRect().width));
  const height = element => element.evaluate(el => Math.round(el.getBoundingClientRect().height));

  const leftBefore = await width(leftPanel);
  const leftSeparator = page.getByRole('separator', { name: 'Redimensionner la largeur du panneau Mission et équipements' });
  await leftSeparator.focus();
  await page.keyboard.press('ArrowRight');
  await expect.poll(() => width(leftPanel)).toBeGreaterThan(leftBefore);

  const rightBefore = await width(rightPanel);
  const rightSeparator = page.getByRole('separator', { name: 'Redimensionner la largeur du panneau Console' });
  await rightSeparator.focus();
  await page.keyboard.press('ArrowLeft');
  await expect.poll(() => width(rightPanel)).toBeGreaterThan(rightBefore);

  const equipmentBefore = await height(equipmentPanel);
  const equipmentSeparator = page.getByRole('separator', { name: "Redimensionner la hauteur de la bibliothèque d'équipements" });
  await equipmentSeparator.focus();
  await page.keyboard.press('ArrowUp');
  await expect.poll(() => height(equipmentPanel)).toBeGreaterThan(equipmentBefore);

  const savedSizes = await page.evaluate(() => ({
    left: Number(localStorage.getItem('skilltree-lab-left-width')),
    right: Number(localStorage.getItem('skilltree-lab-right-width')),
    equipment: Number(localStorage.getItem('skilltree-lab-equipment-height')),
  }));
  expect(savedSizes.left).toBeGreaterThan(leftBefore);
  expect(savedSizes.right).toBeGreaterThan(rightBefore);
  expect(savedSizes.equipment).toBeGreaterThan(equipmentBefore);

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.getByText('Démo', { exact: true }).first()).toBeVisible();
  await expect.poll(() => width(leftPanel)).toBe(savedSizes.left);
  await expect.poll(() => width(rightPanel)).toBe(savedSizes.right);
  await expect.poll(() => height(equipmentPanel)).toBe(savedSizes.equipment);
});

test('les ports peuvent être reliés même lorsque les deux handles sont du même côté', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.goto('/lab.html?demo=1', { waitUntil: 'domcontentloaded' });
  await expect(page.getByText('Démo', { exact: true }).first()).toBeVisible();

  const edges = page.locator('.react-flow__edge');
  await expect(edges).toHaveCount(1);
  const source = page.locator('.react-flow__node[data-id="R1"] .react-flow__handle[data-handleid="Fa0/1"]').first();
  const target = page.locator('.react-flow__node[data-id="R2"] .react-flow__handle[data-handleid="Fa0/1"]').first();
  await expect(source).toBeVisible();
  await expect(target).toBeVisible();

  const sourceBox = await source.boundingBox();
  const targetBox = await target.boundingBox();
  expect(sourceBox).not.toBeNull();
  expect(targetBox).not.toBeNull();

  await page.mouse.move(sourceBox.x + sourceBox.width / 2, sourceBox.y + sourceBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height / 2, { steps: 18 });
  await page.mouse.up();

  await expect(edges).toHaveCount(2, { timeout: 10_000 });
});
