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


test('le menu contextuel démarre la lecture vocale depuis la section visée', async ({ page }) => {
  await openDashboard(page);

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await searchInput.fill("Qu'est-ce qu'un réseau");
  const lessonResult = results.locator('button').filter({
    hasText: "Qu'est-ce qu'un réseau ? - Débutant",
  }).first();
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();

  const article = page.locator('[x-ref="lessonArticle"]');
  await expect(article).toBeVisible();
  const heading = article.locator('h2[id], h3[id], h4[id]').first();
  await expect(heading).toBeVisible();
  const headingId = await heading.getAttribute('id');
  const headingText = (await heading.innerText()).replace(/\s+/g, ' ').trim();

  // Garde le test indépendant du fournisseur audio et ne lance aucun flux réseau TTS.
  await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    state.playSpeechChunk = () => {};
  });

  await heading.click({ button: 'right' });
  const menu = page.getByRole('menu', { name: 'Options de lecture' });
  await expect(menu).toBeVisible();
  await expect(menu.getByText(headingText, { exact: true })).toBeVisible();
  await menu.getByRole('menuitem', { name: 'Lire à ce niveau' }).click();

  await expect(menu).toBeHidden();
  const speech = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return {
      start: state.startSectionSelection,
      kind: state.speechKind,
      status: state.speechState,
      text: state.speechQueue.join(' '),
    };
  });
  expect(speech.start).toBe(headingId);
  expect(speech.kind).toBe('lesson');
  expect(speech.status).toBe('starting');
  expect(speech.text).toContain(headingText);
  await expect(page.getByRole('group', { name: 'Commandes flottantes de lecture vocale' })).toBeVisible();
});

test('les commandes vocales flottantes permettent pause, reprise et arrêt', async ({ page }) => {
  await openDashboard(page);

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await searchInput.fill("Qu'est-ce qu'un réseau");
  const lessonResult = results.locator('button').filter({
    hasText: "Qu'est-ce qu'un réseau ? - Débutant",
  }).first();
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();
  await expect(page.locator('[x-ref="lessonArticle"]')).toBeVisible();

  await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    state.speechKind = 'lesson';
    state.speechEngine = 'server';
    state.speechQueue = ['texte de test'];
    state.speechQueueIndex = 0;
    state.speechState = 'speaking';
    state.playSpeechChunk = function () { this.speechState = 'speaking'; };
  });

  const controls = page.getByRole('group', { name: 'Commandes flottantes de lecture vocale' });
  await expect(controls).toBeVisible();
  const pause = controls.getByRole('button', { name: 'Mettre en pause la lecture vocale' });
  await pause.click();
  await expect(controls.getByRole('button', { name: 'Reprendre la lecture vocale' })).toBeVisible();
  await expect(controls.getByText('Lecture en pause')).toBeVisible();

  await controls.getByRole('button', { name: 'Reprendre la lecture vocale' }).click();
  await expect(controls.getByRole('button', { name: 'Mettre en pause la lecture vocale' })).toBeVisible();

  await controls.getByRole('button', { name: 'Arrêter la lecture vocale' }).click();
  await expect(controls).toBeHidden();
});
