import { useState } from 'react';
import { useLabStore } from '../store/useLabStore.js';
import { CLITab } from '../cli/CLITab.jsx';

export function InspectorPanel() {
  const selectedDeviceId = useLabStore(s => s.selectedDevice);
  const topology = useLabStore(s => s.topology);
  const addPort = useLabStore(s => s.addPort);
  const removePort = useLabStore(s => s.removePort);
  const togglePortState = useLabStore(s => s.togglePortState);
  
  const [activeTab, setActiveTab] = useState('cli'); // 'cli' ou 'hardware'
  const device = topology?.nodes.find(n => n.id === selectedDeviceId);

  if (!device) {
    return (
      <div className="flex h-full flex-col bg-[#0f172a]">
        <div className="border-b border-[#334155] px-4 py-3">
          <div className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#64748b]">Inspector</div>
          <div className="mt-1 text-sm font-bold text-[#e2e8f0]">Aucun équipement sélectionné</div>
        </div>
        <div className="flex flex-1 items-center justify-center p-6 text-center text-xs text-[#64748b]">
          Sélectionnez un équipement sur le canevas<br/>pour ouvrir sa console CLI ou gérer son matériel.
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-[#0f172a]">
      {/* En-tête de l'équipement */}
      <div className="border-b border-[#334155] px-4 py-3">
        <div className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#64748b]">Inspector</div>
        <div className="mt-1 text-sm font-bold text-[#e2e8f0]">{device.config?.hostname || device.id}</div>
      </div>

      {/* Onglets */}
      <div className="flex border-b border-[#334155] bg-[#1e293b]">
        <button 
          onClick={() => setActiveTab('cli')}
          className={`flex-1 py-2 text-xs font-bold transition-colors ${activeTab === 'cli' ? 'bg-[#0f172a] text-[#0ea5e9] border-b-2 border-[#0ea5e9]' : 'text-[#64748b] hover:text-[#e2e8f0]'}`}
        >
          CLI (Terminal)
        </button>
        <button 
          onClick={() => setActiveTab('hardware')}
          className={`flex-1 py-2 text-xs font-bold transition-colors ${activeTab === 'hardware' ? 'bg-[#0f172a] text-[#0ea5e9] border-b-2 border-[#0ea5e9]' : 'text-[#64748b] hover:text-[#e2e8f0]'}`}
        >
          Hardware (Ports)
        </button>
      </div>

      {/* Contenu */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'cli' && <CLITab />}
        
        {activeTab === 'hardware' && (
          <div className="flex h-full flex-col p-4">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xs font-bold text-[#e2e8f0]">Interfaces physiques</h3>
              <button 
                onClick={() => addPort(device.id)}
                className="rounded bg-[#10b981] px-2 py-1 text-[10px] font-bold text-white hover:bg-[#059669]"
              >
                + Ajouter un port
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto space-y-2">
              {device.ports?.map((port) => (
                <div key={port.id} className="flex items-center justify-between rounded bg-[#1e293b] p-2 border border-[#334155]">
                  <div className="flex flex-col">
                    <span className="font-mono text-xs font-bold text-[#e2e8f0]">{port.name}</span>
                    <span className="text-[10px] text-[#64748b]">IP: {port.ip || 'Non assignée'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button 
                      onClick={() => togglePortState(device.id, port.id)}
                      className={`text-[10px] px-2 py-0.5 rounded font-bold ${port.state === 'up' ? 'bg-[#10b981]/20 text-[#10b981]' : 'bg-[#f43f5e]/20 text-[#f43f5e]'}`}
                    >
                      {port.state === 'up' ? 'UP' : 'DOWN'}
                    </button>
                    <button 
                      onClick={() => removePort(device.id, port.id)}
                      className="text-[#f43f5e] hover:bg-[#f43f5e]/20 p-1 rounded"
                      title="Supprimer le port"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
              {(!device.ports || device.ports.length === 0) && (
                <p className="text-center text-xs text-[#64748b] mt-4">Aucun port configuré.</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
