import { Handle, Position } from '@xyflow/react';
import { DeviceIcon } from './DeviceIcon.jsx';

const leftUpper = '!absolute !left-0 !top-[34%] !z-10 !h-2.5 !w-2.5 !-translate-x-1/2 !rounded-full !border-2 !border-[var(--s1)] !bg-[var(--cyan-400)]';
const leftLower = '!absolute !left-0 !top-[68%] !z-10 !h-2.5 !w-2.5 !-translate-x-1/2 !rounded-full !border-2 !border-[var(--s1)] !bg-[var(--cyan-400)]';
const rightUpper = '!absolute !right-0 !left-auto !top-[34%] !z-10 !h-2.5 !w-2.5 !translate-x-1/2 !rounded-full !border-2 !border-[var(--s1)] !bg-[var(--cyan-400)]';
const rightLower = '!absolute !right-0 !left-auto !top-[68%] !z-10 !h-2.5 !w-2.5 !translate-x-1/2 !rounded-full !border-2 !border-[var(--s1)] !bg-[var(--cyan-400)]';

export function DeviceNode({ data = {}, selected = false, kind, title, surface = 'bg-[var(--s1)]' }) {
  const isUp = data.state !== 'down';
  const label = data.label || data.hostname || title;
  const meta = data.hostname || data.model || 'Équipement réseau';
  const rootClass = [
    'relative flex flex-col gap-2 rounded-xl border text-[var(--text-primary)] shadow-lg',
    surface,
    selected ? 'border-[var(--emerald-400)]' : 'border-[var(--s2)]',
  ].join(' ');

  return (
    <div className={rootClass} style={{ width: 180, padding: 12 }}>
      <Handle type="target" position={Position.Left} id="left-upper-target" className={leftUpper} />
      <Handle type="target" position={Position.Left} id="left-lower-target" className={leftLower} />
      <Handle type="source" position={Position.Right} id="right-upper-source" className={rightUpper} />
      <Handle type="source" position={Position.Right} id="right-lower-source" className={rightLower} />

      <div className="flex min-w-0 items-center gap-2">
        <DeviceIcon kind={kind} className="h-6 w-6 shrink-0 text-[var(--cyan-400)]" />
        <span className="min-w-0 truncate font-mono text-sm text-[var(--text-primary)]" title={String(label)}>{label}</span>
      </div>

      {kind === 'switch' && (
        <div className="flex items-center gap-1" aria-label="8 ports de commutation">
          {Array.from({ length: 8 }, (_, index) => (
            <span key={index} className="h-[4px] w-[8px] shrink-0 rounded-[1px] bg-[var(--cyan-400)]" />
          ))}
        </div>
      )}

      <div className="flex min-w-0 items-center justify-between gap-2">
        <span className="min-w-0 truncate text-xs text-zinc-500" title={String(meta)}>{meta}</span>
        <span className="flex shrink-0 items-center gap-1.5 text-[10px] uppercase tracking-wide text-zinc-500" title={isUp ? 'Équipement opérationnel' : 'Équipement hors service'}>
          <span aria-hidden="true" className={`h-2 w-2 rounded-full ${isUp ? 'bg-[var(--emerald-400)]' : 'bg-[var(--red-400)]'}`} />
          {isUp ? 'UP' : 'DOWN'}
        </span>
      </div>
    </div>
  );
}
