const fs = require('node:fs');
const path = require('node:path');
const { test, expect } = require('@playwright/test');

const quizDefinition = JSON.parse(
  fs.readFileSync(
    path.resolve(__dirname, '../../../content/quiz/intro-reseau-debutant.json'),
    'utf8',
  ),
);

async function openDashboard(page) {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.getByRole('button', { name: 'Ouvrir les paramètres' })).toBeVisible();

  await expect.poll(async () => page.evaluate(() => {
    const state = window.Alpine && window.Alpine.$data(document.body);
    return Array.isArray(state?.nodes) ? state.nodes.length : 0;
  }), { timeout: 30_000 }).toBeGreaterThan(0);
}

test('la correction du quiz affiche la réponse choisie et la bonne option après soumission', async ({ page }) => {
  await openDashboard(page);

  const searchInput = page.locator('input[x-ref="searchBox"]');
  await searchInput.fill("Qu'est-ce qu'un réseau");

  const results = page.locator('div[x-show="searchOpen && searchQuery.trim().length >= 2"]');
  const lessonResult = results.locator('button').filter({
    hasText: "Qu'est-ce qu'un réseau ? - Débutant",
  }).first();
  await expect(lessonResult).toBeVisible();
  await lessonResult.click();

  const title = page.locator('#course-reader-title');
  await expect(title).toHaveText("Qu'est-ce qu'un réseau ? - Débutant");

  await page.locator('button').filter({ hasText: '✏️ Exercice' }).click();
  await page.getByRole('button', { name: "Démarrer l'exercice" }).click();

  const fieldsets = page.locator('fieldset');
  await expect(fieldsets).toHaveCount(quizDefinition.questions.length);

  for (const [index, question] of quizDefinition.questions.entries()) {
    const answerIndex = index === 0
      ? (question.answer + 1) % question.choices.length
      : question.answer;
    // Une réponse est volontairement incorrecte ; le reste est correct pour
    // vérifier le retour de correction sans faire échouer artificiellement tout le quiz.
    await fieldsets.nth(index).locator('input[type="radio"]').nth(answerIndex).check();
  }

  await page.getByRole('button', { name: 'Valider mes réponses' }).click();

  const feedback = page.locator('div[x-show="quizResult?.results?.length"]');
  await expect(feedback).toBeVisible();

  const firstQuestion = quizDefinition.questions[0];
  const selected = firstQuestion.choices[(firstQuestion.answer + 1) % firstQuestion.choices.length];
  const correct = firstQuestion.choices[firstQuestion.answer];

  await expect(feedback.getByText(firstQuestion.prompt, { exact: true })).toBeVisible();
  await expect(feedback.getByText('✕ Réponse incorrecte', { exact: true })).toBeVisible();
  await expect(feedback.getByText(`Ta réponse : ${selected}`, { exact: true })).toBeVisible();
  await expect(feedback.getByText(`Bonne réponse : ${correct}`, { exact: true })).toBeVisible();
  await expect(feedback.getByText(firstQuestion.explanation, { exact: true })).toBeVisible();
});
