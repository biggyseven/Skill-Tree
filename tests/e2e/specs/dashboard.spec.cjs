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

test('les préférences du centre de paramètres s’appliquent et persistent après rechargement', async ({ page }) => {
  await openDashboard(page);

  const settingsButton = page.getByRole('button', { name: 'Ouvrir les paramètres' });
  await settingsButton.click();
  const settings = page.locator('div[x-show="settingsMenuOpen"]');
  await expect(settings).toBeVisible();
  await expect(settings.getByText('Centre de préférences')).toBeVisible();

  await settings.getByRole('checkbox', { name: 'Interface compacte' }).check();
  await expect(page.locator('body')).toHaveClass(/compact-ui/);
  await expect.poll(() => page.evaluate(() => {
    const saved = JSON.parse(localStorage.getItem('skilltree-settings-v1') || '{}');
    return saved.compactUi;
  })).toBe(true);

  await settings.getByRole('checkbox', { name: 'Réduire les animations' }).check();
  await expect(page.locator('html')).toHaveClass(/reduce-motion/);
  await expect.poll(() => page.evaluate(() => {
    const saved = JSON.parse(localStorage.getItem('skilltree-settings-v1') || '{}');
    return saved.reduceMotion;
  })).toBe(true);

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();
  await expect(page.locator('body')).toHaveClass(/compact-ui/);
  await expect(page.locator('html')).toHaveClass(/reduce-motion/);

  await settingsButton.click();
  const reopenedSettings = page.locator('div[x-show="settingsMenuOpen"]');
  await expect(reopenedSettings).toBeVisible();
  await reopenedSettings.getByRole('button', { name: 'Agrandir la taille du texte' }).click();
  await expect.poll(() => page.evaluate(() => JSON.parse(localStorage.getItem('skilltree-ui') || '{}').fs)).toBe(18);

  await reopenedSettings.getByRole('button', { name: 'Rétablir les préférences d’affichage' }).click();
  await expect(reopenedSettings).toBeHidden();
  await expect(page.locator('body')).not.toHaveClass(/compact-ui/);
  await expect(page.locator('html')).not.toHaveClass(/reduce-motion/);
  await expect.poll(() => page.evaluate(() => JSON.parse(localStorage.getItem('skilltree-ui') || '{}').fs)).toBe(17);
  await expect.poll(() => page.evaluate(() => localStorage.getItem('skilltree-theme2'))).toBe('graphite');
});

test('l’export des données depuis Paramètres déclenche le téléchargement JSON', async ({ page }) => {
  await openDashboard(page);

  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.getByRole('button', { name: 'Ouvrir les paramètres' }).click();
  const settings = page.locator('div[x-show="settingsMenuOpen"]');
  await expect(settings).toBeVisible();

  await page.evaluate(() => {
    const probe = window.__skilltreeDownloadProbe = { objectUrlCalls: 0, blobs: [], anchorClicks: [], errors: [] };
    const nativeCreateObjectURL = URL.createObjectURL.bind(URL);
    URL.createObjectURL = function (blob) {
      probe.objectUrlCalls += 1;
      probe.blobs.push({ isBlob: blob instanceof Blob, size: Number(blob?.size) || 0, type: String(blob?.type || '') });
      try { return nativeCreateObjectURL(blob); }
      catch (error) { probe.errors.push('createObjectURL: ' + String(error?.message || error)); throw error; }
    };
    const nativeAnchorClick = HTMLAnchorElement.prototype.click;
    HTMLAnchorElement.prototype.click = function () {
      if (this.download) probe.anchorClicks.push({
        download: this.download, href: this.href, connected: this.isConnected,
        display: getComputedStyle(this).display, visibility: getComputedStyle(this).visibility,
      });
      try { return nativeAnchorClick.call(this); }
      catch (error) { probe.errors.push('anchor.click: ' + String(error?.message || error)); throw error; }
    };
    window.addEventListener('error', event => probe.errors.push(String(event.message || 'window error')));
  });

  const downloads = [];
  page.on('download', download => downloads.push(download));
  await settings.getByRole('button', { name: /Exporter mes données/ }).click();
  await page.waitForTimeout(1000);
  const probe = await page.evaluate(() => window.__skilltreeDownloadProbe || null);
  const debug = JSON.stringify({ probe, pageErrors }, null, 2);

  expect(probe, debug).toBeTruthy();
  expect(probe.objectUrlCalls, debug).toBe(1);
  expect(probe.blobs[0]?.size || 0, debug).toBeGreaterThan(0);
  expect(probe.anchorClicks.length, debug).toBe(1);
  expect(downloads.length, debug).toBe(1);

  const download = downloads[0];
  expect(download.suggestedFilename()).toMatch(/^skilltree-sauvegarde-[0-9]{4}-[0-9]{2}-[0-9]{2}[.]json$/);
  const filePath = await download.path();
  expect(filePath).toBeTruthy();
  const snapshot = JSON.parse(await require('node:fs/promises').readFile(filePath, 'utf8'));
  expect(snapshot.app).toBe('Skill-Tree');
  expect(snapshot.schema_version).toBe(2);
  expect(snapshot.preferences).toMatchObject({
    font_size: expect.any(Number),
    reading_width: expect.stringMatching(/^(comfortable|wide)$/),
    compact_ui: expect.any(Boolean),
    reduce_motion: expect.any(Boolean),
  });
  expect(snapshot.local_data).toBeTruthy();
  await expect(settings).toBeHidden();
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


test('la navigation du lecteur respecte l’ordre pédagogique et contextualise la leçon suivante', async ({ page }) => {
  await openDashboard(page);

  const orderedIds = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    const originalNodes = state.nodes;
    // Simulate a persistent DB whose sort_order is stale and contradicts nodes.json.
    state.nodes = [...originalNodes].reverse().map((node, index) => ({
      ...node,
      sort_order: -1 * Number(node.order ?? index + 1),
    }));
    const ordered = state.lessonSequence.slice(0, 3).map(node => node.id);
    state.nodes = originalNodes;
    return ordered;
  });
  expect(orderedIds).toEqual([
    'intro-reseau-debutant',
    'intro-reseau-intermediaire',
    'intro-reseau-expert',
  ]);

  await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    await state.show('intro-reseau-debutant');
  });

  await expect(page.locator('#course-reader-title')).toHaveText("Qu'est-ce qu'un réseau ? - Débutant");
  const navigation = page.getByRole('region', { name: 'Navigation entre les leçons' });
  await expect(navigation).toBeVisible();
  await expect(navigation.getByText('Début du module', { exact: true })).toBeVisible();
  await expect(navigation.getByText('Étape 1 sur', { exact: false })).toBeVisible();

  const nextLesson = navigation.getByRole('button', {
    name: /Ouvrir la leçon suivante.*Qu'est-ce qu'un réseau.*Intermédiaire/,
  });
  await expect(nextLesson).toBeVisible();
  await expect(nextLesson).toContainText('Intermédiaire');
  await nextLesson.click();

  await expect(page.locator('#course-reader-title')).toHaveText("Qu'est-ce qu'un réseau ? - Intermédiaire");
  await expect(navigation.getByRole('button', {
    name: /Ouvrir la leçon précédente.*Qu'est-ce qu'un réseau.*Débutant/,
  })).toBeVisible();
  await expect(navigation.getByText('Étape 2 sur', { exact: false })).toBeVisible();
});

