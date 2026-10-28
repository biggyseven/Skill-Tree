import { useState } from 'react';
import { useTicketStore } from './useTicketStore.js';

export function PostMortemModal({ onClose }) {
  const ticket = useTicketStore(s => s.ticket);
  const [rootCause, setRootCause] = useState('');
  const [impact, setImpact] = useState('');
  const [correctiveAction, setCorrectiveAction] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  if (!ticket) return null;

  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError('');
    try {
      const response = await fetch('/api/tickets/' + encodeURIComponent(ticket.id) + '/post-mortem', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
        body: JSON.stringify({ root_cause: rootCause, impact, corrective_action: correctiveAction }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = Array.isArray(payload.detail) ? payload.detail.map(item => item.msg).join(' · ') : payload.detail;
        throw new Error(detail || 'HTTP ' + response.status);
      }
      setSuccess('Ticket clôturé. +' + (payload.xp_earned || 0) + ' XP ajoutés.');
      window.setTimeout(() => window.location.assign('/?openTab=war'), 850);
    } catch (submitError) {
      setError(submitError.message || 'Le post-mortem n’a pas pu être enregistré.');
    } finally { setBusy(false); }
  }

  const textareaClass = 'mt-2 min-h-[96px] w-full resize-y rounded-xl border border-[#30363d] bg-[#0d1117] px-3 py-2.5 text-sm text-[#e6edf3] outline-none transition focus:border-[#0ea5e9] focus:ring-2 focus:ring-[#0ea5e9]/20';
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto bg-black/75 p-4 backdrop-blur-sm" role="presentation">
      <form onSubmit={submit} role="dialog" aria-modal="true" aria-labelledby="war-postmortem-title" className="my-6 w-full max-w-2xl rounded-2xl border border-[#30363d] bg-[#161b22] p-5 shadow-2xl sm:p-7">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#38bdf8]">Gestion des problèmes · ITSM</p>
            <h2 id="war-postmortem-title" className="mt-1 text-xl font-bold text-white">Post-mortem — {ticket.id}</h2>
            <p className="mt-2 text-xs text-[#8b949e]">Documentez la cause, l’impact et les actions correctives avant clôture.</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-lg border border-[#30363d] px-2.5 py-1.5 text-sm text-[#8b949e] hover:text-white" aria-label="Fermer">✕</button>
        </div>
        <label className="block text-xs font-semibold text-[#e6edf3]">Cause racine
          <textarea className={textareaClass} minLength={3} maxLength={5000} required value={rootCause} onChange={event => setRootCause(event.target.value)} placeholder="Cause technique démontrée par les éléments du diagnostic…" />
        </label>
        <label className="mt-4 block text-xs font-semibold text-[#e6edf3]">Impact
          <textarea className={textareaClass} minLength={3} maxLength={5000} required value={impact} onChange={event => setImpact(event.target.value)} placeholder="Services, utilisateurs et durée affectés…" />
        </label>
        <label className="mt-4 block text-xs font-semibold text-[#e6edf3]">Action corrective / préventive
          <textarea className={textareaClass} minLength={3} maxLength={5000} required value={correctiveAction} onChange={event => setCorrectiveAction(event.target.value)} placeholder="Correction appliquée, prévention et suivi…" />
        </label>
        {error && <div role="alert" className="mt-4 rounded-lg border border-[#f85149]/30 bg-[#f85149]/10 p-3 text-xs text-[#ffb4ad]">{error}</div>}
        {success && <div role="status" className="mt-4 rounded-lg border border-[#3fb950]/30 bg-[#3fb950]/10 p-3 text-xs text-[#7ee787]">{success}</div>}
        <div className="mt-6 flex flex-wrap justify-end gap-2">
          <button type="button" onClick={onClose} disabled={busy} className="rounded-xl border border-[#30363d] px-4 py-2.5 text-xs font-semibold text-[#c9d1d9] hover:bg-white/5 disabled:opacity-50">Continuer plus tard</button>
          <button type="submit" disabled={busy || !!success} className="rounded-xl bg-gradient-to-r from-[var(--emerald-400)] to-[var(--cyan-400)] px-4 py-2.5 text-xs font-bold text-[var(--on-accent)] disabled:opacity-50">{busy ? 'Enregistrement…' : 'Valider le post-mortem'}</button>
        </div>
      </form>
    </div>
  );
}
