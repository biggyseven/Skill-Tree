import { useCallback, useMemo, useState } from 'react';
import { validateConnection } from './connectionValidation.js';
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
  const [connectionMessage, setConnectionMessage] = useState('');

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
    const result = validateConnection({ connection: params, topology, cableType: activeTool });
    if (!result.valid) {
      setConnectionMessage(result.message);
      return;
    }
    setConnectionMessage('');
    addLink(params, activeTool);
  }, [addLink, activeTool, topology]);

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

      {connectionMessage && (
        <div role="alert" className="absolute bottom-16 left-1/2 z-[100] w-[min(420px,calc(100%-24px))] -translate-x-1/2 rounded-lg border border-[#f87171]/60 bg-[#450a0a] px-4 py-3 text-xs leading-relaxed text-[#fee2e2] shadow-xl">
          <div className="flex items-start justify-between gap-3">
            <span>{connectionMessage}</span>
            <button type="button" aria-label="Fermer le message" className="shrink-0 rounded px-1 text-base leading-none hover:bg-white/10" onClick={() => setConnectionMessage('')}>×</button>
          </div>
        </div>
      )}

      <Toolbar />

      <div className="pointer-events-none absolute z-50 flex h-6 w-6 items-center justify-center rounded-full bg-[#10b981] shadow-[0_0_15px_#10b981]" style={packetStyle}>
        <div className="h-2 w-2 rounded-full bg-white animate-ping" />
      </div>
    </div>
  );
}
