import { useState } from 'react';
import { useLabStore } from '../store/useLabStore.js';
import { useTicketStore } from '../war/useTicketStore.js';

export function TopologyToolbar({ onOpenPostMortem }) {
  const topology = useLabStore(s => s.topology);
  const lab = useLabStore(s => s.lab);
  const loadLab = useLabStore(s => s.loadLab);
  const checkResult = useLabStore(s => s.checkResult);
  const loading = useLabStore(s => s.loading);
  const ticket = useTicketStore(s => s.ticket);
  const [persistenceAction, setPersistenceAction] = useState(null);
  const persistenceBusy = persistenceAction !== null;
  const [persistenceMessage, setPersistenceMessage] = useState('');

  async function handleSave() {
    if (!lab?.id || lab.id === 'demo' || !topology || persistenceBusy) return;
    setPersistenceAction('save');
    setPersistenceMessage('');
    try {
      const response = await fetch('/api/lab/v2/' + encodeURIComponent(lab.id) + '/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
      setPersistenceMessage('Topologie sauvegardée');
    } catch (error) {
      setPersistenceMessage('Échec de sauvegarde : ' + error.message);
    } finally {
      setPersistenceAction(null);
    }
  }

  async function handleLoad() {
    if (!lab?.id || lab.id === 'demo' || persistenceBusy) return;
    setPersistenceAction('load');
    setPersistenceMessage('');
    try {
      const response = await fetch('/api/lab/v2/' + encodeURIComponent(lab.id) + '/load');
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
      if (!payload.topology) throw new Error('La réponse ne contient aucune topologie.');
      loadLab(lab.id, lab, payload.topology);
      setPersistenceMessage('Topologie chargée');
    } catch (error) {
      setPersistenceMessage('Échec de chargement : ' + error.message);
    } finally {
      setPersistenceAction(null);
    }
  }

  const handleCheck = async () => {
    const state = useLabStore.getState();
    if (state.loading || persistenceBusy || state.lab?.id === 'demo' || state.lab?.sandbox === true) return;
    if (!ticket) {
      window.dispatchEvent(new CustomEvent('lab:check', { detail: {} }));
      return;
    }
    if (ticket.status === 'failed' || ticket.status === 'resolved') {
      setPersistenceMessage(ticket.status === 'failed'
        ? 'Ticket échoué. Consultez l’Archive pour le rejouer avec un nouveau délai SLA.'
        : 'Ticket déjà résolu.');
      return;
    }
    if (ticket.status === 'pending_postmortem') {
      onOpenPostMortem?.();
      return;
    }
    setPersistenceAction('resolve');
    setPersistenceMessage('');
    try {
      const openedAt = ticket.opened_at ? new Date(ticket.opened_at).getTime() : Date.now();
      const elapsedSeconds = Math.max(0, Math.floor((Date.now() - openedAt) / 1000));
      const response = await fetch('/api/tickets/' + encodeURIComponent(ticket.id) + '/resolve', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
        body: JSON.stringify({ topology: useLabStore.getState().topology, elapsed_seconds: elapsedSeconds }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
      if (!payload.passed) {
        const failed = (payload.checks || []).filter(check => !check.passed).map(check => check.description || (check.target + ' · ' + check.path));
        const reason = payload.reason || 'config_incorrect';
        const message = reason === 'sla_exceeded'
          ? '❌ SLA dépassé : le ticket est marqué comme échoué. Rejouez-le depuis l’Archive.'
          : '❌ Configuration incorrecte : le ticket est marqué comme échoué. Rejouez-le depuis l’Archive.';
        const detail = failed.length ? ' À corriger : ' + failed.join(', ') : '';
        const state = useTicketStore.getState();
        state.setTicket({ ...ticket, status: 'failed', failure_reason: reason }, state.scenario, state.sla_left);
        setPersistenceMessage(message + detail);
        window.alert(message + detail);
        return;
      }
      useTicketStore.getState().setTicket({ ...ticket, status: 'pending_postmortem' }, useTicketStore.getState().scenario, useTicketStore.getState().sla_left);
      setPersistenceMessage(payload.message || 'Configuration validée. Post-mortem requis.');
      onOpenPostMortem?.();
    } catch (error) {
      setPersistenceMessage('Échec de résolution : ' + error.message);
    } finally { setPersistenceAction(null); }
  };
  const handleSubmit = () => {
    const state = useLabStore.getState();
    const result = state.checkResult;
    if (
      state.loading ||
      ticket ||
      state.lab?.id === 'demo' ||
      state.lab?.sandbox === true ||
      !result ||
      result.stale ||
      result.checkError ||
      result.submissionError ||
      result.ok === true
    ) return;
    window.dispatchEvent(new CustomEvent('lab:submit', { detail: {} }));
  };
  const handleClose = () => window.dispatchEvent(new CustomEvent('lab:close', { detail: {} }));
  const persistenceDisabled = persistenceBusy || !lab || lab.id === 'demo';
  const submitDisabled =
    loading ||
    lab?.id === 'demo' ||
    lab?.sandbox === true ||
    lab?.courseLocked === true ||
    !checkResult ||
    checkResult.stale ||
    checkResult.checkError ||
    checkResult.submissionError ||
    checkResult.ok === true;

  return (
    <div className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-[var(--s2)] bg-[var(--s1)] px-4 py-2.5">
      <div className="min-w-0">
        <div className="font-mono text-xs text-[var(--text-secondary)]">
          {topology?.nodes?.length || 0} équipements · {topology?.links?.length || 0} liaisons
          {checkResult && (
            <span className={checkResult.stale ? 'ml-3 text-[var(--amber-400)]' : checkResult.sandbox === true ? 'ml-3 text-[var(--text-secondary)]' : checkResult.passed ? 'ml-3 text-[var(--emerald-400)]' : 'ml-3 text-[var(--rose-400)]'}>
              {checkResult.stale
                ? '⚠ Configuration modifiée — revérifier'
                : checkResult.checkError
                  ? 'Erreur de vérification'
                  : checkResult.sandbox === true
                    ? 'Bac à sable — non noté'
                    : checkResult.ok === true
                      ? (checkResult.passed ? '✓ Tentative enregistrée' : 'Tentative enregistrée — échec')
                      : checkResult.practice_only === true
                        ? (checkResult.passed
                          ? '✓ Réussi en entraînement'
                          : 'Entraînement · Score ' + Math.round((checkResult.score || 0) * 100) + '%')
                        : checkResult.passed
                          ? '✓ Réussi'
                          : 'Score ' + Math.round((checkResult.score || 0) * 100) + '%'}
            </span>
          )}
        </div>
        {Array.isArray(checkResult?.results) && checkResult.results.length > 0 && checkResult.sandbox !== true && (
          <div role="region" aria-label="Détails des vérifications" aria-live="polite" className="mt-2 max-h-36 overflow-y-auto rounded-lg border border-[var(--s2)] bg-[var(--s0)] p-2">
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-[var(--text-secondary)]">Détails des vérifications</p>
            <ul className="space-y-1.5">
              {checkResult.results.map((item, index) => (
                <li
                  key={String(item.rule_id || 'rule') + '-' + index}
                  className={`flex items-start gap-2 text-xs ${item.passed ? 'text-[var(--emerald-400)]' : 'text-[var(--rose-400)]'}`}
                >
                  <span aria-hidden="true" className="shrink-0 font-bold">{item.passed ? '✓' : '✕'}</span>
                  <span className="min-w-0 break-words">{item.message || item.rule_id || 'Règle sans description'}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {persistenceMessage && <p role="status" className="mt-1 text-[10px] text-[var(--text-secondary)]">{persistenceMessage}</p>}
        {checkResult?.sandbox === true && (
          <p role="status" className="mt-1 text-xs text-[var(--text-secondary)]">
            {checkResult.results?.[0]?.message || 'Ce bac à sable permet de tester librement, sans note ni récompense.'}
          </p>
        )}
        {checkResult?.ok === true && checkResult.sandbox !== true && (
          <div role="status" className="mt-1 text-xs text-[var(--text-secondary)]">
            <p>
              {checkResult.passed
                ? (Number(checkResult.xp_gained) > 0
                  ? '+' + Number(checkResult.xp_gained) + ' XP obtenus.'
                  : checkResult.first_success
                    ? 'Lab réussi : aucune récompense XP n’est configurée pour ce lab.'
                    : 'Lab réussi : la récompense XP a déjà été attribuée lors d’une réussite précédente.')
                : 'Tentative enregistrée sans récompense XP.'}
              {checkResult.course_attempt_recorded
                ? ' Progression du parcours mise à jour.'
                : checkResult.passed
                  ? ' Le parcours reste inchangé : aucun cours lié ou prérequis encore verrouillés.'
                  : ''}
            </p>
            {Array.isArray(checkResult.badges_unlocked) && checkResult.badges_unlocked.length > 0 && (
              <p className="mt-1 text-[var(--emerald-400)]">
                Badge(s) débloqué(s) : {checkResult.badges_unlocked.map(badge =>
                  typeof badge === 'string' ? badge : (badge.nom || badge.name || badge.id || 'Badge')
                ).join(', ')}
              </p>
            )}
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={handleSave} disabled={persistenceDisabled}
          title={lab?.id === 'demo' ? 'Indisponible dans la démo' : 'Enregistrer la topologie'}
          className="rounded-md border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-[#c9d1d9] hover:border-[#0ea5e9] hover:text-white disabled:cursor-not-allowed disabled:opacity-40">
          {persistenceAction === 'save' ? 'Enregistrement…' : 'Sauvegarder'}
        </button>
        <button type="button" onClick={handleLoad} disabled={persistenceDisabled}
          title={lab?.id === 'demo' ? 'Indisponible dans la démo' : 'Charger la dernière topologie sauvegardée'}
          className="rounded-md border border-[#30363d] bg-[#161b22] px-3 py-1.5 text-xs font-semibold text-[#c9d1d9] hover:border-[#0ea5e9] hover:text-white disabled:cursor-not-allowed disabled:opacity-40">
          {persistenceAction === 'load' ? 'Chargement…' : 'Charger'}
        </button>
        <button type="button" onClick={handleCheck}
          disabled={loading || persistenceBusy || lab?.id === 'demo' || lab?.sandbox === true || ticket?.status === 'failed' || ticket?.status === 'resolved'}
          title={lab?.courseLocked === true
            ? 'Mode entraînement : le contrôle est disponible, mais la validation du parcours reste bloquée. ' + (lab.courseLockMessage || '')
            : lab?.sandbox === true
              ? 'Atelier libre : aucun scénario de validation n’est associé.'
              : lab?.id === 'demo'
                ? 'La démonstration ne peut pas être vérifiée.'
                : 'Vérifier les règles du scénario'}
          className="btn-glow transition-all duration-300 rounded-lg bg-gradient-to-r from-[var(--emerald-400)] to-[var(--cyan-400)] px-3.5 py-1.5 text-xs font-semibold text-[var(--on-accent)] disabled:opacity-50">
          {persistenceAction === 'resolve' ? 'Vérification…' : ticket?.status === 'failed' ? '❌ Ticket échoué' : ticket?.status === 'resolved' ? '✅ Ticket résolu' : ticket ? '📝 Résoudre le ticket' : loading ? '…' : lab?.courseLocked === true ? '✓ Vérifier en entraînement' : '✓ Vérifier'}
        </button>
        {!ticket && (
        <button type="button" onClick={handleSubmit} disabled={submitDisabled}
          title={lab?.courseLocked === true
            ? (lab.courseLockMessage || 'Ce laboratoire est verrouillé par les prérequis du parcours.')
            : lab?.id === 'demo'
              ? 'La démo ne peut pas être soumise'
            : checkResult?.ok === true
              ? 'Cette vérification a déjà été soumise. Modifiez la configuration puis revérifiez-la.'
              : submitDisabled
                ? 'Vérifiez la configuration avant de soumettre'
                : 'Enregistrer cette tentative et son résultat côté serveur'}
          className="btn-glow transition-all duration-300 rounded-lg border border-[var(--s2)] bg-[var(--s2)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--s3)] disabled:cursor-not-allowed disabled:opacity-40">
          ↑ Soumettre
        </button>
      )}
        <button type="button" onClick={handleClose}
          className="rounded-lg border border-[var(--s2)] bg-[var(--s2)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--s3)]">
          ✕ Fermer
        </button>
      </div>
    </div>
  );
}
