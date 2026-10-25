import { useLabStore } from '../store/useLabStore.js';

const DEVICES = [
  { type: 'router', label: 'Routeur', icon: '🌐' },
  { type: 'switch', label: 'Switch', icon: '🔀' },
  { type: 'pc', label: 'PC', icon: '💻' },
  { type: 'server', label: 'Serveur', icon: '🖥️' },
  { type: 'firewall', label: 'Pare-feu', icon: '🛡️' },
  { type: 'cloud', label: 'Cloud WAN', icon: '☁️' },
];

export function Palette() {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="flex flex-col gap-2 p-4 h-full">
      <div className="text-[10px] font-bold uppercase tracking-widest text-[#64748b] mb-2">Boîte à outils</div>
      <div className="grid grid-cols-2 gap-2 overflow-y-auto">
        {DEVICES.map((d) => (
          <div
            key={d.type}
            className="cursor-grab rounded-lg border border-[#334155] bg-[#1e293b] p-2 flex flex-col items-center justify-center gap-1 hover:border-[#0ea5e9] hover:bg-[#0f172a] transition-colors select-none"
            onDragStart={(e) => onDragStart(e, d.type)}
            draggable
          >
            <span className="text-xl">{d.icon}</span>
            <span className="text-[10px] font-bold text-[#e2e8f0] text-center">{d.label}</span>
          </div>
        ))}
      </div>
      <div className="mt-auto text-center text-[10px] text-[#64748b] leading-tight">
        Glissez un équipement<br/>sur le canevas
      </div>
    </div>
  );
}