test('la navigation du lecteur reste dans le module sélectionné, même quand les ordres se chevauchent entre modules', async ({ page }) => {
  await openDashboard(page);

  const firstCourseId = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    state.setModule('cybersecurite');
    return state.moduleNextCourseId;
  });
  expect(firstCourseId).toBe('secu-cia-debutant');

  const networkTieOrder = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return state.orderedModuleLessons('admin-reseaux').map(node => node.id);
  });
  expect(networkTieOrder.indexOf('wireshark-debutant')).toBe(
    networkTieOrder.indexOf('incident-ospf') + 1,
  );

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const searchResults = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await searchInput.fill('La Triade CIA');
  const firstCourseResult = searchResults.locator('button').filter({ hasText: 'La Triade CIA' }).first();
  await expect(firstCourseResult).toBeVisible();
  await firstCourseResult.click();

  await expect(page.locator('#course-reader-title')).toHaveText('La Triade CIA');
  const navigation = page.getByRole('region', { name: 'Navigation entre les leçons' });
  await expect(navigation).toBeVisible();
  // Le nombre de cours du module évolue avec le catalogue ; vérifier l'étape et le module,
  // sans figer le compteur total dans un test de navigation.
  await expect(navigation.getByText(/Étape 1 sur \d+ · (Cyber|Cybersécurité)/)).toBeVisible();

  const nextLesson = navigation.getByRole('button', {
    name: /Ouvrir la leçon suivante.*Panorama des menaces/,
  });
  await expect(nextLesson).toBeVisible();
  await expect(nextLesson).not.toContainText(/Wireshark/);
  await nextLesson.click();

  await expect(page.locator('#course-reader-title')).toHaveText('Panorama des menaces');
  await expect(navigation.getByRole('button', {
    name: /Ouvrir la leçon précédente.*La Triade CIA/,
  })).toBeVisible();
  await expect(navigation.getByRole('button', {
    name: /Ouvrir la leçon suivante.*Cryptographie/,
  })).toBeVisible();

  const navigationState = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return {
      module: state.lessonNavigationModule,
      previous: state.lessonNeighbors.prev?.id || null,
      next: state.lessonNeighbors.next?.id || null,
      sequenceLength: state.lessonSequence.length,
      currentIndex: state.lessonCurrentIndex,
      wiresharkIndex: state.lessonSequence.findIndex(node => node.id === 'wireshark-debutant'),
    };
  });
  expect(navigationState.module).toBe('cybersecurite');
  expect(navigationState.previous).toBe('secu-cia-debutant');
  expect(navigationState.next).toBe('secu-crypto-debutant');
  expect(navigationState.sequenceLength).toBeGreaterThan(1);
  expect(navigationState.currentIndex).toBe(2);
  expect(navigationState.wiresharkIndex).toBe(-1);
});

