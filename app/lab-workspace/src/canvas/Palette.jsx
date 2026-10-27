import { DeviceIcon } from './nodes/DeviceIcon.jsx';
import { DEVICE_GROUPS, EQUIPMENT_MODEL_COUNT } from './deviceCatalog.js';

export function Palette() {
  const onDragStart = (event, device) => {
    const payload = {
      type: device.type,
      model: device.model,
      iconType: device.iconType || device.type,
      portCount: device.portCount,
      idPrefix: device.idPrefix,
      canvasLabel: device.canvasLabel,
    };
    event.dataTransfer.setData('application/reactflow', JSON.stringify(payload));
    event.dataTransfer.setData('text/plain', device.label);
    event.dataTransfer.effectAllowed = 'move';
    event.currentTarget.classList.add('opacity-60');
  };

  const onDragEnd = (event) => {
    event.currentTarget.classList.remove('opacity-60');
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-[#161b22]">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-[#30363d] px-3 py-2.5">
        <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-[#8b949e]">
          Bibliothèque d’équipements
        </div>
        <span className="rounded border border-[#30363d] bg-[#0d1117] px-1.5 py-0.5 font-mono text-[9px] text-[#8b949e]">
          {EQUIPMENT_MODEL_COUNT} modèles
        </span>
      </div>

      <div className="lab-scrollbar min-h-0 flex-1 space-y-4 overflow-y-auto p-3">
        {DEVICE_GROUPS.map(group => (
          <section key={group.title} aria-label={group.title}>
            <div className="mb-2 flex items-end justify-between gap-2">
              <h3 className="text-[10px] font-bold uppercase tracking-[0.13em] text-[#c9d1d9]">
                {group.title}
              </h3>
              <span className="text-[9px] text-[#6e7681]">{group.caption}</span>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {group.devices.map(device => (
                <button
                  key={device.id}
                  type="button"
                  draggable
                  data-testid={`equipment-model-${device.id}`}
                  aria-label={`Glisser ${device.label} sur le canevas`}
                  title={`Glisser ${device.label} sur le canevas`}
                  onDragStart={event => onDragStart(event, device)}
                  onDragEnd={onDragEnd}
                  className={[
                    'group relative flex min-h-[76px] min-w-0 select-none flex-col items-center justify-center gap-1.5',
                    'cursor-grab rounded-lg border border-[#30363d] bg-[#0d1117] p-2 text-center',
                    'transition-all duration-150 ease-out',
                    'hover:-translate-y-0.5 hover:scale-[1.015] hover:border-[#0ea5e9]/80 hover:bg-[#0ea5e9]/[0.06]',
                    'hover:shadow-[0_5px_16px_rgba(14,165,233,0.09)] active:scale-[0.98] active:cursor-grabbing',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]',
                  ].join(' ')}
                >
                  <span className="absolute left-2 top-2 h-1.5 w-1.5 rounded-full bg-[#30363d] transition-colors group-hover:bg-[#0ea5e9]" />
                  <DeviceIcon type={device.iconType || device.type} className="h-6 w-6 text-[#0ea5e9] transition-transform duration-150 group-hover:scale-110" />
                  <span className="text-[10px] font-semibold text-[#c9d1d9] transition-colors group-hover:text-white">
                    {device.label}
                  </span>
                  <span className="text-[9px] text-[#6e7681]">{device.portCount} ports</span>
                </button>
              ))}
            </div>
          </section>
        ))}
      </div>

      <div className="shrink-0 border-t border-[#30363d] bg-[#0d1117]/60 px-3 py-2.5">
        <div className="flex items-center justify-center gap-2 text-[10px] text-[#8b949e]">
          <span className="text-[#0ea5e9]">↘</span>
          Glisser un équipement vers la topologie
        </div>
      </div>
    </div>
  );
}
