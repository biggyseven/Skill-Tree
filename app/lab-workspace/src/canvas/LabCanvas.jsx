import { useCallback, useMemo } from 'react';
import { ReactFlow, Background, BackgroundVariant, Controls, MiniMap, useReactFlow } from '@xyflow/react';
import { useLabStore } from '../store/useLabStore.js';
import { nodeTypes, edgeTypes } from './nodeTypes.js';
import { Toolbar } from './Toolbar.jsx';

const defaultEdgeOptions = { type: 'cable' };

export function LabCanvas() {
  const topology = useLabStore(s => s.topology);
  const selectDevice = useLabStore(s => s.selectDevice);
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
        data: { type: n.type, iconType: n.iconType || n.type, model: n.model || 'Modèle non renseigné', label: n.label || n.id, hostname: (n.config && n.config.hostname) || n.id, state: anyUp ? 'up' : 'down', ports: n.ports },
      };
    });
  }, [topology]);

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
        className="pointer-events-none absolute left-3 top-3 z-40 w-72 max-w-[90%] rounded-xl border border-[#334155] bg-[#0d1117]/95 p-3 shadow-xl backdrop-blur-sm"
      >
        <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.12em] text-[#e6edf3]">
          Comprendre les ports
        </div>
        <div className="flex items-center gap-2 text-[10px] leading-relaxed text-[#c9d1d9]">
          <span className="h-2.5 w-2.5 shrink-0 rounded-sm border border-[#7dd3fc] bg-[#0ea5e9]" />
          <span><strong className="text-[#7dd3fc]">Bleu</strong> : départ du câble.</span>
        </div>
        <div className="mt-1 flex items-center gap-2 text-[10px] leading-relaxed text-[#c9d1d9]">
          <span className="h-2.5 w-2.5 shrink-0 rounded-sm border border-[#cbd5e1] bg-[#64748b]" />
          <span><strong className="text-[#cbd5e1]">Gris</strong> : arrivée du câble.</span>
        </div>
        <p className="mt-2 border-t border-[#30363d] pt-2 text-[10px] leading-relaxed text-[#8b949e]">
          Les points bleu et gris représentent le même port physique, pas deux ports différents.
          Choisis un câble, puis glisse du bleu d’un équipement vers le gris de l’autre.
        </p>
        <p className="mt-2 text-[10px] leading-relaxed text-[#fca5a5]">
          Un câble rouge pointillé signale qu’au moins un port est OFF. Active les deux interfaces dans Inspecteur → Hardware, ou avec « no shutdown » dans la CLI.
        </p>
      </div>

      <Toolbar />

      <div className="pointer-events-none absolute z-50 flex h-6 w-6 items-center justify-center rounded-full bg-[#10b981] shadow-[0_0_15px_#10b981]" style={packetStyle}>
        <div className="h-2 w-2 rounded-full bg-white animate-ping" />
      </div>
    </div>
  );
}
