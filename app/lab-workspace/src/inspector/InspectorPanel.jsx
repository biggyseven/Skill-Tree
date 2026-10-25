import { useLabStore } from '../store/useLabStore.js';
import { CLITab } from '../cli/CLITab.jsx';

export function InspectorPanel() {
  const selectedDeviceId = useLabStore(s => s.selectedDevice);
  const topology = useLabStore(s => s.topology);
  const device = topology?.nodes.find(n => n.id === selectedDeviceId);

  return (
    <div className="flex h-full flex-col bg-[var(--s1)]">
      <div className="border-b border-[var(--s2)] px-4 py-3">
        <div className="text-[10px] font-bold uppercase tracking-[0.16em] text-[var(--text-muted)]">Inspector</div>
        <div className="mt-1 text-sm font-bold text-[var(--text-primary)]">
          {device ? `${device.config?.hostname || device.id} · ${device.type}` : 'Aucun équipement sélectionné'}
        </div>
      </div>
      <div className="flex-1 overflow-hidden">
        <CLITab />
      </div>
    </div>
  );
}
