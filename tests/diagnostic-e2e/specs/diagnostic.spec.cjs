const { test, expect } = require('@playwright/test');

async function openDashboard(page) {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();

  await expect.poll(async () => page.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return Array.isArray(state?.nodes) ? state.nodes.length : 0;
  }), { timeout: 30_000 }).toBeGreaterThan(0);
}

async function openDiagnostics(page) {
  await openDashboard(page);
  const navigation = page.getByRole('navigation', { name: 'Navigation principale' });
  await navigation.getByRole('button', { name: 'Diagnostic', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Diagnostic interactif', exact: true })).toBeVisible();
}

test('les scénarios Linux, sécurité et cloud sont accessibles depuis le diagnostic', async ({ page }) => {
  await openDiagnostics(page);

  await expect(page.getByRole('button', { name: /Service web Linux indisponible/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /Connexion suspecte sur un serveur/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /Instance cloud inaccessible/ })).toBeVisible();
});

test('une erreur déclenche la consolidation et produit une recommandation de cours contextualisée', async ({ page }) => {
  await openDiagnostics(page);

  await page.getByRole('button', { name: /Service web Linux indisponible/ }).click();
  await expect(page.getByText(/Après un changement, le site interne/)).toBeVisible();

  // Une mauvaise décision doit présenter une consolidation adaptée, sans perdre le scénario.
  await page.getByRole('button', { name: /Redémarrer immédiatement tout le serveur/ }).click();
  await expect(page.getByText('Question de consolidation adaptée', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: /systemctl status nginx --no-pager/ }).click();

  // Le scénario revient à l'étape d'origine puis continue avec les vérifications sûres.
  await expect(page.getByText(/Après un changement, le site interne/)).toBeVisible();
  await page.getByRole('button', { name: /Consulter systemctl status nginx/ }).click();
  await page.getByRole('button', { name: /Lire journalctl -u nginx/ }).click();
  await page.getByRole('button', { name: /Exécuter nginx -t/ }).click();

  await expect(page.getByText('Service rétabli', { exact: true })).toBeVisible();
  await expect(page.getByText('Ton plan d’action personnalisé', { exact: true })).toBeVisible();
  await expect(page.getByText('Cours et révisions', { exact: true })).toBeVisible();
  await expect(page.getByText(/Compétence : Services Linux · résultat : 67 %/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Ouvrir le cours' }).first()).toBeVisible();
});

test('la progression d’un diagnostic est sauvegardée et reprise après rechargement', async ({ page }) => {
  await openDiagnostics(page);

  const scenario = page.getByRole('button', { name: /Service web Linux indisponible/ });
  await scenario.click();
  await page.getByRole('button', { name: /Consulter systemctl status nginx/ }).click();
  await expect(page.getByText(/Le service est en échec et signale une erreur de configuration/)).toBeVisible();

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();
  await page.getByRole('navigation', { name: 'Navigation principale' })
    .getByRole('button', { name: 'Diagnostic', exact: true }).click();

  const resumableScenario = page.getByRole('button', { name: /Service web Linux indisponible/ });
  await expect(resumableScenario).toContainText('À reprendre');
  await expect(resumableScenario).toContainText('1 décision(s)');
  await resumableScenario.click();

  await expect(page.getByText(/Le service est en échec et signale une erreur de configuration/)).toBeVisible();
  await expect(page.getByRole('button', { name: /Lire journalctl -u nginx/ })).toBeVisible();
});

test('le scénario de réponse à incident peut être résolu de bout en bout', async ({ page }) => {
  await openDiagnostics(page);

  await page.getByRole('button', { name: /Connexion suspecte sur un serveur/ }).click();
  await page.getByRole('button', { name: /Préserver les journaux/ }).click();
  await page.getByRole('button', { name: /Corréler l’utilisateur/ }).click();
  await page.getByRole('button', { name: /Révoquer les sessions/ }).click();

  await expect(page.getByText('Incident contenu', { exact: true })).toBeVisible();
  await expect(page.getByText('100 %', { exact: true })).toBeVisible();
});

test('le scénario de connectivité cloud peut être résolu sans exposer largement SSH', async ({ page }) => {
  await openDiagnostics(page);

  await page.getByRole('button', { name: /Instance cloud inaccessible/ }).click();
  await page.getByRole('button', { name: /Contrôler les vérifications d’état/ }).click();
  await page.getByRole('button', { name: /Mettre à jour la règle avec le CIDR/ }).click();
  await page.getByRole('button', { name: /Utiliser le bastion, le VPN/ }).click();

  await expect(page.getByText('Accès cloud rétabli', { exact: true })).toBeVisible();
  await expect(page.getByText('100 %', { exact: true })).toBeVisible();
});

test('les seuils de 60 % et 80 % pilotent une progression fondée sur niveau et domaine', async ({ page }) => {
  await openDiagnostics(page);

  const results = await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    async function recommendationFor(id, correct, incorrect) {
      state.diagProgressMap = {};
      state.diagDoneMap = {};
      await state.openDiag(id);
      state.diagKey = 'ok';
      state.diagTrail = [
        ...Array.from({ length: correct }, () => ({ good: true, competency: 'Test de progression' })),
        ...Array.from({ length: incorrect }, () => ({ good: false, competency: 'Test de progression' })),
      ];
      const recommendation = state.diagNextScenarioRecommendation();
      const current = state.diagList.find(item => item.id === id);
      const target = recommendation && state.diagList.find(item => item.id === recommendation.id);
      return {
        score: state.diagEfficiency,
        recommendation,
        currentLevel: current && current.level,
        currentDomain: current && current.domain,
        targetLevel: target && target.level,
        targetDomain: target && target.domain,
        currentRank: current ? state.diagLevelRank(current.level) : -1,
        targetRank: target ? state.diagLevelRank(target.level) : -1,
      };
    }

    return {
      low: await recommendationFor('linux-service-down', 59, 41),
      threshold60: await recommendationFor('linux-service-down', 60, 40),
      threshold80: await recommendationFor('linux-service-down', 80, 20),
      sameDomainPromotion: await recommendationFor('wifi-lent', 80, 20),
      sameLevelFallback: await recommendationFor('vlan-hote', 80, 20),
    };
  });

  expect(results.low.score).toBe(59);
  expect(results.low.recommendation.replay).toBe(true);
  expect(results.low.recommendation.id).toBe('linux-service-down');

  expect(results.threshold60.score).toBe(60);
  expect(results.threshold60.recommendation.replay).toBe(false);
  expect(results.threshold60.targetLevel).toBe(results.threshold60.currentLevel);
  expect(results.threshold60.recommendation.reason).toContain('au même niveau');
  expect(results.threshold60.recommendation.reason).toContain('systèmes Linux');

  expect(results.threshold80.score).toBe(80);
  expect(results.threshold80.targetRank).toBeGreaterThan(results.threshold80.currentRank);
  expect(results.threshold80.recommendation.reason).toContain('pour élargir ton parcours');

  expect(results.sameDomainPromotion.recommendation.id).toBe('vlan-hote');
  expect(results.sameDomainPromotion.targetRank).toBeGreaterThan(results.sameDomainPromotion.currentRank);
  expect(results.sameDomainPromotion.recommendation.reason).toContain('dans le domaine réseaux');

  expect(results.sameLevelFallback.recommendation.id).toBe('etherchannel-suspendu');
  expect(results.sameLevelFallback.targetLevel).toBe(results.sameLevelFallback.currentLevel);
  expect(results.sameLevelFallback.recommendation.reason).toContain('Aucun scénario inédit de niveau supérieur');
});

test('les ressources recommandées suivent les compétences faibles et excluent les cours verrouillés', async ({ page }) => {
  await openDiagnostics(page);

  const result = await page.evaluate(() => {
    const state = window.Alpine.$data(document.body);
    const targetIds = ['linux-debutant', 'process-debutant', 'linux-intermediaire'];
    const candidates = targetIds.map(id => state.nodes.find(node => String(node.id) === id));
    if (candidates.some(node => !node)) return { missingCatalogNodes: true };

    candidates.forEach(node => { node.status = 'locked'; });
    state.diagTrail = [
      { good: false, competency: 'Services Linux', decisionType: 'scenario' },
      { good: true, competency: 'Services Linux', decisionType: 'scenario' },
    ];
    const allLocked = state.diagLearningRecommendations();

    // Le cours cible reste verrouillé ; un prérequis disponible doit être recommandé à sa place.
    candidates[1].status = 'available';
    const withPrerequisite = state.diagLearningRecommendations();
    return {
      missingCatalogNodes: false,
      summary: state.diagCompetencySummary(),
      allLockedCourseIds: allLocked.courses.map(item => item.node.id),
      recommended: withPrerequisite.courses.map(item => ({
        id: item.node.id, competency: item.competency, rate: item.rate, reason: item.reason,
        status: item.node.status,
      })),
      labs: withPrerequisite.labs.map(item => ({ id: item.node.id, status: item.node.status })),
    };
  });

  expect(result.missingCatalogNodes).toBe(false);
  expect(result.summary).toEqual(expect.arrayContaining([
    expect.objectContaining({ name: 'Services Linux', rate: 50, total: 2, correct: 1 }),
  ]));
  expect(result.allLockedCourseIds).toEqual([]);
  expect(result.recommended[0]).toMatchObject({
    id: 'process-debutant',
    competency: 'Services Linux',
    rate: 50,
    status: 'available',
    reason: 'Prérequis à valider pour débloquer le parcours ciblé.',
  });
  expect(result.labs.every(item => item.status !== 'locked' && item.status !== 'validated')).toBe(true);
});

test('un scénario déjà terminé ne bloque pas un scénario inédit du même niveau ou du niveau suivant', async ({ page }) => {
  await openDiagnostics(page);

  const recommendations = await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    async function forCase(id, score, completedIds) {
      state.diagProgressMap = {};
      state.diagDoneMap = Object.fromEntries(completedIds.map(itemId => [itemId, 100]));
      await state.openDiag(id);
      state.diagKey = 'ok';
      state.diagTrail = [
        ...Array.from({ length: score }, () => ({ good: true, competency: 'Test de parcours' })),
        ...Array.from({ length: 100 - score }, () => ({ good: false, competency: 'Test de parcours' })),
      ];
      const recommendation = state.diagNextScenarioRecommendation();
      return {
        recommendation,
        completed: Object.keys(state.diagDoneMap),
        targetCompleted: recommendation ? Object.prototype.hasOwnProperty.call(state.diagDoneMap, recommendation.id) : false,
      };
    }

    return {
      sameLevel: await forCase('wifi-lent', 70, ['network_down']),
      nextLevel: await forCase('wifi-lent', 80, ['vlan-hote', 'etherchannel-suspendu']),
    };
  });

  expect(recommendations.sameLevel.recommendation).not.toBeNull();
  expect(recommendations.sameLevel.recommendation.id).toBe('linux-service-down');
  expect(recommendations.sameLevel.targetCompleted).toBe(false);
  expect(recommendations.sameLevel.recommendation.reason).toContain('scénarios inédits');

  expect(recommendations.nextLevel.recommendation).not.toBeNull();
  expect(recommendations.nextLevel.recommendation.id).toBe('cloud-instance-unreachable');
  expect(recommendations.nextLevel.targetCompleted).toBe(false);
  expect(recommendations.nextLevel.recommendation.reason).toContain('niveau Intermédiaire');
});

