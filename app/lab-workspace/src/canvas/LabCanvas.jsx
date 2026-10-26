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
        data: { label: n.label || n.id, hostname: (n.config && n.config.hostname) || n.id, state: anyUp ? 'up' : 'down', ports: n.ports },
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
    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;
    const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
    addNode(type, position.x, position.y);
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

      <Toolbar />

      <div className="pointer-events-none absolute z-50 flex h-6 w-6 items-center justify-center rounded-full bg-[#10b981] shadow-[0_0_15px_#10b981]" style={packetStyle}>
        <div className="h-2 w-2 rounded-full bg-white animate-ping" />
      </div>
    </div>
  );
}
