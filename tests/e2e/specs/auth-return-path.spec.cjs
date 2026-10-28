const { test, expect } = require('@playwright/test');

async function mockAuthentication(page) {
  let statusCalls = 0;
  await page.route('**/api/auth/status', async route => {
    statusCalls += 1;
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        required: true,
        configured: true,
        authenticated: statusCalls > 1,
      }),
    });
  });
  await page.route('**/api/auth/login', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ authenticated: true }),
  }));
  return () => statusCalls;
}

async function submitLogin(page, next) {
  await page.goto('/login.html?next=' + encodeURIComponent(next));
  await page.getByLabel("Mot de passe de l'application").fill('mot-de-passe-de-test');
  await page.getByRole('button', { name: 'Se connecter' }).click();
}

test('la connexion reprend le lien Labs demandé au lieu du tableau de bord', async ({ page }) => {
  const getStatusCalls = await mockAuthentication(page);

  await submitLogin(page, '/?openTab=labs');

  // La connexion déclenche une navigation complète : attendre l'URL cible avant
  // de lire le DOM, afin de ne pas interroger un ancien contexte JavaScript.
  await page.waitForURL(url => url.pathname === '/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('heading', { name: 'Labs par niveau' })).toBeVisible();
  expect(getStatusCalls()).toBeGreaterThanOrEqual(2);
});

test('un nouvel onglet affiche directement la section de sidebar demandée', async ({ page }) => {
  const getStatusCalls = await mockAuthentication(page);
  let signalTreeStarted;
  const treeStarted = new Promise(resolve => { signalTreeStarted = resolve; });
  let releaseTreeRequest;
  const treeGate = new Promise(resolve => { releaseTreeRequest = resolve; });

  // Simule un chargement de données lent : la destination doit déjà être affichée.
  await page.route('**/api/tree', async route => {
    signalTreeStarted();
    await treeGate;
    await route.continue();
  });

  await submitLogin(page, '/?openTab=labs');
  await page.waitForURL(url => url.pathname === '/', { waitUntil: 'domcontentloaded' });
  await treeStarted;

  await expect(page.getByRole('heading', { name: 'Labs pratiques', exact: true })).toBeVisible();
  expect(getStatusCalls()).toBeGreaterThanOrEqual(2);

  releaseTreeRequest();
  await expect(page.getByRole('heading', { name: 'Labs par niveau' })).toBeVisible();
});

test('une destination next externe est ignorée après connexion', async ({ page }) => {
  await mockAuthentication(page);
  await page.goto('/login.html?next=' + encodeURIComponent('https://attacker.example/steal'));
  const origin = new URL(page.url()).origin;
  await page.getByLabel("Mot de passe de l'application").fill('mot-de-passe-de-test');
  await page.getByRole('button', { name: 'Se connecter' }).click();

  // La destination externe doit retomber sur l'accueil du même site.
  await page.waitForURL(url => url.origin === origin && url.pathname === '/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();
  expect(page.url()).not.toContain('attacker.example');
});