test('le meilleur score, le dernier bilan et une reprise restent cohérents après rechargement', async ({ page }) => {
  await openDiagnostics(page);

  const history = await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    const id = 'security-suspicious-login';
    await state.openDiag(id);

    // Première tentative parfaite : elle devient le meilleur score enregistré.
    state.diagKey = 'ok';
    state.diagTrail = Array.from({ length: 4 }, () => ({
      key: 'a', good: true, label: 'Réponse correcte', competency: 'Test historique',
    }));
    state.diagCompleteRun();

    // Une tentative ultérieure moins bonne met à jour le dernier bilan sans écraser le record.
    state.diagKey = 'ok';
    state.diagTrail = [
      { key: 'a', good: true, label: 'Correct', competency: 'Test historique' },
      { key: 'b', good: true, label: 'Correct', competency: 'Test historique' },
      { key: 'c', good: true, label: 'Correct', competency: 'Test historique' },
      { key: 'c', good: false, label: 'Incorrect', competency: 'Test historique' },
    ];
    state.diagCompleteRun();
    state.diagClose();

    const read = key => JSON.parse(localStorage.getItem('st:' + key) || '{}');
    return {
      best: read('diag-done')[id],
      latest: read('diag-results')[id]?.score,
      hasProgress: Object.prototype.hasOwnProperty.call(read('diag-progress'), id),
    };
  });

  expect(history).toEqual({ best: 100, latest: 75, hasProgress: false });
  const scenario = page.getByRole('button', { name: /Connexion suspecte sur un serveur/ });
  await expect(scenario).toContainText('Meilleur : 100 % · dernier : 75 %');

  // La tentative en cours doit coexister avec le dernier bilan sans l'effacer.
  await scenario.click();
  await page.getByRole('button', { name: /Préserver les journaux/ }).click();
  const inProgress = await page.evaluate(() => {
    const read = key => JSON.parse(localStorage.getItem('st:' + key) || '{}');
    const id = 'security-suspicious-login';
    return {
      best: read('diag-done')[id],
      latest: read('diag-results')[id]?.score,
      stepKey: read('diag-progress')[id]?.stepKey,
      trailLength: read('diag-progress')[id]?.trail?.length,
    };
  });
  expect(inProgress).toEqual({ best: 100, latest: 75, stepKey: 'b', trailLength: 1 });

  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.getByRole('navigation', { name: 'Navigation principale' })
    .getByRole('button', { name: 'Diagnostic', exact: true }).click();
  const resumedScenario = page.getByRole('button', { name: /Connexion suspecte sur un serveur/ });
  await expect(resumedScenario).toContainText('À reprendre');
  await expect(resumedScenario).toContainText('1 décision(s)');
  await resumedScenario.click();
  await expect(page.getByText(/La connexion inconnue a exécuté une commande avec sudo/)).toBeVisible();
  expect(await page.evaluate(() => {
    const read = key => JSON.parse(localStorage.getItem('st:' + key) || '{}');
    return {
      best: read('diag-done')['security-suspicious-login'],
      latest: read('diag-results')['security-suspicious-login']?.score,
    };
  })).toEqual({ best: 100, latest: 75 });
});