test('un cours cybersécurité complet affiche son contenu dans le lecteur', async ({ page }) => {
  await openDashboard(page);

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await searchInput.fill('Analyse de malwares');

  const lessonResult = results.locator('button').filter({ hasText: 'Analyse de malwares' }).first();
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();

  await expect(page.locator('#course-reader-title')).toHaveText('Analyse de malwares');
  await expect(page.locator('#lesson-preparation-title')).toBeHidden();
  const article = page.locator('[x-ref="lessonArticle"]');
  await expect(article).toHaveCount(1);
  await expect(article).toContainText('Mise en contexte');
  await expect(article).toContainText('préserver les preuves');
  await expect(page.getByText(/Contenu de 5000 mots à rédiger/i)).toHaveCount(0);
});

test('les sections de sidebar, les modules et les cours peuvent s’ouvrir dans un nouvel onglet', async ({ page }) => {
  await openDashboard(page);

  const waitForReadyPage = async (otherPage) => {
    await otherPage.waitForLoadState('domcontentloaded');
    await expect(otherPage.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();
    await expect.poll(async () => otherPage.evaluate(() => {
      const state = window.Alpine && window.Alpine.$data(document.body);
      return Array.isArray(state?.nodes) ? state.nodes.length : 0;
    }), { timeout: 30_000 }).toBeGreaterThan(0);
  };

  const nav = page.getByRole('navigation', { name: 'Navigation principale' });
  const sectionLink = nav.locator('a[href*="openTab=challenges"]');
  await expect(sectionLink).toBeVisible();
  await expect(sectionLink).toHaveAttribute('target', '_blank');
  const sectionPagePromise = page.context().waitForEvent('page');
  await sectionLink.click();
  const sectionPage = await sectionPagePromise;
  await waitForReadyPage(sectionPage);
  await expect.poll(() => sectionPage.evaluate(() => window.Alpine.$data(document.body).tab)).toBe('challenges');
  await sectionPage.close();

  const moduleLink = page.locator('a[aria-label^="Ouvrir le module "][href*="openModule="]').nth(1);
  await expect(moduleLink).toBeVisible();
  await expect(moduleLink).toHaveAttribute('target', '_blank');
  const moduleId = new URL(await moduleLink.getAttribute('href'), 'http://localhost').searchParams.get('openModule');
  const modulePagePromise = page.context().waitForEvent('page');
  await moduleLink.click();
  const modulePage = await modulePagePromise;
  await waitForReadyPage(modulePage);
  await expect.poll(() => modulePage.evaluate(() => window.Alpine.$data(document.body).moduleFilter)).toBe(moduleId);
  const expectedFirstCourse = await modulePage.evaluate((id) => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.nodes?.find(node => state.moduleOf(node) === id)?.id || null;
  }, moduleId);
  expect(expectedFirstCourse).toBeTruthy();
  await expect.poll(() => modulePage.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.moduleNextCourseId || null;
  }), { timeout: 30_000 }).toBe(expectedFirstCourse);
  await expect.poll(() => modulePage.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.resumeNode?.id || null;
  }), { timeout: 30_000 }).toBe(expectedFirstCourse);
  await expect.poll(() => modulePage.evaluate(() => !!window.Alpine.$data(document.body).open)).toBe(false);
  await expect(modulePage.locator('.modal-panel[role="dialog"]')).toBeHidden();
  await modulePage.close();

  const courseLink = page.locator('a[aria-label^="Ouvrir le cours "][href*="openCourse="]').first();
  await expect(courseLink).toBeVisible();
  await expect(courseLink).toHaveAttribute('target', '_blank');
  const courseId = new URL(await courseLink.getAttribute('href'), 'http://localhost').searchParams.get('openCourse');
  const coursePagePromise = page.context().waitForEvent('page');
  await courseLink.click();
  const coursePage = await coursePagePromise;
  await waitForReadyPage(coursePage);
  await expect.poll(() => coursePage.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.open && state?.detail?.id ? state.detail.id : null;
  }), { timeout: 30_000 }).toBe(courseId);
  await coursePage.close();
});

test('changer de module propose le premier cours sans l’ouvrir automatiquement', async ({ page }) => {
  await openDashboard(page);

  // Lier le bouton d’un module à son propre lien d’ouverture évite de dépendre
  // d’autres boutons portant le même libellé accessible dans le tableau de bord.
  const moduleLink = page.locator('a[aria-label^="Ouvrir le module "][href*="openModule="]').nth(1);
  const moduleId = new URL(await moduleLink.getAttribute('href'), 'http://localhost').searchParams.get('openModule');
  const firstCourse = await page.evaluate((id) => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    const node = state?.nodes?.find(item => state.moduleOf(item) === id);
    return node ? { id: node.id, title: node.title } : null;
  }, moduleId);
  expect(firstCourse).toBeTruthy();

  await moduleLink.locator('xpath=..').getByRole('button').click();

  await expect.poll(() => page.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.moduleNextCourseId || null;
  }), { timeout: 30_000 }).toBe(firstCourse.id);
  await expect.poll(() => page.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.resumeNode?.id || null;
  }), { timeout: 30_000 }).toBe(firstCourse.id);
  await expect.poll(() => page.evaluate(() => !!window.Alpine.$data(document.body).open)).toBe(false);
  await expect(page.locator('.modal-panel[role="dialog"]')).toBeHidden();
  await expect(page.getByRole('heading', { name: firstCourse.title, exact: true }).first()).toBeVisible();
});

