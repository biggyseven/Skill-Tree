import { useEffect, useState } from 'react';
import { useLabStore } from '../store/useLabStore.js';
import { CLITab } from '../cli/CLITab.jsx';

function InspectorHeader({ device }) {
  const hostname = device.config?.hostname || device.hostname || device.id;
  const isUp = (device.ports || []).some(port => port.state === 'up');

  return (
    <header className="shrink-0 border-b border-[#30363d] bg-[#161b22] px-4 py-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[9px] font-bold uppercase tracking-[0.18em] text-[#8b949e]">03 / Inspector</span>
        <span className="rounded border border-[#30363d] bg-[#0d1117] px-2 py-1 font-mono text-[9px] uppercase text-[#8b949e]">
          {device.type || 'device'}
        </span>
      </div>
      <div className="mt-2 flex min-w-0 items-center gap-2">
        <span className={['h-2 w-2 shrink-0 rounded-full', isUp ? 'bg-[#10b981] shadow-[0_0_6px_rgba(16,185,129,0.7)]' : 'bg-[#6e7681]'].join(' ')} />
        <h2 className="truncate text-sm font-semibold text-[#e6edf3]" title={hostname}>{hostname}</h2>
      </div>
      <p className="mt-1 truncate pl-4 font-mono text-[10px] text-[#8b949e]">
        {device.model || 'Modèle non renseigné'} <span className="text-[#484f58]">/</span> {device.id}
      </p>
    </header>
  );
}

function PowerSwitch({ port, deviceId, togglePortState }) {
  const isUp = port.state === 'up';
  const label = port.name || port.id;

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isUp}
      aria-label={`${isUp ? 'Désactiver' : 'Activer'} ${label}`}
      title={isUp ? 'Interface active — cliquer pour désactiver' : 'Interface inactive — cliquer pour activer'}
      onClick={() => togglePortState(deviceId, port.id)}
      className={[
        'inline-flex h-7 shrink-0 items-center gap-2 rounded-md border px-2',
        'text-[10px] font-bold transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]',
        isUp
          ? 'border-[#10b981]/40 bg-[#10b981]/10 text-[#10b981] hover:bg-[#10b981]/20'
          : 'border-[#f85149]/40 bg-[#f85149]/10 text-[#ff7b72] hover:bg-[#f85149]/20',
      ].join(' ')}
    >
      <span>{isUp ? 'ON' : 'OFF'}</span>
      <span className={['relative h-[15px] w-[28px] rounded-full border transition-colors', isUp ? 'border-[#10b981] bg-[#10b981]/25' : 'border-[#f85149] bg-[#f85149]/20'].join(' ')}>
        <span className={['absolute top-[2px] h-[9px] w-[9px] rounded-full transition-all duration-150', isUp ? 'left-[15px] bg-[#10b981]' : 'left-[2px] bg-[#ff7b72]'].join(' ')} />
      </span>
    </button>
  );
}

function isIPv4Address(value) {
  const octets = String(value || '').trim().split('.');
  return octets.length === 4 && octets.every(octet =>
    /^\d{1,3}$/.test(octet) && Number(octet) >= 0 && Number(octet) <= 255
  );
}

function isIPv4Mask(value) {
  if (!isIPv4Address(value)) return false;
  const bits = String(value).trim().split('.')
    .map(octet => Number(octet).toString(2).padStart(8, '0'))
    .join('');
  return /^1+0*$/.test(bits);
}

