import { DeviceIcon } from './nodes/DeviceIcon.jsx';

const DEVICE_GROUPS = [
  {
    title: 'Routeurs',
    caption: 'Routage L3',
    devices: [
      { id: 'router-isr', type: 'router', label: 'Routeur ISR', model: 'Cisco ISR 4331', canvasLabel: 'ISR', idPrefix: 'RTR-ISR', portCount: 3 },
      { id: 'router-wan', type: 'router', label: 'Routeur WAN', model: 'Routeur WAN compact', canvasLabel: 'WAN', idPrefix: 'RTR-WAN', portCount: 4 },
      { id: 'router-core', type: 'router', label: 'Routeur cœur', model: 'Routeur cœur L3', canvasLabel: 'CORE', idPrefix: 'RTR-CORE', portCount: 6 },
    ],
  },
  {
    title: 'Switchs & concentration',
    caption: 'Commutation L2/L3',
    devices: [
      { id: 'switch-l2-8', type: 'switch', label: 'Switch L2 · 8 ports', model: 'Switch administrable L2 · 8 ports', canvasLabel: 'SW8', idPrefix: 'SW8', portCount: 8 },
      { id: 'switch-l2-24', type: 'switch', label: 'Switch L2 · 24 ports', model: 'Switch administrable L2 · 24 ports', canvasLabel: 'SW24', idPrefix: 'SW24', portCount: 24 },
      { id: 'switch-l3-48', type: 'switch', label: 'Switch L3 · 48 ports', model: 'Switch multilayer L3 · 48 ports', canvasLabel: 'SW48', idPrefix: 'SW48', portCount: 48 },
      { id: 'switch-poe-24', type: 'switch', label: 'Switch PoE · 24 ports', model: 'Switch PoE+ · 24 ports', canvasLabel: 'POE24', idPrefix: 'POE24', portCount: 24 },
      { id: 'ethernet-hub', type: 'switch', label: 'Hub Ethernet', model: 'Concentrateur Ethernet · 4 ports', canvasLabel: 'HUB', idPrefix: 'HUB', iconType: 'hub', portCount: 4 },
    ],
  },
  {
    title: 'Terminaux & périphériques',
    caption: 'Postes et accès',
    devices: [
      { id: 'desktop-pc', type: 'pc', label: 'PC fixe', model: 'Poste de travail Ethernet', canvasLabel: 'PC', idPrefix: 'PC', portCount: 1 },
      { id: 'laptop', type: 'pc', label: 'Ordinateur portable', model: 'Ordinateur portable Wi-Fi/Ethernet', canvasLabel: 'LAPTOP', idPrefix: 'LAP', iconType: 'laptop', portCount: 1 },
      { id: 'network-printer', type: 'pc', label: 'Imprimante réseau', model: 'Imprimante réseau Ethernet', canvasLabel: 'PRN', idPrefix: 'PRN', iconType: 'printer', portCount: 1 },
      { id: 'ip-phone', type: 'pc', label: 'Téléphone IP', model: 'Téléphone VoIP', canvasLabel: 'IP-PHONE', idPrefix: 'PHONE', iconType: 'phone', portCount: 1 },
    ],
  },
  {
    title: 'Serveurs & stockage',
    caption: 'Services et données',
    devices: [
      { id: 'app-server', type: 'server', label: 'Serveur applicatif', model: 'Serveur applicatif', canvasLabel: 'APP', idPrefix: 'SRV-APP', portCount: 2 },
      { id: 'dns-server', type: 'server', label: 'Serveur DNS/DHCP', model: 'Serveur DNS et DHCP', canvasLabel: 'DNS', idPrefix: 'SRV-DNS', portCount: 2 },
      { id: 'database-server', type: 'server', label: 'Serveur de base de données', model: 'Serveur SQL / base de données', canvasLabel: 'DB', idPrefix: 'SRV-DB', iconType: 'database', portCount: 2 },
      { id: 'nas-storage', type: 'server', label: 'Stockage NAS/SAN', model: 'Baie de stockage NAS/SAN', canvasLabel: 'NAS', idPrefix: 'NAS', iconType: 'storage', portCount: 2 },
    ],
  },
  {
    title: 'Sécurité & distribution',
    caption: 'Périmètre et services',
    devices: [
      { id: 'firewall-ngfw', type: 'firewall', label: 'Pare-feu NGFW', model: 'Pare-feu nouvelle génération', canvasLabel: 'FW', idPrefix: 'FW', portCount: 4 },
      { id: 'vpn-gateway', type: 'firewall', label: 'Passerelle VPN', model: 'Passerelle VPN site-à-site', canvasLabel: 'VPN', idPrefix: 'VPN', iconType: 'vpn_gateway', portCount: 3 },
      { id: 'load-balancer', type: 'server', label: 'Répartiteur de charge', model: 'Load balancer L4/L7', canvasLabel: 'LB', idPrefix: 'LB', iconType: 'load_balancer', portCount: 4 },
      { id: 'wifi-controller', type: 'server', label: 'Contrôleur Wi-Fi', model: 'Contrôleur de points d’accès', canvasLabel: 'WLC', idPrefix: 'WLC', iconType: 'wireless_controller', portCount: 2 },
    ],
  },
  {
    title: 'Accès & WAN',
    caption: 'Accès opérateur et sans fil',
    devices: [
      { id: 'wifi-access-point', type: 'switch', label: 'Point d’accès Wi-Fi', model: 'Point d’accès Wi-Fi 6', canvasLabel: 'AP', idPrefix: 'AP', iconType: 'access_point', portCount: 1 },
      { id: 'modem-ont', type: 'router', label: 'Modem / ONT', model: 'Modem fibre / ONT opérateur', canvasLabel: 'ONT', idPrefix: 'ONT', iconType: 'modem', portCount: 2 },
      { id: 'cloud-wan', type: 'cloud', label: 'Cloud / WAN', model: 'Réseau opérateur / WAN', canvasLabel: 'WAN-CLOUD', idPrefix: 'WAN', portCount: 2 },
    ],
  },
];

const EQUIPMENT_MODEL_COUNT = DEVICE_GROUPS.reduce(
  (total, group) => total + group.devices.length,
  0,
);

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