test('les cartes ouvrent directement le workspace v2 et identifient les labs historiques', async ({ page }) => {
  await openDashboard(page);
  const nav = page.getByRole('navigation', { name: 'Navigation principale' });
  await nav.getByRole('button', { name: 'Labs' }).click();

  const links = page.locator('a[data-lab-card="catalog"]');
  await expect(links.first()).toBeVisible();
  await expect.poll(
    () => page.evaluate(() => window.Alpine.$data(document.body).labIndexTask === null),
    { timeout: 45_000 },
  ).toBe(true);

  const originalUrl = page.url();
  const workspaceLinks = page.locator('a[data-lab-card="catalog"][data-lab-kind="workspace-v2"]');
  await expect(workspaceLinks.first()).toBeVisible();
  const workspaceLink = workspaceLinks.first();
  await expect(workspaceLink).toHaveAttribute('target', '_blank');
  await expect(workspaceLink).toHaveAttribute('rel', /noopener/);
  await expect(workspaceLink).toHaveAttribute('href', /\/lab\.html\?id=/);

  const workspacePagePromise = page.context().waitForEvent('page');
  await workspaceLink.click();
  const workspacePage = await workspacePagePromise;
  await workspacePage.waitForLoadState('domcontentloaded').catch(() => {});
  await expect(workspacePage).toHaveURL(/\/lab\.html\?id=/);
  await expect(workspacePage.getByText('Lab actif', { exact: true })).toBeVisible({ timeout: 60_000 });
  expect(page.url()).toBe(originalUrl);
  await expect(nav.getByRole('button', { name: 'Labs' })).toHaveAttribute('aria-current', 'page');
  await workspacePage.close();

  const legacyLinks = page.locator('a[data-lab-card="catalog"][data-lab-kind="legacy"]');
  if (await legacyLinks.count()) {
    const legacyLink = legacyLinks.first();
    await expect(legacyLink).toHaveAttribute('href', /\/\?openLab=/);
    const legacyPagePromise = page.context().waitForEvent('page');
    await legacyLink.click();
    const legacyPage = await legacyPagePromise;
    await legacyPage.waitForLoadState('domcontentloaded').catch(() => {});
    await expect(legacyPage.locator('.modal-panel[role="dialog"]')).toBeVisible({ timeout: 60_000 });
    // Le mode classique est un repli explicite : aucun bouton ne renvoie en boucle
    // vers un workspace visuel absent.
    await expect(legacyPage.getByText(/Ce laboratoire utilise actuellement le mode classique/)).toBeVisible();
    await expect(legacyPage.getByRole('button', { name: /Workspace visuel indisponible|Ouvrir le Lab Workspace/ })).toHaveCount(0);
    await legacyPage.close();
  }
});