function PortAddressForm({ device, port, updatePortAddress }) {
  const [ip, setIp] = useState(port.ip || '');
  const [mask, setMask] = useState(port.mask || '');
  const [message, setMessage] = useState('');

  useEffect(() => {
    setIp(port.ip || '');
    setMask(port.mask || '');
  }, [device.id, port.id, port.ip, port.mask]);

  function applyAddress() {
    if (!isIPv4Address(ip)) {
      setMessage('Saisissez une adresse IPv4 valide, par exemple 192.168.10.10.');
      return;
    }
    if (!isIPv4Mask(mask)) {
      setMessage('Le masque doit être un masque IPv4 valide, par exemple 255.255.255.0.');
      return;
    }
    updatePortAddress(device.id, port.id, ip, mask);
    setMessage('Configuration appliquée. Lancez « Vérifier » pour contrôler le résultat.');
  }

  return (
    <div className="mt-3 rounded-md border border-[#0ea5e9]/20 bg-[#0d1117] p-2.5">
      <div className="mb-2 text-[9px] font-bold uppercase tracking-[0.13em] text-[#38bdf8]">Configuration IPv4</div>
      <label className="mb-2 block">
        <span className="mb-1 block text-[10px] text-[#8b949e]">Adresse IP</span>
        <input
          type="text"
          inputMode="decimal"
          autoComplete="off"
          spellCheck={false}
          value={ip}
          onChange={event => { setIp(event.target.value); setMessage(''); }}
          placeholder="192.168.10.10"
          aria-label={`Adresse IP de ${device.id}, interface ${port.name || port.id}`}
          className="w-full rounded border border-[#30363d] bg-[#161b22] px-2 py-1.5 font-mono text-[11px] text-[#e6edf3] outline-none focus:border-[#0ea5e9]"
        />
      </label>
      <label className="block">
        <span className="mb-1 block text-[10px] text-[#8b949e]">Masque de sous-réseau</span>
        <input
          type="text"
          inputMode="decimal"
          autoComplete="off"
          spellCheck={false}
          value={mask}
          onChange={event => { setMask(event.target.value); setMessage(''); }}
          placeholder="255.255.255.0"
          aria-label={`Masque IPv4 de ${device.id}, interface ${port.name || port.id}`}
          className="w-full rounded border border-[#30363d] bg-[#161b22] px-2 py-1.5 font-mono text-[11px] text-[#e6edf3] outline-none focus:border-[#0ea5e9]"
        />
      </label>
      <button
        type="button"
        onClick={applyAddress}
        className="mt-2 w-full rounded-md border border-[#0ea5e9]/40 bg-[#0ea5e9]/10 px-2 py-1.5 text-[10px] font-semibold text-[#38bdf8] transition hover:bg-[#0ea5e9]/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]"
      >
        Appliquer l’adresse
      </button>
      {message && <p role="status" aria-live="polite" className="mt-2 text-[10px] leading-relaxed text-[#c9d1d9]">{message}</p>}
    </div>
  );
}

