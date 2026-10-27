const { test, expect } = require('@playwright/test');

const BASE_SCENARIOS = [
  'cli-acl-interface',
  'cli-bgp-neighbor',
  'cli-dhcp-pool',
  'cli-dns-host-records',
  'cli-eigrp-network',
  'cli-hsrp-gateway',
  'cli-ipv4-interfaces',
  'cli-ipv6-interface',
  'cli-nat-overload',
  'cli-ntp-syslog',
  'cli-ospf-area',
  'cli-port-security',
  'cli-qos-voice-policy',
  'cli-static-routing',
  'cli-stp-hardening',
  'cli-vlan-access',
  'cli-vlan-trunk',
];

test.describe('Lab Workspace CLI — production browser smoke (read only)', () => {
  test.setTimeout(60_000);

  for (const labId of BASE_SCENARIOS) {
    test(`ouvre ${labId}, affiche sa topologie et les deux bibliothèques`, async ({ page }) => {
      const pageErrors = [];
      const failedAppResponses = [];
      page.on('pageerror', error => pageErrors.push(error.message));
      page.on('response', response => {
        const url = response.url();
        if (
          (url.includes('/lab/main.js') ||
           url.includes('/lab/main.css') ||
           url.includes('/api/lab/v2/')) &&
          response.status() >= 400
        ) {
          failedAppResponses.push({ url, status: response.status() });
        }
      });

      const detailResponsePromise = page.waitForResponse(response =>
        response.url().includes('/api/lab/v2/' + labId) &&
        response.request().method() === 'GET'
      );
      const navigationResponse = await page.goto('/lab.html?id=' + encodeURIComponent(labId), {
        waitUntil: 'domcontentloaded',
      });
      expect(navigationResponse, 'la page Lab Workspace doit répondre').toBeTruthy();
      expect(navigationResponse.status()).toBe(200);

      const detailResponse = await detailResponsePromise;
      expect(detailResponse.status(), 'l’API du scénario doit répondre HTTP 200').toBe(200);
      const payload = await detailResponse.json();
      expect(payload.id).toBe(labId);
      expect(payload.schema_version).toBe(2);

      const definition = payload.definition || {};
      const topology = payload.initial_topology || definition.initial_topology || {};
      const expectedNodes = topology.nodes || [];
      const expectedLinks = topology.links || [];
      expect(expectedNodes.length, 'la définition doit contenir au moins trois équipements').toBeGreaterThanOrEqual(3);
      expect(expectedLinks.length, 'la définition doit contenir plusieurs liaisons').toBeGreaterThanOrEqual(2);
      expect((definition.check || {}).type).toBe('config_assertions');
      expect((definition.check || {}).rules || []).not.toHaveLength(0);

      await expect(page.getByText('Erreur de chargement')).toHaveCount(0);
      await expect(page.getByText('Chargement du Lab Workspace…')).toHaveCount(0);
      await expect(page.locator('#lab-root header').first()).toBeVisible();
      await expect(page.getByRole('heading', { level: 1, name: definition.title })).toBeVisible();

      await expect(page.locator('.react-flow__node')).toHaveCount(expectedNodes.length);
      await expect(page.locator('.react-flow__edge')).toHaveCount(expectedLinks.length);

      // La bibliothèque d'équipements doit être réellement affichée et utilisable.
      const equipmentTab = page.getByRole('tab', { name: /Équipements/ });
      const cablesTab = page.getByRole('tab', { name: /Câbles/ });
      await expect(equipmentTab).toBeVisible();
      await expect(equipmentTab).toHaveAttribute('aria-selected', 'true');
      await expect(page.locator('section[aria-label="Routeurs"]')).toBeVisible();
      await expect(page.locator('section[aria-label="Switchs"]')).toBeVisible();
      await expect(page.getByText('Routeur', { exact: true }).first()).toBeVisible();
      await expect(page.getByText('Switch', { exact: true }).first()).toBeVisible();

      // Le panneau câbles doit lister ses cinq familles, sans effectuer de liaison.
      await cablesTab.click();
      await expect(cablesTab).toHaveAttribute('aria-selected', 'true');
      for (const cableName of [
        'Cuivre droit',
        'Cuivre croisé',
        'Fibre optique',
        'Câble console',
        'Liaison sans fil',
      ]) {
        await expect(page.getByText(cableName, { exact: true })).toBeVisible();
      }

      // Revenir à la bibliothèque d'équipements vérifie également le changement d'onglet.
      await equipmentTab.click();
      await expect(equipmentTab).toHaveAttribute('aria-selected', 'true');
      await expect(page.locator('section[aria-label="Serveurs"]')).toBeVisible();
      await expect(page.locator('section[aria-label="Sécurité & WAN"]')).toBeVisible();

      expect(failedAppResponses, 'aucun script/style/API du lab ne doit échouer').toEqual([]);
      expect(pageErrors, 'aucune exception JavaScript non interceptée').toEqual([]);
      console.log(
        `PASS ${labId}: ${expectedNodes.length} équipements, ${expectedLinks.length} liaisons, bibliothèques OK`
      );
    });
  }
});