test('le catalogue v2 affiche le lab ACL même si le nœud manque dans le graphe SQLite', async ({ page }) => {
  await page.route('**/api/tree', async route => {
    const response = await route.fetch();
    const payload = await response.json();
    if (Array.isArray(payload.nodes)) {
      payload.nodes = payload.nodes.filter(node => node.id !== 'secu-acl-intermediaire');
    }
    await route.fulfill({ response, body: JSON.stringify(payload) });
  });

  await page.route('**/api/lab/v2', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{
      id: 'secu-acl-intermediaire',
      title: 'ACL et filtrage avancé',
      level: 'intermédiaire',
      module: 'Cybersécurité',
      duration_min: 20,
      difficulty: 'intermédiaire',
      schema_version: 2,
    }]),
  }));

  await openDashboard(page);
  const nav = page.getByRole('navigation', { name: 'Navigation principale' });
  await nav.getByRole('button', { name: 'Labs' }).click();

  const aclLab = page.locator('a[data-lab-card="catalog"]').filter({
    hasText: 'ACL et filtrage avancé',
  }).first();
  await expect(aclLab).toBeVisible();
  await expect(aclLab).toHaveAttribute('data-lab-kind', 'workspace-v2');
  await expect(aclLab).toHaveAttribute('href', '/lab.html?id=secu-acl-intermediaire');
  await expect(aclLab).toContainText('⏱ 20 · intermédiaire');
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
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).labIndexTask === null), { timeout: 45_000 }).toBe(true);
  const requestsAfterFirstLoad = nodeDetailRequests;
  expect(requestsAfterFirstLoad).toBeGreaterThan(0);
  const courseCount = await page.evaluate(() => window.Alpine.$data(document.body).nodes.length);
  expect(requestsAfterFirstLoad).toBeLessThan(courseCount);

  await nav.getByRole('button', { name: 'Tableau de bord' }).click();
  await labsButton.click();
  await expect(links.first()).toBeVisible();
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).labIndexTask === null), { timeout: 45_000 }).toBe(true);
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
  const leftSeparator = page.getByRole('separator', { name: 'Redimensionner le panneau gauche' });
  await leftSeparator.focus();
  await page.keyboard.press('ArrowRight');
  await expect.poll(() => width(leftPanel)).toBeGreaterThan(leftBefore);

  const rightBefore = await width(rightPanel);
  const rightSeparator = page.getByRole('separator', { name: 'Redimensionner le panneau droit' });
  await rightSeparator.focus();
  await page.keyboard.press('ArrowLeft');
  await expect.poll(() => width(rightPanel)).toBeGreaterThan(rightBefore);

  const equipmentBefore = await height(equipmentPanel);
  const equipmentSeparator = page.getByRole('separator', { name: "Redimensionner les bibliothèques d’équipements et de câbles" });
  await equipmentSeparator.focus();
  await page.keyboard.press('ArrowUp');
  await expect.poll(() => height(equipmentPanel)).toBeGreaterThan(equipmentBefore);

  const savedSizes = await page.evaluate(() => ({
    left: Number(JSON.parse(localStorage.getItem('skilltree-lab-panel-sizes') || '{}').left),
    right: Number(JSON.parse(localStorage.getItem('skilltree-lab-panel-sizes') || '{}').right),
    equipment: Number(JSON.parse(localStorage.getItem('skilltree-lab-panel-sizes') || '{}').equipment),
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

  const edges = page.locator('.react-flow__edge-path');
  await expect(edges).toHaveCount(1);
  const source = page.locator('.react-flow__node[data-id="R1"] .react-flow__handle.source[data-handleid="Fa0/1::source"]').first();
  const target = page.locator('.react-flow__node[data-id="R2"] .react-flow__handle.target[data-handleid="Fa0/1::target"]').first();
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

test('la lecture vocale raconte les tableaux, les schémas ASCII et les relations Mermaid', async ({ page }) => {
  await openDashboard(page);
  await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    await state.show('linux-expert');
    state.startSectionSelection = '__top__';
    const article = state.$refs.lessonArticle;
    article.innerHTML = `
      <h1 id="voice-visual-test">Lecture des représentations</h1>
      <p>Les représentations suivantes résument l’architecture.</p>
      <div class="lesson-diagram-block" data-diagram-type="tableau">
        <table>
          <caption>Ports réseau</caption>
          <thead><tr><th>Protocole</th><th>Port</th><th>Usage</th></tr></thead>
          <tbody>
            <tr><td>HTTPS</td><td>443</td><td>Web chiffré</td></tr>
            <tr><td>DNS</td><td>53</td><td>Résolution de noms</td></tr>
          </tbody>
        </table>
        <div class="lesson-diagram-guide"><p>Texte guide qui ne doit pas remplacer les données.</p></div>
      </div>
      <div class="lesson-diagram-block" data-diagram-type="schéma textuel">
        <div class="code-container">
          <div class="code-header"><span class="code-lang">ASCII</span><button>Copier</button></div>
          <pre><code>Client --> Serveur
Serveur --> Base de données</code></pre>
        </div>
        <div class="lesson-diagram-guide"><p>Guide générique du schéma.</p></div>
      </div>
      <div class="lesson-diagram-block" data-diagram-type="schéma textuel">
        <div class="code-container">
          <div class="code-header"><span class="code-lang">ASCII</span></div>
          <pre><code>| Protocol | Port |
|----------|------|
| HTTP     | 80   |
| HTTPS    | 443  |</code></pre>
        </div>
      </div>
      <div class="lesson-diagram-block" data-diagram-type="schéma HTML">
        <div class="flow-node">Client</div><span>→</span><div class="flow-node">Passerelle</div>
        <div class="lesson-diagram-guide"><p>Guide HTML générique à ne pas lire à la place des éléments.</p></div>
      </div>
      <div class="lesson-diagram-block" data-diagram-type="schéma textuel">
        <div class="code-container">
          <div class="code-header"><span class="code-lang">ASCII</span></div>
          <pre><code>Poste de travail
  |
  v
Routeur
  |
  ^
Poste de secours</code></pre>
        </div>
      </div>
      <div class="lesson-diagram-block" data-diagram-type="diagramme Mermaid">
        <div class="mermaid"></div>
      </div>
    `;
    article.querySelector('.mermaid').dataset.originalSource =
      'flowchart LR\nA[Client] -->|HTTPS| B[API]\nB --> C[Base de données]';
  });

  const narration = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return state.speechTextFromArticle();
  });

  expect(narration).toContain('Tableau : Ports réseau.');
  expect(narration).toContain('Les colonnes présentent un élément de référence');
  expect(narration).toContain('Pour HTTPS, le port utilisé est 443');
  expect(narration).toContain('l’usage indiqué est « Web chiffré »');
  expect(narration).toContain('Pour DNS, le port utilisé est 53');
  expect(narration).toContain('l’usage indiqué est « Résolution de noms »');
  expect(narration).toContain('Le schéma relie le bloc « Client » au bloc « Serveur »');
  expect(narration).toContain('Le schéma relie le bloc « Serveur » au bloc « Base de données »');
  expect(narration).toContain('Tableau textuel.');
  expect(narration).toContain('Pour HTTP, le port utilisé est 80');
  expect(narration).toContain('Pour HTTPS, le port utilisé est 443');
  expect(narration).toContain('Le schéma relie le bloc « Client » au bloc « API » en passant par HTTPS');
  expect(narration).toContain('Le schéma relie le bloc « API » au bloc « Base de données »');
  expect(narration).toContain('Le schéma relie le bloc « Poste de travail » au bloc « Routeur »');
  expect(narration).toContain('Le schéma relie le bloc « Poste de secours » au bloc « Routeur »');
  expect(narration).toContain('Le schéma se lit ainsi : Client va vers Passerelle.');
  expect(narration).not.toContain('→');
  expect(narration).not.toContain('Copier');
  expect(narration).not.toContain('Texte guide qui ne doit pas remplacer les données.');
  expect(narration).not.toContain('Guide HTML générique à ne pas lire à la place des éléments.');

  const audioSegments = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return state.splitSpeechText('Première phrase. Deuxième phrase.', 1800);
  });
  expect(audioSegments).toEqual(['Première phrase. Deuxième phrase.']);
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
  const headings = article.locator('h2[id]');
  await expect.poll(() => headings.count()).toBeGreaterThan(1);
  const heading = headings.last();
  await expect(heading).toBeVisible();
  const headingId = await heading.getAttribute('id');
  const headingText = (await heading.innerText()).replace(/\s+/g, ' ').trim();
  const normalizedHeadingText = headingText
    .replace(/^\s*\d+(?:\.\d+)*[.)]?\s+/u, '')
    .replace(/[.!?…:;]+$/u, '')
    .trim();

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
  expect(speech.text.startsWith('Section : ' + normalizedHeadingText + '.')).toBe(true);
  await expect(page.getByRole('group', { name: 'Commandes flottantes de lecture vocale' })).toBeVisible();
});


