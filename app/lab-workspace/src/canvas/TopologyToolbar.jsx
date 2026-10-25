import { useState } from 'react';
import { useLabStore } from '../store/useLabStore.js';

export function TopologyToolbar() {
  const topology = useLabStore(s => s.topology);
  const lab = useLabStore(s => s.lab);
  const loadLab = useLabStore(s => s.loadLab);
  const checkResult = useLabStore(s => s.checkResult);
  const loading = useLabStore(s => s.loading);
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

  const handleCheck = () => {
    if (useLabStore.getState().loading) return;
    window.dispatchEvent(new CustomEvent('lab:check', { detail: {} }));
  };
  const handleSubmit = () => {
    const state = useLabStore.getState();
    const result = state.checkResult;
    if (
      state.loading ||
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
                      : checkResult.passed
                      ? '✓ Réussi'
                      : 'Score ' + Math.round((checkResult.score || 0) * 100) + '%'}
            </span>
          )}
        </div>
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
                  : 'Lab réussi : la récompense XP de ce lab a déjà été attribuée.')
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
        <button type="button" onClick={handleCheck} disabled={loading}
          className="rounded-lg bg-gradient-to-r from-[var(--emerald-400)] to-[var(--cyan-400)] px-3.5 py-1.5 text-xs font-semibold text-[var(--on-accent)] disabled:opacity-50">
          {loading ? '…' : '✓ Vérifier'}
        </button>
        <button type="button" onClick={handleSubmit} disabled={submitDisabled}
          title={lab?.id === 'demo'
            ? 'La démo ne peut pas être soumise'
            : checkResult?.ok === true
              ? 'Cette vérification a déjà été soumise. Modifiez la configuration puis revérifiez-la.'
              : submitDisabled
                ? 'Vérifiez la configuration avant de soumettre'
                : 'Enregistrer cette tentative et son résultat côté serveur'}
          className="rounded-lg border border-[var(--s2)] bg-[var(--s2)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--s3)] disabled:cursor-not-allowed disabled:opacity-40">
          ↑ Soumettre
        </button>
        <button type="button" onClick={handleClose}
          className="rounded-lg border border-[var(--s2)] bg-[var(--s2)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--s3)]">
          ✕ Fermer
        </button>
      </div>
    </div>
  );
}
