(() => {
  'use strict';
  const ticketId = new URLSearchParams(window.location.search).get('ticket');
  if (!ticketId) return;
  let ticket = null, openCount = 0, busy = false, observer = null;

  const api = async (path, options = {}) => {
    const response = await fetch(path, { credentials: 'same-origin', cache: 'no-store',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.detail || ('HTTP ' + response.status));
    return payload;
  };

  function findSlaSection() {
    return Array.from(document.querySelectorAll('section')).find(section => {
      const label = (section.innerText || section.textContent || '').replace(/\s+/g, ' ');
      return /\bSLA\b/.test(label) && (label.includes('Objectif :') || label.includes('Analyse de problème'));
    }) || null;
  }

  function paintStatus() {
    const toolbar = document.querySelector('[data-war-room-controls]');
    if (!toolbar) return;
    const banner = toolbar.querySelector('[data-war-noc-alert]');
    const button = toolbar.querySelector('[data-war-action]');
    const message = toolbar.querySelector('[data-war-message]');
    if (banner) banner.hidden = openCount <= 2;
    if (!button) return;
    const status = ticket && ticket.status;
    if (status === 'pending_postmortem') {
      button.hidden = true;
      if (message && !message.textContent) message.textContent = 'Configuration validée : finalisez le post-mortem pour clôturer le ticket.';
    } else if (status === 'resolved' || status === 'failed') {
      button.hidden = true;
    } else {
      button.hidden = false;
      button.textContent = status === 'paused' ? '▶ Reprendre' : '⏸ Mettre en pause';
      button.disabled = busy;
      button.dataset.action = status === 'paused' ? 'resume' : 'pause';
    }
  }

  function addControls() {
    if (!ticket) return;
    const section = findSlaSection();
    if (!section || section.querySelector('[data-war-room-controls]')) return;
    const toolbar = document.createElement('div');
    toolbar.dataset.warRoomControls = 'true';
    toolbar.className = 'mt-3 space-y-2';
    toolbar.innerHTML = [
      '<div data-war-noc-alert hidden role="status" class="rounded-lg border border-amber-400/30 bg-amber-500/10 px-3 py-2 text-[11px] font-bold text-amber-200">🔥 Situation NOC : plusieurs incidents en cours</div>',
      '<div class="flex flex-wrap items-center gap-2">',
      '<button type="button" data-war-action class="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-xs font-bold text-rose-100 transition hover:bg-rose-500/20 disabled:opacity-50"></button>',
      '<span data-war-message role="status" class="text-[11px] text-amber-200"></span></div>'
    ].join('');
    toolbar.querySelector('[data-war-action]').addEventListener('click', async () => {
      const button = toolbar.querySelector('[data-war-action]');
      const action = button.dataset.action;
      if (busy || !action) return;
      busy = true; button.disabled = true;
      const message = toolbar.querySelector('[data-war-message]');
      if (message) message.textContent = '';
      try {
        await api('/api/tickets/' + encodeURIComponent(ticketId) + '/' + action, { method: 'POST', body: '{}' });
        if (action === 'pause') { window.location.assign('/?openTab=war'); return; }
        const detail = await api('/api/tickets/' + encodeURIComponent(ticketId));
        ticket = detail.ticket || ticket;
        paintStatus();
        if (message) message.textContent = 'SLA repris. Le temps restant est restauré.';
      } catch (error) {
        if (message) message.textContent = 'Action impossible : ' + error.message;
      } finally {
        busy = false; paintStatus();
      }
    });
    section.appendChild(toolbar);
    paintStatus();
  }

  async function loadTicket() {
    try {
      const payload = await api('/api/tickets/' + encodeURIComponent(ticketId));
      ticket = payload.ticket || null;
      addControls(); paintStatus();
    } catch (error) {
      const message = document.querySelector('[data-war-message]');
      if (message) message.textContent = 'Ticket indisponible : ' + error.message;
    }
  }

  async function updateCount() {
    try {
      const payload = await api('/api/tickets/open-count');
      openCount = Math.max(0, Number(payload.count) || 0);
      paintStatus();
    } catch (_) { /* Le Lab reste utilisable si le compteur n'est pas joignable. */ }
  }

  function boot() {
    loadTicket(); updateCount();
    window.setInterval(updateCount, 5000);
    observer = new MutationObserver(() => { addControls(); paintStatus(); });
    observer.observe(document.documentElement, { childList: true, subtree: true });
    window.addEventListener('beforeunload', () => observer && observer.disconnect(), { once: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