test('le clic droit sur un paragraphe démarre la lecture à ce paragraphe et non au début du cours', async ({ page }) => {
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
  const targetHeading = article.locator('h2[id]').nth(1);
  await expect(targetHeading).toBeVisible();
  const targetParagraph = targetHeading.locator('xpath=following-sibling::p[1]');
  await expect(targetParagraph).toBeVisible();
  const paragraphText = (await targetParagraph.innerText()).replace(/\s+/g, ' ').trim();
  expect(paragraphText.length).toBeGreaterThan(20);

  // Ne lance pas le fournisseur audio : on vérifie le texte qui lui serait remis.
  await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    state.playSpeechChunk = () => {};
  });

  await targetParagraph.click({ button: 'right' });
  const menu = page.getByRole('menu', { name: 'Options de lecture' });
  await expect(menu).toBeVisible();
  const targetLabel = paragraphText.slice(0, 100);
  await expect(menu.getByText(targetLabel, { exact: true })).toBeVisible();
  await menu.getByRole('menuitem', { name: 'Lire à ce niveau' }).click();

  const speech = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return {
      start: state.startSectionSelection,
      text: state.speechQueue.join(' '),
    };
  });
  const openingWords = paragraphText.split(/\s+/).slice(0, 5).join(' ');
  const normalizeSpoken = value => value.toLocaleLowerCase('fr-FR').replace(/[.,:;!?…"'«»()[\]]/gu, '').replace(/\s+/g, ' ').trim();
  expect(speech.start).toBe(await targetHeading.getAttribute('id'));
  expect(normalizeSpoken(speech.text).startsWith(normalizeSpoken(openingWords))).toBe(true);
  expect(speech.text).not.toContain('Titre du cours : Qu’est-ce qu’un réseau');
});