test('une progression corrompue est ignorée sans modifier le meilleur score ni le dernier bilan', async ({ page }) => {
  await openDiagnostics(page);

  await page.evaluate(() => {
    const id = 'security-suspicious-login';
    localStorage.setItem('st:diag-done', JSON.stringify({ [id]: 100 }));
    localStorage.setItem('st:diag-results', JSON.stringify({
      [id]: { score: 75, completedAt: '2026-10-26T10:00:00.000Z', outcome: 'success', competencies: [] },
    }));
    localStorage.setItem('st:diag-progress', JSON.stringify({
      [id]: {
        stepKey: 'step-that-does-not-exist',
        trail: [{ key: 'step-that-does-not-exist', good: false }],
        adaptiveQuestion: { prompt: 'Question invalide', choices: [] },
        adaptiveResumeKey: 'missing-resume-step',
        adaptiveNextKey: 'missing-next-step',
        startedAt: Date.now(),
      },
    }));
  });

  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.getByRole('navigation', { name: 'Navigation principale' })
    .getByRole('button', { name: 'Diagnostic', exact: true }).click();
  await page.getByRole('button', { name: /Connexion suspecte sur un serveur/ }).click();
  await expect(page.getByText(/Les journaux montrent plusieurs échecs SSH/)).toBeVisible();

  const stored = await page.evaluate(() => {
    const read = key => JSON.parse(localStorage.getItem('st:' + key) || '{}');
    const id = 'security-suspicious-login';
    return {
      best: read('diag-done')[id],
      latest: read('diag-results')[id]?.score,
      currentStep: read('diag-progress')[id]?.stepKey,
      currentTrail: read('diag-progress')[id]?.trail?.length,
    };
  });
  expect(stored).toEqual({ best: 100, latest: 75, currentStep: 'a', currentTrail: 0 });
});

