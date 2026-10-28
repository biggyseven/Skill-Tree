import { useTicketStore } from '../war/useTicketStore.js';

export function TicketPanel() {
  const ticket = useTicketStore(s => s.ticket);
  const scenario = useTicketStore(s => s.scenario);
  const slaLeft = useTicketStore(s => s.sla_left);
  if (!ticket || !scenario) return null;

  return (
    <div className="space-y-5 p-5 text-[13px] leading-relaxed">
      <div>
        <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#64748b]">War Room · {String(ticket.type || 'ticket').toUpperCase()}</div>
        <h1 className="mt-1 text-lg font-bold leading-tight text-white">{scenario.title}</h1>
        <p className="mt-2 text-[11px] font-mono text-[#8b949e]">{ticket.id} · signalé par {scenario.reported_by || 'NOC'}</p>
      </div>
      <section className="rounded-xl border border-[#0ea5e9]/25 bg-[#0ea5e9]/[0.06] p-4" aria-label="Contexte du ticket">
        <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#38bdf8]">Brief opérationnel</div>
        <p className="text-[12px] leading-relaxed text-[#cbd5e1]">{scenario.story}</p>
      </section>
      <section className="rounded-xl border border-[#30363d] bg-[#0d1117]/70 p-4">
        <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.16em] text-[#8b949e]">Impact métier</div>
        <p className="text-[12px] leading-relaxed text-[#e6edf3]">{scenario.impact}</p>
      </section>
      <section className="rounded-xl border border-[#30363d] bg-[#0d1117]/70 p-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#8b949e]">SLA</h2>
          <span className={'font-mono text-xs font-bold ' + (slaLeft !== null && slaLeft <= 300 ? 'text-[#ff7b72]' : 'text-[#7ee787]')}>{slaLeft === null || slaLeft === undefined ? 'Sans SLA' : Math.floor(slaLeft / 60) + ' min ' + String(Math.floor(slaLeft % 60)).padStart(2, '0') + ' s'}</span>
        </div>
        <p className="mt-1 text-[11px] text-[#8b949e]">{scenario.sla_minutes ? 'Objectif : ' + scenario.sla_minutes + ' minutes' : 'Analyse de problème sans échéance SLA.'}</p>
      </section>
      <section aria-label="Étapes de diagnostic">
        <h2 className="mb-3 text-[10px] font-bold uppercase tracking-[0.16em] text-[#64748b]">Parcours de diagnostic</h2>
        <div className="space-y-2">
          {(scenario.diagnostic_steps || []).map((step, index) => (
            <details key={step.title + '-' + index} className="group rounded-xl border border-[#30363d] bg-[#0d1117]/60">
              <summary className="cursor-pointer list-none px-3.5 py-3 text-xs font-semibold text-[#e6edf3] marker:hidden">
                <span className="mr-2 inline-flex h-5 w-5 items-center justify-center rounded-md bg-[#0ea5e9]/15 font-mono text-[10px] text-[#7dd3fc]">{index + 1}</span>{step.title}
              </summary>
              <div className="space-y-2 border-t border-[#30363d] px-3.5 py-3 text-[11px] leading-relaxed text-[#cbd5e1]">
                <p>{step.instructions}</p>
                {step.hint && <p className="rounded-lg bg-[#d29922]/[0.08] p-2 text-[#e3b341]">💡 {step.hint}</p>}
              </div>
            </details>
          ))}
        </div>
      </section>
      {ticket.status === 'pending_postmortem' && <div role="status" className="rounded-xl border border-[#d29922]/30 bg-[#d29922]/10 p-3 text-xs text-[#e3b341]">La configuration a été vérifiée. Il reste à valider le post-mortem pour clôturer et créditer les XP.</div>}
      <div className="rounded-xl border border-[#30363d] p-3 text-[11px] text-[#8b949e]">💡 Utilisez la console CLI et le panneau d’inspection. Les vérifications sont exécutées côté serveur ; le post-mortem est requis pour fermer le ticket.</div>
    </div>
  );
}
