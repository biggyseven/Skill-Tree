(() => {
  const OVERLAY_ID = 'skilltree-lab-library-overlay';
  const TAB_CONTENT_ID = 'skilltree-lab-library-content';
  const toolTitles = {
    select: 'Sélectionner',
    cable_straight: 'Câble Droit',
    cable_cross: 'Câble Croisé',
    fiber: 'Fibre Optique',
  };
  const equipmentGroups = [
    { title: 'Routage et commutation', items: [
      { type: 'router', label: 'Routeur', detail: 'Routage L3', symbol: '↔', color: '#60a5fa' },
      { type: 'switch', label: 'Switch', detail: 'Commutation L2', symbol: '▤', color: '#34d399' },
    ]},
    { title: 'Postes et services', items: [
      { type: 'pc', label: 'PC / Poste client', detail: 'Équipement utilisateur', symbol: '▣', color: '#38bdf8' },
      { type: 'server', label: 'Serveur', detail: 'Services réseau', symbol: '▥', color: '#a78bfa' },
    ]},
    { title: 'Sécurité et WAN', items: [
      { type: 'firewall', label: 'Pare-feu', detail: 'Filtrage réseau', symbol: '▦', color: '#fb7185' },
      { type: 'cloud', label: 'Cloud / WAN', detail: 'Réseau externe', symbol: '☁', color: '#22d3ee' },
    ]},
  ];
  const cables = [
    { tool: 'cable_straight', title: 'Cuivre droit', detail: 'Ethernet classique', color: '#0ea5e9', dash: '' },
    { tool: 'cable_cross', title: 'Cuivre croisé', detail: 'Liaison croisée', color: '#f97316', dash: '5 3' },
    { tool: 'fiber', title: 'Fibre optique', detail: 'Backbone haut débit', color: '#a855f7', dash: '' },
  ];
  let panel = null, overlay = null, queued = false;
  const watchedTools = new WeakSet();
  const toolObserver = new MutationObserver(() => refreshSelectedTool());

  function createOverlay() {
    if (overlay) return overlay;
    overlay = document.createElement('section');
    overlay.id = OVERLAY_ID;
    overlay.setAttribute('aria-label', 'Bibliothèques du Lab Workspace');
    overlay.innerHTML =
      '<div class="st-library-heading"><div><div class="st-library-eyebrow">Matériel disponible</div><div class="st-library-title">Bibliothèques du laboratoire</div></div><span class="st-library-count" data-library-count>6 types</span></div>' +
      '<div class="st-library-tabs" role="tablist" aria-label="Choisir une bibliothèque">' +
      '<button type="button" class="st-library-tab" role="tab" data-library-tab="equipment" aria-selected="true">Équipements</button>' +
      '<button type="button" class="st-library-tab" role="tab" data-library-tab="cables" aria-selected="false">Câbles</button></div>' +
      '<div id="' + TAB_CONTENT_ID + '" class="st-library-scroll" role="tabpanel"></div>' +
      '<div class="st-library-footer" data-library-footer>Glisse un équipement sur le schéma. Tu peux déposer plusieurs exemplaires.</div>';
    document.body.appendChild(overlay);
    overlay.querySelectorAll('[data-library-tab]').forEach(button => {
      button.addEventListener('click', () => renderTab(button.dataset.libraryTab));
    });
    overlay.addEventListener('dragstart', event => {
      const card = event.target.closest('[data-equipment-type]');
      if (!card) return;
      event.dataTransfer.setData('application/reactflow', card.dataset.equipmentType);
      event.dataTransfer.setData('text/plain', card.dataset.equipmentType);
      event.dataTransfer.effectAllowed = 'move';
      card.style.opacity = '.55';
    });
    overlay.addEventListener('dragend', event => {
      const card = event.target.closest('[data-equipment-type]');
      if (card) card.style.opacity = '';
    });
    renderTab('equipment');
    return overlay;
  }

  function renderEquipment() {
    const content = overlay.querySelector('#' + TAB_CONTENT_ID);
    content.innerHTML = '';
    equipmentGroups.forEach(group => {
      const section = document.createElement('section');
      section.className = 'st-library-group';
      const title = document.createElement('h3');
      title.className = 'st-library-group-title';
      title.textContent = group.title;
      const grid = document.createElement('div');
      grid.className = 'st-library-grid';
      group.items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'st-library-card st-library-device';
        card.draggable = true;
        card.dataset.equipmentType = item.type;
        card.title = 'Glisser ' + item.label + ' sur la topologie';
        card.setAttribute('role', 'listitem');
        card.innerHTML = '<span class="st-library-symbol" style="color:' + item.color + '">' + item.symbol + '</span><span class="st-library-name"></span><span class="st-library-detail"></span>';
        card.querySelector('.st-library-name').textContent = item.label;
        card.querySelector('.st-library-detail').textContent = item.detail;
        grid.appendChild(card);
      });
      section.append(title, grid);
      content.appendChild(section);
    });
    overlay.querySelector('[data-library-count]').textContent = '6 types';
    overlay.querySelector('[data-library-footer]').textContent = 'Glisse un équipement sur le schéma. Tu peux déposer plusieurs exemplaires du même type.';
  }

  function findToolButton(tool) {
    const title = toolTitles[tool];
    return title ? Array.from(document.querySelectorAll('button[title]')).find(button => button.title === title) : null;
  }
  function activeTool() {
    for (const tool of ['cable_straight', 'cable_cross', 'fiber']) {
      const button = findToolButton(tool);
      if (button && button.classList.contains('shadow-inner')) return tool;
    }
    return 'select';
  }
  function refreshSelectedTool() {
    if (!overlay || overlay.querySelector('[data-library-tab="cables"]').getAttribute('aria-selected') !== 'true') return;
    const active = activeTool();
    overlay.querySelectorAll('[data-tool]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.tool === active)));
    const cable = cables.find(item => item.tool === active);
    overlay.querySelector('[data-library-footer]').textContent = cable
      ? 'Type sélectionné : ' + cable.title + '. Relie un port source à un port cible.'
      : 'Choisis un câble pour commencer une liaison entre deux ports.';
  }
  function selectTool(tool) {
    const button = findToolButton(tool);
    if (!button) {
      overlay.querySelector('[data-library-footer]').textContent = 'Le mode de connexion n’est pas encore disponible sur ce canvas.';
      return;
    }
    button.click();
    refreshSelectedTool();
  }
  function renderCables() {
    const content = overlay.querySelector('#' + TAB_CONTENT_ID);
    content.innerHTML = '';
    const select = document.createElement('button');
    select.type = 'button';
    select.className = 'st-library-select';
    select.dataset.tool = 'select';
    select.setAttribute('aria-pressed', String(activeTool() === 'select'));
    select.textContent = '↖  Sélection / déplacement';
    select.addEventListener('click', () => selectTool('select'));
    content.appendChild(select);
    const grid = document.createElement('div');
    grid.className = 'st-library-grid';
    cables.forEach(cable => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'st-library-card st-library-cable';
      button.dataset.tool = cable.tool;
      button.setAttribute('aria-pressed', String(activeTool() === cable.tool));
      button.innerHTML = '<span class="st-library-line"><svg viewBox="0 0 100 16" aria-hidden="true"><path d="M4 8 H96" fill="none" stroke="' + cable.color + '" stroke-width="3" stroke-linecap="round" ' + (cable.dash ? 'stroke-dasharray="' + cable.dash + '"' : '') + ' /><circle cx="4" cy="8" r="3" fill="' + cable.color + '"/><circle cx="96" cy="8" r="3" fill="' + cable.color + '"/></svg></span><span class="st-library-name"></span><span class="st-library-detail"></span>';
      button.querySelector('.st-library-name').textContent = cable.title;
      button.querySelector('.st-library-detail').textContent = cable.detail;
      button.addEventListener('click', () => selectTool(cable.tool));
      grid.appendChild(button);
    });
    content.appendChild(grid);
    const hint = document.createElement('div');
    hint.className = 'st-library-hint';
    hint.textContent = '1. Choisis un câble. 2. Relie un port source à un port cible sur les équipements. 3. Change de type avant la liaison suivante.';
    content.appendChild(hint);
    overlay.querySelector('[data-library-count]').textContent = '3 types';
    overlay.querySelector('[data-library-footer]').textContent = 'Choisis un type de câble, puis relie deux ports sur le schéma.';
    refreshSelectedTool();
  }
  function renderTab(tab) {
    if (!overlay) return;
    overlay.querySelectorAll('[data-library-tab]').forEach(button => button.setAttribute('aria-selected', String(button.dataset.libraryTab === tab)));
    overlay.querySelector('.st-library-title').textContent = tab === 'cables'
      ? 'Bibliothèque de câbles'
      : 'Bibliothèque d’équipements';
    if (tab === 'cables') renderCables(); else renderEquipment();
  }
  function restorePanel(element) {
    if (!element) return;
    const oldValue = element.dataset.stLibraryOriginalVisibility;
    if (oldValue === '__empty__') element.style.removeProperty('visibility');
    else if (oldValue !== undefined) element.style.visibility = oldValue;
    delete element.dataset.stLibraryOriginalVisibility;
  }
  function positionOverlay() {
    const latestPanel = document.querySelector('[data-testid="equipment-palette-panel"]');
    if (!latestPanel) return;
    if (latestPanel.querySelector('[data-library-tabs]')) {
      restorePanel(latestPanel);
      overlay?.remove();
      overlay = null;
      return;
    }
    if (panel !== latestPanel) {
      restorePanel(panel);
      panel = latestPanel;
      panel.dataset.stLibraryOriginalVisibility = panel.style.visibility || '__empty__';
    }
    panel.style.visibility = 'hidden';
    const rect = panel.getBoundingClientRect();
    if (!rect.width || !rect.height) {
      if (overlay) overlay.style.display = 'none';
      return;
    }
    createOverlay();
    overlay.style.display = 'flex';
    overlay.style.left = rect.left + 'px';
    overlay.style.top = rect.top + 'px';
    overlay.style.width = rect.width + 'px';
    overlay.style.height = rect.height + 'px';
    Object.values(toolTitles).forEach(title => {
      const button = Array.from(document.querySelectorAll('button[title]')).find(item => item.title === title);
      if (!button) return;
      button.style.visibility = 'hidden';
      if (!watchedTools.has(button)) {
        watchedTools.add(button);
        toolObserver.observe(button, { attributes: true, attributeFilter: ['class'] });
      }
    });
    refreshSelectedTool();
  }
  function schedulePosition() {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; positionOverlay(); });
  }
  const observer = new MutationObserver(schedulePosition);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener('resize', schedulePosition);
  if (window.ResizeObserver) new ResizeObserver(schedulePosition).observe(document.documentElement);
  schedulePosition();
})();