test('le bouton pause flottant reste en bas à droite pendant le défilement et permet pause/reprise/arrêt', async ({ page }) => {
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
  const scroll = page.locator('[x-ref="modalScroll"]');
  await expect.poll(() => scroll.evaluate(el => el.scrollHeight > el.clientHeight)).toBe(true);

  const readPosition = () => page.evaluate(() => {
    const dialog = document.querySelector('.modal-panel[role="dialog"]');
    const floating = document.querySelector('[aria-label="Commandes flottantes de lecture vocale"]');
    const dialogRect = dialog.getBoundingClientRect();
    const floatingRect = floating.getBoundingClientRect();
    return {
      rightGap: dialogRect.right - floatingRect.right,
      bottomGap: dialogRect.bottom - floatingRect.bottom,
      left: floatingRect.left,
      top: floatingRect.top,
    };
  });

  const positionBeforeScroll = await readPosition();
  expect(positionBeforeScroll.rightGap).toBeGreaterThanOrEqual(0);
  expect(positionBeforeScroll.rightGap).toBeLessThan(40);
  expect(positionBeforeScroll.bottomGap).toBeGreaterThanOrEqual(0);
  expect(positionBeforeScroll.bottomGap).toBeLessThan(40);

  await scroll.evaluate(el => {
    el.scrollTop = Math.min(320, el.scrollHeight - el.clientHeight);
    el.dispatchEvent(new Event('scroll', { bubbles: true }));
  });
  await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
  const positionAfterScroll = await readPosition();
  expect(Math.abs(positionAfterScroll.left - positionBeforeScroll.left)).toBeLessThan(2);
  expect(Math.abs(positionAfterScroll.top - positionBeforeScroll.top)).toBeLessThan(2);
  await expect(controls.getByRole('button', { name: 'Mettre en pause la lecture vocale' })).toHaveText(/Pause lecture/);
  const pause = controls.getByRole('button', { name: 'Mettre en pause la lecture vocale' });
  await pause.click();
  await expect(controls.getByRole('button', { name: 'Reprendre la lecture vocale' })).toBeVisible();
  await expect(controls.getByText('Lecture en pause')).toBeVisible();

  await controls.getByRole('button', { name: 'Reprendre la lecture vocale' }).click();
  await expect(controls.getByRole('button', { name: 'Mettre en pause la lecture vocale' })).toBeVisible();

  await controls.getByRole('button', { name: 'Arrêter la lecture vocale' }).click();
  await expect(controls).toBeHidden();
});



test('le sélecteur Démarrer à fait aussi commencer la lecture à la section choisie', async ({ page }) => {
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
  const headings = article.locator('h2[id]');
  await expect.poll(() => headings.count()).toBeGreaterThan(1);
  const targetHeading = headings.last();
  const targetId = await targetHeading.getAttribute('id');
  const targetText = (await targetHeading.innerText()).replace(/\s+/g, ' ').trim()
    .replace(/^\s*\d+(?:\.\d+)*[.)]?\s+/u, '')
    .replace(/[.!?…:;]+$/u, '')
    .trim();

  await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    state.playSpeechChunk = () => {};
  });

  await page.getByRole('combobox', {
    name: 'Choisir le point de départ de la lecture du cours',
  }).selectOption({ value: targetId });
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).startSectionSelection)).toBe(targetId);
  await page.getByRole('button', { name: 'Écouter le cours' }).click();

  const speechText = await page.evaluate(() => window.Alpine.$data(document.body).speechQueue.join(' '));
  expect(speechText.startsWith('Section : ' + targetText + '.')).toBe(true);
});


test('le défilement reste léger même avec plusieurs centaines de sections', async ({ page }) => {
  await openDashboard(page);
  await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    await state.show('linux-expert');
  });
  const article = page.locator('[x-ref="lessonArticle"]');
  await expect(article).toBeVisible();
  await expect.poll(() => page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return state._lessonHeadingOffsets.length;
  })).toBeGreaterThan(100);

  const result = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    const container = state.$refs.modalScroll;
    // Simule un cours long (300 sections) tout en gardant le cache de géométrie déjà construit.
    state._lessonHeadingOffsets = Array.from({ length: 300 }, (_, index) => ({
      id: 'synthetic-section-' + index,
      top: index * 420,
    }));
    state._lessonHeadingCourseId = String(state.detail.id);

    const original = Element.prototype.getBoundingClientRect;
    let geometryReads = 0;
    Element.prototype.getBoundingClientRect = function (...args) {
      geometryReads += 1;
      return original.apply(this, args);
    };
    try {
      for (let index = 0; index < 40; index += 1) {
        container.scrollTop = index * 170;
        state.onLessonScroll({ target: container });
      }
    } finally {
      Element.prototype.getBoundingClientRect = original;
    }
    return { geometryReads, cachedHeadingCount: state._lessonHeadingOffsets.length };
  });

  expect(result.cachedHeadingCount).toBe(300);
  expect(result.geometryReads).toBe(0);
});

