import { useEffect } from 'react';
import { useTicketStore } from './useTicketStore.js';

function formatTime(seconds) {
  if (seconds === null || seconds === undefined) return 'Sans SLA';
  const total = Math.max(0, Number(seconds) || 0);
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = Math.floor(total % 60);
  const mm = String(minutes).padStart(2, '0');
  const ss = String(secs).padStart(2, '0');
  return hours > 0 ? String(hours).padStart(2, '0') + ':' + mm + ':' + ss : mm + ':' + ss;
}

export function SLABar() {
  const ticket = useTicketStore(s => s.ticket);
  const scenario = useTicketStore(s => s.scenario);
  const slaLeft = useTicketStore(s => s.sla_left);
  const setSlaLeft = useTicketStore(s => s.setSlaLeft);

  useEffect(() => {
    if (slaLeft === null || slaLeft === undefined) return undefined;
    const timer = window.setInterval(() => {
      const current = useTicketStore.getState().sla_left;
      if (current !== null && current !== undefined) setSlaLeft(Math.max(0, current - 1));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [ticket?.id, slaLeft === null || slaLeft === undefined, setSlaLeft]);

  if (!ticket || !scenario) return null;
  const severity = String(ticket.severity || 'medium').toLowerCase();
  const severityClass = severity === 'critical' || severity === 'high'
    ? 'border-[#f85149]/40 bg-[#f85149]/10 text-[#ffb4ad]'
    : severity === 'medium' ? 'border-[#d29922]/40 bg-[#d29922]/10 text-[#e3b341]'
    : 'border-[#0ea5e9]/40 bg-[#0ea5e9]/10 text-[#7dd3fc]';
  const slaClass = slaLeft === null || slaLeft === undefined
    ? 'text-[#8b949e]' : slaLeft <= 300 ? 'text-[#ff7b72]' : 'text-[#7ee787]';

  return (
    <section aria-label="Chronomètre SLA du ticket" className="flex shrink-0 flex-wrap items-center justify-between gap-3 border-b border-[var(--s2)] bg-[var(--s1)] px-4 py-2.5">
      <div className="flex min-w-0 flex-wrap items-center gap-2.5">
        <span className="font-mono text-xs font-bold text-[var(--text-primary)]">{ticket.id}</span>
        <span className={'rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ' + severityClass}>{severity}</span>
        {ticket.status === 'pending_postmortem' && <span className="rounded-full border border-[#d29922]/30 bg-[#d29922]/10 px-2 py-1 text-[10px] font-semibold text-[#e3b341]">Post-mortem requis</span>}
      </div>
      <div className={'flex items-center gap-2 font-mono text-sm font-bold ' + slaClass}>
        <span aria-hidden="true">⏱</span><span>{formatTime(slaLeft)}</span>
      </div>
      <p className="w-full truncate text-[11px] text-[var(--text-secondary)] sm:w-auto sm:max-w-[48%]" title={scenario.impact}>{scenario.impact}</p>
    </section>
  );
}
