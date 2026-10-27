import { useCallback, useMemo } from 'react';
import { ReactFlow, Background, BackgroundVariant, Controls, MiniMap, useReactFlow } from '@xyflow/react';
import { useLabStore } from '../store/useLabStore.js';
import { nodeTypes, edgeTypes } from './nodeTypes.js';
import { Toolbar } from './Toolbar.jsx';
import { CABLES, WIRELESS_LINK } from './cableCatalog.js';

const defaultEdgeOptions = { type: 'cable' };

export function LabCanvas() {
  const topology = useLabStore(s => s.topology);
  const selectDevice = useLabStore(s => s.selectDevice);
  const selectedDevice = useLabStore(s => s.selectedDevice);
  const updateNodePosition = useLabStore(s => s.updateNodePosition);
  const addNode = useLabStore(s => s.addNode);
  const addLink = useLabStore(s => s.addLink);
  const activePacket = useLabStore(s => s.activePacket);
  const activeTool = useLabStore(s => s.activeTool);
  const { screenToFlowPosition } = useReactFlow();

  const flowNodes = useMemo(() => {
    if (!topology) return [];
    return topology.nodes.map(n => {
      const anyUp = (n.ports || []).some(p => p.state === 'up');
      return {
        id: n.id, type: n.type, position: { x: n.x || 100, y: n.y || 100 },
        data: {
          nodeId: n.id,
          type: n.type,
          iconType: n.iconType || n.type,
          model: n.model || 'Modèle non renseigné',
          label: n.label || n.id,
          hostname: (n.config && n.config.hostname) || n.id,
          state: anyUp ? 'up' : 'down',
          ports: n.ports,
          showPortLabels: selectedDevice === n.id,
        },
      };
    });
  }, [topology, selectedDevice]);

  const flowEdges = useMemo(() => {
    if (!topology) return [];
    return topology.links.map(l => ({
      id: l.id, source: l.from.node, target: l.to.node, type: 'cable',
      sourceHandle: `${l.from.port}::source`, targetHandle: `${l.to.port}::target`,
      data: { state: l.state, cable_type: l.cable_type, label: `${l.from.port} → ${l.to.port}` },
    }));
  }, [topology]);

  const onNodesChange = useCallback((changes) => {
    changes.forEach(c => { if (c.type === 'position' && c.position) updateNodePosition(c.id, c.position.x, c.position.y); });
  }, [updateNodePosition]);

  const onNodeClick = useCallback((_e, node) => {
    if (activeTool === 'select') selectDevice(node.id);
  }, [selectDevice, activeTool]);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const rawPayload = event.dataTransfer.getData('application/reactflow');
    if (!rawPayload) return;
    let device = null;
    try {
      const parsed = JSON.parse(rawPayload);
      device = parsed && typeof parsed.type === 'string' ? parsed : null;
    } catch {
      // Compatibilité avec les anciennes cartes qui ne transfèrent que le type.
    }
    if (!device) device = { type: rawPayload };
    const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
    addNode(device.type, position.x, position.y, device);
  }, [screenToFlowPosition, addNode]);

  const onConnect = useCallback((params) => {
    addLink(params, activeTool);
  }, [addLink, activeTool]);

  if (!topology) return null;

  let packetStyle = { display: 'none' };
  if (activePacket) {
    const fromNode = topology.nodes.find(n => n.id === activePacket.from);
    const toNode = topology.nodes.find(n => n.id === activePacket.to);
    if (fromNode && toNode) {
      packetStyle = { left: (fromNode.x + toNode.x)/2 + 40, top: (fromNode.y + toNode.y)/2 + 40, display: 'block', transition: 'all 0.6s ease-in-out' };
    }
  }

  return (
    <div className={`relative flex-1 min-h-0 bg-[#0d1117] ${activeTool !== 'select' ? 'cursor-crosshair' : ''}`} onDrop={onDrop} onDragOver={onDragOver}>
      <ReactFlow nodes={flowNodes} edges={flowEdges} onNodesChange={onNodesChange} onNodeClick={onNodeClick}
        onConnect={onConnect}
        nodeTypes={nodeTypes} edgeTypes={edgeTypes} defaultEdgeOptions={defaultEdgeOptions}
        fitView fitViewOptions={{ padding: 0.2 }} proOptions={{ hideAttribution: true }}>
        
        <Background variant={BackgroundVariant.Dots} color="#21262d" gap={24} size={2} />
        
        <Controls 
          showInteractive={false} 
          style={{ backgroundColor: '#161b22', border: '1px solid #30363d', borderRadius: '8px', color: '#8b949e' }}
        />
        
        <MiniMap 
          pannable zoomable 
          style={{ backgroundColor: '#161b22', border: '1px solid #30363d', borderRadius: '8px' }} 
          nodeColor="#0ea5e9" 
          maskColor="rgba(13, 17, 23, 0.7)" 
        />
      </ReactFlow>

      <div
        role="note"
        aria-label="Guide de connexion des ports"
        data-testid="port-connection-guide"
        className="pointer-events-none absolute left-3 top-3 z-40 w-[360px] max-w-[90%] rounded-xl border border-[#334155] bg-[#0d1117]/95 p-3.5 shadow-xl backdrop-blur-sm"
      >
        <div className="mb-2 text-xs font-bold uppercase tracking-[0.12em] text-[#e6edf3]">
          Relier deux équipements
        </div>

        <div className="rounded-lg border border-[#30363d] bg-[#161b22] p-2.5">
          <div className="mb-2 text-[11px] font-semibold text-[#c9d1d9]">Un seul port physique, deux points de connexion</div>
          <div className="flex items-center gap-2">
            <span className="rounded border border-[#475569] bg-[#0d1117] px-2 py-1 font-mono text-[11px] font-bold text-white">Fa0/0</span>
            <span className="h-3 w-3 shrink-0 rounded-sm border border-[#7dd3fc] bg-[#0ea5e9]" />
            <span className="text-[10px] font-semibold text-[#7dd3fc]">Bleu = départ</span>
            <span className="mx-0.5 h-px min-w-2 flex-1 bg-[#475569]" />
            <span className="h-3 w-3 shrink-0 rounded-sm border border-[#cbd5e1] bg-[#64748b]" />
            <span className="text-[10px] font-semibold text-[#cbd5e1]">Gris = arrivée</span>
          </div>
          <p className="mt-2 text-[11px] leading-relaxed text-[#c9d1d9]">
            Les deux petits points correspondent au même port. Son nom, par exemple <strong>Fa0/0</strong>, est affiché à côté quand tu sélectionnes l’équipement.
          </p>
        </div>

        {activeTool === 'select' ? (
          <div className="mt-2 text-[11px] leading-relaxed text-[#c9d1d9]">
            <p><strong className="text-white">1.</strong> Ouvre l’onglet <strong>Câbles</strong> à gauche et choisis le type de liaison.</p>
            <p className="mt-1"><strong className="text-white">2.</strong> Maintiens le clic sur le point <strong className="text-[#7dd3fc]">bleu</strong> d’un équipement, glisse jusqu’au point <strong className="text-[#cbd5e1]">gris</strong> de l’autre, puis relâche.</p>
            <p className="mt-1 text-[10px] text-[#8b949e]">Sans choix de câble, le système utilise Ethernet droit par défaut.</p>
          </div>
        ) : (
          <div className="mt-2 rounded-lg border border-[#0ea5e9]/40 bg-[#0ea5e9]/10 p-2 text-[11px] leading-relaxed text-[#c9d1d9]">
            <strong className="text-[#7dd3fc]">Câble choisi :</strong> {CABLES.find(cable => cable.id === activeTool)?.name || (activeTool === WIRELESS_LINK.id ? WIRELESS_LINK.name : activeTool)}.
            <span> Maintiens le clic sur le point bleu du premier équipement, puis relâche sur le point gris de l’autre.</span>
          </div>
        )}

        <p className="mt-2 text-[11px] leading-relaxed text-[#fca5a5]">
          Liaison rouge pointillée = au moins un port est éteint (OFF). Sélectionne l’équipement, ouvre Inspecteur → Hardware et active l’interface, ou utilise « no shutdown » dans la CLI.
        </p>
      </div>

      <Toolbar />

      <div className="pointer-events-none absolute z-50 flex h-6 w-6 items-center justify-center rounded-full bg-[#10b981] shadow-[0_0_15px_#10b981]" style={packetStyle}>
        <div className="h-2 w-2 rounded-full bg-white animate-ping" />
      </div>
    </div>
  );
}