test('le parcours se termine clairement au lieu de proposer en boucle des scénarios terminés', async ({ page }) => {
  await openDiagnostics(page);

  await page.evaluate(async () => {
    const state = window.Alpine.$data(document.body);
    state.diagDoneMap = {
      'etherchannel-suspendu': 100,
      'cloud-instance-unreachable': 100,
    };
    await state.openDiag('vlan-hote');
    state.diagKey = 'ok';
    state.diagTrail = [
      ...Array.from({ length: 70 }, () => ({ good: true, competency: 'Test de parcours' })),
      ...Array.from({ length: 30 }, () => ({ good: false, competency: 'Test de parcours' })),
    ];
  });

  const state = await page.evaluate(() => {
    const app = window.Alpine.$data(document.body);
    return {
      recommendation: app.diagNextScenarioRecommendation(),
      efficiency: app.diagEfficiency,
      outcome: app.diagFinalOutcome(),
    };
  });
  expect(state.efficiency).toBe(70);
  expect(state.outcome).toBe('success');
  expect(state.recommendation).toBeNull();
  await expect(page.getByText(
    'Tu as terminé les scénarios inédits disponibles à ce niveau. Travaille les cours, révisions et labs recommandés, puis rejoue pour améliorer ton score.',
    { exact: true },
  )).toBeVisible();
});

