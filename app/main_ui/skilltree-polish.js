
(function () {
  'use strict';
  const selector = 'button, a, [role="button"], input, select, textarea, summary, .card, .card-sm, [data-lab-card]';
  const applyPolish = (root) => {
    if (!root || !root.querySelectorAll) return;
    const items = [];
    if (root.matches && root.matches(selector)) items.push(root);
    items.push(...root.querySelectorAll(selector));
    for (const element of items) {
      element.classList.add('transition-all', 'duration-300');
      if (element.matches('a[data-lab-card="catalog"]')) element.classList.add('btn-glow');
      const label = String(element.innerText || element.getAttribute('aria-label') || element.value || '').replace(/\s+/g, ' ').trim().toLocaleLowerCase('fr');
      if (/\b(vérifier|soumettre|valider)\b/.test(label) || /ouvrir (le )?lab/.test(label)) element.classList.add('btn-glow');
    }
  };
  const boot = () => {
    applyPolish(document.body);
    const observer = new MutationObserver((changes) => changes.forEach(change => {
      change.addedNodes.forEach(node => { if (node.nodeType === 1) applyPolish(node); });
    }));
    observer.observe(document.body, { childList: true, subtree: true });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