test('le lecteur reprend la dernière section après fermeture et respecte le départ demandé', async ({ page }) => {
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
  const headings = article.locator('h2[id]');
  await expect.poll(() => headings.count()).toBeGreaterThan(1);
  const targetHeading = headings.last();
  const targetId = await targetHeading.getAttribute('id');
  const targetText = (await targetHeading.innerText()).replace(/\s+/g, ' ').trim();
  const startSelector = page.getByRole('combobox', {
    name: 'Choisir le point de départ de la lecture du cours',
  });
  const scroll = page.locator('[x-ref="modalScroll"]');

  await startSelector.selectOption({ value: targetId });
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).startSectionSelection)).toBe(targetId);
  await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
  await expect.poll(() => page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return state.lessonPositions[String(state.detail.id)]?.sectionId || '';
  })).toBe(targetId);
  await expect(targetHeading).toBeVisible();
  const beforeClose = await scroll.evaluate(el => el.scrollTop);
  expect(beforeClose).toBeGreaterThan(0);

  await page.getByRole('button', { name: 'Fermer', exact: true }).click();
  await expect(page.locator('div[x-show="open"].fixed.inset-0')).toBeHidden();

  // Réouverture via la même recherche : le lecteur doit reprendre la position persistée.
  await searchInput.fill("Qu'est-ce qu'un réseau");
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();
  await expect(article).toBeVisible();
  await expect.poll(() => page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    return state.lessonPositions[String(state.detail.id)]?.sectionId || '';
  })).toBe(targetId);
  await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).activeSection)).toBe(targetId);
  const afterReopen = await scroll.evaluate(el => el.scrollTop);
  expect(Math.abs(afterReopen - beforeClose)).toBeLessThan(180);

  // « Début du cours » doit annuler l'effet de la reprise automatique.
  await startSelector.selectOption({ value: '__top__' });
  await expect.poll(() => page.evaluate(() => window.Alpine.$data(document.body).startSectionSelection)).toBe('__top__');
  await expect.poll(() => scroll.evaluate(el => el.scrollTop)).toBe(0);
  expect(targetText.length).toBeGreaterThan(0);
});

test('la lecture vocale annonce le nombre d’équipements et de liaisons des schémas ASCII et Mermaid', async ({ page }) => {
  await openDashboard(page);

  const searchInput = page.locator('input[x-ref="searchBox"]');
  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  await searchInput.fill("Qu'est-ce qu'un réseau");
  const lessonResult = results.locator('button').filter({
    hasText: "Qu'est-ce qu'un réseau ? - Débutant",
  }).first();
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();
  await expect(page.locator('#course-reader-title')).toHaveText("Qu'est-ce qu'un réseau ? - Débutant");
  await expect(page.locator('[x-ref="lessonArticle"]')).toBeVisible();

  const ttsRequests = [];
  await page.route('**/api/tts', async route => {
    const payload = route.request().postDataJSON();
    ttsRequests.push(payload);
    // Réponse audio factice non vide : on valide le texte envoyé à la voix sans dépendre
    // du fournisseur TTS externe ni de la présence d'un codec audio sur le runner.
    await route.fulfill({
      status: 200,
      contentType: 'audio/mpeg',
      body: Buffer.from('skilltree-test-audio-segment'),
    });
  });

  const fixture = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    const article = state.$refs.lessonArticle;
    article.innerHTML = `
      <div class="code-container">
        <div class="code-header"><span class="code-lang">ascii</span></div>
        <pre><code>PC1 ---- Switch1
Switch1 ---- Routeur1
Routeur1 ---- Serveur1</code></pre>
      </div>
      <figure class="lesson-mermaid">
        <pre class="lesson-mermaid-source">flowchart LR
  PC2[PC2] --> SW2[Switch2]
  SW2[Switch2] --> R2[Routeur2]
  R2[Routeur2] --> SRV2[Serveur2]</pre>
      </figure>
    `;

    state.startSectionSelection = '__top__';
    state.prepareLessonDiagrams(article);
    const spokenText = state.speechTextFromArticle();
    const chunks = state.splitSpeechText(spokenText);
    const result = {
      diagramCount: article.querySelectorAll('.lesson-diagram-block').length,
      spokenText,
      chunks,
      readerOpen: Boolean(state.open && state.detail?.id === 'intro-reseau-debutant'),
    };
    state.startSpeech(spokenText, 'lesson');
    return result;
  });

  expect(fixture.readerOpen).toBe(true);
  expect(fixture.diagramCount).toBe(2);

  // Chaque représentation possède quatre équipements distincts et trois liens directs.
  expect((fixture.spokenText.match(/4 équipements identifiables/gu) || []).length).toBe(2);
  expect((fixture.spokenText.match(/3 liaisons directes identifiables entre équipements/gu) || []).length).toBe(2);
  expect((fixture.spokenText.match(/3 câbles physiques/gu) || []).length).toBe(2);
  expect(fixture.spokenText).toContain('PC1, Switch1, Routeur1, Serveur1');
  expect(fixture.spokenText).toContain('PC2, Switch2, Routeur2, Serveur2');
  expect(fixture.spokenText).toContain('les liens Wi-Fi et les flux logiques ne sont pas des câbles');

  // Vérifier que le bilan calculé passe aussi par le chemin réel de lecture vers /api/tts.
  await expect.poll(
    () => ttsRequests.some(request => String(request.text || '').includes('Inventaire du schéma :')),
    { timeout: 10_000 },
  ).toBe(true);
  const spokenRequest = ttsRequests.find(request => String(request.text || '').includes('Inventaire du schéma :'));
  expect(spokenRequest.text).toContain('4 équipements identifiables');
  expect(spokenRequest.text).toContain('3 liaisons directes identifiables entre équipements');
  expect(spokenRequest.text).toContain('3 câbles physiques');

  await page.evaluate(() => window.Alpine.$data(document.body).stopSpeech());
});
