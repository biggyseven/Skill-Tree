import { useLabStore } from '../store/useLabStore.js';

const CABLES = [
  {
    id: 'cable_straight',
    name: 'Cuivre droit RJ45',
    description: 'Câble Ethernet droit',
    detail: 'PC, serveurs, switchs et routeurs',
    color: '#0ea5e9',
    dash: '',
  },
  {
    id: 'cable_cross',
    name: 'Cuivre croisé RJ45',
    description: 'Câble Ethernet croisé',
    detail: 'Liaison cuivre entre équipements de même rôle',
    color: '#f97316',
    dash: '5 3',
  },
  {
    id: 'fiber_multimode',
    name: 'Fibre multimode',
    description: 'Fibre optique multimode',
    detail: 'Datacenter et liaisons courtes',
    color: '#a855f7',
    dash: '',
  },
  {
    id: 'fiber_singlemode',
    name: 'Fibre monomode',
    description: 'Fibre optique monomode',
    detail: 'Backbone et longues distances',
    color: '#ec4899',
    dash: '7 3',
  },
  {
    id: 'console',
    name: 'Console RJ45',
    description: 'Câble console série',
    detail: 'Terminal vers port console réseau',
    color: '#eab308',
    dash: '3 3',
  },
  {
    id: 'console_usb',
    name: 'Console USB',
    description: 'Câble USB de configuration',
    detail: 'PC d’administration vers console USB',
    color: '#facc15',
    dash: '1 3',
  },
  {
    id: 'dac',
    name: 'DAC / Twinax SFP+',
    description: 'Câble direct attach cuivre',
    detail: 'Liaisons haut débit en baie',
    color: '#06b6d4',
    dash: '2 2',
  },
  {
    id: 'coaxial',
    name: 'Câble coaxial',
    description: 'Liaison coaxiale',
    detail: 'Accès câble et équipements RF',
    color: '#f59e0b',
    dash: '8 3',
  },
  {
    id: 'serial_dce',
    name: 'Série DCE / DTE',
    description: 'Câble série WAN',
    detail: 'Liaisons série et exercices WAN',
    color: '#fb923c',
    dash: '6 3',
  },
  {
    id: 'telephone',
    name: 'Câble téléphonique RJ11',
    description: 'Liaison téléphonique',
    detail: 'Modem, accès téléphonique et DSL',
    color: '#94a3b8',
    dash: '2 3',
  },
];

const WIRELESS_LINK = {
  id: 'wireless',
  name: 'Liaison radio / Wi-Fi',
  description: 'Connexion sans câble physique',
  detail: 'Wi-Fi et liaison hertzienne simulée',
  color: '#22c55e',
  dash: '2 4',
};

function CableGlyph({ color, dash }) {
  return (
    <svg viewBox="0 0 64 24" className="h-6 w-14 shrink-0" aria-hidden="true">
      <path d="M5 12 H59" stroke={color} strokeWidth="3" strokeLinecap="round" strokeDasharray={dash || undefined} />
      <circle cx="5" cy="12" r="3" fill={color} />
      <circle cx="59" cy="12" r="3" fill={color} />
    </svg>
  );
}

function CableCard({ cable, activeTool, setTool }) {
  const active = activeTool === cable.id;
  return (
    <button
      key={cable.id}
      type="button"
      data-testid={'cable-item-' + cable.id}
      aria-pressed={active}
      onClick={() => setTool(cable.id)}
      className={active
        ? 'group flex min-h-[88px] min-w-0 flex-col justify-center gap-2 rounded-lg border border-[#0ea5e9]/60 bg-[#0ea5e9]/10 p-3 text-left ring-1 ring-[#0ea5e9]/20'
        : 'group flex min-h-[88px] min-w-0 flex-col justify-center gap-2 rounded-lg border border-[#30363d] bg-[#0d1117] p-3 text-left transition-colors hover:border-[#64748b] hover:bg-[#161b22]'}
      title={cable.description + '. ' + cable.detail}
    >
      <div className="flex items-center justify-between gap-2">
        <CableGlyph color={cable.color} dash={cable.dash} />
        <span className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: cable.color }} />
      </div>
      <span className="text-[11px] font-semibold text-[#e6edf3]">{cable.name}</span>
      <span className="text-[9px] leading-relaxed text-[#8b949e]">{cable.detail}</span>
    </button>
  );
}

export function CablePalette() {
  const activeTool = useLabStore(state => state.activeTool);
  const setTool = useLabStore(state => state.setTool);

  return (
    <div className="flex h-full min-h-0 flex-col bg-[#161b22]">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-[#30363d] px-3 py-2">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[0.13em] text-[#c9d1d9]">Bibliothèque de câbles</div>
          <p className="mt-0.5 text-[9px] text-[#6e7681]">Choisis le type de liaison avant de relier deux ports</p>
        </div>
        <span className="rounded border border-[#30363d] bg-[#0d1117] px-1.5 py-0.5 font-mono text-[9px] text-[#8b949e]">
          {CABLES.length} câbles
        </span>
      </div>

      <div className="lab-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
        <button
          type="button"
          data-testid="cable-select-tool"
          aria-pressed={activeTool === 'select'}
          onClick={() => setTool('select')}
          className={activeTool === 'select'
            ? 'mb-3 flex w-full items-center justify-between rounded-lg border border-[#0ea5e9]/50 bg-[#0ea5e9]/10 px-3 py-2 text-left text-[10px] font-semibold text-[#7dd3fc]'
            : 'mb-3 flex w-full items-center justify-between rounded-lg border border-[#30363d] bg-[#0d1117] px-3 py-2 text-left text-[10px] text-[#8b949e] hover:border-[#64748b] hover:text-white'}
        >
          <span className="flex items-center gap-2"><span aria-hidden="true">↖</span> Sélection / déplacement</span>
          <span className="text-[9px]">Esc</span>
        </button>

        <section aria-label="Câbles physiques">
          <div className="mb-2 flex items-end justify-between gap-2">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.13em] text-[#c9d1d9]">Câbles physiques</h3>
            <span className="text-[9px] text-[#6e7681]">Cuivre, fibre, console et WAN</span>
          </div>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {CABLES.map(cable => (
              <CableCard key={cable.id} cable={cable} activeTool={activeTool} setTool={setTool} />
            ))}
          </div>
        </section>

        <section className="mt-4 border-t border-[#30363d] pt-3" aria-label="Liaisons sans fil">
          <div className="mb-2 flex items-end justify-between gap-2">
            <h3 className="text-[10px] font-bold uppercase tracking-[0.13em] text-[#c9d1d9]">Liaisons sans fil</h3>
            <span className="text-[9px] text-[#6e7681]">Sans câble physique</span>
          </div>
          <CableCard cable={WIRELESS_LINK} activeTool={activeTool} setTool={setTool} />
        </section>

        <div className="mt-3 rounded-lg border border-[#30363d] bg-[#0d1117]/70 p-3 text-[10px] leading-relaxed text-[#8b949e]">
          1. Choisis un type de liaison. 2. Fais glisser d’un port source vers un port cible. 3. Change de type avant de créer la liaison suivante.
        </div>
      </div>
    </div>
  );
}
