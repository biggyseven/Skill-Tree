import { useLabStore } from '../store/useLabStore.js';

export function BriefPanel() {
  const lab = useLabStore(s => s.lab);
  const checkResult = useLabStore(s => s.checkResult);
  if (!lab) return null;

  return (
    <div className="space-y-5 p-5 text-[13px] leading-relaxed">
      <div>
        <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#64748b]">
          {lab.level || 'Lab'}
        </div>
        <h1 className="mt-1 text-lg font-bold leading-tight text-white">{lab.title}</h1>
      </div>

      {lab.prompt && (
        <section className="rounded-xl border border-[#0ea5e9]/25 bg-[#0ea5e9]/[0.06] p-4" aria-label="Mise en contexte du laboratoire">
          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#38bdf8]">Mise en contexte</div>
          <p className="text-[12px] leading-relaxed text-[#cbd5e1]">{lab.prompt}</p>
        </section>
      )}

      {Array.isArray(lab.objectives) && lab.objectives.length > 0 && (
        <div>
          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#64748b]">Objectifs</div>
          <ul className="list-disc space-y-1.5 pl-4 text-[#cbd5e1]">
            {lab.objectives.map((o, i) => <li key={i}>{o}</li>)}
          </ul>
        </div>
      )}

      {Array.isArray(lab.hints) && lab.hints.length > 0 && (
        <section className="rounded-xl border border-[#d29922]/25 bg-[#d29922]/[0.06] p-3.5" aria-label="Indices pour réussir">
          <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#e3b341]">
            <span aria-hidden="true">💡</span> Indices
          </div>
          <ol className="list-decimal space-y-2 pl-4 text-xs leading-relaxed text-[#e6edf3]">
            {lab.hints.map((hint, i) => <li key={i}>{hint}</li>)}
          </ol>
        </section>
      )}

      {/* ZONE DE RESULTAT DU CHECK */}
      {checkResult?.stale && (
        <div role="status" className="rounded-lg border border-[#f59e0b]/30 bg-[#f59e0b]/10 px-3 py-2 text-xs leading-relaxed text-[#fcd34d]">
          {checkResult.ok === true
            ? 'La tentative a été enregistrée pour la configuration envoyée, mais la topologie a changé pendant le traitement. Vérifiez à nouveau la configuration actuelle.'
            : 'La topologie a changé pendant la vérification. Relancez le contrôle avant de soumettre.'}
        </div>
      )}
      {typeof checkResult?.xp_gained === 'number' && (
        <div className="rounded-lg border border-[#10b981]/30 bg-[#10b981]/10 px-3 py-2 text-xs text-[#a7f3d0]">
          {checkResult.passed
            ? (checkResult.xp_gained > 0 ? `Laboratoire enregistré · +${checkResult.xp_gained} XP` : 'Laboratoire enregistré · récompense déjà obtenue')
            : 'Tentative enregistrée sans récompense.'}
        </div>
      )}
      {checkResult && (
        <div className="mt-6 rounded-xl border border-[#334155] bg-[#1e293b] p-4 shadow-xl">
          <div className="mb-3 flex items-center justify-between border-b border-[#334155] pb-2">
            <span className="font-bold text-white">Résultat</span>
            <span className={`text-sm font-bold ${checkResult.passed ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
              {Math.round((checkResult.score || 0) * 100)}%
            </span>
          </div>
          <div className="space-y-2">
            {Array.isArray(checkResult.results) && checkResult.results.map(r => (
              <div key={r.rule_id} className="flex gap-2 text-xs">
                <span className={r.passed ? 'text-[#10b981]' : 'text-[#f43f5e]'}>
                  {r.passed ? '✓' : '✗'}
                </span>
                <span className="text-[#cbd5e1]">{r.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
