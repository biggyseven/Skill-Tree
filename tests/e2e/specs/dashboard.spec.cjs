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

  const moduleLink = page.locator('a[aria-label^="Ouvrir le module "][href*="openModule="]').first();
  await expect(moduleLink).toBeVisible();
  await expect(moduleLink).toHaveAttribute('target', '_blank');
  const moduleId = new URL(await moduleLink.getAttribute('href'), 'http://localhost').searchParams.get('openModule');
  const modulePagePromise = page.context().waitForEvent('page');
  await moduleLink.click();
  const modulePage = await modulePagePromise;
  await waitForReadyPage(modulePage);
  await expect.poll(() => modulePage.evaluate(() => window.Alpine.$data(document.body).moduleFilter)).toBe(moduleId);
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
      title: 'ACL et filtrage avancé - Intermédiaire',
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
    hasText: 'ACL et filtrage avancé - Intermédiaire',
  }).first();
  await expect(aclLab).toBeVisible();
  await expect(aclLab).toHaveAttribute('href', '/?openLab=secu-acl-intermediaire');
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
  const equipmentSeparator = page.getByRole('separator', { name: "Redimensionner la bibliothèque d’équipements" });
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
