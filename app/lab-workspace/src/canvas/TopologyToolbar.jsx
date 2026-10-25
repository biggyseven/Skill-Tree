import { useLabStore } from '../store/useLabStore.js';

export function TopologyToolbar() {
  const topology = useLabStore(s => s.topology);
  const lab = useLabStore(s => s.lab);
  const checkResult = useLabStore(s => s.checkResult);
  const loading = useLabStore(s => s.loading);

  const handleCheck = () => window.dispatchEvent(new CustomEvent('lab:check', { detail: {} }));
  const handleSubmit = () => window.dispatchEvent(new CustomEvent('lab:submit', { detail: {} }));
  const handleClose = () => window.dispatchEvent(new CustomEvent('lab:close', { detail: {} }));

  return (
    <div className="flex shrink-0 items-center justify-between border-b border-[var(--s2)] bg-[var(--s1)] px-5 py-3">
      <div className="font-mono text-xs text-[var(--text-secondary)]">
        {topology?.nodes?.length || 0} devices · {topology?.links?.length || 0} links
        {checkResult && (
          <span className={checkResult.passed ? 'ml-4 text-[var(--emerald-400)]' : 'ml-4 text-[var(--rose-400)]'}>
            {checkResult.passed ? '✓ Passé' : 'Score ' + Math.round((checkResult.score || 0) * 100) + '%'}
          </span>
        )}
      </div>
      <div className="flex gap-2">
        <button onClick={handleCheck} disabled={loading}
          className="rounded-lg bg-gradient-to-r from-[var(--emerald-400)] to-[var(--cyan-400)] px-3.5 py-1.5 text-xs font-semibold text-[var(--on-accent)] disabled:opacity-50">
          {loading ? '…' : '✓ Vérifier'}
        </button>
        <button onClick={handleSubmit} disabled={loading || lab?.id === 'demo'}
          title={lab?.id === 'demo' ? 'La démo ne peut pas être soumise' : 'Recalculer et enregistrer le résultat côté serveur'}
          className="rounded-lg border border-[var(--s2)] bg-[var(--s2)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--s3)] disabled:opacity-40">
          ↑ Soumettre
        </button>
        <button onClick={handleClose}
          className="rounded-lg border border-[var(--s2)] bg-[var(--s2)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-primary)] hover:border-[var(--s3)]">
          ✕ Fermer
        </button>
      </div>
    </div>
  );
}
