import { useLabStore } from '../store/useLabStore.js';

export function BriefPanel() {
  const lab = useLabStore(s => s.lab);
  const checkResult = useLabStore(s => s.checkResult);
  if (!lab) return null;

  return (
    <div className="space-y-4 p-5 text-[13px] leading-relaxed">
      <div>
        <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-[var(--text-muted)]">
          {lab.level || 'Lab'}
        </div>
        <h1 className="mt-1 text-[18px] font-bold leading-tight text-[var(--text-primary)]">{lab.title}</h1>
      </div>

      {lab.prompt && <p className="text-[var(--text-secondary)]">{lab.prompt}</p>}

      {Array.isArray(lab.objectives) && lab.objectives.length > 0 && (
        <div>
          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--text-muted)]">Objectifs</div>
          <ul className="list-disc space-y-1 pl-5 text-[var(--text-secondary)]">
            {lab.objectives.map((o, i) => <li key={i}>{o}</li>)}
          </ul>
        </div>
      )}

      {checkResult && (
        <div className={'mt-4 rounded-xl border p-3.5 ' + (checkResult.passed
          ? 'border-[rgba(16,185,129,0.3)] bg-[rgba(16,185,129,0.08)]'
          : 'border-[rgba(251,113,133,0.3)] bg-[rgba(251,113,133,0.08)]')}>
          <div className="mb-2 font-bold text-[var(--text-primary)]">
            {checkResult.passed ? '🎉 Lab réussi !' : 'Score : ' + Math.round((checkResult.score || 0) * 100) + ' %'}
          </div>
          {Array.isArray(checkResult.results) && checkResult.results.map(r => (
            <div key={r.rule_id} className={'mb-1 flex gap-2 text-xs ' + (r.passed ? 'text-[var(--emerald-400)]' : 'text-[var(--rose-400)]')}>
              <span>{r.passed ? '✓' : '✗'}</span>
              <span>{r.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
