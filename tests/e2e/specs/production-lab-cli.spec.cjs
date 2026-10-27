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

      // La vérification d’ouverture/canevas/bibliothèques couvre les 17 scénarios.
      // La saisie CLI réelle est jouée sur quatre représentants de familles différentes.
      if (['cli-ipv4-interfaces', 'cli-vlan-access', 'cli-static-routing', 'cli-qos-voice-policy'].includes(labId)) {
        console.log('Début interaction CLI xterm : ' + labId);
        // Exécuter la séquence de référence dans xterm, comme un apprenant.
        // Le seul POST autorisé est /check : jamais /submit ni /save en production.
        const writeRequests = [];
        page.on('request', request => {
          const requestUrl = new URL(request.url());
          if (request.method() === 'POST' && /\/api\/lab\/v2\/[^/]+\/(submit|save)$/.test(requestUrl.pathname)) {
            writeRequests.push({ method: request.method(), path: requestUrl.pathname });
          }
        });
  
        const targetHint = (definition.hints || []).find(hint => hint.startsWith('Cible CLI'));
        expect(targetHint, 'la cible CLI doit être documentée').toBeTruthy();
        const targetMatch = targetHint.match(/^Cible CLI\s*:\s*([^.]+)\./);
        expect(targetMatch, 'la cible CLI doit être exploitable').toBeTruthy();
        const targetId = targetMatch[1].trim();
        const sequenceHint = (definition.hints || []).find(hint => hint.startsWith('Séquence de référence'));
        expect(sequenceHint, 'la séquence CLI de référence doit être documentée').toBeTruthy();
        const commands = sequenceHint
          .replace(/^Séquence de référence\s*:\s*/, '')
          .replace(/\.$/, '')
          .split(/\s;\s/)
          .map(command => command.trim())
          .filter(Boolean);
        expect(commands.length, 'la séquence de commandes ne doit pas être vide').toBeGreaterThan(0);
  
        const targetNode = page.locator('.react-flow__node[data-id="' + targetId + '"]');
        await expect(targetNode, 'l’équipement cible doit être présent sur le canevas').toBeVisible();
        await targetNode.click();
        const terminal = page.locator('.xterm').first();
        await expect(terminal, 'la console xterm doit apparaître après sélection').toBeVisible();
        await terminal.click({ position: { x: 100, y: 60 } });
        for (const command of commands) {
          await page.keyboard.type(command);
          await page.keyboard.press('Enter');
        }
  
        const checkResponsePromise = page.waitForResponse(response =>
          response.url().includes('/api/lab/v2/' + labId + '/check') &&
          response.request().method() === 'POST'
        );
        await page.getByRole('button', { name: /Vérifier/ }).click();
        const checkResponse = await checkResponsePromise;
        expect(checkResponse.status(), 'le contrôle serveur doit répondre HTTP 200').toBe(200);
        const checkResult = await checkResponse.json();
        expect(checkResult.passed, 'la séquence CLI doit satisfaire le scénario').toBe(true);
        expect(checkResult.score, 'le serveur doit calculer un score complet').toBe(1);
        expect(checkResult.results.length, 'le serveur doit renvoyer les détails des règles').toBeGreaterThan(0);
        expect(checkResult.results.every(item => item.passed), 'toutes les règles serveur doivent réussir').toBe(true);
        const visibleDetails = page.getByRole('region', { name: 'Détails des vérifications' });
        await expect(visibleDetails, 'les résultats du serveur doivent être visibles dans l’interface').toBeVisible();
        await expect(visibleDetails.locator('li')).toHaveCount(checkResult.results.length);
        for (const item of await visibleDetails.locator('li').all()) {
          await expect(item).toContainText('✓');
        }
        expect(writeRequests, 'aucune tentative ne doit être soumise et aucune topologie sauvegardée').toEqual([]);
  
        console.log(
          'PASS ' + labId + ': terminal xterm exécuté (' + commands.length + ' commandes), ' +
          checkResult.results.length + ' règles serveur validées, aucun enregistrement effectué'
        );
  
        
      }

            expect(failedAppResponses, 'aucun script/style/API du lab ne doit échouer').toEqual([]);
      expect(pageErrors, 'aucune exception JavaScript non interceptée').toEqual([]);
      console.log(
        `PASS ${labId}: ${expectedNodes.length} équipements, ${expectedLinks.length} liaisons, bibliothèques OK`
      );
    });
  }
});
