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

  await expect.poll(() => page.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return state?.tab || '';
  })).toBe('labs');
  await expect(page.getByRole('heading', { name: 'Labs par niveau' })).toBeVisible();
  expect(getStatusCalls()).toBeGreaterThanOrEqual(2);
});

test('une destination next externe est ignorée après connexion', async ({ page }) => {
  await mockAuthentication(page);
  const origin = new URL(page.url() || 'http://127.0.0.1:8011').origin;

  await submitLogin(page, 'https://attacker.example/steal');

  await expect.poll(() => page.evaluate(() => window.location.origin)).toBe(origin);
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();
  expect(page.url()).not.toContain('attacker.example');
});