function HardwarePortSlot({ device, port, removePort, togglePortState, updatePortAddress }) {
  const isUp = port.state === 'up';
  const name = port.name || port.id;

  return (
    <article className={['min-w-0 rounded-lg border bg-[#161b22] p-3 transition-colors duration-150', isUp ? 'border-[#10b981]/35 hover:border-[#10b981]/70' : 'border-[#f85149]/25 hover:border-[#f85149]/60'].join(' ')}>
      <div className="flex min-w-0 items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <span className={['h-2 w-2 shrink-0 rounded-full', isUp ? 'bg-[#10b981] shadow-[0_0_6px_rgba(16,185,129,0.6)]' : 'bg-[#f85149]'].join(' ')} />
          <span className="truncate font-mono text-xs font-semibold text-[#e6edf3]" title={name}>{name}</span>
        </div>
        <button
          type="button"
          onClick={() => removePort(device.id, port.id)}
          aria-label={`Supprimer le port ${name}`}
          title="Supprimer cette interface"
          className="rounded px-1.5 py-1 text-sm text-[#8b949e] transition-colors hover:bg-[#f85149]/10 hover:text-[#ff7b72] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]"
        >
          ×
        </button>
      </div>

      {/* Connecteur stylisé : représentation visuelle du port du modèle */}
      <div className="my-3 flex items-center gap-2">
        <div className="grid h-10 w-11 shrink-0 place-items-center rounded border border-[#30363d] bg-[#0d1117]">
          <div className={['flex h-5 w-7 items-center justify-center gap-[2px] rounded-sm border', isUp ? 'border-[#10b981]/50 bg-[#10b981]/10' : 'border-[#f85149]/35 bg-[#f85149]/[0.06]'].join(' ')}>
            <span className="h-2 w-[3px] rounded-[1px] bg-[#6e7681]" />
            <span className="h-2 w-[3px] rounded-[1px] bg-[#6e7681]" />
            <span className="h-2 w-[3px] rounded-[1px] bg-[#6e7681]" />
          </div>
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[9px] font-semibold uppercase tracking-[0.12em] text-[#6e7681]">Adresse IP</div>
          <div className="mt-1 truncate font-mono text-[11px] text-[#c9d1d9]" title={port.ip || 'IP non attribuée'}>
            {port.ip || 'Non attribuée'}
          </div>
          {port.mask && <div className="mt-0.5 truncate font-mono text-[10px] text-[#8b949e]">Masque {port.mask}</div>}
        </div>
      </div>

      {['pc', 'router', 'firewall', 'server', 'cloud'].includes(device.type) && (
        <PortAddressForm device={device} port={port} updatePortAddress={updatePortAddress} />
      )}

      <div className="flex items-center justify-between gap-2 border-t border-[#30363d] pt-2">
        <div className="min-w-0">
          <div className="text-[9px] uppercase tracking-wide text-[#8b949e]">Liaison physique</div>
          {port.mode && <div className="mt-0.5 truncate font-mono text-[10px] text-[#6e7681]">{port.mode}</div>}
        </div>
        <PowerSwitch port={port} deviceId={device.id} togglePortState={togglePortState} />
      </div>
    </article>
  );
}

function HardwareTab({ device, addPort, removePort, togglePortState, updatePortAddress }) {
  const ports = device.ports || [];
  const upCount = ports.filter(port => port.state === 'up').length;

  return (
    <div className="lab-scrollbar flex h-full min-h-0 flex-col gap-3 overflow-y-auto p-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-xs font-semibold text-[#e6edf3]">Interfaces physiques</h3>
          <p className="mt-1 text-[10px] text-[#8b949e]">Façade matérielle · états des ports</p>
        </div>
        <div className="shrink-0 rounded-md border border-[#30363d] bg-[#0d1117] px-2.5 py-1.5 text-right">
          <div className="font-mono text-sm font-bold text-[#e6edf3]">{ports.length}</div>
          <div className="text-[9px] uppercase tracking-wide text-[#8b949e]">Ports</div>
        </div>
      </div>

      <section className="rounded-xl border border-[#30363d] bg-[#0d1117] p-3 shadow-inner">
        <div className="flex items-center justify-between gap-2">
          <span className="truncate text-[9px] font-bold uppercase tracking-[0.16em] text-[#8b949e]">{device.type || 'Équipement'} / face avant</span>
          <span className="shrink-0 font-mono text-[10px] text-[#8b949e]"><span className="mr-1 text-[#10b981]">●</span>{upCount} ON <span className="mx-1 text-[#484f58]">/</span><span className="text-[#ff7b72]">{ports.length - upCount} OFF</span></span>
        </div>
        <div className="mt-3 flex items-center justify-between gap-3 rounded-md border border-[#30363d] bg-[#161b22] px-3 py-2">
          <div className="min-w-0">
            <div className="truncate font-mono text-xs font-semibold text-[#c9d1d9]">{device.model || device.type || 'DEVICE'}</div>
            <div className="mt-0.5 truncate text-[9px] text-[#6e7681]">{device.config?.hostname || device.hostname || device.id}</div>
          </div>
          <span className="flex shrink-0 items-center gap-1.5 text-[9px] uppercase tracking-wide text-[#8b949e]"><span className="h-2 w-2 rounded-full bg-[#10b981]" /> Power</span>
        </div>

        {ports.length > 0 ? (
          <div className="mt-3 grid grid-cols-2 gap-2">
            {ports.map(port => (
              <HardwarePortSlot key={port.id} device={device} port={port} removePort={removePort} togglePortState={togglePortState} updatePortAddress={updatePortAddress} />
            ))}
          </div>
        ) : (
          <div className="mt-3 rounded-lg border border-dashed border-[#30363d] p-5 text-center">
            <p className="text-xs font-medium text-[#c9d1d9]">Aucun port installé</p>
            <p className="mt-1 text-[10px] text-[#8b949e]">Ajoutez une interface pour commencer.</p>
          </div>
        )}
        <p className="mt-3 border-t border-[#30363d] pt-2 text-[9px] leading-relaxed text-[#6e7681]">
          Représentation visuelle des interfaces du modèle. Les valeurs affichées proviennent de la topologie courante.
        </p>
      </section>

      <button
        type="button"
        onClick={() => addPort(device.id)}
        className="flex shrink-0 items-center justify-center gap-2 rounded-lg border border-[#0ea5e9]/50 bg-[#0ea5e9]/10 px-3 py-2.5 text-xs font-semibold text-[#38bdf8] transition-colors hover:border-[#0ea5e9] hover:bg-[#0ea5e9]/15 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]"
      >
        <span className="text-base leading-none">+</span>
        Ajouter une interface
      </button>
    </div>
  );
}

export function InspectorPanel() {
  const selectedDeviceId = useLabStore(s => s.selectedDevice);
  const topology = useLabStore(s => s.topology);
  const addPort = useLabStore(s => s.addPort);
  const removePort = useLabStore(s => s.removePort);
  const togglePortState = useLabStore(s => s.togglePortState);
  const updatePortAddress = useLabStore(s => s.updatePortAddress);
  const [activeTab, setActiveTab] = useState('cli');
  const device = topology?.nodes.find(node => node.id === selectedDeviceId);

  useEffect(() => {
    setActiveTab(device?.type === 'pc' ? 'hardware' : 'cli');
  }, [device?.id, device?.type]);

  if (!device) {
    return (
      <section className="flex h-full min-h-0 flex-col bg-[#161b22]">
        <header className="shrink-0 border-b border-[#30363d] bg-[#161b22] px-4 py-3">
          <div className="text-[9px] font-bold uppercase tracking-[0.18em] text-[#8b949e]">03 / Inspector</div>
          <h2 className="mt-1 text-sm font-semibold text-[#e6edf3]">Aucun équipement sélectionné</h2>
        </header>
        <div className="flex flex-1 flex-col items-center justify-center p-6 text-center">
          <div className="grid h-12 w-12 place-items-center rounded-xl border border-[#30363d] bg-[#0d1117] text-xl text-[#0ea5e9]">◇</div>
          <p className="mt-3 text-xs font-medium text-[#c9d1d9]">Sélectionnez un équipement</p>
          <p className="mt-1 max-w-[230px] text-[11px] leading-relaxed text-[#8b949e]">Sa console CLI et ses interfaces physiques apparaîtront ici.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="flex h-full min-h-0 flex-col bg-[#161b22]">
      <InspectorHeader device={device} />

      <div className="flex shrink-0 border-b border-[#30363d] bg-[#0d1117] p-1">
        <button
          type="button"
          onClick={() => setActiveTab('cli')}
          aria-selected={activeTab === 'cli'}
          className={['flex-1 rounded-md px-3 py-2 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]', activeTab === 'cli' ? 'bg-[#161b22] text-[#38bdf8] shadow-sm' : 'text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]'].join(' ')}
        >
          <span className="mr-1.5 font-mono">&gt;_</span>Console CLI
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('hardware')}
          aria-selected={activeTab === 'hardware'}
          className={['flex-1 rounded-md px-3 py-2 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0ea5e9]', activeTab === 'hardware' ? 'bg-[#161b22] text-[#38bdf8] shadow-sm' : 'text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]'].join(' ')}
        >
          <span className="mr-1.5">▦</span>Hardware
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-hidden">
        {activeTab === 'cli' && <div className="h-full min-h-0 overflow-hidden"><CLITab /></div>}
        {activeTab === 'hardware' && (
          <HardwareTab device={device} addPort={addPort} removePort={removePort} togglePortState={togglePortState} updatePortAddress={updatePortAddress} />
        )}
      </div>
    </section>
  );
}
